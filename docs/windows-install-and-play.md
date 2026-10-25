# Windows installation and game startup: human + economy assistant

This is the execution runbook for a person **or an AI agent operating the Windows
PC**. Run numbered steps in order. Commands are Windows PowerShell, run from the
repository root unless stated otherwise. Do not use WSL, a headless container, or
a remote session without access to the interactive Windows desktop.

## Compatibility contract and stop conditions

Reviewed 2026-10-25. Target: the newest retail Windows SC2 binary installed by
Battle.net, currently represented in Blizzard's protocol repository as
**5.0.17.98310.0**. Dependencies: BurnySC2 **7.3.0**, pys2clientprotocol **1.0.2**,
and the exact transitive versions in `uv.lock`. The Python package version is
not the game binary version and need not have the same number.

**No game version has yet passed this project's live human-control acceptance
checks.** Current retail is the first candidate, not a certified working build.
The raw API explicitly anticipates simultaneous human play, but interactive UI
regressions have been reported in 5.0.x. No launcher change here claims to fix an
SC2 engine regression. If step 7 fails, stop; do not spend time tuning the bot.

Agent rules:

- Execute each command, inspect its exit code/output, and stop at the first
  failed prerequisite. PowerShell does not automatically throw on native command
  failure; the command blocks below check `$LASTEXITCODE` where necessary.
- Authentication, installation agreements and the interactive acceptance checks
  may require the human. Report that boundary explicitly. Do not invent results.
- A successful `--doctor`, `--probe`, unit test, or match result does **not** prove
  human control. Keep `human_control: not_verified` in the machine report;
  record observed human checks separately using step 8.
- Do not install arbitrary older binaries, silently change versions, disable
  anti-cheat, open firewall ports, or overwrite an active game. There is no
  injection, screen capture, model download, API key or cloud service involved.
- This creates a local custom match against Blizzard's computer. It does not
  attach to ladder, campaign, Co-op matchmaking or an ordinary running match.

## 1. Install and initialize SC2 (desktop / human step)

