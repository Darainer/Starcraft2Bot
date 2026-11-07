"""Versioned core/adapter weights with integrity checks; local artifacts only."""

import json
import tempfile
from pathlib import Path

import torch

from source.games.starcraft2.action_codec import DECODER_VERSION
from source.games.starcraft2.actions import ACTION_VERSION, MASK_VERSION
from source.games.starcraft2.encoding import NORMALIZATION_VERSION
from source.games.starcraft2.model import MODEL_VERSION, StarCraftPolicy
from source.games.starcraft2.observation import LIVE_FEATURE_VERSION
from source.opponent_beliefs import ONTOLOGY_ID
from source.strategy_core.contracts import SHARED_ONTOLOGY
from source.training.collector import atomic_json, digest, identity


def contract(model):
    if model.model_version != MODEL_VERSION:
        from source.games.starcraft2 import learned_actions

        return (
            model.model_version,
            model.feature_version,
            learned_actions.ACTION_VERSION,
            learned_actions.MASK_VERSION,
            learned_actions.DECODER_VERSION,
        )
    return MODEL_VERSION, LIVE_FEATURE_VERSION, ACTION_VERSION, MASK_VERSION, DECODER_VERSION


def save_checkpoint(
    directory, model, *, seed, optimizer_steps=0, training=None, optimizer=None, provenance=None
):
    destination = Path(directory)
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix=f".{destination.name}-writing-", dir=destination.parent))
    state = {name: tensor.detach().cpu() for name, tensor in model.state_dict().items()}
    torch.save(
        {name.removeprefix("core."): tensor for name, tensor in state.items() if name.startswith("core.")},
        directory / "core.pt",
    )
    torch.save(
        {name: tensor for name, tensor in state.items() if not name.startswith("core.")},
        directory / "adapter.pt",
    )
    model_version, feature_version, action_version, mask_version, decoder_version = contract(model)
    data = {
        "schema_version": "sc2-checkpoint-v1",
        "model_version": model_version,
        "feature_version": feature_version,
        "action_version": action_version,
        "mask_version": mask_version,
        "decoder_version": decoder_version,
        "core_sha256": digest(directory / "core.pt"),
        "adapter_sha256": digest(directory / "adapter.pt"),
        "seed": seed,
        "optimizer_steps": optimizer_steps,
        "training": training,
        "torch_version": str(torch.__version__),
        "parameters": sum(p.numel() for p in model.parameters()),
        "normalization_version": NORMALIZATION_VERSION,
        "shared_ontology": SHARED_ONTOLOGY,
        "domain_ontology": ONTOLOGY_ID,
        "provenance": provenance,
    }
    if optimizer is not None:
        torch.save(optimizer.state_dict(), directory / "optimizer.pt")
        data["optimizer_sha256"] = digest(directory / "optimizer.pt")
    data["policy_id"] = identity(
        {key: data[key] for key in ("model_version", "core_sha256", "adapter_sha256")}
    )
    atomic_json(directory / "checkpoint.json", data)
    directory.rename(destination)
    return data


def load_checkpoint(directory):
    directory = Path(directory)
    data = json.loads((directory / "checkpoint.json").read_text(encoding="utf-8"))
    model = StarCraftPolicy()
    if data.get("model_version") != MODEL_VERSION:
        from source.games.starcraft2.learned_model import MODEL_VERSION as LEARNED_MODEL_VERSION
        from source.games.starcraft2.learned_model import LearnedPolicy

        if data.get("model_version") != LEARNED_MODEL_VERSION:
            raise ValueError("Checkpoint schema/decoder mismatch")
        model = LearnedPolicy()
    if (
        data.get("schema_version"),
        data.get("model_version"),
        data.get("feature_version"),
        data.get("action_version"),
        data.get("mask_version"),
        data.get("decoder_version"),
    ) != ("sc2-checkpoint-v1", *contract(model)):
        raise ValueError("Checkpoint schema/decoder mismatch")
    for name in ("core", "adapter"):
        if digest(directory / f"{name}.pt") != data[f"{name}_sha256"]:
            raise ValueError("Checkpoint artifact hash mismatch")
    if data["policy_id"] != identity(
        {key: data[key] for key in ("model_version", "core_sha256", "adapter_sha256")}
    ):
        raise ValueError("Checkpoint policy identity mismatch")
    if (data.get("normalization_version"), data.get("shared_ontology"), data.get("domain_ontology")) != (
        NORMALIZATION_VERSION,
        SHARED_ONTOLOGY,
        ONTOLOGY_ID,
    ):
        raise ValueError("Checkpoint semantics mismatch")
    core = torch.load(directory / "core.pt", map_location="cpu", weights_only=True)
    adapter = torch.load(directory / "adapter.pt", map_location="cpu", weights_only=True)
    model.load_state_dict({**adapter, **{f"core.{name}": value for name, value in core.items()}}, strict=True)
    return model, data


def restore_optimizer(directory, model, config):
    directory = Path(directory)
    data = json.loads((directory / "checkpoint.json").read_text(encoding="utf-8"))
    path = directory / "optimizer.pt"
    if not data.get("optimizer_sha256") or digest(path) != data["optimizer_sha256"]:
        raise ValueError("Missing or corrupt optimizer state")
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    optimizer.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    if any(group["lr"] != config.learning_rate for group in optimizer.param_groups):
        raise ValueError("Resumed optimizer learning rate differs from frozen configuration")
    return optimizer
