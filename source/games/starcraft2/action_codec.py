"""Offline reference decoder into existing guarded plans; never issues commands."""

from dataclasses import dataclass, replace
from math import floor

from source.game_ontology import unit_roles
from source.games.starcraft2.actions import (
    OBJECTIVES,
    POSTURES,
    QUESTIONS,
    ActionMasks,
    DirectorActionV0,
    SampledAction,
    draw,
    head_log_probabilities,
    split_logits,
)
from source.strategic_plan import StrategicPlan, validate_plan
from source.strategy_policies import Candidate, candidates, compose

DECODER_VERSION = "sc2-director-decoder-v1"
# Preference order is part of the versioned decoder, not a new learned ability permission.
PREFERENCES = (
    (),
    ("zealots",),
    ("stalkers",),
    ("stalkers", "voidrays"),
    ("immortals", "stalkers"),
    ("colossi", "zealots"),
    ("zealots", "stalkers"),
)


def production_template(belief, posture):
    """Transfer at most eight existing target supply; never enable a zero target/caster.

    These are unaccepted prototype templates. Immediate purchases still belong
    to the macro controller and its resource/prerequisite/ownership checks.
    """
    if type(posture) is not int or not 0 <= posture < len(POSTURES):
        raise ValueError("Unsupported production posture")
    state = belief.assessment
    original = dict(state.production)
    if posture == 0 or not belief.permissions.production:
        return state.production, "Keep current production targets"
    roles = {role.name: role for role in unit_roles()}
    recipient = next((name for name in PREFERENCES[posture] if original.get(name, 0) > 0), None)
    if recipient is None:
        return state.production, "No permitted existing recipient"
    donors = sorted(
        (name for name in original if name != recipient and name in roles and original[name] > 0),
        key=lambda name: (-roles[name].supply, name),
    )
    for donor in donors:
        # Retain a small existing ground/ranged screen when reallocating.
        keep = min(original[donor], 4) if donor in {"zealots", "stalkers"} else 0
        available = min(8, (original[donor] - keep) * roles[donor].supply)
        increment = min(200 - original[recipient], floor(available / roles[recipient].supply))
        spent = increment * roles[recipient].supply
        removed = spent / roles[donor].supply
        # Require exact integer conservation; skip a donor requiring rounding up.
        if increment > 0 and removed.is_integer():
            changed = dict(original)
            changed[recipient] += increment
            changed[donor] -= int(removed)
            return tuple(
                changed.items()
            ), f"{POSTURES[posture]}: transfer {spent:g} target supply from {donor} to {recipient}"
    return state.production, "No transferable whole-unit supply within eight-supply cap"


def options(belief):
    state = belief.assessment
    ids = {target.id for target in belief.targets if target is not None}
    bounded = replace(state, targets=tuple(t for t in state.targets if t.id in ids))
    if not belief.permissions.strategy:
        return bounded, [Candidate("develop", "rally", 0, "Strategy permission unavailable")]
    ranked = [choice for choice in candidates(bounded) if choice.target_id in ids]
    urgent = [choice for choice in ranked if choice.objective in {"recover", "stabilize"}]
    if urgent:
        # Current emergency guards can revoke an earlier policy proposal.
        winner = max(urgent, key=lambda choice: choice.score)
        return bounded, [winner]
    return bounded, ranked + [Candidate("recover", "home", 0, "Preserve force at home")]


def objective_mask(belief):
    _, ranked = options(belief)
    return tuple(any(c.objective == name for c in ranked) for name in OBJECTIVES)


def masks_for(belief, objective):
    _, ranked = options(belief)
    objective_masks = objective_mask(belief)
    if not 0 <= objective < 7 or not objective_masks[objective]:
        raise ValueError("Unsupported objective in this observation")
    target_ids = {c.target_id for c in ranked if c.objective == OBJECTIVES[objective]}
    target_mask = tuple(t is not None and t.id in target_ids for t in belief.targets)
    production_mask = (True,) + tuple(
        belief.permissions.production and production_template(belief, i)[0] != belief.assessment.production
        for i in range(1, 7)
    )
    scouting_mask = (True,) * 4 if belief.permissions.scouting else (True, False, False, False)
    return ActionMasks(
        (objective_masks, target_mask, production_mask, scouting_mask),
        (True, True, belief.permissions.production, belief.permissions.scouting),
    )


