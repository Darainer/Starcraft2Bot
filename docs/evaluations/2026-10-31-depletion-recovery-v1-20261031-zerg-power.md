# Match evaluation: depletion-recovery-v1-20261031

Acceptance: **rejected**, three defeats at 1120.4 / 1120.4 / 1135.4 sampled game
seconds. The [actual Robotics-v2 parent](2026-10-31-robotics-fund-v2-zerg-power-reference.md)
also loses this condition, at 1620.4 in all three repeats. This variant fixes the
previous draft's unknown-resource exclusion but does not improve the outcome.
No broader retention is run.

Gameplay `4af6e8d` changes the expansion gate on `dc09385`, whose 43 source/config
files match frozen Robotics-v2 after newline normalization. It excludes the
counter-tech Bay/Colossus, wave-readiness and siege-approach experiments. The
[manifest](../experiments/2026-10-31/depletion-recovery-v1-manifest.json) records
exact candidate hashes. All starts match the established 3600-second Power
fingerprint; hashes remained unchanged, exact binary/map checks passed and all
three replays are nonempty. Locked checks, configured mypy, 518 tests (88.53%
coverage) and builds passed before freezing. Human controls remain unverified.

In the representative record the earlier worker gate moves the initial third
Nexus start from 420.4 to 390.4 seconds. By 705 seconds the candidate has 40
workers, two ready bases and 32 army supply, versus the parent's 56/3/68. It has
three ready bases again by 785.4 but loses its economy later. This rejects broad
earlier third-base funding as the current repair; it does not establish that
every late replacement gate is correct or that earlier expansion always fails.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Power | 3 Defeat | 10625 / 16575 | 0.64 | 1775 | 13 | 23 | 2 | 7 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Power | 0 | 110.4s / 165.4s | 330-345s | 15.0 | 1120.0 |

## Costly trade windows and match details

### Zerg / Power

Evidence: `runtime-20261031-104749-868959-7fc78a2414e14a17b0742749f2554f0e-001.json`. End sample 1120.4s; peak 56 workers / 81 army supply. First offensive advance: 255.4s; first expansion advance: 410.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 13, 'short_target_reversals': 2, 'advance_regroup_transitions': 7, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1040, 'sampled_long_move_reversals': 93}`. Action rejections: `{}`.

Score-based bad-trade windows: 13; windows also showing own controlled-army disappearances: 13. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 7350.

Opponent prediction at last sample: **Power**, confidence 0.65. First correct confident classification: 330.4s; first home contact: 220.4s. Positive classification lead means recognition preceded contact: -110.0s.

- 765–780s: army lost 2050, army killed 250, economy killed 200; objectives `{'recover': 2, 'pressure': 1}`, targets `['4355260430', 'home']`.
  Own army disappearances: `{'SENTRY': 2, 'STALKER': 2, 'IMMORTAL': 1, 'ZEALOT': 7}`; minimum estimated local advantage: 0.6558592650551762; minimum army health fraction: 0.7731104651162791; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 26, 'QUEEN': 1, 'RAVAGER': 2, 'ROACH': 11, 'HYDRALISK': 10, 'IMMORTAL': 1}`.
- 900–915s: army lost 1600, army killed 75, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 9, 'STALKER': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.7861505681818182; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 4, 'ROACH': 18, 'HYDRALISK': 14, 'ZERGLING': 16, 'CHANGELINGZEALOT': 2, 'QUEEN': 2}`.
- 1065–1080s: army lost 1825, army killed 700, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'SENTRY': 2, 'STALKER': 5, 'ZEALOT': 3, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.0900682376392103; minimum army health fraction: 0.43524590163934423; last sampled army center: `None`; observed enemy composition: `{'ROACH': 14, 'RAVAGER': 6, 'HYDRALISK': 15, 'QUEEN': 4, 'ZERGLING': 10, 'CHANGELINGZEALOT': 1, 'LURKERMPBURROWED': 2}`.
- Economic losses at 600–615s: 1500 resources; own worker/base disappearances `{'PROBE': 18, 'NEXUS': 1}`; objectives `{'stabilize': 2, 'pressure': 1}`.
- Economic losses at 915–930s: 950 resources; own worker/base disappearances `{'PROBE': 7, 'NEXUS': 1}`; objectives `{'recover': 1, 'stabilize': 2}`.
- Economic losses at 900–915s: 750 resources; own worker/base disappearances `{'PROBE': 17}`; objectives `{'recover': 3}`.

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
