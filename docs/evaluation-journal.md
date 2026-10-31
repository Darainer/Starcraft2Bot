# Evaluation journal and opponent assessment

## 2026-10-31: first recurrent PPO infrastructure pilot

The [frozen RL pilot](evaluations/2026-10-31-rl-pilot-v1.md) ran three initial-policy,
three trained-policy and three rule-reference games against explicit VeryHard
Terran Rush at the 3600-second bound. Every start matched; every group lost all
three. The learner produced and reloaded a checkpoint after four KL-bounded
updates, but it failed its targeted win-rate gate and is not promoted. A separate
corrective source passed three live timeout/reset checks and one explicitly
aborted cleanup check. See the linked evidence for source/checkpoint/binary/map
identities, CPU measurements and pending human-control acceptance.

This is the running record of gameplay changes, controlled evaluations, and the
remaining explanations to test. Detailed match evidence stays in local logs and
replays; checked-in reports summarize it without personal paths. The current
historical record is [performance verification](performance-verification.md).

## Completed baseline: 2026-10-25, gameplay af603e0

Thirty games: pressure versus VeryHard Terran/Zerg, three fixed-seed repeats of
Rush, Timing, Power, Macro and Air. Seed 20261025, BelShirVestigeLE, eight loops per
observation, 1500 game-second bound. Results: **9 wins, 15 defeats, 6 timeouts**.
All starts and repeat outcomes matched within each scenario; all replays exist.
Five concurrent Windows clients work. No controlled net-speedup claim is made.

- Wins: Terran Air, Zerg Macro, Zerg Air, each 3/3.
- Defeats: Terran Rush/Timing and Zerg Rush/Timing/Power, each 0/3.
- Timeouts: Terran Power/Macro, each 3/3 reached the bound.
- Worker recovery: gas allocation no longer freezes the mineral economy after
  casualties. Terran Rush still loses; longer survival is not a win-rate gain.
- Regression: prior Terran Timing won 3/3; this revision lost 3/3. Early warning
  and defense behavior need investigation before claiming strategic improvement.
- Scouting gap: Zerg Rush's warning at 135.4 seconds followed home contact at
  125.4. The Probe returned without identifying production tech. Returning after
  danger currently marks the opening scout complete even if inspection failed.
- User observation: expansion attacks work well, but units reverse direction in
  midfield. Recorded targets switch among search sites and bases within seconds;
  advance/regroup changes also occur around a single cohesion threshold.

## Implementation plan: movement stability and measurable opponent inference

1. Preserve a bounded commitment to the current offensive target through brief
   visibility changes, including a safe transition from pressure to containment.
   Immediate defense, genuine retreat, cleared targets, and failed objectives
   still interrupt. Confirmed expansion opportunities can replace speculative
   scouting destinations. Keep expansion scouting and target valuation intact.
2. Add separate stop/resume cohesion thresholds. Count fighting supply consistently
   in numerator and denominator; support units currently produce ratios above one.
   Test target/formation transitions across consecutive observations and measure
   target reversals and advance/regroup changes in saved and live sessions.
3. Add a pure opponent-strategy model driven only by player-visible scouting
   evidence and its timing. Return probabilities, a primary category or Unknown,
   supporting observations, and current tactical indicators. Keep its initial
   integration observational until measured accuracy justifies control changes.
4. Evaluate against the configured AI build **only outside the model**. Report
   confusion matrices, class recall, coverage/abstention, conditional accuracy,
   probability error, and detection timing at fixed game-time horizons. The AI
   setting is a reproducible reference label, not proof of every tactic the AI
   actually used. Fixed-seed repeats are grouped; never split identical repeats
   across training and validation or call them independent examples.
5. Generate detailed match reviews: matchups, resource trades, costly engagement
   windows, economic damage, expansion pressure, scouting coverage, and movement
   instability. Separate observed associations from explanations requiring another
   experiment. Score high-water corrections and five-second sampling limit the
   precision of individual fight attribution.
6. Run the required synthetic gates, commit the implementation, freeze gameplay,
   and repeat the same thirty scenarios with up to five clients. Compare both
   movement stability and wins/trades; fewer reversals alone does not prove better
   tactics. Publish the classifier's measured limits even if accuracy is poor.

## Implementation and closeout: 2026-10-25

