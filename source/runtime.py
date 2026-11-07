"""Local graphical runtime; SDK-private integration is isolated and contract-tested."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import platform
import re
import sys
import time
from contextlib import asynccontextmanager, suppress
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import aiohttp
from google.protobuf.json_format import MessageToDict, ParseDict
from loguru import logger
from s2clientprotocol import data_pb2, query_pb2
from s2clientprotocol import sc2api_pb2 as pb
from sc2 import paths
from sc2.client import Client
from sc2.controller import Controller
from sc2.data import Status
from sc2.dicts.unit_research_abilities import RESEARCH_INFO
from sc2.dicts.unit_train_build_abilities import TRAIN_INFO
from sc2.game_data import AbilityData, GameData
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import _play_game
from sc2.protocol import ProtocolError
from sc2.sc2process import SC2Process
from sc2.versions import VERSIONS

from source.economy_assistant import AIR_UPGRADES, GROUND_UPGRADES, PRODUCERS, SPELLS, EconomyAssistant
from source.local_control import consume_command
from source.scouting import ScoutController
from source.tactics import TacticalController
from source.warp_reinforcement import WARP_UNITS, WarpReinforcement


@dataclass(frozen=True)
class ObservedAbility:
    """Opaque game ID: readable/countable, never a fabricated SDK command."""

    value: int


class ObservedAbilityData(AbilityData):
    @property
    def exact_id(self):
        return ObservedAbility(self._proto.ability_id)

    @property
    def id(self):
        value = self._proto.remaps_to_ability_id or self._proto.ability_id
        known = AbilityId(value)
        return known if known.value else ObservedAbility(value)


class ObservationAbilities(dict):
    """Preserve even order IDs missing from SC2's own metadata response."""

    def __init__(self, game_data, unknown):
        super().__init__(game_data.abilities)
        self.game_data = game_data
        self.unknown = unknown

    def __missing__(self, key):
        if not isinstance(key, int) or key <= 0:
            raise KeyError(key)
        self.unknown.append(key)
        logger.warning("Observed undocumented SC2 order ID {}; preserving opaque identity", key)
        value = ObservedAbilityData(self.game_data, data_pb2.AbilityData(ability_id=key))
        self[key] = value
        return value


def compatible_game_data(data):
    game_data = GameData(data)
    aliases, opaque = [], []
    for ability in data.abilities:
        if ability.ability_id and ability.ability_id not in game_data.abilities:
            canonical = game_data.abilities.get(ability.remaps_to_ability_id)
            if canonical is not None:
                game_data.abilities[ability.ability_id] = canonical
                aliases.append(ability.ability_id)
            else:
                game_data.abilities[ability.ability_id] = ObservedAbilityData(game_data, ability)
                opaque.append(ability.ability_id)
    game_data.abilities = ObservationAbilities(game_data, opaque)
    return game_data, aliases, opaque


