# Match evaluation: production-v5-r2-20261031-terran-air

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit1500`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Air | 3 Victory | 5175 / 1100 | 4.71 | 6350 | 1 | 15 | 1 | 10 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Air | 0 | 140.4s / 170.4s | 375-390s | 10.0 | 750.0 |

## Costly trade windows and match details

### Terran / Air

Evidence: `runtime-20261031-085126-150544-001.json`. End sample 720.4s; peak 56 workers / 115 army supply. First offensive advance: 275.4s; first expansion advance: 315.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 13, 'short_target_reversals': 1, 'advance_regroup_transitions': 10, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1097, 'sampled_long_move_reversals': 60}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: 355.4s; first home contact: not observed. Positive classification lead means recognition preceded contact: not observed.

- 375–390s: army lost 400, army killed 0, economy killed 0; objectives `{'contain': 1, 'recover': 1}`, targets `['4334813185', 'home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 2.215573833317405; minimum army health fraction: 0.566453488372093; last sampled army center: `[50.66943359375, 121.852294921875]`; observed enemy composition: `{'VIKINGASSAULT': 4, 'MARINE': 5, 'BATTLECRUISER': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 360 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.034 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.443 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.443 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 1 |

Expected calibration error: 0.5953903248083103. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `9fd64a1`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Terran / Air | Result.Victory → Result.Victory | 1 → 1 | 35 → 10 | 2 → 1 |
