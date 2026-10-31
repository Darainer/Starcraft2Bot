# Match evaluation: portfolio-final-d0f8cf3-main

Model: `scouting-v1`. 30 matches; 10 distinct starting-condition groups.

Results: `{'Result.Defeat': 12, 'Result.Victory': 18}`. `Result.Tie` means the configured time limit in this suite.

Comparison group: `pressure-veryhard-belshir-20261025-step8-limit3600-snapshot1-revisit1-portfolioauto`. Configuration identities: `f8a34a9d80abcf1508b0fc91fd2a7ebfaf6282623c99ef166d7926bac5106036`.

## Matchups and observed trade evidence

Resource values below are cumulative score high-water estimates (minerals + gas). Economic damage uses the API economy category; it is not a verified worker/base kill count. Sampling and retail score corrections limit fight attribution. Expansion target samples demonstrate committed movement, not economic damage by themselves.

| Race / build | Results | Army killed / lost | Ratio | Economy killed | Bad 15s windows | Expansion samples | Target reversals | Advance/regroup changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Terran / Rush | 3 Defeat | 9000 / 18375 | 0.49 | 2525 | 17 | 166 | 3 | 19 |
| Terran / Timing | 3 Defeat | 6950 / 16725 | 0.42 | 4200 | 18 | 156 | 1 | 36 |
| Terran / Power | 3 Defeat | 1200 / 9750 | 0.12 | 450 | 11 | 19 | 0 | 16 |
| Terran / Macro | 3 Victory | 12650 / 7100 | 1.78 | 8900 | 2 | 205 | 0 | 36 |
| Terran / Air | 3 Victory | 6225 / 2025 | 3.07 | 7000 | 1 | 74 | 1 | 21 |
| Zerg / Rush | 3 Victory | 7350 / 2750 | 2.67 | 2850 | 1 | 133 | 1 | 27 |
| Zerg / Timing | 3 Victory | 12675 / 6425 | 1.97 | 4800 | 3 | 245 | 0 | 18 |
| Zerg / Power | 3 Defeat | 10900 / 18675 | 0.58 | 1425 | 13 | 74 | 0 | 28 |
| Zerg / Macro | 3 Victory | 14500 / 7775 | 1.86 | 7850 | 4 | 230 | 1 | 31 |
| Zerg / Air | 3 Victory | 3825 / 1600 | 2.39 | 4250 | 1 | 77 | 1 | 21 |

Values in the table use the first recording of each matchup; all recording results remain in JSON. Matching starts do not guarantee identical trajectories, so these representative values are not averages over independent games. These observations suggest mechanisms to investigate, not causal proof of why a game was won.

## Opening and spending evidence

Workers are observed Probe disappearances by 240 seconds with no later reappearance, not verified kills. Temporary absences (including gas harvesting) are retracted when the tag returns; loaded passengers remain tracked. Absences near the recording end can remain ambiguous. Completion times and idle/supply-block durations are sampled estimates; idle time sums across production facilities. The first costly army window is a replay-inspection candidate, not proof of the decisive engagement.

| Race / build | Workers lost by 240s | First Zealot / Stalker | First costly army window | Supply block seconds | Idle facility seconds |
| --- | ---: | --- | --- | ---: | ---: |
| Terran / Rush | 0 | 139.3s / 170.4s | 255-270s | 12.9 | 799.3 |
| Terran / Timing | 0 | 144.6s / 174.6s | 240-255s | 148.9 | 1051.1 |
| Terran / Power | 0 | 139.3s / 174.6s | 315-330s | 38.6 | 413.6 |
| Terran / Macro | 0 | 144.6s / 174.6s | 480-495s | 46.1 | 991.1 |
| Terran / Air | 0 | 138.2s / 170.4s | 375-390s | 6.4 | 381.4 |
| Zerg / Rush | 0 | 108.2s / 166.1s | 450-465s | 10.7 | 378.2 |
| Zerg / Timing | 0 | 108.2s / 162.9s | 480-495s | 6.4 | 692.1 |
| Zerg / Power | 0 | 108.2s / 163.9s | 435-450s | 16.1 | 1373.6 |
| Zerg / Macro | 0 | 108.2s / 167.1s | 315-330s | 6.4 | 667.5 |
| Zerg / Air | 0 | 108.2s / 160.7s | 555-570s | 6.4 | 143.6 |

