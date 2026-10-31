import copy
import json

import pytest
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId

from source.strategy_review import counter_response, main, review_recordings, review_rows


def sample(seconds=100, air=10, armor=0):
    return {
        "game_loop": seconds * 22.4,
        "settings": {"enabled": True, "attack": True, "max_workers": 56},
        "scouting": {
            "intel": {
                "visible_enemy_force": {
                    "seen_seconds": seconds,
                    "supply": 10,
                    "air_supply": air,
                    "armored_ground_supply": armor,
                }
            }
        },
        "decision": {"plan": {"production": [["zealots", 5]]}},
        "observation": {"observation": {"raw_data": {"units": []}}},
    }


def unit(kind, tag, **values):
    return {
        "unit_type": kind.value,
        "tag": str(tag),
        "alliance": "Self",
        "build_progress": 1,
        "health": 100,
        **values,
    }


def test_air_response_scores_suitable_targets_and_observed_delivery_separately():
    row = sample()
    assert counter_response(row)["planned_role_fit"] == 0
    row["decision"]["plan"]["production"] = [["stalkers", 5]]
    score = counter_response(row)
    assert score["planned_role_fit"] == 1
    assert score["delivered_role_readiness"] == score["ready_tech_target_fraction"] == 0
    row["observation"]["observation"]["raw_data"]["units"] = [unit(U.STALKER, i) for i in range(5)] + [
        unit(U.CYBERNETICSCORE, 20),
        unit(U.GATEWAY, 21),
    ]
    assert counter_response(row)["delivered_role_readiness"] == 1
    assert counter_response(row)["ready_tech_target_fraction"] == 1
    row["decision"]["plan"]["production"] = [["stalkers", 100]]
    assert counter_response(row)["target_budget_feasible"] == 0


def test_readiness_excludes_selected_released_hallucinated_and_unfinished_units():
    row = sample()
    row["decision"]["plan"]["production"] = [["stalkers", 5]]
    row["released_unit_tags"] = [2]
    row["observation"]["observation"]["raw_data"]["units"] = [
        unit(U.STALKER, 1, is_selected=True),
        unit(U.STALKER, 2),
        unit(U.STALKER, 3, is_hallucination=True),
        unit(U.STALKER, 4, build_progress=0.9),
        unit(U.STALKER, 5),
    ]
    assert counter_response(row)["delivered_role_readiness"] == pytest.approx(0.2)
    row["settings"]["enabled"] = False
    assert counter_response(row)["delivered_role_readiness"] == 0


def test_spell_role_requires_opt_in_research_and_energy():
    row = sample(air=0)
    row["decision"]["plan"]["production"] = [["high_templar", 5]]
    raw = row["observation"]["observation"]["raw_data"]
    raw["units"] = [unit(U.HIGHTEMPLAR, i, energy=100) for i in range(5)]
    assert counter_response(row)["delivered_role_readiness"] == 0
    row["settings"]["storm"] = True
    assert counter_response(row)["delivered_role_readiness"] == 0
    raw["player"] = {"upgrade_ids": [UpgradeId.PSISTORMTECH.value]}
    raw["units"][0]["energy"] = 20
    assert counter_response(row)["delivered_role_readiness"] == pytest.approx(0.8)


def test_fog_and_future_observations_do_not_supply_a_response_denominator():
    row = sample()
    for seen in (0, 200):
        row["scouting"]["intel"]["visible_enemy_force"]["seen_seconds"] = seen
        assert counter_response(row) is None
    del row["scouting"]["intel"]["visible_enemy_force"]
    assert counter_response(row) is None


def test_time_weighting_uses_previous_sample_and_reports_evidence_coverage():
    first, middle, last = sample(0), sample(10), sample(30)
    first["scouting"]["intel"] = {}
    middle["decision"]["plan"]["production"] = [["stalkers", 5]]
    result = review_rows([first, middle, last], "Rush")
    assert result["time_weighted"]["response_evidence_coverage"] == pytest.approx(2 / 3)
    assert result["time_weighted"]["planned_role_fit"] == 1
    assert result["metric_observed_seconds"]["planned_role_fit"] == pytest.approx(20)
    assert result["metric_observed_seconds"]["strategy_accuracy"] == pytest.approx(30)
    with pytest.raises(ValueError, match="ordered"):
        review_rows([last, first])


def test_all_repeats_contribute_before_scenario_average_and_cli(tmp_path):
    paths = []
    for i, (race, fit) in enumerate([("Zerg", 1), ("Zerg", 0), ("Terran", 1)]):
        path = tmp_path / f"{i}.json"
        path.write_text(
            json.dumps(
                {"phase": "ended", "result": "Result.Victory", "opponent_race": race, "opponent_build": "Air"}
            )
        )
        row = sample(0)
        if fit:
            row["decision"]["plan"]["production"] = [["stalkers", 5]]
        later = copy.deepcopy(row)
        later["game_loop"] = 224
        path.with_suffix(".state.jsonl").write_text("\n".join(json.dumps(r) for r in (row, later)))
        paths.append(path)
    result = review_recordings(paths)
    assert result["scenario_mean"]["planned_role_fit"] == 0.75
    assert sorted(s["repeats"] for s in result["scenarios"]) == [1, 2]
    output = tmp_path / "review.json"
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps([{"report": str(p)} for p in paths]))
    main(["--matrix", str(matrix), "--output", str(output)])
    assert json.loads(output.read_text())["scenario_mean"] == result["scenario_mean"]
