# Python bot status

Updated 2026-10-31 during live scouting/data collection.

The current branch contains the combined Zerg response and optional scouting
experiments. The separately successful Terran specialist still needs race-scoped
integration and regression testing. The combined elite milestone is incomplete.

## Playing strength

All results below concern built-in **VeryHard** opposition, the highest
non-cheating protocol difficulty. They do not establish human ladder rank or
strength against established community bots.

| Component | Completed evidence | Remaining qualification |
| --- | --- | --- |
| Zerg combined response, `b3aff99` | 15/15 victories: Rush, Timing, Power, Macro, Air, three repeats each | One map and seed 20261025 |
| Same Zerg gameplan, instrumented reference `2be052b` | Additional 15/15 victories across the same five builds on seed 2026103101 | Development collection, not a held-out reliability test |
| Third Zerg seed, 2026103102 | Rush and Timing triplets won; first Power repeat lost at 1237.5 s | Remaining games are running; this exposes a generalization failure |
| Terran Rush/Timing specialist, `287dbd5` | Rush 3/3 at 1090.4 s; Timing 3/3 at 1180.4 s | Separate experiment; its global version failed Zerg retention |
| Terran Power/Macro/Air in R2 | Each 3/3 in the original suite | Retest with the integrated Terran specialist |
| Protoss, additional maps, community bots | No accepted playing-strength gate | Required before elite acceptance |

These are different frozen revisions and comparison groups. Do not pool their
results into a claim that one revision won a combined Terran/Zerg matrix. Three
fixed-start repeats measure reproducibility, not three independent opponents.
R2's original full matrix was 21 wins / 9 defeats at a 1500-second bound; current
trials use 3600 seconds. The reported victories resolved before either bound.

The Terran specialist funds the requested counter-tech and closes local combat
distance when actors cannot actually fire. Earlier funding alone won Terran Rush
3/3 at 805.4 seconds but did not repair Timing. The combined counter-tech/range
variant won both targeted Terran triplets. Its Zerg losses prevent treating it as
a universal replacement; a Terran race guard and retention tests are still needed.

Evidence: [Zerg combination](zerg-scout-response-experiment.md),
[additional-seed reference](evaluations/2026-10-31-scouting-evidence-reference-newseed.md),
[Terran Timing](evaluations/2026-10-31-engagement-range-v1-20261031-terran-timing.md),
[Terran Rush](evaluations/2026-10-31-engagement-range-v1-20261031-terran-rush.md),
and the [full milestone history](hardcoded-elite-milestone.md).

## Strategic inference and scouting

The original generic five-label classifier is weak: 5.5% scenario-averaged,
time-weighted label accuracy in the first Zerg development suite, with Unknown
counted as incorrect. Configured AI build is only an evaluation/weak auxiliary
label; it is not complete truth about changing enemy intent.

Both information and logic need improvement. Expansion/tech sightings often
arrive late, while early-Pool, first-pressure and armored-force rules are too
coarse to describe overlapping strategic components. We have not established a
causal percentage of errors attributable to either factor.

The first two bounded revisit variants each retained all six Macro/Timing wins,
but an undamaged Probe turned back on a passing Drone before reaching the natural.
They did not pass the early-information objective. Faster wins alone are not
evidence of better recognition.

The current frozen third variant (`0f673b2`) withdraws on actual damage,
multiple nearby workers or army threats, and verifies visibility before marking
the inspection complete. Its first recorded trajectories discover Macro's
expansion around 186.4 seconds, versus 295.7 in the matched reference, and
Timing's first army contact around 174.6 versus 193.9 seconds. These are discovery
times, not enemy construction starts or total army truth. Match outcomes and
retention are still pending; the extra mining opportunity cost must be assessed.

## Data, software and RL handoff

- Logs/replays remain local and ignored by Git. New runs retain every debug-log
  rotation and record one-second sampled observations for collection. Old deleted
  rotations cannot be reconstructed.
- A complete [fact-schema-v2 corpus](experiments/2026-10-31/observed-facts-v2-first-corpus.json)
  contains the first 27 games, 12929 fact records and 299 hashed original
  artifacts, about 3.28 GB. Additional completed archives and live collection
  expand this. The first corpus has one world split group; repeats must stay
  together. A [legal input example](examples/sc2-observed-facts-v2.json) is checked in.
- Inputs contain causal observed facts, timestamps and missingness, with public
  map geometry. Labels, outcomes, inferred beliefs and future/oracle state are
  separate. A same-loop replay oracle-label extractor is not implemented yet;
  there is no reliable trained opponent estimator deployed in this branch.
- Latest gameplay source passed **570 synthetic tests, 89.28% coverage**, locked
  sync, lint, formatting, configured Mypy, protocol/lifecycle tests and packaging.
  Exact SC2 binary/data, map, starting fingerprints and replays are checked live.
  Shared human controls remain unverified.
- The RL model is being built in the user's other session. This session retains
  the [two-layer architecture](game-agnostic-architecture.md) and supplies SC2
  facts through its adapter. It does not implement or train the gameplay learner.

See the [opponent-inference plan](opponent-inference-training.md) for the data
contract, grouped splitting, supervision limitations and scouting experiments.

## Next work

Finish the frozen scouting and third-seed blocks; preserve every result,
including Power defeats, and diagnose the failing condition. Retain a scout
change only after it delivers useful facts at acceptable cost and retains wins.
Then integrate the Terran specialist behind an explicit race guard and run its
targeted gates followed by retention. Protoss, new-map/seed holdouts and community
opponents remain necessary before calling this an elite bot or accepted teacher.
