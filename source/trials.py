"""Run bounded autonomous local matches and collect comparable sampled metrics."""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from source.analyze_session import summarize
from source.strategy_profiles import PROFILES

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", nargs="+", choices=list(PROFILES), default=["pressure", "balanced"])
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--duration", type=int, default=1500)
    parser.add_argument("--fast-step-size", type=int, default=32)
    parser.add_argument(
        "--difficulty",
        choices=["VeryEasy", "Easy", "Medium", "MediumHard", "Hard", "Harder", "VeryHard"],
        default="Easy",
    )
    parser.add_argument("--opponent", choices=["Terran", "Protoss", "Zerg"], default="Terran")
    parser.add_argument("--realtime", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.repeat <= 10 or not 30 <= args.duration <= 3600:
        parser.error("Repeat must be 1–10; duration must be 30–3600 game seconds")
    if not 4 <= args.fast_step_size <= 64:
        parser.error("Fast-test step size must be between 4 and 64 simulation loops")
    try:
        settings = json.loads((ROOT / ".local/windows.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        parser.error(f"Run Setup.ps1 first: {exc}")
    results = []
    for _ in range(args.repeat):
        for profile in args.profiles:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            report = ROOT / "logs" / f"runtime-{stamp}.json"
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
                "--profile",
                profile,
                "--difficulty",
                args.difficulty,
                "--opponent",
                args.opponent,
                "--game-time-limit",
                str(args.duration),
            ]
            if not args.realtime:
                command += ["--fast-test", "--fast-step-size", str(args.fast_step_size)]
            completed = subprocess.run(command, cwd=ROOT, check=False)
            try:
                result = summarize(report)
            except (OSError, ValueError) as exc:
                result = {"error": str(exc), "report": str(report)}
            result.update(
                profile=profile,
                opponent=args.opponent,
                difficulty=args.difficulty,
                game_time_limit=args.duration,
                fast_step_size=None if args.realtime else args.fast_step_size,
                exit_code=completed.returncode,
            )
            results.append(result)
            destination = ROOT / "logs" / "latest-trials.json"
            destination.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
            print(
                json.dumps(
                    {
                        k: result.get(k)
                        for k in (
                            "profile",
                            "result",
                            "sampled_game_seconds",
                            "completed_upgrades",
                            "game_time_limit",
                            "fast_step_size",
                            "error",
                            "report",
                        )
                    }
                ),
                flush=True,
            )
    if any(r["exit_code"] or r.get("error") for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
