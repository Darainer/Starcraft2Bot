"""SC2 semantic encoder, shared recurrent core and four policy/value heads."""

import torch
from torch import nn

from source.games.starcraft2.encoding import FEATURE_VERSION
from source.games.starcraft2.observation import ENTITY_FEATURES, LIVE_FEATURE_VERSION, LIVE_FEATURES
from source.strategy_core.network import RecurrentCore

MODEL_VERSION = "sc2-gru256-v1"
BASE_FEATURES = (
    "candidates.omitted_count",
    "own.deployment_capacity",
    "own.force_health",
    "own.workforce",
    "own.resource_sites",
    "own.primary_bank",
    "own.secondary_bank",
    "own.primary_reserve",
    "own.secondary_reserve",
    "own.primary_spendable",
    "own.secondary_spendable",
    "local.engagement_ratio",
    "opponent.aggression_commitment",
    "opponent.economic_commitment",
    "opponent.vertical_mobility_support",
    "opponent.protected_surface_force_support",
    "opponent.light_surface_force_support",
    "opponent.concealment_support",
    "opponent.deployment_capacity_estimate",
    "opponent.deployment_capacity_lower",
    "opponent.deployment_capacity_upper",
    "opponent.visible_deployment_capacity",
)
SCALAR_FEATURES = BASE_FEATURES + LIVE_FEATURES
GROUPS = ("controlled", "contact", "candidate")


def feature_vector(feature):
    if feature is None:
        return [0.0, 0.0, 0.0, 1.0, 0.0]
    return [
        feature.value if feature.value is not None else 0.0,
        float(feature.value is not None),
        float(feature.supported),
        feature.uncertainty,
        feature.age_seconds / 90 if feature.age_seconds is not None else 0.0,
    ]


class StarCraftPolicy(nn.Module):
    def __init__(self):
        super().__init__()
        self.entity = nn.Sequential(nn.Linear(len(ENTITY_FEATURES) * 5, 64), nn.Tanh())
        self.scalar = nn.Sequential(nn.Linear(len(SCALAR_FEATURES) * 5 + 6, 128), nn.Tanh())
        self.core = RecurrentCore(512, 256)
        self.objective = nn.Linear(256, 7)
        self.target = nn.Sequential(nn.Linear(256 + 64, 64), nn.Tanh(), nn.Linear(64, 1))
        self.production = nn.Linear(256, 7)
        self.scouting = nn.Linear(256, 4)
        self.value = nn.Linear(256, 1)

    def forward(self, belief, memory):
        state = belief.shared
        if state.feature_version not in {FEATURE_VERSION, LIVE_FEATURE_VERSION}:
            raise ValueError("Unsupported neural feature schema")
        device = next(self.parameters()).device
        features = {f.name: f for f in state.features}
        scalar = [v for name in SCALAR_FEATURES for v in feature_vector(features.get(name))]
        capabilities = dict(state.capabilities)
        scalar += [state.time_seconds / 3600, state.elapsed_seconds / 2] + [
            float(capabilities.get(name, False))
            for name in ("strategy", "production", "reconnaissance", "expansion")
        ]
        encoded_scalar = self.scalar(torch.tensor([scalar], dtype=torch.float32, device=device))
        pools, candidate_encodings = [], {}
        for group in GROUPS:
            entities = [e for e in state.entities if e.group == group]
            if entities:
                rows = []
                for entity in entities:
                    values = {f.name: f for f in entity.features}
                    rows.append([v for name in ENTITY_FEATURES for v in feature_vector(values.get(name))])
                encoded = self.entity(torch.tensor(rows, dtype=torch.float32, device=device))
                pools.append(torch.cat((encoded.mean(0), encoded.max(0).values)).unsqueeze(0))
                if group == "candidate":
                    candidate_encodings = {e.handle: row for e, row in zip(entities, encoded, strict=True)}
            else:
                pools.append(torch.zeros(1, 128, device=device))
        latent = self.core(
            torch.cat([encoded_scalar, *pools], dim=-1),
            memory,
            torch.tensor([state.episode_start], device=device),
        )
        locations = torch.stack(
            [
                candidate_encodings.get(t.handle, torch.zeros(64, device=device))
                if t
                else torch.zeros(64, device=device)
                for t in belief.targets
            ]
        )
        target_logits = self.target(torch.cat((latent.expand(16, -1), locations), dim=-1)).flatten()
        logits = torch.cat(
            (
                self.objective(latent).flatten(),
                target_logits,
                self.production(latent).flatten(),
                self.scouting(latent).flatten(),
            )
        )
        return logits, self.value(latent).flatten()[0], latent
