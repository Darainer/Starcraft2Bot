import asyncio
from types import SimpleNamespace

import pytest
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U


def economy(bot, make_unit, populate, *, workers=30, saturation=16):
    bot.control.command("!assist economy off")
    bot.settings.expansion = True
    bot.settings.attack = False
    bot.supply_workers = workers
    bot.state.game_loop = 22400
    populate(
        make_unit(U.NEXUS, ideal_harvesters=saturation),
        make_unit(U.NEXUS, (0, 30), ideal_harvesters=saturation),
        make_unit(U.PROBE),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.MINERALFIELD, (36, 0), alliance=3, mineral_contents=1500),
    )


def test_third_base_is_funded_before_depletion_makes_normal_gate_unreachable(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.minerals = 400
    # 30 workers can saturate the remaining 32 positions; 38 cannot be reached
    # by the worker-production policy once these two mineral lines shrink.
    asyncio.run(bot.macro())
    assert [action.ability for action in bot.actions] == [A.PROTOSSBUILD_NEXUS]
    assert bot.minerals == 0


def test_reachable_gate_saves_income_and_honors_user_reserve(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    bot.settings.reserve_minerals = 100
    bot.settings.production = True
    bot.minerals = 450
    asyncio.run(bot.macro())
    assert not bot.actions and bot._macro_reserve == 400
    assert bot.minerals == 450
    bot.minerals = 500
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_NEXUS
    assert bot.minerals == 100


def test_unseen_mineral_amounts_do_not_block_a_normal_third_base(bot, make_unit, populate):
    economy(bot, make_unit, populate)
    # The owned lines still support 32 workers, but no positive mineral amount
    # for the unseen third appears in this participant's current observation.
    populate(*bot.all_own_units, make_unit(U.MINERALFIELD, (3, 0), alliance=3, mineral_contents=500))
    bot.is_visible = lambda point: point.x < 10
    asyncio.run(bot.macro())
    assert [action.ability for action in bot.actions] == [A.PROTOSSBUILD_NEXUS]
    assert tuple(bot.actions[0].target) == (30, 0)


def test_healthy_capacity_retains_normal_third_base_gate(bot, make_unit, populate):
    economy(bot, make_unit, populate, saturation=24)
    asyncio.run(bot.macro())
    assert not bot.actions
    bot.supply_workers = 38
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_NEXUS


@pytest.mark.parametrize(
    "boundary", ["floor", "disabled", "plan", "emergency", "pending", "ceiling", "ownership"]
)
def test_reachable_expansion_keeps_existing_boundaries(bot, make_unit, populate, boundary):
    economy(bot, make_unit, populate)
    if boundary == "floor":
        bot.supply_workers = 15
        bot.settings.max_workers = 14
    elif boundary == "disabled":
        bot.settings.expansion = False
    elif boundary == "plan":
        bot.strategic_plan = SimpleNamespace(expand=False, expires_at=bot.time + 10)
    elif boundary == "emergency":
        bot.economic_emergency = True
    elif boundary == "pending":
        bot.already_pending.side_effect = lambda kind: int(kind == U.NEXUS)
    elif boundary == "ceiling":
        bot.settings.bases = 2
    else:
        bot.control.released.update(bot.workers.tags)
    asyncio.run(bot.macro())
    assert not bot.actions
