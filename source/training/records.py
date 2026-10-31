"""Decision-level data contract, not a collector or a playable environment.

Evaluation metadata belongs to an external episode manifest. It must never be
merged into the actor state. Error/aborted episodes must be quarantined in full.
"""

from dataclasses import asdict, dataclass
from math import exp, isfinite

from source.games.starcraft2.action_codec import DecodeResult
from source.games.starcraft2.encoding import BeliefStateV1

REASONS = {"running", "victory", "defeat", "draw", "time_limit", "infrastructure_error", "aborted"}


@dataclass(frozen=True)
class Outcome:
    reason: str

    def __post_init__(self):
        if self.reason not in REASONS:
            raise ValueError("Unsupported episode outcome")

    @property
    def terminated(self):
        return self.reason in {"victory", "defeat", "draw"}

    @property
    def truncated(self):
        return self.reason == "time_limit"

    @property
    def learning_eligible(self):
        return self.reason not in {"infrastructure_error", "aborted"}

    @property
    def reward(self):
        return {"victory": 1.0, "defeat": -1.0}.get(self.reason, 0.0)

    @property
    def bootstrap(self):
        return self.reason in {"running", "time_limit"}


@dataclass(frozen=True)
class TransitionV1:
    episode_id: str
    decision_index: int
    policy_id: str
    before: BeliefStateV1
    decoded: DecodeResult
    after: BeliefStateV1
    recurrent_input: tuple[float, ...]
    recurrent_output: tuple[float, ...]
    value_estimate: float
    next_value: float | None
    outcome: Outcome
    issued_intent_ids: tuple[str, ...] = ()
    observed_effect_ids: tuple[str, ...] = ()
    schema_version: str = "sc2-transition-v1"

    def __post_init__(self):
        if self.schema_version != "sc2-transition-v1" or not self.episode_id or not self.policy_id:
            raise ValueError("Missing transition identity")
        if type(self.decision_index) is not int or self.decision_index < 0:
            raise ValueError("Invalid decision index")
        before, after, sampled = self.before.assessment, self.after.assessment, self.decoded.sampled
        if (sampled.based_on, sampled.sampled_at) != (before.version, before.time):
            raise ValueError("Transition must retain the sampling observation")
        if sampled.target_ids != tuple(t.id if t else None for t in self.before.targets):
            raise ValueError("Sampling candidate mapping differs from observation")
        if (
            after.time <= before.time
            or after.version <= before.version
            or after.time < self.decoded.plan.created_at
        ):
            raise ValueError("Transition must advance within the same episode")
        if (
            self.after.shared.episode_start
            or abs(self.after.shared.elapsed_seconds - (after.time - before.time)) > 1e-6
        ):
            raise ValueError("Bootstrap observation cannot be a reset or use a different interval")
        if self.before.shared.episode_start != (self.decision_index == 0):
            raise ValueError("Decision index and recurrent boundary disagree")
        if any(
            not isinstance(values, tuple)
            for values in (
                self.recurrent_input,
                self.recurrent_output,
                self.issued_intent_ids,
                self.observed_effect_ids,
            )
        ):
            raise ValueError("Transition sequences must be immutable")
        if (
            not self.recurrent_input
            or len(self.recurrent_input) != len(self.recurrent_output)
            or any(
                not isfinite(v) for v in (*self.recurrent_input, *self.recurrent_output, self.value_estimate)
            )
        ):
            raise ValueError("Invalid recurrent/value record")
        if self.before.shared.episode_start and any(self.recurrent_input):
            raise ValueError("Recurrent state must reset at episode start")
        if self.outcome.bootstrap and (self.next_value is None or not isfinite(self.next_value)):
            raise ValueError("Running/time-limit transitions require the final observation value")
        if not self.outcome.bootstrap and self.next_value is not None:
            raise ValueError("Terminal/error outcomes must not bootstrap")

    @property
    def elapsed_seconds(self):
        return self.after.assessment.time - self.before.assessment.time

    def discount(self, time_constant_seconds):
        if not isfinite(time_constant_seconds) or time_constant_seconds <= 0:
            raise ValueError("Discount time constant must be positive seconds")
        return exp(-self.elapsed_seconds / time_constant_seconds)

    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "episode_id": self.episode_id,
            "decision_index": self.decision_index,
            "policy_id": self.policy_id,
            "before": self.before.to_dict(),
            "decoded": self.decoded.to_dict(),
            "after": self.after.to_dict(),
            "recurrent_input": self.recurrent_input,
            "recurrent_output": self.recurrent_output,
            "value_estimate": self.value_estimate,
            "next_value": self.next_value,
            "outcome": {
                **asdict(self.outcome),
                "terminated": self.outcome.terminated,
                "truncated": self.outcome.truncated,
                "reward": self.outcome.reward,
                "learning_eligible": self.outcome.learning_eligible,
            },
            "issued_intent_ids": self.issued_intent_ids,
            "observed_effect_ids": self.observed_effect_ids,
            "elapsed_seconds": self.elapsed_seconds,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["episode_id"],
            data["decision_index"],
            data["policy_id"],
            BeliefStateV1.from_dict(data["before"]),
            DecodeResult.from_dict(data["decoded"]),
            BeliefStateV1.from_dict(data["after"]),
            tuple(data["recurrent_input"]),
            tuple(data["recurrent_output"]),
            data["value_estimate"],
            data["next_value"],
            Outcome(data["outcome"]["reason"]),
            tuple(data["issued_intent_ids"]),
            tuple(data["observed_effect_ids"]),
            data["schema_version"],
        )
