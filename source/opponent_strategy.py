"""Transparent, observational strategy beliefs. No opponent configuration input.

Normalized heuristic scores are not calibrated probabilities. Unknown is a real
output: missing vision never establishes that an enemy lacks units or expansions.
"""

from math import exp

LABELS = ("Rush", "Timing", "Power", "Macro", "Air")
MODEL_VERSION = "scouting-v1"


class OpponentStrategyModel:
    def __init__(self):
        self.first_pressure = None
        self.peak_opening_pressure = 0
        self.first_tech = {}
        self.first_two_bases = None
        self.first_three_bases = None
        self.first_two_expansions = None

    def observe(self, seconds, intel):
        """Consume scouting's public evidence contract, never the runtime report."""
        seconds = round(seconds, 6)

        def fresh(seen, limit):
            return -0.000001 <= seconds - seen <= limit

        for kind in intel.get("known_enemy_tech", []):
            self.first_tech.setdefault(kind, seconds)
        bases = [b for b in intel.get("known_enemy_bases", []) if fresh(b.get("seen_seconds", -999), 180)]
        unique = {tuple(b["position"]): b for b in bases}
        if len(unique) >= 2 and self.first_two_bases is None:
            self.first_two_bases = seconds
        if len(unique) >= 3 and self.first_three_bases is None:
            self.first_three_bases = seconds
        if sum(b.get("expansion", False) for b in unique.values()) >= 2 and self.first_two_expansions is None:
            self.first_two_expansions = seconds
        incoming = intel.get("incoming_force") or {}
        warning = intel.get("rush_warning", {})
        pressure = max(
            incoming.get("supply", 0) if fresh(incoming.get("seen_seconds", -999), 5) else 0,
            warning.get("approaching_supply", 0) if fresh(warning.get("seen_seconds", -999), 5) else 0,
        )
        if pressure >= 4 and self.first_pressure is None:
            self.first_pressure = seconds
        if seconds <= 450:
            self.peak_opening_pressure = max(self.peak_opening_pressure, pressure)
        force = intel.get("composition_intel", {})
        if not fresh(force.get("seen_seconds", -999), 90):
            force = {}
        supply = force.get("supply", 0)
        air = force.get("air_supply", 0)
        heavy = force.get("armored_ground_supply", 0)
        scores = dict.fromkeys(LABELS, 0.0)
        evidence, tactics = [], []

        def support(label, weight, signal, at):
            scores[label] += weight
            evidence.append({"supports": label, "weight": weight, "signal": signal, "observed_at": at})

        if self.first_pressure is not None:
            if self.first_pressure <= 210:
                support("Rush", 5, "Combat force on our approaches before 3:30", self.first_pressure)
            elif self.first_pressure <= 420:
                support("Timing", 4, "First observed pressure between 3:30 and 7:00", self.first_pressure)
        pool = self.first_tech.get("SPAWNINGPOOL")
        if pool is not None and pool <= 90:
            support("Rush", 2, "Spawning Pool positively observed early", pool)
        if self.first_two_expansions is not None and self.first_two_expansions <= 420:
            support("Macro", 5, "Two enemy expansion sites occupied by 7:00", self.first_two_expansions)
        elif self.first_three_bases is not None and self.first_three_bases <= 600:
            support("Macro", 4, "Three enemy bases positively observed by 10:00", self.first_three_bases)
        elif self.first_two_bases is not None and self.first_two_bases <= 240:
            support("Macro", 1.5, "Two enemy bases positively observed by 4:00", self.first_two_bases)
        if heavy >= 16 and heavy / max(1, supply) >= 0.4:
            support("Power", 4, "Substantial armored ground force", force.get("seen_seconds", seconds))
            tactics.append("armored_ground")
        if self.peak_opening_pressure >= 24:
            support("Power", 2, "Large observed force committed before 7:30", self.first_pressure)
        if air >= 6 and air / max(1, supply) >= 0.35:
            support("Air", 6, "Significant combat air investment", force.get("seen_seconds", seconds))
            tactics.append("combat_air")
        advanced_air = [
            self.first_tech[k]
            for k in ("SPIRE", "GREATERSPIRE", "FUSIONCORE", "FLEETBEACON")
            if k in self.first_tech
        ]
        if advanced_air:
            support("Air", 2, "Advanced air tech positively observed", min(advanced_air))
        if force.get("light_ground_count", 0) >= 8:
            tactics.append("mass_light_ground")
        if pressure >= 4:
            tactics.append("home_pressure")
        if len(unique) >= 3 or sum(b.get("expansion", False) for b in unique.values()) >= 2:
            tactics.append("multiple_expansions")
        weights = {label: exp(score / 2) for label, score in scores.items()}
        total = sum(weights.values())
        probabilities = {label: value / total for label, value in weights.items()}
        ranked = sorted(probabilities, key=probabilities.get, reverse=True)
        best, second = ranked[:2]
        confidence = probabilities[best]
        last_seen = intel.get("last_seen_seconds", -999)
        age = max(0, seconds - last_seen) if last_seen <= seconds + 0.000001 else 999
        category = (
            best
            if evidence and age <= 120 and confidence >= 0.55 and confidence - probabilities[second] >= 0.15
            else "Unknown"
        )
        return {
            "model_version": MODEL_VERSION,
            "time": seconds,
            "category": category,
            "leading_hypothesis": best if evidence else "Unknown",
            "confidence": round(confidence, 4),
            "probabilities": probabilities,
            "evidence_age_seconds": age,
            "first_observed_pressure_seconds": self.first_pressure,
            "evidence": evidence,
            "tactical_indicators": tactics,
            "control_enabled": False,
        }
