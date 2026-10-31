import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from types import SimpleNamespace

import pytest

from source import trials


def test_simultaneous_runners_with_same_clock_have_disjoint_artifact_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(trials, "ROOT", tmp_path)
    (tmp_path / ".local").mkdir()
    (tmp_path / ".local/windows.json").write_text('{"sc2_path":"game","map_file":"map"}')

    monkeypatch.setattr(trials, "datetime", SimpleNamespace(now=lambda: datetime(2026, 10, 31)))
    barrier, lock = threading.Barrier(2), threading.Lock()
    commands = []

    def run(command, **kwargs):
        with lock:
            commands.append(command)
        barrier.wait(timeout=5)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(trials.subprocess, "run", run)
    monkeypatch.setattr(
        trials,
        "summarize",
        lambda path: {"result": "Result.Victory", "error": None},
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(trials.main, ["--profiles", "pressure", "--output", f"logs/{name}.json"])
            for name in ("rush", "power")
        ]
        for future in futures:
            future.result()
    for flag in ("--runtime-report", "--log-file", "--replay"):
        assert len({command[command.index(flag) + 1] for command in commands}) == 2
    assert len(list((tmp_path / "logs").glob("*.console.log"))) == 2
    assert all(
        len(json.loads((tmp_path / f"logs/{name}.json").read_text())) == 1 for name in ("rush", "power")
    )


def test_trials_run_sequential_bounded_games_and_write_summary(monkeypatch, tmp_path):
    monkeypatch.setattr(trials, "ROOT", tmp_path)
    (tmp_path / ".local").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / ".local/windows.json").write_text('{"sc2_path":"game","map_file":"map"}')
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        report = trials.Path(command[command.index("--runtime-report") + 1])
        report.write_text('{"phase":"ended"}')
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(trials.subprocess, "run", run)
    monkeypatch.setattr(
        trials,
        "summarize",
        lambda path: {
            "result": "Result.Tie",
            "error": None,
            "initial_state_sha256": "same",
            "initial_state": {"game_loop": 0},
        },
    )
    trials.main(
        [
            "--profiles",
            "pressure",
            "air",
            "--duration",
            "600",
            "--seed",
            "42",
            "--opponent-build",
            "Macro",
            "--snapshot-interval",
            "1",
            "--scout-revisit",
            "--composition-policy",
            "scouted",
            "--oracle-harass",
            "--oracle-beam",
            "--archon-merge",
            "--defend-assets",
            "--local-regroup",
        ]
    )
    assert len(commands) == 2
    assert all("--fast-test" in command and "600" in command for command in commands)
    assert all(command[command.index("--seed") + 1] == "42" for command in commands)
    assert all(command[command.index("--opponent-build") + 1] == "Macro" for command in commands)
    assert all(
        command[command.index("--snapshot-interval") + 1] == "1" and "--scout-revisit" in command
        for command in commands
    )
    results = json.loads((tmp_path / "logs/latest-trials.json").read_text())
    assert [r["profile"] for r in results] == ["pressure", "air"]
    assert all(r["random_seed"] == 42 and r["opponent_build"] == "Macro" for r in results)
    for flag in ("oracle_harass", "oracle_beam", "archon_merge", "defend_assets", "local_regroup"):
        assert all("--" + flag.replace("_", "-") in command for command in commands)
        assert all(r[flag] is True for r in results)
    assert all(r["composition_policy"] == "scouted" for r in results)
    trials.main(["--profiles", "balanced", "--realtime"])
    assert "--fast-test" not in commands[-1]
    assert commands[-1][commands[-1].index("--game-time-limit") + 1] == "3600"


def test_trials_report_runtime_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(trials, "ROOT", tmp_path)
    (tmp_path / ".local").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / ".local/windows.json").write_text('{"sc2_path":"game","map_file":"map"}')
    monkeypatch.setattr(trials.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=1))
    with pytest.raises(SystemExit) as exc:
        trials.main(["--profiles", "pressure"])
    assert exc.value.code == 1


