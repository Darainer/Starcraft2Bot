"""Independent, uncertainty-bearing public-evidence estimates, not calibrated probabilities."""

from dataclasses import asdict, dataclass, field, replace
from math import exp, isfinite

from source.game_ontology import ontology_document, parameter, technology_signals

MODEL_VERSION = "beliefs-v1"
ONTOLOGY_ID = ontology_document()["ontology_id"]
AIR_TECH = technology_signals("air")
ARMOR_TECH = technology_signals("armored_ground")
CLOAK_TECH = technology_signals("cloak")
PRODUCTION = frozenset(ontology_document()["early_production_signals"])


@dataclass(frozen=True)
class SignalBelief:
    support: float | None = None
    uncertainty: float = 1.0
    evidence_age: float | None = None
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrengthBelief:
    estimate: float | None = None
    lower: float = 0.0
    upper: float | None = None
    uncertainty: float = 1.0
    evidence_age: float | None = None


@dataclass(frozen=True)
class OpponentBeliefs:
    model_version: str = MODEL_VERSION
    ontology_id: str = ONTOLOGY_ID
    time: float = 0.0
    aggression: SignalBelief = field(default_factory=SignalBelief)
    economy: SignalBelief = field(default_factory=SignalBelief)
    air: SignalBelief = field(default_factory=SignalBelief)
    armored_ground: SignalBelief = field(default_factory=SignalBelief)
    light_ground: SignalBelief = field(default_factory=SignalBelief)
    cloak: SignalBelief = field(default_factory=SignalBelief)
    enemy_army: StrengthBelief = field(default_factory=StrengthBelief)
    relative_army: StrengthBelief = field(default_factory=StrengthBelief)

    def to_dict(self):
        return asdict(self)

    def relative_to(self, own_supply):
        enemy = self.enemy_army
        relative = StrengthBelief(
            own_supply / enemy.estimate if enemy.estimate else None,
            own_supply / enemy.upper if enemy.upper else 0,
            own_supply / enemy.lower if enemy.lower else None,
            enemy.uncertainty,
            enemy.evidence_age,
        )
        return replace(self, relative_army=relative)

    def questions(self):
        """Decision relevance times uncertainty; unit/route cost is charged later."""
        return (
            (
                "commitment",
                max(self.aggression.uncertainty, self.economy.uncertainty)
                * (1.5 if self.time < 240 else 0.5),
            ),
            (
                "technology",
                max(self.air.uncertainty, self.armored_ground.uncertainty, self.cloak.uncertainty),
            ),
            ("army", self.enemy_army.uncertainty * 1.4),
            ("expansions", self.economy.uncertainty * 0.9),
        )


def beliefs_from_dict(data):
    if (
        not data
        or data.get("model_version") != MODEL_VERSION
        or data.get("ontology_id", ONTOLOGY_ID) != ONTOLOGY_ID
    ):
        return None
    values = {"time": data.get("time", 0)}
    for name in ("aggression", "economy", "air", "armored_ground", "light_ground", "cloak"):
        value = dict(data.get(name, {}))
        value["evidence"] = tuple(value.get("evidence", ()))
        values[name] = SignalBelief(**value)
    for name in ("enemy_army", "relative_army"):
        values[name] = StrengthBelief(**data.get(name, {}))
    return OpponentBeliefs(**values)


def _age(now, seen, limit):
    if not isinstance(seen, (int, float)) or not isfinite(seen):
        return None
    age = now - seen
    return max(0, age) if -0.000001 <= age <= limit else None


def _signal(now, facts):
    # Each fact appears once. Repeated observations refresh its timestamp, not
    # its multiplicity; a lack of vision never contributes negative evidence.
    weighted = [
        (value, weight * exp(-max(0, now - seen) / parameter("confidence_decay_seconds")), seen, reason)
        for value, weight, seen, reason in facts
    ]
    total = sum(weight for _, weight, _, _ in weighted)
    if not total:
        return SignalBelief()
    return SignalBelief(
        sum(value * weight for value, weight, _, _ in weighted) / total,
        max(parameter("minimum_signal_uncertainty"), exp(-total / 3)),
        max(0, now - max(seen for _, _, seen, _ in weighted)),
        tuple(reason for _, _, _, reason in weighted),
    )


