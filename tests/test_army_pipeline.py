import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G
from sc2.position import Point2
from sc2.units import Units

from source.army_waves import ArmyWaves
from source.scouting import ScoutController
from source.strategy_profiles import PROFILES
from source.warp_reinforcement import WarpReinforcement


def setup_wave(bot, make_unit, populate, count=12, position=(10, 10)):
    units = [make_unit(U.STALKER, position) for _ in range(count)]
    populate(*units)
    bot.scout_report = {"enemy_seen": True}
    return units


def test_no_single_unit_attack_even_when_global_supply_is_large(bot, make_unit, populate):
    setup_wave(bot, make_unit, populate, count=1)
    bot.supply_army = 100
    waves = ArmyWaves()
    orders, state = waves.plan(bot, bot.units, Point2((100, 100)), Point2((10, 10)), PROFILES["balanced"])
    assert state["phase"] == "assemble" and not state["members"]
    assert all(mode == "move" for mode, target in orders.values())


def test_launch_requires_scouting_composition_and_assembly(bot, make_unit, populate):
    setup_wave(bot, make_unit, populate)
    bot.scout_report = {}
    waves = ArmyWaves()
    args = (bot, bot.units, Point2((100, 100)), Point2((10, 10)), PROFILES["balanced"])
    assert waves.plan(*args)[1]["phase"] == "assemble"
    bot.scout_report = {"enemy_seen": True}
    orders, state = waves.plan(*args)
    assert state["phase"] == "advance" and len(state["members"]) == 12
    assert all(target.distance_to(Point2((10, 10))) <= 20 for mode, target in orders.values())
    assert all(target.distance_to(Point2((100, 100))) > 50 for mode, target in orders.values())


def test_remote_reinforcement_is_held_then_sent_as_a_batch(bot, make_unit, populate):
    original = setup_wave(bot, make_unit, populate)
    waves = ArmyWaves()
    objective, rally, policy = Point2((100, 100)), Point2((10, 10)), PROFILES["balanced"]
    waves.plan(bot, bot.units, objective, rally, policy)
    core = [make_unit(U.STALKER, (40, 40), tag=u.tag) for u in original]
    reserve = make_unit(U.STALKER, (10, 10))
    populate(*core, reserve)
    orders, state = waves.plan(bot, bot.units, objective, rally, policy)
    assert orders[reserve.tag][0] == "move"
    assert orders[reserve.tag][1].distance_to(rally) < 6
    assert reserve.tag not in state["members"]
    extras = [make_unit(U.STALKER, (10, 10)) for _ in range(5)]
    populate(*core, reserve, *extras)
    orders, state = waves.plan(bot, bot.units, objective, rally, policy)
    assert len(state["reinforcement_members"]) == 6
    assert orders[reserve.tag][1].distance_to(rally) > 6


def test_wave_waits_for_stragglers_and_resets_after_losses(bot, make_unit, populate):
    original = setup_wave(bot, make_unit, populate)
    waves = ArmyWaves()
    objective, rally, policy = Point2((100, 100)), Point2((10, 10)), PROFILES["balanced"]
    waves.plan(bot, bot.units, objective, rally, policy)
    split = [make_unit(U.STALKER, (50, 50) if i < 4 else (10, 10), tag=u.tag) for i, u in enumerate(original)]
    populate(*split)
    assert waves.plan(bot, bot.units, objective, rally, policy)[1]["phase"] == "regroup"
    populate(*split[:2])
    assert waves.plan(bot, bot.units, objective, rally, policy)[1]["phase"] == "assemble"


def test_air_profile_requires_air_core(bot, make_unit, populate):
    setup_wave(bot, make_unit, populate, count=16)
    bot.settings.profile = "air"
    waves = ArmyWaves()
    state = waves.plan(bot, bot.units, Point2((100, 100)), Point2((10, 10)), PROFILES["air"])[1]
    assert not state["composition_ready"] and state["phase"] == "assemble"


