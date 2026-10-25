# Adaptive tactics implementation and validation

Date: 2026-10-25. Branch: `feat/adaptive-pressure-tactics`.

Follow-up: [performance verification](performance-verification.md) records the
resolved permission blocker, retail-metadata fix, controller CPU measurements,
and current live match results.

The initial hard-coded overhaul is implemented. No model provider is connected.
This record distinguishes executable behavior from gameplay evidence. New
VeryHard results are now recorded in the follow-up; human-control compatibility
remains unverified.

## Delivered implementation

| Plan area | Implementation |
| --- | --- |
| Shared assessment | Immutable versioned player observations, local compatible-force estimates, economy, recent trades/upgrades, visible targets and aged memory |
| Intelligence | Enemy-natural/main Probe route, expansion Observer patrol and mission approach checks; deduplicated expiring unit/base/tech evidence |
| Director | Scored candidate operations, eight-second commitment, entry/exit thresholds, emergency interruption, failed-target cooldown, validated shared force budgets |
| Coordinated missions | Persistent main/defense/denial squads, local abort and recovery, target-cleared events, containment, reinforcement cohorts and guarded cleanup |
| Fight execution | Ground/air-compatible HP/DPS, visible static defense and conservative Bunker assumption, cooldown kiting, overkill-aware focus and critical-unit retreat |
| Economy | Earlier opening tech/combat spending, sustainable expansion, bounded supply buffers, rotating production, gas balancing, temporary counter-composition, relevant upgrades |
| Arbitration | Existing ownership/reserve checks, one order per actor per observation, revoked/expired movement intents, combat priority over assembly, macro reservations respected by warp-ins |
| Scheduling | Micro 0.125 s, macro 0.25 s, mission updates 1 s, strategic reassessment 2 s plus material changes; full snapshots remain separate |
| Evaluation | Rich decision logs, sampled economy/production metrics, mission outcomes and offline assessment replay |
| Future policy seam | SDK-independent assessments/plans, asynchronous bounded request interface, cancellation, timeout, stale/material-change rejection and fake-backend tests |

The contracts intentionally expose supported roles and actions. Vision, target
evidence, force minimum/budget, assignment revision and expiry are executable
conditions; there is no arbitrary condition language or external model code in
the live control path. Scouting and reinforcement are local controllers attached
to the plan. They do not require an agent framework.

The architecture plan's stages 8 and 9 explicitly follow the initial baseline:
model-backed shadow evaluation, specialist replacements, and broader LLM-PySC2
integration remain subsequent work. They are not silently enabled by this change.
The initial implementation does not freeze those module boundaries permanently.

## Checks performed

The existing Python environment passed:

```powershell
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
.venv/Scripts/python.exe -m mypy
.venv/Scripts/python.exe -m source.run_assistant --check-config --config config/assistant.example.json
.venv/Scripts/python.exe -m pytest --cov --cov-report=term-missing -q -p no:cacheprovider --basetemp .local/pytest-final-overhaul
```

Result: **274 tests passed; 91.10% combined statement/branch coverage**. The
pre-overhaul suite contained 195 tests. Strict mypy scope remains the existing
configuration/ownership module; this is not a claim that every SDK-dependent
module is statically typed. Tests use actual SDK protocol objects and command
accounting with synthetic observations, and never launch SC2.

Scenarios cover air/ground incompatibility, Bunkers, local versus remote support,
fresh versus stale sightings, dead-unit deduplication, early pressure on VeryHard,
fortified targets, competing missions, human ownership, failed-target suppression,
continuation thresholds, manual retreat/regroup, resource reservations, Prism
escape during macro spending, production opening priorities, scheduling, and
asynchronous cancellation/error/freshness handling.

An earlier full run hit the existing one-second external script startup timeout
while other checks were running. A sequential full run passed. The production
script timeout was retained; failed scripts continue to fail closed.

The initial restricted environment could not run the locked/package checks.
After the user enabled Full Access, `uv sync --locked`, `uv run --locked ruff
check .`, `uv run --locked ruff format --check .`, `uv run --locked mypy`, and
`uv build` passed using the installed uv executable. The sdist and wheel were
built without changing dependency pins or the lockfile. A fresh locked coverage
run is recorded in the follow-up performance record when complete.

## Gameplay evidence and next evaluation

The saved pre-overhaul evidence contained six recent defeats, first completed
Stalkers at approximately 4:11-5:49, and gas banks above 1,600 in five of those
games. That motivated opening/production repairs. Those matches do not evaluate
this branch. Their research context and limitations are recorded in the
[architecture plan](tactical-architecture-plan.md).

Autonomous gameplay now runs successfully with the approved Full Access context;
see the follow-up for observed match results. No desktop control tool is available
to verify human input, so human-control acceptance remains pending. Follow
[install and play](windows-install-and-play.md) and complete the
[acceptance record](runtime-acceptance-template.md), using the exact ping identity.
An API probe cannot substitute for that record.

For broader performance evaluation, compare the baseline commit with this branch
on the same map, opponent race/build, difficulty, profile and available seed
controls. Start with bounded smoke matches, then repeated VeryHard trials across
Terran, Zerg and Protoss. Use at least five matches per chosen comparison cell;
report results by cell and retain replays rather than presenting one win as a
win-rate improvement. Use 4-8 game loops per turn when assessing reaction speed;
the default 32-loop fast test cannot validate 0.125-second micro behavior.

Track first combat unit, actual contact and economic damage in replays, expansion
and upgrade timing, army trades, supply blocking, idle production, resource banks,
mission aborts and controller cost. The analyzer's first offensive advance is a
movement milestone; it is not proof of enemy damage. Sampled idle/supply durations
are estimates. Observed empty sites are target-clearance evidence, not proof that
the bot destroyed a base. The force estimator is a heuristic and does not fully
simulate terrain, spells, detection or hidden reinforcements.

```powershell
python -m source.analyze_session logs/runtime-<session>.json
python -m source.replay_strategy logs/runtime-<session>.state.jsonl --output .local/policy-review.json
```

Replay inspection recomputes decisions from recorded assessments without issuing
orders. It cannot predict the outcome of a different action sequence. Later model
experiments should begin here and measure validity, evidence use, latency, stale
responses and cost before activation in live games.
