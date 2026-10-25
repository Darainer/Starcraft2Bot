"""Launch a local real-time game with a human and bot sharing the Protoss player."""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

from loguru import logger
from sc2.data import Difficulty, Race
from sc2.player import Bot, Computer

from source.assistant_control import AssistantSettings
from source.runtime import RuntimeAssistant, RuntimeReport, inspect_installation, resolve_map, run_session


def port_number(value):
    number = int(value)
    if not 1 <= number <= 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", default="AbyssalReefLE", help="Installed .SC2Map name (without extension)")
    parser.add_argument("--map-file", type=Path, help="Explicit .SC2Map file; takes precedence over --map")
    parser.add_argument("--difficulty", choices=[d.name for d in Difficulty], default="Medium")
    parser.add_argument("--opponent", choices=["Terran", "Protoss", "Zerg", "Random"], default="Terran")
    parser.add_argument("--config", type=Path, help="Optional JSON settings file")
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
    try:
        settings = AssistantSettings.load(args.config) if args.config else AssistantSettings()
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
    logger.add(str(args.log_file), level="DEBUG", rotation="5 MB", retention=3)
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
    assistant = RuntimeAssistant(settings, report)
    players = [
        Bot(Race.Protoss, assistant, fullscreen=False),
        Computer(Race[args.opponent], Difficulty[args.difficulty]),
    ]
    logger.info(
        "Runtime report: {}. Human control remains unverified until the live checklist passes.", report.path
    )
    try:
        asyncio.run(
            run_session(
                install,
                game_map,
                players,
                args.replay,
                report,
                probe=args.probe,
                attach_port=args.attach_port,
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
