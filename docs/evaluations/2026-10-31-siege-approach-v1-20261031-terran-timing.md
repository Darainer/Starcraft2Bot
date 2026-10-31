# Match evaluation: siege-approach-v1-20261031

Acceptance: **rejected as a Terran Timing repair**, three defeats at 910.4 sampled
game seconds. Gameplay commit `90f5277` is based on counter-tech `a7cefe1`, which
lost this condition at 845.4; a later defeat does not establish stronger play.
The separate observed-force wave gate is absent. No broader retention is run.

The [frozen manifest](../experiments/2026-10-31/siege-approach-v1-manifest.json)
identifies all source/configuration hashes. All three loop-zero states match the
3600-second reference, source hashes remained unchanged, ping/map identities
match and all three replays are nonempty. The run used three clients, pressure,
VeryHard Terran Timing, BelShirVestigeLE, seed 20261025 and step eight. Locked
sync/lint/format, configured mypy, 521 synthetic tests (88.64% coverage) and builds
passed before freezing. Human controls remain unverified.

The representative five-second recording includes one approach-phase sample at
445.4 seconds and a commit-phase sample at 530.4. This establishes that the path
ran, not its exact duration or effectiveness. It did not prevent the later
army/economy collapse. Further repair needs engagement-level participation and
range evidence; elapsed survival and the heuristic exposure score are insufficient.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Timing | 3 Defeat | 4850 / 13675 | 0.35 | 600 | 15 | 5 | 1 | 0 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Timing | 0 | 145.4s / 175.4s | 255-270s | 5.0 | 365.0 |

## Costly trade windows and match details

### Terran / Timing

Evidence: `runtime-20261031-103826-503967-32223136c4a048618b828495ed3d275c-001.json`. End sample 910.4s; peak 55 workers / 79 army supply. First offensive advance: 340.4s; first expansion advance: 505.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 3, 'short_target_reversals': 1, 'advance_regroup_transitions': 0, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 400, 'sampled_long_move_reversals': 21}`. Action rejections: `{'893:40': 1}`.

Score-based bad-trade windows: 15; windows also showing own controlled-army disappearances: 15. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 6875.

Opponent prediction at last sample: **Unknown**, confidence 0.42. First correct confident classification: 235.4s; first home contact: 250.4s. Positive classification lead means recognition preceded contact: 15.0s.

- 660–675s: army lost 1450, army killed 600, economy killed 0; objectives `{'stabilize': 2, 'recover': 1}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 6, 'STALKER': 2, 'SENTRY': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 1.068253930677793; minimum army health fraction: 0.8385309278350516; last sampled army center: `None`; observed enemy composition: `{'MARINE': 14, 'MARAUDER': 12, 'SIEGETANKSIEGED': 5, 'VIKINGFIGHTER': 1}`.
- 690–705s: army lost 1000, army killed 175, economy killed 0; objectives `{'recover': 2, 'stabilize': 1}`, targets `['home', 'threat']`.
  Own army disappearances: `{'STALKER': 4, 'ZEALOT': 3}`; minimum estimated local advantage: 2.773432245070156; minimum army health fraction: 0.7491191275167786; last sampled army center: `None`; observed enemy composition: `{'MARINE': 13, 'MARAUDER': 10, 'SIEGETANKSIEGED': 5, 'VIKINGFIGHTER': 1}`.
- 705–720s: army lost 1325, army killed 500, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 5, 'ZEALOT': 3, 'SENTRY': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.7273214285714286; last sampled army center: `None`; observed enemy composition: `{'MARINE': 14, 'MARAUDER': 11, 'SIEGETANKSIEGED': 4, 'SIEGETANK': 1, 'VIKINGASSAULT': 2}`.
- Economic losses at 720–735s: 1500 resources; own worker/base disappearances `{'PROBE': 20, 'NEXUS': 1}`; objectives `{'recover': 2, 'stabilize': 1}`.
- Economic losses at 825–840s: 1250 resources; own worker/base disappearances `{'PROBE': 14, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 810–825s: 775 resources; own worker/base disappearances `{'NEXUS': 1, 'ASSIMILATOR': 1, 'PROBE': 6}`; objectives `{'recover': 3}`.

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
