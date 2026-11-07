import json
import random
from dataclasses import replace
from math import log

import pytest
from test_rl_encoding import assessment, settings

from source.game_ontology import unit_roles
from source.games.starcraft2.action_codec import decode, masks_for, production_template, sample_action
from source.games.starcraft2.actions import (
    OBJECTIVES,
    ActionMasks,
    DirectorActionV0,
    SampledAction,
    categorical,
    head_log_probabilities,
    log_probability,
)
from source.games.starcraft2.encoding import from_assessment
from source.strategic_plan import validate_plan


def sample(belief, *, objective="pressure", production=0, scouting=0, target=3):
    masks = masks_for(belief, OBJECTIVES.index(objective))
    action = DirectorActionV0(OBJECTIVES.index(objective), target, production, scouting)
    logits = (0.0,) * 34
    probabilities = head_log_probabilities(logits, action, masks)
    return SampledAction(
        action,
        masks,
        logits,
        probabilities,
        sum(probabilities),
        tuple(t.id if t else None for t in belief.targets),
        belief.assessment.version,
        belief.assessment.time,
    )


def test_34_logits_sample_four_indices_with_conditional_masks_and_exact_likelihood():
    belief = from_assessment(assessment(), settings())
    first = sample_action([0.0] * 34, belief, random.Random(42))
    assert first == sample_action([0.0] * 34, belief, random.Random(42))
    assert len(first.action.indices) == 4
    assert first.log_probability == log_probability(first.logits, first)
    assert first.log_probability == pytest.approx(
        sum(
            -log(sum(mask))
            for mask, active in zip(first.masks.heads, first.masks.active, strict=True)
            if active
        )
    )
    assert len(json.loads(json.dumps(first.to_dict()))["logits"]) == 34
    assert SampledAction.from_dict(json.loads(json.dumps(first.to_dict()))) == first
    for seed in range(40):
        result = sample_action([0.0] * 34, belief, random.Random(seed))
        if OBJECTIVES[result.action.objective] == "recover":
            assert result.action.target == 0
            assert result.head_log_probabilities[1] == 0
        assert all(mask[index] for mask, index in zip(result.masks.heads, result.action.indices, strict=True))


def test_inactive_heads_and_forced_targets_contribute_zero():
    belief = from_assessment(assessment(targets=()), settings(enabled=False))
    result = sample_action([1000.0] * 34, belief, random.Random(1))
    assert result.action.indices == (0, 1, 0, 0)
    assert result.masks.active == (True, True, False, False)
    assert result.log_probability == 0
    assert result.head_log_probabilities == (0, 0, 0, 0)
    decoded = decode(result, belief, 1)
    assert not decoded.plan.expand and not decoded.plan.scouting_requests
    assert decoded.plan.missions[-1].mode == "move"


def test_masked_logits_and_extreme_values_do_not_change_legal_distribution():
    assert categorical((1000, -1000, 0), (False, True, True)) == (0, 0, 1)
    belief = from_assessment(assessment(), settings())
    recorded = sample(belief, objective="recover", target=0)
    changed = list(recorded.logits)
    changed[7 + 3] = 1e6  # Masked economic target under recovery.
    assert log_probability(changed, recorded) == recorded.log_probability
    changed[7] = -1e6  # Forced home still has probability one.
    assert log_probability(changed, recorded) == recorded.log_probability
    changed[0] = -1000  # The sampled recover objective remains finite.
    assert log_probability(changed, recorded) <= 0


@pytest.mark.parametrize("invalid", [[], [0] * 33, [0] * 35, [float("nan")] * 34, [float("inf")] * 34])
def test_invalid_logits_fail_closed(invalid):
    with pytest.raises(ValueError):
        sample_action(invalid, from_assessment(assessment(), settings()), random.Random(0))


def test_invalid_actions_masks_and_tampered_likelihoods_are_rejected():
    belief = from_assessment(assessment(), settings())
    recorded = sample(belief)
    with pytest.raises(ValueError):
        DirectorActionV0(7, 0, 0, 0)
    with pytest.raises(ValueError):
        DirectorActionV0(True, 0, 0, 0)
    with pytest.raises(ValueError, match="all-masked"):
        ActionMasks(((False,) * 7,) + recorded.masks.heads[1:], recorded.masks.active)
    with pytest.raises(ValueError, match="Inactive"):
        ActionMasks(recorded.masks.heads, (True, True, False, True))
    with pytest.raises(ValueError, match="likelihood"):
        replace(recorded, log_probability=123)
    with pytest.raises(ValueError, match="mask"):
        replace(recorded, action=replace(recorded.action, target=2))


