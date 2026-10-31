# Match evaluation: robotics-fund-v2-20261031

Model: `scouting-v1`. 30 matches; 10 distinct starting-condition groups.

Results: `{'Result.Victory': 18, 'Result.Defeat': 12}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600`. Configuration identities: `0e35653e2b33a8dc7c0a383d734789f906a0d9058cdc228d11e8ab12403c00e0`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Zerg / Timing | 3 Victory | 8975 / 5250 | 1.71 | 6750 | 3 | 45 | 2 | 15 |
| Terran / Rush | 3 Defeat | 6175 / 18075 | 0.34 | 1650 | 18 | 27 | 2 | 9 |
| Terran / Timing | 3 Defeat | 2575 / 14025 | 0.18 | 2950 | 15 | 20 | 0 | 7 |
| Terran / Power | 3 Victory | 4600 / 5050 | 0.91 | 7000 | 3 | 34 | 0 | 5 |
| Terran / Macro | 3 Victory | 6150 / 7350 | 0.84 | 7950 | 7 | 45 | 2 | 7 |
| Terran / Air | 3 Victory | 5175 / 1100 | 4.71 | 6350 | 1 | 15 | 1 | 10 |
| Zerg / Rush | 3 Victory | 10375 / 5775 | 1.80 | 5025 | 2 | 44 | 1 | 7 |
| Zerg / Power | 3 Defeat | 18300 / 27825 | 0.66 | 7550 | 14 | 67 | 1 | 15 |
| Zerg / Macro | 3 Defeat | 6925 / 10925 | 0.63 | 0 | 9 | 6 | 0 | 6 |
| Zerg / Air | 3 Victory | 14725 / 8550 | 1.72 | 8050 | 4 | 57 | 0 | 14 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Zerg / Timing | 0 | 110.4s / 165.4s | 435-450s | 5.0 | 800.0 |
| Terran / Rush | 0 | 140.4s / 170.4s | 390-405s | 15.0 | 670.0 |
| Terran / Timing | 0 | 145.4s / 175.4s | 255-270s | 35.0 | 590.0 |
| Terran / Power | 0 | 140.4s / 175.4s | 315-330s | 5.0 | 750.0 |
| Terran / Macro | 0 | 145.4s / 175.4s | 330-345s | 5.0 | 755.0 |
| Terran / Air | 0 | 140.4s / 170.4s | 375-390s | 10.0 | 750.0 |
| Zerg / Rush | 0 | 110.4s / 170.4s | 555-570s | 15.0 | 785.0 |
| Zerg / Power | 0 | 110.4s / 165.4s | 330-345s | 5.0 | 1675.0 |
| Zerg / Macro | 0 | 110.4s / 170.4s | 525-540s | 5.0 | 605.0 |
| Zerg / Air | 0 | 110.4s / 160.4s | 480-495s | 5.0 | 915.0 |

## Costly trade windows and match details

### Zerg / Timing

Evidence: `runtime-20261031-094645-071742-8c2889ccf2a1467fb3ed2418206fe1ff-001.json`. End sample 1050.4s; peak 34 workers / 111 army supply. First offensive advance: 335.4s; first expansion advance: 335.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 16, 'short_target_reversals': 2, 'advance_regroup_transitions': 15, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1822, 'sampled_long_move_reversals': 142}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 400.

Opponent prediction at last sample: **Unknown**, confidence 0.50. First correct confident classification: 620.4s; first home contact: 195.4s. Positive classification lead means recognition preceded contact: -425.0s.

- 495–510s: army lost 450, army killed 100, economy killed 0; objectives `{'recover': 2, 'pressure': 1}`, targets `['4356833284', 'home']`.
  Own army disappearances: `{'ZEALOT': 3, 'SENTRY': 1}`; minimum estimated local advantage: 1.2494735289154402; minimum army health fraction: 0.9313351498637602; last sampled army center: `None`; observed enemy composition: `{'ROACH': 13, 'RAVAGER': 2, 'HYDRALISK': 6, 'ZERGLING': 14, 'CHANGELINGZEALOT': 1}`.
