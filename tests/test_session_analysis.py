import json
import subprocess
import sys
from pathlib import Path

import pytest

from source.analyze_session import main, summarize


def test_sampled_milestones_and_upgrades(tmp_path, capsys):
    report = tmp_path / "runtime.json"
    report.write_text('{"phase":"ended","result":"Victory"}')
    row = {
        "game_loop": 224,
        "decision": {"strategy": "push"},
        "observation": {
            "observation": {
                "player_common": {"minerals": 123},
                "raw_data": {
                    "units": [{"unit_type": 59, "alliance": "Self", "build_progress": 1}],
                    "player": {"upgrade_ids": [39]},
                },
            }
        },
    }
    report.with_suffix(".state.jsonl").write_text(json.dumps(row) + "\n")
    summary = summarize(report)
    assert summary["first_completed_seconds"]["NEXUS"] == 10
    assert summary["completed_upgrades"]
    assert summary["player"]["minerals"] == 123
    main([str(report)])
    assert json.loads(capsys.readouterr().out)["result"] == "Victory"
    report.with_suffix(".state.jsonl").write_text("")
    with pytest.raises(SystemExit):
        main([str(report)])


@pytest.mark.skipif(sys.platform != "win32", reason="Native PowerShell argument binding")
def test_control_wrapper_remaining_arguments_and_named_report(tmp_path):
    root = Path(__file__).resolve().parents[1]
    report = tmp_path / "runtime.json"
    report.write_text('{"phase":"observing","local_control":true}')
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(root / "Control.ps1"),
            "-Report",
            str(report),
            "strategy",
            "retreat",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    queued = json.loads(report.with_suffix(".command.json").read_text())
    assert queued["command"] == "!assist strategy retreat"
