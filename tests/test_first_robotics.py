import asyncio
from unittest.mock import AsyncMock

import pytest
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U

from source.game_assessment import GameAssessment
from source.strategy_director import StrategicDirector
from source.zerg_responses import ZergResponseSelector


def setup_robotics(bot, make_unit, populate):
    bot.control.command("!assist economy off")
    bot.settings.attack = bot.settings.production = bot.settings.construction = True
    bot.settings.gas = True
    bot.enemy_race = Race.Zerg
    bot.state.game_loop = 5376  # Captured 240-second bank before the delayed Robotics.
    bot.supply_workers, bot.supply_army = 19, 12
    bot.minerals, bot.vespene = 370, 70
    populate(
        make_unit(U.NEXUS, ideal_harvesters=16, assigned_harvesters=13),
        make_unit(U.ASSIMILATOR, (5, 0), assigned_harvesters=3, vespene_contents=1000),
        make_unit(U.PROBE),
        make_unit(U.PYLON),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.GATEWAY),
        *[make_unit(U.STALKER, (20 + i, 20)) for i in range(6)],
    )


def test_captured_robo_bank_is_held_against_worker_and_gateway_spending(bot, make_unit, populate):
    setup_robotics(bot, make_unit, populate)
    bot.settings.workers = True
    bot.scout_report["zerg_opening_response"] = ZergResponseSelector().observe(
        bot.time,
        {
            "enemy_unit_evidence": [
                {"tag": str(i), "kind": "ROACH", "supply": 2, "seen_seconds": bot.time} for i in range(2)
            ]
        },
    )
    bot.strategic_plan = StrategicDirector().decide(GameAssessment().observe(bot, bot.units))
    asyncio.run(bot.macro())
    assert not bot.actions
    assert (bot.minerals, bot.vespene) == (370, 70)
    assert not bot.affordable(U.STALKER)
    bot.vespene = 100
    bot._used.clear()
    asyncio.run(bot.macro())
    assert [a.ability for a in bot.actions] == [A.PROTOSSBUILD_ROBOTICSFACILITY]
    assert (bot.minerals, bot.vespene) == (220, 0)
    assert len(bot.construction_reservations) == 1


@pytest.mark.parametrize(
    "reason",
    [
        "emergency",
        "army",
        "workers",
        "income",
        "gas_off",
        "core",
        "pending",
        "selected",
        "released",
        "placement",
        "path",
        "permissions",
    ],
)
def test_unattainable_or_unsafe_robo_never_locks_recovery_budget(bot, make_unit, populate, reason):
    setup_robotics(bot, make_unit, populate)
    supply = 12
    if reason == "emergency":
        bot.economic_emergency = True
    elif reason == "army":
        supply = 4
    elif reason == "workers":
        bot.supply_workers = 8
    elif reason == "income":
        bot.gas_buildings.first._proto.assigned_harvesters = 0
    elif reason == "gas_off":
        bot.settings.gas = False
    elif reason == "core":
        bot.structures(U.CYBERNETICSCORE).first._proto.build_progress = 0.5
    elif reason == "pending":
        bot.already_pending.side_effect = lambda kind: int(kind == U.ROBOTICSFACILITY)
    elif reason == "selected":
        bot.workers.first._proto.is_selected = True
    elif reason == "released":
        bot.control.released.add(bot.workers.first.tag)
    elif reason == "placement":
        bot.find_placement = AsyncMock(return_value=None)
    elif reason == "path":
        bot.client.query_pathing = AsyncMock(return_value=None)
    else:
        bot.settings.construction = False
    assert not asyncio.run(bot.fund_first_robotics(bot.townhalls.first, supply))
    assert not bot.actions
    assert getattr(bot, "_first_tech_reservation", None) is None


def test_robo_reservation_releases_when_builder_becomes_human_owned(bot, make_unit, populate):
    setup_robotics(bot, make_unit, populate)
    assert asyncio.run(bot.fund_first_robotics(bot.townhalls.first, 12))
    assert not bot.affordable(U.STALKER)
    bot.workers.first._proto.is_selected = True
    assert not asyncio.run(bot.fund_first_robotics(bot.townhalls.first, 12))
    assert bot.affordable(U.STALKER)


def test_supply_precedes_first_robo_and_disabling_tech_targets_preserves_production(bot, make_unit, populate):
    setup_robotics(bot, make_unit, populate)
    bot.settings.supply = True
    bot.supply_left = 0
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_PYLON
    bot.settings.immortals = bot.settings.colossi = 0
    bot.settings.scouting = bot.settings.warp_reinforcement = False
    assert not asyncio.run(bot.fund_first_robotics(bot.townhalls.first, 12))
