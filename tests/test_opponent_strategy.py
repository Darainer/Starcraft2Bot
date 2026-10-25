import pytest

from source.opponent_strategy import LABELS, OpponentStrategyModel


def test_unknown_and_missing_vision_never_imply_macro_or_read_hidden_labels():
    first = OpponentStrategyModel().observe(100, {"opponent_build": "Rush"})
    second = OpponentStrategyModel().observe(100, {"opponent_build": "Air"})
    assert first == second and first["category"] == "Unknown"
    assert sum(first["probabilities"].values()) == pytest.approx(1)
    assert first["probabilities"] == dict.fromkeys(LABELS, 0.2)
    assert not first["control_enabled"]


@pytest.mark.parametrize("time,label", [(120, "Rush"), (300, "Timing")])
def test_pressure_timing_is_evidence_without_per_tick_confidence_accumulation(time, label):
    model = OpponentStrategyModel()
    intel = {"last_seen_seconds": time, "incoming_force": {"seen_seconds": time, "supply": 8}}
    prediction = model.observe(time, intel)
    assert prediction["category"] == label
    for offset in (1, 2, 3, 4):
        assert model.observe(time + offset, intel)["probabilities"] == prediction["probabilities"]
    assert model.observe(time + 150, intel)["category"] == "Unknown"


@pytest.mark.parametrize(
    "force,label,indicator",
    [
        ({"supply": 24, "air_supply": 20}, "Air", "combat_air"),
        ({"supply": 30, "armored_ground_supply": 20}, "Power", "armored_ground"),
    ],
)
def test_composition_supports_category_and_tactical_indicator(force, label, indicator):
    prediction = OpponentStrategyModel().observe(
        300, {"last_seen_seconds": 300, "composition_intel": {"seen_seconds": 300, **force}}
    )
    assert prediction["category"] == label
    assert indicator in prediction["tactical_indicators"]
    assert prediction["evidence"]


def test_macro_needs_positive_distinct_expansion_evidence():
    intel = {
        "last_seen_seconds": 200,
        "known_enemy_bases": [
            {"position": [20, 20], "seen_seconds": 200, "expansion": True},
            {"position": [60, 60], "seen_seconds": 200, "expansion": True},
        ],
    }
    assert OpponentStrategyModel().observe(200, intel)["category"] == "Macro"
    intel["known_enemy_bases"][1]["position"] = [20, 20]
    assert OpponentStrategyModel().observe(200, intel)["category"] == "Unknown"


def test_ambiguous_evidence_abstains_and_late_tech_is_not_backdated():
    model = OpponentStrategyModel()
    prediction = model.observe(
        300,
        {
            "last_seen_seconds": 300,
            "incoming_force": {"seen_seconds": 300, "supply": 8},
            "composition_intel": {"seen_seconds": 300, "supply": 30, "armored_ground_supply": 20},
            "known_enemy_tech": ["SPAWNINGPOOL"],
        },
    )
    assert prediction["category"] == "Unknown"
    assert {e["supports"] for e in prediction["evidence"]} == {"Power", "Timing"}
    early = OpponentStrategyModel().observe(
        70, {"last_seen_seconds": 70, "known_enemy_tech": ["SPAWNINGPOOL", "SPIRE"]}
    )
    assert {e["supports"] for e in early["evidence"]} == {"Rush", "Air"}


def test_future_dated_force_and_base_records_do_not_enter_the_belief():
    prediction = OpponentStrategyModel().observe(
        100,
        {
            "last_seen_seconds": 100,
            "incoming_force": {"seen_seconds": 200, "supply": 30},
            "composition_intel": {"seen_seconds": 200, "supply": 30, "air_supply": 30},
            "known_enemy_bases": [
                {"position": [i, i], "seen_seconds": 200, "expansion": True} for i in range(3)
            ],
        },
    )
    assert prediction["category"] == "Unknown" and not prediction["evidence"]
