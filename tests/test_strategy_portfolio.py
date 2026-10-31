import asyncio
import json
from dataclasses import replace

import pytest
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.army_waves import ArmyWaves
from source.assistant_control import AssistantSettings, Control
from source.game_assessment import GameAssessment
from source.replay_strategy import assessment_from_dict
from source.strategic_plan import validate_plan
from source.strategy_director import StrategicDirector
from source.strategy_portfolio import PLAYBOOKS, active_playbook, select_playbook
from source.strategy_profiles import PROFILES
from tests.test_adaptive_execution import weapon
from tests.test_first_robotics import setup_robotics
from tests.test_first_tech_investment import economy


def contacts(kind="MARINE", seen=100, count=4, **extra):
    return {
        "enemy_unit_evidence": [
            {"tag": str(i), "kind": kind, "supply": 1, "seen_seconds": seen, **extra} for i in range(count)
        ]
    }


def test_race_and_configured_labels_cannot_replace_missing_recon():
    for race in ("Terran", "Zerg", "Protoss", "Random", "Unknown"):
        decision = select_playbook(100, race, {"opponent_build": "Timing", "result": "Victory"})
        assert decision.id == "baseline" and decision.uncertainty == 1


def test_terran_options_change_with_individually_fresh_evidence():
    tech = {"known_enemy_tech_evidence": [{"kind": "FACTORY", "seen_seconds": 100}]}
    assert select_playbook(100, "Terran", tech).id == "terran_counter_tech"
    force = {**tech, **contacts()}
    assert select_playbook(100, "Terran", force).id == "terran_counter_range"
    assert select_playbook(145, "Terran", force).id == "terran_counter_tech"
    # One new Marine cannot refresh the old force/Factory.
    force["enemy_unit_evidence"].append(contacts(seen=200, count=1)["enemy_unit_evidence"][0])
    assert select_playbook(200, "Terran", force).id == "baseline"
    assert select_playbook(99, "Terran", tech).id == "baseline"
    duplicate = contacts(count=1)["enemy_unit_evidence"][0]
    assert select_playbook(100, "Terran", {"enemy_unit_evidence": [duplicate] * 8}).id == "baseline"


def test_zerg_completion_requires_own_ready_tech_and_fresh_light_contacts():
    intel = contacts("ZERGLING", count=8, light=True, air=False)
    assert select_playbook(100, "Zerg", intel).id == "baseline"
    assert select_playbook(100, "Zerg", intel, ready_tech=("ROBOTICSBAY",)).id == "zerg_counter_completion"
    assert select_playbook(145, "Zerg", intel, ready_tech=("ROBOTICSBAY",)).id == "baseline"
    intel["zerg_opening_response"] = {
        "response": "early_robotics",
        "time": 100,
        "valid_until": 200,
        "evidence": ["Early Pool"],
        "uncertainty": 0.65,
    }
    assert select_playbook(100, "Zerg", intel, ready_tech=("ROBOTICSBAY",)).id == "zerg_early_robotics"


@pytest.mark.parametrize("name", PLAYBOOKS)
def test_every_playbook_is_available_and_fixed_overrides_are_explicit(name, tmp_path):
    control = Control()
    assert "Rejected" not in control.command(f"!assist playbook {name}")
    assert control.settings.playbook == name
    assert "Rejected" in control.command("!assist playbook missing")
    assert control.settings.playbook == name
    item = PLAYBOOKS[name]
    choice = select_playbook(100, item.race or "Unknown", {}, name)
    assert choice.id == name and choice.uncertainty == 1
    if item.race:
        assert select_playbook(100, "Protoss", {}, name).id == "baseline"
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"playbook": name}))
    assert AssistantSettings.load(path).playbook == name


def select_for_bot(bot, playbook):
    bot.settings.attack = True
    bot.settings.playbook = playbook
    bot.enemy_race = Race[PLAYBOOKS[playbook].race or "Terran"]
    state = GameAssessment().observe(bot, bot.units)
    bot.strategic_plan = StrategicDirector().decide(state)
    return state


def test_selected_package_survives_replay_and_rejects_mixed_or_stale_components(bot):
    state = select_for_bot(bot, "terran_counter_range")
    restored = assessment_from_dict(json.loads(json.dumps(state.to_dict())))
    plan = validate_plan(StrategicDirector().decide(restored), restored)
    assert plan.playbook_id == "terran_counter_range" and plan.tactical_policy == "local_range"
    with pytest.raises(ValueError, match="playbook"):
        validate_plan(replace(plan, tactical_policy="formation"), restored)
    with pytest.raises(ValueError):
        validate_plan(plan, replace(restored, time=31))
    with pytest.raises(ValueError, match="playbook"):
        validate_plan(plan, replace(restored, playbook_id="terran_counter_tech"))


def test_legacy_early_robotics_assessment_replays_with_original_package(bot):
    state = select_for_bot(bot, "zerg_early_robotics")
    legacy = state.to_dict()
    for key in ("playbook_id", "playbook_uncertainty", "tactical_policy"):
        del legacy[key]
    restored = assessment_from_dict(legacy)
    assert StrategicDirector().decide(restored).playbook_id == "zerg_early_robotics"


