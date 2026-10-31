import asyncio
from unittest.mock import AsyncMock

import pytest
from s2clientprotocol import raw_pb2
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source import economy_assistant as candidate
from source import game_assessment as assessment_candidate
from source import strategic_plan as contract
from source import strategy_policies as policies


def opening(bot, make_unit, populate, *, completed=False, busy=False):
    bot.enemy_race = Race.Zerg
    bot.__class__ = candidate.EconomyAssistant
    orders = [raw_pb2.UnitOrder(ability_id=A.GATEWAYTRAIN_ZEALOT.value, progress=0.3)] if busy else []
    units = [make_unit(U.NEXUS), make_unit(U.PYLON), make_unit(U.GATEWAY, orders=orders), make_unit(U.PROBE)]
    if completed:
        units.append(make_unit(U.ZEALOT))
    populate(*units)
    bot.state.game_loop = 2240
    bot.settings.attack = True
    bot.settings.workers = bot.settings.gas = bot.settings.supply = False
    bot.settings.construction = bot.settings.upgrades = False
    bot.minerals, bot.vespene = 400, 0
    bot.supply_workers = 19
    return bot


def test_first_gateway_defender_precedes_core_and_natural_saving(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    bot.settings.construction = True
    asyncio.run(candidate.EconomyAssistant.macro(bot))
    assert [action.ability for action in bot.actions] == [A.GATEWAYTRAIN_ZEALOT]


def test_queued_army_supply_does_not_release_completed_defender_gate(bot, make_unit, populate):
    opening(bot, make_unit, populate, busy=True)
    bot.supply_army = 2
    bot.already_pending.side_effect = lambda kind: int(kind == U.ZEALOT)
    asyncio.run(candidate.EconomyAssistant.macro(bot))
    assert not bot.actions


def test_completed_defender_releases_natural_gate(bot, make_unit, populate):
    opening(bot, make_unit, populate, completed=True, busy=True)
    asyncio.run(candidate.EconomyAssistant.macro(bot))
    assert not bot.actions  # One Zealot is below the completed six-supply force.


@pytest.mark.parametrize("setting", ["attack", "production"])
def test_manual_control_settings_do_not_force_an_opening_defender(bot, make_unit, populate, setting):
    opening(bot, make_unit, populate, busy=True)
    setattr(bot.settings, setting, False)
    asyncio.run(candidate.EconomyAssistant.macro(bot))
    assert [action.ability for action in bot.actions] == [A.PROTOSSBUILD_NEXUS]


def test_selected_gateway_and_reserves_remain_protected(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    bot.structures(U.GATEWAY).first._proto.is_selected = True
    bot.settings.reserve_minerals = 400
    asyncio.run(candidate.EconomyAssistant.macro(bot))
    assert not bot.actions


def test_repeated_defenders_then_completed_force_releases_natural(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.GATEWAYTRAIN_ZEALOT
    bot._used.clear()
    populate(
        make_unit(U.NEXUS), make_unit(U.GATEWAY), make_unit(U.PYLON), make_unit(U.PROBE), make_unit(U.ZEALOT)
    )
    bot.minerals, bot.vespene = 400, 0
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.GATEWAYTRAIN_ZEALOT
    bot._used.clear()
    populate(
        make_unit(U.NEXUS),
        make_unit(U.GATEWAY),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.PYLON),
        make_unit(U.PROBE),
        make_unit(U.ZEALOT),
        make_unit(U.ZEALOT),
    )
    bot.minerals, bot.vespene = 400, 100
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.GATEWAYTRAIN_STALKER
    bot._used.clear()
    populate(
        make_unit(U.NEXUS),
        make_unit(U.GATEWAY),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.PYLON),
        make_unit(U.PROBE),
        make_unit(U.ZEALOT),
        make_unit(U.ZEALOT),
        make_unit(U.STALKER),
    )
    bot.minerals, bot.vespene = 400, 100
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.PROTOSSBUILD_NEXUS


def test_stalker_budget_is_not_spent_on_cheaper_support(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    populate(make_unit(U.NEXUS), make_unit(U.GATEWAY), make_unit(U.CYBERNETICSCORE), make_unit(U.PROBE))
    bot.minerals, bot.vespene = 100, 100
    asyncio.run(bot.macro())
    assert not bot.actions
    assert bot._opening_reserve == 125


def test_workers_continue_while_gateway_is_busy(bot, make_unit, populate):
    opening(bot, make_unit, populate, busy=True)
    bot.settings.workers = True
    bot.supply_workers = 12
    bot.townhalls.first._proto.ideal_harvesters = 16
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.NEXUSTRAIN_PROBE


def test_protected_rear_power_can_be_prepared_before_battery_tech(bot, make_unit, populate, monkeypatch):
    opening(bot, make_unit, populate, busy=True)
    bot.settings.supply = True
    bot._opening_reserve = 0
    bot.state.psionic_matrix.covers = lambda point: False
    monkeypatch.setattr(candidate, "find_spaced_placement", AsyncMock(return_value=Point2((-8, 0))))
    assert asyncio.run(bot.opening_battery(bot.townhalls.first, Units([], bot)))
    assert bot.actions[-1].ability == A.PROTOSSBUILD_PYLON
    assert bot.actions[-1].target == Point2((-8, 0))


def test_small_early_contact_reenters_defense_and_defers_tech(bot, make_unit, populate):
    opening(bot, make_unit, populate, busy=True)
    gateway = bot.structures(U.GATEWAY).first
    populate(
        make_unit(U.NEXUS),
        gateway,
        make_unit(U.PYLON),
        make_unit(U.PROBE),
        *[make_unit(U.ZEALOT) for _ in range(3)],
    )
    bot.enemy_units = Units([make_unit(U.MARINE, (25, 0), alliance=4)], bot)
    bot.upgrade = AsyncMock(return_value=True)
    bot.settings.upgrades = True
    asyncio.run(bot.macro())
    assert bot.opening_phase == "defend" and not bot.actions
    bot.upgrade.assert_not_awaited()


def test_opening_still_builds_gas_for_a_legal_stalker(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    populate(
        make_unit(U.NEXUS),
        make_unit(U.GATEWAY),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.PROBE),
        make_unit(U.VESPENEGEYSER, (6, 0), vespene_contents=2250),
    )
    bot.settings.gas = True
    bot.minerals, bot.vespene = 100, 0
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.PROTOSSBUILD_ASSIMILATOR


def test_front_pylon_can_power_a_safe_battery_and_unsafe_or_unpowered_sites_are_rejected(
    bot, make_unit, populate, monkeypatch
):
    opening(bot, make_unit, populate)
    populate(make_unit(U.NEXUS), make_unit(U.CYBERNETICSCORE), make_unit(U.PYLON, (9, 0)), make_unit(U.PROBE))
    bot._opening_reserve = 0
    bot.vespene = 100  # The generic synthetic building table assigns 100 gas.
    bot.townhalls.first._proto.radius = 2.75
    point = Point2((6.5, -4.5))
    monkeypatch.setattr(candidate, "find_spaced_placement", AsyncMock(return_value=point))
    bot.state.psionic_matrix.covers = lambda p: p == point
    assert asyncio.run(bot.opening_battery(bot.townhalls.first, Units([], bot)))
    assert bot.actions[-1].ability == A.BUILD_SHIELDBATTERY
    bot.actions.clear()
    bot._used.clear()
    bot.state.psionic_matrix.covers = lambda p: False
    assert not asyncio.run(bot.opening_battery(bot.townhalls.first, Units([], bot)))
    assert not bot.actions


def test_second_gateway_is_reserved_before_core_or_workers_while_first_builds(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    populate(
        make_unit(U.NEXUS),
        make_unit(U.PYLON),
        make_unit(U.GATEWAY, (8, 8), build_progress=0.3),
        make_unit(U.PROBE),
    )
    bot.settings.construction = bot.settings.workers = True
    bot.townhalls.first._proto.ideal_harvesters = 16
    bot.already_pending.side_effect = lambda kind: int(kind == U.GATEWAY)
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.PROTOSSBUILD_GATEWAY
    bot._used.clear()
    asyncio.run(bot.macro())  # A reserved second footprint must not become a third Gateway.
    assert sum(action.ability == A.PROTOSSBUILD_GATEWAY for action in bot.actions) == 1


def test_parallel_capacity_respects_budget_and_ownership(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    populate(
        make_unit(U.NEXUS), make_unit(U.PYLON), make_unit(U.GATEWAY, build_progress=0.3), make_unit(U.PROBE)
    )
    bot.settings.construction = True
    bot.minerals = 149
    asyncio.run(bot.macro())
    assert not bot.actions
    bot.minerals = 400
    bot.settings.reserve_minerals = 300
    asyncio.run(bot.macro())
    assert not bot.actions
    bot.settings.reserve_minerals = 0
    bot.workers.first._proto.is_selected = True
    asyncio.run(bot.macro())
    assert not bot.actions


def test_ready_battery_provides_only_a_live_opening_defensive_anchor(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    populate(
        make_unit(U.NEXUS, radius=2.75),
        make_unit(U.PYLON, (9, 0)),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.SHIELDBATTERY, (6.5, -4.5)),
        make_unit(U.PROBE),
    )
    bot._opening_reserve = 0
    bot.opening_phase = "defend"
    assert not asyncio.run(bot.opening_battery(bot.townhalls.first, Units([], bot)))
    anchor = Point2(bot.opening_defense_anchor)
    assert anchor.distance_to(bot.structures(U.SHIELDBATTERY).first) <= 3.01
    assessment = assessment_candidate.GameAssessment().observe(bot, bot.units)
    assert Point2(assessment.home) == Point2(assessment.rally) == anchor
    bot.opening_phase = "complete"
    assert assessment_candidate.GameAssessment().observe(bot, bot.units).home == (0, 0)


def test_early_contact_does_not_pull_lone_defender_out_to_the_observed_threat(bot, make_unit, populate):
    opening(bot, make_unit, populate)
    populate(make_unit(U.NEXUS), make_unit(U.ZEALOT, (3, 0)), make_unit(U.MARINE, (25, 0), alliance=4))
    bot.opening_phase = "first_force"
    state = assessment_candidate.GameAssessment().observe(bot, bot.units)
    assert state.threat == (25, 0)  # Preserve the actual intelligence position.
    assert Point2(state.rally).distance_to(Point2((0, 0))) == pytest.approx(3.5)
    ranked = policies.candidates(state)
    plan = policies.compose(state, max(ranked, key=lambda c: c.score), 1, ranked)
    assert plan.missions[-1].target_id == "rally"
    assert plan.missions[-1].mode == "move"
    assert plan.missions[-1].target != state.threat
    assert contract.validate_plan(plan, state) is plan
    bot.opening_phase = "complete"
    assert assessment_candidate.GameAssessment().observe(bot, bot.units).opening_hold is None
    bot.opening_phase = "first_force"
    bot.settings.strategy = "defend"
    assert assessment_candidate.GameAssessment().observe(bot, bot.units).opening_hold is None
    bot.state.psionic_matrix.covers = lambda p: True
    bot.safe_at = lambda p, radius=18: False
    assert not asyncio.run(bot.opening_battery(bot.townhalls.first, Units([], bot)))
    assert not bot.actions
