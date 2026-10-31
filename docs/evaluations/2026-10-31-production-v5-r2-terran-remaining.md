# Match evaluation: production-v5-r2-20261031-terran-remaining

Model: `scouting-v1`. 9 matches; 3 distinct starting-condition groups.

Results: `{'Result.Defeat': 6, 'Result.Victory': 3}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit1500`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Rush | 3 Defeat | 6175 / 18075 | 0.34 | 1650 | 18 | 27 | 2 | 9 |
| Terran / Timing | 3 Defeat | 2575 / 14025 | 0.18 | 2950 | 15 | 20 | 0 | 7 |
| Terran / Macro | 3 Victory | 6150 / 7350 | 0.84 | 7950 | 7 | 45 | 2 | 7 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Rush | 0 | 140.4s / 170.4s | 390-405s | 15.0 | 670.0 |
| Terran / Timing | 0 | 145.4s / 175.4s | 255-270s | 35.0 | 590.0 |
| Terran / Macro | 0 | 145.4s / 175.4s | 330-345s | 5.0 | 755.0 |

## Costly trade windows and match details

### Terran / Rush

Evidence: `runtime-20261031-085410-827250-001.json`. End sample 1120.4s; peak 34 workers / 65 army supply. First offensive advance: 315.4s; first expansion advance: 365.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 12, 'short_target_reversals': 2, 'advance_regroup_transitions': 9, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 816, 'sampled_long_move_reversals': 44}`. Action rejections: `{}`.

Score-based bad-trade windows: 18; windows also showing own controlled-army disappearances: 18. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 4125.

Opponent prediction at last sample: **Unknown**, confidence 0.54. First correct confident classification: 190.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: 5.0s.

- 900–915s: army lost 2100, army killed 100, economy killed 50; objectives `{'pressure': 1, 'recover': 2}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'STALKER': 8, 'ZEALOT': 8}`; minimum estimated local advantage: 0.92883898357222; minimum army health fraction: 0.7945686900958466; last sampled army center: `[51.1448974609375, 109.836181640625]`; observed enemy composition: `{'GHOST': 4, 'MARAUDER': 8, 'MARINE': 16}`.
- 570–585s: army lost 1250, army killed 50, economy killed 50; objectives `{'pressure': 1, 'recover': 2}`, targets `['4297326594', 'home']`.
  Own army disappearances: `{'IMMORTAL': 1, 'ZEALOT': 4, 'SENTRY': 1, 'STALKER': 2}`; minimum estimated local advantage: 2.7187910918491616; minimum army health fraction: 0.9178378378378378; last sampled army center: `None`; observed enemy composition: `{'MARINE': 13, 'MARAUDER': 10, 'SIEGETANK': 1}`.
- 1020–1035s: army lost 1050, army killed 50, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 6}`; minimum estimated local advantage: 0.21247030104963988; minimum army health fraction: 0.8463541666666666; last sampled army center: `None`; observed enemy composition: `{'GHOST': 4, 'MARAUDER': 17, 'MARINE': 16}`.
- Economic losses at 1095–1110s: 1150 resources; own worker/base disappearances `{'PROBE': 14, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 1050–1065s: 1100 resources; own worker/base disappearances `{'PROBE': 13, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 1110–1125s: 700 resources; own worker/base disappearances `{'PROBE': 1, 'ASSIMILATOR': 2}`; objectives `{'recover': 1, 'develop': 2}`.

### Terran / Timing

Evidence: `runtime-20261031-085410-827250-004.json`. End sample 930.4s; peak 56 workers / 65 army supply. First offensive advance: 340.4s; first expansion advance: 560.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 5, 'short_target_reversals': 0, 'advance_regroup_transitions': 7, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 586, 'sampled_long_move_reversals': 48}`. Action rejections: `{}`.

Score-based bad-trade windows: 15; windows also showing own controlled-army disappearances: 15. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 7425.

Opponent prediction at last sample: **Unknown**, confidence 0.42. First correct confident classification: 235.4s; first home contact: 250.4s. Positive classification lead means recognition preceded contact: 15.0s.

- 840–855s: army lost 2200, army killed 500, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 6, 'IMMORTAL': 3, 'ZEALOT': 1}`; minimum estimated local advantage: 0.39252832228723666; minimum army health fraction: 0.7636775362318841; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 12, 'MARINE': 16, 'SIEGETANKSIEGED': 5, 'SIEGETANK': 1, 'VIKINGASSAULT': 3, 'GHOST': 4, 'BANSHEE': 1}`.
- 705–720s: army lost 1825, army killed 225, economy killed 0; objectives `{'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 1, 'IMMORTAL': 3, 'COLOSSUS': 1, 'STALKER': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8116666666666666; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 14, 'MARINE': 12, 'SIEGETANK': 6}`.
- 885–900s: army lost 1750, army killed 200, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 2, 'IMMORTAL': 1, 'SENTRY': 2, 'ZEALOT': 5}`; minimum estimated local advantage: 0.09406115470069865; minimum army health fraction: 0.690625; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 12, 'MARINE': 17, 'SIEGETANKSIEGED': 6, 'VIKINGASSAULT': 3, 'GHOST': 4, 'BANSHEE': 1}`.
- Economic losses at 795–810s: 1925 resources; own worker/base disappearances `{'PROBE': 20, 'NEXUS': 1, 'ASSIMILATOR': 1}`; objectives `{'recover': 1, 'stabilize': 1, 'pressure': 1}`.
- Economic losses at 855–870s: 1050 resources; own worker/base disappearances `{'PROBE': 12, 'NEXUS': 1}`; objectives `{'recover': 3}`.
- Economic losses at 915–930s: 850 resources; own worker/base disappearances `{'ASSIMILATOR': 2, 'NEXUS': 1}`; objectives `{'develop': 3}`.