Steps 1-5 are implemented. The director retains an offensive target across brief
visibility and mode changes, with a 20-second commitment and emergency overrides.
Confirmed economic targets can replace speculative destinations. Army cohesion
now counts fighting supply consistently, continues advancing at 70%, and resumes
after regrouping at 80%. Regrouping holds a fixed anchor and cancels obsolete
outbound orders for units already at their holding point.

The new `opponent_strategy.py` component consumes only scouting evidence and
timestamps. It records a five-category belief, Unknown/abstention, confidence,
evidence, and current tactical indicators. It does not control tactical decisions.
The configured opponent build enters only the offline evaluator. Repeated sightings
do not multiply confidence, and stale or missing vision can cause abstention.

The [detailed baseline report](evaluations/2026-10-25-af603e0.md) now covers all
30 completed games: outcomes, estimated army trades, economic damage, costly
15-second windows, unit disappearances, enemy composition, objectives, movement
reversals, action rejections, and strategy classification. Loaded passengers stay
tracked so boarding a transport is not counted as a casualty. Score corrections,
transformations, and five-second sampling still limit exact fight attribution.

Findings from the ten distinct fixed scenarios:

- Zerg Air and Macro wins combine favorable estimated army exchanges (4.86 and
  1.70 killed/lost) with substantial economic damage (4675 and 9250 resources).
  Terran Air wins also inflict substantial economic damage (12050). This is
  consistent with effective pressure; it does not isolate expansion denial as
  the cause of victory.
- Terran Power/Macro timeouts have poor army exchange ratios (0.39 and 0.21).
  Their costly windows include sieged tanks and large bio armies, with losses
  sometimes continuing during recovery. Zerg Power loses with a 0.09 ratio.
  Rush/Timing losses and the earlier Terran Timing regression remain unresolved.
- Baseline movement includes 50 advance/regroup changes in the representative
  Terran Air victory and 10 short target reversals against Terran Power. These
  are comparison metrics for the movement fix, not proof every reversal was wrong.
- The observational classifier is not accurate enough to drive strategy. At the
  final sample it scores 10% accuracy, 20% coverage, and 50% conditional accuracy;
  eight of ten scenarios are Unknown. At 360 seconds it scores 55.6% accuracy
  across nine eligible scenarios. The configured opening build and late-game
  composition can differ. Confidence is heuristic and uncalibrated; no held-out
  accuracy claim is justified by this development matrix.

An offline controller benchmark processed 219 recorded observations (up to 212
own units), proposing 5756 orders with zero ownership/duplicate-order violations.
Total controller p95 was 9.486 ms, maximum 20.005 ms. This measures CPU cost on
recorded state; it does not simulate the effects of the changed orders.

Final local checks passed: locked dependency sync, Ruff lint and formatting,
the configured mypy ownership/configuration boundary, **324 tests with 92.33%
coverage**, and source/wheel builds. Tests include consecutive movement decisions,
urgent target overrides, ownership, classifier label isolation and stale evidence,
time-horizon evaluation, score corrections, and transport passenger accounting.

The user requested closeout, a commit, and a PR before a new live matrix began.
All existing game sessions have ended. The fresh 30-game comparison for the latest
movement implementation remains **unverified**, and no new win-rate improvement
is claimed. Step 6's live comparison is explicitly deferred in the PR. The next
evaluation should freeze the committed gameplay revision and reuse the same
settings, three repeats per scenario, and up to five concurrent clients.

Generate future detailed reports with:

```powershell
uv run --locked python -m source.evaluate_matches --matrix logs/movement-matrix-fixed.json --revision <gameplay-commit> --output docs/evaluations/<date-commit>.md --json-output logs/evaluation-<commit>.json --compare logs/evaluation-af603e0.json
```

Keep raw recordings and JSON evaluations local; commit the Markdown findings and
update this journal after each completed frozen matrix.

## Matched movement baseline and next plan: 2026-10-27

**Stopped after baseline evaluation at the user's request. No gameplay tuning
was implemented.** Gameplay stayed frozen at `9fd64a1` for all thirty games.
The [full comparison](evaluations/2026-10-27-9fd64a1.md) and
[runtime acceptance record](evaluations/2026-10-27-runtime.md) retain the evidence.

