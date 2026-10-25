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
| pressure | 10 / 6 | 16 Zealots, 28 Stalkers, 2 Immortals, 3 bases, 56 worker cap | Earlier aggression with sustained production |
| fortress | 50 / 30 | 8 Zealots, 32 Stalkers, 10 Immortals | More cautious engagements |
| robotics | 35 / 22 | 10 Zealots, 28 Stalkers, 8 Immortals, 4 Colossi, 3 bases, 56 worker cap | Larger ground-tech army |
| air | 24 / 16 | 8 Zealots, 12 Stalkers, 14 Void Rays | Air tech |

These are build targets subject to resources, tech and supply. Profiles also vary
health retreat thresholds and rally distance. They preserve your optional
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

Auto uses a shared game assessment to choose and combine operations: develop,
stabilize, pressure, contain, counterattack, recover, and finish. Profiles set
composition and risk preferences. The director ranks visible economic targets,
travel cost, evidence age, local strength, and recent upgrades. It retains a
reasonable choice for eight game seconds, interrupts for danger, and avoids a
failed target for 30 seconds. These are tunable heuristics, not calibrated win
probabilities or a claim of professional-level play.

A plan can combine main-army pressure with a small home response or a separate
expansion-denial squad. All missions share a force budget and have disjoint actor
assignments. A home response requires credible local strength; denial requires a
currently visible expansion, at least 32 total combat supply, and a six-supply
minimum detachment. The detachment uses at most 12 supply or one quarter of the
army, prefers Zealots/Stalkers, and leaves heavy units with the main force. Light
guards can be challenged when their supply is at most half the raid budget and
the observed force comparison is favorable; static defenses prohibit a side raid.
Local fight checks can still abort it. A failed raid recovers independently. Losing
the main force causes a global reassessment and cancels exposed side operations.
Manual strategies and script targets take precedence over automatic missions.

### Scout, compose, assemble, advance, reinforce

An eligible Probe scouts the enemy natural and main after 12 workers, then
returns to mining. The reserved scout cannot receive economy orders. An Observer
prioritizes overdue expansion inspections: occupied sites become due after 20
seconds without vision, empty/unknown sites after 45. It finishes its selected
inspection, favors likely enemy expansion locations and previously occupied
sites, and backs off a threatened route for 30 seconds while checking others.
These are scheduling targets, not guaranteed revisit intervals. When inspections
are current it checks home approaches or the main mission's route. It withdraws
from observed anti-air or serious damage.
Selection and release retain human ownership of both scouts.

Enemy unit memory is keyed by tag, drops observed deaths, and expires after 90
game seconds. Base and tech memory expire after 180 seconds; visible empty base
sites are removed immediately. Strategic base targets use at most 90 seconds of
memory. Visible and remembered bases retain the same target identity. Expansions
receive higher target priority than the main base; unfinished bases and nearby
workers increase the opportunity value. Remembered defenders remain a reason to
rescout. Recently inspected empty sites do not attract an army. Fog targets are
reconnaissance opportunities, never confirmed free bases.
Air-heavy armies raise Stalker targets; armored air adds Void Rays. Armored ground
raises Immortal demand; light ground adds Colossi/Zealots. These temporary targets
preserve configured values and expire with their evidence. Use
`!assist adaptive_composition off` to restore fixed production targets.

Wave launch requires at least **max(16, profile attack supply)**, six combat units
for pressure or eight for other profiles, and 80% assembly near the rally point.
Robotics requires a heavy unit; air requires four Void Rays. Recent substantial
enemy air requires an anti-air component. Scouting gates the opening, with a
120-game-second timeout to avoid indefinite waiting. Difficulty no longer adds
40-96 supply gates. Actual eligible units determine readiness. Global supply,
selected units, and unfinished units cannot satisfy it. Active pressure uses the
lower profile continuation threshold, with an eight-supply floor in the director.

Cohesive waves advance through short common waypoints. Zealots lead, ranged units
follow, and support stays behind. Remote reinforcements gather in groups of six
and 12 supply; nearby arrivals can join directly. Main pressure may contain outside
known weapon ranges while a bounded detachment attacks an exposed expansion.
Recovering squads move toward the safest current base. Cleanup dispersal requires
strong recent winning trades and fresh evidence of a depleted opposing army;
few visible buildings alone are insufficient.

Fight assessment compares nearby health/shields and target-compatible DPS,
including visible defensive structures and conservative Bunker occupancy. It
cannot model every spell, terrain feature, or hidden reinforcement. Micro focuses
reachable targets, reduces obvious overkill, kites shorter-range threats during
weapon cooldown, and resumes firing afterward. Matching standing orders are kept.
Critical units withdraw individually. Spells remain individually opt-in.

### Economy and reinforcement

Opening spending prioritizes a Gateway and Cybernetics Core, gas, early combat
units, then a supportable natural. Further bases require workers and protection;
configured base/worker ceilings remain authoritative throughout the game.
Emergency production comes before new investment, while recovery still permits
workers and gas. Unsafe bases and expansion sites are avoided.

Supply buffers scale with bases and production capacity, from four to 20 supply,
and count pending Pylons. Macro does not build to 200 simply because three bases
exist. Production rotates across Gateway, Robotics, and Stargate facilities and
balances unit deficits against composition targets. Infrastructure scales with
bases and mineral availability; upgrades get periodic spending opportunities.
Charge and Thermal Lance are considered when the army needs them. Ground and air
upgrade chains and all existing spell opt-ins remain available.