### Terran / Macro

Evidence: `runtime-20261031-085410-827250-007.json`. End sample 975.4s; peak 56 workers / 143 army supply. First offensive advance: 280.4s; first expansion advance: 325.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 22, 'short_target_reversals': 2, 'advance_regroup_transitions': 7, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1530, 'sampled_long_move_reversals': 83}`. Action rejections: `{'direct:881:41': 1}`.

Score-based bad-trade windows: 7; windows also showing own controlled-army disappearances: 7. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Macro**, confidence 0.65. First correct confident classification: 425.4s; first home contact: 520.4s. Positive classification lead means recognition preceded contact: 95.0s.

- 525–540s: army lost 1525, army killed 50, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 3, 'ZEALOT': 10}`; minimum estimated local advantage: 0.43619217406782246; minimum army health fraction: 0.9100369458128079; last sampled army center: `None`; observed enemy composition: `{'MARINE': 11, 'MARAUDER': 13, 'SIEGETANK': 4}`.
- 645–660s: army lost 2050, army killed 1000, economy killed 50; objectives `{'contain': 1, 'recover': 2}`, targets `['4371513345', 'home']`.
  Own army disappearances: `{'ZEALOT': 8, 'STALKER': 4, 'SENTRY': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 1.8835007913129802; minimum army health fraction: 0.7943890274314215; last sampled army center: `[65.8695068359375, 118.0089111328125]`; observed enemy composition: `{'MARINE': 9, 'MARAUDER': 10, 'SIEGETANKSIEGED': 4}`.
- 510–525s: army lost 1050, army killed 525, economy killed 850; objectives `{'pressure': 2, 'recover': 1}`, targets `['4383571969', 'home']`.
  Own army disappearances: `{'STALKER': 3, 'ZEALOT': 4, 'SENTRY': 2}`; minimum estimated local advantage: 1.133840092279172; minimum army health fraction: 0.8685294117647059; last sampled army center: `None`; observed enemy composition: `{'MARINE': 14, 'MARAUDER': 12, 'SIEGETANKSIEGED': 2, 'SIEGETANK': 1}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 3 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 180 | 3 | 0.0% | 0.0% | 0.0% | n/a | 0.800 |
| 240 | 3 | 66.7% | 66.7% | 66.7% | 100.0% | 0.344 |
| 360 | 3 | 66.7% | 66.7% | 66.7% | 100.0% | 0.344 |
| 600 | 3 | 0.0% | 0.0% | 0.0% | n/a | 0.457 |
| final | 3 | 33.3% | 33.3% | 33.3% | 100.0% | 0.334 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 1 |
| Timing | 0 | 0 | 0 | 0 | 0 | 1 |
| Power | 0 | 0 | 0 | 0 | 0 | 0 |
| Macro | 0 | 0 | 0 | 1 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 0 |

Expected calibration error: 0.46528664282916715. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `9fd64a1`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Terran / Rush | Result.Defeat → Result.Defeat | 0 → 2 | 0 → 9 | 7 → 18 |
| Terran / Timing | Result.Defeat → Result.Defeat | 0 → 0 | 8 → 7 | 10 → 15 |
| Terran / Macro | Result.Defeat → Result.Victory | 1 → 2 | 7 → 7 | 10 → 7 |
