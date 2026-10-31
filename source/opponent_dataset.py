"""Archive local recordings and export causal facts separately from weak labels."""

import argparse
import hashlib
import json
import shutil
from math import hypot
from pathlib import Path

from s2clientprotocol import sc2api_pb2 as pb
from sc2.ids.unit_typeid import UnitTypeId as U

from source.opponent_strategy import OpponentStrategyModel
from source.scouting_diagnostics import ScoutingDiagnostics
from source.scouting_facts import FACT_SCHEMA, ScoutingFacts


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def unit_metadata(path):
    data = pb.ResponseData.FromString(Path(path).read_bytes())
    workers = {U.PROBE.value, U.DRONE.value, U.SCV.value, U.MULE.value}
    result = {}
    for unit in data.units:
        try:
            kind = U(unit.unit_id).name
        except ValueError:
            kind = f"UNIT_{unit.unit_id}"
        result[unit.unit_id] = {
            "kind": kind,
            "supply": unit.food_required,
            "structure": 8 in unit.attributes,
            "combat": (bool(unit.weapons) or unit.food_required > 0)
            and 8 not in unit.attributes
            and unit.unit_id not in workers,
        }
    return result


def split_group(match):
    """Keep repeats, bot revisions, scout policies and builds of a world together."""
    initial = match.get("initial_state") or {}
    scenario = initial.get("scenario", {})
    world = {key: scenario.get(key) for key in ("map_sha256", "ping", "random_seed", "opponent_race")}
    world["starting_units"] = initial.get("units")
    if world["map_sha256"] is None or world["starting_units"] is None:
        raise ValueError("A dataset needs the loop-zero world identity for safe grouped splitting")
    return hashlib.sha256(json.dumps(world, sort_keys=True).encode()).hexdigest()


def public_map_context(match, game_info):
    """Only our starting base and publicly possible starts; never actual hidden spawn."""
    base = next(
        (
            u
            for u in (match.get("initial_state") or {}).get("units", [])
            if u.get("unit_type") == U.NEXUS.value
        ),
        None,
    )
    if base is None:
        return None
    own = [base["pos"].get("x", 0), base["pos"].get("y", 0)]
    raw = game_info.get("start_raw", {})
    starts = [[p.get("x", 0), p.get("y", 0)] for p in raw.get("start_locations", [])]
    return {
        "own_start": own,
        "possible_enemy_starts": [p for p in starts if hypot(p[0] - own[0], p[1] - own[1]) > 12],
        "playable_area": raw.get("playable_area"),
        "scope": "Public possible starting locations; multiple candidates are not confirmed enemy positions",
    }


def export_dataset(matches, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": 1,
        "phase": "building",
        "episodes": [],
        "input_schema": FACT_SCHEMA,
        "oracle_targets_available": False,
        "extractor_sha256": {
            name: digest(Path(__file__).with_name(name))
            for name in (
                "opponent_dataset.py",
                "scouting_facts.py",
                "scouting_diagnostics.py",
                "opponent_strategy.py",
            )
        },
        "scope": "Local player-view observations. Labels and provenance are separate from model inputs; no RL action policy or reliable trained predictor is included.",
    }
    manifest_path = destination / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    labels, diagnostics = [], []
    for match in matches:
        report_path = Path(match["report"])
        report = json.loads(report_path.read_text(encoding="utf-8-sig"))
        if report.get("phase") not in {"ended", "failed", "interrupted"}:
            raise ValueError("Never archive a recording that is still being written")
        episode = digest(report_path)
        raw_dir = destination / "raw" / episode
        raw_dir.mkdir(parents=True)
        assets = set(report_path.parent.glob(report_path.stem + ".*"))
        source_manifest = report_path.parent.parent / "candidate-manifest.json"
        source_identity = None
        if source_manifest.is_file():
            assets.add(source_manifest)
            source_identity = json.loads(source_manifest.read_text())["source_commit"]
        replay = match.get("replay") or report.get("replay")
        if replay and Path(replay).is_file():
            assets.add(Path(replay))
        archived = []
        for asset in sorted(assets):
            before = digest(asset)
            target = raw_dir / asset.name
            shutil.copy2(asset, target)
            if digest(target) != before or digest(asset) != before:
                raise ValueError("Source changed while archiving")
            archived.append(
                {
                    "file": target.relative_to(destination).as_posix(),
                    "sha256": before,
                    "bytes": target.stat().st_size,
                }
            )
        snapshot = report_path.with_suffix(".state.jsonl")
        facts_path = destination / "facts" / f"{episode}.jsonl"
        examples = 0
        diagnostic = ScoutingDiagnostics(report.get("opponent_build"))
        if snapshot.exists():
            info_path = report_path.with_suffix(".game-info.json")
            info = json.loads(info_path.read_text()) if info_path.exists() else {}
            projector = ScoutingFacts(
                unit_metadata(report_path.with_suffix(".game-data.pb")), public_map_context(match, info)
            )
            model = OpponentStrategyModel()
            facts_path.parent.mkdir(exist_ok=True)
            with (
                snapshot.open(encoding="utf-8-sig") as stream,
                facts_path.open("x", encoding="utf-8") as output,
            ):
                for line in stream:
                    row = json.loads(line)
                    facts = projector.observe(row)
                    output.write(json.dumps(facts, allow_nan=False) + "\n")
                    prediction = model.observe(
                        facts["time_seconds"], row.get("scouting", {}).get("intel", {})
                    )
                    diagnostic.observe(facts, prediction)
                    examples += 1
        group = split_group(match) if match.get("initial_state") else None
        if group is None and report.get("phase") == "ended":
            raise ValueError("Completed games require loop-zero provenance")
        manifest["episodes"].append(
            {
                "episode_id": episode,
                "split_group": group,
                "examples": examples,
                "source_commit": source_identity,
                "eligible_for_learning": bool(
                    group and examples and report.get("phase") == "ended" and not report.get("error")
                ),
                "facts": facts_path.relative_to(destination).as_posix() if examples else None,
                "facts_sha256": digest(facts_path) if examples else None,
                "artifacts": archived,
                "snapshot_interval": report.get("snapshot_interval"),
                "log_retention": report.get("log_retention", "legacy_policy_not_recorded"),
            }
        )
        labels.append(
            {
                "episode_id": episode,
                "configured_build": report.get("opponent_build"),
                "label_kind": "weak_episode_configuration_not_dynamic_intent_truth",
                "result": report.get("result"),
                "phase": report["phase"],
                "scout_revisit": report.get("scout_revisit", False),
                "game_time_limit": report.get("game_time_limit"),
            }
        )
        diagnostics.append(
            {
                "episode_id": episode,
                "configured_build_evaluation_only": report.get("opponent_build"),
                **diagnostic.result(),
            }
        )
    (destination / "labels.json").write_text(json.dumps(labels, indent=2) + "\n", encoding="utf-8")
    (destination / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2) + "\n", encoding="utf-8")
    manifest.update(
        phase="complete",
        split_groups=len({e["split_group"] for e in manifest["episodes"] if e["split_group"] is not None}),
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        matches = [row for path in args.matrix for row in json.loads(path.read_text(encoding="utf-8-sig"))]
        manifest = export_dataset(matches, args.output)
        print(json.dumps({"episodes": len(manifest["episodes"]), "split_groups": manifest["split_groups"]}))
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
