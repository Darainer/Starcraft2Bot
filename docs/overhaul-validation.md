# Adaptive tactics implementation and validation

Date: 2026-10-25. Branch: `feat/adaptive-pressure-tactics`.

Follow-up: [performance verification](performance-verification.md) records the
native startup attempt, a retail-metadata fix, and measured controller CPU costs.

The initial hard-coded overhaul is implemented. No model provider is connected.
This record distinguishes executable behavior from gameplay evidence. New
VeryHard wins and human-control compatibility have **not** been established.

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

The required locked-environment and package gates remain **unverified**:

- The installed `uv` executable is inaccessible in this environment, so
  `uv sync --locked` and the `uv run --locked` gates could not be completed.
- The environment lacks `hatchling`; `python -m build --no-isolation` confirms
  that the build backend cannot be imported. Installing missing build tooling
  was blocked by the environment's network restrictions.
- No dependency pins or lockfile contents were changed to work around this.

Run the repository's normal locked checks and `uv build` in an unrestricted
development environment or CI before publication. Local commits are checkpoints,
not proof that these remaining gates passed.

## Gameplay evidence and next evaluation

The saved pre-overhaul evidence contained six recent defeats, first completed
Stalkers at approximately 4:11-5:49, and gas banks above 1,600 in five of those
games. That motivated opening/production repairs. Those matches do not evaluate
this branch. Their research context and limitations are recorded in the
[architecture plan](tactical-architecture-plan.md).

No desktop control tool is available in this session. The Windows runbook requires
manual handoffs and actual human input checks; consequently no new gameplay or
human-control acceptance is claimed. Follow
[install and play](windows-install-and-play.md) and complete the
[acceptance record](runtime-acceptance-template.md), using the exact ping identity.
An API probe cannot substitute for that record.

Once that environment is accepted, compare the baseline commit with this branch
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
