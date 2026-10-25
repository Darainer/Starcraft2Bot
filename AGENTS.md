# Agent execution instructions

For installation, launch or live validation, follow
[docs/windows-install-and-play.md](docs/windows-install-and-play.md) in order.
It contains PowerShell commands, expected results, exit handling and explicit
human interaction boundaries. Target native Windows and the newest installed
retail binary first. Preserve local changes when updating this branch.

- Do not call `--probe` a gameplay acceptance test. Never infer human input works
  from an API response, a replay, a test pass or a bot match result.
- Record the exact ping binary/data identity and live checklist results. If the
  desktop is inaccessible, report live validation as pending; do not fabricate a
  supported game version or silently downgrade.
- Automation and human share one participant; retain selection preservation and
  ownership checks. Combat abilities must remain individually opt-in.
- `source/runtime.py` isolates SDK-private integration. Keep burnysc2 pinned and
  run the protocol/lifecycle tests when changing that boundary. Do not substitute
  another distribution that also installs the `sc2` or `s2clientprotocol` modules.
- Run `uv sync --locked`, `uv run --locked ruff check .`,
  `uv run --locked ruff format --check .`, `uv run --locked mypy`,
  `uv run --locked pytest --cov`, and `uv build` before publishing code changes.
- Synthetic CI tests must not launch a game or require a Windows desktop. Live
  tests belong on the user's PC and use the acceptance record template.
- Do not commit downloaded maps, logs, replays, credentials or personal paths.

See CONTRIBUTING.md for ownership, budget and ability-controller invariants.
