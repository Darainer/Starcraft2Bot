# Match evaluation: portfolio-final-d0f8cf3-known-failures

Model: `scouting-v1`. 6 matches; 2 distinct starting-condition groups.

Results: `{'Result.Victory': 6}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-2026103102-step8-limit3600-snapshot1-revisit1-portfolioauto`. Configuration identities: `f8a34a9d80abcf1508b0fc91fd2a7ebfaf6282623c99ef166d7926bac5106036`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Power | 3 Victory | 33725 / 20325 | 1.66 | 15075 | 11 | 457 | 1 | 149 |
| Zerg / Macro | 3 Victory | 10425 / 4300 | 2.42 | 5550 | 0 | 182 | 0 | 65 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Power | 0 | 108.2s / 167.1s | 315-330s | 6.4 | 2742.9 |
| Zerg / Macro | 0 | 108.2s / 167.1s | not recorded | 6.4 | 585.0 |

## Costly trade windows and match details

### Zerg / Power

Evidence: `runtime-20261031-164446-850599-f72bf454e4c6417d8c9195073b5912c0-001.json`. End sample 1954.3s; peak 56 workers / 144 army supply. First offensive advance: 244.3s; first expansion advance: 297.9s; inspected sites: 8.

Movement: `{'offensive_target_switches': 37, 'short_target_reversals': 1, 'advance_regroup_transitions': 149, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 23888, 'sampled_long_move_reversals': 1299}`. Action rejections: `{}`.

Score-based bad-trade windows: 11; windows also showing own controlled-army disappearances: 11. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 100.

Opponent prediction at last sample: **Unknown**, confidence 0.35. First correct confident classification: 305.4s; first home contact: 316.1s. Positive classification lead means recognition preceded contact: 10.7s.

- 735–750s: army lost 2350, army killed 475, economy killed 450; objectives `{'pressure': 4, 'recover': 10}`, targets `['4399038474', 'home']`.
  Own army disappearances: `{'ZEALOT': 8, 'IMMORTAL': 1, 'STALKER': 6, 'SENTRY': 1}`; minimum estimated local advantage: 0.5293913672596448; minimum army health fraction: 0.8095580808080808; last sampled army center: `[33.63623046875, 94.97265625]`; observed enemy composition: `{'QUEEN': 2, 'HYDRALISK': 8, 'ZERGLING': 23, 'RAVAGER': 2, 'ROACH': 11, 'LURKERMPBURROWED': 1, 'BROODLING': 9}`.
- 900–915s: army lost 875, army killed 200, economy killed 0; objectives `{'pressure': 4, 'recover': 6, 'counterattack': 1}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'IMMORTAL': 2, 'STALKER': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8525194103134675; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 12, 'RAVAGER': 2, 'ROACH': 10, 'LURKERMPBURROWED': 2, 'ZERGLING': 19, 'CHANGELINGZEALOT': 3, 'ULTRALISK': 3, 'QUEEN': 2, 'BROODLING': 5}`.
- 315–330s: army lost 650, army killed 75, economy killed 0; objectives `{'pressure': 1, 'stabilize': 1, 'recover': 9}`, targets `['4341628929', 'home', 'threat']`.
  Own army disappearances: `{'SENTRY': 1, 'ZEALOT': 5}`; minimum estimated local advantage: 0.5632516203804535; minimum army health fraction: 0.6704470198675496; last sampled army center: `[55.78662109375, 126.892578125]`; observed enemy composition: `{'ROACH': 7, 'ZERGLING': 10}`.

### Zerg / Macro

Evidence: `runtime-20261031-164446-850599-f72bf454e4c6417d8c9195073b5912c0-004.json`. End sample 911.8s; peak 56 workers / 141 army supply. First offensive advance: 244.3s; first expansion advance: 351.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 10, 'short_target_reversals': 0, 'advance_regroup_transitions': 65, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 8934, 'sampled_long_move_reversals': 492}`. Action rejections: `{}`.

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
| final | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.761 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 1 |
| Macro | 0 | 0 | 0 | 0 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.1534934559000516. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
