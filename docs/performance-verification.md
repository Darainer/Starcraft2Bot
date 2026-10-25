# Performance verification — 2026-10-25

**Status:** Full Access resolved the native startup blocker. Independent SC2
instances can run concurrently, with separate API ports, runtime reports, logs
and replays. Four initial matches finished: pressure won one of two; balanced lost both.
The subsequent loss-counter-only pair also lost. The expansion-denial revision finished its initial three-game batch at one win
and two losses. The user requested fixed starting conditions and a broader
30-game matrix; the runner now supports those controls. These early results are
smoke tests, not a reliable win-rate estimate.

## Live environment and initial results

Initial live implementation: `05f3b5c`, branch `feat/adaptive-pressure-tactics`.
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
| Pressure 02 | Defeat | 1320.4 s | 275.4 s | 190.4 s | 10 s | 4.916 ms |
| Balanced 02 | Defeat | 1095.4 s | 330.4 s | 195.4 s | 90 s | 4.337 ms |

Local evidence uses `logs/performance-v1-<profile>-terran-<01|02>.json`, its matching
`.state.jsonl`/metadata files and `.log`, and
`replays/performance-v1-<profile>-terran-<01|02>.SC2Replay`. Logs and replays remain
uncommitted. The displayed duration is the last five-second observation sample,
not an exact end-of-match timestamp. Sampled tactical timings exclude macro/API
latency and run under concurrent game load.

The pressure game reached 56 workers and sustained a growing army. The balanced
loss included repeated defensive withdrawals, then a collapse from 96 assigned
combat supply around 795 seconds to six around 825 seconds while returning to
defend. That identifies defensive transitions and retreat routes for investigation;
it does not establish a single cause from sampled observations. Neither first
match recorded action rejections. The second pressure game recorded one rejected
attack request; the second balanced game recorded one rejected attack and one
failed warp-in placement. The current bot does not consistently beat VeryHard.

Human input acceptance remains separate and unverified under the
[Windows runbook](windows-install-and-play.md). Autonomous games verify API
startup and gameplay, not keyboard/mouse sharing.

### Loss-score correction found during live verification

In balanced run 02, the reported army-loss total had reached 1,625 resources,
then temporarily fell below that value. At sampled times 555-565 seconds it was
1,250, 1,450 and 1,550, yet `trade_bad` was true. The director was treating a
rebound below the previous maximum as fresh losses. Negative totals earlier in
matches also demonstrate that this field is not a monotonic casualty counter.

The assessment now retains the highest cumulative loss value seen and measures
recent increases against that value. Its regression test verifies that a score
rebound keeps pressure active, while 350 genuinely new reported losses still
trigger recovery. This fixes false retreats without changing force thresholds.
It remains an estimate: actual losses can be recognized late while the raw total
is below its previous maximum. Terrain, retreat routes and defensive commitment
still need broader evaluation; this correction does not solve those problems.

### Follow-up revision and batch protocol

The loss-score-only revision `66dd9c0` completed one pressure and one balanced
match before the user requested the three-game protocol. Both lost: pressure at
last sample 1,035.4 seconds and balanced at 335.4 seconds. Neither recorded action
rejections. These two games cannot establish the correction's effect on win rate;
opponent builds were not matched. Evidence is under
`performance-v2-<profile>-terran-01` in the local logs/replays directories.

The expansion-denial revision changes site inspection scheduling, stable base
identity through fog, expansion priority and small-squad eligibility. **284 tests
passed with 91.58% coverage**; locked sync, lint, formatting, mypy and package
build all passed. Reconstructing both initial pressure recordings processed 417
snapshots and proposed 6,858 orders without duplicate/ownership violations.
Controller total p95 was 7.853 and 12.243 ms; the largest sample was 71.458 ms.
These are offline CPU costs, not game response times or simulated match outcomes.

