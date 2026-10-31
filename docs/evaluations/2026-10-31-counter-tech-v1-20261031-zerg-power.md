# Match evaluation: counter-tech-v1-20261031

This additional targeted condition won **3/3 at 820.4 sampled game seconds**.
Gameplay source remains `a7cefe1`; it is the unchanged counter-tech candidate
that won Terran Rush and lost Terran Timing and Zerg Macro. Power's win does not
erase those regressions or establish a global replacement.

All three loop-zero states match the 3600-second reference, frozen hashes remain
unchanged, exact map/ping identities match and all replays are nonempty. See the
[source manifest](../experiments/2026-10-31/counter-tech-v1-manifest.json).
Pressure/VeryHard/Zerg Power/BelShirVestigeLE/seed 20261025/step eight are fixed.
This is the parent for the separately recorded reachable-expansion comparison.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Power | 3 Victory | 10100 / 4800 | 2.10 | 5600 | 5 | 22 | 0 | 3 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Power | 0 | 110.4s / 165.4s | 345-360s | 5.0 | 515.0 |

## Costly trade windows and match details

### Zerg / Power

Evidence: `runtime-20261031-104128-616605-0b32327098ff44989f07b0988cab86ae-001.json`. End sample 820.4s; peak 55 workers / 121 army supply. First offensive advance: 255.4s; first expansion advance: 405.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 9, 'short_target_reversals': 0, 'advance_regroup_transitions': 3, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 925, 'sampled_long_move_reversals': 55}`. Action rejections: `{}`.

Score-based bad-trade windows: 5; windows also showing own controlled-army disappearances: 5. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 200.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: 330.4s; first home contact: 220.4s. Positive classification lead means recognition preceded contact: -110.0s.

- 420–435s: army lost 600, army killed 0, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 6}`; minimum estimated local advantage: 0.6686773512043455; minimum army health fraction: 0.9327868852459016; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 8, 'ROACH': 8, 'RAVAGER': 2, 'HYDRALISK': 5}`.
- 570–585s: army lost 575, army killed 150, economy killed 0; objectives `{'stabilize': 1, 'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 1, 'ZEALOT': 4}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.9015782828282828; last sampled army center: `None`; observed enemy composition: `{'ROACH': 10, 'ZERGLING': 7, 'RAVAGER': 2, 'HYDRALISK': 8, 'BROODLING': 3, 'IMMORTAL': 1, 'CHANGELINGZEALOT': 1}`.
- 495–510s: army lost 800, army killed 400, economy killed 475; objectives `{'pressure': 2, 'recover': 1}`, targets `['4383571970', 'home']`.
  Own army disappearances: `{'ZEALOT': 8}`; minimum estimated local advantage: 0.8639829242038654; minimum army health fraction: 0.8623728813559322; last sampled army center: `[29.987060546875, 95.2841796875]`; observed enemy composition: `{'ZERGLING': 11, 'ROACH': 8, 'RAVAGER': 2, 'HYDRALISK': 8, 'BROODLING': 3}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 360 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |
| 600 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 1 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.2. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
