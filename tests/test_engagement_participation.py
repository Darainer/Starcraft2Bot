from sc2.ids.unit_typeid import UnitTypeId as U

from source.game_assessment import GameAssessment
from source.strategy_director import StrategicDirector


def test_eight_supply_flank_does_not_recall_large_healthy_main(bot, make_unit, populate):
    flank = [make_unit(U.ZEALOT, (70, 70), health=10, shield=0) for _ in range(4)]
    main = [make_unit(U.STALKER) for _ in range(62)]
    enemy = make_unit(U.MARINE, (71, 70), alliance=4, health=10000, health_max=10000)
    populate(make_unit(U.NEXUS), *flank, *main, enemy)
    bot.settings.profile = "pressure"
    state = GameAssessment().observe(bot, bot.units)
    assert state.army_supply == 132
    assert state.local_advantage == 10
    assert StrategicDirector().decide(state).objective != "recover"


def test_substantial_participating_force_still_triggers_recovery(bot, make_unit, populate):
    front = [make_unit(U.STALKER, (70, 70)) for _ in range(20)]
    main = [make_unit(U.STALKER) for _ in range(46)]
    enemy = make_unit(U.MARINE, (71, 70), alliance=4, health=10000, health_max=10000)
    populate(make_unit(U.NEXUS), *front, *main, enemy)
    bot.settings.profile = "pressure"
    state = GameAssessment().observe(bot, bot.units)
    assert state.local_advantage < 0.85
    assert StrategicDirector().decide(state).objective == "recover"


def test_small_whole_army_is_still_assessed(bot, make_unit, populate):
    populate(
        make_unit(U.NEXUS),
        make_unit(U.STALKER, (70, 70)),
        make_unit(U.STALKER, (70, 70)),
        make_unit(U.MARINE, (71, 70), alliance=4, health=10000, health_max=10000),
    )
    state = GameAssessment().observe(bot, bot.units)
    assert state.army_supply == 4
    assert state.local_advantage < 0.85
    assert StrategicDirector().decide(state).objective == "recover"
