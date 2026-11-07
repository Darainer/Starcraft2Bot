"""Independent action ownership, physical masks, recurrent updates and resume.

All worlds here are synthetic. No game is launched by these tests.
"""

# ruff: noqa: E402 -- optional neural dependency is checked before importing it

import asyncio
import json
import random
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

torch = pytest.importorskip("torch")

from sc2.dicts.unit_train_build_abilities import TRAIN_INFO
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from test_rl_learning import belief, manifest

from source import strategy_policies
from source.games.starcraft2.action_codec import DecodeResult
from source.games.starcraft2.actions import head_log_probabilities
from source.games.starcraft2.encoding import BeliefStateV1
from source.games.starcraft2.learned_actions import (
    ACTION_VERSION,
    DECODER_VERSION,
    FEATURE_VERSION,
    HEAD_WIDTHS,
    MACRO_ACTIONS,
    LearnedAction,
    LearnedSample,
    decode,
    masks_for,
    sample_action,
)
from source.games.starcraft2.learned_execution import MacroSkill
from source.games.starcraft2.learned_model import LearnedPolicy
from source.training import cli
from source.training.checkpoints import load_checkpoint, restore_optimizer, save_checkpoint
from source.training.collector import EpisodeWriter, load_episode
from source.training.ppo import PPOConfig, masked_statistics, update
from source.training.records import Outcome, TransitionV1


def independent(time=100, version=2240, first=True, **changes):
    state = belief(time, version, first)
    return replace(
        state,
        shared=replace(state.shared, feature_version=FEATURE_VERSION),
        macro_mask=(True,) * len(MACRO_ACTIONS),
        **changes,
    )


def chosen(state, intent=2, target=0, macro=0, gas=0):
    logits = []
    for width, choice in zip(HEAD_WIDTHS, (intent, target, macro, gas), strict=True):
        logits.extend(50.0 if i == choice else -50.0 for i in range(width))
    return sample_action(logits, state, random.Random(1))


