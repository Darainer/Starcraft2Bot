from dataclasses import replace

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.army_waves import ArmyWaves
from source.game_assessment import GameAssessment
from source.missions import MissionPlanner
from source.scouting import ScoutController
from source.strategy_director import StrategicDirector


def setup(bot, make_unit, populate):
    del bot.game_data.units[U.NEXUS.value]._proto.weapons[:]
    bot.settings.attack = bot.settings.scouting = True
    bot.settings.profile = "pressure"
    main = make_unit(U.NEXUS, (100, 100), alliance=4)
    expansion = make_unit(U.NEXUS, (60, 60), alliance=4, build_progress=0.5)
    army = [make_unit(U.STALKER, (90, 90)) for _ in range(16)]
    home = make_unit(U.NEXUS)
    populate(home, main, expansion, *army)
    bot._expansion_positions_list = [Point2((100, 100)), Point2((60, 60)), Point2((80, 30))]
    return home, main, expansion, army


def test_expansion_priority_and_identity_survive_loss_of_vision(bot, make_unit, populate):
    home, main, expansion, army = setup(bot, make_unit, populate)
    scout = ScoutController()
    scout.tick(bot)
    assessor = GameAssessment()
    state = assessor.observe(bot, bot.units(U.STALKER))
    target = next(t for t in state.targets if t.id == str(expansion.tag))
    assert target.expansion and target.visible
    assert not next(t for t in state.targets if t.id == str(main.tag)).expansion
    plan = StrategicDirector().decide(state)
    assert plan.missions[-1].target_id == str(expansion.tag)
    assert plan.reason == "Deny a scouted expansion"
    populate(home, *army)
    bot.is_visible = lambda point: False
    bot.state.game_loop += 224
    scout.tick(bot)
    state = assessor.observe(bot, bot.units(U.STALKER))
    remembered = next(t for t in state.targets if t.id == str(expansion.tag))
    assert remembered.expansion and not remembered.visible
    assert StrategicDirector().decide(state).missions[-1].target_id == target.id


def test_empty_expansion_is_rechecked_and_not_an_army_target(bot, make_unit, populate):
    home, _, _, army = setup(bot, make_unit, populate)
    observer = make_unit(U.OBSERVER, (20, 20))
    populate(home, observer, *army)
    scout = ScoutController()
    scout.tick(bot)
    state = GameAssessment().observe(bot, bot.units(U.STALKER))
    assert all(t.position != (60, 60) for t in state.targets)
    assert all(info["status"] == "empty" for info in bot.scout_report["expansion_sites"])
    bot.is_visible = lambda point: False
    bot.state.game_loop += 22 * 46
    bot._used.clear()
    result = scout._observer_tick(bot)
    assert result["phase"] == "scouting_expansion"
    assert tuple(result["target"]) in {(60, 60), (80, 30)}


def test_observer_checks_other_expansion_after_air_threat(bot, make_unit, populate):
    home, _, _, _ = setup(bot, make_unit, populate)
    observer = make_unit(U.OBSERVER, (20, 20))
    populate(home, observer)
    bot.is_visible = lambda point: False
    scout = ScoutController()
    first = scout._observer_tick(bot)
    assert first["phase"] == "scouting_expansion"
    first_target = tuple(first["target"])
    bot._used.clear()
    populate(home, observer, make_unit(U.MARINE, (22, 20), alliance=4))
    assert scout._observer_tick(bot)["phase"] == "retreating_from_air_threat"
    bot._used.clear()
    populate(home, observer)
    next_check = scout._observer_tick(bot)
    assert next_check["phase"] == "scouting_expansion"
    assert tuple(next_check["target"]) != first_target


def test_small_denial_squad_can_challenge_light_guard_but_not_fortification(bot, make_unit, populate):
    _, _, expansion, _ = setup(bot, make_unit, populate)
    state = GameAssessment().observe(bot, bot.units(U.STALKER))
    first = next(t for t in state.targets if t.id == str(expansion.tag))
    guarded = replace(
        first,
        id="third",
        position=(80, 30),
        value=60,
        defense=500,
        defender_supply=4,
        advantage=3,
    )
    state = replace(state, targets=(first, guarded))
    plan = StrategicDirector().decide(state)
    denial = next(m for m in plan.missions if m.role == "deny")
    assert denial.target_id == "third" and denial.supply_budget == 8
    assert plan.missions[-1].supply_budget == 24
    for unsafe in (
        replace(guarded, static_defense=True),
        replace(guarded, defender_supply=8),
        replace(guarded, visible=False),
        replace(guarded, expansion=False),
    ):
        plan = StrategicDirector().decide(replace(state, targets=(first, unsafe)))
        assert all(m.role != "deny" for m in plan.missions)


def test_denial_keeps_heavy_units_in_main_army(bot, make_unit, populate):
    home, main, expansion, army = setup(bot, make_unit, populate)
    second = make_unit(U.NEXUS, (80, 30), alliance=4)
    heavy = [make_unit(U.IMMORTAL, (80, 30)) for _ in range(4)]
    populate(home, main, expansion, second, *army, *heavy)
    state = GameAssessment().observe(bot, bot.units.of_type({U.STALKER, U.IMMORTAL}))
    plan = StrategicDirector().decide(state)
    missions = MissionPlanner().execute(
        bot, bot.units.of_type({U.STALKER, U.IMMORTAL}), plan, state, ArmyWaves()
    )
    raid = missions["missions"]["denial"]
    assert raid["members"]
    assert set(raid["members"]).isdisjoint(u.tag for u in heavy)
    assert {u.tag for u in heavy} <= set(missions["missions"]["main"]["members"])
