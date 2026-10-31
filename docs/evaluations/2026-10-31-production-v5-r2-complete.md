# Match evaluation: production-v5-r2-20261031

Model: `scouting-v1`. 30 matches; 10 distinct starting-condition groups.

Results: `{'Result.Victory': 21, 'Result.Defeat': 9}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit1500`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Air | 3 Victory | 5175 / 1100 | 4.71 | 6350 | 1 | 15 | 1 | 10 |
| Terran / Macro | 3 Victory | 6150 / 7350 | 0.84 | 7950 | 7 | 45 | 2 | 7 |
| Terran / Power | 3 Victory | 4600 / 5050 | 0.91 | 7000 | 3 | 34 | 0 | 5 |
| Terran / Rush | 3 Defeat | 6175 / 18075 | 0.34 | 1650 | 18 | 27 | 2 | 9 |
| Terran / Timing | 3 Defeat | 2575 / 14025 | 0.18 | 2950 | 15 | 20 | 0 | 7 |
| Zerg / Air | 3 Victory | 2200 / 500 | 4.40 | 2000 | 0 | 6 | 0 | 1 |
| Zerg / Macro | 3 Victory | 13350 / 8500 | 1.57 | 10475 | 4 | 63 | 2 | 15 |
| Zerg / Power | 3 Victory | 17250 / 7425 | 2.32 | 9000 | 4 | 50 | 3 | 9 |
| Zerg / Rush | 3 Victory | 5525 / 1375 | 4.02 | 3675 | 1 | 24 | 1 | 6 |
| Zerg / Timing | 3 Defeat | 9500 / 13850 | 0.69 | 1200 | 15 | 31 | 0 | 5 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Air | 0 | 140.4s / 170.4s | 375-390s | 10.0 | 750.0 |
| Terran / Macro | 0 | 145.4s / 175.4s | 330-345s | 5.0 | 755.0 |
| Terran / Power | 0 | 140.4s / 175.4s | 315-330s | 5.0 | 750.0 |
| Terran / Rush | 0 | 140.4s / 170.4s | 390-405s | 15.0 | 670.0 |
| Terran / Timing | 0 | 145.4s / 175.4s | 255-270s | 35.0 | 590.0 |
| Zerg / Air | 0 | 110.4s / 160.4s | not recorded | 5.0 | 90.0 |
| Zerg / Macro | 0 | 110.4s / 170.4s | 315-330s | 5.0 | 660.0 |
| Zerg / Power | 0 | 110.4s / 165.4s | 330-345s | 25.0 | 890.0 |
| Zerg / Rush | 0 | 110.4s / 170.4s | 450-465s | 5.0 | 390.0 |
| Zerg / Timing | 0 | 110.4s / 165.4s | 270-285s | 35.0 | 495.0 |

## Costly trade windows and match details

### Terran / Air

Evidence: `runtime-20261031-085126-150544-001.json`. End sample 720.4s; peak 56 workers / 115 army supply. First offensive advance: 275.4s; first expansion advance: 315.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 13, 'short_target_reversals': 1, 'advance_regroup_transitions': 10, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1097, 'sampled_long_move_reversals': 60}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: 355.4s; first home contact: not observed. Positive classification lead means recognition preceded contact: not observed.

- 375–390s: army lost 400, army killed 0, economy killed 0; objectives `{'contain': 1, 'recover': 1}`, targets `['4334813185', 'home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 2.215573833317405; minimum army health fraction: 0.566453488372093; last sampled army center: `[50.66943359375, 121.852294921875]`; observed enemy composition: `{'VIKINGASSAULT': 4, 'MARINE': 5, 'BATTLECRUISER': 1}`.

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

### Terran / Power

Evidence: `runtime-20261031-084756-867116-001.json`. End sample 905.4s; peak 56 workers / 135 army supply. First offensive advance: 275.4s; first expansion advance: 395.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 16, 'short_target_reversals': 0, 'advance_regroup_transitions': 5, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1365, 'sampled_long_move_reversals': 48}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: not observed; first home contact: 560.4s. Positive classification lead means recognition preceded contact: not observed.

- 495–510s: army lost 2075, army killed 100, economy killed 450; objectives `{'pressure': 1, 'recover': 2}`, targets `['4381999105', 'home']`.
  Own army disappearances: `{'STALKER': 3, 'IMMORTAL': 2, 'SENTRY': 1, 'ZEALOT': 7}`; minimum estimated local advantage: 0.6554561752339996; minimum army health fraction: 0.8625; last sampled army center: `None`; observed enemy composition: `{'MARINE': 13, 'MARAUDER': 13, 'SIEGETANK': 4}`.
- 405–420s: army lost 500, army killed 100, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 5}`; minimum estimated local advantage: 0.8575169547477179; minimum army health fraction: 0.9416243654822335; last sampled army center: `None`; observed enemy composition: `{'MARINE': 12, 'MARAUDER': 8, 'SIEGETANK': 1}`.
- 315–330s: army lost 375, army killed 100, economy killed 0; objectives `{'pressure': 1, 'recover': 2}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 2, 'STALKER': 1}`; minimum estimated local advantage: 1.0302721567278292; minimum army health fraction: 0.8978102189781022; last sampled army center: `[56.707275390625, 126.546875]`; observed enemy composition: `{'MARINE': 13, 'MARAUDER': 2, 'SIEGETANKSIEGED': 1}`.

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

