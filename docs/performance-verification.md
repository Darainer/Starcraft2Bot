# Performance verification — 2026-10-25

**Status:** Full Access resolved the native startup blocker. Independent SC2
instances can run concurrently, with separate API ports, runtime reports, logs
and replays. The first pressure match beat VeryHard Terran; the first balanced
match lost. Further repetitions are in progress. These are smoke results, not a
reliable win-rate estimate.

## Live environment and initial results

Current implementation: `05f3b5c`, branch `feat/adaptive-pressure-tactics`.
Opponent: VeryHard Terran. Map: Bel'Shir Vestige LE. Fast stepping: eight loops
(approximately 0.357 game seconds per observation), bounded to 1,500 game seconds.
Optional combat spells remain disabled. No fixed seed or opponent build matching
is claimed. Two concurrent matches successfully completed and saved replays.

Exact live ping identity:

- Game version: `5.0.17.98310`
- Base/data build: `98310` / `98310`
- Data version: `9C1F3D3D30CA252E33FC67CA05CBE1EA`
- Map SHA256: `9cb078a287c76c0b55e3bc137b0e4590415231367d7c5724ab1bfd24a06a1d1e`
- Startup command audit: 59 commands, zero failures in both matches.

| Profile/run | Result | Last sampled game time | First offensive advance | First completed Stalker | Supply block estimate | Sampled tactical p95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Pressure 01 | Victory | 755.4 s | 290.4 s | 200.4 s | 5 s | 4.110 ms |
| Balanced 01 | Defeat | 970.4 s | 340.4 s | 190.4 s | 25 s | 3.583 ms |

Local evidence uses `logs/performance-v1-<profile>-terran-01.json`, its matching
`.state.jsonl`/metadata files and `.log`, and
`replays/performance-v1-<profile>-terran-01.SC2Replay`. Logs and replays remain
uncommitted. The displayed duration is the last five-second observation sample,
not an exact end-of-match timestamp. Sampled tactical timings exclude macro/API
latency and run under concurrent game load.

The pressure game reached 56 workers and sustained a growing army. The balanced
loss included repeated defensive withdrawals, then a collapse from 96 assigned
combat supply around 795 seconds to six around 825 seconds while returning to
defend. That identifies defensive transitions and retreat routes for investigation;
it does not establish a single cause from sampled observations. Neither first
match recorded action rejections. Repetitions are needed before profile selection
or a claim that the bot consistently beats VeryHard.

Human input acceptance remains separate and unverified under the
[Windows runbook](windows-install-and-play.md). Autonomous games verify API
startup and gameplay, not keyboard/mouse sharing.

### Resolved permission blocker

The restricted Codex account exited SC2 before API connection with
`536936448` (`0x20010000`). The pre-overhaul commit `f55dc1b`, launched separately
with the same interpreter and binary, failed identically. Parsed comparisons
showed `LocalProcess`, `connection`, and `run_session` unchanged; the CLI, launcher
scripts and dependency pins were also unchanged.

The earlier successful Codex session used `danger-full-access`. The first retry
after user approval still ran under `codexsandboxoffline`; once the permission
change reached the actual runner and it used the normal desktop account, both
current games launched and finished. No launch-code workaround or downgrade was
needed. [AGENTS.md](../AGENTS.md) records the required execution context and says
not to request permission again after the user has approved it.

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