def test_scout_is_reserved_from_economy_but_retains_human_ownership(bot, make_unit, populate):
    probe = make_unit(U.PROBE, (2, 2))
    populate(probe)
    bot.enemy_structures = Units([], bot)
    bot.game_info.start_locations = [Point2((100, 100))]
    bot.supply_workers = 16
    bot.settings.attack = True
    scout = ScoutController()
    result = scout.tick(bot)
    assert result["phase"] == "scouting_enemy_start"
    assert bot.scout_tag == probe.tag and not bot.available(probe)
    bot._used.clear()
    probe._proto.is_selected = True
    assert scout.tick(bot)["phase"] == "human_owned"
    probe._proto.is_selected = False
    bot.actions.clear()
    bot.enemy_structures = Units([make_unit(U.GATEWAY, (100, 100), alliance=4)], bot)
    assert scout.tick(bot)["intel"]["enemy_seen"]


def test_scout_waits_for_workers_and_can_be_disabled(bot, populate):
    populate()
    bot.enemy_structures = Units([], bot)
    bot.supply_workers = 0
    bot.settings.attack = True
    scout = ScoutController()
    assert scout.tick(bot)["phase"] == "waiting_for_scout"
    bot.settings.scouting = False
    assert scout.tick(bot)["phase"] == "disabled"


def test_home_warp_in_accounts_resources_and_supply_exactly_once(bot, make_unit, populate):
    gate = make_unit(U.WARPGATE)
    populate(gate, make_unit(U.PYLON, (5, 5)))
    bot.settings.attack = True
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    bot.get_available_abilities = AsyncMock(return_value=[A.WARPGATETRAIN_STALKER])
    reinforcement = WarpReinforcement()
    asyncio.run(reinforcement.tick(bot, ArmyWaves()))
    assert bot.actions[0].ability == A.WARPGATETRAIN_STALKER
    assert bot.minerals == 875 and bot.vespene == 950 and bot.supply_left == 18
    assert bot._paid_action_issued and reinforcement.warpins == 1


def test_selected_warpgate_and_reserves_prevent_warp_in(bot, make_unit, populate):
    gate = make_unit(U.WARPGATE, is_selected=True)
    populate(gate, make_unit(U.PYLON, (5, 5)))
    bot.settings.attack = True
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    bot.get_available_abilities = AsyncMock(return_value=[A.WARPGATETRAIN_STALKER])
    reinforcement = WarpReinforcement()
    asyncio.run(reinforcement.tick(bot, ArmyWaves()))
    assert not bot.actions
    gate._proto.is_selected = False
    bot.settings.reserve_minerals = 950
    asyncio.run(reinforcement.tick(bot, ArmyWaves()))
    assert not bot.actions


def test_gateway_converts_only_after_research(bot, make_unit, populate):
    populate(make_unit(U.GATEWAY))
    bot.settings.attack = True
    bot.get_available_abilities = AsyncMock(return_value=[A.MORPH_WARPGATE])
    controller = WarpReinforcement()
    asyncio.run(controller.tick(bot, ArmyWaves()))
    assert not bot.actions
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    asyncio.run(controller.tick(bot, ArmyWaves()))
    assert bot.actions[0].ability == A.MORPH_WARPGATE


def test_prism_follows_and_phases_behind_assembled_wave(bot, make_unit, populate):
    prism = make_unit(U.WARPPRISM, (30, 30), is_flying=True)
    populate(prism)
    bot.settings.attack = True
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    bot.is_visible = lambda p: True
    bot.get_available_abilities = AsyncMock(return_value=[A.MORPH_WARPPRISMPHASINGMODE])
    waves = SimpleNamespace(members={1, 2}, center=Point2((35, 35)), phase="advance")
    controller = WarpReinforcement()
    asyncio.run(controller.tick(bot, waves))
    assert bot.actions[0].ability == A.MORPH_WARPPRISMPHASINGMODE


def test_threatened_phased_prism_unphases(bot, make_unit, populate):
    # The SDK unit's type only needs to be identifiable for the morph controller.
    prism = make_unit(U.WARPPRISM, (30, 30), is_flying=True)
    prism._proto.unit_type = U.WARPPRISMPHASING.value
    bot.game_data.units[U.WARPPRISMPHASING.value] = bot.game_data.units[U.WARPPRISM.value]
    populate(prism, make_unit(U.MARINE, (32, 30), alliance=4))
    bot.settings.attack = True
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    bot.get_available_abilities = AsyncMock(return_value=[A.MORPH_WARPPRISMTRANSPORTMODE])
    waves = SimpleNamespace(members={1}, center=Point2((35, 35)), phase="advance")
    controller = WarpReinforcement()
    asyncio.run(controller.tick(bot, waves))
    assert bot.actions[0].ability == A.MORPH_WARPPRISMTRANSPORTMODE
