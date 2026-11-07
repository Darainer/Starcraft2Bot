"""Immutable episode manifests and complete, integrity-checked local rollouts."""

import gzip
import hashlib
import json
from contextlib import ExitStack
from pathlib import Path

from source.training.records import TransitionV1

MANIFEST_VERSION = "sc2-rollout-manifest-v1"
REQUIRED = {
    "episode_id",
    "source_revision",
    "lock_sha256",
    "policy_id",
    "core_version",
    "adapter_version",
    "shared_ontology",
    "domain_ontology",
    "feature_version",
    "normalization_version",
    "action_version",
    "mask_version",
    "decoder_version",
    "reward_version",
    "map_sha256",
    "executable_sha256",
    "ping",
    "opponent",
    "game_seed",
    "python_seed",
    "step_size",
    "time_limit",
    "split",
    "settings",
    "initial_state",
    "initial_state_sha256",
    "policy_seed",
    "decision_cadence",
    "time_unit",
}


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def atomic_json(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def validate_manifest(data):
    if data.get("schema_version") != MANIFEST_VERSION or REQUIRED - data.keys():
        raise ValueError("Incomplete rollout manifest")
    if data["split"] not in {"train", "development", "held_out"} or data["time_unit"] != "game_seconds":
        raise ValueError("Invalid split/time convention")
    if data["opponent"].get("build") in {None, "RandomBuild"} or data["opponent"].get("race") == "Random":
        raise ValueError("Pilot opponents require explicit race and build")
    if (
        data["initial_state"].get("game_loop") != 0
        or identity(data["initial_state"]) != data["initial_state_sha256"]
    ):
        raise ValueError("Missing verified loop-zero fingerprint")
    if not {"game_version", "base_build", "data_build", "data_version"} <= data["ping"].keys():
        raise ValueError("Missing exact ping identity")
    for name in ("lock_sha256", "map_sha256", "executable_sha256", "initial_state_sha256"):
        if len(data[name]) != 64 or any(c not in "0123456789abcdef" for c in data[name]):
            raise ValueError("Invalid artifact hash")
    return data


class EpisodeWriter:
    def __init__(self, directory, manifest):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.manifest = json.loads(json.dumps(validate_manifest(manifest), allow_nan=False))
        self.path = self.directory / "transitions.jsonl.gz"
        self.stack = ExitStack()
        self.stream = self.stack.enter_context(gzip.open(self.path, "wt", encoding="utf-8", compresslevel=3))  # noqa: SIM115 -- episode lifetime is owned by the ExitStack
        self.count = 0
        self.last = None
        self.finished = False
        self.status = {**self.manifest, "phase": "collecting", "learning_eligible": False}
        atomic_json(self.directory / "manifest.json", self.status)

    def append(self, transition, feedback=None):
        if (
            self.finished
            or transition.episode_id != self.manifest["episode_id"]
            or transition.policy_id != self.manifest["policy_id"]
        ):
            raise ValueError("Episode/policy boundary mismatch")
        if transition.decision_index != self.count or (
            self.last is not None
            and (
                self.last.outcome.reason != "running"
                or self.last.after != transition.before
                or self.last.recurrent_output != transition.recurrent_input
            )
        ):
            raise ValueError("Discontinuous recurrent sequence")
        row = transition.to_dict()
        row["execution_feedback"] = feedback or {"issued": [], "observed": []}
        self.stream.write(json.dumps(row, allow_nan=False) + "\n")
        self.last = transition
        self.count += 1

    def finish(self, outcome, **diagnostics):
        if self.finished:
            return
        self.stack.close()
        self.finished = True
        complete = (
            outcome.reason != "running"
            and outcome.learning_eligible
            and self.last is not None
            and self.last.outcome == outcome
        )
        self.status.update(
            phase="complete" if complete else "quarantined",
            learning_eligible=complete,
            outcome=outcome.reason,
            transition_count=self.count,
            transitions_sha256=digest(self.path),
            diagnostics=diagnostics,
        )
        atomic_json(self.directory / "manifest.json", self.status)


def load_episode(directory, *, split=None):
    directory = Path(directory)
    manifest = validate_manifest(json.loads((directory / "manifest.json").read_text(encoding="utf-8")))
    if manifest.get("phase") != "complete" or not manifest.get("learning_eligible"):
        raise ValueError("Incomplete/error/aborted episode is quarantined")
    if split is not None and manifest["split"] != split:
        raise ValueError("Dataset split mismatch")
    path = directory / "transitions.jsonl.gz"
    if digest(path) != manifest["transitions_sha256"]:
        raise ValueError("Transition artifact hash mismatch")
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        records = [TransitionV1.from_dict(json.loads(line)) for line in stream]
    if (
        len(records) != manifest["transition_count"]
        or not records
        or records[-1].outcome.reason != manifest["outcome"]
    ):
        raise ValueError("Incomplete transition sequence")
    for i, record in enumerate(records):
        if (
            record.decision_index != i
            or record.episode_id != manifest["episode_id"]
            or record.policy_id != manifest["policy_id"]
        ):
            raise ValueError("Mixed episode/policy sequence")
        if not record.outcome.learning_eligible or (
            i < len(records) - 1 and record.outcome.reason != "running"
        ):
            raise ValueError("Invalid outcome inside sequence")
        if i and (
            records[i - 1].after != record.before or records[i - 1].recurrent_output != record.recurrent_input
        ):
            raise ValueError("Discontinuous episode")
    return manifest, records
