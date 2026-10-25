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
| 153505-454397 | pressure / Hard Terran, 3-base economy | 900-game-second limit, tie; replay saved; four rejected attack actions | Reached 3 Nexuses, 6 Warpgates, 54 Zealots/Stalkers/Immortals combined, 116 army supply, but accumulated 2.6k minerals and 3.1k gas; more bases did not convert the larger bank into a win |
| 153837-784433 | robotics / Hard Terran, 3-base economy | 900-game-second limit, tie; replay saved; two rejected attack actions | Reached the fixed 120-army-supply composition with 3 Colossi and 8 Immortals, but ended at 184/197 supply with 5.5k minerals and 3.7k gas. Fixed worker and composition caps were leaving supply and resources unused |
| 154340-267215 | robotics / Hard Terran with expanded army target and 56-worker cap | 900-game-second limit, tie; replay saved; no rejected actions | Army grew to 138 supply (up from 120), 56 workers, 194/200 total supply, 4 Colossi and 8 Immortals. Ground upgrades reached level 3; 4.1k minerals and 3.5k gas remained. Larger force improved capacity but did not finish Hard Terran |

## Regression ledger

Keep this list cumulative across branches and matches. When a failure returns, add the run/sample evidence and link the fix to its regression test or live check. “Live” means observed in the listed matches; it is not a claim of universal correctness.

| Failure mode or optimization | Evidence and correction | Guardrail / current status |
| --- | --- | --- |
| Retail SC2 order ID crashed the SDK when an unknown ID was mapped (`4135`) | Live startup/game surfaced order IDs absent from the SDK enum. Preserve unknown IDs as opaque observations and map known retail aliases to canonical metadata. | Startup audits all required command metadata; live 56-command audit passes with 0 failures. |
| API/runtime version drift could silently invalidate commands | Bot depended on SC2 data and SDK assumptions. Record exact binary/data identity and audit commands before joining. | Startup rejects incompatible versions/metadata. Tested on SC2 `5.0.17.98310`, build `98310`, hash `9C1F3D3D30CA252E33FC67CA05CBE1EA`; other builds remain unverified. |
| State extraction could imply omniscient/full-event access | API observations omit fogged enemy state and sampling skips events between samples. | Save full player-visible observations plus raw availability at five-second cadence; label fog scope and sampling limits. Replay is the separate event record. |
| Research stayed idle despite resources and available Forges | Exact research IDs from availability did not match generic planner IDs. Normalize through live game data. | Regression coverage for exact/generic mapping; live ground upgrades reached levels 1–3 in multiple matches. Air upgrades also completed in the Medium air trial. |
| Supply or construction stalled after exhausting the initial base/Pylon search | Live supply/layout stalls at one small search region. Search safe bases and ready power anchors; retry bounded placement regions. | Placement/supply regression tests; live later matches reached 181–200 cap. Other map geometries still need evaluation. |
| Buildings blocked unit paths or production locations | Live Immortal spawn failed with `CantFindPlacementLocation`; tight candidates risked blocking nearby ground traffic. | Reserve mining/building exits, align powered half-tile locations, check worker reachability and nearby connectivity, reserve accepted pending footprints. Robotics match later produced Immortals and Colossi. |
| Paid production/research classes starved each other | Air Medium trial tied with too few Void Rays despite resources. A fixed first producer order starved specialist production. | Rotate production classes fairly, scale Robotics/Stargates with setup and bases. Subsequent air Medium trial won with 3 Stargates. |
| Economy finished with no upgrades or a low supply ceiling | Early VeryEasy run had no upgrades and stopped at 46 supply; Easy reached 102 with first upgrades. | Research gets periodic priority over extra production; expand supply search and add full ground/air level 1–3 chains. Live Medium/Hard trials completed ground level 3. |
| Direct warp-in action cost/supply accounting could be wrong | SDK's separate warp ability cost lookup can report zero. | Use live unit price and explicit supply debit; regression covers Stalker cost (875 minerals, 950 gas, 18 supply from the recorded test state). |
| Warp-ins repeatedly failed at unavailable or occupied points | Hard wave trial recorded repeated placement rejection `41`. | Require current Psionic Matrix coverage, visible/legal placement, avoid unit footprints and active reservations, expire/back off rejected points. Next Hard runs had 0 rejection `41`; later attack rejections are separately recorded. |
| Bot streamed individual units into combat | User observation and live tests showed piecemeal attacks. | Scout, satisfy minimum supply/unit/composition gates, hold reserves, move a persistent wave with cohesion checks and batched reinforcements. Medium wave trial won; Hard runs now form 24–102 supply cores but can still lose them. |
| Wave movement did not include distant reinforcements promptly | Late units could trail the core; Warp Prism phase could be lost or no longer useful. | Keep remote units at rally until a six-unit/12-supply batch forms; Prism adds forward power behind the wave with home-Pylon fallback. Live Prism staging/phasing and home fallback observed. Cargo drops are not implemented. |
| Scout/composition left counters too low for visible enemy units | Visible enemy composition can expose air, armor or light-ground needs. | Adaptive composition raises Stalker, Immortal and Colossus targets; wave gates require anti-air and profile-specific heavy units. Repeated Hard results still need stronger counter/retreat conversion. |
| Injured units or visible local threats could be ignored between strategic samples | Five-second strategic interval is too slow for immediate combat response. | Half-second tactical micro handles critical-health retreat, in-range focus fire and pathable kiting. Strength estimate remains heuristic, not a combat simulator. |
| Hard late-game armies plateaued at profile targets with high resource banks | Hard pressure 2-base tie: 86 army supply/124 used; 3-base pressure: 116 army and ~5.8k bank; robotics: 120 army and ~9.2k bank. | Pressure now targets 3 bases; pressure/robotics worker cap 56; robotics target increased to 136 nominal army supply (138 observed including Prism). Latest Hard robotics reached 138 army/194 total supply with no rejected actions but still tied. **Open:** improve late-game target selection, counter composition, and repeatable wave survival. |
| Adding a profile-controlled field omitted defaults from other profiles | Launch failed with `KeyError: 'max_workers'` before SC2 started. | Add `max_workers` to every profile and ensure CLI/profile switching applies it. Corrected launch completed; latest Hard robotics result is in the table. |
| Immediate action failures could be lost by the SDK wrapper | SC2 action result is separate from observation errors. | Shared client records response rejections by ability/result/tags and sampled reports aggregate them. Latest Hard robotics recorded none; attacks with result `113` appeared in earlier runs and need target/unit-level investigation. |
| Strategy helper could hang or return invalid orders | Local script is user code and may exceed a game sample. | Fresh subprocess, isolated interpreter flags, one-second timeout, schema and map-bound validation; failures issue no new tactics that sample. It is not a security sandbox. |
| External control could compete with the runtime's SC2 connection or race commands | Second API client is unsupported; multiple commands could overwrite each other. | Session mailbox accepts one atomic command at a time, acknowledges it in the report, and rejects unsupported legacy sessions. |
| Automation could override a selected or released unit | Human selection/release is the ownership boundary. | All delegated actions pass eligibility checks; combat spells stay opt-in. Startup/API telemetry does not certify human-control acceptance. |

This is the running record: add a row for every completed live trial and update the ledger whenever a match, API audit, or startup exposes a failure or optimization. Local raw logs and replays remain ignored by Git; the table records evidence without adding large binary artifacts.

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
