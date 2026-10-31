"""Transparent information/cost ranking; coefficients are experimental heuristics."""

from dataclasses import dataclass

from source.game_ontology import parameter


@dataclass(frozen=True)
class ScoutOption:
    question: str
    target: tuple[float, float]
    relevance_uncertainty: float
    useful_visibility: float
    travel_seconds: float
    replacement_minerals: float
    replacement_gas: float
    exposure: float = 0
    worker_seconds: float = 0
    recent_loss_multiplier: float = 1

    def utility(self):
        information = (
            parameter("information_value_scale") * self.relevance_uncertainty * self.useful_visibility
        )
        replacement = self.replacement_minerals + parameter("gas_resource_weight") * self.replacement_gas
        return (
            information
            - self.travel_seconds
            - parameter("worker_income_cost_per_second") * self.worker_seconds
            - self.exposure * replacement * self.recent_loss_multiplier
        )


def choose_scout(options):
    """Deterministic tie handling; nonpositive options justify retaining a safe patrol."""
    best = max(options, key=lambda option: option.utility(), default=None)
    return best if best is not None and best.utility() > 0 else None
