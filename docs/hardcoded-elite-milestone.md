# Hardcoded bot milestone

Requested 2026-10-31: complete the Python rule-based bot's playing-strength
milestone before implementing or training the RL policy. The RL architecture
remains a later-stage design. The rule bot can eventually supply teacher games,
failure examples and a frozen training opponent; it is not yet an accepted expert.

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
retains the comparison with the winning reference. Broader retention is running
on that same frozen revision. Terran Rush and Timing still lose their triplets;
the targeted repair has not solved those separate failures.

One eight-client Terran Power attempt exited before API startup with `0x20010000`.
Full Access and `ryanpc\\ryanj` were rechecked; other clients launched in the same
context. Its artifacts remain labeled as infrastructure failure. The valid
games finish normally; the missing Power repeat is retried alone before the
Zerg retention block. No launch-code or gameplay change is made to explain that
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
lost 3/3 at 845.4 seconds. Zerg Macro retention is running on the same frozen
candidate. This candidate is not yet accepted as a global replacement.

Counter-tech's Zerg Macro triplet then lost 3/3 at 855.4 seconds. The next
observed-force wave-readiness experiment also lost Terran Timing 3/3 at 1055.4;
it changes survival time, not the resolved outcome, and is rejected as a repair.
The damage-aware focus prototype is retained as an unpromoted patch: coarse
recorded-state inspection found no changed Immortal targets in the sampled
ready-to-fire opportunities, so it was not treated as a demonstrated solution.
The [bot-tactics research](research/winning-bot-tactics.md) prioritizes range-aware
approach and actual firing participation next.

The validated baseline is checked in on `feat/hardcoded-baseline-20261031`:
runtime/trial fixes, R2 gameplay and passive belief/metric instrumentation.
An isolated checkout of commit `67ed0f7` passed all locked checks and **492 tests,
88.54% coverage**. Experimental early-tech and wave rules are kept on separate
branches rather than being presented as accepted gameplay.

The saved Timing recordings show the winning reference's first Robotics Facility
around 180.4 seconds and first Immortal around 270.4. R2 reaches them around
475.4 and 530.4, despite a faster first Stalker. The next hypothesis to investigate
after the current batch is funding the first attainable Robotics investment
without starving opening defenders, income, supply, or an emergency response.
Actual trades and resolved outcomes decide whether that repair is useful.

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
