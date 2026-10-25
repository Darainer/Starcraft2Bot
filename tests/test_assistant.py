import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from s2clientprotocol import raw_pb2
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G
from sc2.position import Point2

from source.economy_assistant import storm_target


def run(awaitable):
    return asyncio.run(awaitable)


def test_real_sdk_command_accounting(bot, make_unit):
    nexus = make_unit(U.NEXUS)
    assert bot.raw_affects_selection is False
    assert bot.issue(nexus.train(U.PROBE), paid=True, supply=True)
    assert (bot.minerals, bot.supply_left) == (950, 19)
    assert len(bot.actions) == 1
    assert not bot.issue(nexus.train(U.PROBE), paid=True, supply=True)
    assert bot.minerals == 950


@pytest.mark.parametrize("selected,released", [(True, False), (False, True)])
def test_no_orders_to_human_owned_units(bot, make_unit, selected, released):
    nexus = make_unit(U.NEXUS, is_selected=selected)
    if released:
        bot.control.released.add(nexus.tag)
    assert not bot.issue(nexus.train(U.PROBE), paid=True, supply=True)
    assert not bot.actions


def test_only_own_chat_can_pause(bot):
    bot.macro = AsyncMock()
    bot.powers = AsyncMock()
    bot.state.chat = [SimpleNamespace(player_id=2, message="!assist pause")]
    run(bot.on_step(0))
    assert bot.settings.enabled
    bot.macro.assert_awaited_once()
    bot.state.chat = [SimpleNamespace(player_id=1, message="!assist pause")]
    bot.macro.reset_mock()
    bot.powers.reset_mock()
    run(bot.on_step(1))
    assert not bot.settings.enabled
    bot.macro.assert_not_awaited()
    bot.powers.assert_not_awaited()


def test_worker_production_and_reserve(bot, make_unit, populate):
    populate(make_unit(U.NEXUS, ideal_harvesters=16))
    bot.control.command("!assist economy off")
    bot.settings.workers = True
    bot.minerals = 449
    bot.settings.reserve_minerals = 400
    run(bot.macro())
    assert not bot.actions
    bot.minerals = 450
    run(bot.macro())
    assert bot.actions[0].ability == A.NEXUSTRAIN_PROBE
    assert bot.minerals == 400


def test_build_pylon_not_army_orders(bot, make_unit, populate):
    nexus = make_unit(U.NEXUS)
    probe = make_unit(U.PROBE)
    army = make_unit(U.STALKER, (20, 20))
    populate(nexus, probe, army)
    bot.supply_left = 2
    run(bot.macro())
    assert len(bot.actions) == 1
    assert bot.actions[0].ability == A.PROTOSSBUILD_PYLON
    assert bot.actions[0].unit.tag == probe.tag
    assert bot.minerals == 900


def test_supply_saves_instead_of_training(bot, make_unit, populate):
    populate(make_unit(U.NEXUS, ideal_harvesters=16), make_unit(U.PROBE))
    bot.supply_left, bot.minerals = 2, 50
    run(bot.macro())
    assert not bot.actions


def test_build_refuses_threatened_location(bot, make_unit, populate):
    populate(make_unit(U.PROBE), make_unit(U.MARINE, (4, 4), alliance=4))
    assert not run(bot.build_structure(U.PYLON, Point2((3, 3))))
    assert not bot.actions


def test_build_refuses_missing_placement(bot, make_unit, populate):
    populate(make_unit(U.PROBE))
    bot.find_placement = AsyncMock(return_value=None)
    assert not run(bot.build_structure(U.PYLON, Point2((3, 3))))


def test_construct_gateway_prerequisite(bot, make_unit, populate):
    nexus = make_unit(U.NEXUS)
    populate(nexus, make_unit(U.PROBE), make_unit(U.PYLON, (5, 5)))
    assert run(bot.construct(nexus, 0))
    assert bot.actions[0].ability == A.PROTOSSBUILD_GATEWAY


def test_opening_defense_adds_gateway_before_robotics_tech(bot, make_unit, populate):
    nexus = make_unit(U.NEXUS)
    populate(
        nexus, make_unit(U.PROBE), make_unit(U.PYLON), make_unit(U.GATEWAY), make_unit(U.CYBERNETICSCORE)
    )
    bot.settings.attack = bot.settings.scouting = True
    bot.minerals = 300
    assert run(bot.construct(nexus, 0, army_only=True))
    assert bot.actions[0].ability == A.PROTOSSBUILD_GATEWAY