def audit_commands(data, game_data):
    """Check every assistant command, including disabled optional features."""
    abilities = {a.ability_id: a for a in data.abilities}
    checks = []

    def check(name, expected, actual=None):
        proto = abilities.get(expected.value)
        supported = proto is not None and expected.value in game_data.abilities
        mapped = proto.remaps_to_ability_id or expected.value if proto else None
        if actual is not None:
            other = abilities.get(actual)
            other_mapped = other.remaps_to_ability_id or actual if other else None
            supported = supported and other is not None and mapped == other_mapped
        checks.append({"command": name, "ability_id": expected.value, "ok": bool(supported)})

    for producer, entries in TRAIN_INFO.items():
        if producer not in {UnitTypeId.PROBE, UnitTypeId.NEXUS, *PRODUCERS}:
            continue
        for kind, info in entries.items():
            if producer == UnitTypeId.PROBE and kind not in {
                UnitTypeId.NEXUS,
                UnitTypeId.PYLON,
                UnitTypeId.ASSIMILATOR,
                UnitTypeId.GATEWAY,
                UnitTypeId.CYBERNETICSCORE,
                UnitTypeId.ROBOTICSFACILITY,
                UnitTypeId.TWILIGHTCOUNCIL,
                UnitTypeId.TEMPLARARCHIVE,
                UnitTypeId.ROBOTICSBAY,
                UnitTypeId.STARGATE,
                UnitTypeId.FORGE,
                UnitTypeId.FLEETBEACON,
            }:
                continue
            if producer in PRODUCERS and kind not in PRODUCERS[producer]:
                continue
            unit = game_data.units.get(kind.value)
            check(f"{producer.name}:{kind.name}", info["ability"], unit._proto.ability_id if unit else -1)
    upgrades = {
        UpgradeId.PSISTORMTECH,
        UpgradeId.BLINKTECH,
        UpgradeId.WARPGATERESEARCH,
        UpgradeId.CHARGE,
        UpgradeId.EXTENDEDTHERMALLANCE,
        *GROUND_UPGRADES,
        *AIR_UPGRADES,
    }
    for entries in RESEARCH_INFO.values():
        for upgrade, info in entries.items():
            if upgrade in upgrades:
                item = game_data.upgrades.get(upgrade.value)
                check(upgrade.name, info["ability"], item._proto.ability_id if item else -1)
    for ability in {
        *SPELLS,
        AbilityId.EFFECT_CHRONOBOOSTENERGYCOST,
        AbilityId.HARVEST_GATHER,
        AbilityId.MOVE_MOVE,
        AbilityId.ATTACK_ATTACK,
        AbilityId.MORPH_WARPGATE,
        AbilityId.MORPH_WARPPRISMPHASINGMODE,
        AbilityId.MORPH_WARPPRISMTRANSPORTMODE,
        *(item[0] for item in WARP_UNITS.values()),
    }:
        check(ability.name, ability)
    return {
        "ok": all(c["ok"] for c in checks),
        "commands": checks,
        "scope": "Static game data and SDK mappings; execution and human controls unverified",
    }


@dataclass(frozen=True)
class Installation:
    root: Path
    executable: Path
    base_build: int
    data_version: str | None
    requested_version: str
    installed_builds: tuple[int, ...]

    def report(self):
        return {
            "root": str(self.root),
            "executable": str(self.executable),
            "base_build": self.base_build,
            "data_version": self.data_version,
            "requested_version": self.requested_version,
            "installed_builds": list(self.installed_builds),
        }


def inspect_installation(root=None, requested="latest"):
    """Resolve an exact installed binary; never silently substitute a version."""
    pf = paths.PF
    if pf not in {"Windows", "Darwin"}:
        raise ValueError(
            "Use native Windows PowerShell (recommended) or macOS for human play; not WSL/headless Linux."
        )
    root = Path(root or os.environ.get("SC2PATH") or paths.get_user_sc2_install() or paths.BASEDIR[pf])
    root = root.expanduser().resolve()
    builds = {
        int(p.name[4:]): p / paths.BINPATH[pf]
        for p in (root / "Versions").glob("Base*")
        if re.fullmatch(r"Base\d+", p.name) and (p / paths.BINPATH[pf]).is_file()
    }
    if not builds:
        raise ValueError(f"No SC2 executable under {root / 'Versions'}. Install SC2 or set --sc2-path.")
    data_version = None
    if requested == "latest":
        build = max(builds)
    else:
        entry = next((v for v in VERSIONS if v["label"] == requested), None)
        if entry is None:
            raise ValueError(
                f"Unknown version {requested!r}. Use 'latest' for current retail; no fallback performed."
            )
        build = entry["base-version"]
        data_version = entry["data-hash"]
        if build not in builds:
            raise ValueError(
                f"{requested} requires Base{build}, which is not installed. No fallback performed."
            )
    if build < 55958:
        raise ValueError("SC2 binary predates API support. Update through Battle.net.")
    if pf == "Windows" and not (root / "Support64").is_dir():
        raise ValueError(f"Missing {root / 'Support64'}; repair the SC2 installation in Battle.net.")
    return Installation(root, builds[build], build, data_version, requested, tuple(sorted(builds)))


