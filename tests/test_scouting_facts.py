import copy

import pytest

from source.scouting_diagnostics import ScoutingDiagnostics
from source.scouting_facts import ScoutingFacts

META = {
    1: {"kind": "ROACH", "supply": 2, "combat": True, "structure": False},
    2: {"kind": "SPAWNINGPOOL", "supply": 0, "combat": False, "structure": True},
    3: {"kind": "RAVAGER", "supply": 3, "combat": True, "structure": False},
}


def contact(kind=1, tag="a", **changes):
    return {"unit_type": kind, "tag": tag, "alliance": "Enemy", "display_type": "Visible", **changes}


def sample(now, units=(), **intel):
    return {
        "game_loop": now * 22.4,
        "visibility_scope": "player_observation_fog_of_war",
        "observation": {
            "observation": {"player_common": {"food_army": 10}, "raw_data": {"units": list(units)}}
        },
        "scouting": {"intel": intel},
    }


def test_facts_ignore_snapshots_blips_hallucinations_and_unknown_unit_data():
    row = sample(
        10,
        [
            contact(),
            contact(tag="b", display_type="Snapshot"),
            contact(tag="c", is_blip=True),
            contact(tag="d", is_hallucination=True),
            contact(kind=999, tag="e"),
        ],
    )
    facts = ScoutingFacts(META).observe(row)
    assert facts["recent_observed_enemy_combat_supply"] == 2
    assert facts["fact_presence"]["fresh_army_contact"]
    assert not facts["fact_presence"]["fresh_force"]
    assert len(facts["enemy_contacts"]) == 1
    assert facts["observed_supply_ratio"] == 0.2
    assert facts["own"]["food_workers"] == 0  # Omitted protobuf scalar means zero.


def test_individual_contacts_expire_without_refresh_from_new_unit_and_morphs_replace_tags():
    model = ScoutingFacts(META)
    model.observe(sample(0, [contact(), contact(tag="b")]))
    changed = model.observe(sample(10, [contact(kind=3)]))
    assert changed["recent_observed_enemy_combat_supply"] == 5
    assert model.observe(sample(50, [contact(tag="c")]))["recent_observed_enemy_combat_supply"] == 2
    assert model.observe(sample(101))["enemy_contacts"] == [
        {
            "kind": "ROACH",
            "visible_count": 0,
            "recent_30s_count": 0,
            "remembered_count": 1,
            "newest_age_seconds": pytest.approx(51),
            "oldest_age_seconds": pytest.approx(51),
            "supply_per_unit": 2,
            "combat_nonworker": True,
        }
    ]
    assert model.observe(sample(141))["enemy_contacts"] == []


def test_timestamped_memory_is_used_without_future_or_global_timestamp_leak():
    row = sample(
        100,
        enemy_unit_evidence=[
            {"tag": "a", "kind": "ROACH", "seen_seconds": 99},
            {"tag": "b", "kind": "ROACH", "seen_seconds": 101},
        ],
        composition_intel={"supply": 1000, "seen_seconds": 100},
    )
    facts = ScoutingFacts(META).observe(row)
    assert facts["recent_observed_enemy_combat_supply"] == 2
    assert facts["enemy_contacts"][0]["visible_count"] == 0
    row["observation"]["observation"]["raw_data"]["event"] = {"dead_units": ["a"]}
    assert ScoutingFacts(META).observe(row)["enemy_contacts"] == []


def test_expansion_empty_inspection_has_timestamp_and_does_not_assert_enemy_absence():
    row = sample(
        200,
        expansion_sites=[{"position": [1, 2], "status": "empty", "last_checked": 40}],
        known_enemy_bases=[{"position": [5, 6], "expansion": True, "seen_seconds": 190}],
    )
    facts = ScoutingFacts(META).observe(row)
    assert facts["fact_presence"]["fresh_expansion"]
    assert not facts["fact_presence"]["fresh_site_inspection"]
    assert facts["site_inspections"][0]["age_seconds"] == 160
    assert "entire" in facts["site_inspections"][0]["scope"]
    row["scouting"]["intel"]["expansion_sites"][0]["last_checked"] = 201
    assert ScoutingFacts(META).observe(row)["site_inspections"][0]["status"] == "unknown"


def test_prefix_outputs_are_immutable_and_never_depend_on_future_or_labels():
    rows = [
        sample(45, [contact(2, build_progress=0.1)]),
        sample(100, [contact(2, build_progress=1), contact(), contact(tag="b")]),
    ]
    model = ScoutingFacts(META)
    outputs = [model.observe(row) for row in rows]
    assert outputs[0] == ScoutingFacts(META).observe(rows[0])
    assert outputs[0]["technology_history"][0]["last_observed_progress"] == 0.1
    poisoned = copy.deepcopy(rows[0])
    poisoned.update(opponent_build="Timing", result="Victory", decision={"strategy": "Macro"})
    poisoned["scouting"]["intel"].update(
        opponent_strategy={"category": "Rush"}, opponent_beliefs={"army": 999}
    )
    assert ScoutingFacts(META).observe(poisoned) == outputs[0]


@pytest.mark.parametrize("bad_time", [-1, float("nan"), float("inf")])
def test_invalid_fact_clock_is_rejected(bad_time):
    with pytest.raises(ValueError, match="time"):
        ScoutingFacts(META).observe(sample(bad_time))


def test_oracle_scope_and_backwards_clock_are_rejected():
    row = sample(100)
    row["visibility_scope"] = "oracle"
    with pytest.raises(ValueError, match="perspective"):
        ScoutingFacts(META).observe(row)
    model = ScoutingFacts(META)
    model.observe(sample(100))
    with pytest.raises(ValueError, match="advance"):
        model.observe(sample(100))


def prediction(label):
    labels = ("Rush", "Timing", "Power", "Macro", "Air")
    return {
        "category": label,
        "leading_hypothesis": label,
        "evidence": [],
        "probabilities": {key: (1 if key == label else 0) if label != "Unknown" else 0.2 for key in labels},
    }


def test_diagnostics_distinguish_missing_evidence_from_wrong_logic_with_evidence():
    model = ScoutingDiagnostics("Timing")
    for now, force, label in [
        (0, False, "Unknown"),
        (10, True, "Rush"),
        (20, True, "Timing"),
        (30, True, "Timing"),
    ]:
        model.observe(
            {
                "time_seconds": now,
                "fact_presence": {"fresh_force": force, "fresh_technology": False, "fresh_expansion": False},
            },
            prediction(label),
        )
    result = model.result()
    assert result["strata"]["all"]["accuracy"] == pytest.approx(1 / 3)
    assert result["strata"]["fresh_force"]["accuracy"] == 0.5
    assert result["strata"]["no_fresh_relevant_evidence"]["recorded_seconds"] == 10
    assert result["first_correct_label_seconds"] == 20


def test_diagnostics_clip_opening_window_and_do_not_invent_labels():
    model = ScoutingDiagnostics()
    facts = {
        "time_seconds": 235,
        "fact_presence": {"fresh_force": False, "fresh_technology": False, "fresh_expansion": False},
    }
    model.observe(facts, prediction("Unknown"))
    model.observe({**facts, "time_seconds": 245}, prediction("Unknown"))
    assert model.result()["strata"]["opening/all"]["recorded_seconds"] == 5
    assert model.result()["strata"]["all"]["accuracy"] is None
    with pytest.raises(ValueError, match="advance"):
        model.observe(facts, prediction("Unknown"))
