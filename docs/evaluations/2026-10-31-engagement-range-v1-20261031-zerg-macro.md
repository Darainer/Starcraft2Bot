# Match evaluation: engagement-range-v1-20261031

Acceptance: **failed retention**, three defeats at 1010.4 / 1005.7 / 1130.4
sampled seconds. Counter-tech parent `a7cefe1` also loses Macro (3 defeats at
855.4), while accepted R2 won its original Macro triplet. The range change has
not repaired this composite's Macro failure. These results do not isolate which
earlier counter-tech change caused the R2 regression.

Gameplay stayed frozen at `287dbd5`. All three 3600-second reference starts,
source hashes, exact binary/map identities and nonempty replays passed
verification; see the [manifest](../experiments/2026-10-31/engagement-range-v1-manifest.json).
Terran successes are retained as experimental component evidence. The composite
is not promoted and no full matrix is run. Human controls remain unverified.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Macro | 3 Defeat | 6050 / 9100 | 0.67 | 1100 | 11 | 33 | 1 | 7 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Macro | 0 | 110.4s / 170.4s | 510-525s | 25.0 | 670.0 |

## Costly trade windows and match details

### Zerg / Macro

Evidence: `runtime-20261031-110626-657182-0fcef9628e3047b2adfc3b10a243d4f6-001.json`. End sample 1010.4s; peak 54 workers / 77 army supply. First offensive advance: 255.4s; first expansion advance: 310.4s; inspected sites: 7.

Movement: `{'offensive_target_switches': 10, 'short_target_reversals': 1, 'advance_regroup_transitions': 7, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 808, 'sampled_long_move_reversals': 64}`. Action rejections: `{}`.

Score-based bad-trade windows: 11; windows also showing own controlled-army disappearances: 11. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 8075.

Opponent prediction at last sample: **Power**, confidence 0.65. First correct confident classification: not observed; first home contact: 315.4s. Positive classification lead means recognition preceded contact: not observed.

- 645–660s: army lost 875, army killed 50, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 1, 'STALKER': 3}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.9247706422018349; last sampled army center: `None`; observed enemy composition: `{'ROACH': 17, 'HYDRALISK': 7, 'RAVAGER': 2, 'ZERGLING': 29, 'LURKERMPBURROWED': 1}`.
- 960–975s: army lost 700, army killed 0, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 1; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 10, 'LURKERMPBURROWED': 6, 'RAVAGER': 4, 'ROACH': 17, 'ZERGLING': 15}`.
- 765–780s: army lost 1025, army killed 350, economy killed 0; objectives `{'counterattack': 1, 'recover': 2}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'STALKER': 1, 'COLOSSUS': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 1.2833858228069395; minimum army health fraction: 0.649407114624506; last sampled army center: `None`; observed enemy composition: `{'ROACH': 13, 'HYDRALISK': 6, 'RAVAGER': 2, 'ZERGLING': 24, 'LURKERMPBURROWED': 1, 'QUEEN': 1, 'CHANGELINGZEALOT': 2, 'BROODLING': 4}`.
- Economic losses at 960–975s: 1400 resources; own worker/base disappearances `{'PROBE': 15, 'NEXUS': 1, 'ASSIMILATOR': 2}`; objectives `{'recover': 3}`.
- Economic losses at 930–945s: 1225 resources; own worker/base disappearances `{'PROBE': 11, 'NEXUS': 1, 'ASSIMILATOR': 1}`; objectives `{'stabilize': 1, 'develop': 2}`.
- Economic losses at 615–630s: 1150 resources; own worker/base disappearances `{'PROBE': 13, 'NEXUS': 1}`; objectives `{'recover': 2, 'stabilize': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 360 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 600 | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 1.276 |
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
