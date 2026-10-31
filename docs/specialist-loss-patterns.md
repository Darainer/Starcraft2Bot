# Specialist preservation and loss patterns

Offline follow-up, 2026-10-31. No new games or gameplay changes underpin this
analysis. The final 36 remain frozen at `d0f8cf3`; see the
[final report](final-bot-report-2026-10-31.md).

## Preserve the specialists as complete recipes

The earlier specialists remain valuable candidates. A failed automatic
integration does not invalidate their fixed-scenario wins. The current registry
adapts their components; its source labels do not load an exact historical bot.
A reproducible recipe also fixes composition rules, funding priorities, tactical
availability, scouting policy, profile and configuration.

| Reference recipe | Evidence | Required fidelity |
| --- | --- | --- |
| Terran funded counters + local range, `287dbd5` | Rush 3/3 and Timing 3/3 | Funding and local range remain available throughout the match; original opening/Observer scouting, no V3 worker revisit |
| Zerg reactive baseline, `b3aff99` | Five-build block 15/15 | Positive-evidence early Robotics plus baseline fallback; original scouting; no new first-Colossus completion rule |
| R2 Terran economy/pressure | Power/Macro/Air each 3/3 | R2 priorities, without new counter-funding or range-selection overrides |
| Zerg completion candidate, `d0f8cf3` | Additional-seed Power/Macro 6/6 | V3 recon + requested first-Colossus completion; main-seed Power still loses 3/3 |

The next implementation should preserve these full recipes with explicit
component permissions. Fixed selection must be tested for fidelity before
using it to evaluate a selector. Missing scouting should raise uncertainty and
request recon; it should not automatically cancel every ongoing investment or
basic tactical capability.

## What the recorded comparisons show

Numbers are means of three fixed-start repeats, not independent samples. Army
trade and economy values are cumulative score estimates, not certified kills.
The older 5s/new 1s sampling also limits exact engagement attribution. The
[full audit](experiments/2026-10-31/specialist-loss-pattern-audit.json) preserves
all source arms and repeat records.

| Case | Winning reference: army trade; own/enemy economy loss | Integrated result: army trade; own/enemy economy loss |
| --- | --- | --- |
| Terran Rush | 1.26;400/5050 | 0.49;4425/2525;3D |
| Terran Timing | 0.87;250/12275 | 0.42;8150/4200;3D |
| Terran Power | 0.91;0/7000 | 0.12;5875/450;3D |
| Zerg Power, original seed | 2.32;1575/9000 | 0.58;7575/1425;3D |

All eight winning conditions in the final set inflicted more economy damage
than they lost; all four losing conditions did the reverse. This is a
retrospective pattern, not a causal threshold or a rule that predicts wins.
The winning Terran Timing specialist traded armies below 1:1 while preserving
income and inflicting substantial economic damage. A blanket 1:1 retreat rule
would reject useful fights.

Concrete differences:

- Terran Rush's first Bay moved from 470.4s to 593.6s, and first Colossus from 650.4s
  to 711.4s. Earlier Robotics alone did not preserve the full investment plan.
- Terran Timing's first Colossus was close: 470.4s versus 483.2s. Both reached
  56 workers, yet peak army fell from 127 to 75 supply. By 600s, the representative
  winner had three bases/56 workers; the loser had two/43. The 585-600s window
  records a Nexus and eleven Probe disappearances. This is a defense/attrition
  problem as well as a production problem.
- Terran Power received an earlier Colossus 456.4s versus 585.4s and still lost.
  Zerg Power likewise received 582.9s versus 625.4s and lost on the original seed.
  Counter availability does not establish protected firing positions or a good
  engagement.
- On the additional Zerg seed, V3 and the completion candidate match first
  Robotics/Immortal/Bay at 279.6/371.8/522.9s. V3 completed no Colossus before its
  997.5s defeat; the candidate completed one at 585s and won at 1954.3s. This is
  useful targeted evidence for delivering an already-requested counter.

