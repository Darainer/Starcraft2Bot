"""Explicit opt-in local CPU collection, recurrent PPO, checkpoints and benchmarks."""

import argparse
import json
import platform
import random
import subprocess
import time
from pathlib import Path
from statistics import mean

import psutil
import torch
from loguru import logger
from sc2.data import AIBuild, Difficulty, Race

from source.assistant_control import AssistantSettings
from source.games.starcraft2.action_codec import sample_action
from source.games.starcraft2.environment import LocalEnvironment, live_client_count
from source.games.starcraft2.model import StarCraftPolicy
from source.runtime import inspect_installation, resolve_map
from source.strategy_profiles import COMPOSITION, PROFILES
from source.training.checkpoints import load_checkpoint, restore_optimizer, save_checkpoint
from source.training.collector import EpisodeWriter, atomic_json, digest, load_episode
from source.training.ppo import PPOConfig, update
from source.training.records import Outcome, TransitionV1

ROOT = Path(__file__).resolve().parents[2]


def validate_config(config):
    for key in ("seed", "policy_seed", "model_seed", "optimizer_seed"):
        if type(config.get(key)) is not int or not 0 <= config[key] <= 0xFFFFFFFF:
            raise ValueError("Pilot seeds must be explicit unsigned integers")
    for key, lower, upper in (
        ("repeats", 1, 10),
        ("step_size", 4, 64),
        ("time_limit", 30, 3600),
        ("capacity_wait_seconds", 0, 3600),
    ):
        if type(config.get(key)) is not int or not lower <= config[key] <= upper:
            raise ValueError(f"Invalid pilot {key}")
    opponent = config.get("opponent", {})
    if (
        opponent.get("race") not in {r.name for r in Race if r.name not in {"Random", "NoRace"}}
        or (opponent.get("build") not in {b.name for b in AIBuild if b.name != "RandomBuild"})
        or opponent.get("difficulty") not in {d.name for d in Difficulty if not d.name.startswith("Cheat")}
    ):
        raise ValueError("Pilot requires an explicit non-cheating opponent")
    if config.get("profile") not in PROFILES:
        raise ValueError("Invalid pilot profile")
    PPOConfig(**config["ppo"])
    return config


def repository_identity():
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

    if git("status", "--porcelain"):
        raise ValueError("Freeze and commit source before collecting live rollout data")
    return git("rev-parse", "HEAD")


def scenario_metadata(config, installation, map_path, policy_id, split):
    return {
        "source_revision": repository_identity(),
        "lock_sha256": digest(ROOT / "uv.lock"),
        "policy_id": policy_id,
        "map_sha256": digest(map_path),
        "executable_sha256": digest(installation.executable),
        "opponent": config["opponent"],
        "step_size": config["step_size"],
        "time_limit": config["time_limit"],
        "policy_seed": config["policy_seed"],
        "split": split,
    }


