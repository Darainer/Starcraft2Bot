# Python bot status

Status, 2026-10-31. Accumulated work was summarized and merged in
[PR #5](https://github.com/Darainer/Starcraft2Bot/pull/5) into the repository's
primary branch `master`, merge `425bca8`. The repository has no `main` branch.
New tactical work is isolated on `experiment/targeted-oracle-archon-20261031`
in [draft PR #6](https://github.com/Darainer/Starcraft2Bot/pull/6).

The follow-up completed **21 matched benchmark games, all resolved defeats**:
six controls, six delivery-v1, six delivery-v2 and three selective-v3 games.
Archons now reach combat in delivery-v2. Oracle beam/worker execution passed a
separate mechanism diagnostic, but useful harassment was not demonstrated in
these benchmark games. No new candidate is promoted and the elite milestone
remains incomplete. See the [targeted results below](#targeted-oraclearchon-results).

The merged opt-in composition work includes race/fielded-force counter recipes,
splash floors, late-game replacement targets, counter-tech investment and
upgrade priorities. Economic-asset defense and bounded local re-engagement
remain available for separate tests; both were off in this tactical comparison.
See the [candidate settings and design](strategy-portfolio.md#opt-in-counter-composition-candidate).

Current gameplay source `dbf4aee` passed locked sync, Ruff lint/format,
configured Mypy, protocol/lifecycle tests, **717 synthetic tests with 89.75%
coverage**, and source/wheel package builds. These checks do not establish
playing strength. Live mechanism diagnostics are excluded from benchmark scores
and training data.

The branch `feat/scouted-strategy-portfolio-20261031` contains five selectable
response packages, with frozen gameplay `d0f8cf3`. The final result is **24 wins /
12 losses / 0 timeouts across 36 games** against verified built-in VeryHard.
The integration fails the combined reliability gate and remains experimental.
The elite milestone is incomplete.

Read the [comprehensive final report](final-bot-report-2026-10-31.md) for evidence,
selection traces, reconnaissance costs, metrics, source identities and limitations.
The [repertoire design](strategy-portfolio.md) explains automatic and fixed choices.

## Final playing strength

Main seed 20261025, pressure, three fixed-start repeats per build:

| Opponent | Rush | Timing | Power | Macro | Air | Total |
| --- | --- | --- | --- | --- | --- | --- |
| Zerg | 3W | 3W | 3D | 3W | 3W | 12W / 3D |
| Terran | 3D | 3D | 3D | 3W | 3W | 6W / 9D |

The additional seed 2026103102 won **6/6**: Zerg Power and Macro each 3/3.
Power resolved at 1954.3 game seconds, after the old 1500-second bound. Both
3600-second reference variants had lost that Power triplet. This is a targeted
gain, while the main-seed Power and Terran regressions prevent promotion.
All final matches used a 3600-second limit; none timed out.

The earlier Zerg selector `b3aff99` won 15/15 on the original seed; the instrumented
reference `2be052b` won another 15/15 on seed 2026103101. The earlier fixed Terran
specialist `287dbd5` won Rush 3/3 and Timing 3/3 on its separate branch. These remain
results for those revisions, not wins attributable to the integrated selector.
Repeated starts measure reproducibility rather than independent opponents.

All results concern built-in **VeryHard**, the highest non-cheating protocol
difficulty. Protoss, additional maps, untouched seed groups and established
community opponents remain unvalidated. Human ladder/elite strength is not established.

## Targeted Oracle/Archon results

Each populated cell is three identical fixed-start repeats, pressure/VeryHard,
explicit build, seed 20261025, BelShirVestigeLE, step 8, V3 scouting revisit,
one-second snapshots and a 3600-game-second bound. Both controls and candidates
enable scouted composition, Archon merge and Oracle/beam permission. Full
loop-zero states/settings match the controls; frozen source/config hashes,
native binary/data, map, actual difficulty and hashed replays were verified.
No games timed out or were intentionally aborted. Repeats are correlated.

| Frozen arm | Terran Timing | Zerg Power | Decision |
| --- | --- | --- | --- |
| Merged control `425bca8` | 0W/3D, 1258.9 s | 0W/3D, 1155.0 s | Failed controls |
| Delivery v1 `54154cd` | 0W/3D, 1285.7 s | 0W/3D, 1155.0 s | Reject promotion |
| Delivery v2 `abf76b1` | 0W/3D, 1329.6 s | 0W/3D, 1164.6 s | Execution improves; reject strength promotion |
| Selective v3 `dbf4aee` | Not run | 0W/3D, 1089.6 s | Reject promotion; no broader matrix |

The [sanitized result records](experiments/2026-10-31/targeted-oracle-archon-results.json)
retain per-game identity, replay hash, unit readiness/participation and resource
scores. These are separate opt-in settings from the previous 36-game campaign;
their results do not revise that campaign's win counts. Terran Rush and Power
have not been retested by this follow-up.

**Delivery defects fixed.** The Zerg control's Archive was ready at 541.1 s,
but its four Gateways had become Warpgates and the first-input funding path
only handled Gateway training. A bounded, legal first-input warp investment
now produces Templars. Reserved pairs rendezvous before ordinary army movement
can separate them. Native retail ability replies also omit the group merge
from individual-unit queries: an exact-two-tag diagnostic produced a ready
Archon despite that omission. The corrected group path delivered the first
ready Archon at 694.3 s in Power and 1054.3 s in Timing. Three distinct Power
Archons and one Timing Archon showed sampled weapon cooldowns. This establishes
firing participation, without attributing specific kills to them.

**Oracle use remains unproven in normal play.** The control and v1 Power games
produced their first Oracle at 902.1 s, chased distant workers and never showed
the beam buff. Partial base vision erased earlier positive worker-line memory.
The new controller retains timestamped positive lines for bounded inspection,
requires current visible workers for attacks, and separates transit from raid
timers. Delivery-v2 and selective-v3 produced no Oracle, so they do not validate
that targeting change. A separate debug-spawned Oracle/SCV diagnostic did show
beam activation and one tracked worker death; it proves local execution only.
Both [Archon](experiments/2026-10-31/archon-group-command-diagnostic.json) and
[Oracle](experiments/2026-10-31/oracle-beam-worker-diagnostic.json) diagnostics
are explicitly excluded from gameplay results and all learning archives.

**Suitability and income still need work.** Selective-v3 avoids new Archon
investment into armored-heavy ground or fresh multiple-Ghost evidence, retaining
Immortal/Colossus production and appropriate biological/air splash roles.
In Power it brought the first Colossus forward from 630.0 to 579.6 s and raised
the army resource trade ratio from 0.518 to 0.684. Yet own economy losses rose
from 4825 to 5125 and the match was still lost. Delivery-v2's Power army ratio
was lower, 0.473, while own economy losses fell to 4150 and enemy economy damage
rose from 1300 to 2800. These final engine resource scores support evaluating
income protection and economic damage alongside army exchange; neither outcome
establishes a winning tactic or an attributed Archon effect.

The earliest [flagged loss windows](experiments/2026-10-31/targeted-loss-windows.json)
precede these late units: Timing at 240–255 s
against observed Marines/Marauders, and Power at 435–450 s against observed
Roach/Ravager/Hydra/Ling forces. A low army ratio during home defense can still
be justified. The reports also show later home-economy collapse; this calls for
testing an adequate early counter and timely short regroup/re-engagement around
income, rather than imposing a universal 1:1 fight rule. Snapshot windows and
heuristic local-strength estimates do not establish the cause of every loss.

## Strategy and reconnaissance

The executable repertoire includes baseline, Zerg early Robotics, Terran
counter-tech, Terran counter-tech with local range closing, and Zerg completion
of a requested first Colossus. Selection consumes positive timestamped scouting
and own readiness, records uncertainty/evidence and expires stale choices.
Configured AI build, future state and outcome do not enter selection. Existing
operational objectives and adaptive composition remain available. Historical
experiments and their results are cataloged alongside the retained components.

V3 reconnaissance discovers Macro's expansion around 186.4 s versus 295.7 s in the
matched reference. Timing's first army contact improves from 193.9 to 174.6 s.
By 240 s, the additional worker opportunity cost is 70.7/46.1 worker-seconds for
Macro/Timing, with no confirmed worker-scout deaths through that horizon.
The final 36 average 153.1 assigned-Probe-away seconds per game; six Observer
losses are confirmed, with twelve missing entries kept uncertain.

The unchanged generic classifier scores 18.4% time-weighted configured-build label
accuracy, 22.9% commitment coverage and 0.619 Brier on the final 12 conditions.
Planned role-fit/readiness proxies are 91.8%/90.3%, measurable on 35.9% of recorded
time. These high proxies do not certify successful engagements or optimal choices.
During the first 240 s, 72.0% of time lacks the counted fresh army/tech/positive
expansion features. This includes quiet early phases and heuristic freshness
cutoffs; it is not a causal error attribution. Both information and logic need work.

## Data, software and RL handoff

- The [completed archive index](experiments/2026-10-31/observed-facts-v2-corpus-index.json)
  covers 132 distinct recordings, 111607 factual records, 1674 hashed artifacts
  (26.66 GB), and four world split groups. The
  [21-game tactical archive](experiments/2026-10-31/targeted-observed-facts-archive.json)
  contributes 23649 facts and 309 artifacts; every archived artifact/facts hash
  was checked. These starts add no independent world split group. Raw artifacts remain local and ignored
  by Git; sanitized results/provenance are committed. Draft/incomplete exports
  are excluded. All surviving historical files remain preserved.
- The `sc2-observed-facts-v2` input contract separates causal observations from
  labels, results, inferred beliefs and oracle state. A
  [legal example](examples/sc2-observed-facts-v2.json) and
  [inference plan](opponent-inference-training.md) are available. A same-loop
  replay-oracle extractor and reliable trained estimator are still outstanding.
- For the frozen final campaign, locked sync, Ruff lint/format, configured Mypy, protocol/lifecycle tests,
  **598 synthetic tests (89.41% coverage)** and package builds passed. All 49
  source/config hashes, actual binary/data, map, starts, difficulty and replay
  files passed final verification. Shared human controls remain NOT_VERIFIED.
- The [approved two-layer architecture](game-agnostic-architecture.md),
  [doctrine background](doctrine-inspired-control.md), [RL design](rl-architecture.md)
  and [environment plan](rl-training-plan.md) remain available to the user's
  separate RL session. This session supplies the SC2 data/repertoire and has not
  trained a learner. The current bot is not an accepted elite teacher.

## Next targeted work

This batch is complete; no live games remain running. First isolate a bounded
Oracle production commitment from a positively scouted worker-line opportunity,
and measure departure/reacquisition, confirmed economic damage and unit cost
before claiming harassment works. Preserve urgent supply, income recovery and
minimum home-defense force. Earlier targeted counter/splash delivery and a
separate economic-defense/local-regroup ablation address the recurring Timing
and Power loss windows. Run three matched repeats per candidate/control, reject
poor candidates early, and expand to Rush/Power and winning-build regressions
only after the targeted failure improves. The fixed specialists remain useful
controls; map/seed/community acceptance and strategy-classifier training remain
outstanding. The new PR stays separate and unpromoted.
