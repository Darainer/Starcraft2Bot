import asyncio
from unittest.mock import AsyncMock

import pytest
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G
from sc2.position import Point2

from source.army_waves import ArmyWaves
from source.warp_reinforcement import WarpReinforcement


def economy(bot, make_unit, populate, *, robo=False):
    bot.control.command("!assist economy off")
    bot.settings.attack = bot.settings.production = True
    bot.enemy_race = Race.Terran
    bot.supply_workers = 20
    bot.supply_army = 12
    bot.state.game_loop = 5600
    bot.minerals, bot.vespene = 115, 54
    units = [
        make_unit(U.NEXUS, ideal_harvesters=16, assigned_harvesters=16),
        make_unit(U.PROBE),
        make_unit(U.PYLON),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.ROBOTICSFACILITY if robo else U.GATEWAY),
    ]
    if robo:
        bot.settings.scouting = False
    populate(*units)


def test_captured_115_minerals_54_gas_saves_for_stalker_instead_of_cheap_fallback(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    assert not bot.produce(0)
    assert not bot.actions and bot.minerals == 115
    assert bot._macro_reserve == 125
    bot.minerals = 125
    assert bot.produce(0)
    assert bot.actions[0].ability == A.GATEWAYTRAIN_STALKER


def test_first_stalker_reservation_precedes_discretionary_worker_spending(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.settings.workers = True
    bot.townhalls.first._proto.ideal_harvesters = 24
    asyncio.run(bot.macro())
    assert not bot.actions and bot.minerals == 115


def test_affordable_first_immortal_precedes_prism_and_third_nexus(bot, make_unit, populate):
    economy(bot, make_unit, populate, robo=True)
    populate(*bot.all_own_units, make_unit(U.NEXUS, (0, 30), ideal_harvesters=16))
    bot.settings.expansion = True
    bot.supply_workers = 40
    bot.minerals, bot.vespene = 400, 200
    asyncio.run(bot.macro())
    assert [a.ability for a in bot.actions] == [A.ROBOTICSFACILITYTRAIN_IMMORTAL]
    assert (bot.minerals, bot.vespene) == (125, 100)


def test_one_requested_observer_can_precede_first_immortal(bot, make_unit, populate):
    economy(bot, make_unit, populate, robo=True)
    bot.settings.scouting = True
    bot.minerals, bot.vespene = 400, 200
    assert bot.produce(0)
    assert bot.actions[0].ability == A.ROBOTICSFACILITYTRAIN_OBSERVER
    bot.actions.clear()
    bot._used.clear()
    bot.already_pending.side_effect = lambda kind: int(kind == U.OBSERVER)
    assert bot.produce(0)
    assert bot.actions[0].ability == A.ROBOTICSFACILITYTRAIN_IMMORTAL


@pytest.mark.parametrize(
    "blocked",
    ["selected", "released", "blocked", "unpowered", "busy", "tech", "target", "supply", "gas_off", "income"],
)
def test_unattainable_or_user_disabled_milestones_do_not_lock_budget(bot, make_unit, populate, blocked):
    economy(bot, make_unit, populate)
    gateway = bot.structures(U.GATEWAY).first
    if blocked == "selected":
        gateway._proto.is_selected = True
    elif blocked == "released":
        bot.control.released.add(gateway.tag)
    elif blocked == "blocked":
        bot._blocked_producers[gateway.tag] = bot.time + 5
    elif blocked == "unpowered":
        gateway._proto.is_powered = False
    elif blocked == "busy":
        from s2clientprotocol import raw_pb2

        gateway._proto.orders.append(raw_pb2.UnitOrder(ability_id=A.GATEWAYTRAIN_ZEALOT.value))
    elif blocked == "tech":
        bot.tech_requirement_progress.return_value = 0
    elif blocked == "target":
        bot.settings.stalkers = 0
    elif blocked == "supply":
        bot.supply_left = 0
    elif blocked == "gas_off":
        bot.vespene = 0
    else:
        bot.townhalls.first._proto.assigned_harvesters = 0
    assert bot.first_tech_combat() is None


def test_reservation_does_not_train_through_user_reserve_and_releases_after_first_exists(
    bot, make_unit, populate
):
    economy(bot, make_unit, populate)
    bot.settings.reserve_minerals = 100
    bot.minerals = 200
    assert not bot.produce(0) and not bot.actions
    bot.minerals = 225
    assert bot.produce(0) and bot.minerals == 100
    bot._used.clear()
    populate(*bot.all_own_units, make_unit(U.STALKER))
    assert bot.first_tech_combat() is None


def test_urgent_supply_and_low_worker_recovery_precede_reservation(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.settings.supply = True
    bot.supply_left = 0
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_PYLON
    bot.actions.clear()
    bot._used.clear()
    bot.settings.supply = False
    bot.settings.workers = True
    bot.supply_left, bot.supply_workers, bot.minerals = 20, 8, 115
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.NEXUSTRAIN_PROBE


def test_core_precedes_more_zealots_after_two_queued_without_contact(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.enemy_race = Race.Zerg
    bot.state.game_loop = 2240
    bot.settings.construction = True
    bot.minerals = 300
    populate(
        make_unit(U.NEXUS),
        make_unit(U.PROBE),
        make_unit(U.PYLON),
        make_unit(U.GATEWAY),
        make_unit(U.GATEWAY, (8, 8)),
    )
    bot.already_pending.side_effect = lambda kind: 2 if kind == U.ZEALOT else 0
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_CYBERNETICSCORE


def test_priority_core_uses_second_pylon_when_closest_power_is_crowded(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.enemy_race = Race.Zerg
    bot.state.game_loop = 2912  # Captured 130-second opening stall, before contact.
    bot.settings.construction = True
    bot.minerals, bot.vespene = 470, 136
    bot.game_info.player_start_location = Point2((114.5, 25.5))
    bot.game_info.map_center = Point2((72, 80))
    populate(
        make_unit(U.NEXUS, (114.5, 25.5)),
        make_unit(U.PROBE, (114, 25)),
        make_unit(U.PYLON, (114, 32)),
        make_unit(U.PYLON, (119, 17)),
        make_unit(U.GATEWAY, (110.5, 36.5)),
        make_unit(U.GATEWAY, (119.5, 32.5)),
        make_unit(U.ZEALOT, (112, 28)),
        make_unit(U.ZEALOT, (113, 28)),
    )

    # The exposed front power has no legal Core slot. A rear site is legal;
    # real placement/path/ownership/issue checks still run for that destination.
    async def placement(kind, near, **kwargs):
        if kind == U.CYBERNETICSCORE and near.x >= 123 and near.y <= 20:
            return near
        return None

    bot.find_placement = AsyncMock(side_effect=placement)
    asyncio.run(bot.macro())
    assert [action.ability for action in bot.actions] == [A.PROTOSSBUILD_CYBERNETICSCORE]
    assert bot.actions[0].target.x >= 123 and bot.actions[0].target.y <= 20
    assert (bot.minerals, bot.vespene) == (320, 136)


def test_early_contact_preserves_two_gateway_defender_production(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.enemy_race = Race.Zerg
    bot.state.game_loop = 2240
    bot.settings.construction = True
    bot.minerals = 300
    populate(
        make_unit(U.NEXUS),
        make_unit(U.PROBE),
        make_unit(U.PYLON),
        make_unit(U.GATEWAY),
        make_unit(U.GATEWAY, (8, 8)),
        make_unit(U.ZERGLING, (20, 0), alliance=4),
    )
    bot.already_pending.side_effect = lambda kind: 2 if kind == U.ZEALOT else 0
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.GATEWAYTRAIN_ZEALOT


def test_missing_gas_income_can_be_built_instead_of_locked_behind_counter(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.settings.gas = True
    bot.vespene = 0
    populate(*bot.all_own_units, make_unit(U.VESPENEGEYSER, (3, 0), alliance=3, vespene_contents=2250))
    asyncio.run(bot.macro())
    assert [a.ability for a in bot.actions] == [A.PROTOSSBUILD_ASSIMILATOR]


def test_user_disabled_gas_allows_legal_mineral_defender_fallback(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.vespene = 0
    assert not bot.settings.gas
    assert bot.produce(0)
    assert bot.actions[0].ability == A.GATEWAYTRAIN_ZEALOT


def test_first_counter_reservation_does_not_restart_after_observed_unit_is_lost(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    original = list(bot.all_own_units)
    populate(*original, make_unit(U.STALKER))
    assert bot.first_tech_combat() is None
    populate(*original)
    assert bot.first_tech_combat() is None
    assert bot.produce(0)
    assert bot.actions[0].ability == A.GATEWAYTRAIN_ZEALOT


def test_first_immortal_gas_is_protected_from_other_controllers_and_released_when_queued(
    bot, make_unit, populate
):
    economy(bot, make_unit, populate, robo=True)
    bot.minerals, bot.vespene = 1000, 100
    assert bot.first_tech_combat()[1] == U.IMMORTAL
    assert bot.affordable(U.IMMORTAL)
    assert not bot.affordable(U.STALKER)  # A Warpgate must not consume the saved counter gas.
    bot.already_pending.side_effect = lambda kind: int(kind == U.IMMORTAL)
    assert bot.first_tech_combat() is None
    assert bot.affordable(U.STALKER)


@pytest.mark.parametrize("release", ["selected", "released", "production_off", "paused", "target_zero"])
def test_first_tech_gas_reservation_releases_when_milestone_becomes_ineligible(
    bot, make_unit, populate, release
):
    economy(bot, make_unit, populate, robo=True)
    bot.minerals, bot.vespene = 500, 100
    assert bot.first_tech_combat()[1] == U.IMMORTAL
    assert not bot.affordable(U.STALKER)
    robo = bot.structures(U.ROBOTICSFACILITY).first
    if release == "selected":
        robo._proto.is_selected = True
    elif release == "released":
        bot.control.released.add(robo.tag)
    elif release == "production_off":
        bot.settings.production = False
    elif release == "paused":
        bot.settings.enabled = False
    else:
        bot.settings.immortals = 0
    assert bot.first_tech_combat() is None
    assert bot.affordable(U.STALKER)


def test_warpgate_cannot_spend_first_immortal_gas_but_resumes_after_training(bot, make_unit, populate):
    economy(bot, make_unit, populate, robo=True)
    populate(*bot.all_own_units, make_unit(U.WARPGATE))
    bot.settings.warp_reinforcement = True
    bot.settings.zealots = bot.settings.sentries = bot.settings.high_templar = 0
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    bot.get_available_abilities = AsyncMock(return_value=[A.WARPGATETRAIN_STALKER])
    bot.minerals, bot.vespene = 500, 100
    assert bot.first_tech_combat()[1] == U.IMMORTAL
    reinforcement = WarpReinforcement()
    asyncio.run(reinforcement.tick(bot, ArmyWaves()))
    assert not bot.actions
    assert bot.produce(0)
    assert (bot.minerals, bot.vespene) == (225, 0)
    bot.actions.clear()
    bot._used.clear()
    bot.already_pending.side_effect = lambda kind: int(kind == U.IMMORTAL)
    assert bot.first_tech_combat() is None
    assert not bot.affordable(U.STALKER)  # Training spent the gas; releasing it creates no income.
    bot.vespene = 50
    bot._macro_reserve = 0
    asyncio.run(reinforcement.tick(bot, ArmyWaves()))
    assert [action.ability for action in bot.actions] == [A.WARPGATETRAIN_STALKER]
    assert (bot.minerals, bot.vespene) == (100, 0)