def test_all_postures_conserve_supply_keep_permissions_and_do_not_compound():
    belief = from_assessment(assessment(), settings())
    supply = {role.name: role.supply for role in unit_roles()}
    original = dict(belief.assessment.production)
    total = sum(supply[name] * count for name, count in original.items())
    for posture in range(7):
        targets, reason = production_template(belief, posture)
        assert production_template(belief, posture)[0] == targets
        assert reason
        assert sum(supply[name] * count for name, count in targets) == total
        assert dict(targets)["high_templar"] == 0
        assert all(type(count) is int and 0 <= count <= 200 for _, count in targets)
        transferred = sum(max(0, count - original[name]) * supply[name] for name, count in targets)
        assert transferred <= 8
    assert dict(belief.assessment.production) == original
    disabled = from_assessment(assessment(), settings(production=False))
    assert production_template(disabled, 3)[0] == disabled.assessment.production
    assert masks_for(disabled, 3).heads[2] == (True, False, False, False, False, False, False)


def test_no_whole_unit_transfer_does_not_round_or_enable_new_units():
    belief = from_assessment(
        assessment(production=(("stalkers", 4), ("zealots", 4), ("colossi", 0))), settings()
    )
    assert production_template(belief, 5)[0] == belief.assessment.production
    capped = from_assessment(assessment(production=(("stalkers", 200), ("zealots", 12))), settings())
    assert production_template(capped, 2)[0] == capped.assessment.production


def test_decode_retains_rule_mission_allocation_and_validates_guarded_plan():
    base = assessment()
    extra = replace(base.targets[0], id="third", position=(60, 60), value=60)
    belief = from_assessment(replace(base, targets=base.targets + (extra,)), settings())
    original = sample(belief, production=3, scouting=1)
    decoded = decode(original, belief, 7)
    assert validate_plan(decoded.plan, belief.assessment) is decoded.plan
    assert decoded.sampled is original and not decoded.override_reasons
    assert decoded.plan.objective == "pressure"
    assert {mission.role for mission in decoded.plan.missions} == {"main", "deny"}
    assert sum(m.supply_budget for m in decoded.plan.missions) == belief.assessment.army_supply
    assert decoded.plan.scouting_requests == ("technology",)
    assert decoded.plan.response_policy == base.response_policy
    assert dict(decoded.plan.production)["high_templar"] == 0


def test_execution_uses_sampled_identity_when_candidate_order_changes():
    base = assessment()
    extra = replace(base.targets[0], id="third", position=(60, 60), value=60)
    before = from_assessment(replace(base, targets=base.targets + (extra,)), settings())
    original = sample(before)
    newer = replace(base, version=2241, time=101, targets=(replace(extra, value=99), base.targets[0]))
    current = from_assessment(newer, settings())
    assert current.targets[3].id == "third"
    decoded = decode(original, current, 2)
    assert next(m for m in decoded.plan.missions if m.role == "main").target_id == "natural"
    assert not decoded.override_reasons


@pytest.mark.parametrize(
    "change",
    [
        {"targets": ()},
        {"time": 106},
        {"version": 2239},
        {"health": 0.2},
        {"rush_warning": True},
    ],
)
def test_stale_missing_or_emergency_actions_preserve_old_likelihood_and_fallback(change):
    before = from_assessment(assessment(), settings())
    recorded = sample(before, production=3, scouting=1)
    current = from_assessment(assessment(**change), settings())
    result = decode(recorded, current, 2)
    assert result.sampled is recorded
    assert result.sampled.log_probability == log_probability(recorded.logits, recorded)
    assert result.override_reasons
    assert result.plan.objective in {"develop", "stabilize", "recover"}
    assert not result.plan.scouting_requests
    assert result.plan.production == current.assessment.production
    assert validate_plan(result.plan, current.assessment) is result.plan


def test_permission_revocation_suppresses_production_scouting_and_expansion():
    base = assessment()
    before = from_assessment(base, settings())
    recorded = sample(before, production=3, scouting=1)
    current = from_assessment(base, settings(production=False, scouting=False, expansion=False))
    result = decode(recorded, current, 2)
    assert result.plan.production == base.production
    assert not result.plan.scouting_requests and not result.plan.expand
    assert "production_fallback_to_current" in result.override_reasons
    assert result.execution_masks.active[2:] == (False, False)
    assert recorded.masks.active[2:] == (True, True)
    assert result.sampled.log_probability == recorded.log_probability


def test_every_sampled_action_decodes_across_safety_scenarios():
    scenarios = [
        assessment(),
        assessment(targets=()),
        assessment(army_supply=0, army_count=0),
        assessment(threat_supply=30, threat=(4, 4)),
        assessment(health=0.1),
        assessment(rush_warning=True),
        assessment(recently_defended=True),
        assessment(local_advantage=4, cleanup_ready=True),
    ]
    for state in scenarios:
        belief = from_assessment(state, settings())
        for seed in range(15):
            recorded = sample_action([0.0] * 34, belief, random.Random(seed))
            result = decode(recorded, belief, seed)
            assert validate_plan(result.plan, state) is result.plan
            assert sum(m.supply_budget for m in result.plan.missions) <= state.army_supply
