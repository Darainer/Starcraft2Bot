# Match evaluation: robotics-fund-v2-zerg-power-reference

This is a **subset of the completed Robotics-v2 matrix**, not a new live batch.
All three Power games lost at 1620.4 sampled game seconds. Commit `dc09385`
preserves the evaluated parent: all 43 frozen source/configuration files match
the original archive after newline normalization. Exact original byte hashes
remain in that archive; the raw results have not been rewritten.

The representative parent had already begun a third Nexus by the 420.4-second
sample and had three ready bases by 705 seconds. At 1400.4 it has lost a base,
has two remaining mineral lines with zero ideal harvesters, 31 idle workers,
10 minerals and 813 gas. The worker-gate issue concerns a **replacement base**
after losses/depletion; it does not establish that the initial third was never
built. Combat losses and the three-base ceiling also matter. The separate
depletion candidate changes the attainable worker gate and ordinary expansion
resource check while retaining that ceiling.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Power | 3 Defeat | 18300 / 27825 | 0.66 | 7550 | 14 | 67 | 1 | 15 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Power | 0 | 110.4s / 165.4s | 330-345s | 5.0 | 1675.0 |

## Costly trade windows and match details

### Zerg / Power

Evidence: `runtime-20261031-100009-792561-8b7ef61b2af1415fb22465b3c08fb9d1-004.json`. End sample 1620.4s; peak 56 workers / 143 army supply. First offensive advance: 255.4s; first expansion advance: 405.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 24, 'short_target_reversals': 1, 'advance_regroup_transitions': 15, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2418, 'sampled_long_move_reversals': 207}`. Action rejections: `{}`.

Score-based bad-trade windows: 14; windows also showing own controlled-army disappearances: 14. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 6350.

Opponent prediction at last sample: **Power**, confidence 0.65. First correct confident classification: 330.4s; first home contact: 220.4s. Positive classification lead means recognition preceded contact: -110.0s.

- 1020–1035s: army lost 5925, army killed 2875, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 12, 'IMMORTAL': 4, 'STALKER': 19}`; minimum estimated local advantage: 0.2616289693702599; minimum army health fraction: 0.8158633667883212; last sampled army center: `None`; observed enemy composition: `{'ROACH': 10, 'ULTRALISK': 3, 'RAVAGER': 2, 'ZERGLING': 5, 'HYDRALISK': 12, 'LURKERMPBURROWED': 2, 'BROODLING': 8, 'CHANGELINGZEALOT': 4}`.
- 765–780s: army lost 3800, army killed 1200, economy killed 50; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 6, 'IMMORTAL': 5, 'COLOSSUS': 2}`; minimum estimated local advantage: 0.4935341439371004; minimum army health fraction: 0.7980736301369863; last sampled army center: `None`; observed enemy composition: `{'QUEEN': 2, 'ZERGLING': 15, 'ROACH': 15, 'RAVAGER': 2, 'HYDRALISK': 7, 'LURKERMPBURROWED': 2, 'BROODLING': 5, 'CHANGELINGZEALOT': 1, 'COLOSSUS': 1, 'IMMORTAL': 1}`.
- 1035–1050s: army lost 1850, army killed 550, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 6, 'IMMORTAL': 2, 'ZEALOT': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8767282958199357; last sampled army center: `None`; observed enemy composition: `{'ROACH': 10, 'ULTRALISK': 3, 'RAVAGER': 2, 'ZERGLING': 13, 'HYDRALISK': 12, 'LURKERMPBURROWED': 2, 'BROODLING': 8, 'CHANGELINGZEALOT': 4, 'QUEEN': 1}`.
- Economic losses at 1275–1290s: 1700 resources; own worker/base disappearances `{'PROBE': 22, 'NEXUS': 1}`; objectives `{'stabilize': 3}`.
- Economic losses at 1560–1575s: 1425 resources; own worker/base disappearances `{'ASSIMILATOR': 1, 'PROBE': 23}`; objectives `{'stabilize': 2}`.
- Economic losses at 1530–1545s: 850 resources; own worker/base disappearances `{'PROBE': 5, 'NEXUS': 1}`; objectives `{'recover': 2}`.

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
| final | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 1 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.35121435571606074. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
