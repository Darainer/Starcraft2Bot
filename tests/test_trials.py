import json
from types import SimpleNamespace

import pytest

from source import trials


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
    monkeypatch.setattr(trials, "summarize", lambda path: {"result": "Result.Tie", "error": None})
    trials.main(["--profiles", "pressure", "air", "--duration", "600"])
    assert len(commands) == 2
    assert all("--fast-test" in command and "600" in command for command in commands)
    results = json.loads((tmp_path / "logs/latest-trials.json").read_text())
    assert [r["profile"] for r in results] == ["pressure", "air"]
    trials.main(["--profiles", "balanced", "--realtime"])
    assert "--fast-test" not in commands[-1]


def test_trials_report_runtime_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(trials, "ROOT", tmp_path)
    (tmp_path / ".local").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / ".local/windows.json").write_text('{"sc2_path":"game","map_file":"map"}')
    monkeypatch.setattr(trials.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=1))
    with pytest.raises(SystemExit) as exc:
        trials.main(["--profiles", "pressure"])
    assert exc.value.code == 1


@pytest.mark.parametrize("args", [["--repeat", "0"], ["--duration", "0"]])
def test_trial_bounds(args):
    with pytest.raises(SystemExit) as exc:
        trials.main(args)
    assert exc.value.code == 2
