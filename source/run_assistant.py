"""Launch a local real-time game with a human and bot sharing the Protoss player."""

import argparse
import asyncio
import json
import os
import random
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

from loguru import logger
from sc2.data import AIBuild, Difficulty, Race
from sc2.player import Bot, Computer

from source.assistant_control import AssistantSettings
from source.counter_composition import COMPOSITION_POLICIES
from source.runtime import RuntimeAssistant, RuntimeReport, inspect_installation, resolve_map, run_session
from source.strategy_portfolio import PLAYBOOK_CHOICES
from source.strategy_profiles import COMPOSITION, PROFILES


def port_number(value):
    number = int(value)
    if not 1 <= number <= 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535")
    return number


def game_seed(value):
    number = int(value)
    if not 0 <= number <= 0xFFFFFFFF:
        raise argparse.ArgumentTypeError("Seed must be an unsigned 32-bit integer")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", default="AbyssalReefLE", help="Installed .SC2Map name (without extension)")
    parser.add_argument("--map-file", type=Path, help="Explicit .SC2Map file; takes precedence over --map")
    parser.add_argument("--difficulty", choices=[d.name for d in Difficulty], default="Medium")
    parser.add_argument("--opponent", choices=["Terran", "Protoss", "Zerg", "Random"], default="Terran")
    parser.add_argument("--opponent-build", choices=[b.name for b in AIBuild], default="RandomBuild")
    parser.add_argument(
        "--seed", type=game_seed, help="Fixed SC2 and Python random seed for repeatable trials"
    )
    parser.add_argument("--config", type=Path, help="Optional JSON settings file")
    parser.add_argument("--profile", choices=list(PROFILES), help="Army setup and tactical thresholds")
    parser.add_argument("--strategy", choices=["auto", "defend", "regroup", "push", "retreat"])
    parser.add_argument("--strategy-script", type=Path, help="Local Python JSON strategy script")
    parser.add_argument("--playbook", choices=PLAYBOOK_CHOICES, help="Scouted repertoire or fixed experiment")
    parser.add_argument("--composition-policy", choices=COMPOSITION_POLICIES)
    for name in ("oracle-harass", "oracle-beam", "archon-merge", "defend-assets", "local-regroup"):
        parser.add_argument("--" + name, action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--attack", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--fast-test", action="store_true", help="Accelerated local autonomous evaluation")
    parser.add_argument(
        "--fast-step-size", type=int, default=32, help="Simulation loops per API turn in accelerated tests"
    )
    parser.add_argument("--game-time-limit", type=int, help="End test after this many game seconds (30–3600)")
    parser.add_argument(
        "--snapshot-interval", type=int, default=5, help="Recorded observation interval (1–30 seconds)"
    )
    parser.add_argument(
        "--scout-revisit", action="store_true", help="Experimental bounded natural-expansion revisit"
    )
    parser.add_argument("--sc2-path", type=Path, help="SC2 installation root; overrides SC2PATH")
    parser.add_argument(
        "--sc2-version", default="latest", help="latest installed binary, or exact SDK version label"
    )
    parser.add_argument(
        "--attach-port", type=port_number, help="Attach to an idle local API client; never kills it"
    )
    parser.add_argument(
        "--start-paused", action="store_true", help="Start automation paused; use !assist resume"
    )
    parser.add_argument("--replay", type=Path, help="Defaults to a unique file under replays/")
    parser.add_argument(
        "--runtime-report", type=Path, help="JSON diagnostics; default unique file under logs/"
    )
    parser.add_argument("--log-file", type=Path, default=Path("logs/assistant.log"))
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check-config", action="store_true", help="Validate configuration without inspecting SC2"
    )
    mode.add_argument("--doctor", action="store_true", help="Check local install/map; JSON output; no launch")
    mode.add_argument(
        "--probe", action="store_true", help="Connect and record actual binary version; no match"
    )
    parser.add_argument("--version", action="version", version=version("starcraft2-economy-assistant"))
    args = parser.parse_args(argv)
    if args.game_time_limit is not None and not 30 <= args.game_time_limit <= 3600:
        parser.error("Game time limit must be between 30 and 3600 seconds")
    if args.fast_test and args.attach_port:
        parser.error("Fast tests require a new owned client, not an attached client")
    if not 4 <= args.fast_step_size <= 64:
        parser.error("Fast-test step size must be between 4 and 64 simulation loops")
    if not 1 <= args.snapshot_interval <= 30:
        parser.error("Snapshot interval must be between 1 and 30 seconds")
    try:
        settings = AssistantSettings.load(args.config) if args.config else AssistantSettings()
        if args.profile:
            settings.profile = args.profile
            for name in COMPOSITION:
                setattr(settings, name, PROFILES[args.profile][name])
        if args.strategy:
            settings.strategy = args.strategy
        if args.playbook:
            settings.playbook = args.playbook
        if args.composition_policy:
            settings.composition_policy = args.composition_policy
        for name in ("oracle_harass", "oracle_beam", "archon_merge", "defend_assets", "local_regroup"):
            if getattr(args, name) is not None:
                setattr(settings, name, getattr(args, name))
        if args.attack is not None:
            settings.attack = args.attack
        if args.strategy_script:
            settings.strategy_script = str(args.strategy_script.resolve(strict=True))
        settings.validate()
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if args.check_config:
        print("Configuration valid")
        return
    if args.start_paused:
        settings.enabled = False
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    args.log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(str(args.log_file), level="DEBUG", rotation="5 MB", retention=None)
    try:
        install = inspect_installation(args.sc2_path, args.sc2_version)
        # Set before the SDK lazily resolves Paths on process launch.
        os.environ["SC2PATH"] = str(install.root)
        game_map = None if args.probe else resolve_map(install, args.map, args.map_file)
    except (ValueError, OSError) as exc:
        if args.doctor:
            print(json.dumps({"preflight_ok": False, "error": str(exc)}))
        parser.error(str(exc))
    if args.doctor:
        print(
            json.dumps(
                {
                    "preflight_ok": True,
                    "installation": install.report(),
                    "map": str(game_map),
                    "human_control": "not_verified",
                },
                indent=2,
            )
        )
        return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    args.replay = args.replay or Path("replays") / f"assistant-{stamp}.SC2Replay"
    args.runtime_report = args.runtime_report or Path("logs") / f"runtime-{stamp}.json"
    args.replay.parent.mkdir(parents=True, exist_ok=True)
    report = RuntimeReport(args.runtime_report, install, game_map, args.attach_port)
    report.update(
        opponent_difficulty=args.difficulty,
        opponent_race=args.opponent,
        opponent_build=args.opponent_build,
        random_seed=args.seed,
        game_time_limit=args.game_time_limit,
        snapshot_interval=args.snapshot_interval,
        scout_revisit=args.scout_revisit,
        log_retention="all_rotations",
        playbook=settings.playbook,
        composition_policy=settings.composition_policy,
    )
    if args.seed is not None:
        random.seed(args.seed)
    if args.fast_test:
        report.update(fast_test=True, fast_step_size=args.fast_step_size)
    assistant = RuntimeAssistant(settings, report)
    assistant.opponent_difficulty = args.difficulty
    players = [
        Bot(Race.Protoss, assistant, fullscreen=False),
        Computer(Race[args.opponent], Difficulty[args.difficulty], ai_build=AIBuild[args.opponent_build]),
    ]
    logger.info(
        "Runtime report: {}. Human control remains unverified until the live checklist passes.", report.path
    )
    try:
        test_options = {}
        if args.seed is not None:
            test_options["random_seed"] = args.seed
        if args.fast_test:
            test_options["realtime"] = False
        if args.game_time_limit is not None:
            test_options["game_time_limit"] = args.game_time_limit
        asyncio.run(
            run_session(
                install,
                game_map,
                players,
                args.replay,
                report,
                probe=args.probe,
                attach_port=args.attach_port,
                **test_options,
            )
        )
    except KeyboardInterrupt:
        report.update(phase="interrupted")
        raise SystemExit(130) from None
    except Exception as exc:
        logger.exception("Runtime failed: {}. See {}", exc, report.path)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