From this revision onward, run **three concurrent pressure-versus-VeryHard-Terran
games per gameplay change**, with the same map and eight-loop step size. Freeze
the committed gameplay code for the complete batch, assess all three outcomes,
and only then tune again. This is recorded in [AGENTS.md](../AGENTS.md). Each game
gets its own report, log and replay. The follow-up runner adds internal bounded
concurrency and unique outputs for every game.

Expansion metrics distinguish Observer travel, inspected sites, known enemy
expansions, an advancing force assigned to an expansion, and allocated denial
squads. They measure selected behavior; they do not certify economic damage.

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

After the metadata fix and benchmark addition, the fresh locked suite passed
**277 tests with 91.28% combined statement/branch coverage**. Full Access also
allowed `uv sync --locked`, locked Ruff lint/formatting, locked mypy and `uv build`
to pass. The package produced both wheel and sdist without changing pins.
After the loss-score correction, **278 tests passed with 91.29% coverage**;
locked lint, formatting, mypy and package build passed again.

```powershell
uv run --locked pytest --cov --cov-report=term-missing -q -p no:cacheprovider --basetemp .local/pytest-full-access-verification
```

## Expansion-denial batch and fixed-condition matrix

Gameplay revision `d48a8fb` completed three concurrent pressure games without a
runtime failure. This batch still used random builds and seeds, so it is kept
separate from the controlled evaluation requested afterward.

| Run | Result | Last sampled time | First expansion advance | Inspected sites | Expansion target samples | Denial squad samples |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 01 | Defeat | 1215.4 s | 335.4 s | 8 | 38 | 0 |
| 02 | Victory | 1215.4 s | 320.4 s | 8 | 56 | 2 |
| 03 | Defeat | 1065.4 s | 350.4 s | 8 | 27 | 0 |

Evidence is `performance-v3-pressure-terran-<01|02|03>` under local logs/replays.
All three inspected expansions and assigned advancing forces to them. Side raids
were rare; the main force did most expansion pressure. This demonstrates selected
behavior, but does not establish an improved win rate or sustained economic denial.

The runner revision passed **294 tests with 91.75% coverage**, locked sync,
lint, formatting, mypy and package build. Protocol tests verify that the fixed
seed and selected AI build reach SC2's serialized create-game request. Concurrency
tests require three simultaneous workers and isolated output paths.

The next matrix keeps the gameplay implementation unchanged and fixes SC2's seed,
Python's random/hash seeds, race/build, map, profile, step and duration. It checks
loop-zero fingerprints of starting player state, units/positions, settings and
scenario metadata. Protocol tags and timestamps are excluded. Hidden opponent
units are never queried. A mismatched or missing initial fingerprint stops the
matrix rather than silently comparing unlike starts.

```powershell
uv run --locked python -m source.trials --profiles pressure --opponents Terran Zerg --builds Rush Timing Power Macro Air --repeat 3 --parallel 3 --difficulty VeryHard --seed 20261025 --fast-step-size 8 --duration 1500 --output logs/expansion-matrix-fixed.json
```

This is ten explicit scenarios, each repeated three times with the same seed.
It checks repeatability across 30 games, not 30 independent random scenarios.
All three repeats complete before the runner starts the next build. The gameplay
code stays frozen for the entire matrix. Future comparisons should reuse exactly
these settings and report results per race/build rather than combine revisions.

The installed Windows retail client is retained. Blizzard documents its separate
[headless Linux packages](https://github.com/Blizzard/s2client-proto#linux-packages);
PySC2's [Windows launch path](https://github.com/google-deepmind/pysc2/blob/master/pysc2/lib/sc_process.py)
uses a window. No alternate binary, platform migration or headless claim is made.
The user explicitly allowed the working windowed setup.

Eight loops are approximately 0.357 game seconds per observation. They improve
resolution over 32/64-loop trials but cannot verify the 0.125-second micro cadence.
Human input acceptance remains separate. All reports and replays stay local.
