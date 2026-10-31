# Match evaluation: production-v5-r2-20261031-zerg-macro

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit1500`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Victory | 13350 / 8500 | 1.57 | 10475 | 4 | 63 | 2 | 15 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 110.4s / 170.4s | 315-330s | 5.0 | 660.0 |

## Costly trade windows and match details

### Zerg / Macro

Evidence: `runtime-20261031-084305-882772-001.json`. End sample 1055.4s; peak 56 workers / 143 army supply. First offensive advance: 245.4s; first expansion advance: 300.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 17, 'short_target_reversals': 2, 'advance_regroup_transitions': 15, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2175, 'sampled_long_move_reversals': 257}`. Action rejections: `{'direct:3674:2': 8}`.

Score-based bad-trade windows: 4; windows also showing own controlled-army disappearances: 4. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 100.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 315.4s. Positive classification lead means recognition preceded contact: not observed.

- 570–585s: army lost 1200, army killed 50, economy killed 50; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 9, 'SENTRY': 2}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8300495426829269; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 12, 'RAVAGER': 2, 'ROACH': 15, 'HYDRALISK': 8, 'CHANGELINGZEALOT': 2}`.
- 435–450s: army lost 650, army killed 225, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 3, 'STALKER': 2}`; minimum estimated local advantage: 0.7879849218507476; minimum army health fraction: 0.9013157894736842; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 9, 'ROACH': 8, 'HYDRALISK': 4}`.
- 315–330s: army lost 500, army killed 150, economy killed 300; objectives `{'pressure': 1, 'counterattack': 1, 'recover': 1}`, targets `['4341891073', 'home']`.
  Own army disappearances: `{'ZEALOT': 5}`; minimum estimated local advantage: 2.095348564014464; minimum army health fraction: 0.6959016393442623; last sampled army center: `[64.3994140625, 129.472900390625]`; observed enemy composition: `{'QUEEN': 1, 'ZERGLING': 7, 'ROACH': 6}`.

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

## Matched comparison

Baseline `9fd64a1`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Zerg / Macro | Result.Defeat → Result.Victory | 0 → 2 | 2 → 15 | 8 → 4 |
