import asyncio
import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from s2clientprotocol import data_pb2, raw_pb2
from s2clientprotocol import sc2api_pb2 as pb
from sc2.data import Difficulty, Race, Result, Status
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer
from sc2.unit import UnitOrder

from source import runtime
from source.assistant_control import AssistantSettings
from source.economy_assistant import EconomyAssistant


def test_retail_order_alias_uses_game_declared_canonical_ability():
    canonical = AbilityId.HARVEST_GATHER.value
    response = pb.Response(
        data=pb.ResponseData(
            abilities=[
                data_pb2.AbilityData(ability_id=canonical),
                data_pb2.AbilityData(ability_id=4135, remaps_to_ability_id=canonical),
                data_pb2.AbilityData(ability_id=99999),
            ]
        )
    )
    client = runtime.SharedClient(FakeSocket([response]))
    data = asyncio.run(client.get_game_data())
    order = UnitOrder.from_proto(
        raw_pb2.UnitOrder(ability_id=4135, target_unit_tag=123),
        SimpleNamespace(game_data=data),
    )
    assert order.ability.exact_id == AbilityId.HARVEST_GATHER
    assert order.ability.id == AbilityId.HARVEST_GATHER
    assert order.target == 123
    opaque = UnitOrder.from_proto(raw_pb2.UnitOrder(ability_id=99999), SimpleNamespace(game_data=data))
    assert opaque.ability.exact_id.value == 99999
    assert opaque.ability.id.value == 99999
    undocumented = UnitOrder.from_proto(raw_pb2.UnitOrder(ability_id=4137), SimpleNamespace(game_data=data))
    assert undocumented.ability.exact_id.value == 4137
    assert undocumented.ability.id.value == 4137
    assert data.abilities.unknown[-1] == 4137
    assert client.compatibility["ok"] is False  # Incomplete metadata is diagnosed.


def test_complete_command_audit_and_changed_creation_ability(bot):
    from sc2.ids.unit_typeid import UnitTypeId

    data = pb.ResponseData(
        abilities=[a._proto for a in bot.game_data.abilities.values()],
        units=[u._proto for u in bot.game_data.units.values()],
        upgrades=[u._proto for u in bot.game_data.upgrades.values()],
    )
    # The economy fixture deliberately omits unused tech structures. Supply
    # metadata from the SDK manifest so every assistant command can be checked.
    from sc2.dicts.unit_train_build_abilities import TRAIN_INFO

    for kind, info in TRAIN_INFO[UnitTypeId.PROBE].items():
        if kind.value not in bot.game_data.units:
            data.units.add(unit_id=kind.value, available=True, ability_id=info["ability"].value)
    game_data, _, _ = runtime.compatible_game_data(data)
    assert runtime.audit_commands(data, game_data)["ok"]
    game_data.units[UnitTypeId.PROBE.value]._proto.ability_id = AbilityId.MOVE.value
    audit = runtime.audit_commands(data, game_data)
    assert not audit["ok"]
    assert any(not c["ok"] and c["command"] == "NEXUS:PROBE" for c in audit["commands"])


def test_compatibility_blocks_automation_before_on_start(monkeypatch, installation, tmp_path):
    report = runtime.RuntimeReport(tmp_path / "audit.json", installation)
    bot = runtime.RuntimeAssistant(AssistantSettings(), report)
    bot.client = SimpleNamespace(compatibility={"ok": False, "commands": [{"command": "PROBE", "ok": False}]})
    start = AsyncMock()
    monkeypatch.setattr(EconomyAssistant, "on_start", start)
    with pytest.raises(RuntimeError, match="Command compatibility failed: PROBE"):
        asyncio.run(bot.on_start())
    start.assert_not_awaited()
    assert report.data["compatibility"]["ok"] is False


@pytest.fixture
def installation(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime.paths, "PF", "Windows")
    (tmp_path / "Support64").mkdir()
    for build in (75689, 98310):
        executable = tmp_path / "Versions" / f"Base{build}" / "SC2_x64.exe"
        executable.parent.mkdir(parents=True)
        executable.touch()
    return runtime.inspect_installation(tmp_path)


