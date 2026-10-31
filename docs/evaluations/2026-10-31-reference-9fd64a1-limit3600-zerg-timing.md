# Match evaluation: reference-9fd64a1-limit3600-zerg-timing

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Timing | 3 Victory | 17000 / 5650 | 3.01 | 8475 | 1 | 63 | 2 | 15 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Timing | 0 | 145.4s / 200.4s | 315-330s | 30.0 | 1015.0 |

## Costly trade windows and match details

### Zerg / Timing

Evidence: `runtime-20261031-090559-691828-cd52296f3f70485ea8358a1cec9e02fa-001.json`. End sample 1515.4s; peak 34 workers / 145 army supply. First offensive advance: 400.4s; first expansion advance: 400.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 41, 'short_target_reversals': 2, 'advance_regroup_transitions': 15, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 5943, 'sampled_long_move_reversals': 661}`. Action rejections: `{'direct:1414:41': 1}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 1000.

Opponent prediction at last sample: **Unknown**, confidence 0.45. First correct confident classification: not observed; first home contact: 195.4s. Positive classification lead means recognition preceded contact: not observed.

- 315–330s: army lost 700, army killed 200, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.299064063200345; minimum army health fraction: 0.46304347826086956; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 6, 'ROACH': 11}`.
- Economic losses at 270–285s: 450 resources; own worker/base disappearances `{'PROBE': 1, 'NEXUS': 1}`; objectives `{'stabilize': 2}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 360 | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 0.992 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.328 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.391 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.5533667761938748. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
