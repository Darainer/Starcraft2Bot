# Install and play on Windows

Use native Windows PowerShell on the gaming PC. Run each stage separately;
**complete the manual steps before continuing**. AI agents follow the same stages
and report any manual handoff. Current retail is the first candidate; live human
control is still unverified. See [troubleshooting](windows-troubleshooting.md) for
compatibility evidence, alternatives and detailed agent/exit-code rules.

## 1. Get the project

Download and extract **Code -> Download ZIP** from
[the repository](https://github.com/Darainer/Starcraft2Bot), or clone it:

```powershell
git clone https://github.com/Darainer/Starcraft2Bot.git
cd Starcraft2Bot
```

For an existing checkout, open PowerShell in that folder. If script execution
is blocked, allow it for this terminal only: `Set-ExecutionPolicy -Scope Process Bypass`.

## 2. Install tools

```powershell
.\Setup.ps1 -Stage Tools
```

Installs **uv** if missing; Python is installed in the next stage. Existing uv
is reused. If installation fails, follow the printed error before proceeding.

**STOP:** after a new installation, close and reopen PowerShell, then return to
the project folder. Reboot Windows first if the installer requests it. Reapply
the process-only execution policy above if needed in the new terminal.

## 3. Install and initialize SC2 (manual)

Install [Battle.net](https://download.battle.net/), sign in, and fully install or
update StarCraft II. Launch it normally once, complete prompts, reach the main
menu, then **exit SC2**. Finish any requested restart before continuing.
Battle.net can stay open. Note the game's installation directory.

## 4. Set up the assistant

```powershell
.\Setup.ps1
```

Creates the locked Python environment, downloads/verifies an official test map,
checks configuration/game paths, and remembers paths locally. It does not start
a match. If your game isn't found automatically, rerun with its actual path:

```powershell
.\Setup.ps1 -Sc2Path 'D:\Games\StarCraft II'
```

Wait for **Setup complete**. Setup is safe to rerun after updates or a failed
attempt; it preserves custom settings and rejects a modified default map.

## 5. First game: check API, then manual controls

```powershell
.\Start.ps1 -Probe
```

Wait for successful completion. This opens and closes the script-owned SC2
client and records its actual version. If it fails, use
[troubleshooting](windows-troubleshooting.md) before proceeding.

```powershell
.\Start.ps1 -StartPaused -Difficulty VeryEasy
```

**Switch to the game window while the command stays running.** The game clock
runs; assistant automation starts paused.

1. Test worker selection/movement, minimap clicks, camera movement, unit-training
   buttons/hotkeys, and control groups.
2. In game chat, send `!assist status` (expect PAUSED), then `!assist resume`.
3. Confirm workers/buildings are produced while you can still command units;
   test army move/attack once troops exist. Send `!assist pause` to stop automation.
4. Surrender/leave through the game menu; wait for the script to finish saving
   the replay and closing its client.

If human controls fail, stop and record the failure. A successful API connection
is not acceptance. Complete [the acceptance record](runtime-acceptance-template.md)
using the JSON report/replay under `logs/` and `replays/`; never invent a pass.

## 6. Subsequent games

```powershell
.\Start.ps1
```

Uses the saved installation/map and starts automation against Medium Terran.
Automation defaults to on and the flashing debug overlay defaults to off.
Each match audits all assistant command mappings against the live game data
before automation starts, including optional spells. A failed audit stops startup
and lists the incompatible commands in the runtime JSON report. The report also
records exact game binary/data and Python package versions. Unknown observed order
IDs retain their identity without being treated as executable assistant commands.
This checks metadata compatibility; it does not prove command effects, tech
availability, or human controls. The API-only probe does not run the command audit.
For example: `./Start.ps1 -Difficulty Hard -Opponent Zerg`.
`!assist pause` / `!assist resume` control automation; spellcasters default off.
See [README](../README.md) for the individual toggles. Logs and replays are saved
automatically. Rerun setup after project dependency updates, and repeat manual
control checks after game updates.
