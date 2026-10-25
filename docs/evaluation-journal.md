# Evaluation journal and opponent assessment

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
