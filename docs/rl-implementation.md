# RL foundation implementation

Implementation started 2026-10-31 on `feat/rl-foundation-20261031`, from frozen
source `64001d5`. This is an offline foundation for the approved
[two-layer architecture](game-agnostic-architecture.md),
[belief/action design](rl-architecture.md) and [training plan](rl-training-plan.md).
The user authorized starting this work while the rule-bot milestone continues.
That source is not an accepted expert teacher. No learner has been trained and
no learned controller is enabled in the assistant.

## Semantic input

`source/strategy_core/contracts.py` defines immutable `StrategicStateV1`, semantic
features, capabilities and opaque candidate handles. The core has no dependency
on SC2, its SDK, the runtime, assessments or game ontologies. Its serialization
retains supported/missing distinctions, uncertainty, evidence age and units.

`source/games/starcraft2/encoding.py` defines the initial `BeliefStateV1` adapter.
It consumes an immutable assessment and a snapshot of validated permissions;
optionally pass the current output of `ScoutingFacts.observe` (v2). Fact and
assessment clocks must match. The adapter stores domain facts and full target
identities outside the shared state. The new fact stream is an adapter input,
not a new shared-core schema. Labels, seeds, outcomes, profile names, raw unit
types and actor tags do not become shared features.

Fixed normalization `sc2-fixed-scales-v1` divides deployment capacity by 200,
workforce by 80, resource sites by 8, primary resource quantities by 1000,
secondary quantities by 500 and target travel distance by 200 map units.
These are declared engineering scales, without clipping or learned statistics.
Deployment capacity is a population-cost proxy, not combat effectiveness.
Banks, reserves and spendable balances remain separate. Local no-contact ratio
sentinels become missing. Opponent heuristic supports are not probabilities;
each belief ages independently and expires at the ontology army-memory bound.
Observed visible capacity may be zero while global enemy capacity stays unknown.

Targets reserve slots 0/1/2 for home/rally/threat, then rank up to thirteen
nonexpired candidates by descending value, ascending travel and canonical ID.
Absent slots are `None`; overflow is recorded explicitly. Domain IDs map to
opaque shared handles. Entity sets, income/queues, actor eligibility, intent,
observed execution effects and COAs need richer inputs before neural training;
unavailable blocks remain explicitly unsupported in this initial view.

## Action and decoder contract

`source/games/starcraft2/actions.py` freezes the documented head ordering:
seven objectives, sixteen targets, seven production postures and four scouting
questions. Four sampled indices consume 34 logits. The reference sampler takes
an explicit RNG; immutable records retain all logits, original conditional masks,
head usage, full candidate IDs and joint/per-head log probabilities. Forced
choices have log probability zero, as do inactive heads. Likelihood evaluation
uses stable log-softmax and the recorded masks; execution masks stay separate.

`action_codec.py` composes existing rule-policy mission allocation with a selected
legal objective/target, then calls `validate_plan`. Rule-supported offensive
options, current emergency guards, stale evidence and permissions constrain the
initial masks. Recovery targets home and development targets rally. Emergencies
can force stabilization/recovery. Reordering slots does not change a previously
sampled full target identity. Stale/future samples, disappeared targets and lost
permissions produce recorded fallbacks, preserving the original likelihood.
Plans still need current ownership/resource/ability checks in the executors.

Prototype production templates transfer at most eight supply of configured
targets per decision, with exact integer conservation and a 200-unit target cap.
Preference order is ground screen: Zealot; general ranged: Stalker; anti-air:
Stalker then Void Ray; anti-armor: Immortal then Stalker; anti-light: Colossus
then Zealot; rebuild: Zealot then Stalker. Only already-positive targets qualify;
no template enables a caster or ability. Donors are ordered by descending unit
supply then name, retaining up to four existing Zealots/Stalkers. A transfer
requiring fractional units is skipped. Keep-current preserves the assessment's
targets. Templates are versioned prototype heuristics awaiting gameplay evidence.
They propose future targets; immediate purchases retain the existing macro rules.
Expansion requires the existing composed decision and current expansion permission.
Scouting requests ask one question through the existing executor, without adding
the rejected cost-aware scouting controller.

## Transition contract

`source/training/records.py` joins sampling observations, decoded plans, subsequent
observations, recurrent input/output, values, intent/effect references and explicit
outcomes. Sample masks and execution masks are separate. Victory/defeat/draw
terminate with rewards +1/-1/0. Duration cutoffs truncate, require the final
observation's bootstrap value and receive no fabricated terminal reward. Errors
and intentionally aborted episodes are ineligible for learning; a future collector
must quarantine the **whole episode**, including earlier running transitions.
Issued intents and observed effects have separate fields, with neither implied
by the other. The default intermediate reward is zero.

Records reject reset observations as bootstrap states, inconsistent clocks and
candidate mappings, and nonzero recurrent state at episode start. A time-based
discount helper uses `exp(-elapsed_seconds / time_constant_seconds)`; selecting
the constant and implementing time-aware GAE remain learner work. No sequence
buffer or PPO update exists yet. A collector must supply frozen episode manifests
with all source/policy/ontology/normalization/lock/binary/map/opponent/seed/split
identities required by the training plan, kept outside actor inputs. It must also
record infrastructure failures that occur before a complete transition exists.

## Status and next gates

Contract tests are synthetic and do not establish playing strength, actual
effects or human-input compatibility. Next implement decision-level collection,
complete manifests and an owned environment. Faithful teacher-label round trips
and richer entity/feedback inputs remain pending. The GRU,
encoder/heads and recurrent PPO follow complete rollout and lifecycle records.
The proposed 64/128/256 network dimensions and training dependencies remain
unbenchmarked. Expert-labelled imitation still requires an accepted frozen
teacher; live gameplay and retail transfer require their own acceptance.

## Validation, 2026-10-31

Native Windows, Python 3.12.10: all 622 synthetic tests passed, including 57 new
RL contract scenarios. Combined statement/branch coverage was 89.51% against the
85% repository floor. `uv sync --locked`, `uv run --locked ruff check .`,
`uv run --locked ruff format --check .`, `uv run --locked mypy`,
`uv run --locked pytest --cov` and `uv build` all passed. Strict typing now covers
the portable contracts in addition to the existing configuration/ownership boundary.
The runtime/SDK pin and live assistant integration are unchanged. No SC2 game
was launched for this foundation; environment/effect/playing-strength validation
and human shared-control acceptance remain pending.
