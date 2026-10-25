"""Run bounded autonomous local matches and collect comparable sampled metrics."""

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from itertools import product
from pathlib import Path

from sc2.data import AIBuild

from source.analyze_session import summarize
from source.run_assistant import game_seed
from source.strategy_profiles import PROFILES

ROOT = Path(__file__).resolve().parents[1]


def run_trial(args, settings, profile, opponent, build, trial_id, stamp):
    report = ROOT / "logs" / f"runtime-{stamp}-{trial_id:03d}.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    replay = ROOT / "replays" / f"assistant-{stamp}-{trial_id:03d}.SC2Replay"
    command = [
        sys.executable,
        "-m",
        "source.run_assistant",
        "--config",
        "config/assistant.example.json",
        "--sc2-path",
        settings["sc2_path"],
        "--map-file",
        settings["map_file"],
        "--runtime-report",
        str(report),
        "--log-file",
        str(report.with_suffix(".log")),
        "--replay",
        str(replay),
        "--profile",
        profile,
        "--difficulty",
        args.difficulty,
        "--opponent",
        opponent,
        "--opponent-build",
        build,
        "--game-time-limit",
        str(args.duration),
    ]
    environment = os.environ.copy()
    if args.seed is not None:
        command += ["--seed", str(args.seed)]
        environment["PYTHONHASHSEED"] = str(args.seed)
    if not args.realtime:
        command += ["--fast-test", "--fast-step-size", str(args.fast_step_size)]
    with report.with_suffix(".console.log").open("w", encoding="utf-8") as console:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            env=environment,
            stdout=console,
            stderr=subprocess.STDOUT,
        )
    try:
        result = summarize(report)
    except (OSError, ValueError) as exc:
        result = {"error": str(exc), "report": str(report)}
    result.update(
        trial_id=trial_id,
        profile=profile,
        opponent=opponent,
        difficulty=args.difficulty,
        opponent_build=build,
        random_seed=args.seed,
        game_time_limit=args.duration,
        fast_step_size=None if args.realtime else args.fast_step_size,
        exit_code=completed.returncode,
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", nargs="+", choices=list(PROFILES), default=["pressure", "balanced"])
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--parallel", type=int, default=1, help="Concurrent games per scenario (1-3)")
    parser.add_argument("--duration", type=int, default=1500)
    parser.add_argument("--fast-step-size", type=int, default=32)
    parser.add_argument(
        "--difficulty",
        choices=["VeryEasy", "Easy", "Medium", "MediumHard", "Hard", "Harder", "VeryHard"],
        default="Easy",
    )
    parser.add_argument(
        "--opponents", "--opponent", nargs="+", choices=["Terran", "Protoss", "Zerg"], default=["Terran"]
    )
    parser.add_argument(
        "--builds", "--opponent-build", nargs="+", choices=[b.name for b in AIBuild], default=["RandomBuild"]
    )
    parser.add_argument("--seed", type=game_seed)
    parser.add_argument("--output", type=Path, default=Path("logs/latest-trials.json"))
    parser.add_argument("--realtime", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.repeat <= 10 or not 30 <= args.duration <= 3600:
        parser.error("Repeat must be 1-10; duration must be 30-3600 game seconds")
    if not 1 <= args.parallel <= 3:
        parser.error("Parallel games must be 1-3")
    if not 4 <= args.fast_step_size <= 64:
        parser.error("Fast-test step size must be between 4 and 64 simulation loops")
    try:
        settings = json.loads((ROOT / ".local/windows.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        parser.error(f"Run Setup.ps1 first: {exc}")
    results = []
    destination = ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    trial_id = 0
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        for profile, opponent, build in product(args.profiles, args.opponents, args.builds):
            # Complete all repeats of this scenario before moving to the next.
            print(f"Starting {args.repeat} x {profile} vs {opponent} {build}; seed={args.seed}", flush=True)
            pending = []
            scenario_results = []
            for _ in range(args.repeat):
                trial_id += 1
                pending.append(
                    pool.submit(run_trial, args, settings, profile, opponent, build, trial_id, stamp)
                )
            for future in as_completed(pending):
                result = future.result()
                scenario_results.append(result)
                results.append(result)
                results.sort(key=lambda item: item["trial_id"])
                temporary = destination.with_suffix(destination.suffix + ".tmp")
                temporary.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
                temporary.replace(destination)
                print(
                    json.dumps(
                        {
                            k: result.get(k)
                            for k in (
                                "trial_id",
                                "profile",
                                "opponent",
                                "opponent_build",
                                "result",
                                "sampled_game_seconds",
                                "random_seed",
                                "initial_state_sha256",
                                "error",
                                "report",
                            )
                        }
                    ),
                    flush=True,
                )
            if args.seed is not None and not any(r["exit_code"] or r.get("error") for r in scenario_results):
                signatures = {r.get("initial_state_sha256") for r in scenario_results}
                identical = (
                    len(signatures) == 1
                    and None not in signatures
                    and all(r.get("initial_state", {}).get("game_loop") == 0 for r in scenario_results)
                )
                for result in scenario_results:
                    result["starting_conditions_match"] = identical
                temporary.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
                temporary.replace(destination)
                if not identical:
                    print(
                        "Starting conditions differ or lack a loop-zero sample; stopping the matrix.",
                        flush=True,
                    )
                    raise SystemExit(1)
    if any(r["exit_code"] or r.get("error") for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