- 435–450s: army lost 400, army killed 75, economy killed 0; objectives `{'recover': 2}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.8746223902046449; minimum army health fraction: 0.9714285714285714; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 5, 'ROACH': 13, 'RAVAGER': 1, 'HYDRALISK': 5, 'CHANGELINGZEALOT': 1}`.
- 810–825s: army lost 300, army killed 150, economy killed 0; objectives `{'pressure': 3}`, targets `['4334813185']`.
  Own army disappearances: `{'ZEALOT': 3}`; minimum estimated local advantage: 4.615090555916168; minimum army health fraction: 0.8628694322374132; last sampled army center: `[40.909423828125, 134.8865966796875]`; observed enemy composition: `{'MUTALISK': 4, 'ZERGLING': 13, 'ROACH': 5, 'BROODLING': 17, 'HYDRALISK': 2, 'QUEEN': 1, 'CHANGELINGZEALOT': 1}`.
- Economic losses at 270–285s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 2}`.

### Terran / Rush

Evidence: `runtime-20261031-094920-980166-abf9b19e0fbf4647b0e11ec68ae9ad87-001.json`. End sample 1120.4s; peak 34 workers / 65 army supply. First offensive advance: 315.4s; first expansion advance: 365.4s; inspected sites: 8.

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

Evidence: `runtime-20261031-094920-980166-abf9b19e0fbf4647b0e11ec68ae9ad87-004.json`. End sample 930.4s; peak 56 workers / 65 army supply. First offensive advance: 340.4s; first expansion advance: 560.4s; inspected sites: 8.

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

### Terran / Power

Evidence: `runtime-20261031-094920-980166-abf9b19e0fbf4647b0e11ec68ae9ad87-007.json`. End sample 905.4s; peak 56 workers / 135 army supply. First offensive advance: 275.4s; first expansion advance: 395.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 16, 'short_target_reversals': 0, 'advance_regroup_transitions': 5, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1365, 'sampled_long_move_reversals': 48}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: not observed; first home contact: 560.4s. Positive classification lead means recognition preceded contact: not observed.

- 495–510s: army lost 2075, army killed 100, economy killed 450; objectives `{'pressure': 1, 'recover': 2}`, targets `['4381999105', 'home']`.
  Own army disappearances: `{'STALKER': 3, 'IMMORTAL': 2, 'SENTRY': 1, 'ZEALOT': 7}`; minimum estimated local advantage: 0.6554561752339996; minimum army health fraction: 0.8625; last sampled army center: `None`; observed enemy composition: `{'MARINE': 13, 'MARAUDER': 13, 'SIEGETANK': 4}`.
- 405–420s: army lost 500, army killed 100, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 5}`; minimum estimated local advantage: 0.8575169547477179; minimum army health fraction: 0.9416243654822335; last sampled army center: `None`; observed enemy composition: `{'MARINE': 12, 'MARAUDER': 8, 'SIEGETANK': 1}`.
- 315–330s: army lost 375, army killed 100, economy killed 0; objectives `{'pressure': 1, 'recover': 2}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 2, 'STALKER': 1}`; minimum estimated local advantage: 1.0302721567278292; minimum army health fraction: 0.8978102189781022; last sampled army center: `[56.707275390625, 126.546875]`; observed enemy composition: `{'MARINE': 13, 'MARAUDER': 2, 'SIEGETANKSIEGED': 1}`.

### Terran / Macro

