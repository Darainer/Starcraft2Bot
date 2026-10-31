"""Owned Windows SC2 environment using the reviewed public runtime boundary.

The game runs on a worker thread and waits at director decisions. The caller
owns policy inference. Only this environment's runtime context cleans up its
client. Neither reset nor close attaches to, quits or kills another session.
"""

import asyncio
import json
import os
import queue
import threading
import time
from collections import deque
from contextlib import suppress
from dataclasses import asdict, replace
from pathlib import Path
from uuid import uuid4

import psutil
from google.protobuf.json_format import MessageToDict
from sc2.data import AIBuild, Difficulty, Race, Result
from sc2.player import Bot, Computer

from source.assistant_control import AssistantSettings
from source.economy_assistant import ARMY_TARGETS
from source.games.starcraft2.action_codec import DECODER_VERSION, decode
from source.games.starcraft2.actions import ACTION_VERSION, MASK_VERSION
from source.games.starcraft2.encoding import NORMALIZATION_VERSION, opaque
from source.games.starcraft2.model import MODEL_VERSION
from source.games.starcraft2.observation import LIVE_FEATURE_VERSION, ObservationAdapter
from source.opponent_beliefs import ONTOLOGY_ID
from source.opponent_dataset import unit_metadata
from source.runtime import RuntimeAssistant, RuntimeReport, prepare_final_observation, run_session
from source.scouting_facts import ScoutingFacts
from source.strategy_core.contracts import SHARED_ONTOLOGY
from source.strategy_director import StrategicDirector
from source.training.collector import MANIFEST_VERSION, identity
from source.training.records import Outcome


def live_client_count():
    return sum(p.info["name"] in {"SC2_x64.exe", "SC2.exe", "SC2"} for p in psutil.process_iter(["name"]))


