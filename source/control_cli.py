"""Inspect a session snapshot or queue a command through its local mailbox."""

import argparse
import json
from pathlib import Path

from source.local_control import queue_command


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--state", action="store_true", help="Print the latest sampled game state")
    parser.add_argument("command", nargs="*")
    args = parser.parse_args(argv)
    try:
        if args.state:
            destination = args.report.with_suffix(".state.jsonl")
            latest = None
            with destination.open(encoding="utf-8") as stream:
                for line in stream:
                    if line.strip():
                        latest = json.loads(line)
            if latest is None:
                raise ValueError("No state samples recorded yet")
            print(json.dumps(latest, indent=2))
        elif args.command:
            mailbox = queue_command(args.report, "!assist " + " ".join(args.command))
            print(f"Queued command: {mailbox}. See report last_control_command for acknowledgement.")
        else:
            print(args.report.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
