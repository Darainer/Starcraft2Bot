"""Run the actual PowerShell entry points on Windows; fake only uv/game/network work."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows PowerShell integration")
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def scripts(tmp_path):
    repo = tmp_path / "checkout with spaces"
    repo.mkdir()
    for name in ("Setup.ps1", "Start.ps1"):
        shutil.copy2(ROOT / name, repo / name)
    (repo / "config").mkdir()
    (repo / "config/assistant.example.json").write_text('{"workers": false}')
    (repo / ".venv/Scripts").mkdir(parents=True)
    (repo / ".venv/Scripts/python.exe").touch()
    game = tmp_path / "SC2 game"
    game.mkdir()
    map_file = tmp_path / "custom map.SC2Map"
    map_file.write_bytes(b"custom map")
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake = fake_bin / "fake_uv.py"
    fake.write_text("""import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with open(os.environ["FAKE_UV_LOG"], "a", encoding="utf-8") as out:
    out.write(json.dumps({"args": args, "cwd": os.getcwd()}) + "\\n")
mode = "doctor" if "--doctor" in args else "sync" if "sync" in args else "other"
if os.environ.get("FAKE_UV_FAIL") == mode:
    sys.exit(7)
if mode == "doctor":
    print(json.dumps({"preflight_ok": True, "installation": {"root": os.environ["FAKE_SC2_PATH"]}}))
else:
    print("fake uv success")
""")
    (fake_bin / "uv.cmd").write_text(f'@"{sys.executable}" "{fake}" %*\n')
    log = tmp_path / "uv-calls.jsonl"
    env = {
        **os.environ,
        "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"],
        "FAKE_UV_LOG": str(log),
        "FAKE_SC2_PATH": str(game),
    }

    def run(script, *args, fail=None):
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(repo / script),
                *map(str, args),
            ],
            cwd=tmp_path,
            env={**env, **({"FAKE_UV_FAIL": fail} if fail else {})},
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result

    def calls():
        return (
            [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
            if log.exists()
            else []
        )

    def setup():
        result = run("Setup.ps1", "-Sc2Path", game, "-MapFile", map_file)
        assert result.returncode == 0, result.stdout + result.stderr

    return repo, game, map_file, run, calls, setup


def test_setup_and_start_from_another_directory(scripts):
    repo, game, map_file, run, calls, setup = scripts
    setup()
    saved = json.loads((repo / ".local/windows.json").read_text(encoding="utf-8-sig"))
    assert saved["sc2_path"] == str(game)
    assert saved["map_file"] == str(map_file)
    assert all(Path(c["cwd"]) == repo for c in calls())
    result = run("Start.ps1", "-StartPaused", "-Opponent", "Zerg", "-Difficulty", "Hard")
    assert result.returncode == 0, result.stdout + result.stderr
    args = calls()[-1]["args"]
    assert "--no-sync" in args and "--locked" in args
    assert "--start-paused" in args
    assert args[args.index("--sc2-path") + 1] == str(game)
    assert args[args.index("--map-file") + 1] == str(map_file)
    assert args[args.index("--opponent") + 1] == "Zerg"
    assert args[args.index("--difficulty") + 1] == "Hard"


def test_setup_rerun_retains_paths_and_config(scripts):
    repo, _, _, run, _, setup = scripts
    setup()
    saved = (repo / ".local/windows.json").read_bytes()
    result = run("Setup.ps1")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (repo / ".local/windows.json").read_bytes() == saved
    assert (repo / "config/assistant.example.json").read_text() == '{"workers": false}'


@pytest.mark.parametrize("failure", ["sync", "doctor"])
def test_failed_setup_does_not_replace_saved_paths(scripts, failure):
    repo, game, map_file, run, _, setup = scripts
    setup()
    saved = (repo / ".local/windows.json").read_bytes()
    result = run("Setup.ps1", "-Sc2Path", game, "-MapFile", map_file, fail=failure)
    assert result.returncode == 1
    assert (repo / ".local/windows.json").read_bytes() == saved


def test_start_requires_completed_setup(scripts):
    _, _, _, run, calls, _ = scripts
    result = run("Start.ps1")
    assert result.returncode == 1
    assert "Setup is incomplete" in result.stderr
    assert not calls()


def test_start_preserves_failure_exit_code(scripts):
    _, _, _, run, _, setup = scripts
    setup()
    assert run("Start.ps1", fail="other").returncode == 7


def test_probe_attach_and_check_only(scripts):
    _, _, _, run, calls, setup = scripts
    setup()
    result = run("Start.ps1", "-Probe", "-AttachPort", "5001", "-Sc2Version", "4.10")
    assert result.returncode == 0, result.stdout + result.stderr
    args = calls()[-1]["args"]
    assert "--probe" in args and "--map-file" not in args
    assert args[args.index("--attach-port") + 1] == "5001"
    assert args[args.index("--sc2-version") + 1] == "4.10"
    assert run("Start.ps1", "-CheckOnly").returncode == 0
    assert "--doctor" in calls()[-1]["args"]
    assert run("Start.ps1", "-CheckOnly", "-Probe").returncode == 1


def test_tools_stage_reuses_uv_without_configuring_game(scripts):
    repo, _, _, run, calls, _ = scripts
    assert run("Setup.ps1", "-Stage", "Tools").returncode == 0
    assert calls()[-1]["args"] == ["--version"]
    assert not (repo / ".local/windows.json").exists()


def test_corrupt_default_map_is_not_overwritten(scripts):
    repo, game, _, run, calls, _ = scripts
    map_file = repo / "maps/BelShirVestigeLE.SC2Map"
    map_file.parent.mkdir()
    map_file.write_bytes(b"modified")
    result = run("Setup.ps1", "-Sc2Path", game)
    assert result.returncode == 1
    assert "Map hash mismatch" in result.stderr
    assert map_file.read_bytes() == b"modified"
    assert not any("--doctor" in call["args"] for call in calls())