## Costly trade windows and match details

### Terran / Rush

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-001.json`. End sample 1316.8s; peak 34 workers / 81 army supply. First offensive advance: 321.4s; first expansion advance: 367.5s; inspected sites: 8.

Movement: `{'offensive_target_switches': 16, 'short_target_reversals': 3, 'advance_regroup_transitions': 19, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 5867, 'sampled_long_move_reversals': 251}`. Action rejections: `{'direct:3674:113': 1}`.

Score-based bad-trade windows: 17; windows also showing own controlled-army disappearances: 17. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 4425.

Opponent prediction at last sample: **Unknown**, confidence 0.54. First correct confident classification: 188.6s; first home contact: 192.9s. Positive classification lead means recognition preceded contact: 4.3s.

- 975–990s: army lost 2625, army killed 825, economy killed 50; objectives `{'pressure': 6, 'recover': 8}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 9, 'IMMORTAL': 3, 'STALKER': 5}`; minimum estimated local advantage: 0.7217587027459957; minimum army health fraction: 0.8648601398601399; last sampled army center: `[41.01318359375, 103.031982421875]`; observed enemy composition: `{'MARAUDER': 10, 'MARINE': 18, 'GHOST': 4, 'VIKINGASSAULT': 2}`.
- 1095–1110s: army lost 1100, army killed 0, economy killed 0; objectives `{'pressure': 4, 'recover': 10}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'STALKER': 4, 'ZEALOT': 4}`; minimum estimated local advantage: 0.7928817325928973; minimum army health fraction: 0.9197247706422018; last sampled army center: `[57.42431640625, 114.786376953125]`; observed enemy composition: `{'MARAUDER': 18, 'MARINE': 22, 'GHOST': 4, 'VIKINGASSAULT': 2, 'VIKINGFIGHTER': 1}`.
- 1245–1260s: army lost 1025, army killed 0, economy killed 0; objectives `{'recover': 14}`, targets `['home']`.
  Own army disappearances: `{'SENTRY': 2, 'ZEALOT': 2, 'STALKER': 3}`; minimum estimated local advantage: 0.060435123366830386; minimum army health fraction: 0.6411184210526316; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 20, 'MARINE': 24, 'GHOST': 5, 'VIKINGASSAULT': 7, 'HELLIONTANK': 5, 'SIEGETANK': 1}`.
- Economic losses at 1245–1260s: 1700 resources; own worker/base disappearances `{'PROBE': 22, 'NEXUS': 1}`; objectives `{'recover': 14}`.
- Economic losses at 1290–1305s: 775 resources; own worker/base disappearances `{'NEXUS': 1, 'ASSIMILATOR': 1}`; objectives `{'stabilize': 1, 'develop': 3, 'recover': 3}`.
- Economic losses at 1260–1275s: 625 resources; own worker/base disappearances `{'PROBE': 7, 'ASSIMILATOR': 1}`; objectives `{'recover': 8, 'stabilize': 6}`.

### Terran / Timing

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-004.json`. End sample 1216.1s; peak 56 workers / 75 army supply. First offensive advance: 339.6s; first expansion advance: 441.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 9, 'short_target_reversals': 1, 'advance_regroup_transitions': 36, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 5672, 'sampled_long_move_reversals': 330}`. Action rejections: `{'881:208': 1, 'direct:3674:113': 2}`.

Score-based bad-trade windows: 18; windows also showing own controlled-army disappearances: 18. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 8150.

Opponent prediction at last sample: **Unknown**, confidence 0.42. First correct confident classification: 234.6s; first home contact: 247.5s. Positive classification lead means recognition preceded contact: 12.9s.

