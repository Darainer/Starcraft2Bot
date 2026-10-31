# Match evaluation: scouting-evidence-v2-revisit-targets

Model: `scouting-v1`. 6 matches; 2 distinct starting-condition groups.

Results: `{'Result.Victory': 6}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600-snapshot1-revisit1`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Victory | 15025 / 7375 | 2.04 | 10475 | 3 | 171 | 2 | 40 |
| Zerg / Timing | 3 Victory | 5950 / 1850 | 3.22 | 3675 | 1 | 82 | 2 | 13 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 108.2s / 167.1s | 435-450s | 6.4 | 996.4 |
| Zerg / Timing | 0 | 108.2s / 162.9s | 255-270s | 6.4 | 440.4 |

## Costly trade windows and match details

### Zerg / Macro

Evidence: `runtime-20261031-153752-047446-ebde0b0ee4924870bba66057d86e3c66-001.json`. End sample 1122.1s; peak 56 workers / 141 army supply. First offensive advance: 239.3s; first expansion advance: 297.1s; inspected sites: 8.

Movement: `{'offensive_target_switches': 24, 'short_target_reversals': 2, 'advance_regroup_transitions': 40, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 11448, 'sampled_long_move_reversals': 480}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: 409.6s; first home contact: 313.2s. Positive classification lead means recognition preceded contact: -96.4s.

- 555–570s: army lost 1125, army killed 525, economy killed 100; objectives `{'pressure': 5, 'counterattack': 1, 'recover': 8}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 4, 'STALKER': 3, 'SENTRY': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.25320730148292075; minimum army health fraction: 0.7140625; last sampled army center: `[54.013916015625, 109.59912109375]`; observed enemy composition: `{'ROACH': 9, 'HYDRALISK': 8, 'RAVAGER': 2, 'ZERGLING': 14, 'CHANGELINGZEALOT': 1}`.
- 435–450s: army lost 1100, army killed 725, economy killed 0; objectives `{'pressure': 12, 'recover': 2}`, targets `['home', 'site:0', 'site:8']`.
  Own army disappearances: `{'ZEALOT': 8, 'SENTRY': 2}`; minimum estimated local advantage: 0.8657917344343007; minimum army health fraction: 0.8332479508196722; last sampled army center: `[63.85498046875, 114.47900390625]`; observed enemy composition: `{'ROACH': 7, 'HYDRALISK': 4, 'RAVAGER': 2, 'ZERGLING': 4}`.
- 675–690s: army lost 525, army killed 250, economy killed 100; objectives `{'pressure': 6, 'recover': 8}`, targets `['4357619722', 'home']`.
  Own army disappearances: `{'STALKER': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.44406577205372144; minimum army health fraction: 0.858600583090379; last sampled army center: `[93.7418212890625, 129.569091796875]`; observed enemy composition: `{'ROACH': 12, 'HYDRALISK': 13, 'RAVAGER': 3, 'ZERGLING': 17, 'CHANGELINGZEALOT': 2, 'QUEEN': 1, 'IMMORTAL': 1}`.

### Zerg / Timing

Evidence: `runtime-20261031-153752-047446-ebde0b0ee4924870bba66057d86e3c66-004.json`. End sample 639.6s; peak 34 workers / 81 army supply. First offensive advance: 241.1s; first expansion advance: 335.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 6, 'short_target_reversals': 2, 'advance_regroup_transitions': 13, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2507, 'sampled_long_move_reversals': 133}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 400.

Opponent prediction at last sample: **Timing**, confidence 0.56. First correct confident classification: 247.5s; first home contact: 193.9s. Positive classification lead means recognition preceded contact: -53.6s.

- 255–270s: army lost 400, army killed 100, economy killed 0; objectives `{'stabilize': 2, 'recover': 9}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.33367894989222374; minimum army health fraction: 0.6792207792207792; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 1, 'ROACH': 10}`.
- Economic losses at 285–300s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 10}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 180 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 240 | 2 | 0.0% | 0.0% | 0.0% | n/a | 0.877 |
| 360 | 2 | 50.0% | 50.0% | 50.0% | 100.0% | 0.525 |
| 600 | 2 | 100.0% | 100.0% | 100.0% | 100.0% | 0.164 |
| final | 2 | 100.0% | 100.0% | 100.0% | 100.0% | 0.164 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 1 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 1 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.34172318941905105. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
