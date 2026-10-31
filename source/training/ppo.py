"""Small recurrent PPO: frozen complete episodes, original masks and time-aware GAE."""

import math
import random
from dataclasses import asdict, dataclass

import torch
from torch.distributions import Categorical


@dataclass(frozen=True)
class PPOConfig:
    learning_rate: float = 0.0003
    clip_ratio: float = 0.2
    value_coefficient: float = 0.5
    entropy_coefficient: float = 0.01
    gamma_seconds: float = 1800
    gae_seconds: float = 600
    epochs: int = 2
    sequence_length: int = 32
    burn_in: int = 8
    maximum_gradient: float = 0.5
    target_kl: float = 0.03

    def __post_init__(self):
        if any(not math.isfinite(v) or v < 0 for v in (self.value_coefficient, self.entropy_coefficient)):
            raise ValueError("Invalid PPO loss coefficients")
        if (
            any(
                not math.isfinite(v) or v <= 0
                for v in (
                    self.learning_rate,
                    self.clip_ratio,
                    self.gamma_seconds,
                    self.gae_seconds,
                    self.maximum_gradient,
                    self.target_kl,
                )
            )
            or not 0 < self.clip_ratio < 1
        ):
            raise ValueError("Invalid PPO constants")
        if self.epochs < 1 or self.sequence_length < 1 or self.burn_in < 0:
            raise ValueError("Invalid sequence configuration")


def masked_statistics(logits, sampled):
    """Differentiable counterpart to the reference sampler's stored distribution."""
    offsets = (0, 7, 23, 30, 34)
    probabilities, entropies = [], []
    for h, index in enumerate(sampled.action.indices):
        if not sampled.masks.active[h]:
            continue
        values = logits[offsets[h] : offsets[h + 1]]
        mask = torch.tensor(sampled.masks.heads[h], dtype=torch.bool, device=logits.device)
        distribution = Categorical(logits=values.masked_fill(~mask, float("-inf")))
        probabilities.append(distribution.log_prob(torch.tensor(index, device=logits.device)))
        entropies.append(distribution.entropy())
    return torch.stack(probabilities).sum(), torch.stack(entropies).sum()


def advantages(records, config):
    if (
        not records
        or records[-1].outcome.reason == "running"
        or any(not r.outcome.learning_eligible for r in records)
    ):
        raise ValueError("PPO requires a complete eligible episode")
    result = [0.0] * len(records)
    carry = 0.0
    for index in range(len(records) - 1, -1, -1):
        record = records[index]
        discount = record.discount(config.gamma_seconds)
        eligibility = math.exp(-record.elapsed_seconds / config.gae_seconds)
        bootstrap = record.next_value if record.outcome.bootstrap else 0.0
        delta = record.outcome.reward + discount * bootstrap - record.value_estimate
        carry = delta + (discount * eligibility * carry if record.outcome.reason == "running" else 0)
        result[index] = carry
    return result, [a + r.value_estimate for a, r in zip(result, records, strict=True)]


def update(model, episodes, policy_id, config=None, seed=0):
    config = config or PPOConfig()
    if not episodes or any(
        manifest["policy_id"] != policy_id or manifest["split"] != "train" for manifest, _ in episodes
    ):
        raise ValueError("PPO rejects foreign policy versions and non-training splits")
    rows, chunks = [], []
    for _manifest, records in episodes:
        if any(r.policy_id != policy_id for r in records):
            raise ValueError("Mixed policy versions inside episode")
        adv, returns = advantages(records, config)
        rows.append((records, adv, returns))
        chunks.extend((len(rows) - 1, start) for start in range(0, len(records), config.sequence_length))
    flattened = torch.tensor([a for _, adv, _ in rows for a in adv])
    mean, scale = flattened.mean().item(), max(flattened.std(unbiased=False).item(), 1e-8)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    rng = random.Random(seed)
    model.train()
    metrics = []
    stopped = False
    for _ in range(config.epochs):
        rng.shuffle(chunks)
        for episode, start in chunks:
            records, adv, returns = rows[episode]
            begin = max(0, start - config.burn_in)
            hidden = torch.tensor([records[begin].recurrent_input], dtype=torch.float32)
            with torch.no_grad():
                for record in records[begin:start]:
                    _, _, hidden = model(record.before, hidden)
            losses, divergences, entropies = [], [], []
            optimizer.zero_grad()
            for index in range(start, min(len(records), start + config.sequence_length)):
                record = records[index]
                logits, value, hidden = model(record.before, hidden)
                logp, entropy = masked_statistics(logits, record.decoded.sampled)
                logratio = logp - record.decoded.sampled.log_probability
                ratio = logratio.exp()
                advantage = (adv[index] - mean) / scale
                surrogate = torch.minimum(
                    ratio * advantage, ratio.clamp(1 - config.clip_ratio, 1 + config.clip_ratio) * advantage
                )
                losses.append(
                    -surrogate
                    + config.value_coefficient * (value - returns[index]).square()
                    - config.entropy_coefficient * entropy
                )
                divergences.append((ratio - 1) - logratio)
                entropies.append(entropy)
            loss = torch.stack(losses).mean()
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite PPO loss")
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(), config.maximum_gradient, error_if_nonfinite=True
            )
            optimizer.step()
            kl = torch.stack(divergences).mean().detach().item()
            metrics.append(
                {
                    "loss": loss.detach().item(),
                    "approximate_kl": kl,
                    "entropy": torch.stack(entropies).mean().detach().item(),
                    "gradient_norm": norm.item(),
                }
            )
            if kl > config.target_kl:
                stopped = True
                break
        if stopped:
            break
    return optimizer, {
        "algorithm": "recurrent-ppo-v1",
        "config": asdict(config),
        "seed": seed,
        "episodes": len(episodes),
        "transitions": len(flattened),
        "optimizer_steps": len(metrics),
        "kl_early_stop": stopped,
        "updates": metrics,
        "episode_ids": [m["episode_id"] for m, _ in episodes],
    }
