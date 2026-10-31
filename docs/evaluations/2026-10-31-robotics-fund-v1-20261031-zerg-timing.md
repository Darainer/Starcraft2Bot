# Match evaluation: robotics-fund-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Timing | 3 Defeat | 575 / 2575 | 0.22 | 50 | 5 | 0 | 0 | 0 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Timing | 0 | 110.4s / 165.4s | 255-270s | 5.0 | 165.0 |

## Costly trade windows and match details

### Zerg / Timing

Evidence: `runtime-20261031-094448-760134-164b8f2c312a4c69b3d7fa6bb57266fe-001.json`. End sample 490.4s; peak 23 workers / 20 army supply. First offensive advance: not observed; first expansion advance: not observed; inspected sites: 7.

Movement: `{'offensive_target_switches': 0, 'short_target_reversals': 0, 'advance_regroup_transitions': 0, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 17, 'sampled_long_move_reversals': 0}`. Action rejections: `{}`.

Score-based bad-trade windows: 5; windows also showing own controlled-army disappearances: 5. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 2575.

Opponent prediction at last sample: **Power**, confidence 0.62. First correct confident classification: not observed; first home contact: 195.4s. Positive classification lead means recognition preceded contact: not observed.

- 255–270s: army lost 600, army killed 125, economy killed 0; objectives `{'stabilize': 1, 'recover': 2}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 3, 'SENTRY': 2}`; minimum estimated local advantage: 0.7303935730405375; minimum army health fraction: 0.7763157894736842; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 1, 'ROACH': 8}`.
- 270–285s: army lost 375, army killed 0, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 1, 'ZEALOT': 2}`; minimum estimated local advantage: 10.0; minimum army health fraction: 1.0; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 1, 'ROACH': 10}`.
- 315–330s: army lost 475, army killed 100, economy killed 0; objectives `{'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 1, 'ZEALOT': 3}`; minimum estimated local advantage: 0.10971796648189905; minimum army health fraction: 0.5486842105263158; last sampled army center: `None`; observed enemy composition: `{'ROACH': 14}`.
- Economic losses at 330–345s: 950 resources; own worker/base disappearances `{'PROBE': 20}`; objectives `{'recover': 2, 'stabilize': 1}`.
- Economic losses at 285–300s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 1}`.
- Economic losses at 360–375s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'develop': 1, 'recover': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 360 | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 0.992 |
| 600 | 0 | n/a | n/a | n/a | n/a | n/a |
| final | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 0.992 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 1 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.6239124966755631. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `reference-9fd64a1-limit3600-zerg-timing`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Zerg / Timing | Result.Victory → Result.Defeat | 2 → 0 | 15 → 0 | 1 → 5 |
