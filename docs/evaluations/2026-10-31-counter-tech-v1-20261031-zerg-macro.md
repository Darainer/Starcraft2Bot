# Match evaluation: counter-tech-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Defeat | 4475 / 10525 | 0.42 | 175 | 10 | 16 | 0 | 5 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 110.4s / 170.4s | 390-405s | 5.0 | 560.0 |

## Costly trade windows and match details

### Zerg / Macro

Evidence: `runtime-20261031-101352-048375-fe09a121cb1b4e0da523bf7e08a4dac6-001.json`. End sample 855.4s; peak 56 workers / 73 army supply. First offensive advance: 255.4s; first expansion advance: 310.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 7, 'short_target_reversals': 0, 'advance_regroup_transitions': 5, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 493, 'sampled_long_move_reversals': 49}`. Action rejections: `{}`.

Score-based bad-trade windows: 10; windows also showing own controlled-army disappearances: 10. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 5775.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 315.4s. Positive classification lead means recognition preceded contact: not observed.

- 630–645s: army lost 2375, army killed 575, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'IMMORTAL': 1, 'STALKER': 9, 'ZEALOT': 3, 'SENTRY': 1}`; minimum estimated local advantage: 0.16317807768514045; minimum army health fraction: 0.7672131147540984; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 7, 'ROACH': 13, 'RAVAGER': 2, 'ZERGLING': 16, 'CHANGELINGZEALOT': 2, 'QUEEN': 1}`.
- 750–765s: army lost 1075, army killed 75, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'SENTRY': 2, 'STALKER': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.577570093457944; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 10, 'ROACH': 15, 'RAVAGER': 2, 'QUEEN': 2, 'ZERGLING': 14, 'LURKERMPBURROWED': 2, 'CHANGELINGZEALOT': 1}`.
- 555–570s: army lost 1000, army killed 175, economy killed 75; objectives `{'pressure': 1, 'recover': 2}`, targets `['4338483203', 'home']`.
  Own army disappearances: `{'ZEALOT': 10}`; minimum estimated local advantage: 0.3192885727442469; minimum army health fraction: 0.8630849753694582; last sampled army center: `[32.3157958984375, 92.907958984375]`; observed enemy composition: `{'ROACH': 16, 'ZERGLING': 13, 'HYDRALISK': 8, 'RAVAGER': 2, 'CHANGELINGZEALOT': 1}`.
- Economic losses at 750–765s: 950 resources; own worker/base disappearances `{'PROBE': 17}`; objectives `{'recover': 3}`.
- Economic losses at 645–660s: 925 resources; own worker/base disappearances `{'NEXUS': 1, 'PROBE': 9, 'ASSIMILATOR': 1}`; objectives `{'recover': 1, 'stabilize': 1, 'counterattack': 1}`.
- Economic losses at 690–705s: 800 resources; own worker/base disappearances `{'PROBE': 16}`; objectives `{'recover': 3}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 360 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 600 | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 1.276 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.2. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
