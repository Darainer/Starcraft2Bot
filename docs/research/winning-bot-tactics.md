# Winning bot tactics and reusable opponents

Research date: 2026-10-31. This is a research and experiment plan for the Python
hardcoded bot. It does not promote a gameplay candidate, certify elite strength,
or report a newly executed match. Live improvement work continues separately.
The [hardcoded milestone](../hardcoded-elite-milestone.md) requires built-in AI
reliability first and established community opponents afterward. The separate
[RL architecture](../rl-architecture.md) remains a later stage.
The [training and environment plan](../rl-training-plan.md) explains how to use
our accepted bot and isolated public bots for collection, training and evaluation.

## What the current failures imply

The [Robotics v2 matrix](../evaluations/2026-10-31-robotics-fund-v2-20261031-complete.md)
finished at 18 wins and 12 defeats. Earlier Robotics repaired Zerg Timing but
regressed other conditions. [Counter-tech funding](../evaluations/2026-10-31-counter-tech-v1-20261031-terran-rush.md)
then won Terran Rush 3/3; its [Terran Timing](../evaluations/2026-10-31-counter-tech-v1-20261031-terran-timing.md)
and [Zerg Macro](../evaluations/2026-10-31-counter-tech-v1-20261031-zerg-macro.md)
triplets still lost. Funding a requested counter is necessary in those recordings,
but constructing it does not establish that it reaches or wins the fight.

The local source review identifies three separate problems to test:

1. `ArmyWaves` recognizes engagement when an attacking enemy is within ten of the
   median army position. Long-range weapons can already reach forward units before
   that condition. Ordinary advance destinations account for terrain but do not
   minimize enemy weapon exposure.
2. `combat_assessment.power` weights current HP by average legal-domain DPS.
   Friends within twenty of the squad anchor can receive full credit despite
   distance, blocking, range, or unsuitable targets. Splash, attribute bonuses,
   armor, healing and firing participation are not modeled. This is a heuristic,
   not a prediction of a positioned battle.
3. A third-base worker threshold can exceed the worker-production target after
   mineral depletion. The Power recording reached two depleted bases and idle
   workers; saving 400 minerals after income collapses cannot repair that. Zerg
   Macro had already reached three bases and 56 workers before its army collapsed,
   so this economy failure must not be substituted as Macro's explanation.

## First tactical experiment: approach before committing