Pressure, BelShirVestigeLE, VeryHard, seed 20261025, eight-loop observations,
1500-second limit, three repeats per explicit race/build: all match the previous
`af603e0` suite. Every loop-zero fingerprint matched across revisions; all thirty
reports ended successfully and all replays exist. The first triplet used three
clients, followed by five; the user subsequently requested more concurrency, and
overlapping batches reached eight. There is no controlled throughput claim.

| Opponent / build | `af603e0` | `9fd64a1` |
| --- | --- | --- |
| Terran Rush | 3 defeats | 3 defeats |
| Terran Timing | 3 defeats | 3 defeats |
| Terran Power | 3 timeouts | 3 wins |
| Terran Macro | 3 timeouts | 3 defeats |
| Terran Air | 3 wins | 3 wins |
| Zerg Rush | 3 defeats | 3 defeats |
| Zerg Timing | 3 defeats | 3 timeouts |
| Zerg Power | 3 defeats | 3 defeats |
| Zerg Macro | 3 wins | 3 defeats |
| Zerg Air | 3 wins | 3 wins |

The total changed from **9 wins / 15 defeats / 6 timeouts** to
**9 wins / 18 defeats / 3 timeouts**. Both win rates are 30%; timeouts remain
non-wins. The movement revision trades a new winning matchup for a previously
winning matchup. It is not an overall playing-strength improvement on this suite.
All triplets matched outcomes, but Zerg Power end samples varied between 785.4
and 795.4 seconds, with trade ratios of 0.09-0.14, despite identical starts.
These are ten development conditions,
not thirty independent scenarios, and exact trajectory determinism is not claimed.

The following representative metrics come from the first recording per scenario;
all three repetitions remain available in the detailed JSON review:

- Terran Power improved from a 0.39 to 1.13 estimated army exchange ratio and
  now wins. Short target reversals dropped from 10 to 2.
- Zerg Macro regressed from a 1.70 to 0.24 army exchange ratio and from 9250 to
  450 estimated economic damage. Short target reversals fell from 5 to 0,
  demonstrating why fewer reversals are insufficient as an acceptance criterion.
  The 585-615 second windows record 5325 army resources lost and no army resources
  killed, entirely during `recover`. The earlier 405-420 second window is also a
  candidate for inspecting how the unfavorable engagement began.
- Terran Macro now loses with a 0.14 exchange ratio (previously 0.21); its first
  costly window at 450-465 seconds also occurs during `recover`. Zerg Power still
  loses with a 0.14 ratio. Local fight selection and retreat remain unresolved.
- Zerg Rush still has an opening information gap: the Probe is marked returned
  around 85.4 seconds and opening-complete without observing enemy tech. Home
  contact occurs at 125.4 seconds, before the warning at 135.4. First completed
  Zealot/Stalker samples remain 145.4/200.4 seconds. Eight Probe disappearances
  by 240 seconds have no later reappearance (previously seven); this is sampled
  evidence, not an exact replay-confirmed kill count.
- Zerg Timing now reaches the limit with a 3.01 exchange ratio and 8050 estimated
  economic damage. The final sample reports 145 army supply, but 33 of 33 Probes
  idle and no gas bank. Both owned Assimilators are depleted, both Nexuses have
  zero ideal harvesters, and other nearby geysers retain gas. Later observations
  also show repeated travel between search sites. Finishing and depletion handling
  warrant separate investigations; favorable cumulative trades did not produce
  a completed win.

The observational classifier still has only 10% final accuracy across the ten
distinct conditions (40% coverage). Its output remains unsuitable for controlling
strategy on the evidence available here.

Five-second samples locate review windows, not the exact decisive instant or
causal mechanism. Replay UI inspection was not completed. No alternative policy
outcome has been simulated, and no human input acceptance is inferred.

### Proposed work, in evidence order — not implemented

1. **Diagnose and repair the lost Zerg Macro win before broad tuning.** Inspect
   matched replays around 390-420 and 570-630 seconds, then the Terran Macro
   435-480 second window. Follow individual retreat orders, terrain access and
   mission transitions. Distinguish target commitment/cohesion effects from a
   retreat route through enemy fire. Use one targeted candidate at a time; if the
   replay does not isolate the mechanism, evaluate target-commitment and cohesion
   ablations separately. Preserve `af603e0` and `9fd64a1` as distinct references.
   Acceptance: restore Zerg Macro 3/3 while retaining Terran Power, Terran Air and
   Zerg Air at 3/3 each; substantially reduce the recovery losses. Reduced reversal
   counts alone do not pass. This would establish at least 12/30, not elite play.
