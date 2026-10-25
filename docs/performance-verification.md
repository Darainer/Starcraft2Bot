# Performance verification — 2026-10-25

**Status:** tactical CPU cost measured on recorded retail observations; new match
performance remains unverified because SC2 exits before API startup in the agent's
Windows session. No new wins, losses, or win-rate improvement are claimed.

## Live attempt

Attempted pressure versus VeryHard Terran on Bel'Shir Vestige LE, bounded to
1,500 game seconds with eight game loops per observation. Installation/map
preflight passed. The installed binary is Base98310; no older binary was selected.

SC2 exited before the API connection with code **536936448 (0x20010000)**. The
runtime report records `phase: failed`, not a match result. No current ping identity,
game observations, or replay were produced. Loopback bind/connect testing passed.
The execution account is the isolated Codex sandbox account, and no fresh normal
game log appeared in the user's game-log directory. Those facts do not establish
the precise cause of the native exit.

The next live attempt requires launching from the user's normal desktop account.
The existing Python environment and trial runner are ready; no dependency change
or reinstall was made. Human input acceptance remains separate, under the
[Windows runbook](windows-install-and-play.md).

Local diagnostics are in `logs/performance-pressure-terran-01.json` and its `.log`.
Logs and personal installation paths remain uncommitted.

### Comparison with the successful session

The pre-overhaul commit `f55dc1b` was checked out separately and launched with the
same existing interpreter and installed binary. Its API probe failed with the
same `536936448` exit before connecting; the current branch was left intact.
The `LocalProcess`, `connection`, and `run_session` implementations are unchanged
between that commit and this branch, as verified by comparing their parsed code.
The CLI, launcher scripts and dependency pins are also unchanged.

The earlier successful Codex session used the same `.venv` interpreter and
`source.trials` entry point. Its recorded execution context was
`danger-full-access`; this session's attempted launches ran as the restricted
`codexsandboxoffline` account. This isolates the failure from the tactical-code
changes and identifies an execution-context difference worth correcting first.
It does not identify the exact internal SC2 failure behind that native exit code.

After the user enabled Full Access, the immediate retry still reported the
restricted account and failed before API connection. The effective command
runner must reflect the permission change before further live testing. This
requirement is now recorded in [AGENTS.md](../AGENTS.md).

## Retail-observation verification

Commit `f9e07fe` adds a controller benchmark that reconstructs real SDK observations
from saved game data, map metadata, and sampled player observations. It creates no
client or network connection. Recorded script paths are disabled; proposed orders
stay in memory and are discarded before the next observation.

The first reconstruction exposed a startup regression: retail unit metadata
contains ID **2005**, which is absent from the pinned SDK's `UnitTypeId` enum.
Converting every metadata key to that enum raised `ValueError`. Supply metadata
now retains integer IDs, while action capabilities still use supported SDK IDs.
A startup regression test covers unknown metadata IDs.

The full command-mapping audit also passed against each of the six saved retail
metadata files, including the new upgrade requests. This verifies metadata
compatibility for those recordings, not current command effects or availability.

After that fix, all six saved VeryHard recordings processed successfully over
three independent passes each:

| Recording suffix | Snapshots/pass | Maximum observed player units | Total p50 | Total p95 | Total max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `182811-418416` | 184 | 217 | 1.281 ms | 5.317 ms | 29.930 ms |
| `182708-927536` | 138 | 156 | 0.874 ms | 2.581 ms | 5.883 ms |
| `182636-231827` | 75 | 56 | 0.553 ms | 1.171 ms | 1.718 ms |
| `174432-935499` | 152 | 246 | 0.956 ms | 3.854 ms | 29.880 ms |
| `174001-194780` | 160 | 165 | 0.980 ms | 3.280 ms | 13.938 ms |
| `173456-303449` | 218 | 240 | 1.202 ms | 9.064 ms | 28.921 ms |

Recording names have the prefix `runtime-20261025-` under `logs/`. Results are
saved locally in `logs/controller-performance.json`.

There were **927 distinct snapshots, 2,781 controller evaluations, and 30,972
proposed orders**, with **zero duplicate-actor or selected/released-actor order
violations**. Maximum observed player units counts our units/buildings plus known
enemy units/buildings; it is not a combat-army count.

These measurements include scouting, tactical assessment/planning/mission
execution, and the subsequent micro pass. They exclude protobuf reconstruction,
serialization, macro queries, game execution, network latency, and rendering.
Orders proposed by an earlier stage also retain priority over the micro stage,
as in the live controller. The per-recording p95 totals were 1.17–9.06 ms and the
largest measured total was 29.93 ms. This indicates CPU headroom on these samples;
it does not certify a frame budget for every possible game state.

All recordings come from pre-overhaul defeats. Their action effects remain those
of the original games: the benchmark does not replay our proposed orders into a
simulator. Their coarse sampling misses intervening fights, and map pathing is
static during reconstruction. Thus these measurements cannot establish better
opening timings, economic damage, good trades, live response latency, or wins.

Example reproduction for one recording:

```powershell
.\.venv\Scripts\python.exe -m source.benchmark_controllers logs/runtime-20261025-182811-418416.json --repeat 3 --output .local/controller-timing.json
```

Pass several report paths to benchmark the full group. Each report requires its
matching `.game-data.pb`, `.game-info.json`, and `.state.jsonl` files.

## Regression checks

After the metadata fix and benchmark addition, **277 tests passed with 91.28%
combined statement/branch coverage**. Ruff lint, formatting, and the existing
mypy scope passed. These checks used the existing environment; the locked/build
limitations in the [implementation record](overhaul-validation.md) still apply.

```powershell
.venv/Scripts/python.exe -m pytest --cov --cov-report=term-missing -q -p no:cacheprovider --basetemp .local/pytest-performance-verification
```

## Bounded live batch prepared

From normal PowerShell in the repository:

```powershell
.\.venv\Scripts\python.exe -m source.trials --profiles pressure balanced --repeat 3 --difficulty VeryHard --opponent Terran --fast-step-size 8 --duration 1500
```

This schedules three games per profile, saves individual runtime reports/replays,
and updates `logs/latest-trials.json`. Eight loops correspond to approximately
0.357 game seconds per observation; this improves resolution over the former
32/64-loop trials but cannot verify the configured 0.125-second micro cadence.
Four-loop and real-time follow-ups are needed for finer reaction measurements.
Three games per profile are a smoke comparison, not a precise win-rate estimate.
No fixed-seed or opponent-build matching is claimed by this command.

After the batch starts, inspect startup errors, first Stalker and pressure timing,
supply blocks, idle production, resources, mission aborts and the recorded result.
Review replays for actual fights and economic damage. Expand to repeated matched
baseline trials and other opponent races once startup and basic play succeed.