- 855–870s: army lost 2000, army killed 250, economy killed 725; objectives `{'pressure': 3, 'recover': 11}`, targets `['4355260425', 'home']`.
  Own army disappearances: `{'ZEALOT': 13, 'STALKER': 2, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.5157989155811992; minimum army health fraction: 0.814470284237726; last sampled army center: `[30.011962890625, 89.32080078125]`; observed enemy composition: `{'MARAUDER': 10, 'VIKINGASSAULT': 3, 'MARINE': 17, 'GHOST': 4}`.
- 735–750s: army lost 2225, army killed 1000, economy killed 0; objectives `{'pressure': 9, 'recover': 3}`, targets `['home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 7, 'STALKER': 3, 'SENTRY': 2, 'IMMORTAL': 2}`; minimum estimated local advantage: 0.6387915742867973; minimum army health fraction: 0.6967441860465117; last sampled army center: `[61.8555908203125, 113.30224609375]`; observed enemy composition: `{'MARAUDER': 6, 'SIEGETANK': 1, 'VIKINGASSAULT': 4, 'MARINE': 9, 'GHOST': 1}`.
- 915–930s: army lost 1000, army killed 50, economy killed 0; objectives `{'recover': 9}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 3, 'STALKER': 4}`; minimum estimated local advantage: 0.41479167880621187; minimum army health fraction: 0.8916666666666667; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 12, 'VIKINGASSAULT': 3, 'MARINE': 18, 'GHOST': 4}`.
- Economic losses at 990–1005s: 1250 resources; own worker/base disappearances `{'PROBE': 13, 'NEXUS': 1}`; objectives `{'recover': 10, 'stabilize': 4}`.
- Economic losses at 1200–1215s: 1150 resources; own worker/base disappearances `{'PROBE': 15, 'NEXUS': 1}`; objectives `{'recover': 9, 'pressure': 3}`.
- Economic losses at 585–600s: 1050 resources; own worker/base disappearances `{'PROBE': 11, 'NEXUS': 1}`; objectives `{'pressure': 3, 'stabilize': 11}`.

### Terran / Power

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-007.json`. End sample 753.2s; peak 56 workers / 49 army supply. First offensive advance: 277.5s; first expansion advance: 325.7s; inspected sites: 8.

Movement: `{'offensive_target_switches': 7, 'short_target_reversals': 0, 'advance_regroup_transitions': 16, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 1336, 'sampled_long_move_reversals': 74}`. Action rejections: `{}`.

Score-based bad-trade windows: 11; windows also showing own controlled-army disappearances: 11. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 5875.

Opponent prediction at last sample: **Unknown**, confidence 0.54. First correct confident classification: not observed; first home contact: 542.1s. Positive classification lead means recognition preceded contact: not observed.

- 555–570s: army lost 2050, army killed 250, economy killed 0; objectives `{'recover': 14}`, targets `['home']`.
  Own army disappearances: `{'COLOSSUS': 1, 'ZEALOT': 5, 'STALKER': 6}`; minimum estimated local advantage: 0.6094060392589824; minimum army health fraction: 0.7173165137614679; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 13, 'MARINE': 11, 'SIEGETANKSIEGED': 4}`.
- 480–495s: army lost 1150, army killed 0, economy killed 200; objectives `{'recover': 12, 'pressure': 2}`, targets `['4369678338', 'home']`.
  Own army disappearances: `{'STALKER': 2, 'SENTRY': 2, 'ZEALOT': 5}`; minimum estimated local advantage: 0.3272532501669592; minimum army health fraction: 0.8133802816901409; last sampled army center: `None`; observed enemy composition: `{'MARAUDER': 12, 'MARINE': 15, 'SIEGETANKSIEGED': 3, 'SIEGETANK': 1}`.
- 705–720s: army lost 1025, army killed 100, economy killed 0; objectives `{'pressure': 4, 'recover': 3}`, targets `['4369678338', 'home']`.
  Own army disappearances: `{'SENTRY': 1, 'STALKER': 1, 'IMMORTAL': 2}`; minimum estimated local advantage: 1.1862962534337698; minimum army health fraction: 0.29714285714285715; last sampled army center: `None`; observed enemy composition: `{'MARINE': 12, 'MARAUDER': 11, 'SIEGETANKSIEGED': 6, 'VIKINGASSAULT': 1, 'VIKINGFIGHTER': 1}`.
- Economic losses at 570–585s: 1500 resources; own worker/base disappearances `{'PROBE': 20, 'NEXUS': 1}`; objectives `{'recover': 10, 'stabilize': 4}`.
- Economic losses at 615–630s: 1500 resources; own worker/base disappearances `{'NEXUS': 1, 'PROBE': 20}`; objectives `{'stabilize': 3, 'pressure': 10}`.
- Economic losses at 675–690s: 700 resources; own worker/base disappearances `{'PROBE': 6, 'NEXUS': 1}`; objectives `{'recover': 4, 'stabilize': 4}`.

### Terran / Macro

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-010.json`. End sample 1067.1s; peak 56 workers / 149 army supply. First offensive advance: 277.5s; first expansion advance: 327.9s; inspected sites: 8.