2. **Make early defense an explicit opening policy.** First correct incomplete
   reconnaissance status and safely retry an interrupted inspection; evaluate that
   candidate before changing spending. Then introduce opening steps with observed
   completion conditions, defensive branches and protected placement. The concrete
   Zerg Rush target is useful completed defense by first contact near 125 seconds,
   earlier warning, and fewer persistent Probe losses by 240 seconds, with economy
   retained in the non-rush scenarios. Do not treat an uninspected enemy base as
   safe or let the observational build classifier choose strategy.
3. **Improve engagement and retreat evidence after the regression mechanism is
   understood.** The continuing Terran Timing/Macro and Zerg Power losses justify
   local participation, weapon reach/domain, terrain access, splash, static defense
   and stale reinforcement evidence. Add reachable retreat destinations and threat
   costs as separately evaluated behavior changes. Cover safe routes, incompatible
   weapons, unseen reinforcements and consecutive mission transitions synthetically;
   judge live army exchanges and losses during recovery, not just heuristic scores.
4. **Turn the Zerg Timing timeout into a win.** Review the last 600 seconds for
   repeatedly abandoned search destinations and loss of progress toward surviving
   structures. Keep expansion denial, retain a viable main force when raiding, and
   preserve emergency overrides. Separately address depleted-base income: currently
   depleted gas buildings still count against construction limits, while low local
   saturation and worker-count expansion gates can prevent recovery. Test mined-out
   bases and replacement gas explicitly. Require completed wins under the existing
   1500-second limit; extending the limit is not an improvement.
5. **Only then broaden economy and ability work.** Schedule gas and production
   against actual spending/income, with defense readiness retained. Test Guardian
   Shield and then Blink in separate ability-on/off matrices with explicit switches,
   prerequisite/target checks and command arbitration. Do not add spellcasters or
   tune multiple behaviors merely because the previous candidate had fewer idle
   facilities. Keep every action behind `issue` and retain ownership/reservations.

The original proposal required a complete matched 30-game matrix for every
candidate. The user superseded that requirement on 2026-10-27: freeze each
candidate and first finish three repeats of its targeted failure; reject poor
candidates early. Only demonstrated improvements proceed to retention checks and
broader regression testing. Compare against the frozen references using
configuration identities and comparison-group IDs; resolve infrastructure
failures and report timeouts as non-wins. The larger milestone remains 24/30
while retaining previously winning groups, followed by the frozen 225-game
three-race/three-map/five-seed holdout with at least 80% overall and 70% per race.
That holdout has not been selected or run. Community-bot competition, public ladder
submission and an RL opponent pool remain deferred until fundamentals improve.

### Offline reporting changes and verification

Evaluation JSON now has schema version 2 and a versioned manifest with resolved
configuration hashes, comparison-group IDs, scenario counts, repeat counts and
starting fingerprints. Optional completeness checks reject incomplete/mismatched
groups; legacy JSON remains readable. Reports add first defensive-unit completion,
first costly army windows, early Probe disappearances, and supply/production idle
metrics. Temporary Probe absences that later reappear (such as gas harvesting)
are retracted; loaded passengers are also retained. These reporting changes do not
change playable observations, strategy, macro or tactics.

Both revisions were reviewed with the same updated analysis. The local evidence
is `logs/evaluation-af603e0-v2.json`, `logs/evaluation-9fd64a1.json`, their generated
manifests, and `logs/movement-9fd64a1-complete.json`. Raw logs/replays remain ignored.
Locked sync, Ruff lint/format checks, mypy, **329 tests with 92.29% coverage**, and
source/wheel builds passed. No gameplay code, dependency pins or optional ability
settings changed during this evaluation.

## Autonomous repair evaluation — 2026-10-27, in progress

The user subsequently authorized implementation without further questions,
parallel agents, and a global limit of eight live SC2 clients. Full Access now
reaches the default runner. Independent candidates use isolated source snapshots;
each restores `9fd64a1` gameplay except its named changes. Frozen source and
orchestration hashes, explicit settings, loop-zero fingerprints and saved replays
are checked for every complete matrix. Raw provenance stays under `.local/` and
`logs/`; candidate labels identify uncommitted source snapshots, not Git commits.

