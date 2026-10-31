from s2clientprotocol import common_pb2, raw_pb2
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2, Rect

from source.action_intents import ActionExecutor, ActionIntent
from source.army_waves import ArmyWaves, terrain_destination
from source.strategy_profiles import PROFILES


def test_walkable_endpoint_across_cliff_uses_actual_goal(bot, make_unit):
    unit = make_unit(U.STALKER)
    slot, goal = Point2((10, 0)), Point2((30, 10))
    bot.in_pathing_grid = lambda p: not (3 < p.x < 6 and abs(p.y) < 3)
    assert bot.in_pathing_grid(slot)
    assert terrain_destination(bot, unit, slot, goal) == goal


def test_invalid_slot_and_blocked_goal_choose_deterministic_walkable_goal(bot, make_unit):
    unit = make_unit(U.STALKER)
    slot, goal = Point2((10, 0)), Point2((30, 10))
    bot.in_pathing_grid = lambda p: p.distance_to(goal) >= 1 and p.distance_to(slot) >= 1
    result = terrain_destination(bot, unit, slot, goal)
    assert bot.in_pathing_grid(result)
    assert result.distance_to(goal) <= 2.001
    assert terrain_destination(bot, unit, slot, goal) == result


def test_valid_formation_and_flying_orders_are_unchanged(bot, make_unit):
    unit = make_unit(U.STALKER)
    slot, goal = Point2((10, 0)), Point2((30, 10))
    assert terrain_destination(bot, unit, slot, goal) == slot
    bot.in_pathing_grid = lambda p: False
    flying = make_unit(U.STALKER, is_flying=True)
    assert terrain_destination(bot, flying, slot, goal) == slot


def test_advancing_ground_wave_routes_around_invalid_slots_without_reassembling(bot, make_unit, populate):
    units = [make_unit(U.STALKER) for _ in range(6)]
    populate(*units)
    waves = ArmyWaves()
    waves.members = {u.tag for u in units}
    waves.phase = "advance"
    bot.in_pathing_grid = lambda p: not 9 < p.x < 15
    goal = Point2((30, 0))
    orders, report = waves.plan(bot, bot.units, goal, Point2((-20, 0)), PROFILES["pressure"])
    assert report["phase"] == "advance"
    assert waves.members == {u.tag for u in units}
    assert all(point == goal for mode, point in orders.values())
    bot.control.released.add(units[0].tag)
    orders, _ = waves.plan(bot, bot.units, goal, Point2((-20, 0)), PROFILES["pressure"])
    assert units[0].tag not in orders


def test_invalid_nearby_standing_order_is_replaced_with_walkable_destination(bot, make_unit, populate):
    old = Point2((10, 0))
    safe = Point2((10.5, 0))
    unit = make_unit(
        U.STALKER,
        orders=[
            raw_pb2.UnitOrder(
                ability_id=A.MOVE_MOVE.value, target_world_space_pos=common_pb2.Point(x=old.x, y=old.y)
            )
        ],
    )
    populate(unit)
    bot.settings.attack = True
    bot.in_pathing_grid = lambda p: p != old
    executor = ActionExecutor()
    executor.assign({unit.tag: "main"})
    intent = ActionIntent(
        unit.tag,
        executor.assignments[unit.tag][1],
        bot.state.game_loop,
        bot.state.game_loop + 8,
        "move",
        tuple(safe),
    )
    assert executor.execute(bot, intent)
    assert len(bot.actions) == 1 and bot.actions[0].target == safe


def test_edge_slots_and_cached_orders_do_not_query_outside_map(bot, make_unit, populate):
    bot.game_info.playable_area = Rect((0, 0, 20, 20))

    def grid(point):
        assert 0 <= point.x < 20 and 0 <= point.y < 20
        return True

    bot.in_pathing_grid = grid
    unit = make_unit(U.STALKER, (1, 1))
    assert terrain_destination(bot, unit, Point2((-1, 1)), Point2((10, 10))) == Point2((10, 10))
    flying = make_unit(U.STALKER, (1, 1), is_flying=True)
    assert terrain_destination(bot, flying, Point2((-1, 1)), Point2((10, 10))) == Point2((10, 10))
    old = Point2((-0.2, 0))
    safe = Point2((0.2, 0))
    unit = make_unit(
        U.STALKER,
        orders=[
            raw_pb2.UnitOrder(
                ability_id=A.MOVE_MOVE.value, target_world_space_pos=common_pb2.Point(x=old.x, y=old.y)
            )
        ],
    )
    populate(unit)
    bot.settings.attack = True
    executor = ActionExecutor()
    executor.assign({unit.tag: "main"})
    assert executor.execute(
        bot,
        ActionIntent(
            unit.tag,
            executor.assignments[unit.tag][1],
            bot.state.game_loop,
            bot.state.game_loop + 8,
            "move",
            tuple(safe),
        ),
    )