def test_latest_and_strict_legacy_selection(installation):
    assert installation.base_build == 98310
    legacy = runtime.inspect_installation(installation.root, "4.10")
    assert legacy.base_build == 75689
    assert legacy.data_version == "B89B5D6FA7CBF6452E721311BFBC6CB2"
    legacy.executable.unlink()
    with pytest.raises(ValueError, match="not installed"):
        runtime.inspect_installation(installation.root, "4.10")
    with pytest.raises(ValueError, match="Unknown version"):
        runtime.inspect_installation(installation.root, "5.0.17.typo")


def test_missing_install_and_headless_fail(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime.paths, "PF", "Linux")
    with pytest.raises(ValueError, match="PowerShell"):
        runtime.inspect_installation(tmp_path)
    monkeypatch.setattr(runtime.paths, "PF", "Windows")
    with pytest.raises(ValueError, match="No SC2 executable"):
        runtime.inspect_installation(tmp_path)


def test_support64_and_old_build_rejected(installation):
    (installation.root / "Support64").rmdir()
    with pytest.raises(ValueError, match="Support64"):
        runtime.inspect_installation(installation.root)
    for f in (installation.root / "Versions").glob("*/SC2_x64.exe"):
        f.unlink()
    old = installation.root / "Versions/Base123/SC2_x64.exe"
    old.parent.mkdir()
    old.touch()
    with pytest.raises(ValueError, match="predates"):
        runtime.inspect_installation(installation.root)


def test_map_lookup_ambiguity_and_explicit_path(installation):
    root = installation.root
    first = root / "Maps/one/Test.SC2Map"
    first.parent.mkdir(parents=True)
    first.write_bytes(b"map")
    assert runtime.resolve_map(installation, "Test") == first
    second = root / "Maps/two/Test.SC2Map"
    second.parent.mkdir()
    second.touch()
    with pytest.raises(ValueError, match="ambiguous"):
        runtime.resolve_map(installation, "Test")
    assert runtime.resolve_map(installation, "ignored", first) == first
    with pytest.raises(ValueError, match="missing"):
        runtime.resolve_map(installation, "Missing")


def ping(build=98310, status=Status.launched.value, data="CURRENT"):
    return pb.Response(
        status=status,
        ping=pb.ResponsePing(
            game_version="5.0.17.98310", base_build=build, data_build=98310, data_version=data
        ),
    )


def test_ping_verifies_actual_binary_and_data(installation):
    assert runtime.verify_ping(ping(), installation)["base_build"] == 98310
    with pytest.raises(RuntimeError, match="Wrong binary"):
        runtime.verify_ping(ping(build=75689), installation)
    with pytest.raises(RuntimeError, match="ping payload"):
        runtime.verify_ping(pb.Response(), installation)
    old = runtime.inspect_installation(installation.root, "4.10")
    with pytest.raises(RuntimeError, match="Wrong game data"):
        runtime.verify_ping(ping(build=75689), old)
    runtime.verify_ping(ping(build=75689, data=old.data_version.lower()), old)


class FakeSocket:
    """Exercise SDK serialization and join behavior with real protobuf messages."""

    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    async def send_bytes(self, data):
        request = pb.Request()
        request.ParseFromString(data)
        self.requests.append(request)

    async def receive_bytes(self):
        return next(self.responses).SerializeToString()


def test_join_preserves_selection_and_checks_errors():
    ws = FakeSocket([pb.Response(status=3, join_game=pb.ResponseJoinGame(player_id=1))])
    client = runtime.SharedClient(ws)
    assert asyncio.run(client.join_game(race=Race.Protoss)) == 1
    options = ws.requests[0].join_game.options
    assert options.raw and options.score
    assert not options.raw_affects_selection and not options.show_cloaked
    assert not options.HasField("render") and not options.HasField("feature_layer")
    failed = FakeSocket([pb.Response(status=2, join_game=pb.ResponseJoinGame(error=1))])
    with pytest.raises(RuntimeError, match="JoinGame"):
        asyncio.run(runtime.SharedClient(failed).join_game(race=Race.Protoss))