def resolve_map(installation, name, map_file=None):
    """Accept a direct file or an unambiguous map name; don't depend on SDK Paths caches."""
    if map_file:
        candidates = [Path(map_file).expanduser().resolve()]
    else:
        candidates = []
        for folder in (installation.root / "Maps", installation.root / "maps"):
            if folder.is_dir():
                for candidate in folder.rglob("*.SC2Map"):
                    # macOS may resolve Maps/maps to the same file without normalizing case.
                    if candidate.stem == name and not any(candidate.samefile(p) for p in candidates):
                        candidates.append(candidate.resolve())
    if len(candidates) != 1 or not candidates[0].is_file() or candidates[0].suffix.lower() != ".sc2map":
        raise ValueError(
            f"Map {map_file or name!s} missing or ambiguous. Use --map-file with an existing .SC2Map."
        )
    return candidates[0]


class RuntimeReport:
    def __init__(self, path, installation, map_path=None, attach_port=None):
        self.path = Path(path)
        self.data = {
            "schema_version": 1,
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "packages": {p: version(p) for p in ("burnysc2", "pys2clientprotocol", "protobuf")},
            "installation": installation.report(),
            "mode": "attach" if attach_port else "launch",
            "map": str(map_path) if map_path else None,
            "map_sha256": hashlib.sha256(map_path.read_bytes()).hexdigest() if map_path else None,
            "phase": "preflight",
            "human_control": "not_verified",
        }
        self.update()

    def update(self, **values):
        self.data.update(values)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(self.data, indent=2) + "\n", encoding="utf-8")
        for attempt in range(4):
            try:
                temporary.replace(self.path)
                return
            except PermissionError:
                if attempt == 3:
                    logger.warning("Runtime report is temporarily locked; retaining update for next sample")
                    return
                time.sleep(0.05 * (attempt + 1))


def verify_ping(response, installation):
    if not response.HasField("ping"):
        raise RuntimeError("SC2 did not return a ping payload.")
    ping = response.ping
    actual = {
        "game_version": ping.game_version,
        "base_build": ping.base_build,
        "data_build": ping.data_build,
        "data_version": ping.data_version,
    }
    if ping.base_build != installation.base_build:
        raise RuntimeError(f"Wrong binary: expected Base{installation.base_build}, received {actual}.")
    if installation.data_version and ping.data_version.lower() != installation.data_version.lower():
        raise RuntimeError(f"Wrong game data: expected {installation.data_version}, received {actual}.")
    return actual


class LocalProcess(SC2Process):
    """Bound connection/receive waits, detect early exit, bind only loopback."""

    def __init__(self, installation):
        super().__init__(
            host="127.0.0.1",
            fullscreen=False,
            resolution=(1280, 720),
            base_build=f"Base{installation.base_build}",
            data_hash=installation.data_version,
        )
        self._serverhost = "127.0.0.1"

    async def __aenter__(self):
        # Own exactly this process; avoid the SDK global KillSwitch/SIGINT handler.
        try:
            self._process = self._launch()
            self._ws = await self._connect()
            return Controller(self._ws, self)
        except BaseException:
            await self.__aexit__(None, None, None)
            raise

    async def __aexit__(self, *args):
        try:
            await self._close_connection()
        finally:
            self._clean()

    async def _connect(self):
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
        for _ in range(60):
            if self._process.poll() is not None:
                raise RuntimeError(f"SC2 exited before API connection (exit {self._process.returncode}).")
            try:
                return await self._session.ws_connect(
                    self.ws_url, timeout=aiohttp.ClientWSTimeout(ws_receive=30, ws_close=5)
                )
            except (aiohttp.ClientConnectorError, TimeoutError):
                await asyncio.sleep(1)
        raise TimeoutError("SC2 API did not start. See docs/windows-install-and-play.md troubleshooting.")


