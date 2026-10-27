from sc2.ids.unit_typeid import UnitTypeId as U

from source.session_review import SessionReview


def row(time, loss=0, kills=0, target="base", point=(100, 0), phase="advance", objective="pressure"):
    return {
        "game_loop": time * 22.4,
        "decision": {
            "plan": {
                "objective": objective,
                "missions": [{"role": "main", "target_id": target, "target": list(point)}],
            },
            "wave": {"id": 1, "phase": phase},
        },
        "observation": {
            "observation": {
                "score": {
                    "score_details": {
                        "lost_minerals": {"army": loss},
                        "killed_minerals": {"army": kills},
                    }
                }
            }
        },
    }


def test_trade_rebound_is_not_counted_twice_and_windows_are_auditable():
    review = SessionReview()
    for sample in (row(0), row(5, 1100, 100), row(20, 750, 100), row(25, 1100, 100), row(35, 1500, 150)):
        review.observe(sample)
    result = review.summary()
    assert result["resource_scores"]["lost_army"] == 1500
    assert result["bad_trade_window_count"] == 2
    assert [(w["start"], w["lost_army"]) for w in result["worst_trade_windows"]] == [(0, 1100), (30, 400)]
    assert result["worst_trade_windows"][0]["targets"] == ["base"]
    assert result["army_trade_ratio"] == 0.1
    assert result["first_bad_trade_window"]["start"] == 0


def test_target_reversals_exclude_emergency_handoffs_and_same_position_ids():
    review = SessionReview()
    for sample in (
        row(0),
        row(5, target="other", point=(-100, 0), phase="regroup"),
        row(10),
        row(15, target="home", point=(0, 0), objective="recover"),
        row(20, target="other", point=(-100, 0)),
        row(25, target="renamed", point=(-100, 0)),
    ):
        review.observe(sample)
    movement = review.summary()["movement"]
    assert movement["offensive_target_switches"] == 2
    assert movement["short_target_reversals"] == 1
    assert movement["advance_regroup_transitions"] == 0  # Different targets, not cohesion chatter.


def test_long_order_reversal_ignores_short_kiting_and_tracks_cohesion_chatter():
    review = SessionReview()
    for time, point, phase in ((0, [20, 0], "advance"), (5, [-20, 0], "regroup"), (10, [2, 0], "advance")):
        sample = row(time, phase=phase)
        sample["observation"]["observation"]["raw_data"] = {
            "units": [{"alliance": "Self", "tag": "1", "pos": {"x": 0, "y": 0}}]
        }
        sample["decision"]["orders"] = [{"unit_tag": 1, "target": point}]
        sample["decision"]["wave"]["cohesion_fraction"] = 1.1 if time == 0 else 1
        review.observe(sample)
    movement = review.summary()["movement"]
    assert movement["sampled_long_move_orders"] == 2
    assert movement["sampled_long_move_reversals"] == 1
    assert movement["advance_regroup_transitions"] == 2
    assert movement["invalid_cohesion_samples"] == 1


def test_transport_loading_is_not_a_casualty_and_real_disappearance_corroborates_loss():
    review = SessionReview()
    soldier = {"alliance": "Self", "tag": "1", "unit_type": U.STALKER.value}
    carrier = {"alliance": "Self", "tag": "2", "unit_type": U.WARPPRISM.value}
    for time, loss, units in (
        (0, 0, [soldier, carrier]),
        (5, 0, [{**carrier, "passengers": [soldier]}]),
        (20, 400, [carrier]),
    ):
        sample = row(time, loss)
        sample["observation"]["observation"]["raw_data"] = {"units": units}
        sample["decision"]["assessment"] = {"local_advantage": 0.5, "health": 0.4}
        review.observe(sample)
    result = review.summary()
    assert result["bad_trade_window_count"] == result["corroborated_bad_trade_window_count"] == 1
    assert result["worst_trade_windows"][0]["own_army_disappearances"] == {"STALKER": 1}
    assert result["worst_trade_windows"][0]["local_advantage_min"] == 0.5


def test_worker_and_base_losses_are_reported_without_large_army_losses():
    review = SessionReview()
    first = row(0)
    first["observation"]["observation"]["raw_data"] = {
        "units": [{"alliance": "Self", "tag": "1", "unit_type": U.NEXUS.value}]
    }
    review.observe(first)
    second = row(5)
    second["observation"]["observation"]["score"]["score_details"]["lost_minerals"]["economy"] = 400
    review.observe(second)
    result = review.summary()
    assert result["bad_trade_window_count"] == 0
    assert result["worst_economy_loss_windows"][0]["own_economy_disappearances"] == {"NEXUS": 1}


def test_early_worker_losses_exclude_loading_and_losses_after_the_horizon():
    review = SessionReview()
    workers = [{"alliance": "Self", "tag": str(i), "unit_type": U.PROBE.value} for i in range(3)]
    prism = {"alliance": "Self", "tag": "prism", "unit_type": U.WARPPRISM.value}
    for time, units in (
        (0, workers + [prism]),
        (100, [{**prism, "passengers": workers}]),
        (120, workers + [prism]),
        (150, workers[1:] + [prism]),  # A gas harvester temporarily leaves raw vision.
        (155, workers + [prism]),
        (240, workers[1:] + [prism]),
        (245, [prism]),
    ):
        sample = row(time)
        sample["observation"]["observation"]["raw_data"] = {"units": units}
        review.observe(sample)
    result = review.summary()
    assert result["worker_disappearances_by_240_seconds"] == 1
    assert result["first_worker_disappearance_seconds"] == 240
    assert result["first_bad_trade_window"] is None