def test_small_emergency_army_does_not_spend_on_prism(bot, make_unit, populate):
    populate(make_unit(U.ROBOTICSFACILITY))
    bot.settings.attack = bot.settings.warp_reinforcement = True
    bot.settings.scouting = False
    bot.settings.immortals = bot.settings.colossi = 0
    bot.economic_emergency = True
    assert not bot.produce(0)
    bot.economic_emergency = False
    assert bot.produce(0)
    assert bot.actions[-1].ability == A.ROBOTICSFACILITYTRAIN_WARPPRISM


def test_production_honors_selected_building_and_supply(bot, make_unit, populate):
    gateway = make_unit(U.GATEWAY, is_selected=True)
    populate(gateway)
    assert not bot.produce(0)
    gateway._proto.is_selected = False
    # SDK selection is a property, not a cached view of the first query.
    bot.supply_left = 0
    assert not bot.produce(0)
    bot.supply_left = 2
    assert bot.produce(0)
    assert bot.actions[0].ability == A.GATEWAYTRAIN_STALKER


def test_expansion_issues_nexus_build(bot, make_unit, populate):
    populate(make_unit(U.NEXUS), make_unit(U.PROBE), make_unit(U.CYBERNETICSCORE))
    bot.control.command("!assist economy off")
    bot.settings.expansion = True
    bot.supply_workers = 16
    run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_NEXUS
    assert bot.actions[0].target == Point2((30, 0))


def test_allocation_preserves_scout_and_released_probe(bot, make_unit, populate):
    scout = make_unit(U.PROBE, orders=[raw_pb2.UnitOrder(ability_id=A.MOVE_MOVE.value)])
    released = make_unit(U.PROBE)
    idle = make_unit(U.PROBE)
    populate(
        make_unit(U.NEXUS, ideal_harvesters=16),
        scout,
        released,
        idle,
        make_unit(U.MINERALFIELD, (3, 0), alliance=3, mineral_contents=1000),
    )
    bot.control.released.add(released.tag)
    run(bot.allocate_workers())
    assert [action.unit.tag for action in bot.actions] == [idle.tag]


def test_disabled_powers_do_not_query_or_cast(bot, make_unit, populate):
    populate(make_unit(U.HIGHTEMPLAR, energy=200))
    run(bot.powers())
    assert not bot.actions
    bot.get_available_abilities.assert_not_awaited()


def test_storm_avoids_friendlies_range_and_overlap(bot, make_unit):
    caster = make_unit(U.HIGHTEMPLAR)
    enemies = [make_unit(U.MARINE, (6, n / 10), alliance=4) for n in range(3)]
    assert storm_target(caster, enemies, [caster], []) is not None
    friendly = make_unit(U.STALKER, (6, 0))
    assert storm_target(caster, enemies, [friendly], []) is None
    assert storm_target(caster, enemies, [], [Point2((6, 0))]) is None
    assert storm_target(make_unit(U.HIGHTEMPLAR, (30, 0)), enemies, [], []) is None
    assert storm_target(caster, enemies[:2], [], []) is None


def test_storm_toggle_and_cast_throttle(bot, make_unit, populate):
    caster = make_unit(U.HIGHTEMPLAR, energy=200)
    populate(caster, *(make_unit(U.MARINE, (6, n / 10), alliance=4) for n in range(3)))
    bot.settings.storm = True
    bot.get_available_abilities = AsyncMock(return_value=[[A.PSISTORM_PSISTORM]])
    run(bot.powers())
    assert bot.actions[0].ability == A.PSISTORM_PSISTORM
    bot._used.clear()
    run(bot.powers())
    assert len(bot.actions) == 1


def test_feedback_never_chases_or_double_targets(bot, make_unit, populate):
    casters = [make_unit(U.HIGHTEMPLAR, energy=200) for _ in range(2)]
    near = make_unit(U.GHOST, (8, 0), alliance=4, energy=100)
    far = make_unit(U.GHOST, (20, 0), alliance=4, energy=200)
    populate(*casters, near, far)
    bot.settings.feedback = True
    bot.get_available_abilities = AsyncMock(return_value=[[A.FEEDBACK_FEEDBACK]] * 2)
    run(bot.powers())
    assert len(bot.actions) == 1 and bot.actions[0].target.tag == near.tag


def test_guardian_shield(bot, make_unit, populate):
    sentry = make_unit(U.SENTRY, energy=100)
    populate(
        sentry,
        make_unit(U.STALKER, (1, 1)),
        make_unit(U.ZEALOT, (2, 0)),
        make_unit(U.MARINE, (6, 0), alliance=4),
    )
    bot.settings.guardian_shield = True
    bot.get_available_abilities = AsyncMock(return_value=[[A.GUARDIANSHIELD_GUARDIANSHIELD]])
    run(bot.powers())
    assert bot.actions[0].ability == A.GUARDIANSHIELD_GUARDIANSHIELD


