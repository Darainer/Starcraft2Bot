"""Local graphical runtime; SDK-private integration is isolated and contract-tested."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import platform
import re
import sys
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import aiohttp
from loguru import logger
from s2clientprotocol import sc2api_pb2 as pb
from sc2 import paths
from sc2.client import Client
from sc2.controller import Controller
from sc2.data import Status
from sc2.main import _play_game
from sc2.protocol import ProtocolError
from sc2.sc2process import SC2Process
from sc2.versions import VERSIONS

from source.economy_assistant import EconomyAssistant


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
        candidates = [
            p
            for folder in (installation.root / "Maps", installation.root / "maps")
            if folder.is_dir()
            for p in folder.rglob("*.SC2Map")
            if p.stem == name
        ]
        candidates = list({p.resolve() for p in candidates})
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
        temporary.replace(self.path)


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

    async def _execute(self, **kwargs):
        if "join_game" in kwargs:
            options = kwargs["join_game"].options
            options.raw_affects_selection = False
            options.show_cloaked = False
        response = await super()._execute(**kwargs)
        if "join_game" in kwargs:
            result = response.join_game
            if result.HasField("error") or not result.player_id:
                raise RuntimeError(f"JoinGame failed: {result}")
        return response


def create_request(map_path, players):
    # Inline map data avoids game-process path resolution / protected-folder differences.
    request = pb.RequestCreateGame(
        local_map=pb.LocalMap(map_path=map_path.name, map_data=map_path.read_bytes()),
        realtime=True,
        disable_fog=False,
    )
    for player in players:
        setup = request.player_setup.add(type=player.type.value)
        if player.type.name == "Computer":
            setup.race = player.race.value
            setup.difficulty = player.difficulty.value
    return request


async def run_session(installation, map_path, players, replay, report, *, probe=False, attach_port=None):
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
            result = await server._execute(create_game=create_request(map_path, players))
            if not result.HasField("create_game") or result.create_game.HasField("error"):
                raise RuntimeError(f"CreateGame failed: {result.create_game}")
            report.update(phase="created")
            client = SharedClient(server._ws)
            client.raw_affects_selection = False
            try:
                outcome = await _play_game(players[0], client, realtime=True)
                if report.data.get("bot_error"):
                    raise RuntimeError(report.data["bot_error"])
                report.update(phase="ended", result=str(outcome))
            finally:
                # Preserve the original failure if saving/leave fails during disconnect.
                try:
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


class RuntimeAssistant(EconomyAssistant):
    """Expose live milestones and errors that the SDK may otherwise turn into defeat."""

    def __init__(self, settings, report):
        super().__init__(settings)
        self.report = report
        self._reported_observation = False

    async def on_start(self):
        try:
            await super().on_start()
            self.report.update(phase="bot_started", automation_paused=not self.settings.enabled)
            if not self.settings.enabled:
                await self.chat_send(
                    "Automation PAUSED. Test controls, then type !assist resume", team_only=True
                )
        except Exception as exc:
            self.report.update(bot_error=f"on_start: {type(exc).__name__}: {exc}")
            raise

    async def on_step(self, iteration):
        try:
            await super().on_step(iteration)
            if not self._reported_observation:
                self.report.update(phase="observing", first_game_loop=self.state.game_loop)
                self._reported_observation = True
        except Exception as exc:
            self.report.update(bot_error=f"on_step: {type(exc).__name__}: {exc}")
            raise
