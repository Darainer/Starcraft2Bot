import asyncio
import json
from dataclasses import replace

import pytest
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U

from source.game_assessment import GameAssessment
from source.replay_strategy import assessment_from_dict
from source.scouting import ScoutController
from source.strategic_plan import validate_plan
from source.strategy_director import StrategicDirector
from source.zerg_responses import ZergResponseSelector
from tests.test_first_robotics import setup_robotics


def technology(kind="SPAWNINGPOOL", seen=45):
    return {"known_enemy_tech_evidence": [{"tag": "pool", "kind": kind, "seen_seconds": seen}]}


def expansion():
    return {
        "enemy_bases": [{"tag": "natural", "position": [32, 0], "expansion": True, "build_progress": 0.2}]
    }


def roaches(seen=200):
    return {
        "enemy_unit_evidence": [
            {"tag": str(i), "kind": "ROACH", "supply": 2, "seen_seconds": seen} for i in range(2)
        ]
    }


def test_unknown_scouting_preserves_baseline_and_high_uncertainty():
    model = ZergResponseSelector()
    for now in (0, 90, 180, 240):
        response = model.observe(now, {})
        assert response["response"] == "baseline"
        assert response["hypothesis"] == "unresolved"
        assert response["uncertainty"] == 1
        assert response["first_expansion_seen"] is None


def test_early_pool_is_weak_evidence_and_does_not_refresh_without_observation():
    model = ZergResponseSelector()
    first = model.observe(45, technology())
    assert first["response"] == "early_robotics" and first["uncertainty"] >= 0.6
    assert model.observe(195, technology("HATCHERY", 195))["response"] == "early_robotics"
    expired = model.observe(231, {})
    assert expired["response"] == "baseline"
    assert expired["first_pool_seen"] == 45


def test_late_pool_cannot_be_mistaken_for_early_construction():
    response = ZergResponseSelector().observe(150, technology(seen=150))
    assert response["response"] == "baseline"
    assert response["first_pool_seen"] == 150


def test_positive_early_expansion_overrides_weak_pool_but_not_observed_force():
    model = ZergResponseSelector()
    model.observe(45, technology())
    economy = model.observe(100, expansion())
    assert economy["response"] == "baseline"
    assert economy["hypothesis"] == "observed_economic_commitment"
    assert economy["first_expansion_seen"] == 100
    force = model.observe(200, roaches())
    assert force["response"] == "early_robotics"
    assert force["observed_roach_path_supply"] == 4


def test_main_hatchery_is_not_an_expansion_signal():
    intel = expansion()
    intel["enemy_bases"][0]["expansion"] = False
    intel.update(technology())
    response = ZergResponseSelector().observe(100, intel)
    assert response["response"] == "early_robotics"
    assert response["first_expansion_seen"] is None


def test_force_is_deduplicated_and_each_contact_keeps_its_own_age():
    model = ZergResponseSelector()
    intel = roaches(100)
    intel["enemy_unit_evidence"].append(intel["enemy_unit_evidence"][0])
    assert model.observe(100, intel)["observed_roach_path_supply"] == 4
    intel["enemy_unit_evidence"].append(
        {"tag": "ling", "kind": "ZERGLING", "supply": 0.5, "seen_seconds": 200}
    )
    intel["composition_intel"] = {"seen_seconds": 200, "supply": 100}
    response = model.observe(200, intel)
    assert response["response"] == "baseline"
    assert response["observed_army_supply"] == 0.5


def test_fresh_warren_is_a_tech_option_not_a_claim_of_observed_army():
    response = ZergResponseSelector().observe(180, technology("ROACHWARREN", 175))
    assert response["response"] == "early_robotics"
    assert response["observed_army_supply"] == 0
    assert response["first_warren_seen"] == 175


def test_future_evidence_and_configured_build_labels_cannot_choose_a_response():
    intel = {
        **technology(seen=101),
        **roaches(101),
        "opponent_build": "Timing",
        "ai_build": 3,
        "opponent_strategy": {"prediction": "Timing"},
    }
    assert ZergResponseSelector().observe(100, intel) == ZergResponseSelector().observe(100, {})


def test_scouting_clock_must_reset_between_episodes():
    model = ZergResponseSelector()
    model.observe(100, technology())
    with pytest.raises(ValueError, match="time"):
        model.observe(10, {})


def prepare_response(bot, now=200):
    bot.enemy_race = Race.Zerg
    bot.settings.attack = True
    bot.state.game_loop = int(now * 22.4)
    model = ZergResponseSelector()
    model.observe(45, technology())
    bot.scout_report["zerg_opening_response"] = model.observe(bot.time, {})
    return GameAssessment().observe(bot, bot.units)


def test_response_survives_serialization_and_director_validation(bot):
    state = prepare_response(bot)
    restored = assessment_from_dict(json.loads(json.dumps(state.to_dict())))
    plan = validate_plan(StrategicDirector().decide(restored), restored)
    assert plan.response_policy == "early_robotics"
    assert plan.response_evidence == ("Spawning Pool observed by 90 seconds",)
    assert plan.response_policy_until == 225
    with pytest.raises(ValueError, match="response"):
        validate_plan(replace(plan, response_policy_until=201), replace(restored, time=202))
    with pytest.raises(ValueError, match="response"):
        validate_plan(plan, replace(restored, response_policy="baseline"))


@pytest.mark.parametrize("override", ["Terran", "Protoss", "manual", "script", "disabled", "not_adaptive"])
def test_race_and_user_controls_keep_baseline_response(bot, override):
    prepare_response(bot)
    if override in {"Terran", "Protoss"}:
        bot.enemy_race = getattr(Race, override)
    elif override == "manual":
        bot.settings.strategy = "regroup"
    elif override == "script":
        bot.settings.strategy_script = "custom.py"
    elif override == "disabled":
        bot.settings.attack = False
    else:
        bot.settings.adaptive_composition = False
    assert GameAssessment().observe(bot, bot.units).response_policy == "baseline"


@pytest.mark.parametrize("selected", [False, True])
def test_director_selected_funding_changes_actual_spending_with_existing_ownership_guards(
    bot, make_unit, populate, selected
):
    setup_robotics(bot, make_unit, populate)
    bot.settings.workers = True
    state = prepare_response(bot, 240 if not selected else 200)
    bot.strategic_plan = StrategicDirector().decide(state)
    asyncio.run(bot.macro())
    if selected:
        assert not bot.actions and (bot.minerals, bot.vespene) == (370, 70)
        bot._used.clear()
        bot.vespene = 100
        bot.workers.first._proto.is_selected = True
        asyncio.run(bot.macro())
        assert all(action.ability != A.PROTOSSBUILD_ROBOTICSFACILITY for action in bot.actions)
        bot._used.clear()
        bot.workers.first._proto.is_selected = False
        bot.actions.clear()
        asyncio.run(bot.macro())
        assert bot.actions[0].ability == A.PROTOSSBUILD_ROBOTICSFACILITY
    else:
        assert bot.actions and bot.actions[0].ability != A.PROTOSSBUILD_ROBOTICSFACILITY
        assert bot.minerals < 370


def test_scout_adapter_publishes_the_response_without_extra_scout_commands(bot, make_unit, populate):
    prepare_response(bot, 100)
    bot.settings.scouting = False
    populate(
        make_unit(U.NEXUS),
        make_unit(U.STALKER),
        make_unit(U.ROACH, (20, 0), alliance=4),
        make_unit(U.ROACH, (21, 0), alliance=4),
    )
    result = ScoutController().tick(bot)
    assert result["intel"]["zerg_opening_response"]["response"] == "early_robotics"
    assert not bot.actions
