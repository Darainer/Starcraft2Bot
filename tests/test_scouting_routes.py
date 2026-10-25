from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source.scouting import ScoutController


def test_routes_screen_bases_clamp_and_include_enemy_expansions(bot, make_unit, populate):
    nexus = make_unit(U.NEXUS, (2, 2))
    populate(nexus)
    bot.game_info.map_center = Point2((50, 50))
    bot.game_info.start_locations = [Point2((90, 90))]
    bot._expansion_positions_list = [Point2((80, 80)), Point2((30, 30))]
    bot.game_info.playable_area = type("Area", (), {"x": 0, "y": 0, "width": 100, "height": 100})()
    scout = ScoutController()

    worker_route = scout._worker_route(bot)
    observer_route = scout._observer_route(bot)
    assert worker_route == [Point2((80, 80)), Point2((90, 90))]
    assert len(observer_route) > len(worker_route)
    assert all(2 <= point.x <= 98 and 2 <= point.y <= 98 for point in observer_route)


def test_observer_waits_respects_human_and_retreats_when_damaged(bot, make_unit, populate):
    scout = ScoutController()
    bot.settings.scouting = True
    bot.settings.attack = True
    populate()
    assert scout._observer_tick(bot)["phase"] == "waiting_for_observer"

    observer = make_unit(U.OBSERVER, (20, 20))
    populate(observer)
    observer._proto.is_selected = True
    assert scout._observer_tick(bot)["phase"] == "human_owned"
    observer._proto.is_selected = False
    observer._proto.health = 10
    bot.game_info.start_locations = []
    bot.actions.clear()
    result = scout._observer_tick(bot)
    assert result["phase"] == "retreating_damaged"
    assert bot.actions[-1].target == bot.start_location


def test_observer_does_not_move_when_automation_or_attack_is_off(bot, make_unit, populate):
    observer = make_unit(U.OBSERVER, (20, 20))
    populate(observer)
    controller = ScoutController()
    bot.settings.scouting = True

    bot.settings.enabled = False
    assert controller._observer_tick(bot)["phase"] == "disabled"
    bot.settings.enabled = True
    bot.settings.attack = False
    assert controller._observer_tick(bot)["phase"] == "disabled"
    assert not bot.actions


def test_worker_scout_returns_home_and_releases_assignment(bot, make_unit, populate):
    probe = make_unit(U.PROBE, (2, 2))
    enemy = make_unit(U.MARINE, (3, 2), alliance=4)
    populate(probe, enemy)
    bot.enemy_units = Units([enemy], bot)
    bot.settings.enabled = bot.settings.attack = bot.settings.scouting = True
    bot.supply_workers = 12
    bot.game_info.start_locations = [Point2((100, 100))]
    scout = ScoutController()
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "returned"
    assert scout.worker_tag is None and bot.scout_tag is None


def test_worker_scout_waits_if_start_is_unknown_and_flees_if_threatened(bot, make_unit, populate):
    probe = make_unit(U.PROBE, (20, 20))
    populate(probe)
    bot.settings.enabled = bot.settings.attack = bot.settings.scouting = True
    scout = ScoutController()
    scout.worker_tag = bot.scout_tag = probe.tag
    bot.game_info.start_locations = []
    assert scout._worker_scout(bot, Units([], bot), {}) == "no_known_start"

    enemy = make_unit(U.MARINE, (21, 20), alliance=4)
    bot.enemy_units = Units([enemy], bot)
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "returning"
    assert bot.actions[-1].target == bot.start_location


def test_scout_reports_enemy_composition_peak_and_incoming_force(bot, make_unit, populate):
    nexus = make_unit(U.NEXUS, (0, 0))
    enemy_base = make_unit(U.NEXUS, (70, 70), alliance=4)
    stalkers = [make_unit(U.STALKER, (8 + i, 0), alliance=4) for i in range(8)]
    populate(nexus, enemy_base, *stalkers)
    bot.enemy_units = Units(stalkers, bot)
    bot.enemy_structures = Units([enemy_base], bot)
    bot.settings.enabled = bot.settings.attack = bot.settings.adaptive_composition = True
    bot.settings.scouting = False
    bot.settings.stalkers = 1
    bot.settings.voidrays = bot.settings.immortals = bot.settings.colossi = 0

    result = ScoutController().tick(bot)
    intel = result["intel"]
    assert intel["visible_enemy_force"]["composition"] == {"STALKER": 8}
    assert intel["peak_enemy_force"]["supply"] >= 8
    assert intel["incoming_force"]["unit_count"] == 8
    assert intel["enemy_bases"][0]["unit_type"] == "NEXUS"
    assert intel["enemy_seen"] and intel["force_intel_ready"]
    assert result["observer"]["phase"] == "disabled"
