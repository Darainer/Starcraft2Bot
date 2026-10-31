# Match evaluation: zerg-scout-selector-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Victory | 15125 / 6350 | 2.38 | 10525 | 4 | 46 | 2 | 5 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 110.4s / 170.4s | 315-330s | 5.0 | 950.0 |

## Costly trade windows and match details

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
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.40460967519168967. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
