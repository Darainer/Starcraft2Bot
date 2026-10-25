"""Summarize sampled build progress and decisions without opening SC2."""

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId


def summarize(report_path):
    report_path = Path(report_path)
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    milestones, strategies, samples = {}, Counter(), 0
    latest = None
    metrics = {"sampled_supply_block_seconds": 0.0, "sampled_idle_facility_seconds": 0.0}
    previous = None
    banks, timings, objectives, outcomes = [], [], Counter(), Counter()
    expansion_scout_samples, expansion_target_samples, denial_samples = 0, 0, 0
    inspected_sites = set()
    peak_known_expansions = 0
    seen_events = set()
    production = {"GATEWAY", "ROBOTICSFACILITY", "STARGATE"}
    with report_path.with_suffix(".state.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            latest = row
            samples += 1
            strategies[row["decision"]["strategy"]] += 1
            decision = row["decision"]
            observation = row["observation"]["observation"]
            raw = observation.get("raw_data", {})
            player = observation.get("player_common", {})
            seconds = row["game_loop"] / 22.4
            blocked = (
                0 < player.get("food_cap", 0) < 200
                and player.get("food_cap", 0) - player.get("food_used", 0) < 2
            )
            idle = sum(
                u.get("alliance") == "Self"
                and u.get("build_progress", 0) >= 1
                and UnitTypeId(u["unit_type"]).name in production
                and not u.get("orders")
                for u in raw.get("units", [])
            )
            if previous is not None:
                elapsed = max(0, seconds - previous[0])
                metrics["sampled_supply_block_seconds"] += elapsed * previous[1]
                metrics["sampled_idle_facility_seconds"] += elapsed * previous[2]
            previous = seconds, blocked, idle
            banks.append((player.get("minerals", 0), player.get("vespene", 0)))
            if "controller_ms" in decision:
                timings.append(decision["controller_ms"])
            objective = decision.get("plan", {}).get("objective")
            scouting = row.get("scouting", {})
            intel = scouting.get("intel", {})
            expansion_scout_samples += scouting.get("observer", {}).get("phase") == "scouting_expansion"
            inspected_sites.update(
                tuple(site["position"])
                for site in intel.get("expansion_sites", [])
                if site.get("last_checked", -999) >= 0
            )
            peak_known_expansions = max(
                peak_known_expansions,
                sum(base.get("expansion", False) for base in intel.get("known_enemy_bases", [])),
            )
            expansion_ids = {
                target["id"]
                for target in decision.get("assessment", {}).get("targets", [])
                if target.get("expansion")
            }
            advancing_expansion = any(
                mission.get("target_id") in expansion_ids
                and mission.get("supply", 0) > 0
                and mission["phase"] in {"advance", "engage", "travel"}
                for mission in decision.get("missions", {}).values()
            )
            expansion_target_samples += advancing_expansion
            denial_samples += any(
                mission.get("role") == "deny" and mission.get("supply", 0) > 0
                for mission in decision.get("missions", {}).values()
            )
            if advancing_expansion:
                metrics.setdefault("first_expansion_advance_seconds", round(seconds, 1))
            if objective:
                objectives[objective] += 1
                phases = {m["phase"] for m in decision.get("missions", {}).values()}
                if objective in {"pressure", "counterattack", "finish"} and phases & {
                    "advance",
                    "engage",
                    "search",
                }:
                    metrics.setdefault("first_offensive_advance_seconds", round(seconds, 1))
            for event in decision.get("events", []):
                key = json.dumps(event, sort_keys=True)
                if key not in seen_events:
                    seen_events.add(key)
                    outcomes[event["result"]] += 1
            for unit in raw.get("units", []):
                if unit.get("alliance") == "Self" and unit.get("build_progress", 0) >= 1:
                    name = UnitTypeId(unit["unit_type"]).name
                    milestones.setdefault(name, round(row["game_loop"] / 22.4, 1))
    if latest is None:
        raise ValueError("No snapshots available")
    observation = latest["observation"]["observation"]
    raw = observation.get("raw_data", {})
    own = Counter(
        UnitTypeId(u["unit_type"]).name for u in raw.get("units", []) if u.get("alliance") == "Self"
    )
    upgrades = [UpgradeId(value).name for value in raw.get("player", {}).get("upgrade_ids", [])]
    metrics.update(
        mean_minerals=round(mean(bank[0] for bank in banks), 1),
        mean_gas=round(mean(bank[1] for bank in banks), 1),
        peak_minerals=max(bank[0] for bank in banks),
        peak_gas=max(bank[1] for bank in banks),
        controller_ms_p95=sorted(timings)[min(len(timings) - 1, int(len(timings) * 0.95))]
        if timings
        else None,
        objective_samples=dict(objectives),
        mission_outcomes=dict(outcomes),
        expansion_scout_samples=expansion_scout_samples,
        expansion_target_samples=expansion_target_samples,
        denial_squad_samples=denial_samples,
        inspected_expansion_sites=len(inspected_sites),
        peak_known_enemy_expansions=peak_known_expansions,
    )
    return {
        "report": str(report_path),
        "phase": report["phase"],
        "result": report.get("result"),
        "samples": samples,
        "sampled_game_seconds": round(latest["game_loop"] / 22.4, 1),
        "player": observation.get("player_common", {}),
        "own_units_and_buildings": dict(own),
        "completed_upgrades": upgrades,
        "observed_action_rejections": latest.get("observed_action_rejections", {}),
        "first_completed_seconds": milestones,
        "strategy_samples": dict(strategies),
        "performance": metrics,
        "last_decision": latest["decision"],
        "error": report.get("error"),
        "replay": report.get("replay"),
        "evidence_scope": "Sampled player API observations; no human-control or win-rate certification",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(summarize(args.report), indent=2))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
