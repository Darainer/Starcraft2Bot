# Match evaluation: scouting-evidence-reference-newseed2

Model: `scouting-v1`. 15 matches; 5 distinct starting-condition groups.

Results: `{'Result.Victory': 9, 'Result.Defeat': 6}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-2026103102-step8-limit3600-snapshot1-revisit0`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Rush | 3 Victory | 2350 / 100 | 23.50 | 2050 | 0 | 29 | 0 | 4 |
| Zerg / Timing | 3 Victory | 5150 / 2200 | 2.34 | 3950 | 2 | 73 | 0 | 17 |
| Zerg / Power | 3 Defeat | 7825 / 13300 | 0.59 | 2200 | 15 | 162 | 0 | 45 |
| Zerg / Macro | 3 Defeat | 8050 / 10275 | 0.78 | 2750 | 9 | 122 | 0 | 39 |
| Zerg / Air | 3 Victory | 1450 / 350 | 4.14 | 3200 | 0 | 47 | 0 | 8 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Rush | 0 | 108.2s / 167.1s | not recorded | 6.4 | 234.6 |
| Zerg / Timing | 0 | 108.2s / 167.1s | 315-330s | 6.4 | 558.2 |
| Zerg / Power | 0 | 108.2s / 167.1s | 300-315s | 6.4 | 760.7 |
| Zerg / Macro | 0 | 108.2s / 167.1s | 405-420s | 132.9 | 255.0 |
| Zerg / Air | 0 | 108.2s / 161.8s | not recorded | 6.4 | 50.4 |

## Costly trade windows and match details

### Zerg / Rush

Evidence: `runtime-20261031-154757-540900-f88daf83d4884acda04ee90b536c9f7a-001.json`. End sample 470.4s; peak 41 workers / 61 army supply. First offensive advance: 243.2s; first expansion advance: 308.6s; inspected sites: 8.

Movement: `{'offensive_target_switches': 3, 'short_target_reversals': 0, 'advance_regroup_transitions': 4, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1346, 'sampled_long_move_reversals': 60}`. Action rejections: `{}`.

Score-based bad-trade windows: 0; windows also showing own controlled-army disappearances: 0. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 125.4s. Positive classification lead means recognition preceded contact: not observed.

No sampled 15-second window met the bad-trade threshold (loss ≥300 and >1.5× enemy army value killed).

### Zerg / Timing

Evidence: `runtime-20261031-154757-540900-f88daf83d4884acda04ee90b536c9f7a-004.json`. End sample 769.3s; peak 56 workers / 129 army supply. First offensive advance: 256.1s; first expansion advance: 292.5s; inspected sites: 8.

Movement: `{'offensive_target_switches': 13, 'short_target_reversals': 0, 'advance_regroup_transitions': 17, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 6231, 'sampled_long_move_reversals': 425}`. Action rejections: `{}`.

Score-based bad-trade windows: 2; windows also showing own controlled-army disappearances: 2. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Timing**, confidence 0.56. First correct confident classification: 215.4s; first home contact: 178.9s. Positive classification lead means recognition preceded contact: -36.4s.

- 315–330s: army lost 300, army killed 25, economy killed 0; objectives `{'stabilize': 1, 'recover': 10, 'pressure': 1}`, targets `['4341891074', 'home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 3}`; minimum estimated local advantage: 0.48863346008398706; minimum army health fraction: 0.827710843373494; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 30}`.
- 585–600s: army lost 400, army killed 250, economy killed 150; objectives `{'pressure': 12, 'contain': 2}`, targets `['4334813185']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 4.428643304532971; minimum army health fraction: 0.7866304347826087; last sampled army center: `[41.482666015625, 133.1142578125]`; observed enemy composition: `{'ZERGLING': 11, 'HYDRALISK': 3, 'RAVAGER': 2, 'ROACH': 4, 'BROODLING': 7, 'QUEEN': 1}`.

### Zerg / Power

Evidence: `runtime-20261031-154757-540900-f88daf83d4884acda04ee90b536c9f7a-007.json`. End sample 1237.5s; peak 54 workers / 77 army supply. First offensive advance: 242.1s; first expansion advance: 292.5s; inspected sites: 8.

Movement: `{'offensive_target_switches': 19, 'short_target_reversals': 0, 'advance_regroup_transitions': 45, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 5141, 'sampled_long_move_reversals': 364}`. Action rejections: `{'direct:3674:3': 1}`.

Score-based bad-trade windows: 15; windows also showing own controlled-army disappearances: 15. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 7350.

Opponent prediction at last sample: **Unknown**, confidence 0.54. First correct confident classification: 383.6s; first home contact: 317.1s. Positive classification lead means recognition preceded contact: -66.4s.

