import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from loguru import logger

from source import run_assistant
from source.runtime import Installation


@pytest.fixture(autouse=True)
def close_logs():
    yield
    logger.remove()


@pytest.fixture
def installed(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    install = Installation(tmp_path, tmp_path / "SC2_x64.exe", 98310, None, "latest", (98310,))
    monkeypatch.setattr(run_assistant, "inspect_installation", Mock(return_value=install))
    game_map = tmp_path / "Test.SC2Map"
    game_map.write_bytes(b"test map")
    monkeypatch.setattr(run_assistant, "resolve_map", Mock(return_value=game_map))
    launch = AsyncMock()
    monkeypatch.setattr(run_assistant, "run_session", launch)
    return launch


def test_cli_help_does_not_launch(monkeypatch, capsys):
    lookup = Mock()
    monkeypatch.setattr(run_assistant, "inspect_installation", lookup)
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--help"])
    assert exc.value.code == 0
    assert "--attach-port" in capsys.readouterr().out
    lookup.assert_not_called()


def test_config_check_without_game(monkeypatch, capsys):
    lookup = Mock(side_effect=AssertionError("Must not inspect game install"))
    monkeypatch.setattr(run_assistant, "inspect_installation", lookup)
    run_assistant.main(["--check-config", "--config", "config/assistant.example.json"])
    assert "Configuration valid" in capsys.readouterr().out


def test_invalid_config_exits_before_game_lookup(monkeypatch, tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"workers": "false"}')
    lookup = Mock()
    monkeypatch.setattr(run_assistant, "inspect_installation", lookup)
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--config", str(path)])
    assert exc.value.code == 2
    lookup.assert_not_called()


def test_launch_is_one_shared_participant_paused_on_request(installed):
    run_assistant.main(["--opponent", "Zerg", "--start-paused", "--attach-port", "5001"])
    args, kwargs = installed.call_args
    assert len(args[2]) == 2
    assert args[2][0].ai.raw_affects_selection is False
    assert args[2][0].ai.settings.enabled is False
    assert args[2][1].race.name == "Zerg"
    assert args[3].suffix == ".SC2Replay"
    assert kwargs == {"probe": False, "attach_port": 5001}


def test_composition_and_individual_tactical_flags_can_be_enabled_and_revoked(installed):
    flags = ("oracle_harass", "oracle_beam", "defend_assets", "local_regroup")
    run_assistant.main(
        ["--composition-policy", "scouted", *("--" + name.replace("_", "-") for name in flags)]
    )
    settings = installed.call_args.args[2][0].ai.settings
    assert settings.composition_policy == "scouted"
    assert all(getattr(settings, name) for name in flags)
    run_assistant.main([*("--no-" + name.replace("_", "-") for name in flags)])
    assert all(not getattr(installed.call_args.args[2][0].ai.settings, name) for name in flags)


def test_doctor_does_not_launch(installed, capsys):
    run_assistant.main(["--doctor"])
    result = json.loads(capsys.readouterr().out)
    assert result["preflight_ok"] is True
    assert result["human_control"] == "not_verified"
    installed.assert_not_called()


def test_probe_needs_no_map(installed, monkeypatch):
    lookup = Mock(side_effect=AssertionError("Probe needs no map"))
    monkeypatch.setattr(run_assistant, "resolve_map", lookup)
    run_assistant.main(["--probe"])
    assert installed.call_args.kwargs["probe"] is True
    assert installed.call_args.args[1] is None


def test_missing_install_actionable_error(installed, monkeypatch, capsys):
    monkeypatch.setattr(run_assistant, "inspect_installation", Mock(side_effect=ValueError("Missing SC2")))
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--doctor"])
    assert exc.value.code == 2
    assert json.loads(capsys.readouterr().out)["preflight_ok"] is False
    installed.assert_not_called()


@pytest.mark.parametrize("port", ["0", "65536", "oops"])
def test_invalid_port(port):
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--attach-port", port])
    assert exc.value.code == 2


def test_runtime_failure_has_nonzero_exit(installed):
    installed.side_effect = RuntimeError("Protocol failure")
    with pytest.raises(SystemExit) as exc:
        run_assistant.main([])
    assert exc.value.code == 1


def test_interrupt_reports_status(installed):
    installed.side_effect = KeyboardInterrupt
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--runtime-report", "logs/interrupted.json"])
    assert exc.value.code == 130
    assert json.loads(Path("logs/interrupted.json").read_text())["phase"] == "interrupted"


def test_fast_test_has_explicit_bounded_runtime(installed):
    run_assistant.main(["--fast-test", "--game-time-limit", "600", "--profile", "air", "--attack"])
    assert installed.call_args.kwargs["realtime"] is False
    assert installed.call_args.kwargs["game_time_limit"] == 600
    settings = installed.call_args.args[2][0].ai.settings
    assert settings.attack and settings.voidrays == 14
    assert installed.call_args.args[4].data["fast_test"]


def test_collection_options_preserve_all_log_rotations_and_enable_only_requested_revisit(
    installed, monkeypatch
):
    add = Mock(wraps=run_assistant.logger.add)
    monkeypatch.setattr(run_assistant.logger, "add", add)
    run_assistant.main(["--snapshot-interval", "1", "--scout-revisit"])
    assistant = installed.call_args.args[2][0].ai
    assert assistant.scouting.revisit
    assert assistant.report.data["snapshot_interval"] == 1
    assert assistant.report.data["log_retention"] == "all_rotations"
    assert add.call_args.kwargs["retention"] is None


@pytest.mark.parametrize("interval", ["0", "31"])
def test_invalid_recording_interval_does_not_launch(installed, interval):
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--snapshot-interval", interval])
    assert exc.value.code == 2
    installed.assert_not_called()


def test_repeatable_game_records_and_passes_seed_and_build(installed, monkeypatch):
    seed = Mock()
    monkeypatch.setattr(run_assistant.random, "seed", seed)
    run_assistant.main(["--fast-test", "--seed", "20261025", "--opponent-build", "Macro"])
    assert installed.call_args.kwargs["random_seed"] == 20261025
    args = installed.call_args.args
    assert args[2][1].ai_build.name == "Macro"
    assert args[4].data["random_seed"] == 20261025
    assert args[4].data["opponent_build"] == "Macro"
    assert args[4].data["opponent_race"] == "Terran"
    seed.assert_called_once_with(20261025)


@pytest.mark.parametrize("seed", ["-1", "4294967296", "invalid"])
def test_invalid_game_seed_does_not_launch(installed, seed):
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(["--seed", seed])
    assert exc.value.code == 2
    installed.assert_not_called()


@pytest.mark.parametrize("args", [["--game-time-limit", "0"], ["--fast-test", "--attach-port", "5001"]])
def test_invalid_fast_test_arguments(args):
    with pytest.raises(SystemExit) as exc:
        run_assistant.main(args)
    assert exc.value.code == 2
