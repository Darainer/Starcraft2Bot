import json

import pytest

from source.evaluate_matches import (
    classification_metrics,
    configuration_identity,
    evaluate,
    evaluate_session,
    main,
    markdown,
    validate_suite,
)
from source.opponent_strategy import LABELS


def recording(tmp_path, name="sample", label="Rush", phase="ended"):
    path = tmp_path / f"{name}.json"
    path.write_text(
        json.dumps(
            {
                "phase": phase,
                "result": "Result.Victory",
                "opponent_build": label,
                "opponent_race": "Zerg",
                "random_seed": 42,
            }
        )
    )
    rows = []
    for time in (0, 120, 240, 360):
        intel = {"last_seen_seconds": time}
        if time == 120:
            intel["incoming_force"] = {"seen_seconds": time, "supply": 8}
        if time >= 240:
            intel.update(
                known_enemy_tech=["SPIRE"],
                composition_intel={"seen_seconds": time, "supply": 20, "air_supply": 20},
            )
        rows.append(
            {
                "game_loop": time * 22.4,
                "settings": {"profile": "pressure", "blink": False},
                "decision": {"strategy": "push", "assessment": {"threat_supply": 8 if time >= 240 else 0}},
                "scouting": {"intel": intel},
                "observation": {"observation": {"raw_data": {"units": []}}},
            }
        )
    path.with_suffix(".state.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return path


def test_reference_label_does_not_change_predictions_and_horizon_has_no_future_leak(tmp_path):
    rush = evaluate_session(recording(tmp_path))
    air = evaluate_session(recording(tmp_path, "other", "Air"))
    assert rush["final_prediction"] == air["final_prediction"]
    assert rush["horizon_predictions"]["180"]["category"] == "Rush"
    assert rush["horizon_predictions"]["240"]["category"] == "Air"
    assert rush["horizon_predictions"]["600"] is None
    assert rush["first_correct_classification_seconds"] == 120
    assert rush["classification_lead_before_home_threat_seconds"] == 120
    assert air["first_correct_classification_seconds"] == 240


def test_metric_denominators_abstentions_brier_and_confusion_are_explicit():
    uniform = {"category": "Unknown", "probabilities": dict.fromkeys(LABELS, 0.2)}
    perfect = {"category": "Rush", "probabilities": {k: float(k == "Rush") for k in LABELS}}
    metrics = classification_metrics([("Rush", perfect), ("Air", uniform)])
    assert metrics["accuracy"] == metrics["balanced_accuracy"] == metrics["coverage"] == 0.5
    assert metrics["conditional_accuracy"] == 1
    assert metrics["multiclass_brier"] == pytest.approx(0.4)
    assert metrics["confusion_matrix"]["Air"]["Unknown"] == 1
    assert metrics["per_class"]["Macro"]["recall"] is None
    assert classification_metrics([])["accuracy"] is None


def test_identical_repeats_are_grouped_and_cli_writes_review_and_comparison(tmp_path):
    paths = [recording(tmp_path, str(i)) for i in range(3)]
    review = evaluate(paths, "baseline")
    assert review["independent_start_groups"] == 1
    assert review["classification"]["final_all_repeats"]["samples"] == 3
    assert review["classification"]["final_unique_scenarios"]["samples"] == 1
    assert review["classification"]["horizons_unique_scenarios"]["600"]["samples"] == 0
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps([{"report": str(p)} for p in paths]))
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps(review))
    output, data = tmp_path / "report.md", tmp_path / "review.json"
    main(
        [
            "--matrix",
            str(matrix),
            "--revision",
            "next",
            "--output",
            str(output),
            "--json-output",
            str(data),
            "--compare",
            str(baseline),
        ]
    )
    text = output.read_text(encoding="utf-8")
    assert "Matched comparison" in text and "confusion matrix" in text and "not causal proof" in text
    assert json.loads(data.read_text())["revision"] == "next"
    assert "No sampled" in markdown(review)
    manifest = json.loads(data.with_suffix(".manifest.json").read_text())
    validate_suite(manifest, 3, 1)
    assert manifest["gameplay_revision"] == "next"
    assert len(manifest["configuration_ids"]) == 1
    assert "Opening and spending evidence" in text


def test_active_recordings_and_missing_inputs_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="still active"):
        evaluate_session(recording(tmp_path, phase="observing"))
    with pytest.raises(SystemExit):
        main(
            ["--revision", "x", "--output", str(tmp_path / "x.md"), "--json-output", str(tmp_path / "x.json")]
        )


def test_configuration_identity_is_canonical_and_does_not_invent_legacy_evidence():
    assert configuration_identity({"blink": False, "profile": "pressure"}) == configuration_identity(
        {"profile": "pressure", "blink": False}
    )
    assert configuration_identity({"blink": True}) != configuration_identity({"blink": False})
    assert configuration_identity(None) is None


def test_suite_rejects_missing_repeats_spawn_drift_and_nonzero_initial_sample(tmp_path):
    paths = [recording(tmp_path, str(i)) for i in range(3)]
    with pytest.raises(ValueError, match="Expected 3 repeats"):
        validate_suite(evaluate(paths[:2], "x")["manifest"], 3)
    with pytest.raises(ValueError, match="Expected 10 scenarios"):
        validate_suite(evaluate(paths, "x")["manifest"], 3, 10)
    snapshots = paths[-1].with_suffix(".state.jsonl")
    rows = [json.loads(line) for line in snapshots.read_text().splitlines()]
    rows[0]["observation"]["observation"]["player_common"] = {"minerals": 999}
    snapshots.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    with pytest.raises(ValueError, match="mismatched starts"):
        validate_suite(evaluate(paths, "x")["manifest"], 3)
    rows[0]["game_loop"] = 8
    snapshots.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    with pytest.raises(ValueError, match="Missing loop-zero"):
        validate_suite(evaluate(paths[-1:], "x")["manifest"], 1)


def test_comparison_reports_unmatched_scenarios_and_accepts_legacy_schema(tmp_path):
    current = evaluate([recording(tmp_path)], "new", "controlled")
    baseline = evaluate([recording(tmp_path, "old")], "old", "other")
    with pytest.raises(ValueError, match="Comparison-group"):
        markdown(current, baseline)
    baseline.pop("manifest")
    baseline.pop("schema_version")
    assert "Legacy baseline" in markdown(current, baseline)
    baseline["matches"][0]["initial_state_sha256"] = "different"
    assert "Unmatched starting fingerprint" in markdown(current, baseline)


def test_infrastructure_failure_cannot_be_counted_as_a_completed_match(tmp_path):
    path = recording(tmp_path)
    report = json.loads(path.read_text())
    report["error"] = "Replay or runtime failure"
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="no valid terminal outcome"):
        evaluate([path], "x")