Warpgate research/conversion and legal warp-ins support reinforcement. A Prism
follows behind the main wave, phases at a visible rear position, and moves or
unphases when exposed. It remains responsive even when macro has spent that tick.
Safe home Pylons provide power before deployment. Warp-ins use queried abilities,
legal placement, live costs, user reserves, and macro reservations for expansion, critical supply, and opening tech.
Issued warp-ins are requests, not confirmed completed units. Rejected locations
back off rather than being retried continuously.

`!assist scouting off`, `!assist army_waves off`, and
`!assist warp_reinforcement off` disable individual controllers. Disabling waves
uses direct mission movement. The Prism is a reinforcement platform; transport
drop juggling and additional spell controllers are outside this baseline.

### Control cadence

| Work | Game-time interval, subject to fresh observations |
| --- | --- |
| Ownership, commands, action errors | Every observation |
| Combat micro | 0.125 seconds |
| Macro and reinforcement | 0.25 seconds |
| Assessment, scouting, mission execution | 1 second; settings changes immediately |
| Director | 2 seconds; material changes or invalid plans immediately |
| Full snapshots | 5 seconds: wall time in real-time games, game time in fast tests |

All orders pass through the existing ownership and resource-accounting boundary.
An actor receives at most one assistant order per observation. Assignment changes
revoke old movement intents; expired, unsupported, or out-of-map intents are
rejected. Selection/release and pause prevent new orders. Existing orders continue
until replaced by the player or a later permitted command.

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
settings changes trigger tactical reevaluation on that observation. To address an
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
`situation`, raw `available_abilities`, profile thresholds, `previous_strategy`,
and the immutable `assessment`. Output accepts
`strategy` (defend/regroup/push/retreat), `reason` (up to 500 characters), and an
optional `target: [x, y]` within the playable map. The script overrides the selected
built-in strategy until disabled. It cannot submit arbitrary SC2 orders through
this plan contract. Use stderr for debugging. Script processes execute local
Python code with normal user permissions; this is not a sandbox.

Scripts are evaluated at most every five game seconds, or when their file changes.
Each evaluation launches a fresh process with a one-second timeout. The last valid
result is reused between evaluations. State that must persist is provided in context
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
python -m source.trials --profiles robotics --difficulty Hard --duration 1500
```

The quit command saves a replay before leaving the match. The analyzer reports
sampled build milestones, completed upgrades, composition, resources, strategy
history and the recorded result. A deliberately stopped test records a defeat;
it is not evidence that the opponent defeated the bot.

The trial runner launches owned clients with bounded game duration and saves
separate reports, logs and replays. `--parallel 3` runs three repeats of a scenario
concurrently before starting the next scenario when `--repeat 3` is selected.
`--parallel 5 --repeat 3` overlaps scenarios, with at most five clients active and
three repeats of every scenario. Results include wall time and simulation throughput.
`--opponents` and `--builds` expand
the matrix; `--output` chooses its aggregate JSON. Use `--seed` and an explicit
build to fix SC2/Python randomness. Seeded scenarios must have matching loop-zero
starting-state fingerprints or the runner stops. The default remains sequential.

```powershell
python -m source.trials --profiles pressure --opponents Terran Zerg --builds Rush Timing Power Macro Air --repeat 3 --parallel 3 --seed 20261025 --difficulty VeryHard --fast-step-size 8 --duration 1500 --output logs/expansion-matrix-fixed.json
```

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
Between strategic decisions, micro checks every 0.125 game seconds for
critical-health retreats, visible in-range focus fire and pathable kiting against
shorter-range ground threats. These orders retain the same ownership rules and
are disabled when a strategy script fails or attack control is off.

Startup checks metadata mappings, including movement and attack commands. The
test suite exercises strategies, scripts, bounds, ownership and snapshot cadence
without launching SC2. New tactics still require live acceptance on your installed
game version; passing these tests does not establish tactical quality.

## Offline director inspection and future models

```powershell
python -m source.replay_strategy logs/runtime-<session>.state.jsonl --output .local/policy-review.json
```

This runs saved assessments through the hard-coded director without opening SC2
or issuing actions. Legacy samples without assessments are counted and skipped.
It supports decision comparison, not counterfactual match simulation.

The session analyzer now reports sampled supply-block and idle-facility seconds,
resource-bank statistics, first offensive advance, controller time, objective
counts, and deduplicated mission outcomes. Idle facility seconds sum idle ready
Gateway/Robotics/Stargate time; they exclude Warpgates because absence of an order
does not establish cooldown readiness. Sampled estimates can miss intervening
changes. Controller times measure the control hook, excluding full serialization.

`StrategicPlan` and `Assessment` are independent of SC2 and model providers.
`DeferredPolicy` provides one bounded asynchronous request at a time, timeout,
request count limits, cancellation, and validation on arrival. No model service
is configured. Later LLM-PySC2-inspired experiments can replace observation,
planning, or specialist execution boundaries after shadow evaluation. See the
[architecture plan](tactical-architecture-plan.md) and
[implementation validation record](overhaul-validation.md).

For tactical CPU measurements on saved raw observations, use
`python -m source.benchmark_controllers logs/runtime-<session>.json --repeat 3`.
This requires the matching metadata/snapshot files and never connects to SC2.
See [performance verification](performance-verification.md) for measured results
and the distinction between CPU cost and live gameplay performance.
