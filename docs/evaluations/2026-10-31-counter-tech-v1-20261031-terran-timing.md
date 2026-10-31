# Match evaluation: counter-tech-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Timing | 3 Defeat | 3925 / 10575 | 0.37 | 1050 | 13 | 15 | 0 | 2 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Timing | 0 | 145.4s / 175.4s | 255-270s | 45.0 | 375.0 |

## Costly trade windows and match details

### Terran / Timing

Evidence: `runtime-20261031-101023-621130-2078cb3a0005485aa4198d452f90247b-001.json`. End sample 845.4s; peak 55 workers / 51 army supply. First offensive advance: 340.4s; first expansion advance: 545.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 2, 'short_target_reversals': 0, 'advance_regroup_transitions': 2, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 309, 'sampled_long_move_reversals': 11}`. Action rejections: `{}`.

Score-based bad-trade windows: 13; windows also showing own controlled-army disappearances: 13. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 6650.

Opponent prediction at last sample: **Unknown**, confidence 0.42. First correct confident classification: 235.4s; first home contact: 250.4s. Positive classification lead means recognition preceded contact: 15.0s.

- 660–675s: army lost 1125, army killed 100, economy killed 0; objectives `{'stabilize': 2, 'recover': 1}`, targets `['home', 'threat']`.
  Own army disappearances: `{'STALKER': 3, 'IMMORTAL': 1, 'ZEALOT': 1, 'SENTRY': 1}`; minimum estimated local advantage: 0.8236406089662507; minimum army health fraction: 0.8320680628272251; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 12, 'MARINE': 16, 'SIEGETANKSIEGED': 4}`.
- 600–615s: army lost 1050, army killed 175, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'SENTRY': 1, 'ZEALOT': 2, 'STALKER': 4}`; minimum estimated local advantage: 0.4790536528452001; minimum army health fraction: 0.7730769230769231; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 11, 'MARINE': 14, 'SIEGETANKSIEGED': 4}`.
- 795–810s: army lost 700, army killed 50, economy killed 50; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.3020138944957416; minimum army health fraction: 0.39019230769230767; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 9, 'SIEGETANKSIEGED': 3, 'MARINE': 21, 'VIKINGASSAULT': 3, 'VIKINGFIGHTER': 1, 'SIEGETANK': 1, 'GHOST': 2}`.
- Economic losses at 810–825s: 1400 resources; own worker/base disappearances `{'PROBE': 17, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 630–645s: 850 resources; own worker/base disappearances `{'PROBE': 15}`; objectives `{'stabilize': 2, 'recover': 1}`.
- Economic losses at 690–705s: 850 resources; own worker/base disappearances `{'PROBE': 8, 'NEXUS': 1}`; objectives `{'recover': 2, 'develop': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |
| 360 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.524 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.524 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.584373412840788. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
