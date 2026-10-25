"""Policy scenarios use plain facts: no game process or model service."""

import asyncio
from dataclasses import replace

import pytest

from source.strategic_plan import Assessment, Opportunity, validate_plan
from source.strategy_director import DeferredPolicy, StrategicDirector


@pytest.fixture
def assessment():
    return Assessment(
        version=2240,
        time=100,
        profile="pressure",
        army_supply=60,
        army_count=30,
        health=1,
        local_advantage=2,
        threat_supply=0,
        home_advantage=2,
        home=(0, 0),
        rally=(8, 8),
        threat=None,
        targets=(
            Opportunity("natural", (80, 80), 100, True, True, 65, 0, 2, 40),
            Opportunity("third", (60, 60), 100, True, True, 60, 0, 2, 45),
        ),
        intel_age=0,
        minerals=400,
        gas=200,
        workers=50,
        bases=3,
        production=(("stalkers", 40), ("zealots", 12)),
    )


def test_pressure_and_denial_share_budget(assessment):
    plan = StrategicDirector().decide(assessment)
    assert plan.objective == "pressure"
    assert {m.role for m in plan.missions} == {"main", "deny"}
    assert sum(m.supply_budget for m in plan.missions) == assessment.army_supply
    assert len({m.target_id for m in plan.missions}) == 2
    assert validate_plan(plan, assessment) is plan
    assert plan.expand


@pytest.mark.parametrize(
    "change,objective",
    [
        ({"army_supply": 10, "army_count": 5}, "develop"),
        ({"health": 0.2}, "recover"),
        ({"trade_bad": True}, "recover"),
        ({"local_advantage": 0.6}, "recover"),
        ({"threat_supply": 30, "threat": (4, 4)}, "stabilize"),
        ({"recently_defended": True}, "counterattack"),
        ({"recently_defended": True, "local_advantage": 10}, "counterattack"),
        ({"cleanup_ready": True, "local_advantage": 4}, "finish"),
        ({"targets": ()}, "develop"),
    ],
)
def test_strategic_scenarios(assessment, change, objective):
    state = replace(assessment, **change)
    plan = StrategicDirector().decide(state)
    assert plan.objective == objective
    if objective in {"recover", "stabilize"}:
        assert not plan.expand


def test_small_raid_coexists_with_pressure_but_requires_local_response(assessment):
    state = replace(assessment, threat_supply=6, threat=(5, 5))
    plan = StrategicDirector().decide(state)
    assert plan.objective == "pressure"
    assert {m.role for m in plan.missions} == {"main", "defend"}
    assert not plan.expand
    weak = StrategicDirector().decide(replace(state, home_advantage=0.5))
    assert len(weak.missions) == 1 and weak.missions[0].target_id == "home"
    assert weak.missions[0].mode == "move"


def test_fortified_natural_yields_to_exposed_third(assessment):
    natural, third = assessment.targets
    state = replace(assessment, targets=(replace(natural, defense=9000, advantage=0.4), third))
    plan = StrategicDirector().decide(state)
    assert plan.missions[-1].target_id == "third"
    assert len(plan.missions) == 1
    plan = StrategicDirector().decide(replace(state, targets=(state.targets[0],)))
    assert plan.objective == "contain"
    assert plan.missions[-1].mode == "move"


def test_commitment_target_failure_and_emergency_interrupt(assessment):
    director = StrategicDirector()
    assert director.decide(assessment).missions[-1].target_id == "natural"
    natural, third = assessment.targets
    changed = replace(assessment, time=102, targets=(natural, replace(third, value=70)))
    assert director.decide(changed).missions[-1].target_id == "natural"
    director.report_failure("natural", 102)
    assert director.decide(changed).missions[-1].target_id == "third"
    assert director.decide(replace(changed, trade_bad=True)).objective == "recover"
    director.report_failure("home", 102)
    assert director.decide(replace(changed, trade_bad=True)).objective == "recover"
    director.report_failure("rally", 102)
    assert director.decide(replace(changed, army_supply=0, army_count=0)).objective == "develop"
    later = replace(assessment, time=140)
    assert director.decide(later).missions[-1].target_id == "natural"
    assert len(director.history) >= 4


def test_failed_target_is_not_reissued_as_secondary_raid(assessment):
    director = StrategicDirector()
    plan = director.decide(assessment)
    failed = next(m.target_id for m in plan.missions if m.role == "deny")
    director.report_failure(failed, assessment.time)
    plan = director.decide(assessment)
    assert all(m.target_id != failed for m in plan.missions)


