"""Four categorical SC2 heads and the exact masked sampling distribution.

No learner dependency is needed to freeze this contract. A tensor implementation
must agree with these reference likelihoods, including inactive/forced heads.
"""

from dataclasses import asdict, dataclass
from math import exp, isclose, isfinite, log

OBJECTIVES = ("develop", "stabilize", "recover", "pressure", "counterattack", "contain", "finish")
POSTURES = (
    "keep_current",
    "ground_screen",
    "general_ranged",
    "anti_air",
    "anti_armor",
    "anti_light",
    "rebuild",
)
QUESTIONS = ("commitment", "technology", "army", "expansions")
HEAD_WIDTHS = (7, 16, 7, 4)
ACTION_VERSION = "director-action-v0"
MASK_VERSION = "sc2-director-masks-v1"


@dataclass(frozen=True)
class DirectorActionV0:
    objective: int
    target: int
    production: int
    scouting: int

    @property
    def indices(self):
        return (self.objective, self.target, self.production, self.scouting)

    def __post_init__(self):
        if any(
            type(i) is not int or not 0 <= i < width
            for i, width in zip(self.indices, HEAD_WIDTHS, strict=True)
        ):
            raise ValueError("Invalid DirectorActionV0 indices")


@dataclass(frozen=True)
class ActionMasks:
    heads: tuple[tuple[bool, ...], ...]
    active: tuple[bool, ...]

    def __post_init__(self):
        if not isinstance(self.heads, tuple) or not isinstance(self.active, tuple) or len(self.active) != 4:
            raise ValueError("Invalid immutable head masks")
        if len(self.heads) != 4 or any(type(active) is not bool for active in self.active):
            raise ValueError("Invalid head usage")
        for mask, active, width in zip(self.heads, self.active, HEAD_WIDTHS, strict=True):
            if not isinstance(mask, tuple) or len(mask) != width or not any(mask):
                raise ValueError("Invalid or all-masked head")
            if any(type(value) is not bool for value in mask):
                raise ValueError("Masks must contain booleans")
            if not active and mask != (True,) + (False,) * (width - 1):
                raise ValueError("Inactive heads must force index zero")


@dataclass(frozen=True)
class SampledAction:
    action: DirectorActionV0
    masks: ActionMasks
    logits: tuple[float, ...]
    head_log_probabilities: tuple[float, ...]
    log_probability: float
    target_ids: tuple[str | None, ...]
    based_on: int
    sampled_at: float
    action_version: str = ACTION_VERSION
    mask_version: str = MASK_VERSION

    def __post_init__(self):
        if self.action_version != ACTION_VERSION or self.mask_version != MASK_VERSION:
            raise ValueError("Unsupported sampling contract")
        if not isinstance(self.logits, tuple) or not isinstance(self.head_log_probabilities, tuple):
            raise ValueError("Sampling record must be immutable")
        if not isinstance(self.target_ids, tuple) or len(self.target_ids) != 16:
            raise ValueError("Missing sampling-time candidate mapping")
        if any(not self.masks.heads[h][index] for h, index in enumerate(self.action.indices)):
            raise ValueError("Sampled action violates its recorded mask")
        if self.target_ids[self.action.target] is None:
            raise ValueError("Sampled a padded candidate")
        if (
            not isfinite(self.sampled_at)
            or self.sampled_at < 0
            or type(self.based_on) is not int
            or self.based_on < 0
        ):
            raise ValueError("Invalid sampling observation")
        expected = head_log_probabilities(self.logits, self.action, self.masks)
        if (
            len(self.head_log_probabilities) != 4
            or any(
                not isfinite(value) or not isclose(value, correct, abs_tol=1e-10)
                for value, correct in zip(self.head_log_probabilities, expected, strict=True)
            )
            or not isfinite(self.log_probability)
            or not isclose(self.log_probability, sum(expected), abs_tol=1e-10)
        ):
            raise ValueError("Recorded likelihood differs from sampling distribution")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        values = dict(data)
        values["action"] = DirectorActionV0(**values["action"])
        masks = values["masks"]
        values["masks"] = ActionMasks(tuple(tuple(head) for head in masks["heads"]), tuple(masks["active"]))
        for key in ("logits", "head_log_probabilities", "target_ids"):
            values[key] = tuple(values[key])
        return cls(**values)


def split_logits(logits):
    if len(logits) != 34 or any(not isfinite(value) for value in logits):
        raise ValueError("Expected 34 finite logits")
    return (logits[:7], logits[7:23], logits[23:30], logits[30:34])


def categorical(logits, mask):
    """Stable softmax over precisely the allowed actions, with no fallback renormalization."""
    if len(logits) != len(mask) or not any(mask):
        raise ValueError("Invalid categorical mask")
    maximum = max(value for value, allowed in zip(logits, mask, strict=True) if allowed)
    weights = tuple(
        exp(value - maximum) if allowed else 0 for value, allowed in zip(logits, mask, strict=True)
    )
    total = sum(weights)
    return tuple(weight / total for weight in weights)


def draw(logits, mask, rng):
    probabilities = categorical(logits, mask)
    threshold = rng.random()
    cumulative = 0.0
    for index, probability in enumerate(probabilities):
        cumulative += probability
        if probability > 0 and threshold < cumulative:
            return index
    return max(index for index, probability in enumerate(probabilities) if probability > 0)


def head_log_probabilities(logits, action, masks):
    result = []
    for values, index, mask, active in zip(
        split_logits(logits), action.indices, masks.heads, masks.active, strict=True
    ):
        if not mask[index]:
            raise ValueError("Action is masked")
        # Log-softmax avoids log(0) for legal actions with tiny probability.
        maximum = max(value for value, allowed in zip(values, mask, strict=True) if allowed)
        normalizer = log(
            sum(exp(value - maximum) for value, allowed in zip(values, mask, strict=True) if allowed)
        )
        result.append(values[index] - maximum - normalizer if active else 0.0)
    return tuple(result)


def log_probability(logits, sample):
    """Evaluate new logits under the recorded conditional masks, as required by PPO."""
    return sum(head_log_probabilities(logits, sample.action, sample.masks))
