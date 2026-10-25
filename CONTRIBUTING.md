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
- `economy_assistant.py`: SDK adapter, one paid macro action per 0.25 game seconds,
  worker allocation and optional abilities. All commands pass through `issue`.
- `game_assessment.py` / `scouting.py`: current-player facts and expiring intelligence.
- `strategic_plan.py` / `strategy_director.py` / `strategy_policies.py`: immutable
  contracts, validated plans, bounded asynchronous policy seam, and initial rules.
- `missions.py` / `action_intents.py`: disjoint persistent squads, local aborts,
  assignment revocation and short-lived movement intents.
- `tactics.py` / `army_waves.py`: tactical integration, combat micro and cohesion.
- `composition.py`: reversible scouting-driven production targets.
- `replay_strategy.py` / `analyze_session.py`: offline decisions and sampled metrics.
- `run_assistant.py`: CLI configuration, preflight/probe selection and reporting.
- `runtime.py`: exact binary/data validation, process ownership, loopback attach,
  raw shared-client configuration, match lifecycle and machine diagnostics.
  Uses pinned BurnySC2 private `_play_game` / `_execute` / process methods;
  `tests/test_runtime.py` exercises wire serialization and failure/cleanup paths.
  Re-review these methods before changing the SDK pin.
- `tests/conftest.py`: synthetic protobuf state plus real BurnySC2 units, actions
  and accounting; map/game queries are test doubles.

Preserve these rules in changes:

1. Never issue an army move/attack order from macro code. The optional tactical
   controller may issue these orders only while attack control and automation are enabled,
   through the same selection/release ownership checks. Abilities that change
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

## Runtime review (2026-10-25)

BurnySC2 7.3.0 and pys2clientprotocol 1.0.2 remain the current reviewed packages;
there is no unsupported dependency bump just to match SC2's game version string.
The protocol package is now an explicit dependency. Latest retail startup bypasses
the SDK's older version-label registry; explicit legacy versions fail closed.
Join options retain raw state/actions and human selection, without requesting
hidden cloaked units. No feature-layer/screenshot control or undocumented UI fix
is introduced. Unit/ability IDs and resource costs still come through the SDK and
live game data, so actual action effects require acceptance on the chosen patch.

The official protocol repository was version-bumped to 5.0.17.98310.0 on
2026-10-08; this alone is not evidence of repaired human input. See the runbook's
primary sources and version-specific acceptance template. This repository has
no verified live binary yet; do not describe a hypothetical fallback as verified.

## Windows entry-point tests

`tests/test_windows_scripts.py` runs Setup.ps1 and Start.ps1 in native Windows
PowerShell 5.1 during the existing Windows CI job. It substitutes uv/game calls,
so it can verify argument quoting, saved paths, repeat setup, failure exit codes,
corrupt-map rejection and execution from another directory without launching SC2
or installing software. These tests are skipped on other operating systems.
Installer/download success and actual gameplay still require the manual stages
in the Windows runbook. Setup tools installation uses WinGet; it exits 3010 after
a new install to signal the terminal/reboot handoff, then Configure can resume.