| Candidate | Wins | Defeats | Timeouts | Decision |
| --- | ---: | ---: | ---: | --- |
| `9fd64a1` reference | 9 | 18 | 3 | Frozen comparison reference |
| `retreat-v1` | 6 | 13 | 11 | Rejected as an improvement |

The [first retreat report](evaluations/2026-10-27-retreat-v1.md) records all thirty
games. It wins Terran Timing 3/3, retains Terran Air 3/3, but loses Terran Power
(two timeouts and a defeat) and converts Zerg Air wins into three timeouts.
Zerg Macro and Power survive to the bound without winning. Terran Power and
Zerg Power also demonstrate meaningful variation between identical-start repeats.
Better survival or cumulative trades do not pass the playing-strength gate.

This first candidate predates the subsequent CPU optimization and micro routing
integration. A separate `retreat-v2` snapshot will evaluate those changes. Recorded
state tests exposed a real integration defect: a strategic safe waypoint for a
critical unit was overwritten by a direct-home micro order on the next observation.
The corrected implementation shares routing across both paths and preserves
ownership, scripted destinations and one-order arbitration. Benchmarks are CPU
diagnostics under concurrent load, not alternative gameplay simulations.

Timeout inspection also found a separate stabilization loop: in Zerg Air,
142 army supply holds at a safe base for at least 90 sampled seconds because of
1–2 threatening supply elsewhere. A projected bounded-response candidate is being
evaluated separately; the full army must not be detained by a small raid when an
eligible, capable response can handle it. Heavy threats and inadequate responses
must retain defensive behavior. These are sampled observations, not a completed
replay UI review.

Other isolated candidates address depleted mineral/gas income, a completed first
defender before the natural, interrupted scouting, and army-relative search travel.
The first defender diagnosis is concrete: the old Gateway is ready around 85
seconds but waits while the bot saves for a Nexus; the first Zealot completes
around 145, after contact near 125. Opening-only and bounded-response staging
passed the entire original synthetic suite plus their new scenarios before live
evaluation. The user then explicitly stopped the broad queue: poor changes should
be rejected in short targeted trials instead of consuming thirty games. Income's
unfinished matrix is labeled an intentional abort. Targeted frozen batches now
gate further work; broader regression checks follow only demonstrated improvement.
No repaired playing-strength claim is made while these evaluations are pending.

## Session stopped and checkpointed

The user requested session closeout and a push. All live clients and launch queues
were stopped. See the [session closeout](session-closeout-2026-10-27.md) for results,
lessons, rejected integrations and unfinished production-reservation work. Later
candidate source/tests are preserved as [patches](experiments/2026-10-27/README.md).
This checkpoint is work in progress; it is not a promoted competitive policy.

## Production recovery resumed — 2026-10-31

The user authorized the review's next steps. The main checkout now has corrected
synthetic structure supply and Robotics prices, independently asserted SDK costs
and resource charging, and Windows wrappers that invoke the existing CLI through
`python -m source.run_assistant`. The generated executable launcher was blocked
by Windows application control (4551); no machine-wide security settings changed.
See the [runtime recheck](evaluations/2026-10-31-runtime.md).

The v5 archive's failing gas-release test was reproduced. Its fixture assigned
the Robotics Facility two supply, causing BurnySC2's morph-cost calculation to
subtract the producer price and report zero gas for an Immortal. Corrected
fixtures resolve that failure. Additional tests cover reservation revocation,
actual training costs and the reinforcement controller spending the same budget.

Reconciliation and trials use separate clean `9fd64a1` worktrees, baseline
scouting, unchanged dependency pins, explicit disabled combat abilities, and
complete [candidate patches/manifests](experiments/2026-10-31/README.md).
Frozen pressure/VeryHard/BelShirVestigeLE/seed-20261025/step-8/1500-second triplets
retain the previous loop-zero fingerprints. Software validation and targeted
gameplay results remain separate. The main working tree adopts R2 gameplay after
its targeted/retention gates; R1 remains rejected.

