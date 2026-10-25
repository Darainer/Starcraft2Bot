# Windows runtime troubleshooting

Setup/launch commands are in [the short installation guide](windows-install-and-play.md).
Run `Get-Help ./Setup.ps1 -Full` or `Get-Help ./Start.ps1 -Full` for script usage;
all paths below assume the repository root.

## Before retrying

Read `logs/assistant.log` and the newest `logs/runtime-*.json`. The report records
actual game binary/data identity, Python packages, map hash and errors.
`Start.ps1 -CheckOnly` validates paths; `Start.ps1 -Probe` opens/connects to SC2
without creating a match. Neither proves human controls work.

| Problem | Action |
| --- | --- |
| uv missing after Tools | Close and reopen PowerShell. If the installer requested a reboot, reboot first. |
| WinGet unavailable or agreements required | Install [uv manually](https://docs.astral.sh/uv/getting-started/installation/), complete installer prompts, then reopen PowerShell. |
| Execution policy blocks scripts | For this terminal only: `Set-ExecutionPolicy -Scope Process Bypass`. Organizational policy may still prevent execution. |
| Wrong game path | Rerun `./Setup.ps1 -Sc2Path 'D:\Games\StarCraft II'`. |
| Wrong/custom map | Rerun setup with `-MapFile 'D:\Maps\MyMap.SC2Map'` (two-player melee map). |
| Default map hash mismatch | Move the reported file aside, then rerun setup. The script will not overwrite it silently. |
| No SC2 binary / missing Support64 | Finish or repair the Battle.net installation; complete normal first launch. |
| SC2 exits / API timeout | Try the attach procedure below once; preserve the error if it also fails. |
| Active match/replay refused | Exit that session yourself, then restart an idle API client. |
| CreateGame / JoinGame / ability-ID error | Preserve report/log; check completed game data install and map compatibility. |
| Probe works, human controls disabled | Record failed acceptance and stop; changing economy policy cannot fix a disabled game UI. |
| Missing replay after interruption | Keep JSON/log; do not claim replay saving succeeded. |

Setup saves machine-specific paths in ignored `.local/windows.json`. Rerunning
setup reuses them, rechecks the map/environment and writes them only after
preflight succeeds. Explicit parameters override saved paths. Startup accepts
one-session `-Sc2Path`, `-MapFile`, `-ConfigFile`, `-Sc2Version`, `-AttachPort`,
`-Difficulty` and `-Opponent` overrides. Relative overrides use your current
folder. Scripts locate their own repository root and never switch Git branches.
Use setup again after pulling dependency changes; startup uses `--no-sync`.

## Alternative: Battle.net launch, then attach

1. Close SC2. In Battle.net's StarCraft II game settings, enable additional
   command-line arguments: `-listen 127.0.0.1 -port 5001 -displayMode 0`.
2. Click Play. Leave the API client idle; do not manually start a match.
3. Run the probe, then start only if it succeeds:

```powershell
.\Start.ps1 -AttachPort 5001 -Probe
.\Start.ps1 -AttachPort 5001 -StartPaused -Difficulty VeryEasy
```

The probe disconnects without quitting SC2. Match startup refuses an active
match/replay. On completion the assistant leaves its match but does not kill the
attached client. Close it yourself before another attempt. Remove the Battle.net
arguments before ordinary play. This route is not a known fix for the UI regression.

## Explicit legacy binary (optional, not automatically installed)

Use `./Start.ps1 -Sc2Version 4.10 -Probe` only if a legitimate 4.10 binary and its
data are already installed. If it succeeds, repeat with `-StartPaused` instead
of `-Probe`. This requires Base75689 and data hash
`B89B5D6FA7CBF6452E721311BFBC6CB2`. Missing/mismatched versions fail without fallback.
Old downloads have reported failures; stop if unavailable. No binary version is
certified by this project yet. Repeat human-control acceptance for any candidate.

## Agent and validation notes

- Scripts need no `Read-Host` or hidden pauses. Finish each stage, inspect its
  exit code, then hand off explicit manual steps in the short guide.
- Setup: 0 = stage complete; 3010 = tools installed, reopen terminal/reboot if
  requested; 1 = failure. Startup preserves CLI exit codes: 0 = completed,
  2 = invalid config/install/map, 1 = runtime/wrapper error, 130 = interruption.
- The game-start process remains running throughout play. Run as a long-lived
  terminal task and hand over to the interactive desktop, not a headless runner.
- Record mouse, keyboard, minimap and command-card checks from direct observation
  or label them human-reported. API success and a replay are insufficient.
- Use [the acceptance template](runtime-acceptance-template.md) and
  [functional checklist](assistant-live-test.md). Revalidate after game/SDK updates.

## Primary sources and evidence boundaries

- [Blizzard API overview](https://github.com/Blizzard/s2client-proto): explicitly lists tool-assisted human play.
- [InterfaceOptions](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto): `raw_affects_selection` explicitly discusses simultaneous human and agent play.
- [Protocol](https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md): WebSocket startup, local games, real-time mode and binary/data identity.
- [2026-10-08 protocol package update](https://github.com/Blizzard/s2client-proto/commit/4867bb9ede01e914c57a6fc9575dcc2f4bf0ca5a): 5.0.17.98310.0 version-string update, not proof of human-control testing.
- [BurnySC2 7.3.0](https://pypi.org/project/burnysc2/7.3.0/) and [pys2clientprotocol 1.0.2](https://pypi.org/project/pys2clientprotocol/1.0.2/): reviewed Python runtime dependencies.
- [BurnySC2 PR 213](https://github.com/BurnySc2/python-sc2/pull/213): 5.0.x UI regression report and version-selection workaround, merged June 2025; not a Blizzard fix.
- [Blizzard issue 208](https://github.com/Blizzard/s2client-proto/issues/208): Windows old-version download difficulties.
- [2026-09-18 third-party runtime procedure](https://github.com/golergka/jev-plays-starcraft-2/blob/main/docs/PROCEDURE.md): Battle.net + API attach tested on macOS; does not establish Windows shared human controls.
