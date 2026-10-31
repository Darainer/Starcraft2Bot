import asyncio

import pytest
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G

from source.army_waves import ArmyWaves
from source.warp_reinforcement import WarpReinforcement


def setup(bot, make_unit, populate):
    bot.control.command("!assist economy off")
    bot.settings.production = bot.settings.attack = bot.settings.archon_merge = True
    bot.settings.scouting = False
    bot.settings.composition_policy = "scouted"
    bot.enemy_race = Race.Zerg
    bot.state.game_loop = 14560
    bot.supply_workers, bot.supply_army = 33, 56
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    bot.scout_report = {
        "enemy_unit_evidence": [
            dict(tag=str(i), kind="ROACH", supply=2, armored=True, seen_seconds=650) for i in range(16)
        ]
    }
    populate(
        make_unit(U.NEXUS, ideal_harvesters=16, assigned_harvesters=16),
        make_unit(U.PYLON, (8, 0)),
        make_unit(U.TEMPLARARCHIVE),
        make_unit(U.ROBOTICSFACILITY),
        make_unit(U.ROBOTICSBAY),
        *(make_unit(U.WARPGATE, (20, i * 6)) for i in range(4)),
        *(make_unit(U.STALKER, (0, 20)) for _ in range(12)),
        *(make_unit(U.IMMORTAL, (0, 20)) for _ in range(2)),
        *(make_unit(U.COLOSSUS, (0, 20)) for _ in range(2)),
    )
    bot.reinforcement = WarpReinforcement()
    bot.get_available_abilities.return_value = [A.WARPGATETRAIN_HIGHTEMPLAR]
    return bot.reinforcement


def test_converted_gates_deliver_paid_archon_input_before_ordinary_spending(bot, make_unit, populate):
    setup(bot, make_unit, populate)
    bot.minerals, bot.vespene = 2520, 157  # Captured bank; existing Colossus floor already satisfied.
    bot.settings.reserve_minerals, bot.settings.reserve_gas = 100, 7
    asyncio.run(bot.macro())
    assert [action.ability for action in bot.actions] == [A.WARPGATETRAIN_HIGHTEMPLAR]
    assert (bot.minerals, bot.vespene) == (2470, 7)
    assert bot._paid_action_issued
    asyncio.run(bot.reinforcement.tick(bot, ArmyWaves(), allow_spending=False))
    assert len(bot.actions) == 1


def test_gas_can_be_reserved_only_with_income_and_expires_without_progress(bot, make_unit, populate):
    controller = setup(bot, make_unit, populate)
    populate(*bot.all_own_units, make_unit(U.ASSIMILATOR, assigned_harvesters=3, vespene_contents=1000))
    bot.settings.gas = True
    bot.vespene = 90
    assert asyncio.run(controller.first_archon_input(bot))
    assert bot._first_tech_reservation == (U.HIGHTEMPLAR, 150)
    assert not bot.actions
    bot._first_tech_reservation = None
    bot.state.game_loop += 560
    assert not asyncio.run(controller.first_archon_input(bot))
    assert controller.archon_input_report["phase"] == "reservation_cooldown"
    assert bot._first_tech_reservation is None


@pytest.mark.parametrize(
    "blocked", ["placement", "selected", "legal", "supply", "income", "permission", "prior_counter"]
)
def test_unattainable_input_never_locks_macro_budget(bot, make_unit, populate, blocked):
    controller = setup(bot, make_unit, populate)
    if blocked == "placement":
        bot.can_place.side_effect = lambda ability, points: [False] * len(points)
    elif blocked == "selected":
        for gate in bot.structures(U.WARPGATE):
            gate._proto.is_selected = True
    elif blocked == "legal":
        bot.get_available_abilities.return_value = []
    elif blocked == "supply":
        bot.supply_left = 0
    elif blocked == "income":
        bot.vespene = 149
    elif blocked == "permission":
        bot.settings.archon_merge = False
    else:
        bot._first_tech_reservation = (U.COLOSSUS, 200)
    assert not asyncio.run(controller.first_archon_input(bot))
    assert not bot.actions
    assert getattr(bot, "_first_tech_reservation", None) == (
        (U.COLOSSUS, 200) if blocked == "prior_counter" else None
    )
