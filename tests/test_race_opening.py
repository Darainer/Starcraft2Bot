import asyncio

import pytest
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U

from source.game_assessment import GameAssessment


def opener(bot, make_unit, populate, race, *, gateway_ready=False):
    populate(
        make_unit(U.NEXUS),
        make_unit(U.PYLON),
        make_unit(U.GATEWAY, (8, 8), build_progress=1 if gateway_ready else 0.3),
        make_unit(U.PROBE),
    )
    bot.enemy_race = race
    bot.state.game_loop = 2240
    bot.settings.attack = bot.settings.construction = True
    bot.settings.workers = bot.settings.gas = bot.settings.supply = bot.settings.upgrades = False
    bot.minerals, bot.vespene = 400, 0
    bot.supply_workers = 19


@pytest.mark.parametrize("race", [Race.Terran, Race.Protoss, Race.Random, None])
def test_non_zerg_and_unknown_retain_natural_sequence_without_proactive_second_gateway(
    bot, make_unit, populate, race
):
    opener(bot, make_unit, populate, race)
    # A hidden evaluation label or observational classifier cannot turn unknown into Zerg.
    bot.opponent_build = "Rush"
    bot.scout_report["opponent_strategy"] = {"category": "Rush"}
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.PROTOSSBUILD_NEXUS
    assert bot.opening_phase == "complete"


@pytest.mark.parametrize("race", [Race.Terran, Race.Protoss, Race.Random, None])
def test_original_core_priority_is_retained_for_non_zerg(bot, make_unit, populate, race):
    opener(bot, make_unit, populate, race, gateway_ready=True)
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.PROTOSSBUILD_CYBERNETICSCORE


@pytest.mark.parametrize("label", ["Rush", "Air"])
def test_known_public_zerg_race_enables_defense_independently_of_build_label(bot, make_unit, populate, label):
    opener(bot, make_unit, populate, Race.Zerg)
    bot.opponent_build = label
    asyncio.run(bot.macro())
    assert bot.actions[-1].ability == A.PROTOSSBUILD_GATEWAY
    assert bot.opening_phase == "first_force"


@pytest.mark.parametrize("race", [Race.Terran, Race.Protoss, Race.Random, None, Race.Zerg])
def test_opening_hold_requires_public_known_zerg_race(bot, make_unit, populate, race):
    opener(bot, make_unit, populate, race)
    bot.opening_phase = "first_force"  # Even stale phase metadata cannot override the race guard.
    state = GameAssessment().observe(bot, bot.units)
    assert (state.opening_hold is not None) == (race == Race.Zerg)
