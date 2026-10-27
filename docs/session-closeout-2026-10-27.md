# Protoss repair session closeout — 2026-10-27

Stopped at the user's request. No game clients or launch queues remain.
This is an **experimental checkpoint**, not a promoted competition release.
The working `source/` tree contains tested draft changes; it is not identical to
any complete live-tested integration. Candidate patches preserve the exact later
experiments separately. Do not infer their results apply to the default checkout.

## Results worth preserving

All targeted comparisons used pressure, VeryHard, BelShirVestigeLE, seed
20261025 and eight-loop observations. Three repeats measure reproducibility under
one condition, not three independent scenarios. Original-limit tests used 1500
game seconds; shorter tests are explicitly censored and are not wins.

| Frozen candidate / target | Result | Interpretation |
| --- | --- | --- |
| `9fd64a1`, full development matrix | 9 wins, 18 defeats, 3 timeouts | Win count unchanged from `af603e0`; Zerg Macro regressed. |
| `pressure-repair-v2`, Zerg Macro | 3 wins at 850.4s | Restored this failing target with scoped danger, bounded defense and movement repairs. |
| `integrated-v1`, Zerg Rush | 3 wins at 935.4s | Opening plus bounded response converted baseline defeats into completed wins. |
| `pressure-fight-v5`, Terran Power | 3 wins at 1335.4s | A healthy force with current favorable fight evidence no longer flees solely because of trailing losses. |
| `integrated-v4`, Terran Power | 3 wins at 1345.4s | Winning combat correction survived integration. |
| `integrated-v4`, Zerg Rush | 3 wins at 915.4s | Zero persistent Probe disappearances by 240s, versus eight in baseline. |
| `integrated-v4`, Zerg Macro | 3 defeats at 1150.4s | **Integration is not ready:** production/tech starvation remains. |

These results come from different frozen candidates and must not be combined
into a claimed overall win rate. The full `retreat-v1` matrix was poor: 6 wins,
13 defeats and 11 timeouts. Terrain-only and counterfire-only iterations also
failed Power retention. The more accurate weapon-DPS variant timed out all three
Power games and was not merged into the successful calibrated decision guard.

## What the evidence taught us

1. **Production and position both matter in the opener.** A Gateway could finish
   around 85s but wait while saving for expansion; the first Zealot arrived after
   the approach warning. One earlier Zealot still failed. Proactive second Gateway
   construction at 50.4s, completion at 95.4s, and a protected early hold prevented
   sequential defenders from chasing enemies up to 32 units from home. All three
   successful Rush tests had zero early persistent Probe disappearances. No battery
   completed in the key opening test, so the gain must not be attributed to healing.
2. **Do not apply that opener indiscriminately.** Against Terran it delayed the
   first Stalker to 420s. Scoping the defense opener to publicly known Zerg restored
   Terran Core/Stalker timings to 120.4/190.4s. Random/unknown race does not activate
   it; hidden AI build labels and classifier predictions are not strategy inputs.
3. **A flank is not the whole army.** `min(8, army_supply * .3)` let an eight-supply
   detachment trigger global recovery of a 132-supply force. The corrected threshold
   is `min(army_supply, max(8, army_supply * .3))`, preserving small-army danger checks.
4. **Tiny raids caused a self-sustaining defensive stall.** More than 140 army supply
   held at a remote safe base against one or two threatening supply. Projected,
   domain-compatible bounded defenders can respond while the main force continues.
   Heavy threats and inadequate responses retain full defense.
5. **Recovery was suppressing fire and sometimes reversing destinations.** Home
   selection flipped 69 map units during a retreat. Stable safe goals and micro
   routing fix that hazard; healthy automatic-recovery units can fire only at
   currently in-range targets, then escape on cooldown. Manual/scripted retreat,
   critical health, ownership and one-order arbitration remain authoritative.
   Movement repairs alone did not produce a stronger policy. The decisive Power
   improvement also required current main-fight evidence before overriding a
   trailing-loss retreat. Missing/legacy evidence remains conservative.
6. **Terrain goals need validation.** Short forward formation destinations could
   land on cliffs. Validating ground segments/slots and falling back to a reachable
   objective lets the engine route around the obstacle; invalid standing orders
   must not suppress their corrective replacement. This fixed a real command flaw
   but did not independently solve combat losses.
7. **Income recovery worked, but was not a completed-win test.** In three deliberately
   interrupted Timing games, replacement Nexus/gas construction reduced idle workers
   from 18 to 3 and restored gas from zero to 172 at 1145.4s. Empty Assimilators must
   not consume the active quota; replacement mineral sites must actually contain
   resources. Configured base ceilings still apply.
8. **Integration exposed spending starvation.** Winning Macro pressure had its
   first Immortal at 290.4s; integrated-v4 delayed it to 585.4s despite Robotics
   finishing only 55s later. Cheap units, support Prism and expansion purchases
   consumed the budget. A first-tech-unit reservation is the next concrete repair.
   Retuning combat thresholds is not a substitute for producing the intended force.

Five-second samples locate important windows, but are not exact replay UI review
or counterfactual simulation. Fungal Growth affected many units during the original
Macro collapse, so the retreat destination flip is not its sole established cause.
Weapon-aware DPS changes alter the ratio scale; do not combine them blindly with
the successful guard's 1.5 threshold. Lower reversal counts, survival and passing
software tests do not by themselves establish stronger play.

## Unfinished work and reproducibility

[Candidate patch archive](experiments/2026-10-27/README.md) preserves later source
and test experiments against `9fd64a1`. Raw logs, runtime JSON and replays remain
local and ignored, with separate records by candidate. The patches contain no
maps, replay binaries, credentials or personal absolute paths.

`integrated-v5` was **never launched**. Its first-tech investment work is unfinished:
the last complete suite passed 429 tests before later gas-arbitration edits; the
latest focused run had **21 passes and one failure**. Staged and latest check source
copies differ. Both versions, their status and the failing test are archived.
Reconcile and retest them before any promotion. The planned investment preserves
two initial defenders, then funds Core/first Stalker/first Immortal instead of
cheaper fallback purchases; cross-controller gas reservation remains unresolved.

The checkpoint working tree passed locked sync, Ruff lint/format, configured mypy,
**355 tests with 92.85% coverage**, and source/wheel builds. This is distinct from
isolated candidate counts (integrated-v4: 411 tests). Archived experimental patches
are not enabled by or covered by that checkpoint pass.

Future work should use short targeted rejection gates, not mandatory thirty-game
runs of a poor candidate. First restore Macro production without losing Rush and
Power, then verify existing Air wins. Only a promising integration earns broader
regression testing. Eight concurrent live clients remains the user-approved limit.
Elite strength, held-out generalization, human shared-control acceptance and an RL
opponent pool are not demonstrated by this session.
