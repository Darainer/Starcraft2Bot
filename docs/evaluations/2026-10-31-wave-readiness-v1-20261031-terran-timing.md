# Match evaluation: wave-readiness-v1-20261031

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Timing | 3 Defeat | 7000 / 19975 | 0.35 | 2325 | 11 | 14 | 1 | 7 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Timing | 0 | 145.4s / 175.4s | 255-270s | 25.0 | 860.0 |

## Costly trade windows and match details

### Terran / Timing

Evidence: `runtime-20261031-102257-592094-c137f68465c541abb32c4873d87215f2-001.json`. End sample 1055.4s; peak 56 workers / 119 army supply. First offensive advance: 370.4s; first expansion advance: 545.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 5, 'short_target_reversals': 1, 'advance_regroup_transitions': 7, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 955, 'sampled_long_move_reversals': 73}`. Action rejections: `{'direct:3674:113': 6}`.

Score-based bad-trade windows: 11; windows also showing own controlled-army disappearances: 11. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 6875.

Opponent prediction at last sample: **Unknown**, confidence 0.42. First correct confident classification: 235.4s; first home contact: 250.4s. Positive classification lead means recognition preceded contact: 15.0s.

- 735–750s: army lost 3800, army killed 475, economy killed 325; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 5, 'STALKER': 10, 'IMMORTAL': 4, 'SENTRY': 1}`; minimum estimated local advantage: 0.39101964975239095; minimum army health fraction: 0.7116869918699187; last sampled army center: `None`; observed enemy composition: `{'MARINE': 19, 'MARAUDER': 10, 'SIEGETANKSIEGED': 6, 'VIKINGASSAULT': 3, 'VIKINGFIGHTER': 1, 'GHOST': 1}`.
- 960–975s: army lost 3700, army killed 1525, economy killed 0; objectives `{'stabilize': 1, 'recover': 2}`, targets `['home', 'threat']`.
  Own army disappearances: `{'STALKER': 12, 'ZEALOT': 4, 'IMMORTAL': 3, 'SENTRY': 1}`; minimum estimated local advantage: 0.43084250738746377; minimum army health fraction: 0.646236559139785; last sampled army center: `None`; observed enemy composition: `{'MARINE': 21, 'MARAUDER': 16, 'SIEGETANKSIEGED': 6, 'VIKINGASSAULT': 3, 'GHOST': 3}`.
- 930–945s: army lost 2050, army killed 725, economy killed 0; objectives `{'recover': 1, 'stabilize': 2}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 12, 'STALKER': 2, 'SENTRY': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 1.12352575372416; minimum army health fraction: 0.8323434622467771; last sampled army center: `None`; observed enemy composition: `{'MARINE': 21, 'MARAUDER': 16, 'SIEGETANKSIEGED': 6, 'VIKINGASSAULT': 3, 'GHOST': 4}`.
- Economic losses at 915–930s: 1750 resources; own worker/base disappearances `{'PROBE': 18, 'NEXUS': 1}`; objectives `{'stabilize': 2, 'recover': 1}`.
- Economic losses at 975–990s: 1450 resources; own worker/base disappearances `{'PROBE': 16, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 1020–1035s: 1250 resources; own worker/base disappearances `{'PROBE': 19}`; objectives `{'stabilize': 1, 'recover': 2}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |
| 360 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.524 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.524 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.584373412840788. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
