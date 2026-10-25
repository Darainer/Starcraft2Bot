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
| 144451-625652 | pressure / Medium Terran, accelerated, 900s bound | Victory near 10:45; replay saved; no runtime error | 130 used supply; all three level-1 ground upgrades completed |
| 144609-480602 | balanced / Medium Terran, accelerated, 900s bound | Victory near 11:25; replay saved; no runtime error | Three-base economy, upgrades and mixed army produced |
| 144827-628075 | robotics / Medium Terran, accelerated, 900s bound | Victory near 10:05; replay saved; no runtime error | Ground tech profile completed a full match; one rejected build action recorded |
| 144941-731526 | air / Medium Terran, accelerated, 900s bound | Time-limit tie; replay saved; no runtime error | Air/ground upgrades through level 2 completed; too few Void Rays despite a resource bank |
| 145414-879919 | air / Medium Terran after production fairness fix | Victory near 11:10; replay saved | Specialist capacity and fair scheduling removed the earlier air-profile stall |
| 145627-579202 | fortress / Medium Terran | Victory near 11:15; replay saved | Parallel Forges researched multiple level-2/3 chains |
| 150926-905704 | pressure / Medium Terran with scout/wave/Prism pipeline | Victory near 11:30; replay saved; no runtime error | Scouting acquired intel, a persistent 24-supply wave launched, 4 Warpgates operated, Prism reached forward phasing mode |
| 151537-875949 | pressure / Hard Terran with grouped waves | Victory near 11:45; replay saved; no runtime error | Direct API diagnostics exposed late warp-in placement failures; add current-power checks and reservation/backoff before further evaluation |
| 152121-807581 | pressure / Hard Terran after warp-in placement safeguards | 900-game-second limit, time-limit tie; replay saved; no runtime error or rejected actions | Wave 2 held 54 supply with 85% cohesion; army reached 86/126 supply; ground weapons and armor level 3 completed. Late reinforcements used the safe home power anchor after the Prism was no longer available |

## Findings and fixes

- Exact research availability IDs did not match the planner's generic IDs. Normalize through live game data; ground and air upgrade chains now complete in live matches.
- Fixed-radius placement search missed valid powered half-tile locations. Search finer candidates across safe bases and ready Pylons, then check worker reachability and nearby-unit connectivity.
- A first production class could consume every producer turn. Rotate fairly between Gateway, Robotics, and Stargate production; scale specialist buildings with the selected profile and bases.
- Individual-unit attacks fed the opponent units piecemeal. Scout first, wait for a minimum-supply and minimum-composition cohort, advance a cohesive wave, and hold reserves until they can reinforce as a group.
- Forward Warp Prism placement could fail repeatedly near occupied or unpowered spots. Restrict candidates to current power, avoid unit footprints and active reservations, and back off a failed location. The subsequent Hard run recorded zero rejected actions, though a time-limit tie shows that late-game finishing remains unresolved.

This is the running record: add one row for every completed live trial and update the findings when a run exposes a cause and a fix. Local raw logs and replays remain ignored by Git; the table records the evidence without adding large binary artifacts.

The research failure was an exact-versus-generic ability-ID mismatch: availability
queries returned exact research IDs, while the planner compared generic remaps.
Normalize both through live game data before comparison. The supply/layout stall
exhausted one small search region at the initial Nexus/Pylon; search all safe
bases and ready power anchors. Regression tests reproduce both causes.

Remaining live work includes additional profiles/opponents, longer economic and
combat evaluation, placement efficiency on other spawn/map geometries, and
measuring recurrent unit congestion. The latest Hard trial tied at the time
limit, so the wave pipeline still needs stronger late-game conversion. A few
successful matches do not establish a competitive bot. See `strategies.md` for
repeatable bounded test commands.