Movement: `{'offensive_target_switches': 23, 'short_target_reversals': 0, 'advance_regroup_transitions': 36, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 12752, 'sampled_long_move_reversals': 499}`. Action rejections: `{'direct:3674:113': 1}`.

Score-based bad-trade windows: 2; windows also showing own controlled-army disappearances: 2. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 2175.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: 402.9s; first home contact: 795.0s. Positive classification lead means recognition preceded contact: 392.1s.

- 480–495s: army lost 950, army killed 50, economy killed 0; objectives `{'pressure': 10, 'recover': 4}`, targets `['4347658241', 'home']`.
  Own army disappearances: `{'ZEALOT': 7, 'STALKER': 2}`; minimum estimated local advantage: 0.8223648528202865; minimum army health fraction: 0.7563508064516129; last sampled army center: `[60.855712890625, 116.545166015625]`; observed enemy composition: `{'MARINE': 17, 'MARAUDER': 13, 'SIEGETANKSIEGED': 3}`.
- 555–570s: army lost 400, army killed 50, economy killed 0; objectives `{'recover': 6, 'pressure': 1}`, targets `['4383834113', 'home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 1.0862168599728625; minimum army health fraction: 0.8904692082111437; last sampled army center: `None`; observed enemy composition: `{'MARINE': 14, 'MARAUDER': 13, 'SIEGETANKSIEGED': 4}`.
- Economic losses at 810–825s: 1525 resources; own worker/base disappearances `{'PROBE': 17, 'NEXUS': 1, 'ASSIMILATOR': 1}`; objectives `{'stabilize': 6, 'pressure': 8}`.
- Economic losses at 825–840s: 400 resources; own worker/base disappearances `{}`; objectives `{'pressure': 11}`.

### Terran / Air

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-013.json`. End sample 752.1s; peak 56 workers / 115 army supply. First offensive advance: 273.2s; first expansion advance: 273.2s; inspected sites: 8.

