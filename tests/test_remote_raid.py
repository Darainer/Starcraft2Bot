"""Load only the four isolated 9fd64a1-based candidate modules."""
# ruff: noqa: E402 -- staged modules must load before their consumers.

from dataclasses import replace

from sc2.ids.unit_typeid import UnitTypeId as U

from source.army_waves import ArmyWaves
from source.game_assessment import GameAssessment
from source.missions import MissionPlanner
from source.strategic_plan import Assessment, Opportunity, validate_plan
from source.strategy_director import StrategicDirector


def facts(**changes):
    state = Assessment(
        224,
        10,
        "pressure",
        142,
        71,
        1,
        10,
        2,
        0,
        (0, 0),
        (8, 8),
        (80, 80),
        (Opportunity("base", (100, 100), 10, True, True, 65, 0, 2, 40),),
        0,
        400,
        200,
        56,
        3,
        (("stalkers", 40),),
        raid_response_tags=(1, 2, 3, 4),
        raid_response_supply=8,
        raid_response_advantage=2,
    )
    return replace(state, **changes)


def test_remote_small_raid_gets_bounded_response_and_pressure_continues():
    state = facts()
    plan = validate_plan(StrategicDirector().decide(state), state)
    assert plan.objective == "pressure"
    assert [(m.role, m.supply_budget) for m in plan.missions] == [("defend", 8), ("main", 134)]


def test_heavy_threat_rush_and_inadequate_response_keep_full_defense():
    for changes in (
        {"threat_supply": 20},
        {"rush_warning": True},
        {"raid_response_advantage": 0.5},
        {"raid_response_tags": ()},
        {"army_supply": 30},
        {"raid_response_supply": 60},
    ):
        plan = StrategicDirector().decide(facts(**changes))
        assert plan.objective == "stabilize"
        assert len(plan.missions) == 1


def test_legacy_assessment_remains_conservative():
    state = facts(raid_response_tags=(), raid_response_supply=0, raid_response_advantage=0)
    data = state.to_dict()
    for key in tuple(data):
        if key.startswith("raid_response_"):
            del data[key]
    from source.replay_strategy import assessment_from_dict

    legacy = assessment_from_dict(data)
    assert StrategicDirector().decide(legacy).objective == "stabilize"


def test_projected_response_uses_only_units_that_can_hit_air_and_preserves_main(bot, make_unit, populate):
    bot.game_data.units[U.ZEALOT.value]._proto.weapons[0].type = 1
    zealots = [make_unit(U.ZEALOT) for _ in range(50)]
    stalkers = [make_unit(U.STALKER) for _ in range(21)]
    populate(
        *zealots,
        *stalkers,
        make_unit(U.NEXUS),
        make_unit(U.NEXUS, (80, 80)),
        make_unit(U.MUTALISK, (81, 80), alliance=4, is_flying=True),
        make_unit(U.MUTALISK, (82, 80), alliance=4, is_flying=True),
    )
    bot.settings.attack = True
    bot.settings.profile = "pressure"
    state = GameAssessment().observe(bot, bot.units)
    assert state.home_advantage == 0
    assert state.raid_response_advantage >= 1.2
    assert set(state.raid_response_tags) <= {unit.tag for unit in stalkers}
    plan = validate_plan(StrategicDirector().decide(state), state)
    assert plan.objective == "pressure"
    result = MissionPlanner().execute(bot, bot.units, plan, state, ArmyWaves())
    response = result["missions"]["home-defense"]
    assert set(response["members"]) == set(state.raid_response_tags)
    assert response["supply"] <= state.army_supply * 0.3
    assert result["missions"]["main"]["supply"] >= 40
    assert len({action.unit.tag for action in bot.actions}) == len(bot.actions)
    bot._used.clear()
    bot.actions.clear()
    bot.control.released.update(state.raid_response_tags)
    MissionPlanner().execute(bot, bot.units, plan, state, ArmyWaves())
    assert not any(action.unit.tag in state.raid_response_tags for action in bot.actions)
    assert len({action.unit.tag for action in bot.actions}) == len(bot.actions)


def test_ground_only_army_does_not_claim_remote_air_response(bot, make_unit, populate):
    bot.game_data.units[U.ZEALOT.value]._proto.weapons[0].type = 1
    populate(
        *(make_unit(U.ZEALOT) for _ in range(30)),
        make_unit(U.NEXUS),
        make_unit(U.MUTALISK, (1, 1), alliance=4, is_flying=True),
    )
    state = GameAssessment().observe(bot, bot.units)
    assert not state.raid_response_tags
    assert state.raid_response_advantage == 0
