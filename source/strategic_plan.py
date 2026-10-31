"""Serializable policy contracts, independent of SC2 and model providers."""

from dataclasses import asdict, dataclass
from math import isfinite

from source.opponent_beliefs import OpponentBeliefs

Point = tuple[float, float]
OBJECTIVES = {"stabilize", "develop", "pressure", "contain", "counterattack", "finish", "recover"}
ROLES = {"main", "defend", "deny"}


@dataclass(frozen=True)
class Opportunity:
    id: str
    position: Point
    seen_at: float
    visible: bool
    economic: bool
    value: float
    defense: float
    advantage: float
    travel: float
    expansion: bool = False
    defender_supply: float = 0
    static_defense: bool = False


@dataclass(frozen=True)
class Assessment:
    version: int
    time: float
    profile: str
    army_supply: float
    army_count: int
    health: float
    local_advantage: float
    threat_supply: float
    home_advantage: float
    home: Point
    rally: Point
    threat: Point | None
    targets: tuple[Opportunity, ...]
    intel_age: float
    minerals: float
    gas: float
    workers: int
    bases: int
    production: tuple[tuple[str, int], ...]
    trade_bad: bool = False
    recently_defended: bool = False
    timing_ready: bool = False
    cleanup_ready: bool = False
    rush_warning: bool = False
    engagement_evidence_schema_version: int = 1
    local_fight_observed: bool = False
    raid_response_schema_version: int = 1
    raid_response_tags: tuple[int, ...] = ()
    raid_response_supply: float = 0
    raid_response_advantage: float = 0
    opening_hold: Point | None = None
    opponent_beliefs: OpponentBeliefs | None = None
    adaptive_composition: bool = False
    belief_control: bool = False
    response_policy: str = "baseline"
    response_policy_until: float = 0
    response_reason: str = "Retain baseline response"
    response_evidence: tuple[str, ...] = ()

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class MissionSpec:
    id: str
    role: str
    target_id: str
    target: Point
    supply_budget: float
    minimum_supply: float
    priority: int
    mode: str = "attack"
    require_visible: bool = False


@dataclass(frozen=True)
class StrategicPlan:
    id: int
    based_on: int
    created_at: float
    expires_at: float
    objective: str
    missions: tuple[MissionSpec, ...]
    production: tuple[tuple[str, int], ...]
    expand: bool
    reason: str
    scores: tuple[tuple[str, float], ...] = ()
    production_reason: str = "Recorded composition targets"
    scouting_requests: tuple[str, ...] = ()
    response_policy: str = "baseline"
    response_policy_until: float = 0
    response_reason: str = "Retain baseline response"
    response_evidence: tuple[str, ...] = ()

    def to_dict(self):
        return asdict(self)


def validate_plan(plan, state, max_age=5):
    """Reject stale/unsupported/infeasible proposals before activation."""
    if not isinstance(plan, StrategicPlan) or plan.objective not in OBJECTIVES:
        raise ValueError("Unsupported strategic plan")
    if (
        plan.response_policy not in {"baseline", "early_robotics"}
        or plan.response_policy != state.response_policy
    ):
        raise ValueError("Unsupported or superseded response policy")
    if plan.response_policy == "early_robotics" and not (
        isfinite(plan.response_policy_until)
        and state.time < plan.response_policy_until <= state.response_policy_until
        and plan.response_evidence
        and plan.response_evidence == state.response_evidence
    ):
        raise ValueError("Expired or unsupported response evidence")
    if len(set(plan.scouting_requests)) != len(plan.scouting_requests) or any(
        request not in {"commitment", "technology", "army", "expansions"}
        for request in plan.scouting_requests
    ):
        raise ValueError("Unsupported scouting question")
    if not (plan.based_on <= state.version and 0 <= state.time - plan.created_at <= max_age):
        raise ValueError("Stale or future assessment")
    if not state.time < plan.expires_at <= plan.created_at + 120:
        raise ValueError("Invalid plan expiry")
    targets = {target.id: target for target in state.targets}
    references = {key: value.position for key, value in targets.items()}
    references.update(home=state.home, rally=state.rally)
    if state.threat is not None:
        references["threat"] = state.threat
    ids = set()
    roles = set()
    total = 0.0
    for mission in plan.missions:
        if (
            mission.id in ids
            or mission.role in roles
            or mission.role not in ROLES
            or mission.mode not in {"move", "attack"}
        ):
            raise ValueError("Conflicting or unsupported mission")
        ids.add(mission.id)
        roles.add(mission.role)
        if mission.target_id not in references or mission.target != references[mission.target_id]:
            raise ValueError("Unknown target evidence")
        if mission.require_visible and not (
            mission.target_id in targets and targets[mission.target_id].visible
        ):
            raise ValueError("Mission requires current vision")
        if not all(isfinite(x) for x in (*mission.target, mission.supply_budget, mission.minimum_supply)):
            raise ValueError("Nonfinite mission parameters")
        if not 0 <= mission.minimum_supply <= mission.supply_budget <= state.army_supply:
            raise ValueError("Invalid mission allocation")
        total += mission.supply_budget
    if total > state.army_supply + 0.01 or "main" not in roles:
        raise ValueError("Shared army budget exceeded")
    names = dict(state.production)
    if len(dict(plan.production)) != len(plan.production) or any(
        name not in names or type(value) is not int or not 0 <= value <= 200
        for name, value in plan.production
    ):
        raise ValueError("Unsupported production targets")
    return plan