def sample_action(logits, belief, rng):
    heads = split_logits(logits)
    objective = draw(heads[0], objective_mask(belief), rng)
    masks = masks_for(belief, objective)
    indices = [objective] + [draw(heads[i], masks.heads[i], rng) for i in range(1, 4)]
    action = DirectorActionV0(*indices)
    probabilities = head_log_probabilities(logits, action, masks)
    return SampledAction(
        action,
        masks,
        tuple(logits),
        probabilities,
        sum(probabilities),
        tuple(t.id if t else None for t in belief.targets),
        belief.assessment.version,
        belief.assessment.time,
    )


@dataclass(frozen=True)
class DecodeResult:
    sampled: SampledAction
    plan: StrategicPlan
    override_reasons: tuple[str, ...]
    execution_masks: ActionMasks
    execution_target_ids: tuple[str | None, ...]
    decoder_version: str = DECODER_VERSION

    def to_dict(self):
        return {
            "sampled": self.sampled.to_dict(),
            "plan": self.plan.to_dict(),
            "override_reasons": self.override_reasons,
            "execution_masks": {"heads": self.execution_masks.heads, "active": self.execution_masks.active},
            "execution_target_ids": self.execution_target_ids,
            "decoder_version": self.decoder_version,
        }

    @classmethod
    def from_dict(cls, data):
        from source.strategic_plan import MissionSpec

        plan = dict(data["plan"])
        plan["missions"] = tuple(MissionSpec(**{**m, "target": tuple(m["target"])}) for m in plan["missions"])
        for key in ("production", "scores"):
            plan[key] = tuple(tuple(pair) for pair in plan[key])
        for key in ("scouting_requests", "response_evidence"):
            plan[key] = tuple(plan[key])
        return cls(
            SampledAction.from_dict(data["sampled"]),
            StrategicPlan(**plan),
            tuple(data["override_reasons"]),
            ActionMasks(
                tuple(tuple(h) for h in data["execution_masks"]["heads"]),
                tuple(data["execution_masks"]["active"]),
            ),
            tuple(data["execution_target_ids"]),
            data["decoder_version"],
        )


def decode(sample, belief, plan_id):
    """Revalidate current masks using the sampled full target ID, never a new slot.

    The returned record preserves old masks/likelihood even on a forced fallback.
    Attaching this decoder to the live director requires a separate acceptance.
    """
    state, ranked = options(belief)
    action = sample.action
    reasons = []
    desired = OBJECTIVES[action.objective]
    target_id = sample.target_ids[action.target]
    choice = next((c for c in ranked if (c.objective, c.target_id) == (desired, target_id)), None)
    if not 0 <= state.time - sample.sampled_at <= 5 or sample.based_on > state.version:
        reasons.append("stale_or_future_sample")
    if choice is None:
        reasons.append("objective_or_target_no_longer_legal")
    if not belief.permissions.strategy:
        reasons.append("strategy_permission_unavailable")
    if reasons:
        urgent = [c for c in ranked if c.objective in {"recover", "stabilize"}]
        choice = (
            max(urgent, key=lambda c: c.score)
            if urgent
            else next(c for c in ranked if c.objective == "develop")
        )
    plan = compose(state, choice, plan_id, candidates(state))
    production_index = action.production
    scouting_index = action.scouting
    current_masks = masks_for(belief, OBJECTIVES.index(choice.objective))
    if reasons or not current_masks.heads[2][production_index]:
        if production_index:
            reasons.append("production_fallback_to_current")
        production_index = 0
    if reasons or not current_masks.active[3]:
        if sample.masks.active[3]:
            reasons.append("scouting_request_suppressed")
        scouting = ()
    else:
        scouting = (QUESTIONS[scouting_index],)
    production, production_reason = production_template(belief, production_index)
    main = next(m for m in plan.missions if m.role == "main")
    if (plan.objective, main.target_id) != (desired, target_id):
        reasons.append("existing_mission_rules_projected_primary_intent")
    plan = replace(
        plan,
        production=production,
        production_reason=production_reason,
        scouting_requests=scouting,
        expand=plan.expand and belief.permissions.expansion and belief.permissions.strategy,
        reason=f"{DECODER_VERSION}: {choice.reason}",
    )
    return DecodeResult(
        sample,
        validate_plan(plan, belief.assessment),
        tuple(reasons),
        current_masks,
        tuple(target.id if target else None for target in belief.targets),
    )
