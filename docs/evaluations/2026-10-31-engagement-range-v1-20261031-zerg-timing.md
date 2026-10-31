# Match evaluation: engagement-range-v1-20261031

Acceptance: **failed targeted condition**, three defeats at 675.4 sampled seconds.
The frozen early-Robotics v2 revision and the extended historical reference each
won this condition in their own recorded triplets. The immediate counter-tech
parent `a7cefe1` has not had a separate Timing triplet, so this comparison cannot
attribute the failure to the new range rule alone; it tests the whole composite.

Gameplay `287dbd5` stayed unchanged. All three 3600-second reference starts,
source hashes, exact binary/map identities and nonempty replays passed
verification; see the [manifest](../experiments/2026-10-31/engagement-range-v1-manifest.json).
The third repeat finished after the first pair before any gameplay revision.
The composite is not promoted; no full matrix follows the Zerg failures.

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Defeat': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Timing | 3 Defeat | 525 / 4975 | 0.11 | 475 | 6 | 21 | 1 | 3 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Timing | 0 | 110.4s / 165.4s | 510-525s | 5.0 | 495.0 |

## Costly trade windows and match details

### Zerg / Timing

Evidence: `runtime-20261031-110636-218181-8d368986198748a887079c089ff0fe7a-001.json`. End sample 675.4s; peak 28 workers / 61 army supply. First offensive advance: 335.4s; first expansion advance: 335.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 5, 'short_target_reversals': 1, 'advance_regroup_transitions': 3, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 434, 'sampled_long_move_reversals': 70}`. Action rejections: `{}`.

Score-based bad-trade windows: 6; windows also showing own controlled-army disappearances: 6. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 3475.

Opponent prediction at last sample: **Unknown**, confidence 0.38. First correct confident classification: not observed; first home contact: 195.4s. Positive classification lead means recognition preceded contact: not observed.

- 630–645s: army lost 1600, army killed 25, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'IMMORTAL': 1, 'ZEALOT': 11, 'SENTRY': 1}`; minimum estimated local advantage: 0.07416374967145514; minimum army health fraction: 0.6566666666666666; last sampled army center: `None`; observed enemy composition: `{'ROACH': 20, 'RAVAGER': 2, 'HYDRALISK': 6, 'ZERGLING': 14, 'QUEEN': 1, 'MUTALISK': 2}`.
- 570–585s: army lost 675, army killed 0, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 1, 'STALKER': 1, 'SENTRY': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 1.0; last sampled army center: `None`; observed enemy composition: `{'ROACH': 20, 'RAVAGER': 2, 'HYDRALISK': 6, 'ZERGLING': 22, 'CHANGELINGZEALOT': 2, 'QUEEN': 1}`.
- 540–555s: army lost 625, army killed 0, economy killed 0; objectives `{'stabilize': 1, 'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 3, 'ZEALOT': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.9410658307210031; last sampled army center: `None`; observed enemy composition: `{'ROACH': 19, 'RAVAGER': 2, 'HYDRALISK': 6, 'ZERGLING': 14, 'CHANGELINGZEALOT': 2}`.
- Economic losses at 570–585s: 1250 resources; own worker/base disappearances `{'PROBE': 16, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 540–555s: 500 resources; own worker/base disappearances `{'NEXUS': 1, 'PROBE': 2}`; objectives `{'stabilize': 1, 'recover': 2}`.
- Economic losses at 270–285s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 2}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.955 |
| 360 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.554 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.554 |
| final | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.554 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.6210039616066774. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `reference-9fd64a1-limit3600-zerg-timing`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Zerg / Timing | Result.Victory → Result.Defeat | 2 → 1 | 15 → 3 | 1 → 6 |
