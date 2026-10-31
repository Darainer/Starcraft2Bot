# Match evaluation: scouting-evidence-reference-targets

Model: `scouting-v1`. 6 matches; 2 distinct starting-condition groups.

Results: `{'Result.Victory': 6}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600-snapshot1-revisit0`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Victory | 14925 / 4925 | 3.03 | 8750 | 4 | 197 | 1 | 52 |
| Zerg / Timing | 3 Victory | 8975 / 5250 | 1.71 | 6750 | 3 | 217 | 1 | 60 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 108.2s / 167.1s | 315-330s | 6.4 | 653.6 |
| Zerg / Timing | 0 | 108.2s / 162.9s | 435-450s | 6.4 | 802.5 |

## Costly trade windows and match details

### Zerg / Macro

Evidence: `runtime-20261031-152341-130739-bf72083b71384b4aa0e88720b46f0059-001.json`. End sample 982.5s; peak 56 workers / 143 army supply. First offensive advance: 244.3s; first expansion advance: 295.7s; inspected sites: 8.

Movement: `{'offensive_target_switches': 19, 'short_target_reversals': 1, 'advance_regroup_transitions': 52, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 9539, 'sampled_long_move_reversals': 492}`. Action rejections: `{}`.

Score-based bad-trade windows: 4; windows also showing own controlled-army disappearances: 4. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 313.9s. Positive classification lead means recognition preceded contact: not observed.

- 570–585s: army lost 700, army killed 75, economy killed 0; objectives `{'pressure': 2, 'recover': 12}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 7}`; minimum estimated local advantage: 0.43093180967226996; minimum army health fraction: 0.9134292565947242; last sampled army center: `[66.299072265625, 106.844482421875]`; observed enemy composition: `{'ZERGLING': 24, 'ROACH': 16, 'HYDRALISK': 6, 'RAVAGER': 2}`.
- 315–330s: army lost 600, army killed 100, economy killed 250; objectives `{'pressure': 1, 'counterattack': 7, 'recover': 5}`, targets `['4341891073', 'home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 6}`; minimum estimated local advantage: 0.6321089564624557; minimum army health fraction: 0.6657786885245902; last sampled army center: `[64.361083984375, 128.674072265625]`; observed enemy composition: `{'QUEEN': 1, 'ZERGLING': 7, 'ROACH': 6}`.
- 630–645s: army lost 775, army killed 350, economy killed 150; objectives `{'pressure': 3, 'recover': 9}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 6, 'STALKER': 1}`; minimum estimated local advantage: 0.23112948428861435; minimum army health fraction: 0.8346732365145229; last sampled army center: `[55.41455078125, 111.953369140625]`; observed enemy composition: `{'ZERGLING': 18, 'ROACH': 17, 'HYDRALISK': 8, 'RAVAGER': 2, 'QUEEN': 1}`.

### Zerg / Timing

Evidence: `runtime-20261031-152341-130739-bf72083b71384b4aa0e88720b46f0059-004.json`. End sample 1050.0s; peak 34 workers / 111 army supply. First offensive advance: 333.2s; first expansion advance: 333.2s; inspected sites: 8.

Movement: `{'offensive_target_switches': 17, 'short_target_reversals': 1, 'advance_regroup_transitions': 60, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 8985, 'sampled_long_move_reversals': 625}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 400.

Opponent prediction at last sample: **Unknown**, confidence 0.50. First correct confident classification: 619.3s; first home contact: 193.9s. Positive classification lead means recognition preceded contact: -425.4s.

- 510–525s: army lost 1050, army killed 600, economy killed 0; objectives `{'recover': 4, 'stabilize': 8}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 9, 'SENTRY': 1}`; minimum estimated local advantage: 0.7103667393053618; minimum army health fraction: 0.7807883522727272; last sampled army center: `None`; observed enemy composition: `{'ROACH': 13, 'RAVAGER': 2, 'HYDRALISK': 6, 'ZERGLING': 12, 'CHANGELINGZEALOT': 1}`.
- 495–510s: army lost 350, army killed 75, economy killed 0; objectives `{'recover': 6, 'pressure': 5}`, targets `['4356833284', 'home']`.
  Own army disappearances: `{'ZEALOT': 2, 'SENTRY': 1}`; minimum estimated local advantage: 0.46955590344971604; minimum army health fraction: 0.90625; last sampled army center: `None`; observed enemy composition: `{'ROACH': 13, 'RAVAGER': 2, 'HYDRALISK': 6, 'ZERGLING': 14, 'CHANGELINGZEALOT': 1}`.
- 435–450s: army lost 400, army killed 175, economy killed 0; objectives `{'pressure': 5, 'recover': 7}`, targets `['4346871810', 'home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.6969507903463349; minimum army health fraction: 0.960968660968661; last sampled army center: `[90.128662109375, 110.862060546875]`; observed enemy composition: `{'ZERGLING': 5, 'ROACH': 13, 'RAVAGER': 1, 'HYDRALISK': 5, 'CHANGELINGZEALOT': 1}`.
- Economic losses at 270–285s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 11}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 180 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 240 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 360 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.677 |
| 600 | 2 | 0.0% | 0.0% | 50.0% | 0.0% | 0.915 |
| final | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.564 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.3508011057677487. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