def collect(
    config, installation, map_path, output, model, policy_id, split, controller="policy", *, resume=False
):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=resume)
    settings = AssistantSettings.load(ROOT / "config/assistant.example.json")
    settings.profile = config["profile"]
    for name in COMPOSITION:
        setattr(settings, name, PROFILES[settings.profile][name])
    metadata = scenario_metadata(config, installation, map_path, policy_id, split)
    sampler = sample_action
    if controller == "learned":
        from source.games.starcraft2.learned_actions import sample_action as learned_sample

        sampler = learned_sample
    results = (
        json.loads((output / "summary.json").read_text())
        if resume and (output / "summary.json").exists()
        else []
    )
    if len(results) > config["repeats"]:
        raise ValueError("Saved collection exceeds the frozen repeat count")
    for previous in results:
        saved, _ = load_episode(output / previous["episode_id"] / "rollout", split=split)
        if any(
            saved.get(k) != v
            for k, v in {**metadata, "game_seed": config["seed"], "python_seed": config["seed"]}.items()
        ):
            raise ValueError("Resume would mix frozen collection identities")
    for repeat in range(len(results), config["repeats"]):
        random.seed(config["seed"])
        rng = random.Random(config["policy_seed"])
        env = LocalEnvironment(installation, map_path, output, settings=settings, controller=controller)
        writer = None
        started = time.perf_counter()
        timings = []
        try:
            deadline = time.monotonic() + config.get("capacity_wait_seconds", 3600)
            while True:
                try:
                    belief, info = env.reset(config["seed"], metadata)
                    break
                except (RuntimeError, OSError) as exc:
                    if (
                        "slots are occupied" not in str(exc) and not isinstance(exc, BlockingIOError)
                    ) or time.monotonic() >= deadline:
                        raise
                    time.sleep(5)
            manifest = info["manifest"]
            logger.info(
                "Episode {}: {} repeat {} starts at loop zero {}",
                env.episode_id,
                controller,
                repeat + 1,
                manifest["initial_state_sha256"],
            )
            if controller != "rule":
                writer = EpisodeWriter(env.episode_directory / "rollout", manifest)
                memory = model.core.initial()
                model.eval()
                with torch.no_grad():
                    logits, value, output_memory = model(belief, memory)
            index = 0
            while True:
                before = belief
                sample = sampler(logits.tolist(), belief, rng) if controller != "rule" else None
                belief, _, terminated, truncated, event = env.step(sample)
                outcome = event["outcome"]
                if controller != "rule":
                    next_value = None
                    if outcome.bootstrap:
                        began = time.perf_counter()
                        with torch.no_grad():
                            next_logits, next_value, next_memory = model(belief, output_memory)
                        timings.append((time.perf_counter() - began) * 1000)
                    record = TransitionV1(
                        env.episode_id,
                        index,
                        policy_id,
                        before,
                        event["decoded"],
                        belief,
                        tuple(memory[0].tolist()),
                        tuple(output_memory[0].tolist()),
                        value.item(),
                        next_value.item() if next_value is not None else None,
                        outcome,
                        tuple(item["id"] for item in event["issued"]),
                        tuple(item["id"] for item in event["effects"]),
                    )
                    writer.append(
                        record,
                        {
                            "issued": event["issued"],
                            "observed": event["effects"],
                            "macro": event.get("macro_feedback", []),
                        },
                    )
                    if outcome.reason == "running":
                        memory, logits, value, output_memory = (
                            output_memory,
                            next_logits,
                            next_value,
                            next_memory,
                        )
                index += 1
                if terminated or truncated:
                    break
            env.close()
            diagnostics = {
                "game_seconds": belief.assessment.time,
                "wall_seconds": time.perf_counter() - started,
                "decisions": index,
                "mean_inference_ms": mean(timings) if timings else None,
                "p95_inference_ms": sorted(timings)[min(len(timings) - 1, int(len(timings) * 0.95))]
                if timings
                else None,
                "human_control": "not_verified",
            }
            if writer:
                writer.finish(outcome, **diagnostics)
            result = {
                "episode_id": env.episode_id,
                "outcome": outcome.reason,
                "initial_state_sha256": manifest["initial_state_sha256"],
                **diagnostics,
            }
            atomic_json(env.episode_directory / "result.json", {**result, "manifest": manifest})
            results.append(result)
            atomic_json(output / "summary.json", results)
            print(json.dumps(result), flush=True)
        except BaseException as exc:
            if writer:
                writer.finish(
                    Outcome("aborted" if isinstance(exc, KeyboardInterrupt) else "infrastructure_error"),
                    error=str(exc),
                )
            atomic_json(
                output / f"failure-{env.episode_id}.json",
                {"error": f"{type(exc).__name__}: {exc}", "completed": results},
            )
            raise
        finally:
            env.close()
    if len({r["initial_state_sha256"] for r in results}) != 1:
        raise ValueError("Fixed-seed repeats have mismatched loop-zero fingerprints")
    return results


