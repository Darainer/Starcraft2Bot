# Autonomous refinement progress — 2026-10-25

Branch: `feature/autonomous-strategy-refinement`. Each behavior change has a
regression test where feasible. Local logs, raw snapshots and replays remain
ignored; the following observations summarize specific runs rather than claiming
a general win rate or human-control acceptance.

Game identity: SC2 5.0.17.98310, data build 98310,
data version `9C1F3D3D30CA252E33FC67CA05CBE1EA`. SDK: burnysc2 7.3.0,
pys2clientprotocol 1.0.2. Map: BelShirVestigeLE.

## Checkpoints

- `a1ce49d`: preserve opaque retail order IDs instead of crashing on 4135;
  audit command metadata; add five-second player-state export, five profiles,
  strategy injection and local session commands. 142 tests passed.
- `cd40a4a`: reserve mining/exit lanes and building aisles, check local ground
  connectivity, retry failed production less frequently, expand upgrade chains.
  Trigger: live Immortal production failed with CantFindPlacementLocation.
  149 tests passed.
- `b73c9b7`: correct half-tile powered building placement, introduce owned-unit
  micro, sampled session analysis and graceful local exit with saved replay.
  Trigger: conservative spacing candidates stalled Gateway construction.
  154 tests passed.

## Live iterations

| Run stamp | Policy/opponent | Observed result | What it revealed |
| --- | --- | --- | --- |
| 143435-526107 | pressure / VeryEasy Terran, real time | Deliberately stopped after 247 sampled game seconds; replay saved | Opening progressed, but research remained inactive |
| 143913-132613 | pressure / VeryEasy Terran, accelerated | Victory near 9:05; replay saved; no runtime error | Supply stalled at 46 and upgrades stayed empty despite surplus resources |
| 144206-109033 | pressure / Easy Terran, accelerated, 600s bound | Time-limit tie; replay saved; no runtime error | Supply reached 102; weapons/armor/shields level 1 completed; Immortals produced |

The research failure was an exact-versus-generic ability-ID mismatch: availability
queries returned exact research IDs, while the planner compared generic remaps.
Normalize both through live game data before comparison. The supply/layout stall
exhausted one small search region at the initial Nexus/Pylon; search all safe
bases and ready power anchors. Regression tests reproduce both causes.

Remaining live work includes additional profiles/opponents, longer economic and
combat evaluation, placement efficiency on other spawn/map geometries, and
measuring recurrent unit congestion. A few successful matches do not establish a
competitive bot. See `strategies.md` for repeatable bounded test commands.
