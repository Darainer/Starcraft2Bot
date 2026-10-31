import asyncio

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U

from source.army_waves import ArmyWaves
from source.warp_reinforcement import WarpReinforcement


def counter_state(bot, make_unit, populate, *, bay=False):
    bot.control.command("!assist economy off")
    bot.settings.attack = bot.settings.production = bot.settings.construction = True
    bot.settings.gas = True
    bot.settings.colossi = 3
    bot.settings.scouting = False
    bot.supply_workers, bot.supply_army = 34, 28
    bot.state.game_loop = 8960
    bot.minerals, bot.vespene = 250, 100
    units = [
        make_unit(U.NEXUS, ideal_harvesters=16, assigned_harvesters=16),
        make_unit(U.PROBE),
        make_unit(U.PYLON),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.GATEWAY),
        make_unit(U.ROBOTICSFACILITY, (12, 12)),
        make_unit(U.ASSIMILATOR, assigned_harvesters=3, vespene_contents=1000),
        make_unit(U.IMMORTAL),
        *[make_unit(U.STALKER, (20 + i, 20)) for i in range(12)],
    ]
    if bay:
        units.append(make_unit(U.ROBOTICSBAY, (20, 30)))
    populate(*units)


def test_requested_splash_prerequisite_budget_survives_active_pressure(bot, make_unit, populate):
    counter_state(bot, make_unit, populate)
    bot.economic_emergency = True
    bot.settings.workers = True
    asyncio.run(bot.macro())
    assert not bot.actions and not bot.affordable(U.STALKER)
    bot.vespene = 150
    asyncio.run(bot.macro())
    assert [a.ability for a in bot.actions] == [A.PROTOSSBUILD_ROBOTICSBAY]
    assert (bot.minerals, bot.vespene) == (100, 0)


def test_defensive_construction_allows_requested_bay_but_not_unrequested_tech(bot, make_unit, populate):
    counter_state(bot, make_unit, populate)
    bot.minerals, bot.vespene = 150, 150
    assert asyncio.run(bot.construct(bot.townhalls.first, 0, army_only=True))
    assert bot.actions[0].ability == A.PROTOSSBUILD_ROBOTICSBAY


def test_first_colossus_reserves_real_price_before_more_cheap_units(bot, make_unit, populate):
    counter_state(bot, make_unit, populate, bay=True)
    bot.minerals, bot.vespene = 350, 150
    assert not bot.produce(0)
    assert not bot.actions and bot._macro_reserve == 300
    assert not bot.affordable(U.STALKER)
    bot.vespene = 200
    assert bot.produce(0)
    assert [a.ability for a in bot.actions] == [A.ROBOTICSFACILITYTRAIN_COLOSSUS]
    assert (bot.minerals, bot.vespene, bot.supply_left) == (50, 0, 14)


def test_unpowered_or_human_owned_robo_cannot_lock_splash_budget(bot, make_unit, populate):
    counter_state(bot, make_unit, populate, bay=True)
    bot.structures(U.ROBOTICSFACILITY).first._proto.is_selected = True
    assert bot.first_tech_combat() is None
    assert bot.affordable(U.STALKER)


def test_first_colossus_fund_is_honored_by_warp_controller(bot, make_unit, populate):
    counter_state(bot, make_unit, populate, bay=True)
    populate(*bot.all_own_units, make_unit(U.WARPGATE))
    bot.minerals, bot.vespene = 1000, 150
    bot.settings.warp_reinforcement = True
    bot.get_available_abilities.return_value = [[A.WARPGATETRAIN_STALKER]]
    assert bot.first_tech_combat()[1] == U.COLOSSUS
    asyncio.run(WarpReinforcement().tick(bot, ArmyWaves()))
    assert not bot.actions and bot.vespene == 150


def test_small_emergency_force_does_not_mortgage_defenders_for_bay(bot, make_unit, populate):
    counter_state(bot, make_unit, populate)
    bot.economic_emergency = True
    assert not asyncio.run(bot.fund_first_robotics(bot.townhalls.first, 12, U.ROBOTICSBAY))
    assert bot.affordable(U.STALKER)
    bot.settings.colossi = 0
    bot.economic_emergency = False
    assert not asyncio.run(bot.fund_first_robotics(bot.townhalls.first, 28, U.ROBOTICSBAY))