def test_blink_retreats_only_to_visible_pathable_point(bot, make_unit, populate):
    stalker = make_unit(U.STALKER, (10, 0), health=40, shield=0)
    populate(make_unit(U.NEXUS), stalker, make_unit(U.MARINE, (12, 0), alliance=4))
    bot.settings.blink = True
    bot.get_available_abilities = AsyncMock(return_value=[[A.EFFECT_BLINK_STALKER]])
    bot.in_pathing_grid = lambda point: True
    bot.is_visible = lambda point: False
    run(bot.powers())
    assert not bot.actions
    bot.is_visible = lambda point: True
    run(bot.powers())
    assert bot.actions[0].ability == A.EFFECT_BLINK_STALKER
    assert bot.actions[0].target == Point2((4, 0))


def test_reply_is_not_reinterpreted_as_command(bot):
    bot.settings.enabled = False
    bot.state.chat = [SimpleNamespace(player_id=1, message="!assist help")]
    run(bot.on_step(0))
    replies = [call.args[0] for call in bot.chat_send.call_args_list]
    assert replies
    assert all(bot.control.command(reply) is None for reply in replies)


def test_upgrade_checks_available_ability_and_reserves(bot, make_unit, populate):
    populate(make_unit(U.FORGE))
    ability = bot.game_data.upgrades[G.PROTOSSGROUNDWEAPONSLEVEL1.value].research_ability.id
    bot.get_available_abilities = AsyncMock(return_value=[])
    assert not run(bot.upgrade(0))
    bot.get_available_abilities = AsyncMock(return_value=[ability])
    bot.settings.reserve_gas = 950
    assert not run(bot.upgrade(0))
    bot.settings.reserve_gas = 900
    assert run(bot.upgrade(0))
    assert bot.actions[0].ability == ability
    assert bot.vespene == 900


@pytest.mark.parametrize(
    "toggle,building,upgrade",
    [
        ("blink", U.TWILIGHTCOUNCIL, G.BLINKTECH),
        ("storm", U.TEMPLARARCHIVE, G.PSISTORMTECH),
    ],
)
def test_enabled_powers_can_research_prerequisites(bot, make_unit, populate, toggle, building, upgrade):
    populate(make_unit(building))
    setattr(bot.settings, toggle, True)
    ability = bot.game_data.upgrades[upgrade.value].research_ability.id
    bot.get_available_abilities = AsyncMock(return_value=[ability])
    assert run(bot.upgrade(0))
    assert bot.actions[0].ability == ability


def test_chrono_does_not_double_cast_and_skips_released_target(bot, make_unit, populate):
    target = make_unit(U.GATEWAY, orders=[raw_pb2.UnitOrder(ability_id=A.GATEWAYTRAIN_STALKER.value)])
    populate(make_unit(U.NEXUS, energy=100), make_unit(U.NEXUS, energy=100), target)
    bot.control.released.add(target.tag)
    bot.get_available_abilities = AsyncMock(return_value=[A.EFFECT_CHRONOBOOSTENERGYCOST])
    run(bot.chrono())
    assert not bot.actions
    bot.control.released.clear()
    run(bot.chrono())
    assert len(bot.actions) == 1
    assert bot.actions[0].ability == A.EFFECT_CHRONOBOOSTENERGYCOST
    assert bot.actions[0].target.tag == target.tag


def test_voidray_power_requires_attacking_armored_target(bot, make_unit, populate):
    bot.game_data.units[U.STALKER.value]._proto.attributes.append(2)  # Armored
    ray = make_unit(U.VOIDRAY, orders=[raw_pb2.UnitOrder(ability_id=A.ATTACK_ATTACK.value)])
    populate(ray, make_unit(U.STALKER, (3, 0), alliance=4))
    bot.settings.voidray_alignment = True
    bot.get_available_abilities = AsyncMock(return_value=[[A.EFFECT_VOIDRAYPRISMATICALIGNMENT]])
    run(bot.powers())
    assert bot.actions[0].ability == A.EFFECT_VOIDRAYPRISMATICALIGNMENT


