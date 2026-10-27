# Match evaluation: pressure-fight-v5-power-targeted

Model: `scouting-v1`. 3 matches; 1 distinct starting-condition groups.

Results: `{'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit1500`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Power | 3 Victory | 16025 / 15025 | 1.07 | 13225 | 7 | 65 | 5 | 17 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Power | 0 | 140.4s / 190.4s | 405-420s | 20.0 | 1610.0 |

## Costly trade windows and match details

### Terran / Power

Evidence: `runtime-20261027-232551-396380-001.json`. End sample 1335.4s; peak 56 workers / 123 army supply. First offensive advance: 285.4s; first expansion advance: 325.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 28, 'short_target_reversals': 5, 'advance_regroup_transitions': 17, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2965, 'sampled_long_move_reversals': 238}`. Action rejections: `{}`.

Score-based bad-trade windows: 7; windows also showing own controlled-army disappearances: 7. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 1500.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: not observed; first home contact: 540.4s. Positive classification lead means recognition preceded contact: not observed.

- 780–795s: army lost 2300, army killed 150, economy killed 100; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 2, 'IMMORTAL': 2, 'STALKER': 8}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8712761324041812; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 10, 'MARINE': 14, 'SIEGETANKSIEGED': 1}`.
- 765–780s: army lost 700, army killed 100, economy killed 450; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 7}`; minimum estimated local advantage: 0.5515123829500187; minimum army health fraction: 0.9285433070866141; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 10, 'MARINE': 15, 'SIEGETANK': 1}`.
- 465–480s: army lost 600, army killed 100, economy killed 0; objectives `{'pressure': 1, 'recover': 1}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 6}`; minimum estimated local advantage: 1.2623535859048078; minimum army health fraction: 0.9094202898550725; last sampled army center: `[48.887451171875, 102.493408203125]`; observed enemy composition: `{'MARINE': 15, 'MARAUDER': 13, 'SIEGETANKSIEGED': 3}`.
- Economic losses at 555–570s: 1000 resources; own worker/base disappearances `{'PROBE': 10, 'NEXUS': 1}`; objectives `{'pressure': 2}`.
- Economic losses at 540–555s: 500 resources; own worker/base disappearances `{'PROBE': 6}`; objectives `{'stabilize': 3}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 360 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 600 | 1 | 0.0% | 0.0% | 0.0% | n/a | 0.750 |
| final | 1 | 0.0% | 0.0% | 100.0% | 0.0% | 1.458 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 0 |
| Timing | 0 | 0 | 0 | 0 | 0 | 0 |
| Power | 0 | 0 | 0 | 1 | 0 | 0 |
| Macro | 0 | 0 | 0 | 0 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.7528193114291688. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `9fd64a1`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Terran / Power | Result.Victory → Result.Victory | 2 → 5 | 9 → 17 | 4 → 7 |
