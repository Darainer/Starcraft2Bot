# Scouted strategy repertoire

The integration branch `feat/scouted-strategy-portfolio-20261031` keeps response
packages together. The director chooses a package from observed facts; its
existing operational objectives still choose whether to develop, defend,
pressure, contain, counterattack, finish or recover. A package controls bounded
production priorities and formation behavior, rather than replacing every
controller or issuing competing orders.

## Available packages

| Playbook ID | Automatic eligibility | Components and origin |
| --- | --- | --- |
| `baseline` | Missing, stale, incompatible or insufficient evidence; explicit baseline override | R2 spending and formation, `67ed0f7`; existing adaptive composition remains available |
| `zerg_early_robotics` | Existing positive Pool/Warren/Roach-path selector with its original deadlines | First Robotics funding from `b3aff99`; baseline formation |
| `terran_counter_tech` | Terran ground-production building observed within 90 s | Attainable first Robotics/Bay funding and requested first Colossus priority, adapted from `a7cefe1` |
| `terran_counter_range` | At least four observed Terran ground supply, contacts individually younger than 45 s | Counter-tech plus engaged actors closing toward a local visible, attackable, domain-compatible enemy when unable to fire; `287dbd5` |
| `zerg_counter_completion` | Own Bay ready, at least eight unique light-ground contacts individually younger than 45 s, and no active early-Robotics selection | Complete an already-requested first Colossus; preserve original Robotics/Bay construction order and baseline formation; new integration hypothesis |

The first four preserve useful choices from earlier experiments on one code
branch. Their earlier results belong to their original frozen revisions, not
automatically to this integration. The completion option is a new hypothesis.
Current source is [strategy_portfolio.py](../source/strategy_portfolio.py).

The composition controller continues to combine air, armored-ground and
light-ground evidence. It can request anti-air, Immortals or splash independently
of a five-label guess about the opponent's overall strategy. The requested
profile and combat-spell permissions remain user controlled. Package selection
does not enable optional spells or turn a single unit sighting into knowledge of
the whole enemy army.

## Selection, uncertainty and execution

Race limits compatibility; race alone cannot choose a specialized package.
Only positive timestamped contacts or technology observations enter automatic
selection. Configured AI build, future replay state, final outcome and generic
classifier guesses are not inputs. Unknown and Random opposition retain baseline
until the adapter supplies an appropriate known race and supporting facts.

Selections record `playbook_id`, `playbook_uncertainty`, `response_reason`,
`response_evidence`, `response_policy_until` and `tactical_policy` in both
assessment and plan. The uncertainty values are heuristic, not calibrated win
probabilities or verified intent probabilities. Missing evidence starts at 1.
Plan validation rejects mixed, stale or superseded packages. Changes in selected
package trigger the director immediately; it normally reassesses at most every
two game seconds. Individual contact ages prevent unrelated sightings from
refreshing old evidence. Existing mission commitment controls target switching.

Evidence expiry returns to baseline spending priorities. Buildings already built
are retained, and observed first-unit milestones remain latched after losses;
the bot does not repeatedly reserve a nominal "first" counter. Supply, income,
power, reachable construction, selected/released actors, emergency minimum force,
resource reserves and the shared paid-action budget still gate execution.
User pause, attack off, manual strategy, scripts and adaptive-composition off
disable package execution. Terran local-range tactics never apply to Zerg.

The observed-facts-v2 input contract and two-layer RL design are unchanged.
This module belongs to the SC2 adapter. A future learned selector can propose
packages through the validated plan boundary while receiving causal facts and
uncertainty. Package identity is an action/provenance field, not hidden truth
about the opponent.

## Choosing a fixed package for an experiment

Default configuration uses `"playbook": "auto"`. A fixed package can be selected
in JSON, at launch, or during a match:

```powershell
uv run --locked sc2-assistant --playbook terran_counter_range
uv run --locked python -m source.trials --profiles pressure --opponents Terran --builds Timing --repeat 3 --playbook terran_counter_tech
```

```text
!assist playbook auto
!assist playbook baseline
!assist playbook zerg_early_robotics
!assist playbook terran_counter_tech
!assist playbook terran_counter_range
!assist playbook zerg_counter_completion
```

Fixed selection is explicitly logged as an experimental override with uncertainty
1; it does not pretend scouting supported the choice. Race compatibility and all
execution safeguards still apply. Changing a package does not reset the game or
undo prior investments. The trial runner records the requested package separately
from the enemy's configured build.

## Preserved experiment lineage

The recorded experiment lineage retains source commits and reports, including
negative results. Rejected global edits are recorded here rather than silently
overwriting a successful component. These entries are historical source
snapshots, not additional automatically enabled packages.

| Experiment | Gameplay revision | Recorded disposition |
| --- | --- | --- |
| R2 production recovery | `67ed0f7` | Original combined suite 21W/9D; baseline spending retained |
| Robotics funding v2 | `dc09385` reconstructed frozen parent | Timing wins but global regressions; bounded funding component retained through the Zerg selector |
| Counter-tech | `a7cefe1` | Terran Rush 3W, Timing 3D; modular funding/first-counter component retained |
| Siege approach | `90f5277` | Terran Timing 3D; archived |
| Reachable expansion | `e9da001` | Power wins slower than matched parent; archived |
| Depletion recovery | `4af6e8d` | Power 3D; archived |
| Sustainable pressure | `16d3016` | Power 3D; archived configuration experiment |
| Engagement range | `287dbd5` | Terran Rush/Timing 6W; global Zerg failures; Terran component retained |
| Zerg scout selector | `b3aff99` | Original Zerg five-build block 15W; positive-evidence selector retained |
| Revisit scouting v1 | `2be052b` | Six target wins, poor early information; archived |
| Revisit scouting v2 | `64001d5` | Six target wins, poor early information; archived |
| Revisit scouting v3 | `0f673b2` | Earlier useful sightings; original targets 6W; third-seed Macro 3W, Power 3D; opt-in recon retained |

See [milestone history](hardcoded-elite-milestone.md),
[scouting evidence](opponent-inference-training.md) and
[overall status](bot-status.md) for the separate comparison groups. Faster
finishes, classification proxies and targeted wins do not certify a generally
stronger bot.

## Final evaluation boundary

The declared set is complete: **24W/12D/0T across 36 games**. See the
[final report](final-bot-report-2026-10-31.md). The integration remains experimental;
no further tuning or games follow this set. The protocol below records the
frozen evaluation boundary.

After software checks, freeze one integration revision. Run pressure versus
VeryHard Terran and Zerg on BelShirVestigeLE, explicit Rush/Timing/Power/Macro/Air,
three repeats each on seed 20261025: 30 games. Add the six known failing Zerg
Power/Macro conditions on development seed 2026103102. Use automatic package
selection, opt-in V3 revisit, one-second fact snapshots, step eight, a 3600-game-
second limit and at most eight global clients. Preserve all resolved/censored
results, logs and replays. Verify source hashes, actual binary/data, map,
computer difficulty and loop-zero starts. The new `playbook` setting is an
explicit integration difference; compare physical starting state separately
from settings when matching historical starts.

Do not tune gameplay during or after this final set. Produce the comprehensive
report and stop. These are fixed-start development gates on one map, not
independent samples, a new held-out benchmark or elite acceptance. Protoss,
additional maps/seeds and established community bots remain outside this set.
