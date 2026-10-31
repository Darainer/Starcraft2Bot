# Match evaluation: scouting-evidence-revisit-targets

Model: `scouting-v1`. 6 matches; 2 distinct starting-condition groups.

Results: `{'Result.Victory': 6}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600-snapshot1-revisit1`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Victory | 11750 / 4800 | 2.45 | 5300 | 1 | 130 | 0 | 44 |
| Zerg / Timing | 3 Victory | 5950 / 1850 | 3.22 | 3675 | 1 | 82 | 2 | 13 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 108.2s / 167.1s | 300-315s | 6.4 | 511.1 |
| Zerg / Timing | 0 | 108.2s / 162.9s | 255-270s | 6.4 | 440.4 |

## Costly trade windows and match details

### Zerg / Macro

Evidence: `runtime-20261031-152351-728106-610a3ccbbf764d6ea0ff302ab4105781-001.json`. End sample 872.1s; peak 56 workers / 141 army supply. First offensive advance: 225.0s; first expansion advance: 286.1s; inspected sites: 8.

Movement: `{'offensive_target_switches': 13, 'short_target_reversals': 0, 'advance_regroup_transitions': 44, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 6227, 'sampled_long_move_reversals': 470}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 324.6s. Positive classification lead means recognition preceded contact: not observed.

- 300–315s: army lost 600, army killed 350, economy killed 150; objectives `{'pressure': 10, 'recover': 2}`, targets `['4341891073', 'home']`.
  Own army disappearances: `{'ZEALOT': 6}`; minimum estimated local advantage: 1.6580831506302718; minimum army health fraction: 0.631811377245509; last sampled army center: `[64.98193359375, 129.1981201171875]`; observed enemy composition: `{'QUEEN': 1, 'ZERGLING': 10, 'ROACH': 2}`.

### Zerg / Timing

Evidence: `runtime-20261031-152351-728106-610a3ccbbf764d6ea0ff302ab4105781-004.json`. End sample 639.6s; peak 34 workers / 81 army supply. First offensive advance: 241.1s; first expansion advance: 335.4s; inspected sites: 8.

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
| 600 | 2 | 50.0% | 50.0% | 50.0% | 100.0% | 0.525 |
| final | 2 | 50.0% | 50.0% | 50.0% | 100.0% | 0.525 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 1 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.3181328451336355. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
