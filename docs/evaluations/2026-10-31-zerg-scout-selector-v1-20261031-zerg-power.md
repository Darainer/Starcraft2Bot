# Match evaluation: zerg-scout-selector-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Power | 3 Victory | 17250 / 7425 | 2.32 | 9000 | 4 | 50 | 3 | 9 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Power | 0 | 110.4s / 165.4s | 330-345s | 25.0 | 890.0 |

## Costly trade windows and match details

### Zerg / Power

Evidence: `runtime-20261031-145557-987810-0c07c01cf52d410bbff7edae2d18dc72-001.json`. End sample 1070.4s; peak 56 workers / 133 army supply. First offensive advance: 255.4s; first expansion advance: 315.4s; inspected sites: 8.

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
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 360 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.750 |
| final | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 1.458 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 1 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.7528193114291688. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
