from dataclasses import asdict
from types import SimpleNamespace

import pytest

from source.assistant_control import COMBAT_POWERS, ECONOMY, AssistantSettings, Control, within_budget


def test_default_ownership():
    c = Control()
    assert all(getattr(c.settings, name) for name in ECONOMY)
    assert not any(getattr(c.settings, name) for name in COMBAT_POWERS)
    assert c.settings.chrono


@pytest.mark.parametrize("name", ECONOMY + COMBAT_POWERS + ("chrono", "hud"))
def test_independent_toggles(name):
    c = Control()
    before = asdict(c.settings)
    c.command(f"!assist {name} off")
    assert not getattr(c.settings, name)
    c.command(f"!assist {name} on")
    assert getattr(c.settings, name)
    assert {k: v for k, v in asdict(c.settings).items() if k != name} == {
        k: v for k, v in before.items() if k != name
    }


def test_group_toggles_and_pause_preserve_choices():
    c = Control()
    c.command("!assist spells on")
    c.command("!assist economy off")
    c.command("!assist pause")
    assert not c.settings.enabled
    assert c.settings.storm and c.settings.chrono
    assert not c.settings.workers
    c.command("!assist resume")
    assert c.settings.enabled and not c.settings.workers


@pytest.mark.parametrize(
    "command",
    [
        "!assist reserve 300 nope",
        "!assist reserve -1 5",
        "!assist set bases 0",
        "!assist set enabled 1",
        "!assist set stalkers 201",
        "!assist reserve 10001 0",
        "!assist missing on",
        "!assist storm maybe",
    ],
)
def test_invalid_commands_are_atomic(command):
    c = Control()
    before = asdict(c.settings)
    assert c.command(command).startswith("Rejected:")
    assert asdict(c.settings) == before


def test_release_survives_deselection():
    c = Control()
    unit = SimpleNamespace(tag=7, is_selected=True)
    assert not c.eligible(unit)
    c.command("!assist release", [7])
    unit.is_selected = False
    assert not c.eligible(unit)
    c.command("!assist claim", [7])
    assert c.eligible(unit)
    c.command("!assist release", [7])
    c.command("!assist claim-all")
    assert c.eligible(unit)


def test_reserves_exact_boundary():
    s = AssistantSettings(reserve_minerals=400, reserve_gas=100)
    assert within_budget(525, 150, 125, 50, s)
    assert not within_budget(524, 150, 125, 50, s)
    assert not within_budget(525, 149, 125, 50, s)
    assert not within_budget(525, 150, 125, 50, s, extra_minerals=400)


@pytest.mark.parametrize(
    "data", ["[]", '{"unknown": true}', '{"workers": "false"}', '{"max_workers": true}', '{"bases": -1}']
)
def test_config_rejects_invalid_types(tmp_path, data):
    path = tmp_path / "settings.json"
    path.write_text(data)
    with pytest.raises(ValueError):
        AssistantSettings.load(path)


def test_example_config_and_help():
    s = AssistantSettings.load("config/assistant.example.json")
    assert s.bases == 3 and not s.storm
    c = Control(s)
    assert c.command("unrelated chat") is None
    assert "reserve" in c.command("!assist help")
    assert "RUNNING" in c.command("!assist")
    c.command("!ASSIST SET HIGH_TEMPLAR 4")
    assert c.settings.high_templar == 4
