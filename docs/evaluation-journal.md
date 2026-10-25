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

## Next implementation: movement stability and measurable opponent inference

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
