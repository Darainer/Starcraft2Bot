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


def test_expansion_metrics_distinguish_scouting_from_committed_force(tmp_path):
    report = tmp_path / "runtime.json"
    report.write_text('{"phase":"ended","result":"Victory"}')
    row = {
        "game_loop": 224,
        "decision": {
            "strategy": "push",
            "assessment": {"targets": [{"id": "third", "expansion": True}]},
            "missions": {"denial": {"role": "deny", "target_id": "third", "supply": 8, "phase": "travel"}},
        },
        "scouting": {
            "observer": {"phase": "scouting_expansion"},
            "intel": {
                "expansion_sites": [{"position": [60, 60], "status": "empty", "last_checked": 10}],
                "known_enemy_bases": [{"expansion": True}, {"expansion": False}],
            },
        },
        "observation": {"observation": {"raw_data": {"units": []}}},
    }
    first = json.dumps(row)
    row["game_loop"] = 448
    row["decision"]["missions"]["denial"]["supply"] = 0
    report.with_suffix(".state.jsonl").write_text(first + "\n" + json.dumps(row) + "\n")
    metrics = summarize(report)["performance"]
    assert metrics["expansion_scout_samples"] == 2
    assert metrics["inspected_expansion_sites"] == 1
    assert metrics["peak_known_enemy_expansions"] == 1
    assert metrics["expansion_target_samples"] == metrics["denial_squad_samples"] == 1
    assert metrics["first_expansion_advance_seconds"] == 10


def test_initial_state_signature_detects_spawn_changes_not_protocol_tags(tmp_path):
    report = tmp_path / "runtime.json"
    report.write_text('{"phase":"ended","random_seed":42,"opponent_build":"Macro"}')
    units = [
        {"unit_type": 59, "tag": 1, "alliance": "Self", "pos": {"x": 30, "y": 40}},
        {"unit_type": 84, "tag": 2, "alliance": "Self", "pos": {"x": 31, "y": 40}},
    ]
    row = {
        "game_loop": 0,
        "decision": {"strategy": "regroup"},
        "observation": {"observation": {"raw_data": {"units": units}}},
    }
    snapshots = report.with_suffix(".state.jsonl")
    snapshots.write_text(json.dumps(row) + "\n")
    signature = summarize(report)["initial_state_sha256"]
    units.reverse()
    units[0]["tag"] = 99
    snapshots.write_text(json.dumps(row) + "\n")
    assert summarize(report)["initial_state_sha256"] == signature
    units[0]["pos"]["x"] = 70
    snapshots.write_text(json.dumps(row) + "\n")
    assert summarize(report)["initial_state_sha256"] != signature


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
