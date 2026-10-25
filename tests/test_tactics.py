import json
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from s2clientprotocol import sc2api_pb2 as pb
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source import runtime
from source.assistant_control import AssistantSettings, Control
from source.economy_assistant import EconomyAssistant
from source.tactics import TacticalController, TacticalSituation, choose_strategy


@pytest.mark.parametrize(
    "changes,expected",
    [
        ({"army_count": 0}, "regroup"),
        ({"health_fraction": 0.2}, "retreat"),
        ({"nearby_enemy_strength": 200}, "retreat"),
        ({"base_threat": True}, "defend"),
        ({"army_supply": 25}, "push"),
        ({"army_supply": 15, "previous": "push"}, "push"),
        ({"army_supply": 10, "previous": "push"}, "regroup"),
    ],
)
def test_auto_policy_priorities_and_attack_hysteresis(changes, expected):
    state = TacticalSituation(15, 8, 0.9, 10, 100, False)
    assert choose_strategy(replace(state, **changes), "auto")[0] == expected
    assert choose_strategy(state, "retreat")[0] == "retreat"


def test_strategy_chat_validation_is_atomic():
    control = Control()
    control.command("!assist attack on")
    control.command("!assist strategy push")
    assert control.settings.attack and control.settings.strategy == "push"
    assert control.command("!assist strategy nonexistent").startswith("Rejected")
    assert control.settings.strategy == "push"
    with pytest.raises(ValueError):
        AssistantSettings(strategy="nonexistent").validate()


def prepare(bot, populate, make_unit):
    base = make_unit(U.NEXUS)
    soldier = make_unit(U.STALKER, (10, 10))
    selected = make_unit(U.STALKER, (11, 10), is_selected=True)
    released = make_unit(U.STALKER, (12, 10))
    populate(base, soldier, selected, released, make_unit(U.PROBE))
    bot.control.released.add(released.tag)
    bot.enemy_structures = Units([], bot)
    bot.game_info.start_locations = [Point2((100, 100))]
    bot.supply_army = 25
    bot.is_visible = lambda point: False
    bot.settings.attack = True
    bot.settings.strategy = "push"
    return soldier


def test_attack_respects_selection_release_and_worker_ownership(bot, populate, make_unit):
    soldier = prepare(bot, populate, make_unit)
    decision = TacticalController().tick(bot)
    assert decision["strategy"] == "push"
    assert [action.unit.tag for action in bot.actions] == [soldier.tag]
    assert decision["orders"] == [{"unit_tag": soldier.tag, "action": "attack"}]
    assert bot.actions[0].target == Point2((100, 100))


@pytest.mark.parametrize("switch", ["attack", "enabled"])
def test_pause_and_attack_off_issue_no_orders(bot, populate, make_unit, switch):
    prepare(bot, populate, make_unit)
    setattr(bot.settings, switch, False)
    assert TacticalController().tick(bot)["strategy"] == "manual"
    assert not bot.actions


def test_retreat_uses_move_towards_home(bot, populate, make_unit):
    prepare(bot, populate, make_unit)
    bot.settings.strategy = "retreat"
    decision = TacticalController().tick(bot)
    assert decision["orders"][0]["action"] == "move"
    assert bot.actions[0].target == bot.start_location


def test_snapshot_interval_and_raw_observation_roundtrip(monkeypatch, tmp_path):
    report = SimpleNamespace(path=tmp_path / "runtime.json", update=lambda **kwargs: None)
    bot = runtime.RuntimeAssistant(AssistantSettings(), report)
    response = pb.ResponseObservation(observation=pb.Observation(game_loop=224))
    response.observation.player_common.minerals = 123
    response.observation.raw_data.units.add(tag=9999999999999, unit_type=84)
    bot.state = SimpleNamespace(game_loop=224, response_observation=response)
    bot.tactics = SimpleNamespace(tick=lambda bot, **kwargs: {"strategy": "regroup", "reason": "test"})
    monkeypatch.setattr(EconomyAssistant, "on_step", AsyncMock())
    clock = iter([0, 4.9, 5.0])
    monkeypatch.setattr(runtime.time, "monotonic", lambda: next(clock))
    # Call the coroutine directly: replacing process-wide monotonic would
    # otherwise also affect asyncio's event-loop clock.
    for index in range(3):
        coroutine = bot.on_step(index)
        with pytest.raises(StopIteration):
            coroutine.send(None)
    lines = report.path.with_suffix(".state.jsonl").read_text().splitlines()
    assert len(lines) == 2
    row = json.loads(lines[0])
    assert row["observation"]["observation"]["player_common"]["minerals"] == 123
    assert row["observation"]["observation"]["raw_data"]["units"][0]["tag"] == "9999999999999"
    assert row["decision"]["strategy"] == "regroup"
