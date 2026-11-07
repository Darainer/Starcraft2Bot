import json
from dataclasses import replace
from math import exp

import pytest
from test_rl_actions import sample
from test_rl_encoding import assessment, settings

from source.games.starcraft2.action_codec import decode
from source.games.starcraft2.encoding import from_assessment
from source.training.records import Outcome, TransitionV1


def transition(reason="running"):
    before = from_assessment(assessment(), settings(), episode_start=True)
    after = from_assessment(assessment(version=2285, time=102), settings(), elapsed_seconds=2)
    sampled = sample(before)
    return TransitionV1(
        episode_id="synthetic-episode",
        decision_index=0,
        policy_id="synthetic-reference",
        before=before,
        decoded=decode(sampled, before, 1),
        after=after,
        recurrent_input=(0.0,) * 256,
        recurrent_output=(0.1,) * 256,
        value_estimate=0.2,
        next_value=0.4 if Outcome(reason).bootstrap else None,
        outcome=Outcome(reason),
    )


@pytest.mark.parametrize(
    "reason,terminated,truncated,reward,bootstrap,eligible",
    [
        ("running", False, False, 0, True, True),
        ("victory", True, False, 1, False, True),
        ("defeat", True, False, -1, False, True),
        ("draw", True, False, 0, False, True),
        ("time_limit", False, True, 0, True, True),
        ("infrastructure_error", False, False, 0, False, False),
        ("aborted", False, False, 0, False, False),
    ],
)
def test_outcomes_do_not_turn_cutoffs_or_failures_into_terminal_losses(
    reason, terminated, truncated, reward, bootstrap, eligible
):
    result = transition(reason)
    assert result.outcome.terminated == terminated
    assert result.outcome.truncated == truncated
    assert result.outcome.reward == reward
    assert result.outcome.bootstrap == bootstrap
    assert result.outcome.learning_eligible == eligible
    data = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    assert data["outcome"]["reward"] == reward
    assert data["decoded"]["sampled"]["log_probability"] == result.decoded.sampled.log_probability
    assert result.discount(120) == exp(-2 / 120)
    assert data["issued_intent_ids"] == data["observed_effect_ids"] == []


@pytest.mark.parametrize(
    "change",
    [
        {"recurrent_input": (1.0,) * 256},
        {"recurrent_output": (0.0,)},
        {"recurrent_input": [0.0] * 256},
        {"value_estimate": float("nan")},
        {"next_value": None},
        {"next_value": float("nan")},
        {"decision_index": 1},
        {"schema_version": "future"},
    ],
)
def test_invalid_sequence_and_value_records_fail_closed(change):
    with pytest.raises(ValueError):
        replace(transition(), **change)


def test_time_limit_bootstraps_final_observation_then_next_episode_resets_memory():
    result = transition("time_limit")
    assert result.next_value == 0.4
    reset = from_assessment(assessment(version=0, time=0), settings(), episode_start=True)
    with pytest.raises(ValueError):
        replace(result, after=reset)
    with pytest.raises(ValueError):
        replace(result, outcome=Outcome("defeat"))
    with pytest.raises(ValueError):
        replace(result, before=replace(result.before, assessment=assessment(version=2241)))
    for invalid in (0, -1, float("inf")):
        with pytest.raises(ValueError):
            result.discount(invalid)


def test_noninitial_sequences_keep_previous_memory_with_explicit_elapsed_time():
    first = transition()
    second_before = first.after
    after = from_assessment(assessment(version=2330, time=104), settings(), elapsed_seconds=2)
    second_sample = sample(second_before)
    second = replace(
        first,
        decision_index=1,
        before=second_before,
        after=after,
        decoded=decode(second_sample, second_before, 2),
        recurrent_input=first.recurrent_output,
    )
    assert second.recurrent_input == first.recurrent_output
    with pytest.raises(ValueError, match="interval"):
        replace(second, after=replace(after, shared=replace(after.shared, elapsed_seconds=1)))


def test_invalid_outcome_is_never_silently_treated_as_draw():
    with pytest.raises(ValueError):
        Outcome("Tie")