@pytest.fixture
def session_setup(monkeypatch, installation, tmp_path):
    game_map = tmp_path / "Test.SC2Map"
    game_map.write_bytes(b"map bytes")
    report = runtime.RuntimeReport(tmp_path / "report.json", installation, game_map)
    bot = runtime.RuntimeAssistant(AssistantSettings(enabled=False), report)
    players = [Bot(Race.Protoss, bot), Computer(Race.Terran, Difficulty.Easy)]
    server = SimpleNamespace(
        ping=AsyncMock(return_value=ping()),
        _ws=object(),
        _execute=AsyncMock(return_value=pb.Response(create_game=pb.ResponseCreateGame())),
    )

    @asynccontextmanager
    async def connect(*args):
        yield server

    monkeypatch.setattr(runtime, "connection", connect)
    client = SimpleNamespace(save_replay=AsyncMock(), leave=AsyncMock())
    monkeypatch.setattr(runtime, "SharedClient", Mock(return_value=client))
    play = AsyncMock(return_value=Result.Victory)
    monkeypatch.setattr(runtime, "_play_game", play)
    args = (installation, game_map, players, tmp_path / "game.SC2Replay", report)
    return args, server, client, play


def test_local_match_realtime_and_report(session_setup):
    args, server, client, play = session_setup
    asyncio.run(runtime.run_session(*args))
    request = server._execute.call_args.kwargs["create_game"]
    assert request.realtime and not request.disable_fog
    assert request.local_map.map_data == b"map bytes"
    assert len(request.player_setup) == 2
    assert request.player_setup[0].type == 1  # Participant, shared with human
    assert request.player_setup[1].type == 2  # Built-in computer
    assert play.call_args.kwargs == {"realtime": True, "game_time_limit": None}
    assert client.raw_affects_selection is False
    client.save_replay.assert_awaited_once()
    client.leave.assert_awaited_once()
    saved = json.loads(args[-1].path.read_text())
    assert saved["phase"] == "ended"
    assert saved["ping"]["base_build"] == 98310
    assert saved["human_control"] == "not_verified"
    assert len(saved["map_sha256"]) == 64


def test_probe_does_not_create_game(session_setup):
    args, server, client, play = session_setup
    asyncio.run(runtime.run_session(*args, probe=True))
    server._execute.assert_not_awaited()
    play.assert_not_awaited()
    client.leave.assert_not_awaited()
    assert args[-1].data["phase"] == "probe_ok"


@pytest.mark.parametrize("failure", ["busy", "create", "play", "bot", "version"])
def test_failure_paths_are_reported(session_setup, failure):
    args, server, client, play = session_setup
    if failure == "busy":
        server.ping.return_value = ping(status=Status.in_game.value)
    elif failure == "version":
        server.ping.return_value = ping(build=75689)
    elif failure == "create":
        server._execute.return_value = pb.Response(create_game=pb.ResponseCreateGame(error=1))
    elif failure == "play":
        play.side_effect = RuntimeError("bad step")
        client.save_replay.side_effect = OSError("disconnected")
    else:
        args[-1].update(bot_error="startup failed")
    with pytest.raises(RuntimeError):
        asyncio.run(runtime.run_session(*args))
    assert args[-1].data["phase"] == "failed"
    if failure in {"busy", "version"}:
        server._execute.assert_not_awaited()
    if failure == "play":
        assert args[-1].data["error"] == "RuntimeError: bad step"
        assert args[-1].data["replay_error"] == "disconnected"


def test_runtime_bot_milestones_and_errors(monkeypatch, installation, tmp_path):
    report = runtime.RuntimeReport(tmp_path / "report.json", installation)
    bot = runtime.RuntimeAssistant(AssistantSettings(enabled=False), report)
    bot.client = SimpleNamespace()
    bot.chat_send = AsyncMock()
    bot.state = SimpleNamespace(game_loop=224)
    monkeypatch.setattr(EconomyAssistant, "on_start", AsyncMock())
    step = AsyncMock()
    monkeypatch.setattr(EconomyAssistant, "on_step", step)
    asyncio.run(bot.on_start())
    assert report.data["automation_paused"] is True
    asyncio.run(bot.on_step(0))
    asyncio.run(bot.on_step(1))
    assert report.data["first_game_loop"] == 224
    step.side_effect = ValueError("unknown ability")
    with pytest.raises(ValueError):
        asyncio.run(bot.on_step(2))
    assert "unknown ability" in report.data["bot_error"]
    monkeypatch.setattr(EconomyAssistant, "on_start", AsyncMock(side_effect=KeyError("bad data")))
    with pytest.raises(KeyError):
        asyncio.run(bot.on_start())
    assert "on_start" in report.data["bot_error"]


