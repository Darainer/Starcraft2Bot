# Match evaluation: zerg-scout-selector-v1-20261031

Model: `scouting-v1`. 15 matches; 5 distinct starting-condition groups.

Results: `{'Result.Victory': 15}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Rush | 3 Victory | 5525 / 1375 | 4.02 | 3675 | 1 | 24 | 1 | 6 |
| Zerg / Timing | 3 Victory | 8975 / 5250 | 1.71 | 6750 | 3 | 45 | 2 | 15 |
| Zerg / Power | 3 Victory | 17250 / 7425 | 2.32 | 9000 | 4 | 50 | 3 | 9 |
| Zerg / Macro | 3 Victory | 15125 / 6350 | 2.38 | 10525 | 4 | 46 | 2 | 5 |
| Zerg / Air | 3 Victory | 2200 / 500 | 4.40 | 2000 | 0 | 6 | 0 | 1 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Rush | 0 | 110.4s / 170.4s | 450-465s | 5.0 | 390.0 |
| Zerg / Timing | 0 | 110.4s / 165.4s | 435-450s | 5.0 | 800.0 |
| Zerg / Power | 0 | 110.4s / 165.4s | 330-345s | 25.0 | 890.0 |
| Zerg / Macro | 0 | 110.4s / 170.4s | 315-330s | 5.0 | 950.0 |
| Zerg / Air | 0 | 110.4s / 160.4s | not recorded | 5.0 | 90.0 |

## Costly trade windows and match details

### Zerg / Rush

Evidence: `runtime-20261031-145546-768785-3472a079070e4fe1a2b5bc2089c9d7b8-001.json`. End sample 685.4s; peak 55 workers / 113 army supply. First offensive advance: 245.4s; first expansion advance: 300.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 9, 'short_target_reversals': 1, 'advance_regroup_transitions': 6, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 755, 'sampled_long_move_reversals': 41}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 125.4s. Positive classification lead means recognition preceded contact: not observed.

- 450–465s: army lost 300, army killed 125, economy killed 0; objectives `{'pressure': 2}`, targets `['4345823234']`.
  Own army disappearances: `{'ZEALOT': 3}`; minimum estimated local advantage: 3.0177343559052248; minimum army health fraction: 0.8630890052356021; last sampled army center: `[75.2337646484375, 125.3350830078125]`; observed enemy composition: `{'ROACH': 4, 'HYDRALISK': 4, 'ZERGLING': 1}`.

### Zerg / Timing

Evidence: `runtime-20261031-145020-935789-c62acd2a79e34d0d816718d10524b2ce-001.json`. End sample 1050.4s; peak 34 workers / 111 army supply. First offensive advance: 335.4s; first expansion advance: 335.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 16, 'short_target_reversals': 2, 'advance_regroup_transitions': 15, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1822, 'sampled_long_move_reversals': 142}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 400.

Opponent prediction at last sample: **Unknown**, confidence 0.50. First correct confident classification: 620.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: -425.0s.

- 495–510s: army lost 450, army killed 100, economy killed 0; objectives `{'recover': 2, 'pressure': 1}`, targets `['4356833284', 'home']`.
  Own army disappearances: `{'ZEALOT': 3, 'SENTRY': 1}`; minimum estimated local advantage: 1.2494735289154402; minimum army health fraction: 0.9313351498637602; last sampled army center: `None`; observed enemy composition: `{'ROACH': 13, 'RAVAGER': 2, 'HYDRALISK': 6, 'ZERGLING': 14, 'CHANGELINGZEALOT': 1}`.
- 435–450s: army lost 400, army killed 75, economy killed 0; objectives `{'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.8746223902046449; minimum army health fraction: 0.9714285714285714; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 5, 'ROACH': 13, 'RAVAGER': 1, 'HYDRALISK': 5, 'CHANGELINGZEALOT': 1}`.
- 810–825s: army lost 300, army killed 150, economy killed 0; objectives `{'pressure': 3}`, targets `['4334813185']`.
  Own army disappearances: `{'ZEALOT': 3}`; minimum estimated local advantage: 4.615090555916168; minimum army health fraction: 0.8628694322374132; last sampled army center: `[40.909423828125, 134.8865966796875]`; observed enemy composition: `{'MUTALISK': 4, 'ZERGLING': 13, 'ROACH': 5, 'BROODLING': 17, 'HYDRALISK': 2, 'QUEEN': 1, 'CHANGELINGZEALOT': 1}`.
- Economic losses at 270–285s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 2}`.

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

### Zerg / Macro

Evidence: `runtime-20261031-145009-490463-a8825c4b4fe14ed7aa0d7d595cc15991-001.json`. End sample 1145.4s; peak 56 workers / 143 army supply. First offensive advance: 245.4s; first expansion advance: 300.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 26, 'short_target_reversals': 2, 'advance_regroup_transitions': 5, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2844, 'sampled_long_move_reversals': 226}`. Action rejections: `{}`.