### Zerg / Air

Evidence: `runtime-20261031-085138-596780-001.json`. End sample 480.4s; peak 44 workers / 59 army supply. First offensive advance: 255.4s; first expansion advance: 300.4s; inspected sites: 3.

Movement: `{'offensive_target_switches': 3, 'short_target_reversals': 0, 'advance_regroup_transitions': 1, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 301, 'sampled_long_move_reversals': 9}`. Action rejections: `{}`.

Score-based bad-trade windows: 0; windows also showing own controlled-army disappearances: 0. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: not observed; first home contact: not observed. Positive classification lead means recognition preceded contact: not observed.

No sampled 15-second window met the bad-trade threshold (loss ≥300 and >1.5× enemy army value killed).

### Zerg / Macro

Evidence: `runtime-20261031-084305-882772-001.json`. End sample 1055.4s; peak 56 workers / 143 army supply. First offensive advance: 245.4s; first expansion advance: 300.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 17, 'short_target_reversals': 2, 'advance_regroup_transitions': 15, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2175, 'sampled_long_move_reversals': 257}`. Action rejections: `{'direct:3674:2': 8}`.

Score-based bad-trade windows: 4; windows also showing own controlled-army disappearances: 4. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 100.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 315.4s. Positive classification lead means recognition preceded contact: not observed.

- 570–585s: army lost 1200, army killed 50, economy killed 50; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 9, 'SENTRY': 2}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8300495426829269; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 12, 'RAVAGER': 2, 'ROACH': 15, 'HYDRALISK': 8, 'CHANGELINGZEALOT': 2}`.
- 435–450s: army lost 650, army killed 225, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 3, 'STALKER': 2}`; minimum estimated local advantage: 0.7879849218507476; minimum army health fraction: 0.9013157894736842; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 9, 'ROACH': 8, 'HYDRALISK': 4}`.
- 315–330s: army lost 500, army killed 150, economy killed 300; objectives `{'pressure': 1, 'counterattack': 1, 'recover': 1}`, targets `['4341891073', 'home']`.
  Own army disappearances: `{'ZEALOT': 5}`; minimum estimated local advantage: 2.095348564014464; minimum army health fraction: 0.6959016393442623; last sampled army center: `[64.3994140625, 129.472900390625]`; observed enemy composition: `{'QUEEN': 1, 'ZERGLING': 7, 'ROACH': 6}`.

### Zerg / Power

Evidence: `runtime-20261031-085423-792713-004.json`. End sample 1070.4s; peak 56 workers / 133 army supply. First offensive advance: 255.4s; first expansion advance: 315.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 23, 'short_target_reversals': 3, 'advance_regroup_transitions': 9, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1864, 'sampled_long_move_reversals': 191}`. Action rejections: `{}`.

Score-based bad-trade windows: 4; windows also showing own controlled-army disappearances: 4. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 1575.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: 315.4s; first home contact: 220.4s. Positive classification lead means recognition preceded contact: -95.0s.

- 330–345s: army lost 650, army killed 75, economy killed 50; objectives `{'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 5, 'SENTRY': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.7782142857142857; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 8, 'QUEEN': 1, 'ROACH': 9}`.
- 510–525s: army lost 400, army killed 0, economy killed 325; objectives `{'recover': 2, 'pressure': 1}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 1.2131088549316245; minimum army health fraction: 0.9885245901639345; last sampled army center: `None`; observed enemy composition: `{'RAVAGER': 2, 'ROACH': 8, 'HYDRALISK': 8, 'ZERGLING': 2, 'CHANGELINGZEALOT': 1}`.
- 495–510s: army lost 400, army killed 75, economy killed 175; objectives `{'pressure': 3}`, targets `['4373086209']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.914363777091332; minimum army health fraction: 0.9040296052631579; last sampled army center: `[31.2554931640625, 93.7423095703125]`; observed enemy composition: `{'RAVAGER': 2, 'ROACH': 8, 'HYDRALISK': 8, 'ZERGLING': 2, 'CHANGELINGZEALOT': 1}`.
- Economic losses at 615–630s: 1075 resources; own worker/base disappearances `{'PROBE': 10, 'NEXUS': 1, 'ASSIMILATOR': 1}`; objectives `{'pressure': 2, 'stabilize': 1}`.
- Economic losses at 600–615s: 450 resources; own worker/base disappearances `{'PROBE': 5}`; objectives `{'stabilize': 2}`.

### Zerg / Rush

Evidence: `runtime-20261031-084744-659435-001.json`. End sample 685.4s; peak 55 workers / 113 army supply. First offensive advance: 245.4s; first expansion advance: 300.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 9, 'short_target_reversals': 1, 'advance_regroup_transitions': 6, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 755, 'sampled_long_move_reversals': 41}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 125.4s. Positive classification lead means recognition preceded contact: not observed.

