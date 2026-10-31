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

## Status and next gates

Contract tests are synthetic and do not establish playing strength, actual
effects or human-input compatibility. Next add the guarded four-head action
contract, then decision-level transitions and an owned environment. The GRU,
encoder/heads and recurrent PPO follow complete rollout and lifecycle records.
The proposed 64/128/256 network dimensions and training dependencies remain
unbenchmarked. Expert-labelled imitation still requires an accepted frozen
teacher; live gameplay and retail transfer require their own acceptance.
