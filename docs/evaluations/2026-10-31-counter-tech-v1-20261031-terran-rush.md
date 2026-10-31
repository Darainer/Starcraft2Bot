# Match evaluation: counter-tech-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Rush | 3 Victory | 6150 / 4900 | 1.25 | 4600 | 1 | 10 | 2 | 3 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Rush | 0 | 140.4s / 170.4s | 540-555s | 15.0 | 415.0 |

## Costly trade windows and match details

### Terran / Rush

Evidence: `runtime-20261031-100520-875363-e9a2e6a54c934bd78e448118274220e5-001.json`. End sample 805.4s; peak 32 workers / 91 army supply. First offensive advance: 315.4s; first expansion advance: 365.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 11, 'short_target_reversals': 2, 'advance_regroup_transitions': 3, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 720, 'sampled_long_move_reversals': 19}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 400.

Opponent prediction at last sample: **Rush**, confidence 0.75. First correct confident classification: 190.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: 5.0s.

- 540–555s: army lost 1200, army killed 650, economy killed 0; objectives `{'pressure': 2}`, targets `['4364173313']`.
  Own army disappearances: `{'IMMORTAL': 1, 'ZEALOT': 5, 'STALKER': 2}`; minimum estimated local advantage: 2.7456402023595454; minimum army health fraction: 0.8921153846153846; last sampled army center: `[67.5966796875, 128.083984375]`; observed enemy composition: `{'MARINE': 12, 'MARAUDER': 7}`.
- Economic losses at 210–225s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.076 |
| 360 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.076 |
| 600 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.076 |
| final | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.076 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 1 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.2471806885708312. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
