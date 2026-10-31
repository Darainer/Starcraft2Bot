"""Offline strategy recognition and observable counter-role diagnostics.

Configured build labels enter scoring only. Role coverage is an ontology-based
proxy, not a combat simulator, confidence interval or counterfactual win rate.
"""

import argparse
import hashlib
import json
from collections import defaultdict
from itertools import chain
from pathlib import Path
from statistics import mean

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId

from source.game_ontology import ontology_document, unit_roles
from source.opponent_beliefs import OpponentBeliefModel
from source.opponent_strategy import LABELS, OpponentStrategyModel


def counter_response(row):
    """Score a recorded decision against fresh player-visible force evidence."""
    now = row["game_loop"] / 22.4
    intel = row.get("scouting", {}).get("intel", {})
    # Only this contemporaneous sighting is a denominator. Retained/global
    # estimates are not truth, and the configured build is deliberately unused.
    force = intel.get("visible_enemy_force") or {}
    age = now - force.get("seen_seconds", -999)
    total = force.get("supply", 0)
    if not 0 <= age <= 5 or total <= 0:
        return None
    air = min(total, max(0, force.get("air_supply", 0)))
    armor = min(total - air, max(0, force.get("armored_ground_supply", 0)))
    demand = {"air": air, "armored_ground": armor, "ground": total - air - armor}
    settings = row.get("settings", {})
    targets = dict(row.get("decision", {}).get("plan", {}).get("production", []))
    if not targets:
        return None
    observation = row.get("observation", {}).get("observation", {})
    raw = observation.get("raw_data", {})
    own = [u for u in raw.get("units", []) if u.get("alliance") == "Self"]
    released = {str(tag) for tag in row.get("released_unit_tags", [])}
    ready = [u for u in own if u.get("build_progress", 0) >= 1 and u.get("health", 0) > 0]
    buildings = {u.get("unit_type") for u in ready}
    upgrades = raw.get("player", {}).get("upgrade_ids", [])
    planned = dict.fromkeys(demand, 0.0)
    delivered = dict.fromkeys(demand, 0.0)
    target_supply = feasible_supply = 0.0
    for role in unit_roles():
        target = max(0, targets.get(role.name, 0)) * role.supply
        target_supply += target
        permitted = not role.requires_opt_in or settings.get(role.requires_opt_in, False)
        tech = all(U[name].value in buildings for name in role.prerequisites) and any(
            U[name].value in buildings for name in role.producers
        )
        if role.unit == "ARCHON":
            tech = U.ARCHON.value in buildings or (
                settings.get("archon_merge", False)
                and all(U[name].value in buildings for name in role.prerequisites)
                and sum(unit.get("unit_type") == U.HIGHTEMPLAR.value for unit in ready) >= 2
            )
        if permitted and tech:
            feasible_supply += target
        units = [
            u
            for u in ready
            if u.get("unit_type") == U[role.unit].value
            and not u.get("is_selected")
            and not u.get("is_hallucination")
            and str(u.get("tag")) not in released
            and settings.get("enabled", False)
            and settings.get("attack", False)
        ]
        if role.requires_opt_in == "storm":
            units = [
                u for u in units if UpgradeId.PSISTORMTECH.value in upgrades and u.get("energy", 0) >= 75
            ]
        for need in demand:
            if need in role.roles and permitted:
                planned[need] += target
                delivered[need] += len(units) * role.supply
    if target_supply <= 0:
        return None
    # Demand is a partition of observed supply. A versatile unit can cover
    # multiple roles in this capacity proxy; it is not an allocated battle plan.
    fit = sum(min(planned[k] / target_supply, value / total) for k, value in demand.items())
    readiness = sum(min(delivered[k], value) for k, value in demand.items()) / total
    capacity = max(0, 200 - settings.get("max_workers", 0))
    return {
        "planned_role_fit": fit,
        "delivered_role_readiness": readiness,
        "ready_tech_target_fraction": feasible_supply / target_supply,
        "target_supply": target_supply,
        "worker_adjusted_army_capacity": capacity,
        "target_budget_feasible": float(target_supply <= capacity),
        "observed_threat_supply": total,
        "planned_role_supply": planned,
        "delivered_role_supply": delivered,
    }