class OpponentBeliefModel:
    def __init__(self):
        self.legacy_tech_seen = {}

    def observe(self, seconds, intel, own_supply=0):
        if not isfinite(seconds) or not isfinite(own_supply) or seconds < 0 or own_supply < 0:
            raise ValueError("Invalid belief observation time or own supply")
        facts = {
            name: [] for name in ("aggression", "economy", "air", "armored_ground", "light_ground", "cloak")
        }
        tech = intel.get("known_enemy_tech_evidence")
        if tech is None:
            # Legacy recordings lack per-building timestamps. Do not refresh
            # their old technology merely because an unrelated unit was seen.
            for kind in intel.get("known_enemy_tech", []):
                self.legacy_tech_seen.setdefault(kind, seconds)
            tech = [
                {"kind": kind, "seen_seconds": self.legacy_tech_seen[kind]}
                for kind in set(intel.get("known_enemy_tech", []))
            ]
        unique_tech = {}
        for item in tech:
            if _age(seconds, item.get("seen_seconds", -999), parameter("tech_memory_seconds")) is not None:
                key = str(item.get("tag", item["kind"]))
                unique_tech[key] = item
        for item in unique_tech.values():
            kind, seen = item["kind"], item["seen_seconds"]
            for name, kinds in (("air", AIR_TECH), ("armored_ground", ARMOR_TECH), ("cloak", CLOAK_TECH)):
                if kind in kinds:
                    # A production path is possible tech, not a confirmed army.
                    facts[name].append((0.8, 2.0, seen, f"Observed {kind}"))
        production = [item for item in unique_tech.values() if item["kind"] in PRODUCTION]
        if seconds < 180 and len(production) >= 2:
            facts["aggression"].append(
                (0.75, 2, max(p["seen_seconds"] for p in production), "Multiple early production structures")
            )
        incoming = intel.get("incoming_force") or {}
        warning = intel.get("rush_warning") or {}
        for evidence, reason in (
            (incoming, "Observed approaching combat force"),
            (warning, "Observed early/proxy warning"),
        ):
            seen = evidence.get("seen_seconds", -999)
            if _age(seconds, seen, 45) is not None and (
                evidence.get("supply", evidence.get("approaching_supply", 0)) >= 4 or evidence.get("reason")
            ):
                facts["aggression"].append((0.95, 3, seen, reason))
                break  # Incoming force and rush warning can describe the same sighting.
        bases = {
            tuple(b["position"]): b
            for b in intel.get("known_enemy_bases", [])
            if _age(seconds, b.get("seen_seconds", -999), 180) is not None
        }
        if len(bases) >= 2:
            facts["economy"].extend(
                (0.85, 1.5, b["seen_seconds"], f"Occupied base at {position}")
                for position, b in bases.items()
            )
        force = intel.get("composition_intel", {})
        age = _age(seconds, force.get("seen_seconds", -999), parameter("army_memory_seconds"))
        units = intel.get("enemy_unit_evidence")
        if units is not None:
            units = {
                str(u["tag"]): u
                for u in units
                if _age(seconds, u.get("seen_seconds", -999), parameter("army_memory_seconds")) is not None
            }
            roles = {
                "air": [u for u in units.values() if u.get("air")],
                "armored_ground": [u for u in units.values() if not u.get("air") and u.get("armored")],
                "light_ground": [u for u in units.values() if not u.get("air") and u.get("light")],
            }
            for name, members in roles.items():
                amount = len(members) if name == "light_ground" else sum(u.get("supply", 0) for u in members)
                threshold = 8 if name == "light_ground" else 4 if name == "air" else 6
                if amount >= threshold:
                    for unit in members:
                        contribution = 1 if name == "light_ground" else max(0, unit.get("supply", 0))
                        facts[name].append(
                            (
                                1,
                                contribution / threshold * 3,
                                unit["seen_seconds"],
                                f"Observed {unit.get('kind', name)}",
                            )
                        )
        elif age is not None:
            for name, key, threshold in (
                ("air", "air_supply", 4),
                ("armored_ground", "armored_ground_supply", 6),
                ("light_ground", "light_ground_count", 8),
            ):
                amount = force.get(key, 0)
                if amount >= threshold:
                    facts[name].append(
                        (
                            1,
                            min(6, amount / threshold * 3),
                            force["seen_seconds"],
                            f"Observed {key}={amount:g}",
                        )
                    )
        observed = intel.get("visible_enemy_force") or {}
        visible = (
            observed.get("supply", 0)
            if _age(seconds, observed.get("seen_seconds", -999), 5) is not None
            else 0
        )
        if units is not None:
            remembered = sum(max(0, u.get("supply", 0)) for u in units.values())
            # Each contact ages independently. A new Marine cannot refresh a
            # remembered army's supply or its aggregate uncertainty.
            evidence_age = (
                sum(max(0, u.get("supply", 0)) * (seconds - u["seen_seconds"]) for u in units.values())
                / remembered
                if remembered
                else 0
            )
            retained_estimate = sum(
                max(0, u.get("supply", 0)) * exp(-(seconds - u["seen_seconds"]) / 180) for u in units.values()
            )
        else:
            remembered = force.get("supply", 0) if age is not None else 0
            seen = force.get("seen_seconds", -999)
            evidence_age = max(0, seconds - seen) if seen >= 0 else 0
            retained_estimate = remembered * exp(-evidence_age / 180)
        remembered = max(visible, remembered)
        army = StrengthBelief()
        if remembered > 0:
            # This is a heuristic range in army supply, not a confidence interval
            # or a weapon/terrain-aware combat prediction. Unseen forces remain possible.
            estimate = max(visible, retained_estimate)
            upper = min(200, max(visible, remembered) + max(12, remembered * 0.75 + evidence_age * 0.35))
            uncertainty = 1 - min(0.75, remembered / 80) * exp(-evidence_age / 60)
            army = StrengthBelief(estimate, visible, upper, uncertainty, evidence_age)
        beliefs = OpponentBeliefs(
            time=seconds,
            enemy_army=army,
            **{name: _signal(seconds, values) for name, values in facts.items()},
        )
        return beliefs.relative_to(own_supply)
