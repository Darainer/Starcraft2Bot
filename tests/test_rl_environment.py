import asyncio
import queue
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

pytest.importorskip("torch")

from s2clientprotocol import sc2api_pb2 as pb
from sc2.data import Status
from sc2.ids.unit_typeid import UnitTypeId as U
from test_rl_actions import sample
from test_rl_encoding import assessment, from_assessment, settings
from test_rl_learning import belief, manifest
from test_runtime import FakeSocket

from source import runtime
from source.games.starcraft2 import environment
from source.games.starcraft2.environment import Effects, EnvironmentDirector, LocalEnvironment
from source.games.starcraft2.observation import ObservationAdapter
from source.scouting_facts import ScoutingFacts
from source.training.records import Outcome


class FakeLease:
    def __init__(self):
        self.acquired = False

    def acquire(self):
        self.acquired = True

    def release(self):
        self.acquired = False


def test_owned_environment_reset_step_close_and_disconnect(tmp_path):
    cleaned = []
    lease = FakeLease()

    async def fake_runtime(installation, map_path, players, replay, report, **options):
        env = players[0].ai.environment
        try:
            env.events.put({"belief": belief(), "outcome": Outcome("running"), "manifest": manifest()})
            action = env.actions.get(timeout=2)
            if action == "disconnect":
                raise RuntimeError("synthetic disconnected owned client")
            env.events.put(
                {"belief": belief(102, 2285, False), "outcome": Outcome("time_limit"), "manifest": manifest()}
            )
        finally:
            cleaned.append(env.episode_id)

    game_map = tmp_path / "map.SC2Map"
    game_map.write_bytes(b"synthetic only")
    install = SimpleNamespace(root=tmp_path, report=lambda: {})
    env = LocalEnvironment(install, game_map, tmp_path / "episodes", runtime=fake_runtime, lease=lease)
    state, _ = env.reset(31, manifest())
    assert state.shared.episode_start
    after, reward, terminated, truncated, _ = env.step(None)
    assert truncated and not terminated and reward == 0 and after.assessment.time == 102
    env.close()
    env.close()
    assert not lease.acquired and len(cleaned) == 1
    env.reset(31, manifest())
    with pytest.raises(RuntimeError, match="disconnected"):
        env.step("disconnect")
    env.close()
    assert len(cleaned) == 2


def test_global_client_limit_refuses_ninth_and_releases_startup_lock(monkeypatch, tmp_path):
    monkeypatch.setattr(environment, "live_client_count", lambda: 8)
    lease = environment.ClientLease(tmp_path / "leases")
    with pytest.raises(RuntimeError, match="eight"):
        lease.acquire()
    assert lease.stream is None
    monkeypatch.setattr(environment, "live_client_count", lambda: 7)
    lease.acquire()
    other = environment.ClientLease(tmp_path / "leases")
    with pytest.raises(OSError):
        other.acquire()
    lease.release()
    other.acquire()
    other.release()


def test_shared_client_retains_actual_observation_and_final_boundary(monkeypatch):
    response = pb.Response(
        status=Status.in_game.value,
        observation=pb.ResponseObservation(observation=pb.Observation(game_loop=64)),
    )
    client = runtime.SharedClient(FakeSocket([response]))
    captured = asyncio.run(client.observation())
    assert client.latest_observation is captured
    bot = SimpleNamespace(
        client=client,
        state=SimpleNamespace(game_loop=32),
        game_info=SimpleNamespace(_proto=pb.ResponseGameInfo()),
        _prepare_step=Mock(),
    )
    assert runtime.prepare_final_observation(bot) == 64
    assert bot._prepare_step.call_args.args[0].game_loop == 64
    bot.state.game_loop = 65
    with pytest.raises(RuntimeError, match="backwards"):
        runtime.prepare_final_observation(bot)
    client.latest_observation = None
    with pytest.raises(RuntimeError, match="Missing"):
        runtime.prepare_final_observation(bot)


