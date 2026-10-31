import json
from dataclasses import replace

import pytest
from sc2.ids.unit_typeid import UnitTypeId as U
from test_remote_raid import facts

from source.game_assessment import GameAssessment
from source.replay_strategy import assessment_from_dict
from source.strategy_director import StrategicDirector


def fighting(**changes):
    state = facts(
        threat_supply=0,
        threat=None,
        health=0.9,
        local_advantage=2,
        trade_bad=True,
        local_fight_observed=True,
    )
    return replace(state, **changes)


@pytest.mark.parametrize("advantage", [1.5, 1.58, 2.56])
def test_healthy_current_favorable_main_fight_continues_despite_trailing_bad_trade(advantage):
    plan = StrategicDirector().decide(fighting(local_advantage=advantage))
    assert plan.objective == "pressure"
    assert plan.missions[-1].mode == "attack"


@pytest.mark.parametrize(
    "changes",
    [
        {"health": 0.2, "trade_bad": False},
        {"local_advantage": 0.7, "trade_bad": False},
        {"health": 0.79},
        {"local_advantage": 1.49},
        {"local_advantage": 10},
        {"local_fight_observed": False},
        {"engagement_evidence_schema_version": 2},
    ],
)
def test_damage_danger_or_missing_current_favorable_evidence_preserves_recovery(changes):
    assert StrategicDirector().decide(fighting(**changes)).objective == "recover"


def test_major_home_emergency_still_commands_full_defense():
    plan = StrategicDirector().decide(fighting(threat_supply=30, threat=(5, 5), home_advantage=0.3))
    assert plan.objective == "stabilize"
    assert len(plan.missions) == 1 and plan.missions[0].target_id == "home"


def test_legacy_assessment_without_engagement_evidence_remains_conservative():
    data = json.loads(json.dumps(fighting().to_dict()))
    data.pop("local_fight_observed")
    data.pop("engagement_evidence_schema_version")
    assert StrategicDirector().decide(assessment_from_dict(data)).objective == "recover"


def test_observed_main_participation_sets_fresh_evidence_but_detached_contact_does_not(
    bot, make_unit, populate
):
    army = [make_unit(U.STALKER) for _ in range(4)]
    enemy = make_unit(U.MARINE, (5, 0), alliance=4)
    populate(*army, enemy, make_unit(U.NEXUS))
    assert GameAssessment().observe(bot, bot.units).local_fight_observed
    detached = [make_unit(U.STALKER)] + [make_unit(U.STALKER, (80, 80)) for _ in range(7)]
    populate(*detached, enemy, make_unit(U.NEXUS))
    state = GameAssessment().observe(bot, bot.units)
    assert not state.local_fight_observed and state.local_advantage == 10
    unseen = make_unit(U.MARINE, (5, 0), alliance=4, display_type=2)
    populate(*army, unseen, make_unit(U.NEXUS))
    state = GameAssessment().observe(bot, bot.units)
    assert not state.local_fight_observed and state.local_advantage == 10