Movement: `{'offensive_target_switches': 12, 'short_target_reversals': 1, 'advance_regroup_transitions': 21, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 5838, 'sampled_long_move_reversals': 209}`. Action rejections: `{'direct:3674:113': 1}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.35. First correct confident classification: 358.9s; first home contact: not observed. Positive classification lead means recognition preceded contact: not observed.

- 375–390s: army lost 450, army killed 0, economy killed 50; objectives `{'pressure': 5, 'recover': 9}`, targets `['4346609665', '4356046849', 'home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 1, 'IMMORTAL': 1}`; minimum estimated local advantage: 1.4180506666948316; minimum army health fraction: 0.5794823232323232; last sampled army center: `[66.465576171875, 110.536865234375]`; observed enemy composition: `{'VIKINGASSAULT': 3, 'MARINE': 4, 'BATTLECRUISER': 1, 'MARAUDER': 1}`.

### Zerg / Rush

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-016.json`. End sample 751.1s; peak 55 workers / 123 army supply. First offensive advance: 255.0s; first expansion advance: 295.7s; inspected sites: 8.

Movement: `{'offensive_target_switches': 9, 'short_target_reversals': 1, 'advance_regroup_transitions': 27, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 4170, 'sampled_long_move_reversals': 279}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.40. First correct confident classification: not observed; first home contact: 125.4s. Positive classification lead means recognition preceded contact: not observed.

- 450–465s: army lost 600, army killed 250, economy killed 0; objectives `{'pressure': 13, 'recover': 1}`, targets `['4345823234', 'home']`.
  Own army disappearances: `{'ZEALOT': 6}`; minimum estimated local advantage: 1.2652244367406829; minimum army health fraction: 0.8277258566978193; last sampled army center: `[73.145751953125, 121.1337890625]`; observed enemy composition: `{'ROACH': 6, 'ZERGLING': 5, 'HYDRALISK': 4, 'CHANGELINGZEALOT': 2}`.

### Zerg / Timing

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-019.json`. End sample 1002.9s; peak 33 workers / 109 army supply. First offensive advance: 339.6s; first expansion advance: 339.6s; inspected sites: 8.

Movement: `{'offensive_target_switches': 11, 'short_target_reversals': 0, 'advance_regroup_transitions': 18, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 6657, 'sampled_long_move_reversals': 311}`. Action rejections: `{}`.

Score-based bad-trade windows: 3; windows also showing own controlled-army disappearances: 3. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 400.

Opponent prediction at last sample: **Unknown**, confidence 0.50. First correct confident classification: 250.7s; first home contact: 190.7s. Positive classification lead means recognition preceded contact: -60.0s.

- 480–495s: army lost 500, army killed 275, economy killed 0; objectives `{'contain': 4, 'pressure': 5, 'recover': 3}`, targets `['4346871810', '4370989065', 'home']`.
  Own army disappearances: `{'ZEALOT': 3, 'SENTRY': 3}`; minimum estimated local advantage: 0.8085360565085866; minimum army health fraction: 0.8771626297577855; last sampled army center: `[56.43798828125, 112.272216796875]`; observed enemy composition: `{'ZERGLING': 8, 'ROACH': 6, 'HYDRALISK': 6, 'RAVAGER': 2, 'CHANGELINGZEALOT': 1}`.
- 570–585s: army lost 375, army killed 225, economy killed 50; objectives `{'pressure': 13, 'recover': 1}`, targets `['4346871810', 'home']`.
  Own army disappearances: `{'STALKER': 1, 'ZEALOT': 6}`; minimum estimated local advantage: 1.066807081694716; minimum army health fraction: 0.8703896103896104; last sampled army center: `[59.355224609375, 114.77197265625]`; observed enemy composition: `{'ROACH': 11, 'HYDRALISK': 6, 'ZERGLING': 14, 'RAVAGER': 2, 'CHANGELINGZEALOT': 2, 'BROODLING': 6, 'QUEEN': 1}`.
- 600–615s: army lost 350, army killed 225, economy killed 0; objectives `{'pressure': 6, 'recover': 8}`, targets `['4346871810', 'home']`.
  Own army disappearances: `{'STALKER': 2}`; minimum estimated local advantage: 0.5954834895691443; minimum army health fraction: 0.8072916666666666; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 6, 'ROACH': 9, 'ZERGLING': 10, 'RAVAGER': 2, 'BROODLING': 6, 'QUEEN': 1, 'CHANGELINGZEALOT': 2}`.
- Economic losses at 270–285s: 400 resources; own worker/base disappearances `{'NEXUS': 1}`; objectives `{'stabilize': 11}`.

### Zerg / Power

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-022.json`. End sample 1225.7s; peak 56 workers / 111 army supply. First offensive advance: 247.5s; first expansion advance: 298.9s; inspected sites: 8.

Movement: `{'offensive_target_switches': 10, 'short_target_reversals': 0, 'advance_regroup_transitions': 28, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 6894, 'sampled_long_move_reversals': 428}`. Action rejections: `{}`.

Score-based bad-trade windows: 13; windows also showing own controlled-army disappearances: 13. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 7575.

Opponent prediction at last sample: **Air**, confidence 0.83. First correct confident classification: 304.3s; first home contact: 217.5s. Positive classification lead means recognition preceded contact: -86.8s.

- 1005–1020s: army lost 2525, army killed 575, economy killed 0; objectives `{'recover': 14}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 9, 'ZEALOT': 1, 'IMMORTAL': 1, 'COLOSSUS': 1}`; minimum estimated local advantage: 0.27206249672945815; minimum army health fraction: 0.736401098901099; last sampled army center: `None`; observed enemy composition: `{'ROACH': 14, 'HYDRALISK': 10, 'BROODLORD': 6, 'ZERGLING': 24, 'QUEEN': 3, 'BROODLING': 47, 'CORRUPTOR': 1, 'LURKERMPBURROWED': 2, 'IMMORTAL': 1, 'CHANGELINGZEALOT': 1}`.
- 1140–1155s: army lost 1700, army killed 0, economy killed 0; objectives `{'recover': 8}`, targets `['home']`.
  Own army disappearances: `{'STALKER': 4, 'VOIDRAY': 1, 'ZEALOT': 2, 'SENTRY': 1}`; minimum estimated local advantage: 0.009325545172776072; minimum army health fraction: 0.332421875; last sampled army center: `None`; observed enemy composition: `{'ROACH': 9, 'HYDRALISK': 12, 'BROODLORD': 7, 'LURKERMPBURROWED': 2, 'ZERGLING': 26, 'CHANGELINGZEALOT': 4, 'QUEEN': 4, 'BROODLING': 136, 'CORRUPTOR': 3}`.
- 1020–1035s: army lost 1800, army killed 200, economy killed 0; objectives `{'recover': 14}`, targets `['home']`.
  Own army disappearances: `{'ZEALOT': 4, 'STALKER': 6, 'IMMORTAL': 1}`; minimum estimated local advantage: 0.1503410929718608; minimum army health fraction: 0.7387765957446808; last sampled army center: `None`; observed enemy composition: `{'ROACH': 13, 'HYDRALISK': 10, 'BROODLORD': 6, 'ZERGLING': 28, 'QUEEN': 3, 'CORRUPTOR': 2, 'BROODLING': 80, 'LURKERMPBURROWED': 2, 'IMMORTAL': 1, 'CHANGELINGZEALOT': 2}`.
- Economic losses at 1080–1095s: 1350 resources; own worker/base disappearances `{'PROBE': 17, 'NEXUS': 1}`; objectives `{'recover': 12, 'stabilize': 1}`.
- Economic losses at 645–660s: 1100 resources; own worker/base disappearances `{'PROBE': 12, 'NEXUS': 1}`; objectives `{'stabilize': 7, 'pressure': 3}`.
- Economic losses at 1095–1110s: 1050 resources; own worker/base disappearances `{'PROBE': 16, 'ASSIMILATOR': 2}`; objectives `{'recover': 2, 'pressure': 3}`.

### Zerg / Macro

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-025.json`. End sample 979.3s; peak 55 workers / 137 army supply. First offensive advance: 245.4s; first expansion advance: 294.6s; inspected sites: 8.

