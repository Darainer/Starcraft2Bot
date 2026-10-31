import pytest
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source.scouting import ScoutController
from source.scouting_costs import ScoutCosts


def prepare(bot, make_unit, populate):
    probe = make_unit(U.PROBE, (10, 10))
    populate(make_unit(U.NEXUS), probe)
    bot.settings.enabled = bot.settings.attack = bot.settings.scouting = True
    bot.state.game_loop = 3360
    bot.supply_workers = 19
    bot.game_info.start_locations = [Point2((100, 100))]
    bot._expansion_positions_list = [Point2((80, 80))]
    scout = ScoutController(revisit=True)
    scout.opening_complete = True
    return scout, probe


def test_revisit_uses_one_worker_only_visits_natural_and_stops_at_deadline(bot, make_unit, populate):
    scout, probe = prepare(bot, make_unit, populate)
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "revisiting_enemy_natural"
    assert bot.actions[-1].target == Point2((80, 80))
    assert scout.revisit_until == 210
    bot._used.clear()
    bot.state.game_loop = int(211 * 22.4)
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "returning"
    assert bot.actions[-1].target == bot.start_location
    probe._proto.pos.x = probe._proto.pos.y = 0
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "returned"
    bot._used.clear()
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "opening_complete"


@pytest.mark.parametrize(
    "guard",
    [
        "disabled",
        "paused",
        "selected",
        "released",
        "emergency",
        "observer",
        "fresh",
        "home_threat",
        "late",
        "workers",
        "manual",
        "script",
        "injured",
    ],
)
def test_revisit_guards_ownership_defense_economy_and_duplicate_inspection(bot, make_unit, populate, guard):
    scout, probe = prepare(bot, make_unit, populate)
    report = {}
    if guard == "disabled":
        scout.revisit = False
    elif guard == "paused":
        bot.settings.enabled = False
    elif guard == "selected":
        probe._proto.is_selected = True
    elif guard == "released":
        bot.control.released.add(probe.tag)
    elif guard == "emergency":
        bot.economic_emergency = True
    elif guard == "observer":
        populate(probe, make_unit(U.OBSERVER))
    elif guard == "fresh":
        report["expansion_sites"] = [{"position": [80, 80], "last_checked": 140}]
    elif guard == "home_threat":
        bot.enemy_units = Units([make_unit(U.MARINE, (20, 20), alliance=4)], bot)
    elif guard == "late":
        bot.state.game_loop = 224 * 22.4
    elif guard == "workers":
        bot.supply_workers = 15
    elif guard == "manual":
        bot.settings.strategy = "defend"
    elif guard == "injured":
        probe._proto.health = 5
        probe._proto.shield = 0
    else:
        bot.settings.strategy_script = "custom.py"
    scout._worker_scout(bot, bot.enemy_units, report)
    assert not bot.actions and not scout.revisit_started


def test_revisit_returns_on_contact_and_hands_off_to_observer(bot, make_unit, populate):
    scout, probe = prepare(bot, make_unit, populate)
    scout._worker_scout(bot, bot.enemy_units, {})
    bot._used.clear()
    populate(make_unit(U.NEXUS), probe, make_unit(U.OBSERVER))
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "returning"
    probe._proto.is_selected = True
    bot.actions.clear()
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "human_owned"
    assert not bot.actions


def test_revisit_passes_workers_but_withdraws_on_first_damage_or_army_contact(bot, make_unit, populate):
    scout, probe = prepare(bot, make_unit, populate)
    probe._proto.pos.x = 40
    worker = make_unit(U.PROBE, (47, 10), alliance=4)
    enemies = Units([worker], bot)
    assert worker.can_attack_ground
    assert scout._worker_scout(bot, enemies, {}) == "revisiting_enemy_natural"
    bot._used.clear()
    worker._proto.pos.x = 42
    assert scout._worker_scout(bot, enemies, {}) == "revisiting_enemy_natural"
    bot._used.clear()
    probe._proto.shield -= 1
    assert scout._worker_scout(bot, enemies, {}) == "returning"
    scout.returning = False
    army = Units([make_unit(U.MARINE, (47, 10), alliance=4)], bot)
    assert scout._worker_scout(bot, army, {}) == "returning"


def test_revisit_avoids_worker_swarm_without_waiting_for_damage(bot, make_unit, populate):
    scout, probe = prepare(bot, make_unit, populate)
    probe._proto.pos.x = 40
    workers = Units([make_unit(U.PROBE, (47, 10), alliance=4), make_unit(U.PROBE, (46, 10), alliance=4)], bot)
    assert scout._worker_scout(bot, workers, {}) == "returning"


def test_revisit_detects_first_hit_after_shield_regeneration(bot, make_unit, populate):
    scout, probe = prepare(bot, make_unit, populate)
    probe._proto.health = probe._proto.health_max = probe._proto.shield_max = 20
    probe._proto.shield = 18
    scout._worker_scout(bot, bot.enemy_units, {})
    bot._used.clear()
    probe._proto.shield = 20
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "revisiting_enemy_natural"
    probe._proto.shield = 19
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "returning"


def test_revisit_requires_actual_visibility_to_finish_the_inspection(bot, make_unit, populate):
    scout, probe = prepare(bot, make_unit, populate)
    probe._proto.pos.x, probe._proto.pos.y = 78, 80
    bot.is_visible = lambda point: False
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "revisiting_enemy_natural"
    bot._used.clear()
    bot.is_visible = lambda point: True
    assert scout._worker_scout(bot, bot.enemy_units, {}) == "returning"


def test_original_opening_scout_keeps_its_worker_threat_margin(bot, make_unit, populate):
    scout, probe = prepare(bot, make_unit, populate)
    scout.opening_complete = False
    worker = make_unit(U.PROBE, (17, 10), alliance=4)
    assert scout._worker_scout(bot, Units([worker], bot), {}) == "returning"
    assert not scout.revisit_active


def test_scout_costs_confirm_death_and_do_not_treat_absence_as_loss(bot, make_unit, populate):
    _, probe = prepare(bot, make_unit, populate)
    costs = ScoutCosts()
    costs.register(bot, probe, "worker")
    costs.observe(bot, probe.tag)
    bot.state.game_loop += 224
    assert costs.observe(bot, probe.tag)["worker_opportunity_seconds"] == 10
    populate()
    assert costs.observe(bot, probe.tag)["confirmed_lost_minerals"] == 0
    bot.state.dead_units = {probe.tag}
    assert costs.observe(bot, probe.tag)["confirmed_lost_minerals"] == 50
    assert costs.observe(bot, probe.tag)["confirmed_lost_minerals"] == 50


def test_paused_or_human_owned_scout_cost_is_not_charged_to_automation(bot, make_unit, populate):
    _, probe = prepare(bot, make_unit, populate)
    costs = ScoutCosts()
    costs.register(bot, probe, "worker")
    probe._proto.is_selected = True
    assert costs.observe(bot, probe.tag)["units"][0]["status"] == "human_owned"
    probe._proto.is_selected = False
    costs.register(bot, probe, "worker")
    bot.settings.enabled = False
    assert costs.observe(bot, probe.tag)["units"][0]["status"] == "automation_disabled"
