"""Player-view assessment/fact stream -> portable semantics and domain mappings.

This initial view deliberately marks unavailable observation blocks unsupported.
It is not yet a complete neural input or a claim of calibrated beliefs.
"""

import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import isfinite

from source.game_ontology import parameter
from source.opponent_beliefs import ONTOLOGY_ID
from source.scouting_facts import FACT_SCHEMA
from source.strategic_plan import Assessment
from source.strategy_core.contracts import Candidate, Feature, StrategicStateV1

FEATURE_VERSION = "sc2-semantic-features-v1"
NORMALIZATION_VERSION = "sc2-fixed-scales-v1"
TARGET_CAPACITY = 16
TARGET_MEMORY_SECONDS = 90
SIGNALS = (
    ("aggression", "opponent.aggression_commitment"),
    ("economy", "opponent.economic_commitment"),
    ("air", "opponent.vertical_mobility_support"),
    ("armored_ground", "opponent.protected_surface_force_support"),
    ("light_ground", "opponent.light_surface_force_support"),
    ("cloak", "opponent.concealment_support"),
)


def opaque(prefix, identity):
    return prefix + sha256(identity.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True)
class Permissions:
    strategy: bool
    production: bool
    scouting: bool
    expansion: bool
    reserve_minerals: int
    reserve_gas: int


@dataclass(frozen=True)
class Target:
    id: str
    handle: str
    position: tuple[float, float]
    role: str
    visible: bool
    age_seconds: float
    travel: float


@dataclass(frozen=True)
class BeliefStateV1:
    assessment: Assessment
    permissions: Permissions
    targets: tuple[Target | None, ...]
    shared: StrategicStateV1
    facts_json: str | None
    target_overflow: int
    schema_version: str = "sc2-belief-state-v1"
    domain_ontology_version: str = ONTOLOGY_ID

    def to_dict(self):
        result = asdict(self)
        result.pop("facts_json")
        result["facts"] = json.loads(self.facts_json) if self.facts_json is not None else None
        return result


def target_table(state):
    ids = [target.id for target in state.targets]
    if len(set(ids)) != len(ids) or set(ids) & {"home", "rally", "threat"}:
        raise ValueError("Conflicting candidate identities")
    result = [
        Target("home", opaque("c", "home"), state.home, "home", True, 0, 0),
        Target("rally", opaque("c", "rally"), state.rally, "assembly", True, 0, 0),
        Target("threat", opaque("c", "threat"), state.threat, "threat", True, 0, 0)
        if state.threat is not None
        else None,
    ]
    eligible = [t for t in state.targets if 0 <= state.time - t.seen_at <= TARGET_MEMORY_SECONDS]
    for target in sorted(eligible, key=lambda t: (-t.value, t.travel, t.id))[:13]:
        if any(not isfinite(v) for v in (*target.position, target.travel, target.value)) or target.travel < 0:
            raise ValueError("Invalid target geometry")
        result.append(
            Target(
                target.id,
                opaque("c", target.id),
                target.position,
                "economic_site" if target.economic else "search_site",
                target.visible,
                state.time - target.seen_at,
                target.travel,
            )
        )
    return tuple(result + [None] * (TARGET_CAPACITY - len(result)))