`production-v5-r1-20261031` passed 452 tests (92.74% coverage) but lost all three
Zerg Macro games. It was rejected without broader testing. R2 changes only the
priority construction path to try all safe powered Pylons; its regression case
uses the captured crowded opening. R2 passed 453 tests (92.78% coverage), locked
lint/format/type/build checks and its probe. Its targeted Macro triplet won 3/3
at 1055.4 sampled game seconds, with matching starts, frozen source and nonempty
replays. Rush, Power and both Air triplets also won 3/3, making the first five
groups 15/15 wins. The remaining five scenarios completed under the same frozen
gameplay. The [full development matrix](evaluations/2026-10-31-production-v5-r2-complete.md)
finished **21 wins / 9 defeats / 0 timeouts**, versus the reference's 9/18/3.
All 30 starts and nonempty replays passed verification; eight clients was the
global ceiling. Remaining defeats are Terran Rush, Terran Timing and Zerg Timing.

The user then requested longer games be resolved to judge effectiveness.
Subsequent trials default to **3600 game seconds**, superseding the earlier
1500-second acceptance budget. The completed shorter-bound results stay intact.
Matched reference/R2 Zerg Timing triplets completed at 3600 seconds in a separate
comparison group: reference `9fd64a1` won all three at 1515.4s; R2 lost all three
at 1205.4s. All six loop-zero states match at the new limit. Relative to the old
fingerprints only the recorded time-limit field differs. The old reference
timeouts remain censored in their original group. The extension exposes a real
Timing regression despite R2's broader shorter-bound improvements.

Two simultaneously started retention runners selected the same timestamp and
collided on report/log/replay paths. All six attempts are invalid: two failed
before API startup and four owned clients were intentionally stopped. Their
mixed artifacts and explicit abort labels remain local; none count as match
results. Valid replacement runs used the same frozen source with staggered starts.
The main checkout's runner now includes a UUID in its artifact prefix, with a
synthetic test forcing two runners onto the same clock value. Gameplay and
game/Python seeds are unchanged by that reporting fix.

After adopting R2 gameplay, the main checkout passed locked sync, Ruff lint and
format checks, configured mypy, **454 tests with 92.78% coverage**, and source/wheel
builds. At that checkpoint its source differences from frozen R2 were UUID
artifact naming and the subsequent 3600-second default. Later ontology, belief,
scouting and director work is an experimental revision pending live acceptance.
Shared human control remains unverified.

The [strategy baseline](evaluations/2026-10-31-strategy-belief-baseline.md)
calculates recognition and planned/delivered response metrics for all thirty R2
games and the separate six-game long comparison. The [belief/scouting design](opponent-beliefs-and-scouting.md)
records new instrumentation and its limits. The [first RL architecture](rl-architecture.md)
specifies a recurrent belief-state policy, four categorical action heads with
34 logits, a deterministic guarded decoder, transition logging, training and
evaluation phases. No RL learner or trained weights are implemented.

## Subsequent targeted repairs

The later [hardcoded milestone record](hardcoded-elite-milestone.md) tracks early
Robotics, counter-tech, wave readiness and siege-approach experiments separately
from accepted R2 gameplay. Counter-tech won Terran Rush 3/3 but lost Terran Timing
and Zerg Macro; wave readiness and siege approach also failed their Timing gates.
Their commits, source manifests and outcome reports remain on experiment branches.
The separate [RL training plan](rl-training-plan.md) covers teacher collection,
public opponents and conditional headless Linux deployment. Learner work remains
after the hardcoded playing-strength gate.

## Research basis and limits

Blizzard's [protocol defines the five AI build labels](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto).
They are configuration categories, not a detailed strategic ontology.
[Inferring Strategies from Limited Reconnaissance](https://arxiv.org/abs/1210.4880)
models strategy from partial scouting evidence; the useful design principle here
is an explicit belief over possibilities rather than treating missing vision as
absence. [High-Level Strategy Selection under Partial Observability](https://arxiv.org/abs/1811.08568)
distinguishes training-time full-state information from playable partial
observations. These papers study StarCraft: Brood War; they motivate the evidence
boundary, not validated thresholds for this SC2 bot. The initial component is a
transparent heuristic baseline, not a trained or calibrated predictor.

New independent seeds and maps will be needed to validate generalization after
this fixed-condition development suite. Future learned/LLM providers should use
the same evidence contract and evaluation metrics.