def test_active_pressure_uses_lower_exit_threshold(assessment):
    director = StrategicDirector()
    director.decide(assessment)
    reduced = replace(assessment, army_supply=12, army_count=6)
    assert director.decide(reduced).objective == "pressure"
    assert StrategicDirector().decide(reduced).objective == "develop"
    assert director.decide(replace(reduced, army_supply=4, army_count=2)).objective == "develop"


def test_stale_fog_cannot_authorize_denial(assessment):
    fog = tuple(replace(t, visible=False, seen_at=30) for t in assessment.targets)
    state = replace(assessment, targets=fog, timing_ready=True, profile="fortress")
    plan = StrategicDirector().decide(state)
    assert len(plan.missions) == 1
    assert plan.scores
    assert state.to_dict()["targets"][0]["visible"] is False


@pytest.mark.parametrize(
    "case",
    [
        "type",
        "objective",
        "future",
        "old",
        "expired",
        "long_expiry",
        "duplicate",
        "role",
        "mode",
        "target",
        "vision",
        "nan",
        "negative",
        "overcommit",
        "empty",
        "production",
        "duplicate_production",
        "production_type",
        "two_main",
    ],
)
def test_invalid_plans_rejected(assessment, case):
    plan = StrategicDirector().decide(assessment)
    main = plan.missions[-1]
    changes = {
        "objective": {"objective": "nuke"},
        "future": {"created_at": 101},
        "old": {"created_at": 90},
        "expired": {"expires_at": 99},
        "long_expiry": {"expires_at": 500},
        "duplicate": {"missions": (main, main)},
        "role": {"missions": (replace(main, role="hacker"),)},
        "mode": {"missions": (replace(main, mode="spell"),)},
        "target": {"missions": (replace(main, target_id="unknown"),)},
        "vision": {"missions": (replace(main, target_id="home", target=(0, 0), require_visible=True),)},
        "nan": {"missions": (replace(main, supply_budget=float("nan")),)},
        "negative": {"missions": (replace(main, minimum_supply=-1),)},
        "overcommit": {"missions": (main, replace(main, id="raid", role="deny"))},
        "empty": {"missions": ()},
        "production": {"production": (("battlecruisers", 20),)},
        "duplicate_production": {"production": (("stalkers", 20), ("stalkers", 40))},
        "production_type": {"production": (("stalkers", True),)},
        "two_main": {"missions": (main, replace(main, id="second"))},
    }
    proposal = {} if case == "type" else replace(plan, **changes[case])
    with pytest.raises(ValueError):
        validate_plan(proposal, assessment)


def test_async_policy_does_not_block_and_rejects_stale_result(assessment):
    async def scenario():
        gate = asyncio.Event()

        class Backend:
            async def propose(self, state):
                await gate.wait()
                return StrategicDirector().decide(state)

        policy = DeferredPolicy(Backend(), max_requests=2)
        assert policy.request(assessment)
        assert not policy.request(assessment)
        assert policy.poll(assessment) is None
        gate.set()
        await policy.pending
        assert policy.poll(assessment).objective == "pressure"
        assert policy.last_error is None
        assert policy.request(assessment)
        await policy.pending
        assert policy.poll(replace(assessment, time=110)) is None
        assert "Stale" in policy.last_error
        assert not policy.request(assessment)
        assert "budget" in policy.last_error

    asyncio.run(scenario())


def test_async_policy_timeout_error_and_revocation(assessment):
    async def scenario():
        class Backend:
            async def propose(self, state):
                await asyncio.Event().wait()

        policy = DeferredPolicy(Backend(), timeout=0.001)
        policy.request(assessment)
        await asyncio.sleep(0.02)
        assert policy.poll(assessment) is None and policy.last_error
        policy.request(assessment)
        pending = policy.pending
        policy.interrupt()
        await asyncio.gather(pending, return_exceptions=True)
        assert policy.poll(assessment) is None
        policy.interrupt()

        class Broken:
            async def propose(self, state):
                raise ValueError("bad backend")

        broken = DeferredPolicy(Broken())
        broken.request(assessment)
        await asyncio.gather(broken.pending, return_exceptions=True)
        assert broken.poll(assessment) is None
        assert broken.last_error == "bad backend"

    asyncio.run(scenario())
