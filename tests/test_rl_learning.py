"""Real neural updates on synthetic transitions; never evidence of game strength."""

# ruff: noqa: E402 -- optional training dependency must be checked before neural imports

import json
import random
from dataclasses import replace

import pytest

torch = pytest.importorskip("torch")

from test_rl_encoding import assessment, from_assessment, settings

from source.games.starcraft2.action_codec import decode, sample_action
from source.games.starcraft2.model import StarCraftPolicy, feature_vector
from source.games.starcraft2.observation import LIVE_FEATURE_VERSION
from source.strategy_core.contracts import Entity, Feature, StrategicStateV1
from source.training.checkpoints import load_checkpoint, save_checkpoint
from source.training.collector import MANIFEST_VERSION, EpisodeWriter, identity, load_episode
from source.training.ppo import PPOConfig, advantages, masked_statistics, update
from source.training.records import Outcome, TransitionV1

torch.set_num_threads(1)


def belief(time=100, version=2240, first=True):
    result = from_assessment(
        assessment(time=time, version=version),
        settings(),
        episode_start=first,
        elapsed_seconds=0 if first else 2,
    )
    entities = (Entity("opaque-unit", "controlled", (Feature("capacity", 0.01, "fraction", 0, 0),)),)
    return replace(
        result, shared=replace(result.shared, feature_version=LIVE_FEATURE_VERSION, entities=entities)
    )


def neural_episode(model, policy_id="synthetic-reference", end="victory"):
    states = [belief(), belief(102, 2285, False), belief(104, 2330, False)]
    memory = model.core.initial()
    rng = random.Random(123)
    records = []
    with torch.no_grad():
        logits, value, output_memory = model(states[0], memory)
        for index in range(2):
            sampled = sample_action(logits.tolist(), states[index], rng)
            next_logits, next_value, next_memory = model(states[index + 1], output_memory)
            outcome = Outcome("running" if index == 0 else end)
            records.append(
                TransitionV1(
                    "synthetic-episode",
                    index,
                    policy_id,
                    states[index],
                    decode(sampled, states[index], index),
                    states[index + 1],
                    tuple(memory[0].tolist()),
                    tuple(output_memory[0].tolist()),
                    value.item(),
                    next_value.item() if outcome.bootstrap else None,
                    outcome,
                )
            )
            memory, logits, value, output_memory = output_memory, next_logits, next_value, next_memory
    return records


def manifest(policy_id="synthetic-reference", **changes):
    initial = {"game_loop": 0, "units": []}
    result = {
        "schema_version": MANIFEST_VERSION,
        "episode_id": "synthetic-episode",
        "source_revision": "a" * 40,
        "lock_sha256": "b" * 64,
        "policy_id": policy_id,
        "core_version": "test",
        "adapter_version": "test",
        "shared_ontology": "strategic-semantics-v1",
        "domain_ontology": "test",
        "feature_version": LIVE_FEATURE_VERSION,
        "normalization_version": "sc2-fixed-scales-v1",
        "action_version": "director-action-v0",
        "mask_version": "sc2-director-masks-v1",
        "decoder_version": "sc2-director-decoder-v1",
        "reward_version": "terminal-win-loss-v1",
        "map_sha256": "c" * 64,
        "executable_sha256": "d" * 64,
        "ping": {"game_version": "synthetic", "base_build": 1, "data_build": 1, "data_version": "synthetic"},
        "opponent": {"race": "Terran", "difficulty": "VeryHard", "build": "Rush"},
        "game_seed": 31,
        "python_seed": 31,
        "policy_seed": 101,
        "step_size": 32,
        "time_limit": 3600,
        "split": "train",
        "settings": {},
        "initial_state": initial,
        "initial_state_sha256": identity(initial),
        "decision_cadence": "synthetic",
        "time_unit": "game_seconds",
    }
    return {**result, **changes}


