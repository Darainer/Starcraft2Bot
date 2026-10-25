import asyncio
import json
import subprocess
from types import SimpleNamespace

import pytest
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.units import Units

from source import control_cli, runtime
from source.assistant_control import AssistantSettings, Control
from source.local_control import consume_command, queue_command
from source.strategy_profiles import PROFILES
from source.strategy_scripts import run_strategy_script
from source.tactics import TacticalController, TacticalSituation, choose_strategy


@pytest.mark.parametrize("name", PROFILES)
def test_named_profiles_change_setup_and_policy(name, tmp_path):
    control = Control()
    control.command(f"!assist profile {name}")
    assert control.settings.profile == name
    assert control.settings.voidrays == PROFILES[name]["voidrays"]
    assert not control.settings.storm
    state = TacticalSituation(PROFILES[name]["attack_supply"], 10, 1, 0, 10, False)
    assert choose_strategy(state, "auto", PROFILES[name])[0] == "push"
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"profile": name}))
    assert AssistantSettings.load(path).stalkers == PROFILES[name]["stalkers"]
    assert "Rejected" in control.command("!assist profile missing")
    assert control.settings.profile == name


def test_script_path_case_spaces_and_disable():
    control = Control()
    control.command("!assist script C:/My Scripts/Plan.py")
    assert control.settings.strategy_script == "C:/My Scripts/Plan.py"
    control.command("!assist script off")
    assert not control.settings.strategy_script


@pytest.mark.parametrize("script", ["timing_attack", "conservative", "counterattack"])
def test_shipped_scripts_execute_with_real_json_contract(script):
    context = {
        "situation": {
            "army_supply": 60,
            "health_fraction": 1,
            "base_threat": False,
            "nearby_enemy_strength": 0,
            "own_strength": 100,
        },
        "observation": {"observation": {"game_loop": 20000}},
        "previous_strategy": "defend",
    }
    plan = run_strategy_script(f"scripts/strategies/{script}.py", context)
    assert plan["strategy"] == "push"
    assert len(plan["script_sha256"]) == 64
    context["situation"]["base_threat"] = True
    assert run_strategy_script(f"scripts/strategies/{script}.py", context)["strategy"] == "defend"
    context["situation"]["health_fraction"] = 0.1
    assert run_strategy_script(f"scripts/strategies/{script}.py", context)["strategy"] == "retreat"


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"strategy": "auto", "reason": "x"},
        {"strategy": "push", "reason": 1},
        {"strategy": "push", "reason": "x", "arbitrary_action": "bad"},
        {"strategy": "push", "reason": "x", "target": [True, 2]},
    ],
)
def test_invalid_script_output_rejected(tmp_path, payload):
    script = tmp_path / "plan.py"
    script.write_text(f"print({json.dumps(payload)!r})")
    with pytest.raises(ValueError):
        run_strategy_script(script, {})


def test_script_timeout_and_nonpython_rejected(tmp_path):
    script = tmp_path / "slow.py"
    script.write_text("import time; time.sleep(5)")
    with pytest.raises(subprocess.TimeoutExpired):
        run_strategy_script(script, {})
    script = tmp_path / "wrong.txt"
    script.touch()
    with pytest.raises(ValueError):
        run_strategy_script(script, {})


def test_script_plan_goes_through_ownership_and_map_validation(bot, make_unit, populate, tmp_path):
    script = tmp_path / "plan.py"
    script.write_text('print(\'{"strategy":"push","reason":"test","target":[20,20]}\')')
    selected = make_unit(U.STALKER, (10, 10), is_selected=True)
    soldier = make_unit(U.STALKER, (10, 10))
    populate(make_unit(U.NEXUS), soldier, selected)
    bot.settings.attack = True
    bot.settings.strategy_script = str(script)
    bot.supply_army = 20
    bot.enemy_structures = Units([], bot)
    bot.game_info.start_locations = [Point2((100, 100))]
    bot.game_info.playable_area = SimpleNamespace(x=0, y=0, width=100, height=100)
    bot.is_visible = lambda point: False
    controller = TacticalController()
    assert controller.tick(bot)["target"] == [20, 20]
    assert [action.unit.tag for action in bot.actions] == [soldier.tag]
    bot._used.clear()
    bot.actions.clear()
    script.write_text('print(\'{"strategy":"push","reason":"test","target":[200,200]}\')')
    assert controller.tick(bot)["strategy"] == "manual"
    assert not bot.actions
    script.write_text("raise RuntimeError('broken strategy')")
    assert "rejected" in controller.tick(bot)["reason"]
    assert not bot.actions


def test_mailbox_acknowledgement_and_cli_state(tmp_path, capsys):
    report = tmp_path / "runtime.json"
    report.write_text(json.dumps({"phase": "observing", "local_control": True}))
    control_cli.main(["--report", str(report), "strategy", "push"])
    assert "Queued" in capsys.readouterr().out
    with pytest.raises(FileExistsError):
        queue_command(report, "!assist pause")
    control = Control()
    assert "RUNNING" in consume_command(report, control, [])["reply"]
    assert control.settings.strategy == "push"
    assert consume_command(report, control, []) is None
    report.with_suffix(".state.jsonl").write_text('{"game_loop":1}\n{"game_loop":2}\n')
    control_cli.main(["--report", str(report), "--state"])
    assert json.loads(capsys.readouterr().out)["game_loop"] == 2
    control_cli.main(["--report", str(report)])
    assert json.loads(capsys.readouterr().out)["phase"] == "observing"
    report.with_suffix(".command.json").write_text("not JSON")
    assert "Rejected" in consume_command(report, control, [])["reply"]
    report.write_text('{"phase":"ended"}')
    with pytest.raises(ValueError):
        queue_command(report, "!assist resume")


def test_mailbox_rejects_legacy_sessions_invalid_input_and_cli_missing_state(tmp_path):
    report = tmp_path / "runtime.json"
    report.write_text('{"phase":"observing"}')
    with pytest.raises(ValueError, match="predates"):
        queue_command(report, "!assist resume")
    report.write_text('{"phase":"observing","local_control":true}')
    with pytest.raises(ValueError):
        queue_command(report, "random text")
    with pytest.raises(SystemExit):
        control_cli.main(["--report", str(report), "--state"])


def test_runtime_applies_mailbox_before_step(monkeypatch, tmp_path):
    from unittest.mock import AsyncMock

    from source.economy_assistant import EconomyAssistant

    path = tmp_path / "runtime.json"
    path.write_text('{"phase":"observing","local_control":true}')
    updates = []
    report = SimpleNamespace(path=path, update=lambda **kw: updates.append(kw))
    bot = runtime.RuntimeAssistant(AssistantSettings(enabled=False), report)
    bot.state = SimpleNamespace(game_loop=1)
    monkeypatch.setattr(EconomyAssistant, "on_step", AsyncMock())
    queue_command(path, "!assist resume")
    asyncio.run(bot.on_step(0))
    assert bot.settings.enabled
    assert updates[0]["last_control_command"]["command"] == "!assist resume"