@asynccontextmanager
async def connection(installation, attach_port=None):
    if attach_port:
        async with (
            aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session,
            session.ws_connect(
                f"ws://127.0.0.1:{attach_port}/sc2api",
                timeout=aiohttp.ClientWSTimeout(ws_receive=30, ws_close=5),
            ) as ws,
        ):
            # An attached process belongs to the user. Never quit/kill it.
            yield Controller(ws, None)
    else:
        async with LocalProcess(installation) as server:
            yield server


class SharedClient(Client):
    """Preserve selection and check JoinGame errors before the SDK consumes them."""

    async def observation(self, game_loop=None):
        response = await super().observation(game_loop)
        # BurnySC2 calls on_end before preparing the terminal/time-limit state.
        # Retain the actual final response for the public training adapter.
        self.latest_observation = response
        return response

    async def available_ability_snapshot(self, units):
        if not units:
            return {}
        response = await self._execute(
            query=query_pb2.RequestQuery(
                abilities=[query_pb2.RequestQueryAvailableAbilities(unit_tag=u.tag) for u in units],
                ignore_resource_requirements=False,
            )
        )
        return MessageToDict(response.query, preserving_proto_field_name=True)

    async def get_game_data(self):
        response = await self._execute(
            data=pb.RequestData(
                ability_id=True, unit_type_id=True, upgrade_id=True, buff_id=True, effect_id=True
            )
        )
        game_data, aliases, opaque = compatible_game_data(response.data)
        self.game_data_wire = response.data.SerializeToString()
        self.compatibility = audit_commands(response.data, game_data)
        self.compatibility.update(
            declared_alias_ids=aliases,
            opaque_order_ids=opaque,
            sdk_version=version("burnysc2"),
            protocol_version=version("pys2clientprotocol"),
        )
        logger.info(
            "Startup compatibility: {} commands, {} failures, {} aliases, {} opaque order IDs",
            len(self.compatibility["commands"]),
            sum(not check["ok"] for check in self.compatibility["commands"]),
            len(aliases),
            len(opaque),
        )
        return game_data

    async def _execute(self, **kwargs):
        if "join_game" in kwargs:
            options = kwargs["join_game"].options
            options.raw_affects_selection = False
            options.show_cloaked = False
        response = await super()._execute(**kwargs)
        if "action" in kwargs and response.HasField("action"):
            failures = getattr(self, "recent_rejections", [])
            for action, result in zip(kwargs["action"].actions, response.action.result, strict=False):
                if result != 1 and action.HasField("action_raw"):
                    command = action.action_raw.unit_command
                    failure = {
                        "ability_id": command.ability_id,
                        "result": result,
                        "unit_tags": list(command.unit_tags),
                    }
                    failures.append(failure)
                    logger.warning("SC2 rejected action request: {}", failure)
            self.recent_rejections = failures
        if "join_game" in kwargs:
            result = response.join_game
            if result.HasField("error") or not result.player_id:
                raise RuntimeError(f"JoinGame failed: {result}")
        return response


def create_request(map_path, players, realtime=True, random_seed=None):
    # Inline map data avoids game-process path resolution / protected-folder differences.
    request = pb.RequestCreateGame(
        local_map=pb.LocalMap(map_path=map_path.name, map_data=map_path.read_bytes()),
        realtime=realtime,
        disable_fog=False,
    )
    if random_seed is not None:
        request.random_seed = random_seed
    for player in players:
        setup = request.player_setup.add(type=player.type.value)
        if player.type.name == "Computer":
            setup.race = player.race.value
            setup.difficulty = player.difficulty.value
            if player.ai_build is not None:
                setup.ai_build = player.ai_build.value
    return request


