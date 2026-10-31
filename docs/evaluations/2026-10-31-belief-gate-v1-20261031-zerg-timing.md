# Match evaluation: belief-gate-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Timing | 3 Defeat | 3175 / 10275 | 0.31 | 300 | 13 | 3 | 0 | 2 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Timing | 0 | 110.4s / 165.4s | 270-285s | 25.0 | 90.0 |

## Costly trade windows and match details

### Zerg / Timing

Evidence: `runtime-20261031-094024-770488-7347a01a19e2406dabb7535b952b07ea-001.json`. End sample 820.4s; peak 34 workers / 43 army supply. First offensive advance: 375.4s; first expansion advance: 425.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 7, 'short_target_reversals': 0, 'advance_regroup_transitions': 2, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 296, 'sampled_long_move_reversals': 21}`. Action rejections: `{}`.

Score-based bad-trade windows: 13; windows also showing own controlled-army disappearances: 13. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 4000.

Opponent prediction at last sample: **Unknown**, confidence 0.50. First correct confident classification: 250.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: -55.0s.

- 435–450s: army lost 1050, army killed 75, economy killed 150; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 6}`; minimum estimated local advantage: 0.32712214329705835; minimum army health fraction: 0.9119912790697674; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 4, 'ROACH': 12, 'RAVAGER': 2, 'HYDRALISK': 5}`.
- 750–765s: army lost 950, army killed 25, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 6, 'STALKER': 2}`; minimum estimated local advantage: 0.11808553435768128; minimum army health fraction: 0.6283514492753624; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 2, 'ROACH': 10, 'HYDRALISK': 6, 'ZERGLING': 19, 'MUTALISK': 8, 'QUEEN': 2, 'CHANGELINGZEALOT': 3, 'CORRUPTOR': 2}`.
- 675–690s: army lost 900, army killed 75, economy killed 0; objectives `{'recover': 2, 'pressure': 1}`, targets `['4365221893', 'home']`.
  Own army disappearances: `{'STALKER': 2, 'ZEALOT': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.19380802276353956; minimum army health fraction: 0.8141774891774892; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 2, 'ROACH': 9, 'HYDRALISK': 6, 'ZERGLING': 10, 'MUTALISK': 7, 'QUEEN': 2, 'CHANGELINGZEALOT': 1}`.
- Economic losses at 705–720s: 1350 resources; own worker/base disappearances `{'PROBE': 17, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 735–750s: 800 resources; own worker/base disappearances `{'PROBE': 14}`; objectives `{'recover': 3}`.
- Economic losses at 330–345s: 600 resources; own worker/base disappearances `{'PROBE': 4, 'NEXUS': 1}`; objectives `{'stabilize': 2, 'recover': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 360 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.554 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.554 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.328 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.5016022115354974. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `reference-9fd64a1-limit3600-zerg-timing`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Zerg / Timing | Result.Victory → Result.Defeat | 2 → 0 | 15 → 2 | 1 → 13 |