def test_attach_context_never_quits_user_process(monkeypatch, installation):
    ws = Mock()
    socket_context = Mock(__aenter__=AsyncMock(return_value=ws), __aexit__=AsyncMock())
    session = Mock(ws_connect=Mock(return_value=socket_context))
    session_context = Mock(__aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock())
    monkeypatch.setattr(runtime.aiohttp, "ClientSession", Mock(return_value=session_context))

    async def check():
        async with runtime.connection(installation, 5001) as server:
            assert server._ws is ws

    asyncio.run(check())
    assert session.ws_connect.call_args.args == ("ws://127.0.0.1:5001/sc2api",)
    ws.send_bytes.assert_not_called()  # Neither quit nor leave sent by connection context
    socket_context.__aexit__.assert_awaited_once()


def test_owned_connection_uses_process_context(monkeypatch, installation):
    process = Mock(__aenter__=AsyncMock(return_value="server"), __aexit__=AsyncMock())
    monkeypatch.setattr(runtime, "LocalProcess", Mock(return_value=process))

    async def check():
        async with runtime.connection(installation) as server:
            assert server == "server"

    asyncio.run(check())
    process.__aexit__.assert_awaited_once()


@pytest.mark.parametrize("mode", ["success", "exit", "timeout"])
def test_process_connection_bounded_and_cleanable(monkeypatch, installation, mode):
    # Stub constructor side effects (port allocation, temp directory); exercise our connect loop.
    monkeypatch.setattr(runtime.SC2Process, "__init__", lambda self, **kwargs: None)
    process = runtime.LocalProcess(installation)
    assert process._serverhost == "127.0.0.1"
    process._host, process._port = "127.0.0.1", 5001
    process._process = Mock(poll=Mock(return_value=1 if mode == "exit" else None), returncode=1)
    session = Mock(ws_connect=AsyncMock(return_value="socket"))
    if mode == "timeout":
        session.ws_connect.side_effect = TimeoutError
    monkeypatch.setattr(runtime.aiohttp, "ClientSession", Mock(return_value=session))
    monkeypatch.setattr(runtime.asyncio, "sleep", AsyncMock())
    if mode == "success":
        assert asyncio.run(process._connect()) == "socket"
    else:
        with pytest.raises((RuntimeError, TimeoutError)):
            asyncio.run(process._connect())
        if mode == "timeout":
            assert session.ws_connect.await_count == 60
    assert process._session is session  # SDK __aenter__ cleans this even when _connect raises


@pytest.mark.parametrize("fail", [False, True])
def test_owned_process_cleanup_on_entry_failure_and_normal_exit(monkeypatch, installation, fail):
    monkeypatch.setattr(runtime.SC2Process, "__init__", lambda self, **kwargs: None)
    process = runtime.LocalProcess(installation)
    process._launch = Mock(return_value="owned process")
    process._connect = AsyncMock(return_value=object())
    process._close_connection = AsyncMock()
    process._clean = Mock()
    if fail:
        process._connect.side_effect = RuntimeError("cannot connect")

    async def check():
        async with process as server:
            assert server._process is process

    if fail:
        with pytest.raises(RuntimeError, match="cannot connect"):
            asyncio.run(check())
    else:
        asyncio.run(check())
    process._close_connection.assert_awaited_once()
    process._clean.assert_called_once()


def test_map_lookup_deduplicates_same_file(installation):
    import os

    first = installation.root / "Maps/one/Test.SC2Map"
    second = installation.root / "Maps/two/Test.SC2Map"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_bytes(b"map")
    os.link(first, second)
    assert runtime.resolve_map(installation, "Test").samefile(first)