async def run_session(
    installation,
    map_path,
    players,
    replay,
    report,
    *,
    probe=False,
    attach_port=None,
    realtime=True,
    game_time_limit=None,
    random_seed=None,
):
    try:
        async with connection(installation, attach_port) as server:
            response = await server.ping()
            # Save actual identity even on a mismatch; useful for agent diagnosis.
            report.update(
                phase="connected",
                ping={
                    "game_version": response.ping.game_version,
                    "base_build": response.ping.base_build,
                    "data_build": response.ping.data_build,
                    "data_version": response.ping.data_version,
                },
            )
            actual = verify_ping(response, installation)
            logger.info("Connected SC2: {}", actual)
            if probe:
                report.update(phase="probe_ok")
                return
            if response.status != Status.launched.value:
                raise RuntimeError(
                    "Client is not idle/launched. Refusing to replace an existing game or replay."
                )
            result = await server._execute(
                create_game=create_request(map_path, players, realtime, random_seed)
            )
            if not result.HasField("create_game") or result.create_game.HasField("error"):
                raise RuntimeError(f"CreateGame failed: {result.create_game}")
            report.update(phase="created", replay_target=str(replay))
            client = SharedClient(server._ws)
            client.raw_affects_selection = False
            try:
                outcome = await _play_game(
                    players[0], client, realtime=realtime, game_time_limit=game_time_limit
                )
                if report.data.get("bot_error"):
                    raise RuntimeError(report.data["bot_error"])
                report.update(phase="ended", result=str(outcome))
            finally:
                # Preserve the original failure if saving/leave fails during disconnect.
                try:
                    if report.data.get("replay") != str(replay):
                        await client.save_replay(str(replay))
                        report.update(replay=str(replay))
                except (ProtocolError, OSError, TimeoutError, aiohttp.ClientError) as exc:
                    report.update(replay_error=str(exc))
                    logger.warning("Replay could not be saved: {}", exc)
                with suppress(ProtocolError, OSError, TimeoutError, aiohttp.ClientError):
                    await client.leave()
    except Exception as exc:
        report.update(phase="failed", error=f"{type(exc).__name__}: {exc}")
        raise


