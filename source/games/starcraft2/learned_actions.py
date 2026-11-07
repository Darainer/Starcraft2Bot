"""Independent strategy/economy contract; no rule-policy candidate generation.

The actor chooses movement intent, a player-view target, one immediate paid
macro action, and gas staffing per extractor. Placement, actor selection and
unit micro are fixed execution skills. No automatic opening or spending runs.
"""

from dataclasses import dataclass

from source.games.starcraft2.action_codec import DecodeResult
from source.games.starcraft2.actions import (
    ActionMasks,
    SampledAction,
    draw,
    head_log_probabilities,
    split_logits,
)
from source.strategic_plan import MissionSpec, StrategicPlan, validate_plan

ACTION_VERSION = "strategy-economy-action-v1"
MASK_VERSION = "sc2-mechanical-masks-v1"
DECODER_VERSION = "sc2-strategy-economy-decoder-v1"
FEATURE_VERSION = "sc2-strategy-economy-features-v1"
EXECUTOR_VERSION = "sc2-placement-allocation-micro-v1"
INTENTS = ("hold", "move", "attack")
# Append-only within this contract. New meanings/order require a new version.
MACRO_ACTIONS = (
    "wait",
    "probe",
    "pylon",
    "assimilator",
    "nexus",
    "gateway",
    "cybernetics_core",
    "robotics_facility",
    "robotics_bay",
    "stargate",
    "forge",
    "twilight_council",
    "templar_archive",
    "zealot",
    "stalker",
    "sentry",
    "immortal",
    "colossus",
    "voidray",
    "high_templar",
    "observer",
    "ground_weapons_1",
    "ground_armor_1",
    "shields_1",
    "air_weapons_1",
    "air_armor_1",
    "blink",
    "charge",
    "thermal_lance",
    "storm",
)
HEAD_WIDTHS = (3, 16, len(MACRO_ACTIONS), 4)


@dataclass(frozen=True)
class LearnedAction:
    intent: int
    target: int
    macro: int
    gas: int

    @property
    def indices(self):
        return (self.intent, self.target, self.macro, self.gas)

    def __post_init__(self):
        if any(type(i) is not int or not 0 <= i < w for i, w in zip(self.indices, HEAD_WIDTHS, strict=True)):
            raise ValueError("Invalid strategy/economy action indices")


@dataclass(frozen=True)
class LearnedMasks(ActionMasks):
    widths = HEAD_WIDTHS


@dataclass(frozen=True)
class LearnedSample(SampledAction):
    action_version: str = ACTION_VERSION
    mask_version: str = MASK_VERSION
    contract_action_version = ACTION_VERSION
    contract_mask_version = MASK_VERSION
    action_type = LearnedAction
    masks_type = LearnedMasks


def masks_for(belief, intent):
    if len(belief.macro_mask) != len(MACRO_ACTIONS) or belief.macro_mask[0] is not True:
        raise ValueError("Independent policy requires a complete mechanical macro mask")
    strategy = belief.permissions.strategy
    allocation = dict(belief.shared.capabilities).get("resource_allocation", strategy)
    intents = (True, strategy, strategy)
    if type(intent) is not int or not 0 <= intent < 3 or not intents[intent]:
        raise ValueError("Unsupported movement intent")
    targets = tuple(t is not None for t in belief.targets) if intent else (True,) + (False,) * 15
    return LearnedMasks(
        (intents, targets, belief.macro_mask, (True,) * 4 if allocation else (True, False, False, False)),
        (True, bool(intent), True, allocation),
    )


def sample_action(logits, belief, rng):
    heads = split_logits(logits, HEAD_WIDTHS)
    intent = draw(heads[0], masks_for(belief, 0).heads[0], rng)
    masks = masks_for(belief, intent)
    action = LearnedAction(intent, *(draw(heads[h], masks.heads[h], rng) for h in range(1, 4)))
    probabilities = head_log_probabilities(logits, action, masks)
    return LearnedSample(
        action,
        masks,
        tuple(logits),
        probabilities,
        sum(probabilities),
        tuple(t.id if t else None for t in belief.targets),
        belief.assessment.version,
        belief.assessment.time,
    )


def decode(sample, belief, plan_id):
    if not isinstance(sample, LearnedSample) or belief.shared.feature_version != FEATURE_VERSION:
        raise ValueError("Independent decoder rejects other action/feature contracts")
    state, action = belief.assessment, sample.action
    reasons = []
    current = masks_for(belief, action.intent if belief.permissions.strategy else 0)
    target_id = sample.target_ids[action.target]
    target = next((t for t in belief.targets if t is not None and t.id == target_id), None)
    if not 0 <= state.time - sample.sampled_at <= 5 or sample.based_on > state.version:
        reasons.append("stale_or_future_sample")
    if target is None:
        reasons.append("target_no_longer_supported")
    if action.intent and not belief.permissions.strategy:
        reasons.append("strategy_permission_unavailable")
    if not current.heads[2][action.macro]:
        reasons.append("macro_no_longer_available")
    # Hold has no army order. A failed macro is skipped rather than substituted
    # with another spending decision. Sampling masks/likelihood remain intact.
    intent = 0 if reasons else action.intent
    target = belief.targets[0] if target is None else target
    objective = "pressure" if intent == 2 else "develop"
    mission = MissionSpec(
        "main",
        "main",
        target.id,
        target.position,
        state.army_supply,
        0,
        50,
        "attack" if intent == 2 else "move",
    )
    plan = StrategicPlan(
        plan_id,
        state.version,
        state.time,
        state.time + 5,
        objective,
        (mission,),
        state.production,
        not reasons and MACRO_ACTIONS[action.macro] == "nexus",
        f"{DECODER_VERSION}: {INTENTS[intent]}; {MACRO_ACTIONS[action.macro]}; gas={action.gas}",
        production_reason="Explicit sampled macro action; profile composition is not executed",
    )
    return DecodeResult(
        sample,
        validate_plan(plan, state),
        tuple(reasons),
        current,
        tuple(t.id if t else None for t in belief.targets),
        DECODER_VERSION,
    )
