"""Build a reproducible Markdown/JSON review from completed player recordings."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from source.analyze_session import summarize
from source.opponent_strategy import LABELS, MODEL_VERSION, OpponentStrategyModel

HORIZONS = (120, 180, 240, 360, 600)


def configuration_identity(settings):
    """Hash resolved playable settings, not a pathname or hidden opponent label."""
    if settings is None:
        return None  # Legacy recordings may lack configuration evidence.
    return hashlib.sha256(json.dumps(settings, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def evaluation_manifest(matches, revision, comparison_group_id=None):
    groups = defaultdict(list)
    for match in matches:
        key = json.dumps(
            [match["scenario"], match["configuration_id"]], sort_keys=True, separators=(",", ":")
        )
        groups[key].append(match)
    return {
        "schema_version": 1,
        "gameplay_revision": revision,
        "comparison_group_id": comparison_group_id,
        "games": len(matches),
        "scenario_count": len(groups),
        "configuration_ids": sorted({m["configuration_id"] for m in matches if m["configuration_id"]}),
        "scenarios": [
            {
                "scenario": group[0]["scenario"],
                "configuration_id": group[0]["configuration_id"],
                "repeats": len(group),
                "loop_zero": all(m["initial_game_loop"] == 0 for m in group),
                "starting_fingerprints": sorted({m["initial_state_sha256"] for m in group}),
                "recordings": [m["recording"] for m in group],
            }
            for group in groups.values()
        ],
    }


def validate_suite(manifest, repeats, scenarios=None):
    """Fail closed on incomplete or unmatched matrices instead of dropping games."""
    if scenarios is not None and manifest["scenario_count"] != scenarios:
        raise ValueError(f"Expected {scenarios} scenarios; found {manifest['scenario_count']}")
    for group in manifest["scenarios"]:
        if group["repeats"] != repeats:
            raise ValueError(f"Expected {repeats} repeats: {group['scenario']}")
        if not group["loop_zero"] or len(group["starting_fingerprints"]) != 1:
            raise ValueError(f"Missing loop-zero sample or mismatched starts: {group['scenario']}")
        if group["configuration_id"] is None:
            raise ValueError("Missing resolved configuration evidence")
        scenario = group["scenario"]
        if scenario.get("random_seed") is None or scenario.get("opponent_build") not in LABELS:
            raise ValueError("Controlled suites require fixed seeds and explicit opponent builds")


def classification_metrics(examples):
    """One prediction per match/scenario, with abstentions counted in total accuracy."""
    matrix = {label: dict.fromkeys((*LABELS, "Unknown"), 0) for label in LABELS}
    correct = covered = conditional_correct = 0
    briers, calibration = [], defaultdict(list)
    for label, prediction in examples:
        category = prediction["category"]
        matrix[label][category] += 1
        correct += category == label
        covered += category != "Unknown"
        conditional_correct += category == label and category != "Unknown"
        probabilities = prediction["probabilities"]
        briers.append(sum((probabilities[k] - (k == label)) ** 2 for k in LABELS))
        best = max(probabilities, key=probabilities.get)
        confidence = probabilities[best]
        calibration[min(4, int(confidence * 5))].append((confidence, best == label))
    count = len(examples)
    per_class = {}
    for label, row in matrix.items():
        support = sum(row.values())
        predicted = sum(matrix[other][label] for other in LABELS)
        per_class[label] = {
            "support": support,
            "recall": row[label] / support if support else None,
            "precision": row[label] / predicted if predicted else None,
        }
    recalls = [row["recall"] for row in per_class.values() if row["recall"] is not None]
    bins = [
        {
            "range": [index / 5, (index + 1) / 5],
            "count": len(values),
            "mean_confidence": mean(v[0] for v in values),
            "empirical_accuracy": mean(v[1] for v in values),
        }
        for index, values in sorted(calibration.items())
    ]
    return {
        "samples": count,
        "accuracy": correct / count if count else None,
        "balanced_accuracy": mean(recalls) if recalls else None,
        "coverage": covered / count if count else None,
        "conditional_accuracy": conditional_correct / covered if covered else None,
        "multiclass_brier": mean(briers) if briers else None,
        "expected_calibration_error": sum(
            abs(b["mean_confidence"] - b["empirical_accuracy"]) * b["count"] for b in bins
        )
        / count
        if count
        else None,
        "confusion_matrix": matrix,
        "per_class": per_class,
        "calibration_bins": bins,
    }


def evaluate_session(path):
    result = summarize(path)
    if result["phase"] != "ended":
        raise ValueError(f"Recording is still active: {path}")
    if result["error"] or result["result"] not in {"Result.Victory", "Result.Defeat", "Result.Tie"}:
        raise ValueError(f"Recording has no valid terminal outcome: {path}")
    report = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    label = report.get("opponent_build")
    model = OpponentStrategyModel()
    predictions = []
    first_threat = None
    peak_workers = peak_army = 0
    with Path(path).with_suffix(".state.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            row = json.loads(line)
            seconds = round(row["game_loop"] / 22.4, 6)
            # Reconstruct every revision at the recorded cadence for fair comparison.
            # The reference label never enters this call or the evidence dictionary.
            predictions.append(model.observe(seconds, row.get("scouting", {}).get("intel", {})))
            assessment = row.get("decision", {}).get("assessment", {})
            if first_threat is None and assessment.get("threat_supply", 0) > 0:
                first_threat = seconds
            player = row.get("observation", {}).get("observation", {}).get("player_common", {})
            peak_workers = max(peak_workers, player.get("food_workers", 0))
            peak_army = max(peak_army, player.get("food_army", 0))
    first_correct = next((p["time"] for p in predictions if p["category"] == label), None)
    horizons = {
        str(horizon): next((p for p in reversed(predictions) if p["time"] <= horizon), None)
        if predictions[-1]["time"] >= horizon
        else None
        for horizon in HORIZONS
    }
    return {
        "recording": Path(path).name,
        "race": report.get("opponent_race", "Unknown"),
        "reference_build": label,
        "result": result["result"],
        "configuration_id": configuration_identity(result["initial_state"]["settings"]),
        "scenario": result["initial_state"]["scenario"],
        "initial_game_loop": result["initial_state"]["game_loop"],
        "initial_state_sha256": result["initial_state_sha256"],
        "sampled_game_seconds": result["sampled_game_seconds"],
        "performance": result["performance"],
        "first_completed_seconds": result["first_completed_seconds"],
        "action_rejections": result["observed_action_rejections"],
        "peak_workers": peak_workers,
        "peak_army_supply": peak_army,
        "first_home_threat_seconds": first_threat,
        "first_correct_classification_seconds": first_correct,
        "classification_lead_before_home_threat_seconds": first_threat - first_correct
        if first_threat is not None and first_correct is not None
        else None,
        "final_prediction": predictions[-1],
        "horizon_predictions": horizons,
    }


def evaluate(reports, revision, comparison_group_id=None):
    matches = [evaluate_session(path) for path in reports]
    unique = {}
    for match in matches:
        unique.setdefault(match["initial_state_sha256"], match)
    eligible = [m for m in unique.values() if m["reference_build"] in LABELS]
    horizons = {
        str(h): classification_metrics(
            [
                (m["reference_build"], m["horizon_predictions"][str(h)])
                for m in eligible
                if m["horizon_predictions"][str(h)] is not None
            ]
        )
        for h in HORIZONS
    }
    return {
        "schema_version": 2,
        "revision": revision,
        "manifest": evaluation_manifest(matches, revision, comparison_group_id),
        "model_version": MODEL_VERSION,
        "matches": matches,
        "independent_start_groups": len(unique),
        "result_counts": dict(Counter(m["result"] for m in matches)),
        "classification": {
            "final_unique_scenarios": classification_metrics(
                [(m["reference_build"], m["final_prediction"]) for m in eligible]
            ),
            "final_all_repeats": classification_metrics(
                [
                    (m["reference_build"], m["final_prediction"])
                    for m in matches
                    if m["reference_build"] in LABELS
                ]
            ),
            "horizons_unique_scenarios": horizons,
            "unlabeled_scenarios": len(unique) - len(eligible),
            "scope": "Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.",
        },
    }


def percent(value):
    return "n/a" if value is None else f"{100 * value:.1f}%"


def seconds(value):
    return "not observed" if value is None else f"{value:.1f}s"


def markdown(review, baseline=None):
    manifest = review.get("manifest", {})
    baseline_manifest = (baseline or {}).get("manifest", {})
    group_id = manifest.get("comparison_group_id")
    baseline_group_id = baseline_manifest.get("comparison_group_id")
    if group_id and baseline_group_id and group_id != baseline_group_id:
        raise ValueError("Comparison-group identifiers differ")
    lines = [
        f"# Match evaluation: {review['revision']}",
        "",
        f"Model: `{review['model_version']}`. {len(review['matches'])} matches; {review['independent_start_groups']} distinct starting-condition groups.",
        "",
        f"Results: `{review['result_counts']}`. `Result.Tie` means the configured time limit in this suite.",
        "",
        f"Comparison group: `{group_id or 'unrecorded (legacy)'}`. Configuration identities: `{', '.join(manifest.get('configuration_ids', [])) or 'unrecorded (legacy)'}`.",
        "",
        "## Matchups and observed trade evidence",
        "",
        "Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.",
        "",
        "| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    groups = defaultdict(list)
    for match in review["matches"]:
        groups[(match["race"], match["reference_build"])].append(match)
    for (race, build), matches in groups.items():
        perf = matches[0]["performance"]
        scores, movement = perf["resource_scores"], perf["movement"]
        outcomes = ", ".join(
            f"{count} {name.removeprefix('Result.')}"
            for name, count in Counter(m["result"] for m in matches).items()
        )
        lines.append(
            f"| {race} / {build} | {outcomes} | {scores.get('killed_army', 0):.0f} / {scores.get('lost_army', 0):.0f} | {perf['army_trade_ratio']:.2f} | {scores.get('killed_economy', 0):.0f} | {perf['bad_trade_window_count']} | {perf['expansion_target_samples']} | {movement['short_target_reversals']} | {movement['advance_regroup_transitions']} |"
        )
    lines += [
        "",
        "Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.",
        "",
        "## Opening and spending evidence",
        "",
        "Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.",
        "",
        "| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |",
        "| --- | ---: | --- | --- | ---: | ---: |",
    ]
    for (race, build), matches in groups.items():
        match = matches[0]
        perf = match["performance"]
        completed = match.get("first_completed_seconds", {})
        window = perf.get("first_bad_trade_window")
        window_text = f"{window['start']}-{window['end']}s" if window else "not recorded"
        lines.append(
            f"| {race} / {build} | {perf.get('worker_disappearances_by_240_seconds', 'n/a')} | {seconds(completed.get('ZEALOT'))} / {seconds(completed.get('STALKER'))} | {window_text} | {perf['sampled_supply_block_seconds']:.1f} | {perf['sampled_idle_facility_seconds']:.1f} |"
        )
    lines += [
        "",
        "## Costly trade windows and match details",
        "",
    ]
    for (race, build), matches in groups.items():
        match = matches[0]
        perf = match["performance"]
        lines += [
            f"### {race} / {build}",
            "",
            f"Evidence: `{match['recording']}`. End sample {match['sampled_game_seconds']:.1f}s; peak {match['peak_workers']} workers / {match['peak_army_supply']} army supply. First offensive advance: {seconds(perf.get('first_offensive_advance_seconds'))}; first expansion advance: {seconds(perf.get('first_expansion_advance_seconds'))}; inspected sites: {perf['inspected_expansion_sites']}.",
            "",
            f"Movement: `{perf['movement']}`. Action rejections: `{match['action_rejections']}`.",
            "",
            f"Score-based bad-trade windows: {perf['bad_trade_window_count']}; windows also showing own controlled-army disappearances: {perf['corroborated_bad_trade_window_count']}. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: {perf['resource_scores'].get('lost_economy', 0):.0f}.",
            "",
            f"Opponent prediction at last sample: **{match['final_prediction']['category']}**, confidence {match['final_prediction']['confidence']:.2f}. First correct confident classification: {seconds(match['first_correct_classification_seconds'])}; first home contact: {seconds(match['first_home_threat_seconds'])}. Positive classification lead means recognition preceded contact: {seconds(match['classification_lead_before_home_threat_seconds'])}.",
            "",
        ]
        for window in perf["worst_trade_windows"][:3]:
            lines.append(
                f"- {window['start']}–{window['end']}s: army lost {window['lost_army']:.0f}, army killed {window['killed_army']:.0f}, economy killed {window['killed_economy']:.0f}; objectives `{window['objectives']}`, targets `{window['targets']}`."
            )
            lines.append(
                f"  Own army disappearances: `{window['own_army_disappearances']}`; minimum estimated local advantage: {window['local_advantage_min']}; minimum army health fraction: {window['health_min']}; last sampled army center: `{window['last_army_center']}`; observed enemy composition: `{window['observed_enemy_composition']}`."
            )
        if not perf["worst_trade_windows"]:
            lines.append(
                "No sampled 15-second window met the bad-trade threshold (loss ≥300 and >1.5× enemy army value killed)."
            )
        for window in perf["worst_economy_loss_windows"]:
            lines.append(
                f"- Economic losses at {window['start']}–{window['end']}s: {window['lost_economy']:.0f} resources; own worker/base disappearances `{window['own_economy_disappearances']}`; objectives `{window['objectives']}`."
            )
        lines.append("")
    classification = review["classification"]
    final = classification["final_unique_scenarios"]
    lines += [
        "## Opponent-strategy classification",
        "",
        classification["scope"],
        "",
        "Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.",
        "",
        "| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, values in [*classification["horizons_unique_scenarios"].items(), ("final", final)]:
        brier = "n/a" if values["multiclass_brier"] is None else f"{values['multiclass_brier']:.3f}"
        lines.append(
            f"| {label} | {values['samples']} | {percent(values['accuracy'])} | {percent(values['balanced_accuracy'])} | {percent(values['coverage'])} | {percent(values['conditional_accuracy'])} | {brier} |"
        )
    lines += [
        "",
        "Final confusion matrix: rows are configured reference builds; columns are predictions.",
        "",
        "| Reference | Rush | Timing | Power | Macro | Air | Unknown |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, values in final["confusion_matrix"].items():
        lines.append(f"| {label} | " + " | ".join(str(values[k]) for k in (*LABELS, "Unknown")) + " |")
    lines += [
        "",
        f"Expected calibration error: {final['expected_calibration_error']}. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.",
        "",
    ]
    if baseline:
        old = {(m["race"], m["reference_build"], m["initial_state_sha256"]): m for m in baseline["matches"]}
        lines += [
            "## Matched comparison",
            "",
            f"Baseline `{baseline['revision']}`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.",
            "",
            "| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
        for (race, build), matches in groups.items():
            current = matches[0]
            prior = old.get((race, build, current["initial_state_sha256"]))
            if prior:
                a, b = prior["performance"], current["performance"]
                lines.append(
                    f"| {race} / {build} | {prior['result']} → {current['result']} | {a['movement']['short_target_reversals']} → {b['movement']['short_target_reversals']} | {a['movement']['advance_regroup_transitions']} → {b['movement']['advance_regroup_transitions']} | {a['bad_trade_window_count']} → {b['bad_trade_window_count']} |"
                )
            else:
                lines.append(f"| {race} / {build} | **Unmatched starting fingerprint** | n/a | n/a | n/a |")
        if not baseline_manifest:
            lines += [
                "",
                "Legacy baseline: configuration/group identity was not recorded separately; matching still requires the full starting fingerprint.",
            ]
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="*", type=Path)
    parser.add_argument("--matrix", type=Path)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--comparison-group", help="Stable identifier for this controlled comparison")
    parser.add_argument(
        "--expected-repeats", type=int, help="Reject incomplete or mismatched scenario groups"
    )
    parser.add_argument("--expected-scenarios", type=int)
    args = parser.parse_args(argv)
    try:
        reports = args.reports + (
            [Path(row["report"]) for row in json.loads(args.matrix.read_text(encoding="utf-8-sig"))]
            if args.matrix
            else []
        )
        if not reports:
            raise ValueError("Supply completed reports or a matrix")
        reports = list(dict.fromkeys(path.resolve() for path in reports))
        if args.expected_scenarios is not None and args.expected_repeats is None:
            raise ValueError("--expected-scenarios requires --expected-repeats")
        if args.expected_repeats is not None and args.expected_repeats < 1:
            raise ValueError("Expected repeats must be positive")
        review = evaluate(reports, args.revision, args.comparison_group)
        if args.expected_repeats is not None:
            validate_suite(review["manifest"], args.expected_repeats, args.expected_scenarios)
        baseline = json.loads(args.compare.read_text(encoding="utf-8-sig")) if args.compare else None
        rendered = markdown(review, baseline)
        for path in (args.output, args.json_output):
            path.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        args.json_output.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        args.json_output.with_suffix(".manifest.json").write_text(
            json.dumps(review["manifest"], indent=2) + "\n", encoding="utf-8"
        )
        print(f"Reviewed {len(review['matches'])} matches into {args.output}")
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
