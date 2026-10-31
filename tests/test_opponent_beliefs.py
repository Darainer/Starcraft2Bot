from dataclasses import FrozenInstanceError

import pytest

from source.opponent_beliefs import OpponentBeliefModel, beliefs_from_dict


def test_unknown_axes_start_maximally_uncertain_and_ignore_hidden_build():
    first = OpponentBeliefModel().observe(0, {"opponent_build": "Rush"})
    other = OpponentBeliefModel().observe(0, {"opponent_build": "Macro"})
    assert first == other
    for name in ("aggression", "economy", "air", "armored_ground", "light_ground", "cloak"):
        signal = getattr(first, name)
        assert signal.support is None and signal.uncertainty == 1
    assert first.enemy_army.estimate is None and first.enemy_army.upper is None
    assert first.relative_army.estimate is None and first.relative_army.uncertainty == 1


def test_economy_aggression_and_mixed_tech_are_independent_positive_evidence():
    intel = {
        "incoming_force": {"seen_seconds": 120, "supply": 8},
        "known_enemy_bases": [{"position": [i * 30, 0], "seen_seconds": 120} for i in range(3)],
        "known_enemy_tech_evidence": [{"tag": "tech", "kind": "SPIRE", "seen_seconds": 120}],
        "enemy_unit_evidence": [
            {"tag": i, "kind": "ROACH", "supply": 2, "armored": True, "air": False, "seen_seconds": 120}
            for i in range(6)
        ],
        "visible_enemy_force": {"supply": 12, "seen_seconds": 120},
    }
    model = OpponentBeliefModel()
    beliefs = model.observe(120, intel, own_supply=24)
    assert beliefs.aggression.support > 0.8 and beliefs.economy.support > 0.8
    assert beliefs.air.support == 0.8 and beliefs.armored_ground.support == 1
    assert beliefs.cloak.uncertainty == 1
    assert beliefs.enemy_army.lower == 12 and beliefs.enemy_army.upper > 12
    assert beliefs.relative_army.lower < beliefs.relative_army.estimate <= beliefs.relative_army.upper
    assert model.observe(120, intel, own_supply=24) == beliefs
    assert (
        model.observe(150, intel, own_supply=24).armored_ground.uncertainty
        > beliefs.armored_ground.uncertainty
    )


def test_future_sightings_and_unseen_areas_are_not_evidence():
    beliefs = OpponentBeliefModel().observe(
        100,
        {
            "known_enemy_tech_evidence": [{"kind": "DARKSHRINE", "seen_seconds": 200}],
            "known_enemy_bases": [{"position": [i, 0], "seen_seconds": 200} for i in range(3)],
            "composition_intel": {"supply": 100, "air_supply": 100, "seen_seconds": 200},
            "visible_enemy_force": {"supply": 100, "seen_seconds": 200},
            "incoming_force": {"supply": 100, "seen_seconds": 200},
            "expansion_sites": [{"position": [30, 0], "status": "unknown", "last_checked": -999}],
        },
    )
    assert beliefs.cloak.support is None and beliefs.economy.support is None
    assert beliefs.aggression.support is None and beliefs.air.support is None
    assert beliefs.enemy_army.estimate is None


def test_new_unrelated_unit_does_not_refresh_old_technology_or_old_army():
    model = OpponentBeliefModel()
    first = model.observe(100, {"known_enemy_tech": ["SPIRE"]})
    later = model.observe(
        200,
        {
            "known_enemy_tech": ["SPIRE"],
            "composition_intel": {"seen_seconds": 200, "supply": 100, "air_supply": 100},
            "enemy_unit_evidence": [
                {"tag": 1, "kind": "MUTALISK", "supply": 2, "air": True, "seen_seconds": 100}
            ],
        },
    )
    assert later.air.evidence_age == 100
    assert later.air.uncertainty > first.air.uncertainty
    assert later.enemy_army.estimate is None
    assert model.observe(300, {"known_enemy_tech": ["SPIRE"]}).air.support is None


def test_individual_unit_ages_and_tags_prevent_repeated_confidence_credit():
    sightings = [
        {"tag": i, "kind": "ROACH", "supply": 2, "armored": True, "seen_seconds": 100} for i in range(4)
    ]
    model = OpponentBeliefModel()
    first = model.observe(100, {"enemy_unit_evidence": sightings})
    duplicate = model.observe(100, {"enemy_unit_evidence": sightings + sightings})
    assert first == duplicate
    old = model.observe(160, {"enemy_unit_evidence": sightings})
    new = model.observe(
        160,
        {
            "enemy_unit_evidence": sightings
            + [{"tag": 10, "kind": "MARINE", "supply": 1, "light": True, "seen_seconds": 160}]
        },
    )
    assert old.armored_ground == new.armored_ground
    assert old.armored_ground.evidence_age == 60


def test_one_contact_cannot_establish_global_superiority_and_fog_reopens_range():
    model = OpponentBeliefModel()
    intel = {
        "composition_intel": {"supply": 20, "seen_seconds": 100},
        "visible_enemy_force": {"supply": 20, "seen_seconds": 100},
    }
    current = model.observe(100, intel, own_supply=30)
    assert current.enemy_army.uncertainty >= 0.7
    assert current.relative_army.lower < 1 < current.relative_army.upper
    stale = model.observe(150, intel, own_supply=30)
    assert (
        stale.relative_army.upper is None
        and stale.relative_army.uncertainty > current.relative_army.uncertainty
    )
    unknown = model.observe(200, intel, own_supply=30)
    assert unknown.relative_army.estimate is None


def test_nested_beliefs_round_trip_immutably_and_unknown_version_fails_closed():
    beliefs = OpponentBeliefModel().observe(100, {"known_enemy_tech": ["DARKSHRINE"]}, 20)
    assert beliefs_from_dict(beliefs.to_dict()) == beliefs
    with pytest.raises(FrozenInstanceError):
        beliefs.air.uncertainty = 0
    assert beliefs_from_dict({"model_version": "future"}) is None
    assert beliefs_from_dict(None) is None
    assert dict(beliefs.questions())["army"] > 0


@pytest.mark.parametrize("seconds,supply", [(float("nan"), 0), (-1, 0), (0, -1)])
def test_invalid_observation_values_fail_closed(seconds, supply):
    with pytest.raises(ValueError):
        OpponentBeliefModel().observe(seconds, {}, supply)
