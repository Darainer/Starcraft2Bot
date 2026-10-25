import json

import pytest
from google.protobuf.json_format import MessageToDict
from s2clientprotocol import sc2api_pb2 as pb
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.benchmark_controllers import benchmark, distribution, main
from source.economy_assistant import EconomyAssistant
from source.runtime import recorded_observations


@pytest.fixture
def recording(bot, make_unit, tmp_path, monkeypatch):
    path = tmp_path / "recording.json"
    path.write_text('{"ping":{"base_build":98310},"opponent_difficulty":"VeryHard"}')
    bot.game_data.units[U.NEXUS.value]._proto.attributes.append(8)  # Structure
    data = pb.ResponseData(
        abilities=[entry._proto for entry in bot.game_data.abilities.values()],
        units=[entry._proto for entry in bot.game_data.units.values()],
        upgrades=[entry._proto for entry in bot.game_data.upgrades.values()],
    )
    path.with_suffix(".game-data.pb").write_bytes(data.SerializeToString())
    info = pb.ResponseGameInfo(map_name="Synthetic benchmark")
    info.player_info.add(player_id=1, race_actual=3)
    info.player_info.add(player_id=2, race_actual=1)
    raw = info.start_raw
    raw.map_size.x = raw.map_size.y = 32
    raw.playable_area.p1.x = raw.playable_area.p1.y = 32
    raw.start_locations.add(x=25, y=25)
    for grid in (raw.pathing_grid, raw.placement_grid, raw.terrain_height):
        grid.size.x = grid.size.y = 32
        grid.bits_per_pixel = 8 if grid is raw.terrain_height else 1
        grid.data = bytes([255]) * (1024 if grid.bits_per_pixel == 8 else 128)
    path.with_suffix(".game-info.json").write_text(json.dumps(MessageToDict(info)))
    observation = pb.ResponseObservation()
    observation.observation.player_common.player_id = 1
    state = observation.observation.raw_data
    state.units.extend([make_unit(U.NEXUS, (5, 5))._proto, make_unit(U.STALKER, (8, 8))._proto])
    for grid, bits, byte in ((state.map_state.visibility, 8, 2), (state.map_state.creep, 1, 0)):
        grid.size.x = grid.size.y = 32
        grid.bits_per_pixel = bits
        grid.data = bytes([byte]) * (1024 if bits == 8 else 128)
    rows = []
    for loop in (0, 224):
        observation.observation.game_loop = loop
        rows.append(
            {
                "observation": MessageToDict(observation),
                "settings": {
                    "attack": True,
                    "scouting": False,
                    "strategy_script": "do-not-execute-this.py",
                },
                "released_unit_tags": [],
            }
        )
    path.with_suffix(".state.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    def prepare_start(bot):
        bot.game_info.player_start_location = bot.townhalls.first.position
        bot._expansion_positions_list = [Point2((20, 20))]

    # Topology discovery is unrelated to the replay/measurement contract.
    monkeypatch.setattr(EconomyAssistant, "_prepare_first_step", prepare_start)
    return path


def test_recorded_adapter_has_no_client_and_never_executes_script(recording):
    loops = []
    for bot, _row in recorded_observations(recording):
        assert bot.client is None
        assert bot.settings.strategy_script == ""
        assert bot.townhalls and len(bot.units) == 1
        assert not bot.actions
        loops.append(bot.state.game_loop)
    assert loops == [0, 224]


def test_measurement_and_cli(recording, tmp_path, capsys):
    result = benchmark(recording, repeat=2)
    assert result["evaluations"] == 4 and result["snapshots_per_pass"] == 2
    assert result["ownership_or_duplicate_order_violations"] == 0
    assert result["stage_costs"]["total"]["max_ms"] >= result["stage_costs"]["total"]["p50_ms"]
    assert distribution([1, 2, 3, 4, 5])["p95_ms"] == 5
    output = tmp_path / "timings.json"
    main([str(recording), "--repeat", "1", "--output", str(output)])
    assert json.loads(output.read_text())[0]["evaluations"] == 2
    assert json.loads(capsys.readouterr().out)[0]["proposed_orders"] >= 0
    with pytest.raises(SystemExit):
        main([str(recording), "--repeat", "0"])


def test_recording_rejects_time_reversal_missing_base_and_empty_input(recording):
    snapshots = recording.with_suffix(".state.jsonl")
    lines = snapshots.read_text().splitlines()
    snapshots.write_text(lines[1] + "\n" + lines[0] + "\n")
    with pytest.raises(ValueError, match="monotonically"):
        list(recorded_observations(recording))
    row = json.loads(lines[0])
    row["observation"]["observation"]["rawData"]["units"] = []
    snapshots.write_text(json.dumps(row) + "\n")
    with pytest.raises(ValueError, match="starting base"):
        list(recorded_observations(recording))
    snapshots.write_text("")
    with pytest.raises(ValueError, match="no observations"):
        benchmark(recording)