1. Install the [Battle.net desktop app](https://download.battle.net/).
2. Sign in, choose StarCraft II, and install it. Let the download/update finish
   completely, not just reach the playable threshold.
3. Click Play once. Complete any first-launch prompts and reach the main menu.
4. Exit StarCraft II. Battle.net may remain open. Close other SC2 game instances
   yourself; this runbook does not kill unrelated sessions.
5. Record the installation directory (Battle.net game settings show it). The
   usual value is `C:\Program Files (x86)\StarCraft II`.

## 2. Install Git and uv

Open Windows PowerShell. If Git or uv is already installed, skip its install.
Use [Git for Windows](https://git-scm.com/download/win) if WinGet is unavailable;
uv also provides an [official installer](https://docs.astral.sh/uv/getting-started/installation/).

```powershell
winget install --id Git.Git -e --source winget
if ($LASTEXITCODE -ne 0) { throw 'Git installation failed; inspect WinGet output.' }
winget install --id astral-sh.uv -e --source winget
if ($LASTEXITCODE -ne 0) { throw 'uv installation failed; inspect WinGet output.' }
```

Close and reopen PowerShell so PATH changes take effect, then check:

```powershell
$ErrorActionPreference = 'Stop'
git --version
if ($LASTEXITCODE -ne 0) { throw 'Git is not available.' }
uv --version
if ($LASTEXITCODE -ne 0) { throw 'uv is not available.' }
```

No separate Python installation or virtual-environment activation is needed.

## 3. Get the branch and locked Python environment

For a new checkout:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\source" | Out-Null
Set-Location "$env:USERPROFILE\source"
git clone --branch feature/human-economy-assistant --single-branch https://github.com/Darainer/Starcraft2Bot.git
if ($LASTEXITCODE -ne 0) { throw 'Clone failed; do not continue in a different checkout.' }
Set-Location Starcraft2Bot
```

For an existing checkout, navigate to it first. Run `git status --short`. Preserve
any local changes before switching branches; do not reset or overwrite them.
On a clean checkout:

```powershell
git fetch origin
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed.' }
git switch feature/human-economy-assistant
if ($LASTEXITCODE -ne 0) { throw 'Branch switch failed.' }
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'Branch cannot fast-forward; inspect before continuing.' }
```

Now install and verify:

```powershell
uv sync --locked --python 3.12
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
uv run --locked sc2-assistant --check-config --config config/assistant.example.json
if ($LASTEXITCODE -ne 0) { throw 'Configuration validation failed.' }
uv run --locked pytest
if ($LASTEXITCODE -ne 0) { throw 'Automated checks failed.' }
git rev-parse HEAD
```

Expected: configuration valid and tests pass. Keep the commit ID for step 8.
Do not install the old `sc2`/`s2clientprotocol` distributions into this environment:
they collide with the module names supplied by the pinned modern packages.

## 4. Set the game path and install a reproducible test map

Use the actual path from step 1:

```powershell
$env:SC2PATH = 'C:\Program Files (x86)\StarCraft II'
if (-not (Test-Path "$env:SC2PATH\Versions")) { throw 'Wrong SC2PATH.' }
Get-ChildItem "$env:SC2PATH\Versions" -Directory
New-Item -ItemType Directory -Force maps, logs, replays | Out-Null
```

Download Blizzard's two-player Bel'Shir Vestige map from a pinned revision of
its official C++ API repository. This is an older test map, not a current ladder
balance/map claim. The file stays in the checkout; the launcher sends its bytes
through the API, avoiding administrator writes into Program Files.

```powershell
$MapUrl = "https://raw.githubusercontent.com/Blizzard/s2client-api/614acc00abb5355e4c94a1b0279b46e9d845b7ce/maps/Ladder/(2)Bel'ShirVestigeLE%20(Void).SC2Map"
Invoke-WebRequest -Uri $MapUrl -OutFile 'maps/BelShirVestigeLE.SC2Map' -UseBasicParsing
uv run --locked python -c "import hashlib,pathlib; d=pathlib.Path('maps/BelShirVestigeLE.SC2Map').read_bytes(); h=hashlib.sha1(b'blob '+str(len(d)).encode()+bytes([0])+d).hexdigest(); assert h=='42694de3201acea2269813c2f1bf6703af29c703', 'Map download differs from Blizzard Git blob'; print('Map verified:',len(d),'bytes')"
if ($LASTEXITCODE -ne 0) { throw 'Map verification failed; do not use this download.' }
```

The Git blob check verifies file identity, not gameplay compatibility. An
alternative is an existing official two-player melee `.SC2Map`: substitute its
full path in `--map-file` below. Avoid campaign/Arcade maps for this first test.

## 5. Run preflight without starting the game

```powershell
uv run --locked sc2-assistant --doctor --map-file maps/BelShirVestigeLE.SC2Map
if ($LASTEXITCODE -ne 0) { throw 'Preflight failed; fix the reported path/map problem.' }
```

Expected JSON: `preflight_ok: true`, executable path, installed build numbers and
selected build. `latest` means highest installed Base build, not an online update
check; step 1 must have completed the Battle.net update. Human control remains
`not_verified`. An old game-data installation may still fail at launch/create.

## 6. Probe the real binary/API without starting a match

```powershell
uv run --locked sc2-assistant --probe --runtime-report logs/probe.json
if ($LASTEXITCODE -ne 0) { throw 'API probe failed; read logs/probe.json and logs/assistant.log.' }
Get-Content logs/probe.json
```

The launcher opens and then closes its own SC2 process. Expected report:
`phase: probe_ok`, with `ping.game_version`, `ping.base_build`, `ping.data_build`
and `ping.data_version`. It rejects a different binary from the one selected by
preflight. For explicit legacy versions it also checks the data hash. Keep the
full identity: a patch label alone is insufficient to reproduce a game.

If direct launching fails before API connection, use the attach alternative
below. A probe proves transport/version only, not map loading or human input.

## 7. Start a paused-assistant match and test human control

```powershell
uv run --locked sc2-assistant --map-file maps/BelShirVestigeLE.SC2Map --difficulty VeryEasy --opponent Terran --start-paused --runtime-report logs/first-play.json --replay replays/first-play.SC2Replay
if ($LASTEXITCODE -ne 0) { throw 'Match failed; preserve the report, log and replay if saved.' }
```

This command stays running until the game ends. Do not wait for the PowerShell
prompt before interacting with the game window. A foreground automation tool
should launch it as a long-running terminal task, then switch to the desktop.
The match clock runs normally; only assistant automation is paused.

In the SC2 window, perform these checks in order:

1. Select a Probe. Right-click a mineral patch and then a nearby ground location.
   Confirm the worker actually responds.
2. Click different locations on the minimap. Confirm the camera moves.
3. Select a Nexus, train a Probe using the command card, and try its configured
   train-Probe hotkey. Confirm it enters the queue when resources/supply permit.
4. Assign and recall a control group using your configured keys (normally
   Ctrl+1 then 1). Test camera movement and drag selection.
5. Press Enter, type `!assist status`, and press Enter again. Expect a reply
   containing `PAUSED`. Type `!assist resume` the same way.
6. Watch the assistant train workers/build supply. Select a worker and move it
   while automation runs; confirm your selection/camera remain yours.
7. Let production create combat units. Select them, assign a control group and
   issue move/attack orders while the economy continues. Confirm orders take
   effect and controls still work.
8. Type `!assist pause`; confirm new assistant orders stop (already queued
   orders may finish). Type `!assist resume` to continue.
9. Use the normal in-game menu to surrender/leave. Allow the terminal command to
   finish and save its replay. The directly launched SC2 process then closes.

**Fail immediately** if minimap interaction, command-card buttons, hotkeys, chat,
or manual orders do not work. Note whether the failure occurs with automation
paused, enabled, or both. A paused failure is not something to fix by changing
the economy policy. Do not mark the workflow compatible if only the bot works.

## 8. Record acceptance with reproducible evidence

In PowerShell, after the game exits:

```powershell
Get-Content logs/first-play.json
Get-Item replays/first-play.SC2Replay
Copy-Item docs/runtime-acceptance-template.md logs/runtime-acceptance.md
```

Fill `logs/runtime-acceptance.md` using observed results and exact identity from
the JSON report. An AI agent without desktop access must ask the human for the
listed observations and label them human-reported. A replay cannot prove that
mouse/keyboard controls worked. Do not turn failed or untested checks into pass.

Then complete [the functional live checklist](assistant-live-test.md), including
ability toggles. `phase: ended` says the match completed, not that all checks
passed. The machine report deliberately never claims human-control validation.
Logs/maps/replays are ignored by git; explicitly share selected artifacts when
reporting results. There is no automatic upload. Revalidate after game updates,
SDK/lockfile updates, interface changes or switching binaries/maps.

## 9. Normal subsequent startup

After the preceding checks pass for the installed build, use:

```powershell
$env:SC2PATH = 'C:\Program Files (x86)\StarCraft II'
uv run --locked sc2-assistant --map-file maps/BelShirVestigeLE.SC2Map --difficulty Medium --opponent Terran --config config/assistant.example.json
if ($LASTEXITCODE -ne 0) { throw 'Session failed; inspect the newest runtime report.' }
```

Run from the checkout root. Reports/replays use unique timestamps by default.
`--start-paused` is optional after validation. Chat commands include
`!assist economy off`, `!assist storm on`, `!assist feedback on`,
`!assist guardian_shield on`, `!assist blink on` and `!assist voidray_alignment on`.
Combat powers default off. See [README](../README.md) for production targets,
research requirements, unit release/claim and per-feature limits.

## Alternative A: launch from Battle.net, then attach

Use this only when direct process launch fails. It is an alternative process
startup path, not a known fix for disabled human controls.

1. Close SC2. In Battle.net, open StarCraft II's game settings.
2. Enable Additional command line arguments and enter:
   `-listen 127.0.0.1 -port 5001 -displayMode 0`.
3. Click Play. Leave the API client idle; do not create a match manually.
4. From the configured checkout/PowerShell session run:

```powershell
uv run --locked sc2-assistant --attach-port 5001 --probe --runtime-report logs/attach-probe.json
if ($LASTEXITCODE -ne 0) { throw 'Attach probe failed.' }
uv run --locked sc2-assistant --attach-port 5001 --map-file maps/BelShirVestigeLE.SC2Map --start-paused --difficulty VeryEasy --runtime-report logs/attach-play.json --replay replays/attach-play.SC2Replay
if ($LASTEXITCODE -ne 0) { throw 'Attached game failed.' }
```

The first command disconnects without quitting SC2. The second creates a new
local match, provided the API reports the idle `launched` state. It refuses an
active game/replay or another unexpected state. Verify controls using step 7.
On completion it leaves the match but does not quit/kill the attached process.
Close that SC2 instance yourself before a new attempt. Remove the Battle.net
API arguments before returning to ordinary game use. Never expose this port
beyond loopback. The attach path is implemented/tested with protocol doubles;
live Windows validation remains pending.

## Alternative B: explicitly installed legacy version

Only consider this after documenting a current-build failure. Upstream suggested
4.10 for the 5.0.x UI regression. This is not a promise that 4.10 is downloadable,
works with this assistant, or accepts the same maps. It has older gameplay/data.

If a legitimate 4.10 installation is already available:

```powershell
uv run --locked sc2-assistant --sc2-version 4.10 --probe --runtime-report logs/probe-4.10.json
if ($LASTEXITCODE -ne 0) { throw 'Legacy binary/data unavailable or mismatched. Stop here.' }
uv run --locked sc2-assistant --sc2-version 4.10 --map-file maps/BelShirVestigeLE.SC2Map --start-paused --difficulty VeryEasy --runtime-report logs/play-4.10.json --replay replays/play-4.10.SC2Replay
if ($LASTEXITCODE -ne 0) { throw 'Legacy match failed.' }
```

4.10 requires `Base75689` and data hash `B89B5D6FA7CBF6452E721311BFBC6CB2`.
The launcher refuses a missing binary or wrong returned data hash. It never
falls back to current retail. Old replay downloads have reported failures;
there is intentionally no unverified downgrade/install recipe here. If absent,
report the blocker and stop. Use `latest` again for the current retail route.

## Troubleshooting / agent decision table

| Observation | Next action / stop rule |
| --- | --- |
| Wrong OS/headless error | Run native Windows Python/PowerShell on the gaming desktop. |
| No executable / missing Support64 | Correct SC2PATH or repair/finish installation in Battle.net. |
| Unknown explicit version | Use `latest` for current retail; SDK version-label registry is older than current releases. Do not fabricate hashes. |
| SC2 exits before API / connection timeout | Finish normal first launch; check logs; try Alternative A once. |
| Connection refused on attach | Check API arguments/port and restart SC2; do not open public firewall ports. |
| Wrong binary/data in ping | Inspect selected and actual identity; close stale client and select correct installation/version. |
| Client not idle | Exit existing match/client yourself; restart an idle API client. Never force replacement. |
| CreateGame map/data error | Check verified map bytes, completed SC2 data install and game version; preserve server error details. |
| JoinGame / unknown unit or ability error | Stop and retain report/log; SDK/live-data compatibility needs investigation. |
| Probe works, controls disabled | Record a failed human-control test. No current-build compatibility claim; consider B only if already installed. |
| Bot commands rejected | Read action errors in assistant.log; distinguish missing resources/research from stale IDs. |
| Replay missing after crash/disconnect | Report replay_error; retain JSON/log. Do not claim a saved replay. |
| Manual abort | Prefer normal surrender; Ctrl+C is an emergency stop and may prevent replay saving. |

Exit codes: 0 means the requested preflight/probe/session operation completed;
2 means invalid arguments/config/install/map; 1 means a runtime failure; 130 is
an interrupted CLI session. None of these alone verifies human controls.

## Primary sources and evidence boundaries

- [Blizzard API overview](https://github.com/Blizzard/s2client-proto): explicitly lists tool-assisted human play.
- [InterfaceOptions](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto): `raw_affects_selection` explicitly discusses simultaneous human and agent play.
- [Protocol](https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md): WebSocket startup, local games, real-time mode and binary/data identity.
- [2026-10-08 protocol package update](https://github.com/Blizzard/s2client-proto/commit/4867bb9ede01e914c57a6fc9575dcc2f4bf0ca5a): 5.0.17.98310.0 version-string update, not proof of human-control testing.
- [BurnySC2 7.3.0](https://pypi.org/project/burnysc2/7.3.0/) and [pys2clientprotocol 1.0.2](https://pypi.org/project/pys2clientprotocol/1.0.2/): reviewed Python runtime dependencies.
- [BurnySC2 PR 213](https://github.com/BurnySc2/python-sc2/pull/213): 5.0.x UI regression report and version-selection workaround, merged June 2025; not a Blizzard fix.
- [Blizzard issue 208](https://github.com/Blizzard/s2client-proto/issues/208): Windows old-version download difficulties.
- [2026-09-18 third-party runtime procedure](https://github.com/golergka/jev-plays-starcraft-2/blob/main/docs/PROCEDURE.md): Battle.net + API attach tested on macOS; does not establish Windows shared human controls.