def test_gas_build_and_worker_allocation(bot, make_unit, populate):
    nexus = make_unit(U.NEXUS, ideal_harvesters=16)
    probe = make_unit(U.PROBE)
    geyser = make_unit(U.VESPENEGEYSER, (3, 0), alliance=3, vespene_contents=1000)
    populate(nexus, probe, make_unit(U.CYBERNETICSCORE), geyser)
    bot.control.command("!assist economy off")
    bot.settings.gas = True
    run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_ASSIMILATOR
    assert bot.actions[0].target.tag == geyser.tag
    bot.actions.clear()
    bot._used.clear()
    gas = make_unit(U.ASSIMILATOR, (3, 0), ideal_harvesters=3, vespene_contents=1000)
    mineral = make_unit(U.MINERALFIELD, (3, 3), alliance=3, mineral_contents=1000)
    miners = [
        make_unit(
            U.PROBE,
            orders=[raw_pb2.UnitOrder(ability_id=A.HARVEST_GATHER.value, target_unit_tag=mineral.tag)],
        )
        for _ in range(16)
    ]
    populate(nexus, probe, gas, mineral, *miners)
    run(bot.allocate_workers())
    assert bot.actions[0].target.tag == gas.tag


def test_borrow_mineral_worker_to_fill_gas(bot, make_unit, populate):
    mineral = make_unit(U.MINERALFIELD, (3, 0), alliance=3, mineral_contents=1000)
    worker = make_unit(
        U.PROBE, orders=[raw_pb2.UnitOrder(ability_id=A.HARVEST_GATHER.value, target_unit_tag=mineral.tag)]
    )
    gas = make_unit(U.ASSIMILATOR, (4, 0), ideal_harvesters=3, vespene_contents=1000)
    miners = [
        make_unit(
            U.PROBE,
            orders=[raw_pb2.UnitOrder(ability_id=A.HARVEST_GATHER.value, target_unit_tag=mineral.tag)],
        )
        for _ in range(15)
    ]
    populate(make_unit(U.NEXUS, ideal_harvesters=16, assigned_harvesters=16), worker, gas, mineral, *miners)
    run(bot.allocate_workers())
    assert bot.actions[0].target.tag == gas.tag


@pytest.mark.parametrize("workers,gas_count,expected_moved", [(3, 1, 3), (10, 2, 4)])
def test_worker_loss_immediately_releases_gas_for_mineral_recovery(
    bot, make_unit, populate, workers, gas_count, expected_moved
):
    gases = [
        make_unit(U.ASSIMILATOR, (4, i), ideal_harvesters=3, assigned_harvesters=3, vespene_contents=1000)
        for i in range(gas_count)
    ]
    mineral = make_unit(U.MINERALFIELD, (3, 3), alliance=3, mineral_contents=1000)
    probes = [
        make_unit(
            U.PROBE,
            orders=[
                raw_pb2.UnitOrder(
                    ability_id=A.HARVEST_GATHER.value,
                    target_unit_tag=gases[i // 3].tag if i < gas_count * 3 else mineral.tag,
                )
            ],
        )
        for i in range(workers)
    ]
    populate(
        make_unit(U.NEXUS, ideal_harvesters=16, assigned_harvesters=workers - 3 * gas_count),
        mineral,
        *gases,
        *probes,
    )
    bot.minerals, bot.vespene = 15, 73
    run(bot.allocate_workers())
    assert len(bot.actions) == expected_moved
    assert all(action.target.tag == mineral.tag for action in bot.actions)


def test_expansion_saving_blocks_lower_priority_production(bot, make_unit, populate):
    populate(make_unit(U.NEXUS), make_unit(U.PROBE), make_unit(U.CYBERNETICSCORE), make_unit(U.GATEWAY))
    bot.control.command("!assist economy off")
    bot.settings.expansion = bot.settings.production = True
    bot.supply_workers, bot.minerals = 16, 300
    run(bot.macro())
    assert not bot.actions
    bot.settings.expansion = False
    run(bot.macro())
    assert bot.actions[0].ability == A.GATEWAYTRAIN_STALKER


def test_all_macro_toggles_off_leaves_all_units_alone(bot, make_unit, populate):
    populate(make_unit(U.NEXUS), make_unit(U.PROBE), make_unit(U.GATEWAY), make_unit(U.STALKER))
    bot.control.command("!assist economy off")
    run(bot.on_step(0))
    assert not bot.actions


def test_base_loss_rebuild_and_no_workers(bot, make_unit, populate):
    populate()
    run(bot.macro())
    assert not bot.actions
    populate(make_unit(U.PROBE))
    run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_NEXUS


def test_hud_and_action_error_processing(bot):
    bot.settings.enabled = False
    bot.settings.hud = True
    bot.state.action_errors = [SimpleNamespace(unit_tag=1, ability_id=1, result=1)]
    run(bot.on_start())
    run(bot.on_step(0))
    assert "PAUSED" in bot.client.debug_text_screen.call_args.args[0]
    bot.chat_send.assert_awaited()