def test_observation_entities_preserve_selected_and_released_ownership(bot, make_unit, populate):
    units = [
        make_unit(U.NEXUS),
        make_unit(U.PROBE),
        make_unit(U.STALKER, is_selected=True),
        make_unit(U.STALKER),
        make_unit(U.MARINE, alliance=4),
    ]
    populate(*units)
    bot.control.settings = settings()
    bot.control.released.add(units[3].tag)
    bot.state.response_observation = pb.ResponseObservation(observation=pb.Observation(game_loop=224))
    bot.state.score = SimpleNamespace(collection_rate_minerals=800, collection_rate_vespene=200)
    adapter = ObservationAdapter(ScoutingFacts({}))
    state = adapter.observe(
        bot, assessment(time=10, version=224), episode_start=True, issued=({"id": "queued"},), effects=()
    )
    controlled = [e for e in state.shared.entities if e.group == "controlled"]
    eligibility = [next(f.value for f in e.features if f.name == "control_eligible") for e in controlled]
    assert eligibility.count(0) == 2 and eligibility.count(1) == 2
    assert len([e for e in state.shared.entities if e.group == "contact"]) == 1
    assert all("STALKER" not in e.handle and "MARINE" not in e.handle for e in state.shared.entities)
    features = {f.name: f for f in state.shared.features}
    assert features["own.income_primary"].value == 0.8
    assert features["execution.issued_count"].value == 0.01
    assert features["execution.observed_effect_count"].value == 0
    assert bot.settings.scouting  # Automatic baseline scouts retain their setting.
    assert not state.permissions.scouting
    assert dict(state.shared.capabilities)["reconnaissance"] is False
    from source.games.starcraft2.action_codec import masks_for

    assert masks_for(state, 0).active[3] is False


def test_effects_require_observed_changes_and_do_not_treat_queue_as_effect(bot, make_unit, populate):
    tracker = Effects()
    populate(make_unit(U.PROBE, position=(0, 0), tag=1))
    assert tracker.observe(bot) == []
    populate(make_unit(U.PROBE, position=(2, 0), tag=1))
    result = tracker.observe(bot)
    assert result[0]["event"] == "observed_movement"
    assert "intent" not in result[0]


def test_returning_ready_contacts_are_not_reported_as_new_production(bot, make_unit, populate):
    tracker = Effects()
    base, worker = make_unit(U.NEXUS, tag=1), make_unit(U.PROBE, tag=2)
    populate(base, worker)
    assert tracker.observe(bot) == []
    populate(base)  # For example, a worker is temporarily inside a gas building.
    assert tracker.observe(bot) == []
    populate(base, worker)
    assert tracker.observe(bot)[0]["event"] == "observed_ready_contact_appeared"


def test_close_cancels_an_owned_runtime_while_no_director_callback_is_running(tmp_path):
    cleaned = []

    async def waiting_runtime(installation, map_path, players, replay, report, **options):
        env = players[0].ai.environment
        try:
            env.events.put({"belief": belief(), "outcome": Outcome("running"), "manifest": manifest()})
            await asyncio.Event().wait()
        finally:
            cleaned.append(env.episode_id)

    game_map = tmp_path / "map.SC2Map"
    game_map.write_bytes(b"synthetic")
    env = LocalEnvironment(
        SimpleNamespace(root=tmp_path, report=lambda: {}),
        game_map,
        tmp_path / "episodes",
        runtime=waiting_runtime,
        lease=FakeLease(),
    )
    env.reset(31, manifest())
    env.close()
    assert cleaned == [env.episode_id] and not env.worker.is_alive()
    assert env.report.data["training_termination"] == "aborted"


def test_environment_director_decodes_action_at_existing_policy_seam():
    state = assessment()
    current = from_assessment(state, settings(), episode_start=True)
    recorded = sample(current)
    env = SimpleNamespace(
        events=queue.Queue(),
        actions=queue.Queue(),
        closed=__import__("threading").Event(),
        lease=FakeLease(),
        inference_timeout=1,
        controller="policy",
    )
    env.actions.put(recorded)
    bot = SimpleNamespace(
        effects=SimpleNamespace(observe=lambda _: []),
        issued=[],
        previous_decision=None,
        adapter=SimpleNamespace(observe=lambda *args, **kwargs: current),
        manifest=manifest(),
        last_decoded=None,
    )
    director = EnvironmentDirector(bot, env)
    plan = director.decide(state)
    assert director.active is plan and plan.objective == "pressure"
    assert bot.last_decoded.sampled is recorded
    director.report_failure("natural", 100)
    assert director.blocked["natural"] == 130
