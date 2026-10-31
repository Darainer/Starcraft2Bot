# Match evaluation: engagement-range-v1-20261031

Targeted gate: **3 victories at 1180.4 sampled game seconds**, improving this
condition over counter-tech parent `a7cefe1` (3 defeats at 845.4). Gameplay
`287dbd5` changes engaged-wave destinations for actors that cannot yet reach a
visible local combat target. Already in-range actors keep existing formation
behavior; mission/micro retreat and ownership arbitration remain in place.
The separate siege, readiness and expansion drafts are excluded.

All three full loop-zero states and hashes match the established 3600-second
Terran Timing reference. Exact ping/map identity, unchanged source hashes and
three nonempty replays passed verification. See the
[manifest](../experiments/2026-10-31/engagement-range-v1-manifest.json).
Locked sync/lint/format, configured mypy, 521 tests (88.58% coverage) and builds
passed before freezing. Human controls remain unverified.

The representative run reaches 127 army supply versus the parent's 51 and
records much less own economic loss (250 versus 6650 resource-score units).
Its army trade ratio remains below one (0.87); an objective win and sustained
income cannot be replaced by that ratio alone. Two recorded action rejections
remain visible below. Correlated snapshots and score categories do not identify
the exact causal contribution of every unit. Terran Rush, Zerg Macro and Zerg
Timing are tested next on unchanged gameplay before any promotion.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Timing | 3 Victory | 12700 / 14600 | 0.87 | 12275 | 10 | 43 | 3 | 5 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Timing | 0 | 145.4s / 175.4s | 255-270s | 5.0 | 915.0 |

## Costly trade windows and match details

### Terran / Timing

Evidence: `runtime-20261031-110231-595566-d09647961649442bb13e64233a145126-001.json`. End sample 1180.4s; peak 56 workers / 127 army supply. First offensive advance: 340.4s; first expansion advance: 500.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 22, 'short_target_reversals': 3, 'advance_regroup_transitions': 5, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2092, 'sampled_long_move_reversals': 127}`. Action rejections: `{'direct:3674:113': 2}`.

Score-based bad-trade windows: 10; windows also showing own controlled-army disappearances: 10. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 250.

Opponent prediction at last sample: **Timing**, confidence 0.65. First correct confident classification: 235.4s; first home contact: 250.4s. Positive classification lead means recognition preceded contact: 15.0s.

- 720–735s: army lost 2725, army killed 925, economy killed 0; objectives `{'contain': 2, 'recover': 1}`, targets `['4352376836', 'home']`.
  Own army disappearances: `{'IMMORTAL': 4, 'STALKER': 7, 'ZEALOT': 1}`; minimum estimated local advantage: 1.9373615492689287; minimum army health fraction: 0.9103030303030303; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 12, 'MARINE': 14, 'SIEGETANKSIEGED': 4, 'SIEGETANK': 1, 'VIKINGASSAULT': 1}`.
- 375–390s: army lost 1150, army killed 175, economy killed 0; objectives `{'pressure': 2, 'recover': 1}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 3, 'SENTRY': 1, 'IMMORTAL': 2}`; minimum estimated local advantage: 0.925526623341143; minimum army health fraction: 0.9486842105263158; last sampled army center: `[61.3660888671875, 116.1495361328125]`; observed enemy composition: `{'MARAUDER': 9, 'MARINE': 14}`.
- 915–930s: army lost 700, army killed 0, economy killed 1650; objectives `{'pressure': 3}`, targets `['site:0']`.
  Own army disappearances: `{'IMMORTAL': 1, 'STALKER': 2}`; minimum estimated local advantage: 3.930766752975444; minimum army health fraction: 0.8168499353169469; last sampled army center: `[48.675537109375, 108.179443359375]`; observed enemy composition: `{'MARINE': 12, 'VIKINGASSAULT': 1, 'GHOST': 1, 'MARAUDER': 6, 'VIKINGFIGHTER': 1}`.

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
| final | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.154 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 1 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.35121435571606074. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