- 450–465s: army lost 300, army killed 125, economy killed 0; objectives `{'pressure': 2}`, targets `['4345823234']`.
  Own army disappearances: `{'ZEALOT': 3}`; minimum estimated local advantage: 3.0177343559052248; minimum army health fraction: 0.8630890052356021; last sampled army center: `[75.2337646484375, 125.3350830078125]`; observed enemy composition: `{'ROACH': 4, 'HYDRALISK': 4, 'ZERGLING': 1}`.

### Zerg / Timing

Evidence: `runtime-20261031-085423-792713-001.json`. End sample 1220.4s; peak 56 workers / 85 army supply. First offensive advance: 340.4s; first expansion advance: 455.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 17, 'short_target_reversals': 0, 'advance_regroup_transitions': 5, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1088, 'sampled_long_move_reversals': 105}`. Action rejections: `{'direct:881:41': 1, 'direct:3674:3': 2}`.

Score-based bad-trade windows: 15; windows also showing own controlled-army disappearances: 15. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 7275.

Opponent prediction at last sample: **Unknown**, confidence 0.52. First correct confident classification: 260.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: -65.0s.

- 1110–1125s: army lost 1325, army killed 250, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 5, 'ZEALOT': 2}`; minimum estimated local advantage: 0.008491613016115972; minimum army health fraction: 0.325; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 12, 'ROACH': 9, 'BROODLORD': 10, 'QUEEN': 4, 'HYDRALISK': 6, 'RAVAGER': 2, 'CORRUPTOR': 2, 'BROODLING': 30, 'IMMORTAL': 1}`.
- 555–570s: army lost 975, army killed 100, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 5, 'ZEALOT': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8227661596958175; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 7, 'RAVAGER': 2, 'HYDRALISK': 6, 'ROACH': 8, 'QUEEN': 2}`.
- 270–285s: army lost 550, army killed 0, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 4, 'SENTRY': 1}`; minimum estimated local advantage: 0.6823800667084142; minimum army health fraction: 0.49623983739837396; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 2, 'ROACH': 8}`.
- Economic losses at 1185–1200s: 975 resources; own worker/base disappearances `{'PROBE': 6, 'ASSIMILATOR': 1}`; objectives `{'develop': 3}`.
- Economic losses at 750–765s: 750 resources; own worker/base disappearances `{'NEXUS': 1, 'PROBE': 7}`; objectives `{'recover': 3}`.
- Economic losses at 705–720s: 700 resources; own worker/base disappearances `{'PROBE': 4, 'NEXUS': 1}`; objectives `{'recover': 1, 'stabilize': 2}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 10 | 0.0% | 0.0% | 0.0% | n/a | 0.815 |
| 180 | 10 | 0.0% | 0.0% | 0.0% | n/a | 0.815 |
| 240 | 10 | 20.0% | 20.0% | 20.0% | 100.0% | 0.679 |
| 360 | 10 | 40.0% | 40.0% | 40.0% | 100.0% | 0.497 |
| 600 | 9 | 0.0% | 0.0% | 11.1% | 0.0% | 0.661 |
| final | 10 | 10.0% | 10.0% | 30.0% | 33.3% | 0.737 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 2 |
| Timing | 0 | 0 | 0 | 0 | 0 | 2 |
| Power | 0 | 0 | 0 | 2 | 0 | 0 |
| Macro | 0 | 0 | 0 | 1 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 2 |

Expected calibration error: 0.34692560965365427. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.

## Matched comparison

Baseline `9fd64a1`. Only matching starting fingerprints are included. Counts are sampled trajectory indicators; changed match length and battles also change these counts.

| Scenario | Previous → current result | Target reversals | Advance/regroup transitions | Bad trade windows |
| --- | --- | ---: | ---: | ---: |
| Terran / Air | Result.Victory → Result.Victory | 1 → 1 | 35 → 10 | 2 → 1 |
| Terran / Macro | Result.Defeat → Result.Victory | 1 → 2 | 7 → 7 | 10 → 7 |
| Terran / Power | Result.Victory → Result.Victory | 2 → 0 | 9 → 5 | 4 → 3 |
| Terran / Rush | Result.Defeat → Result.Defeat | 0 → 2 | 0 → 9 | 7 → 18 |
| Terran / Timing | Result.Defeat → Result.Defeat | 0 → 0 | 8 → 7 | 10 → 15 |
| Zerg / Air | Result.Victory → Result.Victory | 3 → 0 | 4 → 1 | 0 → 0 |
| Zerg / Macro | Result.Defeat → Result.Victory | 0 → 2 | 2 → 15 | 8 → 4 |
| Zerg / Power | Result.Defeat → Result.Victory | 0 → 3 | 0 → 9 | 9 → 4 |
| Zerg / Rush | Result.Defeat → Result.Victory | 0 → 1 | 0 → 6 | 0 → 1 |
| Zerg / Timing | Result.Tie → Result.Defeat | 2 → 0 | 15 → 5 | 1 → 15 |