@pytest.mark.parametrize(
    "override", ["pause", "attack", "adaptive", "manual", "script", "expired", "race", "playbook"]
)
def test_all_component_consumers_honor_user_control_and_expiry(bot, override):
    select_for_bot(bot, "terran_counter_range")
    assert active_playbook(bot).fund_bay
    if override == "pause":
        bot.settings.enabled = False
    elif override == "attack":
        bot.settings.attack = False
    elif override == "adaptive":
        bot.settings.adaptive_composition = False
    elif override == "manual":
        bot.settings.strategy = "retreat"
    elif override == "script":
        bot.settings.strategy_script = "custom.py"
    elif override == "expired":
        bot.state.game_loop += 22 * 22.4
    elif override == "playbook":
        bot.settings.playbook = "baseline"
    else:
        bot.enemy_race = Race.Zerg
    assert active_playbook(bot) == PLAYBOOKS["baseline"]


def setup_completion(bot, make_unit, populate, playbook):
    economy(bot, make_unit, populate, robo=True)
    bot.settings.colossi = 3
    populate(*bot.all_own_units, make_unit(U.ROBOTICSBAY), make_unit(U.IMMORTAL))
    data = bot.game_data.units[U.COLOSSUS.value]._proto
    data.mineral_cost, data.vespene_cost, data.food_required = 300, 200, 6
    bot.unit_supplies[U.COLOSSUS.value] = 6
    select_for_bot(bot, playbook)
    bot.minerals, bot.vespene = 125, 213


@pytest.mark.parametrize(
    "playbook", ["terran_counter_tech", "terran_counter_range", "zerg_counter_completion"]
)
def test_requested_counter_is_funded_without_cheap_fallback_spending(bot, make_unit, populate, playbook):
    setup_completion(bot, make_unit, populate, playbook)
    assert bot.first_tech_combat()[1] == U.COLOSSUS
    asyncio.run(bot.macro())
    assert not bot.actions and bot.minerals == 125
    assert not bot.affordable(U.STALKER)
    bot.minerals = 300
    bot._used.clear()
    asyncio.run(bot.macro())
    assert [a.ability for a in bot.actions] == [A.ROBOTICSFACILITYTRAIN_COLOSSUS]
    assert bot.minerals == 0 and bot.vespene == 13


@pytest.mark.parametrize("block", ["selected", "power", "supply", "income", "target"])
def test_completion_never_reserves_an_unattainable_or_disabled_counter(bot, make_unit, populate, block):
    setup_completion(bot, make_unit, populate, "zerg_counter_completion")
    producer = bot.structures(U.ROBOTICSFACILITY).first
    if block == "selected":
        producer._proto.is_selected = True
    elif block == "power":
        producer._proto.is_powered = False
    elif block == "supply":
        bot.supply_left = 5
    elif block == "income":
        bot.townhalls.first._proto.assigned_harvesters = 0
    else:
        bot.strategic_plan = replace(bot.strategic_plan, production=(("colossi", 0),))
    assert bot.first_tech_combat() is None
    assert getattr(bot, "_first_tech_reservation", None) is None


def test_bay_funding_is_attainable_and_scoped_to_selected_terran_package(bot, make_unit, populate):
    setup_robotics(bot, make_unit, populate)
    bot.settings.colossi = 3
    populate(*bot.all_own_units, make_unit(U.ROBOTICSFACILITY))
    bay = bot.game_data.units[U.ROBOTICSBAY.value]._proto
    bay.mineral_cost, bay.vespene_cost = 150, 150
    select_for_bot(bot, "terran_counter_tech")
    bot.minerals, bot.vespene = 300, 100
    assert asyncio.run(bot.fund_first_robotics(bot.start_location, 24, U.ROBOTICSBAY))
    assert not bot.actions and not bot.affordable(U.STALKER)
    bot.vespene = 150
    assert asyncio.run(bot.fund_first_robotics(bot.start_location, 24, U.ROBOTICSBAY))
    assert [a.ability for a in bot.actions] == [A.PROTOSSBUILD_ROBOTICSBAY]
    bot.actions.clear()
    bot._used.clear()
    select_for_bot(bot, "zerg_counter_completion")
    assert not asyncio.run(bot.fund_first_robotics(bot.start_location, 24, U.ROBOTICSBAY))
    assert not bot.actions


def test_local_range_policy_only_moves_eligible_out_of_range_ground_fighters(bot, make_unit, populate):
    weapon(bot, U.ZEALOT, domain=1, distance=0.1)
    army = [make_unit(U.ZEALOT, (10, 10)) for _ in range(12)]
    selected = make_unit(U.ZEALOT, (10, 10), is_selected=True)
    enemy = make_unit(U.MARINE, (18, 10), alliance=4)
    populate(*army, selected, enemy)
    bot.settings.scouting = False
    select_for_bot(bot, "terran_counter_range")
    args = (bot, bot.units, Point2((100, 10)), Point2((10, 10)), PROFILES["balanced"])
    orders, state = ArmyWaves().plan(*args)
    assert state["phase"] == "engage" and selected.tag not in orders
    assert all(target == enemy.position for mode, target in orders.values())
    select_for_bot(bot, "baseline")
    baseline, _ = ArmyWaves().plan(*args)
    assert all(target != enemy.position for mode, target in baseline.values())
    # A melee actor cannot chase a flying target through this policy.
    flying = make_unit(U.MUTALISK, (18, 10), alliance=4, is_flying=True)
    populate(*army, flying)
    select_for_bot(bot, "terran_counter_range")
    orders, _ = ArmyWaves().plan(*args)
    assert all(target != flying.position for mode, target in orders.values())