class ClientLease:
    """Serialize training startups until their actual client is visible.

    Native process counting also includes existing non-training clients. The
    startup lock is released only after join or failure; process death releases
    the OS lock. All training runners share this lock across worktrees.
    """

    def __init__(self, directory=None):
        import tempfile

        self.directory = Path(directory or Path(tempfile.gettempdir()) / "sc2bot-client-pool")
        self.stream = None

    def acquire(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        self.stream = (self.directory / "startup.lock").open("a+b")  # noqa: SIM115 -- held through startup, released explicitly
        try:
            self.stream.seek(0)
            if os.name == "nt":
                import msvcrt

                if self.stream.read(1) == b"":
                    self.stream.write(b"0")
                    self.stream.flush()
                self.stream.seek(0)
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            if live_client_count() >= 8:
                raise RuntimeError("All eight global SC2 client slots are occupied")
        except BaseException:
            self.release()
            raise

    def release(self):
        if self.stream is not None:
            self.stream.close()
            self.stream = None


class Effects:
    """Observed changes, with no claim that a queued intent caused a change."""

    def __init__(self):
        self.previous = {}

    def observe(self, bot):
        current = {u.tag: (u.type_id.name, u.is_ready, tuple(u.position)) for u in bot.all_own_units}
        effects = []
        for tag, (kind, ready, position) in current.items():
            previous = self.previous.get(tag)
            event = None
            if ready and previous is not None and (not previous[1] or previous[0] != kind):
                event = "observed_completion_or_morph"
            elif ready and previous is None and self.previous:
                event = "observed_new_completed_unit"
            elif (
                previous is not None
                and sum((a - b) ** 2 for a, b in zip(position, previous[2], strict=True)) >= 1
            ):
                event = "observed_movement"
            if event:
                effects.append(
                    {
                        "id": opaque("effect", f"{bot.state.game_loop}:{tag}:{event}"),
                        "event": event,
                        "actor": opaque("u", str(tag)),
                        "time": bot.time,
                    }
                )
        self.previous = current
        return effects


class EnvironmentDirector:
    def __init__(self, bot, environment):
        self.bot, self.environment = bot, environment
        self.active = None
        self.history = deque(maxlen=32)
        self.sequence = 0
        self.blocked = {}
        self.rule = StrategicDirector()

    def report_failure(self, target, now):
        self.blocked[target] = now + 30
        self.rule.report_failure(target, now)

    def decide(self, assessment):
        bot, environment = self.bot, self.environment
        assessment = replace(
            assessment,
            targets=tuple(t for t in assessment.targets if self.blocked.get(t.id, -1) <= assessment.time),
        )
        effects = bot.effects.observe(bot)
        issued, bot.issued = bot.issued, []
        elapsed = 0 if bot.previous_decision is None else assessment.time - bot.previous_decision
        belief = bot.adapter.observe(
            bot,
            assessment,
            elapsed_seconds=elapsed,
            episode_start=bot.previous_decision is None,
            issued=issued,
            effects=effects,
        )
        bot.previous_decision = assessment.time
        environment.events.put(
            {
                "belief": belief,
                "outcome": Outcome("running"),
                "decoded": bot.last_decoded,
                "issued": issued,
                "effects": effects,
                "manifest": bot.manifest,
            }
        )
        environment.lease.release()
        sample = environment.actions.get(timeout=environment.inference_timeout)
        if environment.closed.is_set():
            raise RuntimeError("Training environment intentionally closed")
        self.sequence += 1
        if environment.controller == "rule":
            plan = self.rule.decide(assessment)
            bot.last_decoded = None
        else:
            if sample is None or (sample.based_on, sample.sampled_at) != (
                assessment.version,
                assessment.time,
            ):
                raise ValueError("Environment action must match the current sampling observation")
            bot.last_decoded = decode(sample, belief, self.sequence)
            plan = bot.last_decoded.plan
        self.active = plan
        self.history.append({"time": assessment.time, "objective": plan.objective, "reason": plan.reason})
        return plan


class TrainingAssistant(RuntimeAssistant):
    def __init__(self, settings, report, environment):
        super().__init__(settings, report)
        self.environment = environment
        self.tactics.director = EnvironmentDirector(self, environment)
        self.previous_decision = None
        self.last_decoded = None
        self.issued = []
        self.effects = Effects()
        self.manifest = None

    def issue(self, command, paid=False, supply=False, scout_order=False):
        accepted = super().issue(command, paid=paid, supply=supply, scout_order=scout_order)
        if accepted:
            self.issued.append(
                {
                    "id": opaque("intent", f"{self.state.game_loop}:{command.unit.tag}:{len(self.issued)}"),
                    "time": self.time,
                    "actor": opaque("u", str(command.unit.tag)),
                    "ability": command.ability.value,
                    "status": "queued",
                }
            )
        return accepted

    async def on_start(self):
        await super().on_start()
        context = {
            "own_start": list(self.start_location),
            "possible_enemy_starts": [list(p) for p in self.enemy_start_locations],
        }
        self.adapter = ObservationAdapter(
            ScoutingFacts(unit_metadata(self.report.path.with_suffix(".game-data.pb")), context)
        )
        observed = MessageToDict(self.state.response_observation, preserving_proto_field_name=True)[
            "observation"
        ]
        initial = {
            "game_loop": self.state.game_loop,
            "player": observed.get("player_common", {}),
            "units": sorted(
                (
                    {k: u.get(k) for k in ("unit_type", "pos", "health", "shield", "build_progress")}
                    for u in observed.get("raw_data", {}).get("units", [])
                    if u.get("alliance") == "Self"
                ),
                key=lambda u: json.dumps(u, sort_keys=True),
            ),
        }
        manifest = self.environment.metadata
        self.manifest = {
            **manifest,
            "schema_version": MANIFEST_VERSION,
            "episode_id": self.environment.episode_id,
            "ping": self.report.data["ping"],
            "initial_state": initial,
            "initial_state_sha256": identity(initial),
            "shared_ontology": SHARED_ONTOLOGY,
            "domain_ontology": ONTOLOGY_ID,
            "core_version": MODEL_VERSION,
            "adapter_version": LIVE_FEATURE_VERSION,
            "feature_version": LIVE_FEATURE_VERSION,
            "normalization_version": NORMALIZATION_VERSION,
            "action_version": ACTION_VERSION,
            "mask_version": MASK_VERSION,
            "decoder_version": DECODER_VERSION,
            "reward_version": "terminal-win-loss-v1",
            "settings": asdict(self.settings),
            "decision_cadence": "existing_two_seconds_or_signature_invalidation",
            "time_unit": "game_seconds",
        }

    async def on_end(self, result):
        if self.environment.closed.is_set() or self.report.data.get("bot_error"):
            return
        try:
            prepare_final_observation(self)
            army = self.units.of_type(set(ARMY_TARGETS)).ready.filter(self.control.eligible)
            assessment = self.tactics.assessor.observe(self, army)
            effects = self.effects.observe(self)
            belief = self.adapter.observe(
                self,
                assessment,
                elapsed_seconds=assessment.time - self.previous_decision,
                issued=self.issued,
                effects=effects,
            )
            reason = {Result.Victory: "victory", Result.Defeat: "defeat", Result.Tie: "draw"}.get(result)
            if reason is None:
                raise RuntimeError(f"Unresolved game result: {result}")
            if result == Result.Tie and not self.client.latest_observation.observation.player_result:
                if self.time < self.environment.metadata["time_limit"]:
                    raise RuntimeError("Tie without a game result or elapsed time limit")
                reason = "time_limit"
            self.environment.events.put(
                {
                    "belief": belief,
                    "outcome": Outcome(reason),
                    "decoded": self.last_decoded,
                    "issued": self.issued,
                    "effects": effects,
                    "manifest": self.manifest,
                }
            )
        except Exception as exc:
            self.report.update(bot_error=f"training on_end: {type(exc).__name__}: {exc}")
            raise


class LocalEnvironment:
    def __init__(
        self,
        installation,
        map_path,
        output,
        *,
        settings=None,
        controller="policy",
        inference_timeout=30,
        runtime=run_session,
        lease=None,
    ):
        if controller not in {"policy", "rule"}:
            raise ValueError("Unsupported environment controller")
        self.installation, self.map_path, self.output = installation, Path(map_path), Path(output)
        self.settings = settings or AssistantSettings(attack=True, profile="pressure")
        self.controller, self.inference_timeout, self.runtime = controller, inference_timeout, runtime
        self.lease = lease or ClientLease()
        self.worker = None
        self.closed = threading.Event()
        self.events, self.actions = queue.Queue(maxsize=2), queue.Queue(maxsize=1)
        self.last_event = None
        self.done = False

    def reset(self, seed, scenario_manifest):
        if self.worker is not None:
            self.close()
            self.worker = None
            self.closed = threading.Event()
            self.events, self.actions = queue.Queue(maxsize=2), queue.Queue(maxsize=1)
            self.done = False
        self.lease.acquire()
        self.metadata = {**scenario_manifest, "game_seed": seed, "python_seed": seed}
        self.episode_id = uuid4().hex[:16]
        self.episode_directory = self.output / self.episode_id
        self.episode_directory.mkdir(parents=True, exist_ok=False)
        self.report = RuntimeReport(self.episode_directory / "runtime.json", self.installation, self.map_path)
        self.report.update(
            fast_test=True,
            fast_step_size=self.metadata["step_size"],
            snapshot_interval=30,
            game_time_limit=self.metadata["time_limit"],
            random_seed=seed,
            opponent_race=self.metadata["opponent"]["race"],
            opponent_build=self.metadata["opponent"]["build"],
            opponent_difficulty=self.metadata["opponent"]["difficulty"],
        )
        self.worker = threading.Thread(target=self._run, name=f"sc2-training-{self.episode_id}", daemon=True)
        self.worker.start()
        event = self._receive()
        return event["belief"], {"manifest": event["manifest"]}

    def _run(self):
        try:
            os.environ["SC2PATH"] = str(self.installation.root)
            assistant = TrainingAssistant(self.settings, self.report, self)
            opponent = self.metadata["opponent"]
            players = [
                Bot(Race.Protoss, assistant, fullscreen=False),
                Computer(
                    Race[opponent["race"]],
                    Difficulty[opponent["difficulty"]],
                    ai_build=AIBuild[opponent["build"]],
                ),
            ]
            asyncio.run(
                self.runtime(
                    self.installation,
                    self.map_path,
                    players,
                    self.episode_directory / "match.SC2Replay",
                    self.report,
                    realtime=False,
                    random_seed=self.metadata["game_seed"],
                    game_time_limit=self.metadata["time_limit"],
                )
            )
            if self.report.data.get("bot_error"):
                raise RuntimeError(self.report.data["bot_error"])
        except BaseException as exc:
            if not self.closed.is_set():
                self.events.put({"error": f"{type(exc).__name__}: {exc}"})
        finally:
            self.lease.release()

    def _receive(self):
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            try:
                event = self.events.get(timeout=1)
            except queue.Empty:
                if self.worker is not None and not self.worker.is_alive():
                    raise RuntimeError("SC2 worker stopped without a complete observation") from None
                continue
            if "error" in event:
                raise RuntimeError(event["error"])
            self.last_event = event
            return event
        raise TimeoutError("SC2 observation deadline exceeded")

    def step(self, action):
        if self.worker is None or self.closed.is_set() or self.done:
            raise RuntimeError("Environment is not awaiting an action")
        self.actions.put(action, timeout=1)
        event = self._receive()
        outcome = event["outcome"]
        self.done = outcome.reason != "running"
        return event["belief"], outcome.reward, outcome.terminated, outcome.truncated, event

    def close(self):
        if self.closed.is_set():
            return
        self.closed.set()
        with suppress(queue.Full):
            self.actions.put_nowait(None)
        if self.worker is not None:
            self.worker.join(timeout=15)
            if self.worker.is_alive():
                raise TimeoutError("Owned runtime has not completed cleanup; no unrelated process was killed")
        self.lease.release()
