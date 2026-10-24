# Development

## Reproducible environment

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
uv sync --locked
uv run --locked pre-commit install
uv run --locked sc2-assistant --check-config --config config/assistant.example.json
```

`.python-version` selects Python 3.12 for development. `pyproject.toml` supports
Python 3.10–3.13; CI tests representative Linux, Windows and macOS combinations.
`uv.lock` is committed. Change dependencies using `uv add` or `uv add --group dev`,
and commit both project metadata and lockfile. Use `uv sync --locked --no-dev`
for a runtime-only environment. `requirements.txt` is only a pip compatibility
shim; it does not duplicate dependency versions.

## Checks

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy
uv run --locked pytest --cov --cov-report=term-missing
uv build
```

Use `uv run ruff format .` and `uv run ruff check . --fix` to apply formatting and
safe lint fixes. Pre-commit runs lint and format checks; CI also runs types,
tests, CLI smoke checks and packaging. No SC2 installation, API key or paid
service is required for these checks. Tests must not accidentally launch SC2.

Strict type checking covers `assistant_control.py`, the configuration and
ownership boundary. The dynamic SDK adapter has protocol-based tests rather
than a claim of full static typing. Coverage reports include branches and are
published as CI artifacts. The combined statement/branch coverage floor is 85%;
coverage is not proof of actual gameplay quality.

## Architecture and invariants

- `assistant_control.py`: validated configuration, ownership and command parsing.
- `economy_assistant.py`: SDK adapter, one paid macro action per 0.5 game seconds,
  worker allocation and optional abilities. All commands pass through `issue`.
- `run_assistant.py`: configuration, logging, map selection and real-time launch.
- `tests/conftest.py`: synthetic protobuf state plus real BurnySC2 units, actions
  and accounting; map/game queries are test doubles.

Preserve these rules in changes:

1. Never issue an army move/attack order from macro code. Abilities that change
   position or interrupt orders must be opt-in and documented.
2. Skip selected/released actors, honor resource reserves, and avoid two orders
   to the same actor in one observation. Do not bypass `issue`.
3. Parse only the local player's `!assist` commands. Invalid settings must not
   partially mutate state. Pausing stops all new automation.
4. Keep tests of ownership, resource boundaries, ability legality, timing and
   failure paths. Add meaningful scenarios when behavior changes.
5. Do not describe a queued command as proof of an observed game effect.

Original `ThreeBaseVoidRay.py`, `setup_sc2_bot.py`, and `run_SC2_game.py` are legacy
examples, excluded from the assistant wheel and quality/coverage scope. Changes
to those examples need their own migration and tests; they are not certified by
the new suite.

## Debugging a live game

Run with `--log-level DEBUG`. Rotating logs live under `logs/` and record startup,
assistant commands and SC2 action errors. Replays get unique timestamped names
unless `--replay` is supplied. Logs and replays are ignored by git.

Complete [the live checklist](docs/assistant-live-test.md) and attach the relevant
log/replay when reporting a problem. Include OS, SC2 version, map, command,
expected behavior and actual behavior. Keep credentials and unrelated personal
information out of reports. There is no automatic telemetry upload.