def review_rows(rows, reference_build=None):
    """Integrate held predictions only until the next recorded observation."""
    model = OpponentStrategyModel()
    belief_model = OpponentBeliefModel()
    weighted = defaultdict(float)
    durations = defaultdict(float)
    first_correct = first_threat = None
    previous = None
    samples = 0
    for row in rows:
        now = row["game_loop"] / 22.4
        if previous is not None:
            before, values = previous
            if now < before:
                raise ValueError("Observation times must be ordered")
            for key, value in values.items():
                if value is not None:
                    weighted[key] += value * (now - before)
                    durations[key] += now - before
        intel = row.get("scouting", {}).get("intel", {})
        prediction = model.observe(now, intel)
        beliefs = belief_model.observe(now, intel)
        values = {}
        if reference_build in LABELS:
            category = prediction["category"]
            values.update(
                strategy_accuracy=float(category == reference_build),
                strategy_coverage=float(category != "Unknown"),
                strategy_brier=sum(
                    (prediction["probabilities"][k] - (k == reference_build)) ** 2 for k in LABELS
                ),
            )
            if category == reference_build and first_correct is None:
                first_correct = now
        assessment = row.get("decision", {}).get("assessment", {})
        if first_threat is None and assessment.get("threat_supply", 0) > 0:
            first_threat = now
        response = counter_response(row)
        values["response_evidence_coverage"] = float(response is not None)
        if response is not None:
            values.update(
                {
                    key: response[key]
                    for key in (
                        "planned_role_fit",
                        "delivered_role_readiness",
                        "ready_tech_target_fraction",
                        "target_budget_feasible",
                    )
                }
            )
        for name in ("aggression", "economy", "air", "armored_ground", "light_ground", "cloak", "enemy_army"):
            signal = getattr(beliefs, name)
            values[f"{name}_uncertainty"] = signal.uncertainty
            values[f"{name}_evidence_age"] = signal.evidence_age
        previous = now, values
        samples += 1
    return {
        "samples": samples,
        "time_weighted": {key: weighted[key] / duration for key, duration in durations.items() if duration},
        "metric_observed_seconds": dict(durations),
        "first_correct_seconds": first_correct,
        "first_home_threat_seconds": first_threat,
        "recognition_lead_seconds": first_threat - first_correct
        if first_threat is not None and first_correct is not None
        else None,
    }


def review_recordings(paths):
    matches = []
    groups = defaultdict(list)
    for path in paths:
        path = Path(path)
        report = json.loads(path.read_text(encoding="utf-8-sig"))
        if (
            report.get("phase") != "ended"
            or report.get("error")
            or report.get("result") not in {"Result.Victory", "Result.Defeat", "Result.Tie"}
        ):
            raise ValueError(f"Incomplete recording: {path.name}")
        with path.with_suffix(".state.jsonl").open(encoding="utf-8-sig") as stream:
            rows = (json.loads(line) for line in stream if line.strip())
            first = next(rows, None)
            if first is None:
                raise ValueError("Recording has no observations")
            result = review_rows(chain([first], rows), report.get("opponent_build"))
        condition = {
            key: report.get(key)
            for key in (
                "map",
                "map_sha256",
                "random_seed",
                "game_time_limit",
                "fast_step_size",
                "opponent_race",
                "opponent_build",
                "opponent_difficulty",
                "ping",
            )
        }
        condition["settings"] = first.get("settings")
        condition_id = hashlib.sha256(json.dumps(condition, sort_keys=True).encode()).hexdigest()
        scenario = (report.get("opponent_race"), report.get("opponent_build"), condition_id)
        result.update(recording=path.name, scenario=scenario)
        matches.append(result)
        groups[scenario].append(result)
    # Every repeat contributes, then each explicit scenario contributes equally.
    metrics = sorted({key for m in matches for key in m["time_weighted"]})
    scenarios = []
    for scenario, repeats in sorted(groups.items()):
        scores = {}
        for key in metrics:
            values = [m["time_weighted"][key] for m in repeats if key in m["time_weighted"]]
            if values:
                scores[key] = mean(values)
        scenarios.append({"scenario": scenario, "repeats": len(repeats), "time_weighted": scores})
    return {
        "schema_version": 1,
        "ontology_id": ontology_document()["ontology_id"],
        "ontology_sha256": hashlib.sha256(
            json.dumps(ontology_document(), sort_keys=True).encode()
        ).hexdigest(),
        "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "matches": matches,
        "scenarios": scenarios,
        "scenario_mean": {
            key: mean(s["time_weighted"][key] for s in scenarios if key in s["time_weighted"])
            for key in metrics
            if any(key in s["time_weighted"] for s in scenarios)
        },
        "scope": "Retrospective public-observation diagnostics. Labels score recognition only. Role fit is an uncalibrated capacity proxy, not battle success. Missing evidence is excluded with coverage reported. Fixed-start repeats are not independent scenarios. No counterfactual match outcomes.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recordings", nargs="*", type=Path)
    parser.add_argument("--matrix", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    paths = list(args.recordings)
    if args.matrix:
        paths.extend(Path(row["report"]) for row in json.loads(args.matrix.read_text(encoding="utf-8-sig")))
    if not paths:
        parser.error("Provide recordings or --matrix")
    try:
        args.output.write_text(json.dumps(review_recordings(paths), indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
