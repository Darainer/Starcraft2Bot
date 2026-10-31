# Match evaluation: scouting-evidence-v3-revisit-newseed2-failures

Model: `scouting-v1`. 6 matches; 2 distinct starting-condition groups.

Results: `{'Result.Defeat': 3, 'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-2026103102-step8-limit3600-snapshot1-revisit1`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Power | 3 Defeat | 7250 / 12525 | 0.58 | 875 | 10 | 109 | 0 | 56 |
| Zerg / Macro | 3 Victory | 10475 / 4450 | 2.35 | 6175 | 0 | 208 | 0 | 52 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Power | 0 | 108.2s / 167.1s | 315-330s | 21.4 | 871.1 |
| Zerg / Macro | 0 | 108.2s / 167.1s | not recorded | 6.4 | 570.0 |

## Costly trade windows and match details

### Zerg / Power

Evidence: `runtime-20261031-160635-413503-e5c7ebeeb6754096b5dd1e859b335c77-001.json`. End sample 997.5s; peak 56 workers / 75 army supply. First offensive advance: 244.3s; first expansion advance: 297.9s; inspected sites: 8.

Movement: `{'offensive_target_switches': 8, 'short_target_reversals': 0, 'advance_regroup_transitions': 56, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 3660, 'sampled_long_move_reversals': 226}`. Action rejections: `{}`.

Score-based bad-trade windows: 10; windows also showing own controlled-army disappearances: 10. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 6900.

Opponent prediction at last sample: **Power**, confidence 0.59. First correct confident classification: 305.4s; first home contact: 316.1s. Positive classification lead means recognition preceded contact: 10.7s.

- 930–945s: army lost 1550, army killed 50, economy killed 0; objectives `{'recover': 11}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 1, 'STALKER': 2, 'IMMORTAL': 2, 'SENTRY': 1}`; minimum estimated local advantage: 0.0937264545991672; minimum army health fraction: 0.6062158469945356; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 14, 'HYDRALISK': 8, 'ROACH': 17, 'RAVAGER': 4, 'CHANGELINGZEALOT': 3, 'LURKERMPBURROWED': 2, 'QUEEN': 1}`.
- 615–630s: army lost 1025, army killed 0, economy killed 0; objectives `{'recover': 13, 'stabilize': 1}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 3, 'ZEALOT': 2, 'SENTRY': 2}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8678292410714286; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 17, 'RAVAGER': 2, 'ROACH': 15, 'HYDRALISK': 11, 'LURKERMPBURROWED': 1, 'QUEEN': 1}`.
- 945–960s: army lost 700, army killed 0, economy killed 0; objectives `{'recover': 6}`, targets `['home']`.
  Own army disappearances: `{'IMMORTAL': 1, 'ZEALOT': 2, 'SENTRY': 1}`; minimum estimated local advantage: 0.13334388134244063; minimum army health fraction: 0.6645161290322581; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 16, 'HYDRALISK': 8, 'ROACH': 17, 'RAVAGER': 6, 'CHANGELINGZEALOT': 3, 'LURKERMPBURROWED': 2, 'QUEEN': 4}`.
- Economic losses at 705–720s: 1050 resources; own worker/base disappearances `{'PROBE': 7, 'NEXUS': 1}`; objectives `{'stabilize': 8, 'recover': 3, 'pressure': 1}`.
- Economic losses at 930–945s: 1050 resources; own worker/base disappearances `{'PROBE': 15}`; objectives `{'recover': 11}`.
- Economic losses at 630–645s: 850 resources; own worker/base disappearances `{'PROBE': 7, 'NEXUS': 1}`; objectives `{'recover': 3, 'stabilize': 11}`.

### Zerg / Macro

Evidence: `runtime-20261031-160635-413503-e5c7ebeeb6754096b5dd1e859b335c77-004.json`. End sample 920.4s; peak 56 workers / 143 army supply. First offensive advance: 244.3s; first expansion advance: 351.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 14, 'short_target_reversals': 0, 'advance_regroup_transitions': 52, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 9131, 'sampled_long_move_reversals': 538}`. Action rejections: `{}`.

Score-based bad-trade windows: 0; windows also showing own controlled-army disappearances: 0. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 100.

Opponent prediction at last sample: **Unknown**, confidence 0.35. First correct confident classification: not observed; first home contact: 312.9s. Positive classification lead means recognition preceded contact: not observed.

No sampled 15-second window met the bad-trade threshold (loss ≥300 and >1.5× enemy army value killed).

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.717 |
| 360 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.717 |
| 600 | 2 | 50.0% | 50.0% | 100.0% | 50.0% | 0.637 |
| final | 2 | 50.0% | 50.0% | 50.0% | 100.0% | 0.375 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 1 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.5315385415222711. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