def test_rule_thresholds_do_not_restrict_learned_attack_or_spending(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Hardcoded policy must not decide learned actions")

    monkeypatch.setattr(strategy_policies, "candidates", forbidden)
    monkeypatch.setattr(strategy_policies, "compose", forbidden)
    state = independent()
    state = replace(
        state,
        assessment=replace(
            state.assessment, army_supply=0, army_count=0, health=0.1, trade_bad=True, rush_warning=True
        ),
    )
    sample = chosen(state, macro=MACRO_ACTIONS.index("nexus"), gas=3)
    result = decode(sample, state, 1)
    assert result.plan.objective == "pressure"
    assert result.plan.expand
    assert result.plan.missions[0].minimum_supply == 0
    assert not result.override_reasons
    assert result.sampled.action.gas == 3
    restored = DecodeResult.from_dict(json.loads(json.dumps(result.to_dict())))
    assert restored == result
    assert BeliefStateV1.from_dict(json.loads(json.dumps(state.to_dict()))) == state


def test_conditional_hold_likelihood_and_tensor_statistics():
    state = independent()
    sample = chosen(state, intent=0, target=8, macro=1, gas=2)
    assert sample.action.target == 0 and sample.head_log_probabilities[1] == 0
    assert sample.masks.active == (True, False, True, True)
    logits = torch.randn(sum(HEAD_WIDTHS), requires_grad=True)
    logp, entropy = masked_statistics(logits, sample)
    expected = sum(head_log_probabilities(logits.detach().tolist(), sample.action, sample.masks))
    assert logp.item() == pytest.approx(expected, abs=1e-5)
    (logp + entropy).backward()
    assert torch.isfinite(logits.grad).all()
    assert logits.grad[3:19].abs().sum() == 0
    paused = replace(
        state,
        permissions=replace(state.permissions, strategy=False),
        macro_mask=(True,) + (False,) * (len(MACRO_ACTIONS) - 1),
    )
    forced = sample_action([0.0] * sum(HEAD_WIDTHS), paused, random.Random(2))
    assert forced.action.indices == (0, 0, 0, 0)
    assert forced.log_probability == 0


def test_stale_target_and_macro_failure_keep_original_likelihood():
    state = independent()
    sample = chosen(state, macro=1)
    later = independent(106, 2375, False)
    later = replace(later, macro_mask=(True,) + (False,) * (len(MACRO_ACTIONS) - 1))
    result = decode(sample, later, 2)
    assert result.sampled == sample
    assert set(result.override_reasons) == {"stale_or_future_sample", "macro_no_longer_available"}
    skill = MacroSkill()
    skill.propose(result)
    assert skill.consumed and skill.feedback[0]["status"] == "decoder_rejected"
    with pytest.raises(ValueError):
        masks_for(replace(state, macro_mask=()), 0)
    with pytest.raises(ValueError):
        masks_for(state, 3)
    with pytest.raises(ValueError):
        LearnedAction(0, 0, len(MACRO_ACTIONS), 0)
    with pytest.raises(ValueError):
        LearnedSample.from_dict({**sample.to_dict(), "action_version": "director-action-v0"})


def test_macro_query_ownership_reserves_and_one_paid_attempt(bot, make_unit, populate):
    nexus = make_unit(U.NEXUS)
    selected = make_unit(U.NEXUS, (10, 0), is_selected=True)
    populate(nexus, selected)
    skill = MacroSkill()
    ability = TRAIN_INFO[U.NEXUS][U.PROBE]["ability"]
    bot.get_available_abilities = AsyncMock(return_value=[[ability]])
    asyncio.run(skill.refresh(bot))
    assert set(skill.abilities) == {nexus.tag}
    assert skill.allowed(bot, "probe")
    bot.control.settings.reserve_minerals = 999
    assert not skill.allowed(bot, "probe")
    bot.control.settings.reserve_minerals = 0
    bot.supply_left = 0
    assert not skill.allowed(bot, "probe")
    bot.supply_left = 10
    state = independent()
    result = decode(chosen(state, macro=1), state, 1)
    skill.propose(result)
    asyncio.run(skill.execute(bot))
    asyncio.run(skill.execute(bot))
    assert len(bot.actions) == 1
    assert bot.actions[0].unit.tag == nexus.tag
    assert skill.feedback[-1]["status"] == "queued"
    assert bot.minerals == 950
    bot._used.clear()
    bot.control.released.add(nexus.tag)
    skill.propose(result)
    asyncio.run(skill.execute(bot))
    assert len(bot.actions) == 1 and skill.feedback[-1]["status"] == "no_longer_available"


def test_macro_builds_only_requested_structure_and_records_failed_placement(
    bot, make_unit, populate, monkeypatch
):
    from source.games.starcraft2 import learned_execution

    worker = make_unit(U.PROBE)
    populate(worker)
    bot.client.query_pathing = AsyncMock(return_value=1)
    skill = MacroSkill()
    skill.abilities = {worker.tag: {TRAIN_INFO[U.PROBE][U.PYLON]["ability"]}}
    state = independent()
    skill.propose(decode(chosen(state, macro=2), state, 1))
    monkeypatch.setattr(learned_execution, "find_spaced_placement", AsyncMock(return_value=None))
    asyncio.run(skill.execute(bot))
    assert not bot.actions and skill.feedback[-1]["status"] == "execution_failed"
    skill.propose(decode(chosen(state, macro=2), state, 2))
    monkeypatch.setattr(learned_execution, "find_spaced_placement", AsyncMock(return_value=worker.position))
    asyncio.run(skill.execute(bot))
    assert len(bot.actions) == 1 and worker.tag in bot.construction_reservations


def test_gas_staffing_routes_owned_workers_without_overriding_selection(bot, make_unit, populate):
    from s2clientprotocol import raw_pb2

    gas = make_unit(U.ASSIMILATOR, (3, 0), vespene_contents=1000, assigned_harvesters=1)
    mineral = make_unit(U.MINERALFIELD, (2, 0), alliance=3, mineral_contents=1000)
    worker = make_unit(
        U.PROBE, orders=[raw_pb2.UnitOrder(ability_id=A.HARVEST_GATHER.value, target_unit_tag=gas.tag)]
    )
    selected = make_unit(U.PROBE, is_selected=True)
    populate(make_unit(U.NEXUS), gas, mineral, worker, selected)
    skill = MacroSkill()
    skill.gas_staffing = 0
    asyncio.run(skill.allocate(bot))
    assert len(bot.actions) == 1 and bot.actions[0].unit.tag == worker.tag
    assert bot.actions[0].target.tag == mineral.tag


def test_training_runtime_bypasses_rule_director_macro_and_mission_abort(
    bot, make_unit, populate, monkeypatch
):
    import queue
    import threading

    from source.economy_assistant import EconomyAssistant
    from source.games.starcraft2.environment import Effects, EnvironmentDirector, TrainingAssistant
    from source.games.starcraft2.learned_execution import DisabledReinforcement, LearnedTactics

    actor = make_unit(U.STALKER, (0, 0), health=5, shield=0)
    populate(actor)
    bot.control.settings.attack = True
    state = independent()
    sample = chosen(state, target=1)
    environment = SimpleNamespace(
        controller="learned",
        closed=threading.Event(),
        actions=queue.Queue(),
        events=queue.Queue(),
        inference_timeout=1,
        lease=SimpleNamespace(release=Mock()),
    )
    instance = TrainingAssistant(bot.settings, SimpleNamespace(data={}), environment)
    assert isinstance(instance.tactics, LearnedTactics)
    assert isinstance(instance.reinforcement, DisabledReinforcement)
    assert instance.tactics.director.rule is None
    bot.adapter = SimpleNamespace(observe=Mock(return_value=state))
    bot.macro_skill = SimpleNamespace(
        observe=lambda _bot, b: b, feedback=[], propose=Mock(), execute=AsyncMock()
    )
    bot.previous_decision, bot.last_decoded, bot.issued, bot.manifest = None, None, [], {}
    bot.effects = Effects()
    bot.environment = environment
    tactics = LearnedTactics()
    tactics.assessor.observe = Mock(return_value=state.assessment)
    tactics.missions.execute = Mock(side_effect=AssertionError("Rule mission planner must not run"))
    tactics.director = EnvironmentDirector(bot, environment)
    environment.actions.put(sample)
    result = tactics.tick(bot)
    assert result["strategy"] == "push" and bot.actions
    assert bot.actions[0].unit.tag == actor.tag
    assert not tactics.director.blocked
    tactics.director.report_failure("rally", state.assessment.time)
    assert not tactics.director.blocked
    monkeypatch.setattr(
        EconomyAssistant, "macro", AsyncMock(side_effect=AssertionError("Rule macro must not run"))
    )
    asyncio.run(TrainingAssistant.macro(bot))
    bot.macro_skill.execute.assert_awaited_once()
    bot.macro_skill.propose.assert_called_once()


def test_live_macro_features_include_legal_choices_and_own_progress(bot, make_unit, populate):
    populate(make_unit(U.NEXUS), make_unit(U.PROBE))
    bot.supply_cap = 15
    skill = MacroSkill()
    skill.abilities = {u.tag: {TRAIN_INFO[U.NEXUS][U.PROBE]["ability"]} for u in bot.townhalls}
    state = skill.observe(bot, independent())
    values = {f.name: f.value for f in state.shared.features}
    assert state.macro_mask[1]
    assert values["macro.probe.completed"] == 0.05
    assert values["macro.pylon.available"] == 0
    assert state.shared.feature_version == FEATURE_VERSION
    bot.get_available_abilities = AsyncMock(return_value=[])
    with pytest.raises(ValueError, match="Incomplete"):
        asyncio.run(skill.refresh(bot))


def neural_records(model, policy_id):
    states = [independent(), independent(102, 2285, False)]
    memory = model.core.initial()
    with torch.no_grad():
        logits, value, hidden = model(states[0], memory)
        sample = sample_action(logits.tolist(), states[0], random.Random(4))
    return [
        TransitionV1(
            "synthetic-episode",
            0,
            policy_id,
            states[0],
            decode(sample, states[0], 1),
            states[1],
            tuple(memory[0].tolist()),
            tuple(hidden[0].tolist()),
            value.item(),
            None,
            Outcome("victory"),
        )
    ]


def test_independent_checkpoint_optimizer_and_original_rollout_contracts(tmp_path):
    model = LearnedPolicy()
    config = PPOConfig(epochs=1, sequence_length=2, burn_in=0, learning_rate=5e-5)
    data = save_checkpoint(tmp_path / "initial", model, seed=17)
    records = neural_records(model, data["policy_id"])
    metadata = manifest(
        data["policy_id"],
        action_version=ACTION_VERSION,
        feature_version=FEATURE_VERSION,
        decoder_version=DECODER_VERSION,
    )
    writer = EpisodeWriter(tmp_path / "rollout", metadata)
    writer.append(records[0])
    writer.finish(Outcome("victory"))
    episode = load_episode(tmp_path / "rollout")
    optimizer, first = update(model, [episode], data["policy_id"], config)
    assert first["optimizer_steps"] == 1
    saved = save_checkpoint(tmp_path / "trained", model, seed=17, optimizer=optimizer, optimizer_steps=1)
    restored, loaded = load_checkpoint(tmp_path / "trained")
    resumed = restore_optimizer(tmp_path / "trained", restored, config)
    assert loaded == saved and resumed.state_dict()["state"]
    assert max(v["step"].item() for v in resumed.state.values()) == 1
    next_records = neural_records(restored, loaded["policy_id"])
    resumed, second = update(
        restored,
        [(manifest(loaded["policy_id"]), next_records)],
        loaded["policy_id"],
        config,
        optimizer=resumed,
    )
    assert second["optimizer_steps"] == 1
    assert max(v["step"].item() for v in resumed.state.values()) == 2
    with pytest.raises(ValueError):
        restore_optimizer(tmp_path / "trained", restored, PPOConfig(learning_rate=0.01))
    with pytest.raises(ValueError):
        update(
            restored,
            [(manifest(), neural_records(LearnedPolicy(), "synthetic-reference"))],
            "synthetic-reference",
            config,
            optimizer=optimizer,
        )


def test_curriculum_runs_two_rounds_and_resumes_without_recollecting(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "repository_identity", lambda: "a" * 40)
    monkeypatch.setattr(cli, "benchmark", lambda *args: {"scope": "synthetic"})

    def synthetic_collect(
        config, installation, map_path, output, model, policy_id, split, controller, **kwargs
    ):
        if output.exists():
            return json.loads((output / "summary.json").read_text())
        assert config["opponent"]["difficulty"] == "Easy" and controller == "learned"
        calls.append((config["seed"], split))
        records = neural_records(model, policy_id)
        metadata = manifest(
            policy_id,
            split=split,
            action_version=ACTION_VERSION,
            feature_version=FEATURE_VERSION,
            decoder_version=DECODER_VERSION,
        )
        writer = EpisodeWriter(output / "synthetic-episode/rollout", metadata)
        writer.append(records[0])
        writer.finish(Outcome("victory"))
        summary = [{"episode_id": "synthetic-episode", "outcome": "victory"}]
        cli.atomic_json(output / "summary.json", summary)
        return summary

    monkeypatch.setattr(cli, "collect", synthetic_collect)
    executable, game_map = tmp_path / "exe", tmp_path / "map"
    executable.write_bytes(b"synthetic")
    game_map.write_bytes(b"synthetic")
    config = json.loads((cli.ROOT / "config/training/easy.json").read_text())
    config["ppo"] = {"epochs": 1, "sequence_length": 2, "burn_in": 0, "learning_rate": 5e-5}
    args = (config, SimpleNamespace(executable=executable), game_map, tmp_path / "training")
    result = cli.train(*args)
    assert calls == [(31, "train"), (131, "development"), (32, "train"), (131, "development")]
    assert result[-1]["optimizer_steps"] == 2
    assert cli.train(*args, resume=True) == result
    assert len(calls) == 4
    with pytest.raises(ValueError, match="original source"):
        cli.train({**config, "model_seed": 18}, *args[1:], resume=True)
    with pytest.raises(ValueError, match="requires Easy"):
        cli.train({**config, "opponent": {**config["opponent"], "difficulty": "VeryHard"}}, *args[1:])
