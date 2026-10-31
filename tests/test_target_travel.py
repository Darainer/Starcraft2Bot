"""Distant-army search costs and emergency overrides use actual observations."""

import pytest
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source.game_assessment import GameAssessment
from source.strategy_director import StrategicDirector


def setup(bot, make_unit, populate):
    soldiers = [make_unit(U.STALKER, (99 + i * 0.2, 100)) for i in range(12)]
    populate(make_unit(U.NEXUS), *soldiers)
    bot.settings.profile = "pressure"
    bot.state.game_loop = 22400
    bot.game_info.start_locations = [Point2((200, 200))]
    bot._expansion_positions_list = [Point2((25, 0)), Point2((100, 90))]
    bot.is_visible = lambda point: False
    return Units(soldiers, bot)


def test_distant_army_searches_near_its_position_instead_of_near_home(bot, make_unit, populate):
    army = setup(bot, make_unit, populate)
    state = GameAssessment().observe(bot, army)
    targets = {target.id: target for target in state.targets}
    assert targets["site:2"].travel == pytest.approx(army.center.distance_to(Point2((100, 90))))
    assert targets["site:2"].travel < targets["site:1"].travel
    assert StrategicDirector().decide(state).missions[-1].target_id == "site:2"


def test_remembered_bases_use_army_travel_and_do_not_override_an_emergency(bot, make_unit, populate):
    army = setup(bot, make_unit, populate)
    bot.scout_report = {
        "known_enemy_bases": [
            {"tag": "near_army", "position": [100, 110], "seen_seconds": 990, "expansion": True},
            {"tag": "near_home", "position": [20, 0], "seen_seconds": 990, "expansion": True},
        ]
    }
    assessment = GameAssessment()
    state = assessment.observe(bot, army)
    targets = {target.id: target for target in state.targets}
    assert targets["near_army"].travel < targets["near_home"].travel
    director = StrategicDirector()
    assert director.decide(state).missions[-1].target_id == "near_army"
    bot.scout_report["rush_warning"] = {"expires_at": 1100}
    plan = director.decide(assessment.observe(bot, army))
    assert plan.objective == "stabilize" and not plan.expand


def test_no_fighting_army_uses_front_and_fresh_empty_sites_stay_suppressed(bot, make_unit, populate):
    setup(bot, make_unit, populate)
    bot.scout_report = {
        "expansion_sites": [{"position": [100, 90], "status": "empty", "last_checked": 999}],
        "known_enemy_bases": [
            {"tag": "remembered", "position": [120, 100], "seen_seconds": 990, "expansion": True}
        ],
    }
    state = GameAssessment().observe(bot, Units([], bot))
    targets = {target.id: target for target in state.targets}
    assert "site:2" not in targets
    assert targets["site:1"].travel == pytest.approx(25)
    assert targets["remembered"].travel == pytest.approx(Point2((0, 0)).distance_to(Point2((120, 100))))
    assert StrategicDirector().decide(state).objective == "develop"
