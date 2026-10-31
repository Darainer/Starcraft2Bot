import copy
import json

import pytest
from s2clientprotocol import sc2api_pb2 as pb
from sc2.ids.unit_typeid import UnitTypeId as U

from source.opponent_dataset import digest, export_dataset, main, public_map_context, split_group
from tests.test_scouting_facts import sample


def world():
    return {
        "units": [{"unit_type": 59, "pos": {"x": 1, "y": 2}}],
        "scenario": {
            "map_sha256": "map",
            "ping": {"base_build": 98310},
            "random_seed": 1,
            "opponent_race": "Zerg",
            "opponent_build": "Timing",
        },
    }


def test_splits_keep_all_builds_repeats_scout_policies_and_bot_versions_together():
    first = {"initial_state": world()}
    other = copy.deepcopy(first)
    other["initial_state"]["scenario"]["opponent_build"] = "Macro"
    other.update(source_commit="different", scout_revisit=True)
    other["initial_state"]["settings"] = {"workers": False}
    assert split_group(first) == split_group(other)
    other["initial_state"]["scenario"]["random_seed"] = 2
    assert split_group(first) != split_group(other)
    with pytest.raises(ValueError, match="identity"):
        split_group({})


def test_public_map_context_excludes_hidden_player_metadata():
    initial = world()
    info = {
        "start_raw": {"start_locations": [{"x": 1, "y": 2}, {"x": 90, "y": 90}, {"x": 30, "y": 90}]},
        "player_info": [{"actual_hidden_spawn": [90, 90], "ai_build": "Macro"}],
    }
    context = public_map_context({"initial_state": initial}, info)
    assert context["possible_enemy_starts"] == [[90, 90], [30, 90]]
    assert "Macro" not in json.dumps(context)
    assert public_map_context({}, info) is None


def recording(tmp_path, phase="ended"):
    path = tmp_path / "original/logs/game.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"phase": phase, "opponent_build": "Timing", "result": "Result.Victory"}))
    rows = [sample(0), sample(10)]
    path.with_suffix(".state.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    data = pb.ResponseData(units=[{"unit_id": U.ROACH.value, "food_required": 2}])
    path.with_suffix(".game-data.pb").write_bytes(data.SerializeToString())
    path.with_suffix(".console.log").write_text("console")
    path.with_suffix(".2026-10-31.log").write_text("rotated debug")
    (path.parent.parent / "candidate-manifest.json").write_text('{"source_commit":"abc123"}')
    replay = tmp_path / "original/game.SC2Replay"
    replay.write_bytes(b"replay")
    return {"report": str(path), "replay": str(replay), "initial_state": world()}


def test_export_archives_every_surviving_artifact_and_separates_labels(tmp_path):
    match = recording(tmp_path)
    original_hash = digest(match["report"])
    output = tmp_path / "dataset"
    result = export_dataset([match], output)
    assert result["phase"] == "complete" and result["split_groups"] == 1
    episode = result["episodes"][0]
    assert episode["examples"] == 2 and episode["eligible_for_learning"]
    assert episode["source_commit"] == "abc123"
    assert len(episode["artifacts"]) == 7
    for asset in episode["artifacts"]:
        assert digest(output / asset["file"]) == asset["sha256"]
    assert digest(match["report"]) == original_hash
    facts = (output / episode["facts"]).read_text()
    assert "Timing" not in facts and "Victory" not in facts and "episode_id" not in facts
    assert json.loads((output / "labels.json").read_text())[0]["configured_build"] == "Timing"
    with pytest.raises(FileExistsError):
        export_dataset([match], output)


def test_running_recordings_are_not_copied_as_complete(tmp_path):
    match = recording(tmp_path, "observing")
    with pytest.raises(ValueError, match="still being written"):
        export_dataset([match], tmp_path / "out")
    assert json.loads((tmp_path / "out/manifest.json").read_text())["phase"] == "building"


def test_failed_no_snapshot_run_is_archived_but_not_training_data(tmp_path):
    path = tmp_path / "failed.json"
    path.write_text('{"phase":"failed", "error":"launch"}')
    result = export_dataset([{"report": str(path)}], tmp_path / "out")
    assert result["split_groups"] == 0
    assert not result["episodes"][0]["eligible_for_learning"]


def test_dataset_cli_and_invalid_input(tmp_path, capsys):
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps([recording(tmp_path)]))
    main(["--matrix", str(matrix), "--output", str(tmp_path / "out")])
    assert json.loads(capsys.readouterr().out)["episodes"] == 1
    with pytest.raises(SystemExit) as exc:
        main(["--matrix", str(tmp_path / "missing"), "--output", str(tmp_path / "other")])
    assert exc.value.code == 2
