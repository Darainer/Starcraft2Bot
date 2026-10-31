"""Offline actor boundary tests; these must never launch a game."""

import json
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace

import pytest

from source.assistant_control import AssistantSettings
from source.games.starcraft2.encoding import from_assessment
from source.opponent_beliefs import OpponentBeliefs, SignalBelief, StrengthBelief
from source.scouting_facts import ScoutingFacts
from source.strategic_plan import Assessment, Opportunity
from source.strategy_core.contracts import Feature, StrategicStateV1


def assessment(**changes):
    state = Assessment(
        version=2240,
        time=100,
        profile="pressure",
        army_supply=60,
        army_count=30,
        health=1,
        local_advantage=10,
        threat_supply=0,
        home_advantage=10,
        home=(0, 0),
        rally=(8, 8),
        threat=None,
        targets=(Opportunity("natural", (80, 80), 100, True, True, 65, 0, 2, 40, expansion=True),),
        intel_age=0,
        minerals=400,
        gas=200,
        workers=50,
        bases=3,
        production=(("stalkers", 40), ("zealots", 12), ("immortals", 6), ("high_templar", 0)),
    )
    return replace(state, **changes)


def settings(**changes):
    return AssistantSettings(attack=True, **changes)


def features(belief):
    return {feature.name: feature for feature in belief.shared.features}


def fact_sample(now=100, units=()):
    return ScoutingFacts({1: {"kind": "ROACH", "supply": 2, "combat": True, "structure": False}}).observe(
        {
            "game_loop": now * 22.4,
            "observation": {"observation": {"raw_data": {"units": list(units)}}},
        }
    )