Score-based bad-trade windows: 4; windows also showing own controlled-army disappearances: 4. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: not observed; first home contact: 315.4s. Positive classification lead means recognition preceded contact: not observed.

- 570–585s: army lost 700, army killed 75, economy killed 0; objectives `{'pressure': 1, 'recover': 2}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 7}`; minimum estimated local advantage: 0.9156426370627035; minimum army health fraction: 0.9577956989247312; last sampled army center: `[67.5635986328125, 107.16845703125]`; observed enemy composition: `{'ZERGLING': 24, 'ROACH': 16, 'HYDRALISK': 6, 'RAVAGER': 2}`.
- 630–645s: army lost 775, army killed 350, economy killed 250; objectives `{'pressure': 1, 'recover': 2}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 6, 'STALKER': 1}`; minimum estimated local advantage: 0.24279423501856354; minimum army health fraction: 0.8532789079229122; last sampled army center: `[54.792236328125, 110.9227294921875]`; observed enemy composition: `{'ZERGLING': 19, 'ROACH': 17, 'HYDRALISK': 8, 'RAVAGER': 2}`.
- 510–525s: army lost 400, army killed 100, economy killed 0; objectives `{'recover': 2, 'stabilize': 1}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.7733652472482669; minimum army health fraction: 0.8491228070175438; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 13, 'ROACH': 16, 'HYDRALISK': 4, 'RAVAGER': 2}`.

### Zerg / Air

Evidence: `runtime-20261031-145607-807756-5612765ca4454dfd97758ffd1547a7b8-001.json`. End sample 480.4s; peak 44 workers / 59 army supply. First offensive advance: 255.4s; first expansion advance: 300.4s; inspected sites: 3.

Movement: `{'offensive_target_switches': 3, 'short_target_reversals': 0, 'advance_regroup_transitions': 1, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 301, 'sampled_long_move_reversals': 9}`. Action rejections: `{}`.

Score-based bad-trade windows: 0; windows also showing own controlled-army disappearances: 0. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: not observed; first home contact: not observed. Positive classification lead means recognition preceded contact: not observed.

No sampled 15-second window met the bad-trade threshold (loss ≥300 and >1.5× enemy army value killed).

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 5 | 0.0% | 0.0% | 0.0% | n/a | 0.831 |
| 180 | 5 | 0.0% | 0.0% | 0.0% | n/a | 0.831 |
| 240 | 5 | 0.0% | 0.0% | 0.0% | n/a | 0.831 |
| 360 | 5 | 20.0% | 20.0% | 20.0% | 100.0% | 0.622 |
| 600 | 4 | 0.0% | 0.0% | 25.0% | 0.0% | 0.845 |
| final | 5 | 0.0% | 0.0% | 20.0% | 0.0% | 0.797 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 1 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 1 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 1 |

Expected calibration error: 0.4490404345162574. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
