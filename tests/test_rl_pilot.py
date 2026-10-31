"""Exercise orchestration with an explicitly synthetic environment, never SC2."""

import json
from types import SimpleNamespace

import pytest

pytest.importorskip("torch")

from test_rl_learning import belief, manifest

from source.games.starcraft2.action_codec import decode
from source.training import cli
from source.training.collector import load_episode
from source.training.records import Outcome


class SyntheticEnvironment:
    def __init__(self, installation, map_path, output, **kwargs):
        self.output = output
        self.episode_id = "synthetic-episode"
        self.episode_directory = output / self.episode_id
        self.episode_directory.mkdir()
        self.current = belief()
        self.done = False
        self.worker = None

    def reset(self, seed, metadata):
        self.metadata = manifest(**metadata)
        return self.current, {"manifest": self.metadata}

    def step(self, sampled):
        after = belief(102, 2285, False)
        event = {
            "belief": after,
            "outcome": Outcome("victory"),
            "decoded": decode(sampled, self.current, 1) if sampled else None,
            "issued": [{"id": "synthetic-queued"}],
            "effects": [{"id": "synthetic-observed"}],
        }
        self.done = True
        return after, 1, True, False, event

    def close(self):
        pass


def test_complete_collect_update_reload_evaluate_and_benchmark_pipeline(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "LocalEnvironment", SyntheticEnvironment)
    monkeypatch.setattr(cli, "repository_identity", lambda: "a" * 40)
    monkeypatch.setattr(cli, "live_client_count", lambda: 0)
    executable = tmp_path / "synthetic-exe"
    executable.write_bytes(b"not an executable")
    game_map = tmp_path / "synthetic-map"
    game_map.write_bytes(b"not a map")
    config = json.loads((cli.ROOT / "config/training/pilot.json").read_text())
    config.update(repeats=1, ppo={"epochs": 1, "sequence_length": 2, "burn_in": 0})
    result = cli.pilot(config, SimpleNamespace(executable=executable), game_map, tmp_path / "pilot")
    assert result["trained_policy"]["optimizer_steps"] == 1
    assert result["initial_policy"]["policy_id"] != result["trained_policy"]["policy_id"]
    assert result["benchmark"]["model_parameters"] > 600_000
    assert result["playing_strength_accepted"] is False
    _, records = load_episode(tmp_path / "pilot/train/synthetic-episode/rollout")
    assert records[0].issued_intent_ids == ("synthetic-queued",)
    assert records[0].observed_effect_ids == ("synthetic-observed",)
    assert (tmp_path / "pilot/pilot-results.json").is_file()


@pytest.mark.parametrize(
    "change",
    [{"time_limit": 0}, {"repeats": 0}, {"step_size": 128}, {"seed": None}, {"opponent": {"race": "Random"}}],
)
def test_invalid_pilot_configuration_is_rejected_before_launch(change):
    config = json.loads((cli.ROOT / "config/training/pilot.json").read_text())
    with pytest.raises(ValueError):
        cli.validate_config({**config, **change})
