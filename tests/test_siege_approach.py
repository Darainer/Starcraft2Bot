from dataclasses import replace

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source.army_waves import ArmyWaves
from source.game_assessment import GameAssessment
from source.missions import MissionPlanner, retreat_geometry
from source.siege_approach import approach_siege
from source.strategic_plan import MissionSpec, StrategicPlan
from source.tactics import TacticalController


def setup_siege(bot, make_unit, populate):
    weapon = bot.game_data.units[U.SIEGETANKSIEGED.value]._proto.weapons[0]
    weapon.range, weapon.damage, weapon.speed, weapon.type = 13, 35, 2.14, 1
    units = [make_unit(U.STALKER, (0, i * 0.5)) for i in range(8)]
    tank = make_unit(U.SIEGETANKSIEGED, (16, 0), alliance=4)
    populate(*units, tank)
    bot.settings.attack = True
    return bot.units, Units([tank], bot), Point2((40, 0))


def test_front_weapon_envelope_triggers_approach_before_anchor_distance_ten(bot, make_unit, populate):
    squad, contacts, goal = setup_siege(bot, make_unit, populate)
    assert squad.center.distance_to(contacts.first) > 10
    result = approach_siege(bot, squad, contacts, goal, {}, retreat_geometry(contacts))
    assert result["siege_phase"] == "approach"
    point = Point2(result["approach_goal"])
    assert abs(point.y - squad.center.y) > 2
    assert point.distance_to(contacts.first) > squad.center.towards(goal, 8).distance_to(contacts.first)


def test_approach_is_latched_then_allows_deliberate_assault(bot, make_unit, populate):
    squad, contacts, goal = setup_siege(bot, make_unit, populate)
    geometry = retreat_geometry(contacts)
    first = approach_siege(bot, squad, contacts, goal, {}, geometry)
    assert approach_siege(bot, squad, contacts, goal, first, geometry) == first
    bot.state.game_loop += 224
    commit = approach_siege(bot, squad, contacts, goal, first, geometry)
    assert commit["siege_phase"] == "commit"
    assert approach_siege(bot, squad, contacts, goal, commit, geometry) == commit


def test_shootable_tank_does_not_force_an_extra_standoff(bot, make_unit, populate):
    squad, contacts, goal = setup_siege(bot, make_unit, populate)
    contacts.first._proto.pos.x = 5
    assert (
        approach_siege(bot, squad, contacts, goal, {}, retreat_geometry(contacts))["siege_phase"] == "commit"
    )


def test_hidden_tank_or_air_only_force_does_not_claim_ground_danger(bot, make_unit, populate):
    squad, contacts, goal = setup_siege(bot, make_unit, populate)
    contacts.first._proto.display_type = 2
    assert approach_siege(bot, squad, contacts, goal, {}, retreat_geometry(contacts)) is None
    contacts.first._proto.display_type = 1
    flying = Units([make_unit(U.VOIDRAY)], bot)
    flying.first._proto.is_flying = True
    assert approach_siege(bot, flying, contacts, goal, {}, retreat_geometry(contacts)) is None


def test_blocked_lateral_routes_never_claim_a_traversable_approach(bot, make_unit, populate):
    squad, contacts, goal = setup_siege(bot, make_unit, populate)
    bot.in_pathing_grid = lambda point: False
    assert approach_siege(bot, squad, contacts, goal, {}, retreat_geometry(contacts)) is None


def test_approach_survives_order_arbitration_and_micro_while_critical_escape_wins(bot, make_unit, populate):
    squad, contacts, goal = setup_siege(bot, make_unit, populate)
    marine = make_unit(U.MARINE, (3, 0), alliance=4)
    populate(*squad, contacts.first, marine, make_unit(U.NEXUS))
    army = bot.units(U.STALKER)
    state = GameAssessment().observe(bot, army)
    state = replace(state, threat=tuple(goal), threat_supply=20)
    spec = MissionSpec("main", "main", "threat", tuple(goal), state.army_supply, 0, 100)
    plan = StrategicPlan(
        1,
        state.version,
        bot.time,
        bot.time + 20,
        "stabilize",
        (spec,),
        state.production,
        False,
        "Test approach",
    )
    planner = MissionPlanner()
    result = planner.execute(bot, army, plan, state, ArmyWaves(), preserve_combat=True)
    assert result["missions"]["main"]["phase"] == "approach"
    assert result["orders"] and all(order["action"] == "move" for order in result["orders"])
    bot._used.clear()
    bot.actions.clear()
    controller = TacticalController()
    controller.active_mode = "defend"
    controller.missions = planner
    assert controller.micro(bot) == []
    army.first._proto.health = 1
    army.first._proto.shield = 0
    assert controller.micro(bot)[0]["action"] == "individual_retreat"
