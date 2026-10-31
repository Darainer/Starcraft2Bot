# Python bot status

Final snapshot, 2026-10-31. Evaluation and improvement work stopped after the
requested final set and report.

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
  covers 111 distinct recordings, 87958 factual records, 1365 hashed artifacts
  (21.15 GB), and four world split groups. Raw artifacts remain local and ignored
  by Git; sanitized results/provenance are committed. Draft/incomplete exports
  are excluded. All surviving historical files remain preserved.
- The `sc2-observed-facts-v2` input contract separates causal observations from
  labels, results, inferred beliefs and oracle state. A
  [legal example](examples/sc2-observed-facts-v2.json) and
  [inference plan](opponent-inference-training.md) are available. A same-loop
  replay-oracle extractor and reliable trained estimator are still outstanding.
- Locked sync, Ruff lint/format, configured Mypy, protocol/lifecycle tests,
  **598 synthetic tests (89.41% coverage)** and package builds passed. All 49
  source/config hashes, actual binary/data, map, starts, difficulty and replay
  files passed final verification. Shared human controls remain NOT_VERIFIED.
- The [approved two-layer architecture](game-agnostic-architecture.md),
  [doctrine background](doctrine-inspired-control.md), [RL design](rl-architecture.md)
  and [environment plan](rl-training-plan.md) remain available to the user's
  separate RL session. This session supplies the SC2 data/repertoire and has not
  trained a learner. The current bot is not an accepted elite teacher.

## Stopping point

No further tuning or evaluation batches are running from this session. Future
priorities, if resumed, are matched fixed-versus-auto/recon ablations, improved
investment commitment and combat suitability, richer strategy estimation, and
untouched map/seed/community gates. The baseline and specialized branches remain
preserved; no candidate is promoted merely because its software checks pass.
