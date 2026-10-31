import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U


def depleted_economy(bot, make_unit, populate):
    bot.control.command("!assist economy off")
    bot.settings.expansion = True
    bot.settings.attack = False
    bot.state.game_loop = 22400
    bot.supply_workers = 33
    bot.supply_army = 20
    populate(
        make_unit(U.NEXUS, ideal_harvesters=0),
        make_unit(U.NEXUS, (0, 30), ideal_harvesters=0),
        make_unit(U.PROBE),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.MINERALFIELD, (36, 0), alliance=3, mineral_contents=1500),
    )


def test_depleted_mineral_lines_expand_below_normal_worker_gate(bot, make_unit, populate):
    depleted_economy(bot, make_unit, populate)
    bot.minerals = 400
    asyncio.run(bot.macro())
    assert [action.ability for action in bot.actions] == [A.PROTOSSBUILD_NEXUS]
    assert bot.minerals == 0


def test_recovery_skips_safe_mined_out_former_base_for_remaining_minerals(bot, make_unit, populate):
    depleted_economy(bot, make_unit, populate)
    for patch in bot.mineral_field:
        patch._proto.mineral_contents = 0
    populate(
        *bot.all_own_units,
        *bot.mineral_field,
        make_unit(U.MINERALFIELD, (86, 80), alliance=3, mineral_contents=1500),
    )
    # Ordinary expansion retains its historical preferred-site behavior.
    assert asyncio.run(bot.safe_expansion_location(bot.start_location)).x == 30
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_NEXUS
    assert tuple(bot.actions[0].target) == (80, 80)


def test_recovery_does_not_build_a_nexus_when_all_known_sites_are_mined_out(bot, make_unit, populate):
    depleted_economy(bot, make_unit, populate)
    for patch in bot.mineral_field:
        patch._proto.mineral_contents = 0
    asyncio.run(bot.macro())
    assert not bot.actions


def test_recovery_retains_nexus_bank_and_user_reserve(bot, make_unit, populate):
    depleted_economy(bot, make_unit, populate)
    bot.settings.reserve_minerals = 100
    bot.settings.gas = True
    bot.settings.production = True
    bot.minerals = 450
    asyncio.run(bot.macro())
    assert not bot.actions
    assert bot.minerals == 450
    bot.minerals = 500
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_NEXUS
    assert bot.minerals == 100


def test_healthy_oversaturated_bases_keep_normal_spending_priority(bot, make_unit, populate):
    depleted_economy(bot, make_unit, populate)
    for nexus in bot.townhalls:
        nexus._proto.ideal_harvesters = 16
    bot.supply_workers = 70
    bot.settings.workers = True
    bot.settings.max_workers = 80
    # Worker target is already met; normal macro still expands with the surplus
    # workforce, but only after its supply response, preserving healthy behavior.
    bot.settings.supply = True
    bot.supply_left = 0
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_PYLON


@pytest.mark.parametrize("blocked", ["ceiling", "strategy", "emergency", "pending", "ownership", "unsafe"])
def test_income_recovery_preserves_existing_expansion_boundaries(bot, make_unit, populate, blocked):
    depleted_economy(bot, make_unit, populate)
    if blocked == "ceiling":
        bot.settings.bases = 2
    elif blocked == "strategy":
        bot.strategic_plan = SimpleNamespace(expand=False, expires_at=bot.time + 10)
    elif blocked == "emergency":
        bot.economic_emergency = True
    elif blocked == "pending":
        bot.already_pending.side_effect = lambda kind: int(kind == U.NEXUS)
    elif blocked == "ownership":
        bot.control.released.update(bot.workers.tags)
    else:
        bot.safe_expansion_location = AsyncMock(return_value=None)
    asyncio.run(bot.macro())
    assert not bot.actions


def test_depleted_assimilators_do_not_block_fresh_gas(bot, make_unit, populate):
    bot.control.command("!assist economy off")
    bot.settings.gas = True
    bot.supply_workers = 33
    bot.vespene = 0
    populate(
        make_unit(U.NEXUS, ideal_harvesters=16),
        make_unit(U.NEXUS, (0, 30), ideal_harvesters=16),
        make_unit(U.PROBE),
        make_unit(U.GATEWAY),
        make_unit(U.ASSIMILATOR, (0, 3), vespene_contents=0),
        make_unit(U.ASSIMILATOR, (3, 0), vespene_contents=0),
        make_unit(U.VESPENEGEYSER, (0, 33), alliance=3, vespene_contents=2250),
    )
    asyncio.run(bot.macro())
    assert [action.ability for action in bot.actions] == [A.PROTOSSBUILD_ASSIMILATOR]
