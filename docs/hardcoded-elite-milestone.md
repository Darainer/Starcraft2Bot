# Hardcoded bot milestone

Requested 2026-10-31: complete the Python rule-based bot's playing-strength
milestone before implementing or training the RL policy. The RL architecture
remains a later-stage design. The rule bot can eventually supply teacher games,
failure examples and a frozen training opponent; it is not yet an accepted expert.

The separate [RL training plan](rl-training-plan.md) covers that later teacher
pipeline, public opponents and the proposed headless container environment.
The approved [two layer design](game-agnostic-architecture.md) places the
[doctrine framework](doctrine-inspired-control.md) in a game-agnostic reasoning
core and SC2 mechanics/execution in its game-specific adapter. The architecture
can support other games; individual mechanisms and transfer still need evidence.
The hardcoded milestone continues before implementing or training the learner.

## Working benchmark

The user selected **both built-in AI reliability and established community bots**,
with built-in reliability as the first gate. The first target is reliable
performance against the strongest non-cheating built-in AI, expressed as
`Difficulty.VeryHard` in the protocol. Blizzard's [difficulty enumeration](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto)
lists three stronger cheating variants separately. Built-in-AI results establish
performance against that opponent pool; they do not establish a human ladder rank
or competitive community-bot strength.

The proposed acceptance gates are:

1. Repair each of the three failing development conditions: Zerg Timing,
   Terran Rush and Terran Timing. Use three explicit repeats per frozen candidate;
   reject failures before broader regression. Compare Zerg Timing with the
   winning extended reference as well as R2.
2. Retain the seven established winning conditions and complete the ten-condition
   Terran/Zerg development matrix with 30 resolved victories at the longer bound.
3. Extend development coverage to Protoss's five explicit builds, three repeats
   each. Freeze the resulting rule bot before holdout evaluation.
4. Predeclare a holdout manifest covering all three opponent races, all five
   builds, two additional maps and three unused seeds: at least eighteen distinct
   conditions, each with three reproducibility repeats. Target at least 90%
   resolved wins overall and no race below 80%. Publish every outcome, per-condition
   results and uncertainty about generalization; repeated starts are not
   independent opponents. Failed holdouts become development data and require
   a new untouched holdout before acceptance.
5. Preserve ownership, resource and opt-in-ability invariants; pass the required
   software checks and retain exact source, settings, ontology, map and binary
   identities. Keep a frozen teacher snapshot with its limitations and failures.

6. Then evaluate against frozen established community bots. Record their source/
   release identities and selection/rating evidence, use matched local games on
   held-out maps/seeds, and publish per-opponent/race results. Select that opponent
   pool and acceptance threshold before examining its test outcomes. Count actual
   SC2 clients, including both participants where the environment needs two.
   Built-in AI wins alone cannot complete the combined milestone.

These thresholds define the first engineering acceptance target, not a claim of
statistically proven ladder strength. Community evaluation is mandatory before
the combined elite milestone or RL teacher is accepted. Publishing/uploading a
bot or registering a competition account is a separate action from local testing.

## Current evidence and next repair

Latest experiment: the [scout-driven Zerg response](zerg-scout-response-experiment.md)
combines R2 baseline spending with evidence-selected early Robotics, on its own
branch at `b3aff99`. All six relevant historical winning games were verified as
actual VeryHard computer opposition in runtime and game-info records. The
candidate passed 526 synthetic tests and required software checks. Its frozen
Macro/Timing gate completed with **six victories**: Macro 3/3 at 1145.4 seconds,
Timing 3/3 at 1050.4. Retention then completed on the same source with Rush,
Power and Air all 3/3, for **15/15 Zerg development victories** at the 3600-second
bound. All starts, source hashes, map/binary identities, actual
VeryHard difficulty and replays were verified. Opening evidence selects Timing's
early Robotics; Macro keeps baseline opening spending and responds later to
observed Roaches. Macro is 90 seconds slower than R2 but retains victory.
Rush/Power/Air finish times match R2. This passes the Zerg development component;
Terran/Protoss regression, holdouts and community opponents remain outstanding.
The existing generic strategy classifier remains weak (5.5% time-weighted label
accuracy across these five conditions); action selection success is not proof
of accurate intent classification. The response and build-suitability diagnostics
are recorded separately in the linked experiment report.
Two initial preflights failed before connection with `0x20010000`; after the user
closed the ordinary SC2 client, unchanged preflight passed. These launch failures
remain separate from gameplay outcomes.

