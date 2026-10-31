# Match evaluation: engagement-range-v1-20261031

Retention: **3 victories at 1090.4 sampled seconds**, preserving counter-tech's
Rush outcome (parent: 3 wins at 805.4). Gameplay remains `287dbd5`; all three
3600-second loop-zero fingerprints, source hashes, exact binary/map checks and
nonempty replays passed verification. See the
[manifest](../experiments/2026-10-31/engagement-range-v1-manifest.json).
This success does not establish global acceptance: the same frozen composite
lost its Zerg Macro and Timing triplets. No full matrix follows those failures.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Rush | 3 Victory | 9300 / 7375 | 1.26 | 5050 | 3 | 23 | 4 | 10 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Rush | 0 | 140.4s / 170.4s | 570-585s | 15.0 | 645.0 |

## Costly trade windows and match details

### Terran / Rush

Evidence: `runtime-20261031-110615-191814-0053a73dc6cc4e93a4758789f605a9da-001.json`. End sample 1090.4s; peak 34 workers / 111 army supply. First offensive advance: 315.4s; first expansion advance: 365.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 19, 'short_target_reversals': 4, 'advance_regroup_transitions': 10, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1574, 'sampled_long_move_reversals': 30}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 400.

Opponent prediction at last sample: **Rush**, confidence 0.75. First correct confident classification: 190.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: 5.0s.

- 570–585s: army lost 1725, army killed 625, economy killed 0; objectives `{'pressure': 3}`, targets `['4364435457', 'site:0']`.
  Own army disappearances: `{'STALKER': 7, 'ZEALOT': 5}`; minimum estimated local advantage: 2.525933200579882; minimum army health fraction: 0.9174418604651163; last sampled army center: `[53.990234375, 126.37744140625]`; observed enemy composition: `{'MARAUDER': 8, 'MARINE': 12}`.
- 585–600s: army lost 850, army killed 300, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'SENTRY': 1, 'IMMORTAL': 2}`; minimum estimated local advantage: 2.162351528807369; minimum army health fraction: 0.7582848837209303; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 7, 'MARINE': 9}`.
- 645–660s: army lost 350, army killed 0, economy killed 0; objectives `{'recover': 1}`, targets `['home']`.
  Own army disappearances: `{'IMMORTAL': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.9730769230769231; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 10, 'MARINE': 15}`.
- Economic losses at 210–225s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.076 |
| 360 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.076 |
| 600 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.076 |
| final | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 0.076 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 1 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.2471806885708312. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