def from_assessment(state, settings, *, facts=None, elapsed_seconds=0.0, episode_start=False):
    """Snapshot legal inputs; metadata (build, seed, result, profile) is never encoded.

    `facts` is one output of ScoutingFacts.observe, at this assessment's time.
    Raw observations/oracle labels must not be supplied in its place.
    """
    settings.validate()
    state = deepcopy(state)
    strategy = (
        settings.enabled and settings.attack and settings.strategy == "auto" and not settings.strategy_script
    )
    permissions = Permissions(
        bool(strategy),
        bool(strategy and settings.production and settings.adaptive_composition),
        bool(strategy and settings.scouting),
        bool(strategy and settings.expansion),
        settings.reserve_minerals,
        settings.reserve_gas,
    )
    targets = target_table(state)
    evidence = (opaque("e", f"assessment:{state.version}"),)

    def observed(name, value, scale=1.0):
        return Feature(name, value / scale, "fraction", 0, 0, evidence)

    features = [
        observed(
            "candidates.omitted_count",
            max(0, sum(0 <= state.time - t.seen_at <= TARGET_MEMORY_SECONDS for t in state.targets) - 13),
        ),
        observed("own.deployment_capacity", state.army_supply, 200),
        observed("own.force_health", state.health),
        observed("own.workforce", state.workers, 80),
        observed("own.resource_sites", state.bases, 8),
        observed("own.primary_bank", state.minerals, 1000),
        observed("own.secondary_bank", state.gas, 500),
        observed("own.primary_reserve", settings.reserve_minerals, 1000),
        observed("own.secondary_reserve", settings.reserve_gas, 500),
        observed("own.primary_spendable", max(0, state.minerals - settings.reserve_minerals), 1000),
        observed("own.secondary_spendable", max(0, state.gas - settings.reserve_gas), 500),
        Feature(
            "local.engagement_ratio",
            state.local_advantage if state.local_fight_observed and state.local_advantage < 10 else None,
            "ratio",
            0 if state.local_fight_observed and state.local_advantage < 10 else 1,
            0 if state.local_fight_observed and state.local_advantage < 10 else None,
            evidence if state.local_fight_observed and state.local_advantage < 10 else (),
        ),
    ]
    beliefs = state.opponent_beliefs
    delay = state.time - beliefs.time if beliefs is not None else -1
    for domain_name, name in SIGNALS:
        signal = getattr(beliefs, domain_name) if beliefs is not None else None
        age = signal.evidence_age + delay if signal is not None and signal.evidence_age is not None else None
        valid = delay >= 0 and age is not None and 0 <= age <= parameter("army_memory_seconds")
        features.append(
            Feature(
                name,
                signal.support if valid else None,
                "heuristic_support",
                signal.uncertainty if valid else 1,
                age if valid else None,
                tuple(opaque("e", e) for e in signal.evidence) if valid else (),
            )
        )
    strength = beliefs.enemy_army if beliefs is not None else None
    age = (
        strength.evidence_age + delay if strength is not None and strength.evidence_age is not None else None
    )
    valid = delay >= 0 and age is not None and 0 <= age <= parameter("army_memory_seconds")
    for suffix, value in (
        ("estimate", strength.estimate if strength else None),
        ("lower", strength.lower if strength else None),
        ("upper", strength.upper if strength else None),
    ):
        features.append(
            Feature(
                f"opponent.deployment_capacity_{suffix}",
                value / 200 if valid and value is not None else None,
                "fraction",
                strength.uncertainty if valid else 1,
                age if valid else None,
                (opaque("e", f"belief:{beliefs.time}:enemy_army"),) if valid else (),
            )
        )
    facts_json = None
    visible = None
    fact_evidence = ()
    if facts is not None:
        if facts.get("schema_version") != FACT_SCHEMA or not isfinite(
            facts.get("time_seconds", float("nan"))
        ):
            raise ValueError("Unsupported fact stream")
        if abs(facts["time_seconds"] - state.time) > 0.000001:
            raise ValueError("Fact and assessment clocks must match")
        # Store only domain facts, never arbitrary metadata attached by a caller.
        facts_json = json.dumps(
            {
                key: facts[key]
                for key in (
                    "schema_version",
                    "time_seconds",
                    "own",
                    "enemy_contacts",
                    "technology_history",
                    "expansion_history",
                    "site_inspections",
                    "fact_presence",
                )
            },
            sort_keys=True,
            allow_nan=False,
        )
        visible = (
            sum(
                c["visible_count"] * c["supply_per_unit"]
                for c in facts["enemy_contacts"]
                if c["combat_nonworker"]
            )
            / 200
        )
        fact_evidence = (opaque("e", facts_json),)
    features.append(
        Feature(
            "opponent.visible_deployment_capacity",
            visible,
            "fraction",
            0 if facts is not None else 1,
            0 if facts is not None else None,
            fact_evidence,
        )
    )
    features.extend(
        Feature(name, None, "unsupported", supported=False)
        for name in (
            "own.income",
            "own.production_queues",
            "actors.control_eligibility",
            "execution.observed_effects",
            "intent.current",
            "opponent.courses_of_action",
        )
    )
    shared = StrategicStateV1(
        state.time,
        elapsed_seconds,
        episode_start,
        tuple(features),
        tuple(Candidate(t.handle, t.role, t.visible, t.age_seconds, t.travel / 200) for t in targets if t),
        (
            ("strategy", permissions.strategy),
            ("production", permissions.production),
            ("reconnaissance", permissions.scouting),
            ("expansion", permissions.expansion),
        ),
        FEATURE_VERSION,
        NORMALIZATION_VERSION,
    )
    return BeliefStateV1(
        state,
        permissions,
        targets,
        shared,
        facts_json,
        int(next(f.value for f in features if f.name == "candidates.omitted_count")),
    )