R2 completed the original shorter-bound matrix with 21 wins and nine defeats.
At the new 3600-second bound, the reference wins Zerg Timing 3/3 at 1515.4 seconds;
R2 loses 3/3 at 1205.4 seconds. The later belief/scouting revision has synthetic
coverage but failed its first live gate: `belief-gate-v1-20261031` lost all three
Timing games at 820.4 seconds. Starts, exact map/binary, replays and frozen source
passed verification. The candidate is rejected without broad regression.
The next frozen triplet, `robotics-fund-v1-20261031`, restores R2 control while
retaining belief telemetry and funds the first attainable Robotics investment.
Its new tests cover income, opening supply, emergencies, permissions, builder
ownership, placement/path failures and resource charging. Main software validation
before launch: 507 tests, 88.51% coverage, locked sync/lint/format/mypy/build.

| Frozen gate | Zerg Timing result | Decision |
| --- | --- | --- |
| Belief/scouting v1 | 3 defeats at 820.4s | Reject; preserve experimental controller and telemetry |
| Robotics funding v1, twelve completed fighting supply | 3 defeats at 490.4s | Reject; counter arrived after the critical attack |
| Robotics funding v2, six completed fighting supply | 3 victories at 1050.4s | Target improved; run retention before promotion |

V2 completes Robotics around 195.4 seconds and its first Immortal around 265.4,
versus R2's 475.4/530.4. It reaches 111 army supply and trades about 1.71 army
resources killed per resource lost in the representative recording. All three
starts, source hashes, map/binary identities and nonempty replays are verified.
The [triplet report](evaluations/2026-10-31-robotics-fund-v2-20261031-zerg-timing.md)
retains the comparison with the winning reference. Broader retention subsequently
completed on that same frozen revision. Terran Rush and Timing still lose their triplets;
the targeted repair has not solved those separate failures.

One eight-client Terran Power attempt exited before API startup with `0x20010000`.
Full Access and `ryanpc\\ryanj` were rechecked; other clients launched in the same
context. Its artifacts remain labeled as infrastructure failure. The valid
games finished normally; the missing Power repeat was retried alone and won
before the Zerg retention block. No launch-code or gameplay change was made to explain that
isolated failure, and it does not count as a defeat.

The Terran Rush recordings reveal a separate delivery gap: 163 sampled decisions
request Colossi with a Robotics Facility present and no Robotics Bay, yet none
of those samples has the combined 150-mineral/150-gas Bay budget. Under pressure,
the construction filter also excludes the Bay. This motivates a focused
counter-tech funding experiment after retention finishes. It is not a proven
explanation of every lost battle.

The Robotics v2 matrix subsequently completed at **18 wins / 12 defeats** with
all thirty starts, frozen hashes and replays verified. Zerg Macro regressed to
three defeats at 840.4 seconds and Power to three defeats at 1620.4. It is rejected
globally despite its three Timing victories. Macro had already reached three
bases and 56 workers before its army collapsed; the depleted-base worker-gate
failure seen in Power must not be substituted as the explanation for Macro.

`counter-tech-v1-20261031` funds the requested Bay and first Colossus, permits the
counter prerequisite under pressure, and preserves a basic-force emergency floor.
It passed 515 tests with 88.53% coverage and all locked checks. Its targeted
Terran Rush triplet won 3/3 at 805.4 seconds, with first Bay/Colossus at
465.4/550.4 and a representative peak of 91 army supply. Terran Timing still
lost 3/3 at 845.4 seconds. Zerg Macro then lost 3/3 at 855.4 seconds on the same
frozen candidate. It is not accepted as a global replacement. The next
observed-force wave-readiness experiment also lost Terran Timing 3/3 at 1055.4;
it changes survival time, not the resolved outcome, and is rejected as a repair.
The damage-aware focus prototype is retained as an unpromoted patch: coarse
recorded-state inspection found no changed Immortal targets in the sampled
ready-to-fire opportunities, so it was not treated as a demonstrated solution.
The [bot-tactics research](research/winning-bot-tactics.md) prioritizes range-aware
approach and actual firing participation next.

The [siege-approach experiment](evaluations/2026-10-31-siege-approach-v1-20261031-terran-timing.md)
at gameplay commit `90f5277` then lost Terran Timing 3/3 at 910.4 seconds and was
rejected without broader retention. It detects visible Tank weapon envelopes
before the old anchor-distance check, scores short formation moves for exposure
and allows a bounded deliberate assault. Its representative recording includes
the new approach and commit phases, but the army still collapses. It passed
521 synthetic tests (88.64% coverage) and all required software checks.

An independent reachable-expansion candidate (`e9da001`) addresses Power's
depletion deadlock by capping the worker gate at attainable saturation minus two,
with a sixteen-worker floor and a positive-resource destination check. Its parent
and candidate Power triplets both won 3/3 at 3600 seconds, ending at 820.4 and
1245.4 respectively. The candidate delayed expansion because unseen resource
amounts were treated as empty. It is not promoted. Software validation passed
525 tests (88.55% coverage), locked checks and builds. The next variant preserves
the distinction between unknown and depleted minerals and is evaluated on the
earlier Robotics-only revision that actually suffered the depletion stall.