Evidence: `runtime-20261031-094920-980166-abf9b19e0fbf4647b0e11ec68ae9ad87-010.json`. End sample 975.4s; peak 56 workers / 143 army supply. First offensive advance: 280.4s; first expansion advance: 325.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 22, 'short_target_reversals': 2, 'advance_regroup_transitions': 7, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1530, 'sampled_long_move_reversals': 83}`. Action rejections: `{'direct:881:41': 1}`.

Score-based bad-trade windows: 7; windows also showing own controlled-army disappearances: 7. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Macro**, confidence 0.65. First correct confident classification: 425.4s; first home contact: 520.4s. Positive classification lead means recognition preceded contact: 95.0s.

- 525–540s: army lost 1525, army killed 50, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 3, 'ZEALOT': 10}`; minimum estimated local advantage: 0.43619217406782246; minimum army health fraction: 0.9100369458128079; last sampled army center: `None`; observed enemy composition: `{'MARINE': 11, 'MARAUDER': 13, 'SIEGETANK': 4}`.
- 645–660s: army lost 2050, army killed 1000, economy killed 50; objectives `{'contain': 1, 'recover': 2}`, targets `['4371513345', 'home']`.
  Own army disappearances: `{'ZEALOT': 8, 'STALKER': 4, 'SENTRY': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 1.8835007913129802; minimum army health fraction: 0.7943890274314215; last sampled army center: `[65.8695068359375, 118.0089111328125]`; observed enemy composition: `{'MARINE': 9, 'MARAUDER': 10, 'SIEGETANKSIEGED': 4}`.
- 510–525s: army lost 1050, army killed 525, economy killed 850; objectives `{'pressure': 2, 'recover': 1}`, targets `['4383571969', 'home']`.
  Own army disappearances: `{'STALKER': 3, 'ZEALOT': 4, 'SENTRY': 2}`; minimum estimated local advantage: 1.133840092279172; minimum army health fraction: 0.8685294117647059; last sampled army center: `None`; observed enemy composition: `{'MARINE': 14, 'MARAUDER': 12, 'SIEGETANKSIEGED': 2, 'SIEGETANK': 1}`.

### Terran / Air

Evidence: `runtime-20261031-094920-980166-abf9b19e0fbf4647b0e11ec68ae9ad87-013.json`. End sample 720.4s; peak 56 workers / 115 army supply. First offensive advance: 275.4s; first expansion advance: 315.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 13, 'short_target_reversals': 1, 'advance_regroup_transitions': 10, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1097, 'sampled_long_move_reversals': 60}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: 355.4s; first home contact: not observed. Positive classification lead means recognition preceded contact: not observed.

- 375–390s: army lost 400, army killed 0, economy killed 0; objectives `{'contain': 1, 'recover': 1}`, targets `['4334813185', 'home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 2.215573833317405; minimum army health fraction: 0.566453488372093; last sampled army center: `[50.66943359375, 121.852294921875]`; observed enemy composition: `{'VIKINGASSAULT': 4, 'MARINE': 5, 'BATTLECRUISER': 1}`.

### Zerg / Rush

Evidence: `runtime-20261031-100009-792561-8b7ef61b2af1415fb22465b3c08fb9d1-001.json`. End sample 965.4s; peak 55 workers / 127 army supply. First offensive advance: 270.4s; first expansion advance: 275.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 12, 'short_target_reversals': 1, 'advance_regroup_transitions': 7, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1624, 'sampled_long_move_reversals': 118}`. Action rejections: `{'direct:3674:2': 9}`.

Score-based bad-trade windows: 2; windows also showing own controlled-army disappearances: 2. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 1675.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: not observed; first home contact: 125.4s. Positive classification lead means recognition preceded contact: not observed.

- 555–570s: army lost 400, army killed 75, economy killed 325; objectives `{'pressure': 2, 'recover': 1}`, targets `['4345823234', 'home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 1.2404180380101344; minimum army health fraction: 0.8878048780487805; last sampled army center: `[46.2822265625, 109.4940185546875]`; observed enemy composition: `{'RAVAGER': 2, 'HYDRALISK': 7, 'ZERGLING': 11, 'ROACH': 9}`.
- 720–735s: army lost 300, army killed 25, economy killed 625; objectives `{'pressure': 2, 'recover': 1}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 3}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8622822299651568; last sampled army center: `[34.245361328125, 92.615478515625]`; observed enemy composition: `{'RAVAGER': 1, 'HYDRALISK': 4, 'ROACH': 13, 'ZERGLING': 15, 'MUTALISK': 5, 'CHANGELINGZEALOT': 1, 'BROODLING': 6, 'LOCUSTMP': 3}`.
- Economic losses at 630–645s: 950 resources; own worker/base disappearances `{'PROBE': 10, 'NEXUS': 1}`; objectives `{'pressure': 2, 'stabilize': 1}`.
- Economic losses at 645–660s: 725 resources; own worker/base disappearances `{'PROBE': 7, 'ASSIMILATOR': 1}`; objectives `{'pressure': 2, 'stabilize': 1}`.

### Zerg / Power

Evidence: `runtime-20261031-100009-792561-8b7ef61b2af1415fb22465b3c08fb9d1-004.json`. End sample 1620.4s; peak 56 workers / 143 army supply. First offensive advance: 255.4s; first expansion advance: 405.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 24, 'short_target_reversals': 1, 'advance_regroup_transitions': 15, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 2418, 'sampled_long_move_reversals': 207}`. Action rejections: `{}`.

Score-based bad-trade windows: 14; windows also showing own controlled-army disappearances: 14. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 6350.

Opponent prediction at last sample: **Power**, confidence 0.65. First correct confident classification: 330.4s; first home contact: 220.4s. Positive classification lead means recognition preceded contact: -110.0s.

- 1020–1035s: army lost 5925, army killed 2875, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 12, 'IMMORTAL': 4, 'STALKER': 19}`; minimum estimated local advantage: 0.2616289693702599; minimum army health fraction: 0.8158633667883212; last sampled army center: `None`; observed enemy composition: `{'ROACH': 10, 'ULTRALISK': 3, 'RAVAGER': 2, 'ZERGLING': 5, 'HYDRALISK': 12, 'LURKERMPBURROWED': 2, 'BROODLING': 8, 'CHANGELINGZEALOT': 4}`.
- 765–780s: army lost 3800, army killed 1200, economy killed 50; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 6, 'IMMORTAL': 5, 'COLOSSUS': 2}`; minimum estimated local advantage: 0.4935341439371004; minimum army health fraction: 0.7980736301369863; last sampled army center: `None`; observed enemy composition: `{'QUEEN': 2, 'ZERGLING': 15, 'ROACH': 15, 'RAVAGER': 2, 'HYDRALISK': 7, 'LURKERMPBURROWED': 2, 'BROODLING': 5, 'CHANGELINGZEALOT': 1, 'COLOSSUS': 1, 'IMMORTAL': 1}`.
- 1035–1050s: army lost 1850, army killed 550, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 6, 'IMMORTAL': 2, 'ZEALOT': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8767282958199357; last sampled army center: `None`; observed enemy composition: `{'ROACH': 10, 'ULTRALISK': 3, 'RAVAGER': 2, 'ZERGLING': 13, 'HYDRALISK': 12, 'LURKERMPBURROWED': 2, 'BROODLING': 8, 'CHANGELINGZEALOT': 4, 'QUEEN': 1}`.
- Economic losses at 1275–1290s: 1700 resources; own worker/base disappearances `{'PROBE': 22, 'NEXUS': 1}`; objectives `{'stabilize': 3}`.
- Economic losses at 1560–1575s: 1425 resources; own worker/base disappearances `{'ASSIMILATOR': 1, 'PROBE': 23}`; objectives `{'stabilize': 2}`.
- Economic losses at 1530–1545s: 850 resources; own worker/base disappearances `{'PROBE': 5, 'NEXUS': 1}`; objectives `{'recover': 2}`.

