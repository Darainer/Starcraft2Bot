# Match evaluation: scouting-evidence-v3-revisit-targets

Model: `scouting-v1`. 6 matches; 2 distinct starting-condition groups.

Results: `{'Result.Victory': 6}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600-snapshot1-revisit1`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Victory | 14275 / 10525 | 1.36 | 8825 | 6 | 225 | 2 | 41 |
| Zerg / Timing | 3 Victory | 12675 / 6425 | 1.97 | 4800 | 3 | 245 | 0 | 18 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 108.2s / 167.1s | 315-330s | 6.4 | 774.6 |
| Zerg / Timing | 0 | 108.2s / 162.9s | 480-495s | 6.4 | 692.1 |

## Costly trade windows and match details

### Zerg / Macro

Evidence: `runtime-20261031-155344-118531-3f88fd63960e406cbaaec9658f04d2c4-001.json`. End sample 1050.0s; peak 55 workers / 139 army supply. First offensive advance: 245.4s; first expansion advance: 294.6s; inspected sites: 8.

Movement: `{'offensive_target_switches': 23, 'short_target_reversals': 2, 'advance_regroup_transitions': 41, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 8661, 'sampled_long_move_reversals': 430}`. Action rejections: `{}`.

Score-based bad-trade windows: 6; windows also showing own controlled-army disappearances: 6. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 300.

Opponent prediction at last sample: **Macro**, confidence 0.68. First correct confident classification: 418.9s; first home contact: 313.9s. Positive classification lead means recognition preceded contact: -105.0s.

- 600–615s: army lost 1325, army killed 725, economy killed 0; objectives `{'stabilize': 13, 'recover': 1}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 5, 'STALKER': 1, 'SENTRY': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.9468617341694391; minimum army health fraction: 0.6806451612903226; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 7, 'RAVAGER': 2, 'ZERGLING': 19, 'ROACH': 11}`.
- 570–585s: army lost 450, army killed 75, economy killed 0; objectives `{'stabilize': 6, 'recover': 8}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.9064673689711908; minimum army health fraction: 0.7502367424242424; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 7, 'RAVAGER': 2, 'ZERGLING': 17, 'ROACH': 12}`.
- 450–465s: army lost 400, army killed 75, economy killed 0; objectives `{'pressure': 1, 'recover': 13}`, targets `['4341891073', 'home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.2439575328728412; minimum army health fraction: 0.8087912087912088; last sampled army center: `[65.20849609375, 122.466796875]`; observed enemy composition: `{'ZERGLING': 9, 'HYDRALISK': 5, 'ROACH': 9, 'RAVAGER': 2, 'CHANGELINGZEALOT': 1}`.

### Zerg / Timing

Evidence: `runtime-20261031-155344-118531-3f88fd63960e406cbaaec9658f04d2c4-004.json`. End sample 1002.9s; peak 33 workers / 109 army supply. First offensive advance: 339.6s; first expansion advance: 339.6s; inspected sites: 8.

Movement: `{'offensive_target_switches': 11, 'short_target_reversals': 0, 'advance_regroup_transitions': 18, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 6657, 'sampled_long_move_reversals': 311}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 400.

Opponent prediction at last sample: **Unknown**, confidence 0.50. First correct confident classification: 250.7s; first home contact: 190.7s. Positive classification lead means recognition preceded contact: -60.0s.

- 480–495s: army lost 500, army killed 275, economy killed 0; objectives `{'contain': 4, 'pressure': 5, 'recover': 3}`, targets `['4346871810', '4370989065', 'home']`.
  Own army disappearances: `{'ZEALOT': 3, 'SENTRY': 3}`; minimum estimated local advantage: 0.8085360565085866; minimum army health fraction: 0.8771626297577855; last sampled army center: `[56.43798828125, 112.272216796875]`; observed enemy composition: `{'ZERGLING': 8, 'ROACH': 6, 'HYDRALISK': 6, 'RAVAGER': 2, 'CHANGELINGZEALOT': 1}`.
- 570–585s: army lost 375, army killed 225, economy killed 50; objectives `{'pressure': 13, 'recover': 1}`, targets `['4346871810', 'home']`.
  Own army disappearances: `{'STALKER': 1, 'ZEALOT': 6}`; minimum estimated local advantage: 1.066807081694716; minimum army health fraction: 0.8703896103896104; last sampled army center: `[59.355224609375, 114.77197265625]`; observed enemy composition: `{'ROACH': 11, 'HYDRALISK': 6, 'ZERGLING': 14, 'RAVAGER': 2, 'CHANGELINGZEALOT': 2, 'BROODLING': 6, 'QUEEN': 1}`.
- 600–615s: army lost 350, army killed 225, economy killed 0; objectives `{'pressure': 6, 'recover': 8}`, targets `['4346871810', 'home']`.
  Own army disappearances: `{'STALKER': 2}`; minimum estimated local advantage: 0.5954834895691443; minimum army health fraction: 0.8072916666666666; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 6, 'ROACH': 9, 'ZERGLING': 10, 'RAVAGER': 2, 'BROODLING': 6, 'QUEEN': 1, 'CHANGELINGZEALOT': 2}`.
- Economic losses at 270–285s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 11}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 180 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 240 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.745 |
| 360 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.544 |
| 600 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.439 |
| final | 2 | 50.0% | 50.0% | 50.0% | 100.0% | 0.231 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 1 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.4105227260988912. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