The [prefix audit](experiments/2026-10-31/specialist-prefix-audit.json) retains
representative observations through 600s. Its first home contact is sometimes a
single Zergling; that is not proof of a committed attack.

## Hypotheses checked rather than assumed

All 15 Terran final games selected both counter-tech and counter-range at some
point. The four-supply trigger does not distinguish bio pressure from a fortified
Tank line, or identify a good opportunity to attack workers.

Selection churn is real, but cannot explain every loss: the winning additional
Zerg Power trace changes packages 33 times. An offline real-SDK
[range availability audit](experiments/2026-10-31/specialist-range-availability-audit.json)
found that during 180-600s, counter-range was enabled throughout the recorded
Terran Timing engagement phases. Rush had only 2.1s of recorded engaged time
without it. A theory that the rule simply switched off in every decisive fight
is unsupported.

The Timing loser accumulated 148.9 supply-block seconds overall, but only 8.6s
before 600s, versus 5s in the winner. Most of this block therefore follows the
initial fighting and base damage; it is not evidence of a broken initial build.
Likewise, raw ready actors outside geometric weapon range can be moving normally;
these samples do not prove avoidable idle time or canceled shots.

## Dedicated tactics to develop

| Trigger from observed facts | Tactic | Exit/reassessment and useful metric |
| --- | --- | --- |
| Valuable mining/production asset taking damage; nearby defenders can arrive while it survives | Local asset counterattack: tolerate a moderately worse army trade to preserve income; maintain a nearby regroup position | Reassess own damage, full enemy potential DPS and asset survival; measure workers/base saved and subsequent trades |
| Unfavorable skirmish near an expansion | Short local regroup, cohesion and weapon recovery, then re-engage the same force from a better position | Require a changed position/readiness/support condition; avoid repeated identical pushes; measure regroup distance and time until useful re-engagement |
| Visible Tank line or other dangerous weapon envelope | Screen, stage protected counters, cost approaches by exposure, or attack a softer scouted economic target | Preserve ready volleys and critical-unit escape; measure damage before first own volley and participating counter supply |
| Scouted army mix differs from existing targets | Reframe composition by matchup, actual fielded units, tech readiness and bounded supply/production budget | Stop replacing unsuitable units; do not discard living units; measure delivered counters before the relevant fight |
| Fresh exposed worker line and a usable escape route | Dedicated Oracle worker harassment with exclusive ownership and opt-in beam | Leave on visible air threats, low shields/energy, empty line or Lock On; measure worker damage, unit losses and mining disruption |
| Burrowed/cloaked threat evidence, missing detector coverage | Protect and assign detection to the fighting force before entering that position | Detection/escort must reach the fight; expansion patrol completion alone is insufficient |

Ares provides a primary example of separate weapon/effect danger grids and
costed paths, useful for implementing exposure-aware approaches. Its coefficients
are starting choices, not validated thresholds for this bot.
[Ares pathing](https://raw.githubusercontent.com/AresSC2/ares-sc2/67187778f931035c8bb0380ef63a6cd9dedc478b/docs/tutorials/influence_and_pathing.md)
Blizzard's public weapon schema supplies domains, damage bonuses, range and
period for more faithful matchup scoring.
[Blizzard weapon data](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/data.proto)

Enemy fire spent on a structure may create an opportunity, but enemy targeting
is uncertain and can change immediately. Use observed own-structure damage and
legal visible geometry; keep enemy potential DPS intact in the risk estimate.
The earlier siege-approach candidate lost 3/3, so its whole implementation should
not be re-enabled without isolating and testing a narrower change.

## Next comparison boundary

First reproduce the fixed Terran Rush/Timing recipes in six games with original
scouting. Stop to repair fidelity if those fail. Then isolate fixed versus auto
selection and opening-only versus revisit scouting on one failed build, three
repeats per arm. New composition, Oracle harassment and asset-defense tactics
need separate opt-ins and targeted gates; do not combine all of them in the next
acceptance batch. This document starts no games.