The transferable pattern is to separate approaching an enemy formation from
committing to a fight. Ares uses separate movement grids containing ground, air,
and effect danger, with costed paths and safe positions. Its grids are explicitly
opinionated starting points, not universal combat rules.
[Ares influence/pathing tutorial](https://github.com/AresSC2/ares-sc2/blob/67187778f931035c8bb0380ef63a6cd9dedc478b/docs/tutorials/influence_and_pathing.md)
Sajuuk's approach state routes through safe regions, holds outside enemy reach,
and evaluates the force actually in striking position before entering its engage
state. Its numerical margin is an implementation choice, not a validated setting
for our bot.
[Sajuuk approach state](https://github.com/Guillaume-Docquier/Sajuuk-SC2/blob/390bb8b77d05ded0385971055f377e5efacc8f15/Sajuuk/Managers/WarManagement/ArmySupervision/RegionalArmySupervision/ApproachState.cs)

**Proposed minimal integration, one frozen candidate:**

- Add a pre-engagement approach decision in `MissionPlanner`/`ArmyWaves`, using
  visible hostile weapons and eligible squad members. Detect threatened forward
  units through weapon range plus both unit radii and a bounded movement buffer;
  do not rely only on distance from the median. Keep ground/air eligibility and
  the Colossus dual-target exception explicit.
- Reuse the geometry-caching pattern in `retreat_geometry`, but give offensive
  approach its own cost. Sample short traversable segments toward the objective,
  two lateral approaches and a standoff position. Score exposure along the segment,
  endpoint danger, travel and objective progress. A terrain fallback must not
  silently replace a rejected segment with a longer path through the same weapon
  envelope. Start with visible contacts; adding remembered positions is a separate
  belief change requiring age and uncertainty.
- Retain existing wave membership, reinforcement batches, ownership checks and
  terrain validation. Add `approach` telemetry and a commitment latch/hysteresis
  so the army does not alternate advance and retreat every observation. Once a
  deliberate assault starts, ordinary attack micro retains its actor budget.
  Reassess on material force loss or new threats rather than repeatedly canceling
  ready volleys.
- A costed approach must eventually allow a deliberate assault, a different
  objective, or defense of threatened income. Waiting outside every Siege Tank's
  range indefinitely is not success. Do not assume an unsieged tank or unseen
  flank without scouting it.

This is a hypothesis about avoidable approach damage, not proof that all Timing
losses are caused by pathing. A small candidate isolates that mechanism before
adding a full influence-map framework or combat simulator.

Meaningful synthetic scenarios: a tank reaches the forward unit while the median
is beyond ten; a lateral path has less exposure; a tempting flank crosses a
cliff; a support unit cannot attack the threatening domain; no safe route exists;
an army already firing does not have its volley canceled; selected/released actors
remain untouched. Then run a frozen Terran Timing triplet at 3600 game seconds.
Inspect damage taken before the first own volley, participating supply over the
next few seconds, recovery/approach transitions, siege-envelope exposure and
resource trade. Existing five-second samples cannot reconstruct every volley;
use bounded high-frequency engagement telemetry or replay inspection where needed.
Reject a losing candidate before broad regression. Retain Terran Rush and Zerg
Timing before promoting a successful targeted change.

## Subsequent experiments, kept separate

| Priority | Proposed change and local seam | Evidence and test |
| --- | --- | --- |
| P0 | Advance expansion planning before depletion in `economy_assistant.py`. Count mineral-bearing capacity, remaining resources and pending bases; allow safe income replacement independently of a fixed worker threshold. Reserve while income remains, retain an eligible builder, and transfer idle workers after completion. | Sharpy counts mineral-bearing zones as active bases and maintains builder/reservation state. Test depleted two-base/31-worker state, approaching depletion with income, unsafe/blocked expansion, pending Nexus and budget ownership. Gate on Zerg Power; do not claim this repairs Macro. |
| P1 | Log a shadow engagement estimate in `combat_assessment.py` using target-specific damage and bounded time-to-fire participation. Separate observed enemy force from inferred reinforcements. Calibrate before making it govern retreat. | Blizzard exposes weapon domain, damage, attribute bonus, attack count, range and period. Test Immortal versus armored/light targets, mixed air, Colossus dual vulnerability, blocked melee and distant reinforcements. Compare predictions with the following trade window, grouped by engagement rather than repeated frames. |
| P1 | Add role-aware approach slots in `army_waves.py`: reachable frontline, damage dealers and protected splash/support positions; bound nearby clustering. | Current depth treats Immortal and Colossus like other ranged units. Sajuuk explicitly implements flanks/concaves. Test a mixed force approaching siege plus bio, measuring survival and actual shots by counter units; avoid copying Zerg burrow tactics into Protoss control. |
| P1 | Give scouting a specific army/technology question in `scouting.py`, with value, route exposure and replacement cost. | An Observer's expansion patrol should not indefinitely postpone locating the army that determines whether a wave can engage. Keep the rejected belief controller experimental; reintroduce one question/route at a time with a matched gate. |
| P2 | Revisit damage/role-aware focus only where recordings show changed feasible decisions. | The archived local prototype changed only two of 21 sampled first-shooter choices and no Immortal choices. This limited sample is not a general micro verdict. Do not bundle fixed priority weights with pathing and macro changes. |

Primary references for these rows:
[Sharpy expansion controller](https://github.com/DrInfy/sharpy-sc2/blob/d9577a00ee47634b56ff7ee0740c6ed3043659a2/sharpy/plans/acts/expand.py),
[Blizzard weapon data schema](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/data.proto),
[Sajuuk features](https://github.com/Guillaume-Docquier/Sajuuk-SC2/blob/390bb8b77d05ded0385971055f377e5efacc8f15/README.md),
[local belief/scouting review](../opponent-beliefs-and-scouting.md).

Use live game data rather than copying historical unit values or timing tables.
Static weapon fields alone do not fully represent splash geometry, temporary
buffs, healing or every upgrade. Keep those limitations visible in any confidence
or engagement score. Ares' own combat-simulator manager documents serious
domain-related errors and recommends caution; importing it would not by itself
validate fight decisions.
[Ares simulator warning and interface](https://github.com/AresSC2/ares-sc2/blob/67187778f931035c8bb0380ef63a6cd9dedc478b/src/ares/managers/combat_sim_manager.py)

For scouting, retain separate uncertainty about commitment, technology, army
strength and relative strength. The limited-reconnaissance research models hidden
state separately from the observation process and recognizes scouting's cost;
it concerns Brood War, so its principle transfers while its learned parameters do
not. Evaluate information gain together with scout losses and downstream build
readiness, not label accuracy alone.
[Hostetler et al., limited reconnaissance](https://arxiv.org/abs/1210.4880)
The repository's [existing metric contract](../opponent-beliefs-and-scouting.md)
already distinguishes recognition, planned response and delivered readiness.
Configured built-in build labels remain evaluation references, never policy input.

## Public bots and frameworks worth using

These source snapshots were checked on 2026-10-31. Source availability is not
evidence of current competitive strength. No candidate below was installed, built
or launched during this research, and retail 5.0.17 compatibility remains untested.

| Project and frozen source | Useful role | Interface and limitations |
| --- | --- | --- |
| [MicroMachine](https://github.com/RaphaelRoyerRivard/MicroMachine/tree/eb893161371dab975a0a7e600f9e250ac03ec1ef), Terran, C++, [MIT](https://github.com/RaphaelRoyerRivard/MicroMachine/blob/eb893161371dab975a0a7e600f9e250ac03ec1ef/LICENSE) | Established Terran opponent and source for range/influence-aware micro. The organizer records MicroMachine reaching the 2025 quarterfinal. | Build with its own C++/SC2API dependencies or obtain an identified author artifact. Its configuration must enable `ConnectToLadder`; `main.cpp` passes the coordinator arguments to `RunBot`. Public source head is from 2023 and need not equal the 2025 competitor. Source warns about step sizes above one; use a documented opponent step rather than forcing ours. |
| [Sajuuk](https://github.com/Guillaume-Docquier/Sajuuk-SC2/tree/390bb8b77d05ded0385971055f377e5efacc8f15), Zerg, C#, [MIT](https://github.com/Guillaume-Docquier/Sajuuk-SC2/blob/390bb8b77d05ded0385971055f377e5efacc8f15/LICENSE) | Inspectable two-base Roach opponent; strong architectural examples for scouting, regional approach and dynamic priorities. | Project targets .NET 6. `Program` dispatches arguments to ladder play, using ladder host/game/start ports; no-argument execution starts its own local game. It bundles analysis for named maps, so confirm/generate required data for the actual benchmark map. No current elite result established here. |
| [Aristaeus](https://github.com/august-k/Aristaeus/tree/d3d8928b0901ae4aeece261e237dd62a289185b1), Python/Ares, [MIT](https://github.com/august-k/Aristaeus/blob/d3d8928b0901ae4aeece261e237dd62a289185b1/LICENSE) | Public Protoss candidate and source-inspectable teacher candidate after validation. | Check configured race/build explicitly; `run.py` reads its configuration and selects ladder mode when `--LadderServer` is present. `ladder.py` joins a supplied websocket/port allocation. Python requirement is 3.11 and the Ares submodule/dependencies must be frozen. Public head is from 2023; no competitive acceptance evidence established here. |
| [TyrSc2](https://github.com/SimonPrins/TyrSc2/tree/bca42ab0a209308ba626c9b25fda44632a7b7543), C#, [MIT](https://github.com/SimonPrins/TyrSc2/blob/bca42ab0a209308ba626c9b25fda44632a7b7543/LICENSE) | Historical alternative with inspectable builds and a Windows-oriented workflow. | README uses Visual Studio/.NET and LadderManager for other-bot games. Choose race/build from source, not the name. The public head is from 2022; it is not verified to be the 2026 tournament TyrT artifact. |

Runtime evidence:
[MicroMachine main](https://github.com/RaphaelRoyerRivard/MicroMachine/blob/eb893161371dab975a0a7e600f9e250ac03ec1ef/src/main.cpp),
[Sajuuk project](https://github.com/Guillaume-Docquier/Sajuuk-SC2/blob/390bb8b77d05ded0385971055f377e5efacc8f15/Sajuuk/Sajuuk.csproj),
[Sajuuk entry point](https://github.com/Guillaume-Docquier/Sajuuk-SC2/blob/390bb8b77d05ded0385971055f377e5efacc8f15/Sajuuk/Program.cs),
[Aristaeus entry point](https://github.com/august-k/Aristaeus/blob/d3d8928b0901ae4aeece261e237dd62a289185b1/run.py),
[Aristaeus ladder adapter](https://github.com/august-k/Aristaeus/blob/d3d8928b0901ae4aeece261e237dd62a289185b1/ladder.py),
[Tyr setup](https://github.com/SimonPrins/TyrSc2/blob/bca42ab0a209308ba626c9b25fda44632a7b7543/README.md),
[2025 tournament results](https://aiarena.net/wiki/sc2ai-arena-2025-tournament/).

[Ares](https://github.com/AresSC2/ares-sc2/tree/67187778f931035c8bb0380ef63a6cd9dedc478b)
and [Sharpy](https://github.com/DrInfy/sharpy-sc2/tree/d9577a00ee47634b56ff7ee0740c6ed3043659a2)
are MIT frameworks, not a fixed strategy or automatically strong opponent. Study
specific behaviors without migrating our SDK. Current Ares depends on a Git
branch of a different BurnySC2 source plus native extensions; this conflicts with
treating it as a drop-in package under our pinned environment.
[Ares dependencies](https://github.com/AresSC2/ares-sc2/blob/67187778f931035c8bb0380ef63a6cd9dedc478b/pyproject.toml)

The organizer's 2026 tournament shows Eris beating BenBotBC in the final, with
Zozo and AvocaDOS in the third-place match. Those dated results help select
established opposition; they are neither October ladder rankings nor proof that
a same-named public repository is the submitted artifact. Obtain an identifiable
author-approved artifact and verify availability/license before adding such bots
to the acceptance pool.
[2026 tournament conditions and results](https://aiarena.net/wiki/sc2ai-arena-2026-tournament/)

MIT notices must accompany copied substantial code. Check nested dependencies
and artifact terms separately. GPL orchestration below can be used as a separate
tool; any copied or distributed modifications must retain its applicable terms.

## How to use our bot and other bots together

Use a separate process and dependency environment per opponent. Share the SC2
protocol through a match coordinator; do not import another bot's `sc2` modules
into our root environment. Preserve `burnysc2==7.3.0`,
`pys2clientprotocol==1.0.2` and the SDK boundary in `source/runtime.py`.
The existing built-in-AI launch path does not become an external-bot match merely
by giving it an executable path. A future adapter must coordinate create/join,
participant ports, stepping, timeouts, results and owned-process cleanup, with
synthetic lifecycle coverage before a live interoperability trial.

AI Arena's GPLv3 [match controller](https://github.com/aiarena/sc2-ai-match-controller)
separates match scheduling, SC2/websocket management and bot launching. Its README
explicitly permits local operation without asset downloads or result uploads.
The GPLv3 [local-play bootstrap](https://github.com/aiarena/local-play-bootstrap)
documents bot/map folders, a match manifest, result/replay outputs and Compose
execution. Its example arguments include `--GamePort`, `--StartPort`,
`--LadderServer` and `--OpponentId`; each bot's actual parser remains authoritative.
This research does not register, upload or publish our bot.

For a first integration, run one external match, verify both participants' loops,
legal fog-of-war observations and resolved result, then test owned cleanup on
failure. Only afterward schedule repeat batches. Count actual SC2 clients toward
the eight-client ceiling; a two-client external match consumes two slots. Isolate
write/data directories and either reset or explicitly freeze an opponent's
persistent learning between comparisons.

Retain a per-opponent manifest: source commit/submodules, executable/container
hash, dependency lock, license, race/build/configuration, opponent ID, persistent
state policy, seed, participant step sizes, time limit, map hash, exact engine
ping/data identity and unit-data fingerprint. Protocol handshake success alone
does not validate tactical compatibility.

Keep the native Windows retail domain authoritative for the current milestone.
The AI Arena [SC2 image recipe](https://github.com/aiarena/aiarena-docker-base/blob/master/docker/Dockerfile.sc2)
uses a Linux SC2 4.10 package; the local-play example uses AcropolisAIE, while
the 2026 tournament lists versioned AIE maps. Check embedded balance changes,
dependencies and game-data fingerprints. Report Linux/AIE outcomes in a separate
domain until unit data, effects and meaningful behavior match the intended retail
benchmark; do not silently downgrade our acceptance binary or substitute maps.

Validated source-inspectable opponents can later supply targeted examples,
curriculum opponents or teacher trajectories. A teacher still needs measured
strength and recorded legal observations/actions. Source access does not make
its internal state compatible with our action vector. Preserve our participant's
fog and belief state for policy inputs; keep omniscient replay labels or another
participant's private observations confined to clearly separated offline targets.

The next concrete work is a frozen siege-approach experiment and the independent
depletion regression fix. Community interoperability can then be implemented
without blocking those live improvement gates.

## Long game economy follow up

Subsequent trials rejected siege approach and broad earlier third-base funding;
the [milestone record](../hardcoded-elite-milestone.md) preserves their outcomes.
The Robotics-v2 Power parent did build a third base, then lost one and exhausted
the remaining lines. At 1005 seconds it still has 56 workers and three bases but
only 22 mineral ideal-harvester positions. Pressure's three-base ceiling prevents
preemptive renewal; its worker cap of 56 also makes the fourth-base gate of 58
unreachable if only the base ceiling is raised. A configuration test of four
bases/seventy workers keeps the old gates; it is a hypothesis, not an established
optimum. A fifth base adds no reachable gate while the unchanged requirement is
78 workers.

MicroMachine provides a useful independent mechanism: its expansion condition
uses accessible mineral-patch capacity with an offset to start before workers
arrive, and worker targeting allows for the next expansion. It also responds to
positive observed early Roach Warren/Roach evidence for an armored-ground counter.
These are precedents for preemptive capacity and evidence-driven investment;
the historical Terran thresholds are not copied into this Protoss bot.
[MicroMachine production manager](https://github.com/RaphaelRoyerRivard/MicroMachine/blob/eb893161371dab975a0a7e600f9e250ac03ec1ef/src/ProductionManager.cpp#L755)

Our current observation omits mineral amounts outside vision. Treating a missing
positive amount as depletion delayed a third base in a controlled trial. A later
resource model should retain timestamped site inspections and confirmed depletion,
request a safe scout for stale sites, and preserve the distinction between unknown
and empty. A strict requirement for an Observer before funding Robotics would
be circular: Robotics produces the Observer. Positive earlier worker/army evidence
can motivate counters; missing tech observations cannot prove the opponent lacks
that technology. No new evidence gate has been accepted yet.