That [depletion variant](evaluations/2026-10-31-depletion-recovery-v1-20261031-zerg-power.md)
(`4af6e8d`) lost Power 3/3 at 1120.4/1120.4/1135.4 and is rejected. It moved the
initial third-base investment earlier, weakening the representative midgame;
fixing a reachable gate did not establish better play. The
[parent subset](evaluations/2026-10-31-robotics-fund-v2-zerg-power-reference.md)
also corrects the chronology: the parent built its initial third, then lost one
base and exhausted its remaining lines. Pressure's three-base ceiling and
56-worker cap separately prevent reaching the old fourth-base gate of 58.

A minimal subsequent configuration experiment keeps the original gates and
Robotics-v2 gameplay, raising pressure to four bases and seventy workers. This
tests preemptive fourth-base income, not recovery from an already empty bank;
its [Power triplet](evaluations/2026-10-31-sustainable-pressure-v1-20261031-zerg-power.md)
lost all three games at 1780.4 seconds. It never starts a fourth Nexus and is
rejected as a repair. The full fingerprint differs only in the two declared
assistant settings; world starts remain identical. This is a configuration
ablation with its own comparison group, not a claim of unchanged settings.

A subsequent engagement-range candidate (`287dbd5`) is based on counter-tech,
excluding the rejected expansion/siege/wave drafts. It lets out-of-range actors
close on a local visible combat contact during an engaged wave; the old anchor
slots can leave them unable to fire. Recorded-state inspection found this gap
in 29 of 38 ready actor-samples across the representative Timing engagement
samples, mostly Zealots; these are correlated snapshots, not independent fights.
The candidate passed 521 tests (88.58% coverage) and required checks. Its
[Terran Timing triplet](evaluations/2026-10-31-engagement-range-v1-20261031-terran-timing.md)
won 3/3 at 1180.4 seconds, versus the parent's three defeats. Starts, source,
binary/map identities and replays pass verification. Subsequent frozen triplets
won [Terran Rush](evaluations/2026-10-31-engagement-range-v1-20261031-terran-rush.md)
3/3 at 1090.4, but lost [Zerg Macro](evaluations/2026-10-31-engagement-range-v1-20261031-zerg-macro.md)
3/3 at 1010.4/1005.7/1130.4 and [Zerg Timing](evaluations/2026-10-31-engagement-range-v1-20261031-zerg-timing.md)
3/3 at 675.4. The composite is not promoted; no full matrix is spent confirming
those failures. Counter-tech already lost Macro, and its own Timing condition
has not been isolated, so the Zerg losses cannot be assigned entirely to the
range change. These are experimental Terran successes, not a global solution.

The validated baseline is checked in on `feat/hardcoded-baseline-20261031`:
runtime/trial fixes, R2 gameplay and passive belief/metric instrumentation.
An isolated checkout of commit `67ed0f7` passed all locked checks and **492 tests,
88.54% coverage**. Experimental early-tech and wave rules are kept on separate
branches rather than being presented as accepted gameplay.

The saved Timing recordings motivated the earlier Robotics investments above:
the winning reference's first Facility/Immortal arrive around 180.4/270.4 seconds,
versus R2's 475.4/530.4. That delivery gap is real, but the subsequent regressions
show why tech timing alone cannot establish a global improvement. Actual trades,
army participation and resolved outcomes must decide the next repair.

## Evaluation discipline

Every subsequent game uses a 3600-game-second bound unless an explicitly distinct
experiment says otherwise. Timeouts remain censored; they are not victories or
defeats. Use at most eight live clients, identical starts within matched groups,
explicit opponent builds and separate artifacts per frozen revision. Finish a
targeted batch before tuning. A better proxy or faster tech completion cannot
substitute for a resolved improvement and retention of existing winners.

The [strategy baseline](evaluations/2026-10-31-strategy-belief-baseline.md) separates
opponent recognition, intended counter-role fit, delivered readiness and tech
availability. Those measurements diagnose failures; none alone certifies playing
strength. Autonomous performance and shared human-control acceptance remain
separate, with human control still unverified.


## Final integration and stopping point

The [comprehensive final report](final-bot-report-2026-10-31.md) records the
integrated repertoire at `d0f8cf3`: **24W/12D/0T across 36 games**. Main-seed Zerg
finished 12W/3D and Terran 6W/9D; the additional known-failure Zerg Power/Macro
block won 6/6, including Power victories at 1954.3 s under the 3600-second bound.

The main-seed Power and Terran regressions reject global promotion. Earlier
Zerg 15/15 blocks and the separate Terran Rush/Timing 6/6 specialist remain tied
to their own frozen revisions. The repertoire and negative results are preserved
on the feature branch. The elite milestone remains incomplete; work stopped
after the final set and report at the user's request.