- 1110–1125s: army lost 1000, army killed 25, economy killed 0; objectives `{'recover': 14}`, targets `['home']`.
  Own army disappearances: `{'COLOSSUS': 1, 'STALKER': 2, 'SENTRY': 1}`; minimum estimated local advantage: 0.20482309755100522; minimum army health fraction: 0.7785407725321889; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 4, 'ROACH': 21, 'HYDRALISK': 13, 'ZERGLING': 18, 'LURKERMPBURROWED': 2, 'CHANGELINGZEALOT': 3, 'QUEEN': 3, 'IMMORTAL': 1}`.
- 1065–1080s: army lost 1025, army killed 225, economy killed 0; objectives `{'stabilize': 12, 'recover': 1}`, targets `['home', 'threat']`.
  Own army disappearances: `{'SENTRY': 1, 'ZEALOT': 7, 'STALKER': 1}`; minimum estimated local advantage: 1.7381994383423849; minimum army health fraction: 0.7719424460431654; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 4, 'ZERGLING': 15, 'ROACH': 16, 'HYDRALISK': 12, 'CHANGELINGZEALOT': 3, 'LURKERMPBURROWED': 2, 'QUEEN': 2}`.
- 540–555s: army lost 700, army killed 75, economy killed 0; objectives `{'recover': 14}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 4}`; minimum estimated local advantage: 0.1543929113541977; minimum army health fraction: 0.731845238095238; last sampled army center: `None`; observed enemy composition: `{'ROACH': 12, 'ZERGLING': 14, 'HYDRALISK': 10, 'RAVAGER': 2}`.
- Economic losses at 1110–1125s: 1300 resources; own worker/base disappearances `{'PROBE': 18, 'NEXUS': 1}`; objectives `{'recover': 14}`.
- Economic losses at 600–615s: 1200 resources; own worker/base disappearances `{'PROBE': 16, 'NEXUS': 1}`; objectives `{'pressure': 14}`.
- Economic losses at 645–660s: 1100 resources; own worker/base disappearances `{'PROBE': 12, 'NEXUS': 1}`; objectives `{'recover': 6, 'stabilize': 1}`.

### Zerg / Macro

Evidence: `runtime-20261031-154757-540900-f88daf83d4884acda04ee90b536c9f7a-010.json`. End sample 1068.2s; peak 54 workers / 85 army supply. First offensive advance: 243.2s; first expansion advance: 296.8s; inspected sites: 8.

Movement: `{'offensive_target_switches': 9, 'short_target_reversals': 0, 'advance_regroup_transitions': 39, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 5577, 'sampled_long_move_reversals': 325}`. Action rejections: `{'direct:881:41': 1}`.

Score-based bad-trade windows: 9; windows also showing own controlled-army disappearances: 9. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 8125.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: 416.8s; first home contact: 313.9s. Positive classification lead means recognition preceded contact: -102.9s.

- 810–825s: army lost 625, army killed 50, economy killed 0; objectives `{'recover': 6}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 3, 'ZEALOT': 1}`; minimum estimated local advantage: 0.36383615618185466; minimum army health fraction: 0.8412836322869955; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 10, 'RAVAGER': 2, 'ROACH': 18, 'ZERGLING': 17, 'QUEEN': 2, 'LURKERMPBURROWED': 1, 'CHANGELINGZEALOT': 1, 'BROODLING': 6}`.
- 615–630s: army lost 525, army killed 0, economy killed 0; objectives `{'stabilize': 2, 'recover': 12}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 3}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.9351624015748031; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 8, 'RAVAGER': 2, 'ROACH': 13, 'ZERGLING': 19, 'QUEEN': 1}`.
- 660–675s: army lost 525, army killed 0, economy killed 0; objectives `{'recover': 11, 'pressure': 3}`, targets `['home', 'site:4']`.
  Own army disappearances: `{'STALKER': 1, 'ZEALOT': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.9636341222879684; last sampled army center: `[45.63330078125, 26.636474609375]`; observed enemy composition: `{'HYDRALISK': 8, 'RAVAGER': 1, 'ROACH': 16, 'ZERGLING': 28}`.
- Economic losses at 915–930s: 1200 resources; own worker/base disappearances `{'PROBE': 16, 'NEXUS': 1}`; objectives `{'recover': 11, 'develop': 3}`.
- Economic losses at 615–630s: 1000 resources; own worker/base disappearances `{'PROBE': 12, 'NEXUS': 1}`; objectives `{'stabilize': 2, 'recover': 12}`.
- Economic losses at 660–675s: 800 resources; own worker/base disappearances `{'PROBE': 4, 'NEXUS': 1}`; objectives `{'recover': 11, 'pressure': 3}`.

### Zerg / Air

Evidence: `runtime-20261031-154757-540900-f88daf83d4884acda04ee90b536c9f7a-013.json`. End sample 453.2s; peak 41 workers / 55 army supply. First offensive advance: 243.2s; first expansion advance: 300.0s; inspected sites: 4.

Movement: `{'offensive_target_switches': 4, 'short_target_reversals': 0, 'advance_regroup_transitions': 8, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1213, 'sampled_long_move_reversals': 30}`. Action rejections: `{}`.

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
| 240 | 5 | 20.0% | 20.0% | 20.0% | 100.0% | 0.690 |
| 360 | 5 | 20.0% | 20.0% | 20.0% | 100.0% | 0.690 |
| 600 | 3 | 33.3% | 33.3% | 33.3% | 100.0% | 0.442 |
| final | 5 | 40.0% | 40.0% | 40.0% | 100.0% | 0.464 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 1 |
| Timing | 0 | 1 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 1 |
| Macro | 0 | 0 | 0 | 1 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 1 |

Expected calibration error: 0.307821772715413. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
