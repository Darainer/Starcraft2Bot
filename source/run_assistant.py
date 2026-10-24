"""Launch a local real-time game with a human and bot sharing the Protoss player."""

import argparse
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

from loguru import logger
from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from source.assistant_control import AssistantSettings
from source.economy_assistant import EconomyAssistant


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", default="AbyssalReefLE", help="Installed .SC2Map name (without extension)")
    parser.add_argument("--difficulty", choices=[d.name for d in Difficulty], default="Medium")
    parser.add_argument("--opponent", choices=["Terran", "Protoss", "Zerg", "Random"], default="Terran")
    parser.add_argument("--config", type=Path, help="Optional JSON settings file")
    parser.add_argument("--replay", type=Path, help="Defaults to a timestamped file under replays/")
    parser.add_argument("--log-file", type=Path, default=Path("logs/assistant.log"))
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    parser.add_argument(
        "--check-config", action="store_true", help="Validate configuration without launching SC2"
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
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    args.log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(str(args.log_file), level="DEBUG", rotation="5 MB", retention=3)
    try:
        game_map = maps.get(args.map)
    except (ValueError, OSError, KeyError) as exc:
        parser.error(str(exc))
    if args.replay is None:
        args.replay = Path("replays") / f"assistant-{datetime.now():%Y%m%d-%H%M%S-%f}.SC2Replay"
    args.replay.parent.mkdir(parents=True, exist_ok=True)
    logger.info(
        "Starting local assistant: map={} opponent={} difficulty={}", args.map, args.opponent, args.difficulty
    )
    run_game(
        game_map,
        [
            Bot(Race.Protoss, EconomyAssistant(settings), fullscreen=False),
            Computer(Race[args.opponent], Difficulty[args.difficulty]),
        ],
        realtime=True,
        save_replay_as=str(args.replay),
    )


if __name__ == "__main__":
    main()
