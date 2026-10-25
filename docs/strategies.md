# Tactical strategies and live state

The standard Windows config enables economy and attack automation, selects the
balanced setup and auto strategy, and hides the debug overlay. Existing running
games keep the code/settings they started with. Launch a new match to load changes.
Use `Start.ps1 -ManualArmy` or `!assist attack off` for manual army control.

## Launch variants

```powershell
.\Start.ps1 -Profile pressure -Strategy auto
.\Start.ps1 -Profile fortress -Strategy defend
.\Start.ps1 -Profile robotics -Strategy auto
.\Start.ps1 -Profile air -Strategy auto
.\Start.ps1 -Profile balanced -Strategy retreat
.\Start.ps1 -StrategyScript .\scripts\strategies\timing_attack.py
```

| Setup | Attack / continue army supply | Composition targets | Intent |
| --- | --- | --- | --- |
| balanced | 20 / 12 | 12 Zealots, 40 Stalkers, 6 Immortals | General purpose |
| pressure | 10 / 6 | 16 Zealots, 28 Stalkers, 2 Immortals, 2 bases | Earlier aggression |
| fortress | 50 / 30 | 8 Zealots, 32 Stalkers, 10 Immortals | More cautious engagements |
| robotics | 35 / 22 | 8 Zealots, 24 Stalkers, 8 Immortals, 3 Colossi | Ground tech |
| air | 24 / 16 | 8 Zealots, 12 Stalkers, 14 Void Rays | Air tech |

These are build targets subject to resources, tech and supply. Profiles also vary
health/strength retreat thresholds and rally distance. They preserve your optional
spell toggles. Switching a profile changes future build targets, not existing units
or queued production. Overrides in a JSON config take precedence over that config's
profile defaults; an explicit launch `-Profile` applies that profile's composition.

## Switch during play

Press Enter, type one command, then Enter again:

```text
!assist attack on
!assist strategy auto
!assist strategy defend
!assist strategy regroup
!assist strategy push
!assist strategy retreat
!assist profile robotics
!assist script scripts/strategies/counterattack.py
!assist script off
!assist pause
!assist resume
```

Auto prioritizes retreat when depleted/locally outmatched, then base defense,
then attacking above the profile's supply threshold, otherwise regrouping. A
lower continuation threshold avoids repeatedly switching an attacking army home.
Strength is a health-times-DPS heuristic, not a combat simulator. No terrain-aware
formation planner or full opponent model is claimed. Visible enemy buildings are
attack objectives; otherwise it checks the enemy spawn and then known expansion
locations. Retreat/regroup issue move orders; defend/push issue attack-move orders.
Nonattacking support units move with the group. Workers are never recruited.

### Scout, compose, assemble, advance, reinforce

Autonomous mode assigns one eligible Probe to scouting after reaching 16 workers.
That Probe is reserved from economic orders and returns after acquiring enemy
information or meeting a threat. Human selection/release still takes precedence.
Visible enemy combat composition can raise Stalker, Immortal or Colossus targets;
disable this with `!assist adaptive_composition off` to retain fixed targets.