Movement: `{'offensive_target_switches': 18, 'short_target_reversals': 1, 'advance_regroup_transitions': 31, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 7690, 'sampled_long_move_reversals': 300}`. Action rejections: `{}`.

Score-based bad-trade windows: 4; windows also showing own controlled-army disappearances: 4. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 700.

Opponent prediction at last sample: **Macro**, confidence 0.75. First correct confident classification: 418.9s; first home contact: 313.9s. Positive classification lead means recognition preceded contact: -105.0s.

- 690–705s: army lost 1175, army killed 675, economy killed 200; objectives `{'recover': 4, 'pressure': 5, 'counterattack': 2}`, targets `['4352638984', 'home', 'site:0']`.
  Own army disappearances: `{'ZEALOT': 3, 'STALKER': 5}`; minimum estimated local advantage: 0.8054825359316897; minimum army health fraction: 0.7656622911694511; last sampled army center: `None`; observed enemy composition: `{'HYDRALISK': 10, 'RAVAGER': 3, 'ZERGLING': 12, 'ROACH': 11, 'CHANGELINGZEALOT': 1}`.
- 450–465s: army lost 400, army killed 75, economy killed 0; objectives `{'pressure': 1, 'recover': 13}`, targets `['4341891073', 'home']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.2439575328728412; minimum army health fraction: 0.8087912087912088; last sampled army center: `[65.20849609375, 122.466796875]`; observed enemy composition: `{'ZERGLING': 9, 'HYDRALISK': 5, 'ROACH': 9, 'RAVAGER': 2, 'CHANGELINGZEALOT': 1}`.
- 315–330s: army lost 400, army killed 125, economy killed 50; objectives `{'stabilize': 5, 'pressure': 2, 'counterattack': 1, 'recover': 2}`, targets `['4341891073', 'home', 'threat']`.
  Own army disappearances: `{'ZEALOT': 4}`; minimum estimated local advantage: 0.5281830321024074; minimum army health fraction: 0.6496323529411765; last sampled army center: `None`; observed enemy composition: `{'QUEEN': 1, 'ZERGLING': 10, 'ROACH': 6}`.
- Economic losses at 570–585s: 450 resources; own worker/base disappearances `{'PROBE': 9}`; objectives `{'stabilize': 7, 'recover': 7}`.

### Zerg / Air

Evidence: `runtime-20261031-161655-940898-42012dd3347940f89ea74c58cf4f9536-028.json`. End sample 627.9s; peak 56 workers / 91 army supply. First offensive advance: 260.4s; first expansion advance: 260.4s; inspected sites: 8.

Movement: `{'offensive_target_switches': 7, 'short_target_reversals': 1, 'advance_regroup_transitions': 21, 'invalid_cohesion_samples': 0, 'sampled_long_move_orders': 3173, 'sampled_long_move_reversals': 114}`. Action rejections: `{}`.

Score-based bad-trade windows: 1; windows also showing own controlled-army disappearances: 1. Loaded passengers remain tracked. Disappearances can include transformations; these checks corroborate evidence rather than certify every casualty. Own economy resource losses: 0.

Opponent prediction at last sample: **Unknown**, confidence 0.35. First correct confident classification: not observed; first home contact: 355.7s. Positive classification lead means recognition preceded contact: not observed.

- 555–570s: army lost 350, army killed 75, economy killed 100; objectives `{'counterattack': 8, 'pressure': 6}`, targets `['4334813185']`.
  Own army disappearances: `{'ZEALOT': 2, 'SENTRY': 1}`; minimum estimated local advantage: 1.8779257949912163; minimum army health fraction: 0.8613611111111111; last sampled army center: `[46.252685546875, 134.3946533203125]`; observed enemy composition: `{'MUTALISK': 1, 'ROACH': 7, 'ZERGLING': 11, 'HYDRALISK': 4, 'BROODLING': 13, 'QUEEN': 1, 'CHANGELINGZEALOT': 2}`.

## Opponent-strategy classification

Configured AI build is an evaluation reference, never model input. Heuristic scores are uncalibrated. Identical starts are grouped, not independent training/validation examples. Horizons use observations at or before that time and exclude games already ended. No future observations are used.

Accuracy counts Unknown as incorrect. Conditional accuracy considers only non-Unknown predictions; coverage shows how often the model committed. Multiclass Brier is the mean sum of squared probability error across five labels (0 is best; a uniform five-class forecast scores 0.8). Calibration bins compare the leading hypothesis probability with its observed correctness. These are development diagnostics on fixed scenarios, not held-out generalization results.

| Horizon | Eligible scenarios | Accuracy | Balanced accuracy | Coverage | Conditional accuracy | Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 120 | 10 | 0.0% | 0.0% | 0.0% | n/a | 0.815 |
| 180 | 10 | 0.0% | 0.0% | 0.0% | n/a | 0.815 |
| 240 | 10 | 20.0% | 20.0% | 20.0% | 100.0% | 0.672 |
| 360 | 10 | 40.0% | 40.0% | 40.0% | 100.0% | 0.483 |
| 600 | 10 | 10.0% | 10.0% | 20.0% | 50.0% | 0.594 |
| final | 10 | 20.0% | 20.0% | 30.0% | 66.7% | 0.575 |

Final confusion matrix: rows are configured reference builds; columns are predictions.

| Reference | Rush | Timing | Power | Macro | Air | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rush | 0 | 0 | 0 | 0 | 0 | 2 |
| Timing | 0 | 0 | 0 | 0 | 0 | 2 |
| Power | 0 | 0 | 0 | 0 | 1 | 1 |
| Macro | 0 | 0 | 0 | 2 | 0 | 0 |
| Air | 0 | 0 | 0 | 0 | 0 | 2 |

Expected calibration error: 0.32363400676081105. Per-class precision/recall, calibration bins, horizon predictions, evidence signals and all repeats are retained in JSON.
