# Match evaluation: production-v5-r2-20261031-limit3600-zerg-timing

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Timing | 3 Defeat | 9525 / 13850 | 0.69 | 1200 | 14 | 32 | 0 | 5 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Timing | 0 | 110.4s / 165.4s | 270-285s | 35.0 | 470.0 |

## Costly trade windows and match details

### Zerg / Timing

Evidence: `runtime-20261031-090611-945502-001.json`. End sample 1205.4s; peak 56 workers / 85 army supply. First offensive advance: 340.4s; first expansion advance: 455.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 16, 'short_target_reversals': 0, 'advance_regroup_transitions': 5, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1086, 'sampled_long_move_reversals': 105}`. Action rejections: `{'direct:881:41': 1, 'direct:3674:3': 3}`.

Score-based bad-trade windows: 14; windows also showing own controlled-army disappearances: 14. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 7325.

Opponent prediction at last sample: **Unknown**, confidence 0.52. First correct confident classification: 260.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: -65.0s.

- 1110–1125s: army lost 1550, army killed 375, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 1, 'STALKER': 4, 'COLOSSUS': 1}`; minimum estimated local advantage: 0.022001688611647235; minimum army health fraction: 0.23024193548387098; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 10, 'ROACH': 10, 'BROODLORD': 10, 'QUEEN': 2, 'HYDRALISK': 7, 'RAVAGER': 2, 'BROODLING': 31, 'CHANGELINGZEALOT': 2, 'CORRUPTOR': 2}`.
- 1020–1035s: army lost 1050, army killed 125, economy killed 50; objectives `{'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 4, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.406488023881395; minimum army health fraction: 0.7066379310344828; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 16, 'ROACH': 9, 'BROODLORD': 6, 'QUEEN': 3, 'HYDRALISK': 4, 'RAVAGER': 2, 'BROODLING': 11, 'CHANGELINGZEALOT': 1, 'IMMORTAL': 1}`.
- 555–570s: army lost 975, army killed 100, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 5, 'ZEALOT': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8227661596958175; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 7, 'RAVAGER': 2, 'HYDRALISK': 6, 'ROACH': 8, 'QUEEN': 2}`.
- Economic losses at 1170–1185s: 775 resources; own worker/base disappearances `{'PROBE': 6, 'ASSIMILATOR': 1}`; objectives `{'develop': 3}`.
- Economic losses at 750–765s: 750 resources; own worker/base disappearances `{'NEXUS': 1, 'PROBE': 7}`; objectives `{'recover': 3}`.
- Economic losses at 1155–1170s: 750 resources; own worker/base disappearances `{'PROBE': 9}`; objectives `{'develop': 2}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 360 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.554 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.554 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.967 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.5205943929937958. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `reference-9fd64a1-limit3600-zerg-timing`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Zerg / Timing | Result.Victory → Result.Defeat | 2 → 0 | 15 → 5 | 1 → 14 |