### Zerg / Macro

Evidence: `runtime-20261031-100009-792561-8b7ef61b2af1415fb22465b3c08fb9d1-007.json`. End sample 840.4s; peak 56 workers / 69 army supply. First offensive advance: 255.4s; first expansion advance: 310.4s; inspected sites: 7.

Movement: `{'offensive_target_switches': 6, 'short_target_reversals': 0, 'advance_regroup_transitions': 6, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 450, 'sampled_long_move_reversals': 59}`. Action rejections: `{'881:208': 1}`.

Score-based bad-trade windows: 9; windows also showing own controlled-army disappearances: 9. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 5825.

Opponent prediction at last sample: **Unknown**, confidence 0.20. First correct confident classification: not observed; first home contact: 315.4s. Positive classification lead means recognition preceded contact: not observed.

- 660–675s: army lost 1575, army killed 450, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'SENTRY': 1, 'IMMORTAL': 2, 'STALKER': 3, 'ZEALOT': 2}`; minimum estimated local advantage: 0.5739951739636295; minimum army health fraction: 0.8737288135593221; last sampled army center: `None`; observed enemy composition: `{'ROACH': 10, 'HYDRALISK': 10, 'RAVAGER': 1, 'ZERGLING': 26, 'QUEEN': 2}`.
- 525–540s: army lost 1000, army killed 0, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 10}`; minimum estimated local advantage: 0.7268404261523834; minimum army health fraction: 0.8436208010335917; last sampled army center: `None`; observed enemy composition: `{'ROACH': 18, 'HYDRALISK': 7, 'ZERGLING': 4, 'RAVAGER': 3, 'CHANGELINGZEALOT': 1}`.
- 735–750s: army lost 950, army killed 150, economy killed 0; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'COLOSSUS': 1, 'IMMORTAL': 1, 'ZEALOT': 1}`; minimum estimated local advantage: 0.40415502269149395; minimum army health fraction: 0.43157894736842106; last sampled army center: `None`; observed enemy composition: `{'ROACH': 14, 'HYDRALISK': 9, 'RAVAGER': 2, 'QUEEN': 2, 'ZERGLING': 32}`.
- Economic losses at 615–630s: 800 resources; own worker/base disappearances `{'PROBE': 8, 'NEXUS': 1}`; objectives `{'stabilize': 3}`.
- Economic losses at 795–810s: 800 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'develop': 3}`.
- Economic losses at 660–675s: 600 resources; own worker/base disappearances `{'PROBE': 13}`; objectives `{'recover': 3}`.

