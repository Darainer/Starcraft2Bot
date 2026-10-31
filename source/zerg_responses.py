"""Experimental SC2 opening responses from positive, timestamped scouting only.

Support/uncertainty and timing thresholds are development heuristics. A response
is an investment choice, not a calibrated prediction of the configured AI build.
"""

from math import isfinite


class ZergResponseSelector:
    def __init__(self):
        self.technology = {}
        self.expansions = {}
        self.time = -1

    def observe(self, now, intel):
        if not isfinite(now) or now < 0 or now < self.time:
            raise ValueError("Invalid scouting time")
        self.time = now
        for item in intel.get("known_enemy_tech_evidence", []):
            seen = item.get("seen_seconds", -999)
            if not isinstance(seen, (int, float)) or not isfinite(seen) or not 0 <= seen <= now:
                continue
            key = (str(item.get("tag", item["kind"])), item["kind"])
            prior = self.technology.get(key)
            self.technology[key] = {
                "kind": item["kind"],
                "first_seen": min(seen, prior["first_seen"]) if prior else seen,
                "last_seen": max(seen, prior["last_seen"]) if prior else seen,
            }
        for base in intel.get("enemy_bases", []):
            if base.get("expansion"):
                key = str(base["tag"]) if "tag" in base else str(tuple(base["position"]))
                prior = self.expansions.get(key)
                self.expansions[key] = {
                    "first_seen": prior["first_seen"] if prior else now,
                    "last_seen": now,
                    "observed_build_progress": base.get("build_progress"),
                }
        # Sightings are deduplicated and age individually. Empty/missing vision
        # supplies no proof of absent army, absent expansion or a completed scout.
        units = {
            str(unit["tag"]): unit
            for unit in intel.get("enemy_unit_evidence", [])
            if isinstance(unit.get("seen_seconds"), (int, float))
            and isfinite(unit["seen_seconds"])
            and 0 <= now - unit["seen_seconds"] <= 45
        }
        army = sum(max(0, unit.get("supply", 0)) for unit in units.values())
        roach_path = sum(
            max(0, unit.get("supply", 0))
            for unit in units.values()
            if unit.get("kind") in {"ROACH", "RAVAGER"}
        )
        pool = [
            item
            for item in self.technology.values()
            if item["kind"] == "SPAWNINGPOOL" and item["first_seen"] <= 90 and now - item["last_seen"] <= 180
        ]
        warren = [
            item
            for item in self.technology.values()
            if item["kind"] == "ROACHWARREN" and item["first_seen"] <= 210 and now - item["last_seen"] <= 90
        ]
        expansion = [
            item
            for item in self.expansions.values()
            if item["first_seen"] <= 150 and now - item["last_seen"] <= 180
        ]
        response, hypothesis, uncertainty = "baseline", "unresolved", 1.0
        reason = "No sufficiently fresh positive opening evidence; retain R2 baseline"
        evidence = []
        until = 0
        if now <= 360 and roach_path >= 4:
            response, hypothesis, uncertainty = "early_robotics", "observed_roach_path_force", 0.25
            reason = "Fresh Roach/Ravager force supports a Robotics ground response"
            evidence = ["Fresh observed Roach/Ravager supply >= 4"]
            until = min(
                360,
                max(
                    unit["seen_seconds"]
                    for unit in units.values()
                    if unit.get("kind") in {"ROACH", "RAVAGER"}
                )
                + 45,
            )
        elif now <= 240 and warren:
            response, hypothesis, uncertainty = "early_robotics", "early_armored_technology", 0.4
            reason = "Early observed Roach Warren supports Robotics investment"
            evidence = ["Early Roach Warren observed"]
            until = min(240, max(item["last_seen"] for item in warren) + 90)
        elif now <= 240 and pool and not expansion:
            response, hypothesis, uncertainty = "early_robotics", "early_ground_technology", 0.65
            reason = "Early observed Pool supports a bounded ground-counter investment"
            evidence = ["Spawning Pool observed by 90 seconds"]
            until = min(240, max(item["last_seen"] for item in pool) + 180)
        elif expansion:
            hypothesis, uncertainty = "observed_economic_commitment", 0.45
            reason = "Positively observed early expansion retains R2 economic spending"
            evidence = ["Enemy expansion observed by 150 seconds"]
        if until <= now:
            response, until = "baseline", 0
        return {
            "model_version": "zerg-response-v1",
            "time": now,
            "response": response,
            "hypothesis": hypothesis,
            "uncertainty": uncertainty,
            "reason": reason,
            "evidence": evidence,
            "valid_until": until,
            "observed_army_supply": army,
            "observed_roach_path_supply": roach_path,
            "first_pool_seen": min(
                (item["first_seen"] for item in self.technology.values() if item["kind"] == "SPAWNINGPOOL"),
                default=None,
            ),
            "first_warren_seen": min(
                (item["first_seen"] for item in self.technology.values() if item["kind"] == "ROACHWARREN"),
                default=None,
            ),
            "first_expansion_seen": min(
                (item["first_seen"] for item in self.expansions.values()), default=None
            ),
            "expansion_observation_kind": "First positive sighting, not inferred construction start",
            "questions": ["opening_technology", "expansion_occupancy", "army_commitment"],
        }
