"""The small semantic GRU with independent strategy/economy action heads."""

from torch import nn

from source.games.starcraft2.learned_actions import FEATURE_VERSION, HEAD_WIDTHS
from source.games.starcraft2.learned_execution import ECONOMY_FEATURES
from source.games.starcraft2.model import SCALAR_FEATURES, StarCraftPolicy

MODEL_VERSION = "sc2-strategy-economy-gru256-v1"


class LearnedPolicy(StarCraftPolicy):
    model_version = MODEL_VERSION
    feature_version = FEATURE_VERSION
    supported_features = (FEATURE_VERSION,)
    scalar_features = SCALAR_FEATURES + ECONOMY_FEATURES

    def __init__(self):
        super().__init__()
        self.objective = nn.Linear(256, HEAD_WIDTHS[0])
        self.production = nn.Linear(256, HEAD_WIDTHS[2])
        self.scouting = nn.Linear(256, HEAD_WIDTHS[3])
