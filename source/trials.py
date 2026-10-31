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
from time import perf_counter
from uuid import uuid4

from sc2.data import AIBuild

from source.analyze_session import summarize
from source.counter_composition import COMPOSITION_POLICIES
from source.run_assistant import game_seed
from source.strategy_portfolio import PLAYBOOK_CHOICES
from source.strategy_profiles import PROFILES

ROOT = Path(__file__).resolve().parents[1]


def run_trial(args, settings, profile, opponent, build, trial_id, stamp):
    started = perf_counter()
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
    command += ["--snapshot-interval", str(getattr(args, "snapshot_interval", 5))]
    command += ["--playbook", getattr(args, "playbook", "auto")]
    command += ["--composition-policy", getattr(args, "composition_policy", "legacy")]
    for name in ("oracle_harass", "oracle_beam", "defend_assets", "local_regroup"):
        if getattr(args, name, False):
            command.append("--" + name.replace("_", "-"))
    if getattr(args, "scout_revisit", False):
        command.append("--scout-revisit")
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
        scout_revisit=getattr(args, "scout_revisit", False),
        snapshot_interval=getattr(args, "snapshot_interval", 5),
        playbook=getattr(args, "playbook", "auto"),
        composition_policy=getattr(args, "composition_policy", "legacy"),
        oracle_harass=getattr(args, "oracle_harass", False),
        oracle_beam=getattr(args, "oracle_beam", False),
        defend_assets=getattr(args, "defend_assets", False),
        local_regroup=getattr(args, "local_regroup", False),
        exit_code=completed.returncode,
        wall_seconds=round(perf_counter() - started, 3),
    )
    result["game_seconds_per_wall_second"] = round(
        result.get("sampled_game_seconds", 0) / max(0.001, result["wall_seconds"]), 3
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", nargs="+", choices=list(PROFILES), default=["pressure", "balanced"])
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Concurrent games (1-8); may overlap scenarios when greater than repeat count",
    )
    parser.add_argument(
        "--duration", type=int, default=3600, help="Game-second limit (30-3600; default 3600)"
    )
    parser.add_argument("--fast-step-size", type=int, default=32)
    parser.add_argument("--snapshot-interval", type=int, default=5)
    parser.add_argument("--scout-revisit", action="store_true")
    parser.add_argument("--playbook", choices=PLAYBOOK_CHOICES, default="auto")
    parser.add_argument("--composition-policy", choices=COMPOSITION_POLICIES, default="legacy")
    for name in ("oracle-harass", "oracle-beam", "defend-assets", "local-regroup"):
        parser.add_argument("--" + name, action="store_true")
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
    if not 1 <= args.parallel <= 8:
        parser.error("Parallel games must be 1-8")
    if not 4 <= args.fast_step_size <= 64:
        parser.error("Fast-test step size must be between 4 and 64 simulation loops")
    if not 1 <= args.snapshot_interval <= 30:
        parser.error("Snapshot interval must be between 1 and 30 seconds")
    try:
        settings = json.loads((ROOT / ".local/windows.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        parser.error(f"Run Setup.ps1 first: {exc}")
    results = []
    destination = ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Separate runner processes can observe the same Windows clock tick. Their
    # report/log/replay paths must remain disjoint even when the timestamps match.
    stamp = f"{datetime.now():%Y%m%d-%H%M%S-%f}-{uuid4().hex}"
    trial_id = 0
    scenarios = list(product(args.profiles, args.opponents, args.builds))
    batches = [scenarios] if args.parallel > args.repeat else [[scenario] for scenario in scenarios]
    temporary = destination.with_suffix(destination.suffix + ".tmp")

    def save():
        results.sort(key=lambda item: item["trial_id"])
        temporary.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        temporary.replace(destination)

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        for batch in batches:
            pending = {}
            scenario_results = {scenario: [] for scenario in batch}
            for profile, opponent, build in batch:
                print(f"Queued {args.repeat} x {profile} vs {opponent} {build}; seed={args.seed}", flush=True)
                for _ in range(args.repeat):
                    trial_id += 1
                    future = pool.submit(run_trial, args, settings, profile, opponent, build, trial_id, stamp)
                    pending[future] = (profile, opponent, build)
            for future in as_completed(pending):
                result = future.result()
                group = scenario_results[pending[future]]
                group.append(result)
                results.append(result)
                save()
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
                                "wall_seconds",
                                "game_seconds_per_wall_second",
                            )
                        }
                    ),
                    flush=True,
                )
                if (
                    len(group) == args.repeat
                    and args.seed is not None
                    and not any(r["exit_code"] or r.get("error") for r in group)
                ):
                    signatures = {r.get("initial_state_sha256") for r in group}
                    identical = (
                        len(signatures) == 1
                        and None not in signatures
                        and all(r.get("initial_state", {}).get("game_loop") == 0 for r in group)
                    )
                    for item in group:
                        item["starting_conditions_match"] = identical
                    save()
                    if not identical:
                        for queued in pending:
                            queued.cancel()
                        print(
                            "Starting conditions differ or lack a loop-zero sample; stopping queued trials. "
                            "Already running games will finish and retain their individual reports.",
                            flush=True,
                        )
                        raise SystemExit(1)
    if any(r["exit_code"] or r.get("error") for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
