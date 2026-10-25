# Agent execution instructions

For installation, launch or live validation, follow
[docs/windows-install-and-play.md](docs/windows-install-and-play.md) in order.
It calls Setup.ps1 and Start.ps1, with explicit manual handoffs between stages.
Detailed exit handling is in docs/windows-troubleshooting.md. Target native Windows and the newest installed
retail binary first. Preserve local changes when updating the checkout.

- Live SC2 launches from Codex on this Windows PC require the user-approved
  **Full Access** execution context used by the successful sessions. Before
  launching, check the effective sandbox mode and `whoami`; a restricted
  `codexsandboxoffline` account is not the same context. Ordinary editing and
  synthetic tests do not require Full Access.
- If SC2 exits before API startup with `536936448` (`0x20010000`), check execution
  permissions before changing launch code or blaming tactical changes. The
  pre-overhaul commit `f55dc1b` also fails this way under the restricted account,
  while the earlier successful session recorded `danger-full-access`.
- If the user has already enabled Full Access, do not ask for permission again.
  Verify that it has reached the actual command runner; a still-restricted
  process means the change has not taken effect there. Report that distinction
  and resume live trials once the approved execution context is active.
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
