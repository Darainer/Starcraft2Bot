# Match evaluation: sustainable-pressure-v1-20261031

Acceptance: **rejected as a Power repair**, three defeats at 1780.4 sampled
seconds. The Robotics-v2 parent loses at 1620.4; longer survival is not a win.
No wider matrix is run. Source `16d3016` changes only pressure's base ceiling
from three to four and worker cap from 56 to 70 on parent `dc09385`.

The full starting-state fingerprint intentionally differs from the parent only
in `settings.bases` and `settings.max_workers`. Deep comparison verified every
other field identical, including world positions/resources, map, player slots,
seed, step and 3600-second bound. All three candidate fingerprints match each
other. This report uses a separate configuration-ablation group; it must not be
presented as identical assistant settings. The original gate helper rejected its
post-game old-settings assertion; a dedicated validator checked these two
declared differences, exact ping/map, unchanged source and all three nonempty
replays without changing the original artifacts. It was not a launch/game failure.

The representative game starts its initial third Nexus at 420.4 seconds and
never starts a fourth. The changed limits are confirmed in recorded settings.
Declining capacity prevents worker production from reaching the unchanged
58-worker gate. Raising limits alone did not establish preemptive replacement
income. The [manifest](../experiments/2026-10-31/sustainable-pressure-v1-manifest.json)
records all frozen source/configuration hashes. Locked checks, configured mypy,
507 tests (88.51% coverage) and builds passed; human controls remain unverified.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-4base70worker-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `56217e014ab2c6e4a56262e9c8b1aca55d86e0a218c242b30966e6e54b126408`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Power | 3 Defeat | 24650 / 24800 | 0.99 | 7850 | 12 | 76 | 1 | 10 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Power | 0 | 110.4s / 165.4s | 330-345s | 5.0 | 1860.0 |

## Costly trade windows and match details

### Zerg / Power

Evidence: `runtime-20261031-105233-736092-c012d1e97b0142d3a66a127581198ac2-001.json`. End sample 1780.4s; peak 56 workers / 149 army supply. First offensive advance: 255.4s; first expansion advance: 405.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 25, 'short_target_reversals': 1, 'advance_regroup_transitions': 10, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 3020, 'sampled_long_move_reversals': 200}`. Action rejections: `{}`.

Score-based bad-trade windows: 12; windows also showing own controlled-army disappearances: 12. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 6900.

Opponent prediction at last sample: **Power**, confidence 0.65. First correct confident classification: 330.4s; first home contact: 220.4s. Positive classification lead means recognition preceded contact: -110.0s.

- 765–780s: army lost 3800, army killed 1200, economy killed 50; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 6, 'IMMORTAL': 5, 'COLOSSUS': 2}`; minimum estimated local advantage: 0.4935341439371004; minimum army health fraction: 0.7980736301369863; last sampled army center: `None`; observed enemy composition: `{'QUEEN': 2, 'ZERGLING': 15, 'ROACH': 15, 'RAVAGER': 2, 'HYDRALISK': 7, 'LURKERMPBURROWED': 2, 'BROODLING': 5, 'CHANGELINGZEALOT': 1, 'COLOSSUS': 1, 'IMMORTAL': 1}`.
- 1665–1680s: army lost 1550, army killed 0, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'IMMORTAL': 3, 'STALKER': 2, 'SENTRY': 1}`; minimum estimated local advantage: 0.006692029119267859; minimum army health fraction: 0.783935546875; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 13, 'ZERGLING': 4, 'ULTRALISK': 6, 'CORRUPTOR': 2, 'ROACH': 6, 'IMMORTAL': 2, 'QUEEN': 1}`.
- 1185–1200s: army lost 1425, army killed 50, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'IMMORTAL': 1, 'STALKER': 5, 'ZEALOT': 2}`; minimum estimated local advantage: 1.3175557822020236; minimum army health fraction: 0.9257000927511415; last sampled army center: `None`; observed enemy composition: `{'ULTRALISK': 5, 'ROACH': 15, 'RAVAGER': 2, 'HYDRALISK': 15, 'ZERGLING': 19, 'QUEEN': 1, 'LURKERMPBURROWED': 1, 'COLOSSUS': 1, 'BROODLING': 1}`.
- Economic losses at 1710–1725s: 1225 resources; own worker/base disappearances `{'ASSIMILATOR': 3, 'PROBE': 10, 'NEXUS': 1}`; objectives `{'stabilize': 2, 'develop': 1}`.
- Economic losses at 1665–1680s: 1000 resources; own worker/base disappearances `{'PROBE': 12, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 1065–1080s: 900 resources; own worker/base disappearances `{'PROBE': 10, 'NEXUS': 1}`; objectives `{'stabilize': 2, 'pressure': 1}`.

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
