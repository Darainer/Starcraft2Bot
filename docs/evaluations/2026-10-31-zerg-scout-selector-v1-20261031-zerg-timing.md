# Match evaluation: zerg-scout-selector-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Timing | 3 Victory | 8975 / 5250 | 1.71 | 6750 | 3 | 45 | 2 | 15 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Timing | 0 | 110.4s / 165.4s | 435-450s | 5.0 | 800.0 |

## Costly trade windows and match details

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
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.328 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.5016022115354974. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `reference-9fd64a1-limit3600-zerg-timing`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Zerg / Timing | Result.Victory → Result.Victory | 2 → 2 | 15 → 15 | 1 → 3 |
