import json

from test_remote_raid import facts

from source.replay_strategy import assessment_from_dict
from source.strategic_plan import validate_plan
from source.strategy_director import StrategicDirector


def test_serialized_opening_hold_preserves_raid_evidence_and_emergency_full_defense():
    state = facts(rush_warning=True, rally=(3.5, 0), opening_hold=(3.5, 0))
    restored = assessment_from_dict(json.loads(json.dumps(state.to_dict())))
    plan = validate_plan(StrategicDirector().decide(restored), restored)
    assert restored.raid_response_schema_version == 1
    assert tuple(restored.raid_response_tags) == state.raid_response_tags
    assert len(plan.missions) == 1
    assert plan.missions[0].target == restored.rally
    assert plan.missions[0].supply_budget == state.army_supply


def test_serialized_remote_raid_response_remains_bounded_after_opening_hold_clears():
    state = facts(opening_hold=None)
    restored = assessment_from_dict(json.loads(json.dumps(state.to_dict())))
    plan = validate_plan(StrategicDirector().decide(restored), restored)
    assert [(mission.role, mission.supply_budget) for mission in plan.missions] == [
        ("defend", 8),
        ("main", 134),
    ]
