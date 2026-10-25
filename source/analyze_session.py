"""Summarize sampled build progress and decisions without opening SC2."""

import argparse
import json
from collections import Counter
from pathlib import Path

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId


def summarize(report_path):
    report_path = Path(report_path)
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    milestones, strategies, samples = {}, Counter(), 0
    latest = None
    with report_path.with_suffix(".state.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            latest = row
            samples += 1
            strategies[row["decision"]["strategy"]] += 1
            raw = row["observation"]["observation"].get("raw_data", {})
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
