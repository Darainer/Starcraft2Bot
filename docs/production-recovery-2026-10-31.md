# Production recovery — 2026-10-31

Status: the original 1500-second development matrix completed with **21 wins,
9 defeats and no timeouts**. R2 is the tested production-recovery revision. At the
user's request, subsequent trials now default to **3600 game seconds (60 minutes)**;
matched extended Zerg Timing games resolved the reference's old censored result:
**reference 3 wins at 1515.4s, R2 3 defeats at 1205.4s**. This exposes a regression.
The two time horizons remain separate comparisons. Later working-tree belief and
scouting changes are experimental and are not covered by R2's match results.

## Candidate and results

`production-v5-r2-20261031` reconciles the archived v5 integration with its later
gas reservation and a priority-construction placement repair. It retains baseline
scouting and the calibrated combat estimator. It does not enable combat spells
or use configured opponent build labels as gameplay inputs.

| Frozen candidate / scenario | Result | End sample seconds |
| --- | --- | --- |
| R1 / Zerg Macro | 3 defeats; rejected | 875.4 / 815.4 / 875.4 |
| R2 / Zerg Macro | 3 wins | 1055.4 / 1055.4 / 1055.4 |
| R2 / Zerg Rush | 3 wins | 685.4 / 685.4 / 685.4 |
| R2 / Terran Power | 3 wins | 905.4 / 905.4 / 905.4 |
| R2 / Terran Air | 3 wins | 720.4 / 720.4 / 720.4 |
| R2 / Zerg Air | 3 wins | 480.4 / 480.4 / 480.4 |
| R2 / Terran Rush | 3 defeats | 1120.4 / 1120.4 / 1120.4 |
| R2 / Terran Timing | 3 defeats | 930.4 / 930.4 / 930.4 |
| R2 / Terran Macro | 3 wins | 975.4 / 975.4 / 975.4 |
| R2 / Zerg Timing | 3 defeats | 1220.4 / 1210.4 / 1225.4 |
| R2 / Zerg Power | 3 wins | 1070.4 / 1070.4 / 1070.4 |

All 30 R2 games pass their loop-zero baseline fingerprints, exact binary/map
identity, frozen-source checks and nonempty replay checks. The
[full comparison](evaluations/2026-10-31-production-v5-r2-complete.md) records the
improvement from the reference's 9 wins / 18 defeats / 3 timeouts. Results
remain tied to this candidate and its pressure profile. R1 was rejected after
its targeted failure, without spending a full matrix on it. Broader regression
testing began only after the five successful triplets.

## Repairs and evidence

The historical failing gas-release test used synthetic data in which a Robotics
Facility consumed two supply. BurnySC2 then treated its production as a morph,
subtracting the producer's price and reporting zero gas for an Immortal. The
fixture now uses zero supply for structures and explicit Robotics prices. Tests
independently assert an Immortal's 275 minerals, 100 gas and four supply, actual
resource deduction, release when a producer becomes human-owned or disabled,
and competition with the reinforcement controller. The old failing case passes
with corrected data; that alone is not gameplay improvement.

R1 revealed a separate opening stall. Once two Zealots were queued, its tech
priority stopped additional cheap purchases while the basic construction path
tried only the closest Pylon. At 170.4s it had two Zealots, two Gateways, two
Pylons and 1,075 minerals, but no Core. General construction later used rear
power after the 180-second opening bound. R2 tries every safe ready Pylon in
distance order in the priority path, using the same placement and ownership
checks. A regression case uses those captured building coordinates with blocked
front and available rear placement queries.

In the first Macro recording, Core / first Stalker completion moved from
220.4 / 255.4 seconds in R1 to 135.4 / 170.4 in R2. The R2 win reached 56 workers
and 143 army supply, with zero persistent Probe disappearances by 240 seconds.
Its first Immortal still arrived around 520.4 seconds: the result does not show
that every tech or production timing is solved. Five-second observations locate
these windows; they are not exact replay UI review or simulated counterfactuals.

## Infrastructure and validation

Windows application control blocked the generated CLI executable (4551).
Setup and Start now invoke the same CLI as a Python module, and their native
PowerShell tests verify quoting, execution from another folder and exit handling.
The [runtime record](evaluations/2026-10-31-runtime.md) preserves exact ping
identity and the pending human-control checks.

Two simultaneous retention runners chose the same timestamp and collided on
report paths. All six attempts are invalid: two startup failures and four
intentionally stopped owned clients. Mixed raw artifacts and explicit abort
records remain local; none count in the results table. Replacement runs use
distinct start times. The main runner now adds a UUID to artifact prefixes,
covered by a synthetic test forcing two concurrent runners onto the same clock.
Concurrent invocations still require distinct summary `--output` paths.

Main-checkout software checks passed after adopting the integration: locked sync,
Ruff lint/format, configured mypy, **454 tests with 92.78% coverage**, and
source/wheel builds. Isolated R2
passed its corresponding full checks with **453 tests and 92.78% coverage**.
Configured mypy covers the SDK-independent configuration/ownership module. The
adopted gameplay source matched frozen R2 after newline normalization at that
checkpoint, with later UUID naming and the 3600-second default in the trial
runner. Subsequent ontology, belief, scouting and director changes are a separate
experimental revision. The original matrix explicitly passed 1500 seconds; the
longer paired comparison explicitly passes 3600 seconds. See the
[strategy baseline](evaluations/2026-10-31-strategy-belief-baseline.md) and
[RL architecture](rl-architecture.md) for that follow-up's measurement contract.

## Reproducibility and limits

The [source archives and manifests](experiments/2026-10-31/README.md) contain
complete deltas against clean `9fd64a1`; archive reconstruction was verified.
The previous draft scouting retries remain in checkpoint `b3deb3a` and are not
part of this candidate. Dependency pins, optional spell switches and gameplay
source stayed frozen within every valid R2 batch.

The original matrix uses pressure, VeryHard, BelShirVestigeLE, game/Python seed
20261025, eight-loop observations, a 1500-second bound and three repeats per
explicit race/build. The user subsequently requested a 3600-second bound to
resolve long games; the paired reference/R2 Zerg Timing triplets use that bound
and the same remaining settings. Concurrency stays within the approved
eight-client ceiling; no
matched throughput improvement is claimed. These repeated fixed starts are
development conditions, not independent held-out scenarios. Shared human input,
elite strength and the proposed multi-map/multi-seed holdout remain unverified.
