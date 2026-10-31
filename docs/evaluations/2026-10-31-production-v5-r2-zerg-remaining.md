# Match evaluation: production-v5-r2-20261031-zerg-remaining

Model: `scouting-v1`. 6 matches; 2 distinct starting-condition groups.

Results: `{'Result.Defeat': 3, 'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit1500`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Timing | 3 Defeat | 9500 / 13850 | 0.69 | 1200 | 15 | 31 | 0 | 5 |
| Zerg / Power | 3 Victory | 17250 / 7425 | 2.32 | 9000 | 4 | 50 | 3 | 9 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Timing | 0 | 110.4s / 165.4s | 270-285s | 35.0 | 495.0 |
| Zerg / Power | 0 | 110.4s / 165.4s | 330-345s | 25.0 | 890.0 |

## Costly trade windows and match details

### Zerg / Timing

Evidence: `runtime-20261031-085423-792713-001.json`. End sample 1220.4s; peak 56 workers / 85 army supply. First offensive advance: 340.4s; first expansion advance: 455.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 17, 'short_target_reversals': 0, 'advance_regroup_transitions': 5, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1088, 'sampled_long_move_reversals': 105}`. Action rejections: `{'direct:881:41': 1, 'direct:3674:3': 2}`.

Score-based bad-trade windows: 15; windows also showing own controlled-army disappearances: 15. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 7275.

Opponent prediction at last sample: **Unknown**, confidence 0.52. First correct confident classification: 260.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: -65.0s.

- 1110–1125s: army lost 1325, army killed 250, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 5, 'ZEALOT': 2}`; minimum estimated local advantage: 0.008491613016115972; minimum army health fraction: 0.325; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 12, 'ROACH': 9, 'BROODLORD': 10, 'QUEEN': 4, 'HYDRALISK': 6, 'RAVAGER': 2, 'CORRUPTOR': 2, 'BROODLING': 30, 'IMMORTAL': 1}`.
- 555–570s: army lost 975, army killed 100, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 5, 'ZEALOT': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8227661596958175; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 7, 'RAVAGER': 2, 'HYDRALISK': 6, 'ROACH': 8, 'QUEEN': 2}`.
- 270–285s: army lost 550, army killed 0, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 4, 'SENTRY': 1}`; minimum estimated local advantage: 0.6823800667084142; minimum army health fraction: 0.49623983739837396; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 2, 'ROACH': 8}`.
- Economic losses at 1185–1200s: 975 resources; own worker/base disappearances `{'PROBE': 6, 'ASSIMILATOR': 1}`; objectives `{'develop': 3}`.
- Economic losses at 750–765s: 750 resources; own worker/base disappearances `{'NEXUS': 1, 'PROBE': 7}`; objectives `{'recover': 3}`.
- Economic losses at 705–720s: 700 resources; own worker/base disappearances `{'PROBE': 4, 'NEXUS': 1}`; objectives `{'recover': 1, 'stabilize': 2}`.

### Zerg / Power

Evidence: `runtime-20261031-085423-792713-004.json`. End sample 1070.4s; peak 56 workers / 133 army supply. First offensive advance: 255.4s; first expansion advance: 315.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 23, 'short_target_reversals': 3, 'advance_regroup_transitions': 9, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1864, 'sampled_long_move_reversals': 191}`. Action rejections: `{}`.

Score-based bad-trade windows: 4; windows also showing own controlled-army disappearances: 4. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 1575.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: 315.4s; first home contact: 220.4s. Positive classification lead means recognition preceded contact: -95.0s.

- 330–345s: army lost 650, army killed 75, economy killed 50; objectives `{'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 5, 'SENTRY': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.7782142857142857; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 8, 'QUEEN': 1, 'ROACH': 9}`.
- 510–525s: army lost 400, army killed 0, economy killed 325; objectives `{'recover': 2, 'pressure': 1}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 1.2131088549316245; minimum army health fraction: 0.9885245901639345; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 2, 'ROACH': 8, 'HYDRALISK': 8, 'ZERGLING': 2, 'CHANGELINGZEALOT': 1}`.
- 495–510s: army lost 400, army killed 75, economy killed 175; objectives `{'pressure': 3}`, targets `['4373086209']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.914363777091332; minimum army health fraction: 0.9040296052631579; last sampled army center: `[31.2554931640625, 93.7423095703125]`; observed enemy composition: `{'RAVAGER': 2, 'ROACH': 8, 'HYDRALISK': 8, 'ZERGLING': 2, 'CHANGELINGZEALOT': 1}`.
- Economic losses at 615–630s: 1075 resources; own worker/base disappearances `{'PROBE': 10, 'NEXUS': 1, 'ASSIMILATOR': 1}`; objectives `{'pressure': 2, 'stabilize': 1}`.
- Economic losses at 600–615s: 450 resources; own worker/base disappearances `{'PROBE': 5}`; objectives `{'stabilize': 2}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 180 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 240 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 360 | 2 | 50.0% | 50.0% | 50.0% | 100.0% | 0.354 |
| 600 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.652 |
| final | 2 | 0.0% | 0.0% | 50.0% | 0.0% | 1.213 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 1 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.6367068522114823. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `9fd64a1`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Zerg / Timing | Result.Tie → Result.Defeat | 2 → 0 | 15 → 5 | 1 → 15 |
| Zerg / Power | Result.Defeat → Result.Victory | 0 → 3 | 0 → 9 | 9 → 4 |
