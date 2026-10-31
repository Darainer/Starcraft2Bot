"""Replay logged assessments through a policy without connecting to SC2."""

import argparse
import json
from collections import Counter
from pathlib import Path

from source.opponent_beliefs import beliefs_from_dict
from source.strategic_plan import Assessment, Opportunity, validate_plan
from source.strategy_director import StrategicDirector


def assessment_from_dict(data):
    values = dict(data)
    values["targets"] = tuple(
        Opportunity(**{**target, "position": tuple(target["position"])}) for target in data["targets"]
    )
    for key in ("home", "rally", "threat"):
        values[key] = tuple(data[key]) if data[key] is not None else None
    values["production"] = tuple(tuple(pair) for pair in data["production"])
    values["response_evidence"] = tuple(data.get("response_evidence", ()))
    values["opponent_beliefs"] = beliefs_from_dict(data.get("opponent_beliefs"))
    return Assessment(**values)


def replay(path, director=None):
    director = director or StrategicDirector()
    decisions, objectives, skipped = [], Counter(), 0
    with Path(path).open(encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            logged = row.get("decision", {})
            data = logged.get("assessment", row.get("assessment"))
            if data is None:
                skipped += 1
                continue
            state = assessment_from_dict(data)
            plan = validate_plan(director.decide(state), state)
            objectives[plan.objective] += 1
            decisions.append(
                {
                    "line": line_number,
                    "time": state.time,
                    "plan": plan.to_dict(),
                    "recorded_objective": logged.get("plan", {}).get("objective"),
                }
            )
    return {
        "samples": len(decisions),
        "skipped_legacy_samples": skipped,
        "objectives": dict(objectives),
        "decisions": decisions,
        "scope": "Decision inspection only; no orders or counterfactual match outcomes",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshots", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = json.dumps(replay(args.snapshots), indent=2) + "\n"
        if args.output:
            args.output.write_text(result, encoding="utf-8")
        else:
            print(result, end="")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