def test_matrix_runs_three_concurrently_with_isolated_outputs_and_fixed_seed(monkeypatch, tmp_path):
    monkeypatch.setattr(trials, "ROOT", tmp_path)
    (tmp_path / ".local").mkdir()
    (tmp_path / ".local/windows.json").write_text('{"sc2_path":"game","map_file":"map"}')
    barrier, lock = threading.Barrier(3), threading.Lock()
    commands, completed = [], []
    active = peak = 0

    def run(command, **kwargs):
        nonlocal active, peak
        opponent = command[command.index("--opponent") + 1]
        with lock:
            if opponent == "Zerg":
                assert completed.count("Terran") == 3
            active += 1
            peak = max(peak, active)
            commands.append(command)
        assert kwargs["env"]["PYTHONHASHSEED"] == "20261025"
        barrier.wait(timeout=5)
        with lock:
            completed.append(opponent)
            active -= 1
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(trials.subprocess, "run", run)
    monkeypatch.setattr(
        trials,
        "summarize",
        lambda path: {
            "result": "Result.Victory",
            "error": None,
            "initial_state_sha256": "same",
            "initial_state": {"game_loop": 0},
        },
    )
    trials.main(
        [
            "--profiles",
            "pressure",
            "--opponents",
            "Terran",
            "Zerg",
            "--builds",
            "Rush",
            "--repeat",
            "3",
            "--parallel",
            "3",
            "--seed",
            "20261025",
            "--output",
            "logs/matrix.json",
        ]
    )
    assert peak == 3 and active == 0 and len(commands) == 6
    for flag in ("--runtime-report", "--log-file", "--replay"):
        assert len({command[command.index(flag) + 1] for command in commands}) == 6
    assert all(command[command.index("--seed") + 1] == "20261025" for command in commands)
    assert len(json.loads((tmp_path / "logs/matrix.json").read_text())) == 6


def test_seeded_matrix_stops_when_initial_conditions_differ(monkeypatch, tmp_path):
    monkeypatch.setattr(trials, "ROOT", tmp_path)
    (tmp_path / ".local").mkdir()
    (tmp_path / ".local/windows.json").write_text('{"sc2_path":"game","map_file":"map"}')
    monkeypatch.setattr(trials.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0))
    monkeypatch.setattr(
        trials,
        "summarize",
        lambda path: {
            "result": "Result.Victory",
            "error": None,
            "initial_state_sha256": path.stem,
            "initial_state": {"game_loop": 0},
        },
    )
    with pytest.raises(SystemExit) as exc:
        trials.main(
            [
                "--profiles",
                "pressure",
                "--repeat",
                "3",
                "--parallel",
                "3",
                "--seed",
                "42",
                "--builds",
                "Rush",
                "Macro",
            ]
        )
    assert exc.value.code == 1
    results = json.loads((tmp_path / "logs/latest-trials.json").read_text())
    assert len(results) == 3 and all(not r["starting_conditions_match"] for r in results)


@pytest.mark.parametrize("parallel", [5, 8])
def test_clients_overlap_scenarios_and_validate_each_triplet(monkeypatch, tmp_path, parallel):
    monkeypatch.setattr(trials, "ROOT", tmp_path)
    (tmp_path / ".local").mkdir()
    (tmp_path / ".local/windows.json").write_text('{"sc2_path":"game","map_file":"map"}')
    barrier, lock = threading.Barrier(parallel), threading.Lock()
    active = peak = launched = 0
    races = {}

    def run(command, **kwargs):
        nonlocal active, peak, launched
        report = command[command.index("--runtime-report") + 1]
        with lock:
            launched += 1
            index = launched
            active += 1
            peak = max(peak, active)
            races[report] = command[command.index("--opponent") + 1]
        if index <= parallel:
            barrier.wait(timeout=5)
        with lock:
            active -= 1
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(trials.subprocess, "run", run)
    monkeypatch.setattr(
        trials,
        "summarize",
        lambda path: {
            "result": "Result.Victory",
            "sampled_game_seconds": 600,
            "initial_state_sha256": races[str(path)],
            "initial_state": {"game_loop": 0},
        },
    )
    trials.main(
        [
            "--profiles",
            "pressure",
            "--opponents",
            "Terran",
            "Zerg",
            "--builds",
            "Rush",
            "Timing",
            "--repeat",
            "3",
            "--parallel",
            str(parallel),
            "--seed",
            "42",
        ]
    )
    results = json.loads((tmp_path / "logs/latest-trials.json").read_text())
    assert peak == parallel and active == 0 and len(races) == len(results) == 12
    assert [r["opponent"] for r in results] == ["Terran"] * 6 + ["Zerg"] * 6
    assert all(r["starting_conditions_match"] and r["wall_seconds"] >= 0 for r in results)
    assert all(r["game_seconds_per_wall_second"] > 0 for r in results)


@pytest.mark.parametrize("args", [["--repeat", "0"], ["--duration", "0"], ["--parallel", "9"]])
def test_trial_bounds(args):
    with pytest.raises(SystemExit) as exc:
        trials.main(args)
    assert exc.value.code == 2