An attack request now passes a separate **wave assembly gate**: at least 24 actual
combat-unit supply (or the profile's larger threshold), 8 units for pressure or
10 for other profiles, 80% of supply assembled near the rally point, and acquired
scouting information. Robotics requires a heavy unit; air requires four Void Rays.
Known enemy air also requires an anti-air component. Global supply and units still
in production do not satisfy these gates. Small forces wait rather than stream
individually toward the enemy.

Launched waves retain membership, move through common short waypoints, and wait
for stragglers when cohesion drops. Zealots occupy forward slots; ranged units
follow; support/casters take rear slots. Remote reinforcements assemble in groups
of at least six/12 supply before moving toward the core. Nearby safe arrivals can
join directly. Pause, selection and release still prevent new delegated orders.

Warpgate research and eligible Gateway conversion support reinforcement. A Warp
Prism follows behind a deployed wave, phases at a visible rear position, and
unphases/repositions when exposed to anti-air, damaged, or left behind. Warpgates
use queried available abilities and legal warp-in placement checks. Before Prism
deployment, safe home Pylons provide warp-in power so assembly does not deadlock.
Warp-ins explicitly debit live unit prices/supply and preserve resource reserves.
Queued warp-in orders are telemetry, not a count of confirmed completed units.

Use `!assist scouting off`, `!assist army_waves off`, or
`!assist warp_reinforcement off` to disable individual parts. Disabling waves
restores direct attack-move behavior and should be used deliberately. Movement
and warp positioning are heuristic; this is not a terrain-perfect formation or
transport-drop planner. The Prism is a mobile reinforcement platform, not a cargo
drop script. Wave, scouting and Prism phases are recorded with every snapshot.

Selection and explicit release exclude units from tactical orders. Use
`!assist release` to retain manual ownership after deselecting. Disabling attacks
or pausing stops new orders; already issued movement/attacks continue until you
override them. Combat spells remain separately opt-in.

## Local Python interface

The assistant owns SC2's API connection. External tools use a local, session-scoped
mailbox rather than trying to connect a second client. For the latest session:

```powershell
.\Control.ps1 -State
.\Control.ps1 strategy retreat
.\Control.ps1 profile pressure
.\Control.ps1 script scripts/strategies/timing_attack.py
.\Control.ps1 resume
```

Only one command may be pending; wait for `last_control_command` in the runtime
report before sending another. Commands normally apply on the next observation;
tactical orders are reevaluated at the next five-second sample. To address an
exact session, add `-Report logs/runtime-<session>.json`. A legacy running session
without the mailbox is explicitly rejected. A queued command is not proof of
execution. This local interface has the same command validation and ownership
rules as in-game chat, including selected-unit release/claim.

Equivalent Python commands (use the project's `.venv` interpreter):

```powershell
python -m source.control_cli --report logs/runtime-<session>.json --state
python -m source.control_cli --report logs/runtime-<session>.json strategy push
```

## Full observed state

Every five wall-clock seconds, after a fresh observation, the runtime appends
`logs/runtime-<session>.state.jsonl`: the full API `ResponseObservation` as
protobuf JSON, with captured time, game loop, chosen strategy, reason, inputs,
target and newly queued unit orders. This includes observed units/buildings and
their raw orders, health, shields, energy, positions, resources, supply, upgrades,
effects, visibility grids, selection and observed events. Large tags retain their
protobuf string representation. Absent optional fields remain absent.
Each sample also batches a resource-aware availability query for every owned
unit/building, preserving raw ability IDs. This is queried immediately after the
observation, rather than an atomic snapshot of both responses. Settings,
released tags and accumulated observed action rejections accompany the sample.

Static ability/unit/upgrade data is saved once as `.game-data.pb`; map metadata,
terrain/pathing/placement grids and player setup as `.game-info.json`. The runtime
report carries exact game binary/data identity, package versions and compatibility
results. Snapshots obey fog of war and contain no omniscient enemy resources or
hidden units. They are sampled states, not a lossless stream of every event between
samples; the replay is the separate match record. Sampling can be delayed by a
busy frame or game pause. Files remain local and are ignored by Git.

## Inject a Python strategy

A script reads one JSON object from stdin and prints exactly one JSON plan:

```python
import json
import sys

context = json.load(sys.stdin)
state = context["situation"]
strategy = "defend" if state["base_threat"] else "regroup"
print(json.dumps({"strategy": strategy, "reason": "Protect home"}))
```

Input contains `schema_version`, the full player `observation`, summarized
`situation`, raw `available_abilities`, profile thresholds, and `previous_strategy`. Output accepts
`strategy` (defend/regroup/push/retreat), `reason` (up to 500 characters), and an
optional `target: [x, y]` within the playable map. The script overrides the selected
built-in strategy until disabled. It cannot submit arbitrary SC2 orders through
this plan contract. Use stderr for debugging. Script processes execute local
Python code with normal user permissions; this is not a sandbox.

Each evaluation launches a fresh process with a one-second timeout, so edits
are loaded on the next sample. State that must persist is provided in context
or must be explicitly stored by the script. Failures, invalid output and out-of-map
targets produce a diagnostic and no new tactical orders for that sample; economy
automation continues and existing unit orders are not cancelled. Script path and
SHA-256 are recorded with the plan. Three executable examples are included:

- `timing_attack.py`: six-minute army timing with defense/retreat overrides.
- `counterattack.py`: repel a raid, then counterattack while army supply permits.
- `conservative.py`: require a large, healthy force before pushing.

## Autonomous test analysis

```powershell
.\Control.ps1 quit
python -m source.analyze_session logs/runtime-<session>.json
python -m source.trials --profiles pressure balanced --difficulty Easy --duration 600
python -m source.trials --profiles robotics air --difficulty Medium --duration 900 --repeat 2
```

The quit command saves a replay before leaving the match. The analyzer reports
sampled build milestones, completed upgrades, composition, resources, strategy
history and the recorded result. A deliberately stopped test records a defeat;
it is not evidence that the opponent defeated the bot.

The trial runner launches owned local clients sequentially, with bounded game
durations, snapshots and replays per trial. It records the comparison in
`logs/latest-trials.json`. Do not run it concurrently with a match you want to keep.
By default it uses accelerated non-real-time API games; snapshots and tactical
decisions then use five **game** seconds and micro uses half a game second.
Add `--realtime` to watch at normal speed. A time-limit result is not a win.
Single-game CLI equivalents are `--fast-test --game-time-limit 600`.

Building placement reserves two-tile aisles, mining routes and production exit
corridors, and checks nearby ground connectivity before placing structures. It
aligns odd-width buildings to half-tile centers so spacing can coexist with
pylon power. These conservative constraints can reject cramped layouts; they
are not a guarantee against every terrain/unit collision. A rejected production
spawn backs off for 15 game seconds instead of retrying every macro tick.
Workers are chosen again at the final placement and checked for a path before
receiving a build order. Accepted footprints are reserved while workers travel,
so another planned building cannot claim the same space before construction starts.

Production rotates between Gateway, Robotics and Stargate classes instead of
letting the first class starve the others. High-tech setups scale Robotics
facilities and Stargates with composition/base count, and larger armies add
parallel Forges for research.

Research periodically takes precedence over additional production buildings.
Ground weapon/armor/shield and air weapon/armor chains support levels 1–3; tech,
resources, selection, reserves and ability availability still gate research.
Between five-second strategic decisions, micro checks every half second for
critical-health retreats, visible in-range focus fire and pathable kiting against
shorter-range ground threats. These orders retain the same ownership rules and
are disabled when a strategy script fails or attack control is off.

Startup checks metadata mappings, including movement and attack commands. The
test suite exercises strategies, scripts, bounds, ownership and snapshot cadence
without launching SC2. New tactics still require live acceptance on your installed
game version; passing these tests does not establish tactical quality.
