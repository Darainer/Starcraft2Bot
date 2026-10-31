# Final Python bot report - 2026-10-31

The scouted response repertoire is integrated on
`feat/scouted-strategy-portfolio-20261031`, with frozen gameplay **`d0f8cf3`**.
The final set completed **24W / 12D / 0T across 36 games**. The integration
fails the combined reliability gate and must remain experimental. Earlier
specialist wins remain valid evidence for their original revisions; they do not
transfer automatically to this selector. The elite milestone is incomplete.

Work stopped after this declared set, evidence preservation and reporting. No
further tuning or game batches follow this report.

## Final results

All opponents were the built-in **VeryHard**, the highest non-cheating protocol
difficulty. These results establish neither human ladder rank nor strength
against established community bots.

The main block used seed **20261025**, three fixed-start repeats per explicit
build. Terran: **6W / 9D / 0T**.
Zerg: **12W / 3D / 0T**.

| Race | Build | Result | Last sampled game seconds |
| --- | --- | --- | --- |
| Terran | Rush | 0W / 3D / 0T | 1316.8 / 1316.8 / 1316.8 |
| Terran | Timing | 0W / 3D / 0T | 1216.1 / 1216.1 / 1216.1 |
| Terran | Power | 0W / 3D / 0T | 753.2 / 753.2 / 753.2 |
| Terran | Macro | 3W / 0D / 0T | 1067.1 / 1067.1 / 1067.1 |
| Terran | Air | 3W / 0D / 0T | 752.1 / 752.1 / 752.1 |
| Zerg | Rush | 3W / 0D / 0T | 751.1 / 751.1 / 751.1 |
| Zerg | Timing | 3W / 0D / 0T | 1002.9 / 1002.9 / 1002.9 |
| Zerg | Power | 0W / 3D / 0T | 1225.7 / 1225.7 / 1225.7 |
| Zerg | Macro | 3W / 0D / 0T | 979.3 / 979.3 / 979.3 |
| Zerg | Air | 3W / 0D / 0T | 627.9 / 627.9 / 627.9 |

The additional development block used seed **2026103102** and the previously
failing Zerg Power/Macro conditions. It completed **6W / 0D / 0T**.

| Race | Build | Result | Last sampled game seconds |
| --- | --- | --- | --- |
| Zerg | Power | 3W / 0D / 0T | 1954.3 / 1954.3 / 1954.3 |
| Zerg | Macro | 3W / 0D / 0T | 911.8 / 911.8 / 911.8 |

`T` denotes a censored result at the configured time bound, not a victory or
defeat. Times above are last sampled observations, not exact engine end times.
Fixed-start repeats measure reproducibility; they are not independent opponents.
These seeds were used for development, not untouched holdout evaluation.

Evidence: [main evaluation](evaluations/2026-10-31-portfolio-final-main.md),
[known-failure evaluation](evaluations/2026-10-31-portfolio-final-known-failures.md),
[main verified outcomes](experiments/2026-10-31/portfolio-final-main-outcomes.json)
and [known-failure verified outcomes](experiments/2026-10-31/portfolio-final-known-failures-outcomes.json).

## What was brought together

Five executable packages coexist in [the portfolio](strategy-portfolio.md):

| Package | Intended use | Execution components |
| --- | --- | --- |
| `baseline` | Missing/stale evidence, or a fixed baseline comparison | R2 spending and formation with existing adaptive composition |
| `zerg_early_robotics` | Existing positive early Pool/Warren/Roach-path evidence | Bounded first Robotics investment; original formation |
| `terran_counter_tech` | Fresh observed Terran ground-production technology | Attainable Robotics/Bay funding and requested first Colossus priority |
| `terran_counter_range` | Fresh observed Terran ground force | Counter-tech plus local domain-compatible range closing |
| `zerg_counter_completion` | Ready own Bay and fresh light-ground contacts | Finish a requested first Colossus without moving Robotics/Bay construction earlier |

