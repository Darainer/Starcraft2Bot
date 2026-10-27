from types import SimpleNamespace

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source.army_waves import ArmyWaves
from source.missions import MissionPlanner, retreat_waypoint
from source.strategic_plan import MissionSpec
from source.tactics import TacticalController


def test_retreat_avoids_visible_weapons_instead_of_running_through_them(bot, make_unit):
    unit = make_unit(U.STALKER)
    enemy = make_unit(U.MARINE, (5, 0), alliance=4)
    waypoint = retreat_waypoint(bot, unit, Point2((30, 0)), Units([enemy], bot))
    assert waypoint.distance_to(enemy.position) > unit.distance_to(enemy)
    assert waypoint.distance_to(unit.position) <= 10.001


def test_retreat_checks_entire_ground_segment_but_air_can_cross(bot, make_unit):
    unit = make_unit(U.STALKER)
    bot.in_pathing_grid = lambda point: not 3 < point.x < 5
    goal = Point2((10, 0))
    assert retreat_waypoint(bot, unit, goal, Units([], bot)).x <= 3
    flying = make_unit(U.STALKER, is_flying=True)
    assert retreat_waypoint(bot, flying, goal, Units([], bot)) == goal


def test_unit_at_home_still_escapes_an_attacker_without_zero_length_normalization(bot, make_unit):
    unit = make_unit(U.STALKER)
    enemy = make_unit(U.MARINE, (2, 0), alliance=4)
    waypoint = retreat_waypoint(bot, unit, unit.position, Units([enemy], bot))
    assert waypoint.distance_to(enemy.position) > unit.distance_to(enemy)
    assert retreat_waypoint(bot, unit, unit.position, Units([], bot)) == unit.position


def test_ground_only_weapons_do_not_divert_air_retreat(bot, make_unit):
    bot.game_data.units[U.MARINE.value]._proto.weapons[0].type = 1
    enemy = make_unit(U.MARINE, (5, 0), alliance=4)
    flying = make_unit(U.STALKER, is_flying=True)
    goal = Point2((30, 0))
    assert retreat_waypoint(bot, flying, goal, Units([enemy], bot)) == goal


def test_recovery_goal_survives_home_changes_but_revokes_destroyed_base(bot, make_unit, populate):
    unit = make_unit(U.STALKER, (10, 0))
    first = make_unit(U.NEXUS, (0, 0))
    other = make_unit(U.NEXUS, (80, 0))
    populate(unit, first, other)
    bot.settings.attack = True
    planner = MissionPlanner()
    spec = MissionSpec("main", "main", "home", (0, 0), 2, 0, 100, "move")
    plan = SimpleNamespace(missions=(spec,), objective="recover")
    state = SimpleNamespace(targets=(), home=(0, 0))
    waves = ArmyWaves()
    planner.execute(bot, bot.units, plan, state, waves)
    assert planner.records["main"]["retreat_goal"] == [0, 0]
    bot._used.clear()
    state.home = (80, 0)
    planner.execute(bot, bot.units, plan, state, waves)
    assert planner.records["main"]["retreat_goal"] == [0, 0]
    populate(unit, other)
    bot._used.clear()
    planner.execute(bot, bot.units, plan, state, waves)
    assert planner.records["main"]["retreat_goal"] == [80, 0]


def test_scripted_retreat_keeps_explicit_destination(bot, make_unit, populate):
    populate(make_unit(U.STALKER, (10, 0)), make_unit(U.NEXUS))
    bot.settings.attack = True
    planner = MissionPlanner()
    spec = MissionSpec("main", "main", "script", (50, 50), 2, 0, 100, "move")
    plan = SimpleNamespace(missions=(spec,), objective="recover")
    state = SimpleNamespace(targets=(), home=(0, 0))
    result = planner.execute(bot, bot.units, plan, state, ArmyWaves(), preserve_combat=False)
    assert result["missions"]["main"]["retreat_goal"] == [50, 50]
    assert result["orders"][0]["target"] == [50, 50]


def test_critical_escape_stays_safe_between_strategic_ticks_and_honors_ownership(bot, make_unit, populate):
    weak = make_unit(U.STALKER, health=10, shield=0)
    enemy = make_unit(U.MARINE, (5, 0), alliance=4)
    populate(weak, *(make_unit(U.STALKER) for _ in range(6)), make_unit(U.NEXUS, (30, 0)), enemy)
    bot.settings.attack = True
    bot.settings.strategy = "push"
    bot.settings.army_waves = False
    controller = TacticalController()
    decision = controller.tick(bot)
    assert decision["missions"]["main"]["phase"] == "engage"
    initial = next(action for action in bot.actions if action.unit.tag == weak.tag)
    assert initial.target.distance_to(enemy.position) > weak.distance_to(enemy)
    # The runtime clears the actor budget on the next observation, while the
    # strategic plan remains active until the one-second planning interval.
    for _ in range(2):
        bot._used.clear()
        bot.actions.clear()
        bot.state.game_loop += 8
        controller.micro(bot)
        orders = [action for action in bot.actions if action.unit.tag == weak.tag]
        assert len(orders) == 1
        assert orders[0].target.distance_to(enemy.position) > weak.distance_to(enemy)
        controller.micro(bot)
        assert len([action for action in bot.actions if action.unit.tag == weak.tag]) == 1
    bot._used.clear()
    bot.actions.clear()
    bot.control.released.add(weak.tag)
    controller.micro(bot)
    assert not any(action.unit.tag == weak.tag for action in bot.actions)