def test_neural_shape_entity_serialization_and_episode_reset():
    torch.manual_seed(3)
    model = StarCraftPolicy().eval()
    state = belief()
    restored = StrategicStateV1.from_dict(json.loads(json.dumps(state.shared.to_dict())))
    assert restored == state.shared
    with torch.no_grad():
        logits, value, memory = model(state, model.core.initial())
        repeated, _, _ = model(state, torch.ones(1, 256))
    assert logits.shape == (34,) and value.shape == () and memory.shape == (1, 256)
    assert torch.equal(logits, repeated)
    assert all(torch.isfinite(x).all() for x in (logits, value, memory))
    assert 600_000 < sum(p.numel() for p in model.parameters()) < 700_000
    assert feature_vector(Feature("x", None, "ratio")) != feature_vector(Feature("x", 0, "ratio", 0, 0))
    with pytest.raises(ValueError):
        model(replace(state, shared=replace(state.shared, feature_version="future")), model.core.initial())


def test_tensor_distribution_matches_original_masks_likelihood_and_has_finite_gradients():
    model = StarCraftPolicy()
    records = neural_episode(model)
    for record in records:
        logits, _, _ = model(record.before, torch.tensor([record.recurrent_input]))
        probability, entropy = masked_statistics(logits, record.decoded.sampled)
        assert probability.item() == pytest.approx(record.decoded.sampled.log_probability, abs=1e-6)
        assert entropy.item() >= 0
        (-probability).backward()
    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)


def test_recurrent_ppo_changes_weights_and_rejects_foreign_or_held_out_data():
    model = StarCraftPolicy()
    records = neural_episode(model)
    before = model.core.cell.weight_hh.clone()
    optimizer, metrics = update(
        model,
        [(manifest(), records)],
        "synthetic-reference",
        PPOConfig(epochs=1, sequence_length=1, burn_in=1),
        seed=2,
    )
    assert optimizer and metrics["optimizer_steps"] > 0
    assert not torch.equal(before, model.core.cell.weight_hh)
    assert all(item["loss"] == item["loss"] for item in metrics["updates"])
    for invalid in (manifest(policy_id="foreign"), manifest(split="held_out")):
        with pytest.raises(ValueError):
            update(model, [(invalid, records)], "synthetic-reference")
    with pytest.raises(ValueError):
        advantages(records[:-1], PPOConfig())


def test_time_aware_gae_bootstraps_cutoff_but_ends_eligibility_at_boundary():
    records = neural_episode(StarCraftPolicy(), end="time_limit")
    config = PPOConfig(gamma_seconds=10, gae_seconds=20)
    adv, returns = advantages(records, config)
    gamma = records[-1].discount(10)
    expected = gamma * records[-1].next_value - records[-1].value_estimate
    assert adv[-1] == pytest.approx(expected)
    assert returns[-1] == pytest.approx(gamma * records[-1].next_value)
    broken = records[:-1] + [replace(records[-1], outcome=Outcome("infrastructure_error"), next_value=None)]
    with pytest.raises(ValueError):
        advantages(broken, config)


def test_episode_writer_round_trip_integrity_and_entire_error_quarantine(tmp_path):
    records = neural_episode(StarCraftPolicy())
    writer = EpisodeWriter(tmp_path / "complete", manifest())
    for record in records:
        writer.append(record)
    writer.finish(Outcome("victory"))
    data, restored = load_episode(tmp_path / "complete", split="train")
    assert restored == records and data["learning_eligible"]
    with pytest.raises(ValueError):
        load_episode(tmp_path / "complete", split="development")
    error = EpisodeWriter(tmp_path / "error", manifest())
    error.append(records[0])
    error.finish(Outcome("infrastructure_error"), error="synthetic disconnect")
    with pytest.raises(ValueError, match="quarantined"):
        load_episode(tmp_path / "error")
    with writer.path.open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="hash"):
        load_episode(tmp_path / "complete")


def test_checkpoint_round_trip_and_corruption_rejection(tmp_path):
    model = StarCraftPolicy().eval()
    saved = save_checkpoint(tmp_path / "checkpoint", model, seed=12)
    restored, metadata = load_checkpoint(tmp_path / "checkpoint")
    assert saved["policy_id"] == metadata["policy_id"]
    assert all(torch.equal(value, restored.state_dict()[key]) for key, value in model.state_dict().items())
    with (tmp_path / "checkpoint/core.pt").open("ab") as stream:
        stream.write(b"tampered")
    with pytest.raises(ValueError, match="hash"):
        load_checkpoint(tmp_path / "checkpoint")
