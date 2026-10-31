"""Keep the neural dependency optional for the ordinary assistant."""

import importlib.util
import sys


def main():
    if sys.version_info < (3, 11) or importlib.util.find_spec("torch") is None:
        raise SystemExit("Training requires Python 3.11+ and: uv sync --locked --extra training")
    from source.training.cli import main as training_main

    training_main()