### Zerg / Air

Evidence: `runtime-20261031-100009-792561-8b7ef61b2af1415fb22465b3c08fb9d1-010.json`. End sample 1025.4s; peak 56 workers / 139 army supply. First offensive advance: 285.4s; first expansion advance: 330.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 15, 'short_target_reversals': 0, 'advance_regroup_transitions': 14, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1839, 'sampled_long_move_reversals': 92}`. Action rejections: `{}`.

Score-based bad-trade windows: 4; windows also showing own controlled-army disappearances: 4. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: not observed; first home contact: 355.4s. Positive classification lead means recognition preceded contact: not observed.

- 735–750s: army lost 1375, army killed 450, economy killed 50; objectives `{'recover': 3}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 5, 'SENTRY': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 10.0; minimum army health fraction: 0.8857792207792208; last sampled army center: `None`; observed enemy composition: `{'ZERGLING': 24, 'HYDRALISK': 6, 'RAVAGER': 2, 'ROACH': 6, 'IMMORTAL': 2}`.
- 480–495s: army lost 900, army killed 250, economy killed 325; objectives `{'pressure': 1, 'recover': 2}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 9}`; minimum estimated local advantage: 0.6621774260340725; minimum army health fraction: 0.8384330985915492; last sampled army center: `[30.27392578125, 93.139404296875]`; observed enemy composition: `{'MUTALISK': 2, 'ZERGLING': 5, 'RAVAGER': 2, 'ROACH': 11, 'HYDRALISK': 5, 'BROODLING': 5, 'CHANGELINGZEALOT': 1}`.
- 555–570s: army lost 550, army killed 225, economy killed 0; objectives `{'recover': 2, 'stabilize': 1}`, targets `['home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 2, 'STALKER': 2}`; minimum estimated local advantage: 0.38263814766925286; minimum army health fraction: 0.8378686797752809; last sampled army center: `None`; observed enemy composition: `{'MUTALISK': 2, 'ZERGLING': 16, 'RAVAGER': 2, 'ROACH': 12, 'HYDRALISK': 6, 'BROODLING': 5, 'CHANGELINGZEALOT': 2}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 10 | 0.0% | 0.0% | 0.0% | n/a | 0.815 |
| 180 | 10 | 0.0% | 0.0% | 0.0% | n/a | 0.815 |
| 240 | 10 | 20.0% | 20.0% | 20.0% | 100.0% | 0.679 |
| 360 | 10 | 40.0% | 40.0% | 40.0% | 100.0% | 0.497 |
| 600 | 10 | 10.0% | 10.0% | 30.0% | 33.3% | 0.663 |
| final | 10 | 20.0% | 20.0% | 30.0% | 66.7% | 0.558 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 2 |
| Timing | 0 | 0 | 0 | 0 | 0 | 2 |
| Power | 0 | 0 | 1 | 1 | 0 | 0 |
| Macro | 0 | 0 | 0 | 1 | 0 | 1 |
| Air | 0 | 0 | 0 | 0 | 0 | 2 |

Expected calibration error: 0.2582809358728917. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