The existing operational choices remain available: develop, stabilize, pressure,
contain, counterattack, finish and recover. Air, armored-ground and light-ground
composition overlays can coexist. Profiles and individual spell permissions
remain user controlled. The [experiment lineage](strategy-portfolio.md#preserved-experiment-lineage)
preserves other completed experiments and their source revisions. Rejected global
edits are historical snapshots, not additional automatically enabled packages.

`--playbook auto` selects from positive timestamped scouting and own readiness.
Fixed packages are selectable through configuration, the runtime/trial CLI and
`!assist playbook <id>`. Overrides are explicitly recorded as experiments with
uncertainty 1. Race compatibility, evidence expiry, plan validation, protected
resources, selected/released actors and emergency priorities still apply.

This is a rule-based selector. It does not consult the configured AI build,
future replay state or match outcome. The generic five-label classifier does not
control the new package choice. Missing vision remains unknown rather than
proof that an enemy force or expansion is absent.

## What the selector actually did

| Package | Games in which selected | Share of pooled recorded time | First selection range |
| --- | ---: | ---: | --- |
| `baseline` | 36 | 42.8% | 0.0-0.0 s |
| `zerg_early_robotics` | 15 | 4.1% | 45.0-307.5 s |
| `terran_counter_tech` | 15 | 5.0% | 43.9-360.0 s |
| `terran_counter_range` | 15 | 25.5% | 188.6-352.5 s |
| `zerg_counter_completion` | 18 | 22.5% | 491.8-664.3 s |

These shares pool recorded game time, so long games contribute more. They are
exposure measurements, not correct-choice accuracy or causal package value.
[Selection traces](experiments/2026-10-31/portfolio-final-selections.json) retain
each transition, supporting evidence, reason, uncertainty and expiry for all 36
games. Plan validation rejects mixed or superseded packages; legacy early-Robotics
assessments still load for offline replay.

The available options now survive together, but automatic selection has not
retained the fixed specialists' results. The Terran triggers distinguish recent
ground production/force, not sufficiently detailed economic commitment, attack
timing or fortified engagement conditions. The final losses make this an
observed reliability gap, rather than a reason to merge the candidate as the
accepted baseline.

## Earlier wins and the scouting comparison

| Frozen revision/group | Completed evidence | Qualification |
| --- | --- | --- |
| Zerg selector `b3aff99`, seed 20261025 | 15/15 wins, all five builds | One map and world seed |
| Instrumented reference `2be052b`, seed 2026103101 | Another 15/15 Zerg wins | Additional development group |
| Reference `2be052b`, seed 2026103102 | 9W/6D; Power and Macro each 0/3 | Zerg was not solved across seeds |
| Terran specialist `287dbd5` | Rush 3/3 and Timing 3/3 | Separate fixed experiment, not this integrated selector |
| Revisit V3 `0f673b2`, original targets | Macro 3/3 and Timing 3/3 | Useful earlier facts with added worker opportunity cost |
| V3 on third-seed failures | Macro 3/3 at 920.4 s; Power 0/3 at 997.5 s | Reference lost both triplets; information alone did not solve Power |

The original R2 full matrix was 21W/9D at a 1500-second bound. It won the Terran
Power/Macro/Air triplets. New runs use 3600 seconds. Historical outcomes and bounds
remain intact; a longer-bound victory alone would not demonstrate stronger play.
See [milestone history](hardcoded-elite-milestone.md) and
[scouting comparisons](opponent-inference-training.md).

The matched original-seed V3 comparison establishes a real reconnaissance gain:
Macro's expansion first appears at 186.4 s versus 295.7 s, about 109.3 s earlier.
Timing's first army contact moves from 193.9 s to 174.6 s. Timing expansion discovery
does not improve (271.1 s versus 268.9 s). These are first recorded sightings, not
construction starts or total enemy army truth.

Through 240 s, assigned-worker opportunity increases by 70.7 worker-seconds for Macro
and 46.1 for Timing, with no confirmed worker-scout deaths through that horizon.
This is a mining-opportunity proxy, not directly measured lost minerals. The
additional Probe has bounded departure/outbound time, damage/army/worker-pressure
withdrawal and ownership guards. V3 is opt-in and was enabled throughout the
final suite. [Early evidence and costs](experiments/2026-10-31/scouting-v3-early-information.json)
are retained separately from outcome claims. Across the final 36, the
[scout-cost ledger](experiments/2026-10-31/portfolio-final-scout-costs.json) records
153.1 assigned-Probe-away seconds per game on average. All 72 tracked worker
scouts returned; none was confirmed dead while assigned. Six Observer losses
were confirmed (150 minerals/450 gas in total), while 12 Observer entries were
missing without a native death confirmation. Those missing entries are kept
uncertain. Losses after a scout is released are outside this assignment ledger.

## Recognition and build suitability

The final scenario means average each repeat within its declared condition,
then weight the 12 conditions equally. They are retrospective public-observation
diagnostics, not a held-out predictor benchmark.

| Metric | Final value | Interpretation |
| --- | ---: | --- |
| Time-weighted configured-build label accuracy | 18.4% | Unknown counts as incorrect; configured build is a weak episode label |
| Committed label coverage | 22.9% | Fraction assigned a non-Unknown label |
| Multiclass Brier score | 0.619 | Against the same weak label; lower is better |
| Planned counter-role fit | 91.8% | Ontology capacity proxy, conditional on force evidence |
| Delivered role readiness | 90.3% | Observed role capacity versus demand; not battle success |
| Response-evidence coverage | 35.9% | How often suitability was measurable |
| Ready-tech target fraction | 90.9% | Target supply with ready prerequisites/producers; excludes production time and bank |
| Target supply feasibility | 66.1% | Requested supply fits 200 minus configured worker cap; not a resource-bank test |

The [full metric artifact](experiments/2026-10-31/portfolio-final-strategy-metrics.json)
contains scenario/repeat values, uncertainty, evidence ages and denominators.
High role-fit/readiness scores can coexist with losses: these proxies do not
measure route safety, weapon participation, effective combined arms or whether
resources arrived before the critical fight. Package uncertainty values are
heuristics, not calibrated intent or win probabilities.

The [observability breakdown](experiments/2026-10-31/portfolio-final-observability.json)
finds that during the first 240 s, 72.0% of recorded time lacks all three counted
fresh features: army contact, nonordinary technology, or a positive expansion
sighting. Fresh force of at least four recently observed supply covers only 2.0%
of opening time across the 12 conditions. Across whole games, recent-force
coverage rises to 56.7%, while the same classifier's label accuracy within those
intervals is 22.9%. Recent here means 30 s; the counter-role metrics above require
contemporaneous visible-force evidence within 5 s. Empty-site inspections are
recorded separately and are not included in that three-feature definition.
The fraction includes quiet early phases and depends on chosen freshness cutoffs.
The conditional strata overlap and are descriptive, not a causal error budget.

Mean model uncertainty remains high: aggression 0.95, economy 0.87 and enemy
army 0.79 on its heuristic 0-1 scale. These are not calibrated error probabilities.
Both information delivery and execution/selection logic remain weaknesses. We
have not measured a causal percentage of errors attributable to either, and do
not have replay-oracle targets establishing an upper-information bound.

## Concrete delivery and combat findings

The third-seed reference lost despite recognizing fresh Roach-path pressure
around 290-300 s. Its first Robotics/Immortal arrived around 352/405 s in Power and
351/410 s in Macro. Bay readiness then preceded the first Colossus by hundreds of
seconds: Power 503.6 to 983.6 s; Macro 498.2 to 866.8 s.

The [delivery audit](experiments/2026-10-31/counter-delivery-audit.json) found
333 qualifying pre-completion snapshots per Power repeat, all below 300m/200g,
and 109 per Macro repeat, 107 below cost. Qualifying snapshots already had the
requested counter, ready Bay, eligible idle powered Robo, sufficient supply and
fresh light-ground contacts. These correlated snapshots motivated the narrow
completion package; they did not prove an earlier Colossus would save the games.

The final Terran Power example demonstrates why earlier tech is insufficient.
The first Colossus arrived at **456.4 s**, versus **585.4 s**
in the winning historical R2 example, yet the final candidate lost. Its sampled
army trade ratio was **0.123**, versus
**0.911** in that reference. The
final recording includes severe trades against Marine/Marauder/Tank forces and
base losses. This is evidence of failed combat/response suitability, not proof
that recognition alone was late. Multiple integration changes prevent assigning
the regression to one component without a matched ablation.

The original-seed Zerg Power example also received earlier tech but lost:
first Colossus **582.9 s**
versus **625.4 s** in the winning
`b3aff99` example; army trade ratio **0.584**
versus **2.323**. The final Power triplet
lost all three. Counter availability therefore does not by itself establish an
appropriate engagement, sustainable force or successful outcome.

On development seed 2026103102, however, Power improved from 0/3 wins in both
3600-second references (`2be052b` and V3 `0f673b2`) to **3/3 wins at 1954.3 s**
in the integration. Macro also won 3/3. These are resolved targeted gains under
the same longer bound. The Power victories occur after the old 1500-second bound;
the original censored records remain unchanged. This supports preserving the
completion package while the original-seed Power regression prevents universal
promotion. It does not isolate every interaction in the combined candidate.
With V3 recon in both arms, first Robotics/Immortal/Bay timings match at
279.6/371.8/522.9 s. The integration completes its first Colossus at 585.0 s;
V3 had no completed Colossus before its 997.5 s defeat. The representative army
trade ratio improves from 0.579 to 1.659. The
[delivery comparison](experiments/2026-10-31/portfolio-final-delivery-comparison.json)
retains all three repeats of both builds and all reference arms.

The next investigation, if resumed later, should compare fixed package versus
automatic selection and revisit off versus on with frozen matched starts. It
should test investment commitment under fog, counter mix/readiness and safe
Tank engagement separately. No such extra batches were run after this final set.

## Reproducibility and software validation

| Item | Recorded identity |
| --- | --- |
| Gameplay revision | `d0f8cf3` |
| Frozen source/config files | 49, verified before and after the final groups |
| Map | BelShirVestigeLE |
| Map SHA256 | `9cb078a287c76c0b55e3bc137b0e4590415231367d7c5724ab1bfd24a06a1d1e` |
| Native retail game | `5.0.17.98310`, Base/DataBuild 98310 |
| Data version | `9C1F3D3D30CA252E33FC67CA05CBE1EA` |
| Runtime packages | burnysc2 7.3.0; pys2clientprotocol 1.0.2 |
| Profile / step / limit | pressure / 8 loops / 3600 game seconds |
| Collection | One-second snapshots; all new debug-log rotations retained |
| Execution | Native Windows, approved Full Access context verified |
| Concurrency | At most seven evaluation clients alongside the other active client; global limit eight |

Both SC2/Python random seeds and PYTHONHASHSEED used the listed group seed.
Three repeats per condition share verified loop-zero fingerprints. Historical
physical starts match; the added `playbook=auto` setting and declared longer bound
for old R2 references are recorded differences. Original result records were
not rewritten. All 36 final games retain nonempty hashed replays.
[Frozen source and start verification](experiments/2026-10-31/portfolio-final-provenance.json)
records the source hashes and explicit comparison differences.

Required locked sync, Ruff lint/format, configured Mypy, protocol/lifecycle tests,
**598 synthetic tests (89.41% coverage)** and both package builds passed before
publication. Configured static typing covers the documented control boundary,
not every dynamic SDK module. Synthetic checks do not launch SC2 or establish
playing strength.

The API probe recorded the exact native game identity. Automated matches and
metadata checks passed their lifecycle gates. Shared human selection, camera,
hotkeys and manual input remain **NOT_VERIFIED**; API success and bot results do
not certify them. Evaluation cleanup concerns owned clients only.

## Preserved data and RL handoff

The completed [archive index](experiments/2026-10-31/observed-facts-v2-corpus-index.json)
now contains **111 distinct game recordings,
87,958 factual records and 1,365 hashed
artifacts**, about **21.15 GB**, across
**4 world split groups**. This count excludes draft
or incomplete exports and does not call repeated trajectories independent data.
Raw logs, rotations, states, game metadata, manifests and replays remain local
and ignored by Git; sanitized outcomes, metrics and provenance are committed.
All surviving earlier artifacts are preserved; already deleted legacy rotations
cannot be reconstructed.

`sc2-observed-facts-v2` supplies causal visible contacts, per-contact age,
first-recorded technology/expansion sightings, own public state and public map
geometry. Inferred beliefs, configured build labels, final outcome and oracle
state are separate from inputs. The [legal example](examples/sc2-observed-facts-v2.json)
and [inference training plan](opponent-inference-training.md) document the
contract. Group all builds, repeats and bot policies sharing a world together;
4 groups on one map are insufficient for reliable
cross-map/opponent claims.

A same-loop replay oracle-label extractor and a reliable trained opponent
estimator are still outstanding. Own-state versus enemy-fact-only ablations,
real-fog validation, uncertainty calibration and shadow evaluation precede
activating a learned selector. The current export targets opponent estimation; an RL action-vector export is
not implemented here. Poor-play trajectories should not automatically be treated
as expert imitation targets.

The approved [two-layer architecture](game-agnostic-architecture.md) separates
portable reasoning from the SC2 adapter. The [U.S. Army doctrine background](doctrine-inspired-control.md)
organizes running estimates, competing courses of action, reconnaissance,
mission intent, sustainment and continuous assessment. It supplies no SC2 counter
coefficients or proof of tactical quality. The SC2 repertoire belongs to the
adapter; the existing BeliefStateV1/DirectorActionV0 RL design remains unchanged.

The [RL architecture](rl-architecture.md) and [environment plan](rl-training-plan.md)
are available for the user's separate RL session. Headless Linux/container
rollouts remain a proposed measured deployment target; native Windows retail is
the current acceptance domain. This work did not implement or train the learner,
and the hardcoded bot is not yet an accepted elite teacher.

## Remaining gates and stopping point

1. Repair the integrated selector's regressions through small matched component
   tests, while retaining the successful fixed packages and their provenance.
2. Improve decision-linked reconnaissance and multi-axis inference: economic
   commitment, technology, observed army lower bounds and relative strength, with
   stale/missing evidence represented explicitly.
3. Demonstrate retention across untouched seeds/maps, then Protoss and established
   community bots. Built-in fixed-start wins alone do not meet the elite target.
4. Validate human shared controls separately if that interaction is required.

These are future priorities, not additional work started after the requested
stop. The integration, evidence and comprehensive report are checked in on the
feature branch; the R2 baseline and earlier experiment branches remain
available. No evaluation jobs or further tuning from this session remain active.