def test_shared_core_imports_without_sdk_or_any_game_modules():
    code = """
import sys
import importlib.abc
class NoGames(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'sc2' or fullname.startswith(('sc2.', 'source.games', 'source.runtime',
            'source.strategic_plan', 'source.opponent_', 'source.game_')):
            raise AssertionError(fullname)
sys.meta_path.insert(0, NoGames())
from source.strategy_core.contracts import StrategicStateV1, Feature
assert Feature('test', None, 'ratio').value is None
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr


def test_contract_round_trip_preserves_missing_masks_units_and_immutability():
    belief = from_assessment(assessment(), settings(), elapsed_seconds=2)
    restored = StrategicStateV1.from_dict(json.loads(json.dumps(belief.shared.to_dict())))
    assert restored == belief.shared
    values = features(belief)
    assert values["own.deployment_capacity"].value == 0.3
    assert values["local.engagement_ratio"].value is None
    assert values["opponent.deployment_capacity_estimate"].value is None
    assert values["opponent.visible_deployment_capacity"].value is None
    assert not values["actors.control_eligibility"].supported
    with pytest.raises(FrozenInstanceError):
        restored.time_seconds = 0
    changed = belief.to_dict()
    changed["shared"]["features"][0]["value"] = 999
    assert features(belief)["own.deployment_capacity"].value == 0.3


def test_profile_tags_and_evaluation_labels_do_not_reach_shared_state():
    state = assessment()
    baseline = from_assessment(state, settings())
    changed = from_assessment(
        replace(state, profile="secret_build_seed_result", raid_response_tags=(987654,)), settings()
    )
    assert baseline.shared == changed.shared
    encoded = json.dumps(baseline.shared.to_dict())
    assert all(word not in encoded for word in ("pressure", "stalkers", "natural", "ROACH", "987654"))
    facts = fact_sample()
    facts.update(opponent_build="Rush", seed=42, result="Victory", oracle={"army": 999})
    clean = from_assessment(state, settings(), facts=fact_sample())
    poisoned = from_assessment(state, settings(), facts=facts)
    assert clean == poisoned


def test_fact_stream_records_visible_lower_bound_without_inventing_global_strength():
    facts = fact_sample(
        units=({"unit_type": 1, "tag": "enemy", "alliance": "Enemy", "display_type": "Visible"},)
    )
    belief = from_assessment(assessment(), settings(), facts=facts)
    values = features(belief)
    assert values["opponent.visible_deployment_capacity"].value == 0.01
    assert values["opponent.deployment_capacity_estimate"].value is None
    facts["enemy_contacts"][0]["visible_count"] = 999
    assert belief.to_dict()["facts"]["enemy_contacts"][0]["visible_count"] == 1
    empty = features(from_assessment(assessment(), settings(), facts=fact_sample()))
    assert empty["opponent.visible_deployment_capacity"].value == 0
    assert empty["opponent.deployment_capacity_estimate"].value is None


def test_independent_belief_ages_and_no_contact_sentinels():
    beliefs = OpponentBeliefs(
        time=98,
        air=SignalBelief(0.9, 0.2, 1, ("Observed STARPORT",)),
        cloak=SignalBelief(0.8, 0.3, 90, ("Old tech",)),
        enemy_army=StrengthBelief(40, 12, 70, 0.5, 5),
    )
    values = features(from_assessment(assessment(opponent_beliefs=beliefs), settings()))
    assert values["opponent.vertical_mobility_support"].age_seconds == 3
    assert values["opponent.vertical_mobility_support"].evidence[0].startswith("e")
    assert values["opponent.concealment_support"].value is None
    assert values["opponent.deployment_capacity_estimate"].value == 0.2
    assert values["opponent.deployment_capacity_lower"].value == 0.06
    assert values["opponent.deployment_capacity_upper"].value == 0.35
    assert values["opponent.deployment_capacity_estimate"].age_seconds == 7
    future = from_assessment(assessment(opponent_beliefs=replace(beliefs, time=101)), settings())
    assert features(future)["opponent.vertical_mobility_support"].value is None
    local = from_assessment(assessment(local_fight_observed=True, local_advantage=1.5), settings())
    assert features(local)["local.engagement_ratio"].value == 1.5


def test_target_order_padding_overflow_and_evidence_expiry():
    targets = tuple(Opportunity(str(i), (i, i), 100, False, False, i, 0, 1, i) for i in range(20))
    state = assessment(targets=targets)
    result = from_assessment(state, settings())
    assert result.target_overflow == 7
    assert result.targets[2] is None
    assert [t.id for t in result.targets[3:]] == [str(i) for i in range(19, 6, -1)]
    assert result.targets == from_assessment(replace(state, targets=targets[::-1]), settings()).targets
    expired = from_assessment(assessment(targets=(replace(targets[0], seen_at=9),)), settings())
    assert all(t is None for t in expired.targets[2:])
    with pytest.raises(ValueError, match="identities"):
        from_assessment(assessment(targets=(targets[0], targets[0])), settings())


def test_reserves_permissions_and_unavailable_blocks_are_explicit():
    belief = from_assessment(assessment(), settings(enabled=False, reserve_minerals=500, reserve_gas=30))
    assert not any(enabled for _, enabled in belief.shared.capabilities)
    assert features(belief)["own.primary_bank"].value == 0.4
    assert features(belief)["own.primary_reserve"].value == 0.5
    assert features(belief)["own.primary_spendable"].value == 0
    assert features(belief)["own.secondary_spendable"].value == 0.34


@pytest.mark.parametrize(
    "change",
    [
        {"time_seconds": -1},
        {"elapsed_seconds": 101},
        {"episode_start": True, "elapsed_seconds": 1},
        {"schema_version": "future"},
        {"ontology_version": "other"},
        {"features": []},
    ],
)
def test_invalid_shared_states_fail_closed(change):
    original = from_assessment(assessment(), settings()).shared
    with pytest.raises(ValueError):
        replace(original, **change)


@pytest.mark.parametrize(
    "change",
    [
        {"value": float("nan")},
        {"uncertainty": 2},
        {"age_seconds": -1},
        {"supported": False},
        {"evidence": ["mutable"]},
    ],
)
def test_invalid_features_fail_closed(change):
    with pytest.raises(ValueError):
        replace(Feature("test", 1, "fraction"), **change)


def test_fact_clock_and_schema_must_match():
    for facts in (fact_sample(now=99), {**fact_sample(), "schema_version": "oracle"}):
        with pytest.raises(ValueError):
            from_assessment(assessment(), settings(), facts=facts)