def recorded_observations(report_path):
    """Rehydrate sampled player observations without a client or API connection.

    Dynamic pathing changes between snapshots are unavailable. Actions accumulate
    only in memory; callers must never attach a live client to this replay bot.
    Recorded script paths are deliberately not executed during offline analysis.
    """
    from sc2.game_info import GameInfo
    from sc2.game_state import GameState

    from source.assistant_control import AssistantSettings

    path = Path(report_path)
    report = json.loads(path.read_text(encoding="utf-8-sig"))
    data = pb.ResponseData.FromString(path.with_suffix(".game-data.pb").read_bytes())
    info = ParseDict(
        json.loads(path.with_suffix(".game-info.json").read_text(encoding="utf-8")), pb.ResponseGameInfo()
    )
    game_data = compatible_game_data(data)[0]
    bot = None
    previous_loop = -1
    with path.with_suffix(".state.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            settings = AssistantSettings(**{**row["settings"], "strategy_script": ""}).validate()
            state = GameState(ParseDict(row["observation"], pb.ResponseObservation()))
            if state.game_loop <= previous_loop:
                raise ValueError("Recorded observations must advance monotonically")
            previous_loop = state.game_loop
            first = bot is None
            if first:
                bot = EconomyAssistant(settings)
                bot._prepare_start(
                    None,
                    state.common.player_id,
                    GameInfo(info),
                    game_data,
                    base_build=report["ping"]["base_build"],
                )
                bot.unit_supplies = {
                    kind: entry._proto.food_required for kind, entry in game_data.units.items()
                }
                bot.opponent_difficulty = report.get("opponent_difficulty", "Unknown")
            bot.control.settings = settings
            bot.control.released = set(row.get("released_unit_tags", []))
            bot._prepare_step(state, pb.Response(game_info=info))
            if first:
                if not bot.townhalls:
                    raise ValueError("Recording must begin with an owned starting base")
                bot._prepare_first_step()
            bot._used.clear()
            bot.actions.clear()
            bot.unit_tags_received_action.clear()
            yield bot, row


def prepare_final_observation(bot):
    """Prepare the last real observation at SDK end, without advancing/resetting.

    Keep the SDK-private state preparation inside this reviewed boundary. A
    missing final observation is an infrastructure failure, never fabricated.
    """
    from sc2.game_state import GameState

    response = getattr(bot.client, "latest_observation", None)
    if response is None or not response.HasField("observation"):
        raise RuntimeError("Missing final player observation")
    final = GameState(response.observation)
    if final.game_loop < bot.state.game_loop:
        raise RuntimeError("Final observation clock moved backwards")
    if final.game_loop > bot.state.game_loop:
        bot._prepare_step(final, pb.Response(game_info=bot.game_info._proto))
    return final.game_loop


class RuntimeAssistant(EconomyAssistant):
    """Expose live milestones and errors that the SDK may otherwise turn into defeat."""

    def __init__(self, settings, report):
        super().__init__(settings)
        self.report = report
        self._reported_observation = False
        self._last_tactical_snapshot = float("-inf")
        self.tactics = TacticalController()
        self._last_micro = float("-inf")
        self._last_tactics = float("-inf")
        self._last_decision = None
        self._last_scouting = {}
        self._last_script_context = float("-inf")
        self._script_observation = None
        self._script_abilities = {}
        self._tactical_ms = 0.0
        self._micro_decisions = []
        self.scouting = ScoutController(revisit=getattr(report, "data", {}).get("scout_revisit", False))
        self.reinforcement = WarpReinforcement()

    async def on_start(self):
        try:
            if self.report.data.get("fast_test"):
                self.client.game_step = self.report.data["fast_step_size"]
            audit = getattr(self.client, "compatibility", None)
            if audit is not None:
                self.report.update(compatibility=audit)
                if not audit["ok"]:
                    failures = [c["command"] for c in audit["commands"] if not c["ok"]]
                    raise RuntimeError("Command compatibility failed: " + ", ".join(failures))
            self.unit_supplies = {
                kind: data._proto.food_required for kind, data in self.game_data.units.items()
            }
            wire = getattr(self.client, "game_data_wire", None)
            if wire is not None:
                metadata = self.report.path.with_suffix(".game-data.pb")
                metadata.write_bytes(wire)
                self.report.update(game_data_snapshot=str(metadata))
            await super().on_start()
            game_info = getattr(getattr(self, "game_info", None), "_proto", None)
            if game_info is not None:
                map_info = self.report.path.with_suffix(".game-info.json")
                map_info.write_text(
                    json.dumps(MessageToDict(game_info, preserving_proto_field_name=True)), encoding="utf-8"
                )
                self.report.update(game_info_snapshot=str(map_info))
            self.report.update(
                phase="bot_started", automation_paused=not self.settings.enabled, local_control=True
            )
            if not self.settings.enabled:
                await self.chat_send(
                    "Automation PAUSED. Test controls, then type !assist resume", team_only=True
                )
        except Exception as exc:
            self.report.update(bot_error=f"on_start: {type(exc).__name__}: {exc}")
            raise

    async def on_tactical_step(self):
        observation = getattr(self.state, "response_observation", None)
        if observation is None:
            return
        started = time.perf_counter()
        changed = getattr(self, "_tactical_settings", None) != asdict(self.settings)
        self._tactical_settings = asdict(self.settings)
        if self.time - self._last_tactics >= 1 or changed:
            self._last_tactics = self.time
            self._last_scouting = self.scouting.tick(self)
            if self.settings.strategy_script and self.time - self._last_script_context >= 5:
                self._last_script_context = self.time
                self._script_observation = MessageToDict(observation, preserving_proto_field_name=True)
                query = getattr(getattr(self, "client", None), "available_ability_snapshot", None)
                self._script_abilities = await query(self.all_own_units) if query is not None else {}
            self._last_decision = self.tactics.tick(
                self, observation=self._script_observation, available_abilities=self._script_abilities
            )
        if self.time - self._last_micro >= 0.125:
            self._last_micro = self.time
            self._micro_decisions.extend(self.tactics.micro(self))
            self._micro_decisions = self._micro_decisions[-512:]
        self._tactical_ms = round((time.perf_counter() - started) * 1000, 3)

    async def on_step(self, iteration):
        try:
            for failure in getattr(getattr(self, "client", None), "recent_rejections", []):
                key = f"direct:{failure['ability_id']}:{failure['result']}"
                self.action_rejections[key] = self.action_rejections.get(key, 0) + 1
                self.reinforcement.reject(failure, self.time)
            if getattr(self, "client", None) is not None:
                self.client.recent_rejections = []
            selected = [unit.tag for unit in getattr(self, "all_own_units", ()) if unit.is_selected]
            command = consume_command(self.report.path, self.control, selected)
            if command:
                self.report.update(last_control_command=command)
                logger.info("Local control: {}", command)
                if command.get("quit"):
                    replay = self.report.data.get("replay_target")
                    if replay:
                        await self.client.save_replay(replay)
                        self.report.update(replay=replay)
                    await self.client.leave()
                    return
            await super().on_step(iteration)
            fast = getattr(self.report, "data", {}).get("fast_test", False)
            now = self.time if fast else time.monotonic()
            observation = getattr(self.state, "response_observation", None)
            interval = getattr(self.report, "data", {}).get("snapshot_interval", 5)
            if observation is not None and now - self._last_tactical_snapshot >= interval:
                self._last_tactical_snapshot = now
                observed = MessageToDict(observation, preserving_proto_field_name=True)
                if self._last_decision is None:
                    await self.on_tactical_step()
                abilities = {}
                query = getattr(getattr(self, "client", None), "available_ability_snapshot", None)
                if query is not None:
                    abilities = await query(getattr(self, "all_own_units", ()))
                decision = dict(self._last_decision)
                decision["controller_ms"] = self._tactical_ms
                decision["micro_since_last_sample"] = self._micro_decisions
                self._micro_decisions = []
                snapshot = {
                    "schema_version": 1,
                    "captured_utc": datetime.now(timezone.utc).isoformat(),
                    "game_loop": self.state.game_loop,
                    "visibility_scope": "player_observation_fog_of_war",
                    "sampling_clock": "game_seconds" if fast else "wall_seconds",
                    "api_step_size": getattr(self.client, "game_step", None) if fast else None,
                    "opponent_difficulty": getattr(self.report, "data", {}).get("opponent_difficulty"),
                    "decision": decision,
                    "observation": observed,
                    "available_abilities": abilities,
                    "settings": asdict(self.settings),
                    "released_unit_tags": sorted(self.control.released),
                    "observed_action_rejections": dict(self.action_rejections),
                    "scouting": self._last_scouting,
                    "reinforcement": self.reinforcement.last_report,
                }
                destination = self.report.path.with_suffix(".state.jsonl")
                with destination.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(snapshot) + "\n")
                self.report.update(
                    state_snapshots=str(destination),
                    last_game_loop=self.state.game_loop,
                    strategy=decision["strategy"],
                    strategy_reason=decision["reason"],
                    automation_paused=not self.settings.enabled,
                )
            if not self._reported_observation:
                self.report.update(phase="observing", first_game_loop=self.state.game_loop)
                self._reported_observation = True
        except Exception as exc:
            self.report.update(bot_error=f"on_step: {type(exc).__name__}: {exc}")
            raise
