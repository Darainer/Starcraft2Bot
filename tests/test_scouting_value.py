from dataclasses import replace

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source.experimental_scouting import BeliefScoutController as ScoutController
from source.opponent_beliefs import OpponentBeliefs
from source.scouting_value import ScoutOption, choose_scout


def test_cost_aware_information_choice_rejects_redundant_or_expensive_scouting():
    safe = ScoutOption("technology", (100, 100), 1, 1, 20, 25, 75)
    dangerous = replace(safe, exposure=1, recent_loss_multiplier=2)
    redundant = replace(safe, useful_visibility=0)
    assert choose_scout([dangerous, safe]) is safe
    assert choose_scout([dangerous, redundant]) is None
    assert replace(safe, worker_seconds=90).utility() < safe.utility()


def test_interrupted_worker_return_is_not_a_completed_inspection(bot, make_unit, populate):
    probe = make_unit(U.PROBE, (2, 2))
    enemy = make_unit(U.MARINE, (3, 2), alliance=4)
    populate(probe, enemy)
    bot.settings.enabled = bot.settings.attack = bot.settings.scouting = True
    bot.supply_workers = 12
    bot.game_info.start_locations = [Point2((100, 100))]
    scout = ScoutController()
    assert scout._worker_scout(bot, Units([enemy], bot), {}) == "returned"
    assert not scout.opening_complete and scout.worker_route_index == 0
    assert scout.worker_attempts == 1


def test_missing_worker_reserves_loss_budget_without_fabricating_death(bot, make_unit, populate):
    probe = make_unit(U.PROBE, (20, 20))
    populate(probe)
    bot.settings.enabled = bot.settings.attack = bot.settings.scouting = True
    bot.supply_workers = 12
    bot.game_info.start_locations = [Point2((100, 100))]
    scout = ScoutController()
    report = {}
    scout._worker_scout(bot, Units([], bot), report)
    assert scout.worker_tag == probe.tag
    populate()
    bot.state.game_loop = 2240
    assert scout._worker_scout(bot, Units([], bot), report) == "worker_scout_budget_exhausted"
    assert report["scouting_costs"]["confirmed_lost_minerals"] == 0
    assert scout.scout_costs[probe.tag]["status"] == "missing"
    populate(probe)
    scout._account_scouts(bot, report)
    assert scout.scout_costs[probe.tag]["status"] == "present"
    bot.state.dead_units = {probe.tag}
    scout._account_scouts(bot, report)
    assert report["scouting_costs"]["confirmed_lost_minerals"] == 50
    scout._account_scouts(bot, report)
    assert report["scouting_costs"]["confirmed_lost_minerals"] == 50


def test_worker_opportunity_budget_forces_return_and_prevents_repeat_cost(bot, make_unit, populate):
    probe = make_unit(U.PROBE, (20, 20))
    populate(probe)
    bot.settings.enabled = bot.settings.attack = bot.settings.scouting = True
    bot.supply_workers = 12
    bot.game_info.start_locations = [Point2((100, 100))]
    scout = ScoutController()
    scout._worker_scout(bot, Units([], bot), {})
    bot._used.clear()
    bot.state.game_loop = 2240
    report = {}
    assert scout._worker_scout(bot, Units([], bot), report) == "returning"
    assert report["scouting_costs"]["worker_opportunity_seconds"] == 90
    assert not scout.opening_complete


def test_returned_worker_later_lost_while_mining_is_not_charged_as_scout_loss(bot, make_unit, populate):
    probe = make_unit(U.PROBE, (2, 2))
    enemy = make_unit(U.MARINE, (3, 2), alliance=4)
    populate(probe, enemy)
    bot.settings.enabled = bot.settings.attack = bot.settings.scouting = True
    bot.supply_workers = 12
    scout = ScoutController()
    assert scout._worker_scout(bot, Units([enemy], bot), {}) == "returned"
    populate()
    bot.state.dead_units = {probe.tag}
    report = {}
    scout._account_scouts(bot, report)
    assert report["scouting_costs"]["confirmed_lost_minerals"] == 0


def test_observer_questions_avoid_visible_answers_and_armed_destinations(bot, make_unit, populate):
    observer = make_unit(U.OBSERVER, (20, 20))
    marines = [make_unit(U.MARINE, (99 + i, 100), alliance=4) for i in range(2)]
    populate(observer, *marines)
    bot.enemy_units = Units(marines, bot)
    bot.settings.enabled = bot.settings.attack = bot.settings.scouting = True
    bot.game_info.start_locations = [Point2((100, 100))]
    bot.scout_report = {"opponent_beliefs": OpponentBeliefs(time=0).to_dict()}
    bot.is_visible = lambda point: point.distance_to(Point2((100, 100))) < 1
    scout = ScoutController()
    assert scout._question_target(bot, observer, []) is None
    bot.is_visible = lambda point: False
    scout._record_scout(bot, observer, "observer")
    # A recent lost scout increases the cost of repeating the same exposure.
    scout.scout_costs[-1] = {"status": "confirmed_dead"}
    assert scout._question_target(bot, observer, []) is None
    bot.enemy_units = Units([], bot)
    choice = scout._question_target(bot, observer, [])
    assert choice is not None and choice[1] in {"technology", "commitment"}
    scout.observer_loss_until = 90
    assert scout._question_target(bot, observer, []) is None
