# Match evaluation: production-v5-r1-20261031-zerg-macro

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit1500`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Defeat | 2650 / 7850 | 0.34 | 200 | 13 | 16 | 0 | 1 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 110.4s / 255.4s | 330-345s | 30.0 | 595.0 |

## Costly trade windows and match details

### Zerg / Macro

Evidence: `runtime-20261031-083711-157557-001.json`. End sample 875.4s; peak 42 workers / 55 army supply. First offensive advance: 275.4s; first expansion advance: 315.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 6, 'short_target_reversals': 0, 'advance_regroup_transitions': 1, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 499, 'sampled_long_move_reversals': 49}`. Action rejections: `{}`.

Score-based bad-trade windows: 13; windows also showing own controlled-army disappearances: 13. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 5525.

Opponent prediction at last sample: **Power**, confidence 0.65. First correct confident classification: not observed; first home contact: 195.4s. Positive classification lead means recognition preceded contact: not observed.

- 810–825s: army lost 775, army killed 50, economy killed 0; objectives `{'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 1, 'ZEALOT': 1, 'SENTRY': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.10590645670191365; minimum army health fraction: 0.4533333333333333; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 4, 'ROACH': 18, 'HYDRALISK': 12, 'ZERGLING': 21, 'QUEEN': 1, 'CORRUPTOR': 2}`.
- 765–780s: army lost 650, army killed 100, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 3, 'STALKER': 2}`; minimum estimated local advantage: 0.26409719273799415; minimum army health fraction: 0.639344262295082; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 4, 'ROACH': 18, 'HYDRALISK': 12, 'QUEEN': 2, 'ZERGLING': 19}`.
- 570–585s: army lost 575, army killed 100, economy killed 0; objectives `{'stabilize': 1, 'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 4, 'STALKER': 1}`; minimum estimated local advantage: 1.2373060652625172; minimum army health fraction: 0.9329710144927537; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 2, 'ROACH': 9, 'HYDRALISK': 8, 'ZERGLING': 4, 'CHANGELINGZEALOT': 1, 'QUEEN': 2}`.
- Economic losses at 645–660s: 1400 resources; own worker/base disappearances `{'PROBE': 18, 'NEXUS': 1}`; objectives `{'counterattack': 1, 'pressure': 1}`.
- Economic losses at 690–705s: 850 resources; own worker/base disappearances `{'PROBE': 9, 'NEXUS': 1}`; objectives `{'pressure': 2, 'recover': 1}`.
- Economic losses at 615–630s: 500 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 2, 'recover': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 360 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| final | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 1.276 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 1 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.6487856442839393. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `9fd64a1`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Zerg / Macro | Result.Defeat → Result.Defeat | 0 → 0 | 2 → 1 | 8 → 13 |
