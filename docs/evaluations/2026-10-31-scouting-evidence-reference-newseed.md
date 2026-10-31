# Match evaluation: scouting-evidence-reference-newseed

Model: `scouting-v1`. 15 matches; 5 distinct starting-condition groups.

Results: `{'Result.Victory': 15}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-2026103101-step8-limit3600-snapshot1-revisit0`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Rush | 3 Victory | 4025 / 1800 | 2.24 | 3425 | 1 | 72 | 1 | 25 |
| Zerg / Timing | 3 Victory | 14550 / 6925 | 2.10 | 9800 | 5 | 333 | 2 | 92 |
| Zerg / Power | 3 Victory | 12400 / 4925 | 2.52 | 6175 | 1 | 223 | 3 | 55 |
| Zerg / Macro | 3 Victory | 14775 / 7975 | 1.85 | 9100 | 5 | 253 | 2 | 50 |
| Zerg / Air | 3 Victory | 3050 / 775 | 3.94 | 3475 | 0 | 81 | 1 | 11 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Rush | 0 | 113.6s / 157.5s | 345-360s | 8.6 | 143.6 |
| Zerg / Timing | 0 | 113.6s / 157.5s | 510-525s | 8.6 | 803.6 |
| Zerg / Power | 0 | 113.6s / 158.6s | 435-450s | 32.1 | 731.8 |
| Zerg / Macro | 0 | 113.6s / 158.6s | 300-315s | 8.6 | 1397.1 |
| Zerg / Air | 0 | 113.6s / 148.9s | not recorded | 10.7 | 136.1 |

## Costly trade windows and match details

### Zerg / Rush

Evidence: `runtime-20261031-153301-710054-414455697aea44ae85a0419b6936b286-001.json`. End sample 616.1s; peak 54 workers / 79 army supply. First offensive advance: 225.0s; first expansion advance: 303.2s; inspected sites: 8.

Movement: `{'offensive_target_switches': 9, 'short_target_reversals': 1, 'advance_regroup_transitions': 25, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2774, 'sampled_long_move_reversals': 144}`. Action rejections: `{'880:44': 1}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Rush**, confidence 0.75. First correct confident classification: 133.9s; first home contact: 123.2s. Positive classification lead means recognition preceded contact: -10.7s.

- 345–360s: army lost 425, army killed 0, economy killed 100; objectives `{'contain': 4, 'pressure': 2, 'stabilize': 2, 'recover': 3}`, targets `['4348706818', 'home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 1, 'SENTRY': 1, 'STALKER': 1}`; minimum estimated local advantage: 1.2052611694912674; minimum army health fraction: 0.7494791666666667; last sampled army center: `[76.8050537109375, 51.8001708984375]`; observed enemy composition: `{'ZERGLING': 24, 'ROACH': 4}`.

### Zerg / Timing

Evidence: `runtime-20261031-153301-710054-414455697aea44ae85a0419b6936b286-004.json`. End sample 1256.8s; peak 34 workers / 133 army supply. First offensive advance: 339.6s; first expansion advance: 339.6s; inspected sites: 8.

Movement: `{'offensive_target_switches': 24, 'short_target_reversals': 2, 'advance_regroup_transitions': 92, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 12482, 'sampled_long_move_reversals': 915}`. Action rejections: `{}`.

Score-based bad-trade windows: 5; windows also showing own controlled-army disappearances: 5. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 450.

Opponent prediction at last sample: **Unknown**, confidence 0.50. First correct confident classification: 247.5s; first home contact: 191.8s. Positive classification lead means recognition preceded contact: -55.7s.

- 630–645s: army lost 1075, army killed 625, economy killed 0; objectives `{'pressure': 2, 'stabilize': 7, 'recover': 4}`, targets `['home', 'site:2', 'threat']`.
  Own army disappearances: `{'ZEALOT': 4, 'IMMORTAL': 1, 'SENTRY': 1, 'STALKER': 1}`; minimum estimated local advantage: 1.508154001357049; minimum army health fraction: 0.7188653846153846; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 2, 'HYDRALISK': 7, 'ROACH': 9, 'ZERGLING': 22, 'QUEEN': 1}`.
- 900–915s: army lost 350, army killed 0, economy killed 50; objectives `{'pressure': 2, 'contain': 9, 'recover': 2}`, targets `['4334813185', 'home', 'site:6']`.
  Own army disappearances: `{'STALKER': 2}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8950140449438202; last sampled army center: `None`; observed enemy composition: `{'BROODLORD': 1, 'QUEEN': 2, 'ZERGLING': 11, 'ROACH': 6, 'HYDRALISK': 3, 'BROODLING': 27}`.
- 585–600s: army lost 600, army killed 350, economy killed 0; objectives `{'pressure': 5, 'recover': 7}`, targets `['4346871810', '4355522565', 'home']`.
  Own army disappearances: `{'ZEALOT': 6}`; minimum estimated local advantage: 0.7554170626055404; minimum army health fraction: 0.8066395184135977; last sampled army center: `[50.36328125, 78.242919921875]`; observed enemy composition: `{'RAVAGER': 2, 'HYDRALISK': 6, 'ROACH': 7, 'CHANGELINGZEALOT': 1, 'ZERGLING': 10}`.