def benchmark(model, records, iterations=100):
    model.eval()
    representative = [
        records[0],
        records[len(records) // 2],
        max(records, key=lambda r: len(r.before.shared.entities)),
    ]
    measurements = []
    clients = live_client_count()
    with torch.no_grad():
        for record in representative:
            memory = torch.tensor([record.recurrent_input])
            for _ in range(10):
                model(record.before, memory)
            timings = []
            for _ in range(iterations):
                started = time.perf_counter()
                model(record.before, memory)
                timings.append((time.perf_counter() - started) * 1000)
            timings.sort()
            measurements.append(
                {
                    "entities": len(record.before.shared.entities),
                    "iterations": iterations,
                    "p50_ms": timings[len(timings) // 2],
                    "p95_ms": timings[int(len(timings) * 0.95)],
                    "p99_ms": timings[min(len(timings) - 1, int(len(timings) * 0.99))],
                }
            )
    return {
        "model_parameters": sum(p.numel() for p in model.parameters()),
        "float32_weight_bytes": sum(p.numel() * 4 for p in model.parameters()),
        "cpu": platform.processor(),
        "torch": str(torch.__version__),
        "torch_threads": torch.get_num_threads(),
        "physical_memory_bytes": psutil.virtual_memory().total,
        "process_rss_bytes": psutil.Process().memory_info().rss,
        "live_sc2_clients_at_start": clients,
        "live_sc2_clients_at_end": live_client_count(),
        "samples": measurements,
        "scope": "End-to-end CPU neural forward including tensor encoding; game stepping and sampling excluded",
    }


def pilot(config, installation, map_path, output):
    validate_config(config)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    atomic_json(output / "pilot-config.json", config)
    torch.manual_seed(config["model_seed"])
    torch.set_num_threads(1)
    model = StarCraftPolicy()
    provenance = {"source_revision": repository_identity(), "lock_sha256": digest(ROOT / "uv.lock")}
    initial = save_checkpoint(output / "initial", model, seed=config["model_seed"], provenance=provenance)
    initial_results = collect(
        config, installation, map_path, output / "train", model, initial["policy_id"], "train"
    )
    episodes = [
        load_episode(p.parent, split="train")
        for p in sorted((output / "train").glob("*/rollout/manifest.json"))
    ]
    optimizer, training = update(
        model, episodes, initial["policy_id"], PPOConfig(**config["ppo"]), seed=config["optimizer_seed"]
    )
    trained = save_checkpoint(
        output / "trained",
        model,
        seed=config["model_seed"],
        optimizer_steps=training["optimizer_steps"],
        training=training,
        optimizer=optimizer,
        provenance=provenance,
    )
    # Reload the frozen artifact before evaluation; worker weights change only at reset.
    model, _ = load_checkpoint(output / "trained")
    trained_results = collect(
        config, installation, map_path, output / "evaluation", model, trained["policy_id"], "development"
    )
    reference = collect(
        config,
        installation,
        map_path,
        output / "reference",
        None,
        f"rule-reference:{repository_identity()}",
        "development",
        controller="rule",
    )
    fingerprints = {r["initial_state_sha256"] for r in initial_results + trained_results + reference}
    if len(fingerprints) != 1:
        raise ValueError("Pilot comparison groups have unmatched starting states")
    evidence = benchmark(model, episodes[0][1])
    result = {
        "scope": "Small from-scratch development pilot; repeated starts measure reproducibility, not generalization",
        "config": config,
        "initial_policy": initial,
        "trained_policy": trained,
        "initial_training_outcomes": initial_results,
        "trained_development_outcomes": trained_results,
        "rule_reference_outcomes": reference,
        "benchmark": evidence,
        "teacher_imitation": "not_used",
        "playing_strength_accepted": False,
        "human_control": "not_verified",
    }
    atomic_json(output / "pilot-results.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["train", "pilot", "benchmark"])
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sc2-path", type=Path)
    parser.add_argument("--map-file", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--episode", type=Path)
    parser.add_argument("--resume", action="store_true", help="Resume the same frozen independent curriculum")
    args = parser.parse_args(argv)
    torch.set_num_threads(1)
    if args.command == "benchmark":
        if args.checkpoint is None or args.episode is None:
            parser.error("benchmark requires --checkpoint and --episode")
        model, _ = load_checkpoint(args.checkpoint)
        _, records = load_episode(args.episode)
        atomic_json(args.output, benchmark(model, records))
        return
    config_path = args.config or ROOT / "config/training" / (
        "easy.json" if args.command == "train" else "pilot.json"
    )
    config = validate_config(json.loads(config_path.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(args.output.parent / (args.output.name + ".log"), level="INFO")
    try:
        install = inspect_installation(args.sc2_path)
        map_path = resolve_map(install, "BelShirVestigeLE", args.map_file)
        if args.command == "train":
            train(config, install, map_path, args.output, resume=args.resume)
        else:
            pilot(config, install, map_path, args.output)
    except Exception as exc:
        logger.exception("Training pilot failed: {}", exc)
        raise SystemExit(str(exc)) from exc


def train(config, installation, map_path, output, *, resume=False):
    """Bounded Easy curriculum with separate development worlds and resumable Adam.

    Completed episodes/checkpoints are immutable. Interrupted episodes stay
    quarantined; resume collects only missing repeats under the original source.
    There is no hardcoded-policy reference or promotion gate in this track.
    """
    from source.games.starcraft2.learned_model import LearnedPolicy

    validate_config(config)
    if (
        config["opponent"]["difficulty"] != "Easy"
        or config["repeats"] != 3
        or type(config.get("iterations")) is not int
        or not 1 <= config["iterations"] <= 100
        or type(config.get("development_seed")) is not int
        or not 0 <= config["development_seed"] <= 0xFFFFFFFF
        or config["development_seed"] in range(config["seed"], config["seed"] + config["iterations"])
        or config["seed"] + config["iterations"] > 0xFFFFFFFF
        or config["policy_seed"] + 10000 + config["iterations"] > 0xFFFFFFFF
    ):
        raise ValueError(
            "Independent curriculum requires Easy, three repeats, and separate explicit development seeds"
        )
    provenance = {"source_revision": repository_identity(), "lock_sha256": digest(ROOT / "uv.lock")}
    output = Path(output)
    output.mkdir(parents=True, exist_ok=resume)
    frozen = output / "training-config.json"
    context = {
        "config": config,
        "provenance": provenance,
        "map_sha256": digest(map_path),
        "executable_sha256": digest(installation.executable),
    }
    if frozen.exists():
        if json.loads(frozen.read_text()) != context:
            raise ValueError("Resume requires the original source, environment and curriculum configuration")
    else:
        atomic_json(frozen, context)
    torch.set_num_threads(1)
    initial_path = output / "initial"
    if not initial_path.exists():
        torch.manual_seed(config["model_seed"])
        save_checkpoint(initial_path, LearnedPolicy(), seed=config["model_seed"], provenance=provenance)
    model, checkpoint = load_checkpoint(initial_path)
    optimizer = None
    completed = []
    ppo = PPOConfig(**config["ppo"])
    for iteration in range(config["iterations"]):
        directory = output / f"iteration-{iteration + 1:03d}"
        directory.mkdir(exist_ok=True)
        training_config = {
            **config,
            "seed": config["seed"] + iteration,
            "policy_seed": config["policy_seed"] + iteration,
        }
        training_results = collect(
            training_config,
            installation,
            map_path,
            directory / "train",
            model,
            checkpoint["policy_id"],
            "train",
            "learned",
            resume=resume,
        )
        episodes = [
            load_episode(directory / "train" / r["episode_id"] / "rollout", split="train")
            for r in training_results
        ]
        parent = checkpoint
        trained_path = directory / "checkpoint"
        if not trained_path.exists():
            optimizer, metrics = update(
                model,
                episodes,
                parent["policy_id"],
                ppo,
                seed=config["optimizer_seed"] + iteration,
                optimizer=optimizer,
            )
            metrics.update(parent_policy_id=parent["policy_id"], iteration=iteration + 1)
            save_checkpoint(
                trained_path,
                model,
                seed=config["model_seed"],
                optimizer_steps=parent["optimizer_steps"] + metrics["optimizer_steps"],
                training=metrics,
                optimizer=optimizer,
                provenance=provenance,
            )
        model, checkpoint = load_checkpoint(trained_path)
        if checkpoint["training"]["parent_policy_id"] != parent["policy_id"]:
            raise ValueError("Resumed checkpoint does not descend from this frozen rollout policy")
        optimizer = restore_optimizer(trained_path, model, ppo)
        development_config = {
            **config,
            "seed": config["development_seed"],
            "policy_seed": config["policy_seed"] + 10000,
        }
        development_results = collect(
            development_config,
            installation,
            map_path,
            directory / "development",
            model,
            checkpoint["policy_id"],
            "development",
            "learned",
            resume=resume,
        )
        result = {
            "iteration": iteration + 1,
            "parent_policy_id": parent["policy_id"],
            "policy_id": checkpoint["policy_id"],
            "optimizer_steps": checkpoint["optimizer_steps"],
            "training": training_results,
            "development": development_results,
            "metrics": checkpoint["training"],
            "benchmark": benchmark(model, episodes[0][1]),
            "human_control": "not_verified",
        }
        atomic_json(directory / "result.json", result)
        completed.append(result)
        atomic_json(
            output / "progress.json",
            {
                "completed_iterations": completed,
                "latest_checkpoint": str(trained_path.relative_to(output)),
                "difficulty": "Easy",
                "scope": "Independent strategy/economy; fixed placement, allocation routing, scouting and unit micro",
            },
        )
        del episodes
    return completed


if __name__ == "__main__":
    main()
