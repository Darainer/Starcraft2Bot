from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.army_waves import ArmyWaves
from source.game_assessment import GameAssessment
from source.missions import MissionPlanner
from source.strategic_plan import MissionSpec, StrategicPlan
from source.strategy_profiles import PROFILES


def engagement(bot, make_unit, populate, distance=9, kind=U.STALKER):
    bot.settings.attack = True
    bot.settings.profile = "pressure"
    bot.game_data.units[kind.value]._proto.weapons[0].range = 6 if kind == U.STALKER else 0.1
    bot.game_data.units[kind.value]._proto.weapons[0].type = 1
    army = [make_unit(kind, (0, i * 0.1)) for i in range(8)]
    marine = make_unit(U.MARINE, (distance, 0), alliance=4)
    populate(*army, marine)
    waves = ArmyWaves()
    waves.members = set(bot.units.tags)
    return waves, marine


def orders(bot, waves):
    return waves.plan(bot, bot.units, Point2((40, 0)), Point2((0, 0)), PROFILES["pressure"])


def test_out_of_range_ranged_wave_closes_instead_of_attacking_its_own_anchor(bot, make_unit, populate):
    waves, marine = engagement(bot, make_unit, populate)
    assert all(not unit.target_in_range(marine) for unit in bot.units)
    destinations, state = orders(bot, waves)
    assert state["phase"] == "engage"
    assert all(mode == "attack" and point == marine.position for mode, point in destinations.values())


def test_melee_units_close_to_the_actual_contact(bot, make_unit, populate):
    waves, marine = engagement(bot, make_unit, populate, kind=U.ZEALOT)
    destinations, _ = orders(bot, waves)
    assert all(point == marine.position for _, point in destinations.values())


def test_units_already_in_range_keep_the_existing_engagement_slots(bot, make_unit, populate):
    waves, marine = engagement(bot, make_unit, populate, distance=5)
    assert all(unit.target_in_range(marine) for unit in bot.units)
    destinations, _ = orders(bot, waves)
    assert all(point != marine.position for _, point in destinations.values())


def test_ground_only_wave_does_not_chase_air_or_a_distant_ground_contact(bot, make_unit, populate):
    waves, marine = engagement(bot, make_unit, populate, kind=U.ZEALOT)
    flying = make_unit(U.VOIDRAY, (9, 0), alliance=4)
    flying._proto.is_flying = True
    marine._proto.pos.x = 30
    populate(*bot.units, marine, flying)
    destinations, state = orders(bot, waves)
    assert state["phase"] == "engage"
    assert all(point not in {marine.position, flying.position} for _, point in destinations.values())


def test_hidden_contacts_never_trigger_closing_orders(bot, make_unit, populate):
    waves, marine = engagement(bot, make_unit, populate)
    marine._proto.display_type = 2
    destinations, state = orders(bot, waves)
    assert state["phase"] != "engage"
    assert all(point != marine.position for _, point in destinations.values())


def test_closing_orders_pass_mission_arbitration_and_keep_released_actors_owned_by_user(
    bot, make_unit, populate
):
    waves, marine = engagement(bot, make_unit, populate)
    populate(*bot.units, marine, make_unit(U.NEXUS, (-20, 0)))
    bot.settings.army_waves = True
    released = bot.units.first.tag
    bot.control.released.add(released)
    state = GameAssessment().observe(bot, bot.units)
    spec = MissionSpec("main", "main", "site:0", (40, 0), state.army_supply, 0, 100)
    plan = StrategicPlan(
        1, state.version, bot.time, bot.time + 20, "pressure", (spec,), state.production, False, "Test range"
    )
    result = MissionPlanner().execute(bot, bot.units, plan, state, waves, preserve_combat=True)
    assert result["missions"]["main"]["phase"] == "engage"
    assert bot.actions and all(action.target == marine.position for action in bot.actions)
    assert released not in {action.unit.tag for action in bot.actions}
