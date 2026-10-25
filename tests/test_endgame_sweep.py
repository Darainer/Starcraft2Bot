from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source.endgame_sweep import EndgameSweep, exposed_base_target, group_center


def test_group_center_and_exposed_base_prefer_undefended_resource_center(bot, make_unit):
    first = make_unit(U.STALKER, (10, 10))
    second = make_unit(U.STALKER, (20, 20))
    assert group_center([first, second]) == Point2((15, 15))

    defended = make_unit(U.NEXUS, (80, 80), alliance=4)
    exposed = make_unit(U.NEXUS, (20, 20), alliance=4)
    cannon = make_unit(U.PHOTONCANNON, (80, 81), alliance=4)
    bot.enemy_units = Units([defended, exposed, cannon], bot)
    buildings = Units([defended, exposed, cannon], bot)
    assert exposed_base_target(bot, buildings, Units([first], bot)) == exposed


def test_exposed_target_skips_unhittable_flying_base(bot, make_unit):
    flying = make_unit(U.COMMANDCENTER, (20, 20), alliance=4, is_flying=True)
    bot.enemy_units = Units([], bot)
    assert exposed_base_target(bot, Units([flying], bot), Units([], bot)) is None


def test_sweep_assigns_units_searches_and_answers_base_raid(bot, make_unit, populate):
    army = [make_unit(U.STALKER, (40, 40)) for _ in range(15)]
    base = make_unit(U.NEXUS, (0, 0))
    raid = make_unit(U.MARINE, (5, 5), alliance=4)
    populate(*army, base, raid)
    bot.enemy_units = Units([raid], bot)
    bot.game_info.start_locations = [Point2((100, 100))]
    bot._expansion_positions_list = [Point2((100, 100)), Point2((80, 80)), Point2((40, 40))]
    sweep = EndgameSweep()
    sweep.start()

    destinations, report = sweep.plan(bot, bot.units, Units([], bot), Units([raid], bot), bot.townhalls)
    assert len(destinations) == 15
    assert len({group for group in sweep.assignments.values()}) == 3
    assert report["mode"] == "split_search"
    assert next(group for group in report["groups"] if group["id"] == 2)["phase"] == "respond_to_base_raid"
    assert all(mode in {"move", "attack"} for mode, target in destinations.values())

    # Dead or unavailable tags are dropped and their slots can be reassigned.
    populate(*army[3:], base, raid)
    destinations, report = sweep.plan(bot, bot.units, Units([], bot), Units([], bot), bot.townhalls)
    assert len(destinations) == 12
    assert set(sweep.assignments) == {unit.tag for unit in army[3:]}


def test_sweep_tracks_sites_and_denies_clear_expansions(bot, make_unit, populate):
    army = [make_unit(U.STALKER, (100, 100)) for _ in range(15)]
    base = make_unit(U.NEXUS, (0, 0))
    populate(*army, base)
    bot.game_info.start_locations = [Point2((100, 100))]
    bot._expansion_positions_list = [Point2((80, 80)), Point2((40, 40))]
    sweep = EndgameSweep()
    sweep.start()
    sweep.visited_sites.update({0, 1, 2})

    destinations, report = sweep.plan(bot, bot.units, Units([], bot), Units([], bot), bot.townhalls)
    assert report["scouting_complete"]
    assert set(report["denial_sites"]) == {"1", "2"}
    assert all(destination.distance_to(Point2((40, 40))) > 0 for mode, destination in destinations.values())


def test_sweep_uses_map_center_without_known_enemy_start(bot, make_unit, populate):
    army = [make_unit(U.STALKER, (10, 10)) for _ in range(3)]
    populate(*army)
    bot.game_info.start_locations = []
    bot._expansion_positions_list = []
    sweep = EndgameSweep()
    destinations, report = sweep.plan(bot, bot.units, Units([], bot), Units([], bot), Units([], bot))
    assert report["site_count"] == 1
    assert all(mode == "move" for mode, target in destinations.values())


def test_sweep_clears_visible_non_base_structures_and_sends_wounded_unit_home(bot, make_unit, populate):
    army = [make_unit(U.STALKER, (40, 40)) for _ in range(9)]
    army[0]._proto.health = 10
    army[0]._proto.shield = 0
    base = make_unit(U.NEXUS, (0, 0))
    gateway = make_unit(U.GATEWAY, (80, 80), alliance=4)
    populate(*army, base, gateway)
    bot.game_info.start_locations = [Point2((100, 100))]
    bot._expansion_positions_list = [Point2((80, 80)), Point2((40, 40))]
    sweep = EndgameSweep()

    destinations, report = sweep.plan(bot, bot.units, Units([gateway], bot), Units([], bot), bot.townhalls)
    assert report["groups"][0]["phase"] == "clear_visible_structure"
    assert destinations[army[0].tag][0] == "move"
    assert destinations[army[0].tag][1] == base.position
    assert report["groups"][1]["phase"] == "clear_visible_structure"