- Economic losses at 255–270s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 11}`.

### Zerg / Power

Evidence: `runtime-20261031-153301-710054-414455697aea44ae85a0419b6936b286-007.json`. End sample 991.1s; peak 56 workers / 137 army supply. First offensive advance: 247.5s; first expansion advance: 287.1s; inspected sites: 8.

Movement: `{'offensive_target_switches': 20, 'short_target_reversals': 3, 'advance_regroup_transitions': 55, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 9283, 'sampled_long_move_reversals': 592}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 1950.

Opponent prediction at last sample: **Macro**, confidence 0.68. First correct confident classification: not observed; first home contact: 185.4s. Positive classification lead means recognition preceded contact: not observed.

- 435–450s: army lost 650, army killed 100, economy killed 0; objectives `{'pressure': 2, 'recover': 12}`, targets `['4342153217', 'home']`.
  Own army disappearances: `{'SENTRY': 1, 'ZEALOT': 5}`; minimum estimated local advantage: 0.37470832745242516; minimum army health fraction: 0.8239382239382239; last sampled army center: `[78.25927734375, 38.92041015625]`; observed enemy composition: `{'ROACH': 9, 'ZERGLING': 9, 'RAVAGER': 2, 'HYDRALISK': 6, 'QUEEN': 1}`.
- Economic losses at 630–645s: 1250 resources; own worker/base disappearances `{'PROBE': 15, 'NEXUS': 1}`; objectives `{'pressure': 3, 'stabilize': 11}`.
- Economic losses at 645–660s: 700 resources; own worker/base disappearances `{'PROBE': 8}`; objectives `{'pressure': 8, 'stabilize': 2}`.

### Zerg / Macro

Evidence: `runtime-20261031-153301-710054-414455697aea44ae85a0419b6936b286-010.json`. End sample 1080.0s; peak 56 workers / 143 army supply. First offensive advance: 248.6s; first expansion advance: 294.6s; inspected sites: 8.

Movement: `{'offensive_target_switches': 22, 'short_target_reversals': 2, 'advance_regroup_transitions': 50, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 10106, 'sampled_long_move_reversals': 645}`. Action rejections: `{}`.

Score-based bad-trade windows: 5; windows also showing own controlled-army disappearances: 5. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Macro**, confidence 0.68. First correct confident classification: 549.6s; first home contact: 183.2s. Positive classification lead means recognition preceded contact: -366.4s.

- 645–660s: army lost 1025, army killed 175, economy killed 0; objectives `{'pressure': 4, 'recover': 10}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 1, 'STALKER': 3, 'VOIDRAY': 1}`; minimum estimated local advantage: 0.5048863721063716; minimum army health fraction: 0.9287162162162163; last sampled army center: `None`; observed enemy composition: `{'ROACH': 13, 'RAVAGER': 2, 'ZERGLING': 19, 'CORRUPTOR': 4, 'HYDRALISK': 6, 'MUTALISK': 6, 'BROODLING': 5}`.
- 300–315s: army lost 775, army killed 100, economy killed 100; objectives `{'pressure': 9, 'recover': 3}`, targets `['4342153217', 'home']`.
  Own army disappearances: `{'SENTRY': 2, 'STALKER': 1, 'ZEALOT': 3}`; minimum estimated local advantage: 0.5902862193458661; minimum army health fraction: 0.7262978142076503; last sampled army center: `[82.2734375, 29.71044921875]`; observed enemy composition: `{'ZERGLING': 11, 'ROACH': 8}`.
- 585–600s: army lost 800, army killed 175, economy killed 50; objectives `{'pressure': 2, 'recover': 12}`, targets `['4392222721', 'home']`.
  Own army disappearances: `{'SENTRY': 2, 'ZEALOT': 5}`; minimum estimated local advantage: 0.0; minimum army health fraction: 0.8938175675675676; last sampled army center: `[112.781005859375, 62.47998046875]`; observed enemy composition: `{'ROACH': 10, 'RAVAGER': 2, 'ZERGLING': 9, 'CORRUPTOR': 4, 'HYDRALISK': 6, 'MUTALISK': 3, 'BROODLING': 5}`.

### Zerg / Air

Evidence: `runtime-20261031-153301-710054-414455697aea44ae85a0419b6936b286-013.json`. End sample 551.8s; peak 54 workers / 75 army supply. First offensive advance: 250.7s; first expansion advance: 292.5s; inspected sites: 7.

Movement: `{'offensive_target_switches': 7, 'short_target_reversals': 1, 'advance_regroup_transitions': 11, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2117, 'sampled_long_move_reversals': 91}`. Action rejections: `{}`.

Score-based bad-trade windows: 0; windows also showing own controlled-army disappearances: 0. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: not observed; first home contact: 452.1s. Positive classification lead means recognition preceded contact: not observed.

No sampled 15-second window met the bad-trade threshold (loss ≥300 and >1.5× enemy army value killed).

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 5 | 0.0% | 0.0% | 0.0% | n/a | 0.831 |
| 180 | 5 | 20.0% | 20.0% | 20.0% | 100.0% | 0.686 |
| 240 | 5 | 20.0% | 20.0% | 20.0% | 100.0% | 0.686 |
| 360 | 5 | 40.0% | 40.0% | 60.0% | 66.7% | 0.569 |
| 600 | 4 | 75.0% | 75.0% | 100.0% | 75.0% | 0.465 |
| final | 5 | 40.0% | 40.0% | 60.0% | 66.7% | 0.473 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 1 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 1 | 0 | 0 |
| Macro | 0 | 0 | 0 | 1 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 1 |

Expected calibration error: 0.24218507328968136. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
