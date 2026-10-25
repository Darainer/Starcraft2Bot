"""Measure tactical CPU cost on saved observations; never launch or connect to SC2."""

import argparse
import json
from collections import Counter
from math import ceil
from pathlib import Path
from statistics import median
from time import perf_counter

from source.runtime import recorded_observations
from source.scouting import ScoutController
from source.tactics import TacticalController


def distribution(values):
    ordered = sorted(values)
    return {
        "p50_ms": round(median(ordered), 3),
        "p95_ms": round(ordered[ceil(len(ordered) * 0.95) - 1], 3),
        "max_ms": round(ordered[-1], 3),
    }


def benchmark(report, repeat=3):
    if not 1 <= repeat <= 20:
        raise ValueError("Repeat must be between 1 and 20")
    stages = {name: [] for name in ("scouting", "tactics", "micro", "total")}
    objectives = Counter()
    samples = orders = maximum_units = violations = 0
    for _ in range(repeat):
        scout, controller = ScoutController(), TacticalController()
        for bot, _row in recorded_observations(report):
            started = perf_counter()
            scout.tick(bot)
            scouted = perf_counter()
            decision = controller.tick(bot)
            planned = perf_counter()
            controller.micro(bot)
            ended = perf_counter()
            for name, duration in (
                ("scouting", scouted - started),
                ("tactics", planned - scouted),
                ("micro", ended - planned),
                ("total", ended - started),
            ):
                stages[name].append(duration * 1000)
            tags = [action.unit.tag for action in bot.actions]
            violations += len(tags) != len(set(tags)) or any(
                not bot.control.eligible(action.unit) for action in bot.actions
            )
            samples += 1
            orders += len(tags)
            maximum_units = max(maximum_units, len(bot.all_own_units) + len(bot.all_enemy_units))
            objectives[decision.get("plan", {}).get("objective", decision["strategy"])] += 1
    if not samples:
        raise ValueError("Recording contains no observations")
    return {
        "recording": str(report),
        "repeat": repeat,
        "evaluations": samples,
        "snapshots_per_pass": samples // repeat,
        "maximum_observed_player_units": maximum_units,
        "stage_costs": {name: distribution(values) for name, values in stages.items()},
        "proposed_orders": orders,
        "ownership_or_duplicate_order_violations": violations,
        "objective_evaluations": dict(objectives),
        "scope": "Tactical CPU only. No game, network, macro API queries, serialization, or simulated action effects. Recorded pathing is static; snapshot intervals are not the micro cadence.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        results = [benchmark(report, args.repeat) for report in args.reports]
        output = json.dumps(results, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        print(output, end="")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
