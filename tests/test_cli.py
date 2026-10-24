from unittest.mock import Mock

import pytest
from loguru import logger

from source import run_assistant


@pytest.fixture(autouse=True)
def close_logs():
    yield
    logger.remove()


def test_cli_help_does_not_launch(monkeypatch, capsys):
    launch = Mock()
    monkeypatch.setattr(run_assistant, "run_game", launch)
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--help"])
    assert exc.value.code == 0
    assert "--config" in capsys.readouterr().out
    launch.assert_not_called()


def test_config_check_without_game(monkeypatch, capsys):
    lookup = Mock(side_effect=AssertionError("Must not inspect game install"))
    monkeypatch.setattr(run_assistant.maps, "get", lookup)
    run_assistant.main(["--check-config", "--config", "config/assistant.example.json"])
    assert "Configuration valid" in capsys.readouterr().out


def test_invalid_config_exits_before_game_lookup(monkeypatch, tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"workers": "false"}')
    lookup = Mock()
    monkeypatch.setattr(run_assistant.maps, "get", lookup)
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--config", str(path)])
    assert exc.value.code == 2
    lookup.assert_not_called()


def test_launch_is_one_shared_realtime_participant(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    game_map = object()
    monkeypatch.setattr(run_assistant.maps, "get", Mock(return_value=game_map))
    launch = Mock()
    monkeypatch.setattr(run_assistant, "run_game", launch)
    run_assistant.main(["--map", "TestMap", "--opponent", "Zerg"])
    args, kwargs = launch.call_args
    assert args[0] is game_map and len(args[1]) == 2
    assert args[1][0].ai.raw_affects_selection is False
    assert args[1][1].race.name == "Zerg"
    assert kwargs["realtime"] is True
    assert kwargs["save_replay_as"].startswith("replays")
    assert kwargs["save_replay_as"].endswith(".SC2Replay")


def test_missing_map_has_actionable_error(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run_assistant.maps, "get", Mock(side_effect=KeyError("MissingMap")))
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--map", "MissingMap"])
    assert exc.value.code == 2
    assert "MissingMap" in capsys.readouterr().err
