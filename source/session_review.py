"""Incremental, sampled trade and movement evidence for reproducible match reviews."""

from collections import Counter
from math import hypot

from sc2.ids.unit_typeid import UnitTypeId as U

from source.economy_assistant import ARMY_TARGETS

OFFENSIVE = {"pressure", "contain", "counterattack", "finish"}


class SessionReview:
    def __init__(self):
        self.high_water = {}
        self.windows = {}
        self.targets = []
        self.last_wave = None
        self.moves = {}
        self.movement = Counter()
        self.own_units = {}

    def observe(self, row):
        now = row["game_loop"] / 22.4
        decision = row.get("decision", {})
        plan = decision.get("plan", {})
        objective = plan.get("objective")
        main = next((m for m in plan.get("missions", []) if m.get("role") == "main"), {})
        target = main.get("target_id")
        point = main.get("target")
        wave = decision.get("wave") or {}
        phase = wave.get("phase")
        if objective in OFFENSIVE and target and point:
            if self.targets and target != self.targets[-1][0]:
                old = self.targets[-1]
                distance = hypot(point[0] - old[2][0], point[1] - old[2][1])
                if distance >= 12:
                    self.movement["offensive_target_switches"] += 1
                    if len(self.targets) >= 2 and target == self.targets[-2][0] and now - old[1] <= 20:
                        self.movement["short_target_reversals"] += 1
            if not self.targets or target != self.targets[-1][0]:
                self.targets.append((target, now, point))
                self.targets = self.targets[-2:]
            if (
                self.last_wave
                and self.last_wave[:2] == (target, wave.get("id"))
                and {phase, self.last_wave[2]} == {"advance", "regroup"}
            ):
                self.movement["advance_regroup_transitions"] += 1
            self.last_wave = target, wave.get("id"), phase
        else:
            self.targets.clear()
            self.last_wave = None
        if wave.get("cohesion_fraction", 0) > 1.0001:
            self.movement["invalid_cohesion_samples"] += 1
        observation = row.get("observation", {}).get("observation", {})
        raw_units = observation.get("raw_data", {}).get("units", [])
        present = {str(u["tag"]) for u in raw_units if "tag" in u}
        present.update(str(p["tag"]) for u in raw_units for p in u.get("passengers", []) if "tag" in p)
        units = {
            str(u["tag"]): u
            for u in observation.get("raw_data", {}).get("units", [])
            if u.get("alliance") == "Self" and "tag" in u
        }
        own = dict(units)
        own.update({str(p["tag"]): p for u in units.values() for p in u.get("passengers", []) if "tag" in p})
        missing = [u for tag, u in self.own_units.items() if tag not in present]
        self.own_units = own
        army_types = {kind.value for kind in ARMY_TARGETS}
        missing_army = Counter(U(u["unit_type"]).name for u in missing if u.get("unit_type") in army_types)
        missing_economy = Counter(
            U(u["unit_type"]).name
            for u in missing
            if u.get("unit_type") in {U.PROBE.value, U.NEXUS.value, U.ASSIMILATOR.value}
        )
        for order in decision.get("orders", []):
            tag = str(order["unit_tag"])
            unit = units.get(tag)
            if unit is None or not isinstance(order.get("target"), list):
                continue
            position, destination = unit.get("pos", {}), order["target"]
            dx, dy = destination[0] - position.get("x", 0), destination[1] - position.get("y", 0)
            length = hypot(dx, dy)
            if length < 6:
                continue  # Short combat kiting is not a long movement reversal.
            self.movement["sampled_long_move_orders"] += 1
            previous = self.moves.get(tag)
            if (
                previous
                and now - previous[0] <= 10
                and dx / length * previous[1] + dy / length * previous[2] < -0.5
            ):
                self.movement["sampled_long_move_reversals"] += 1
            self.moves[tag] = now, dx / length, dy / length
        self.moves = {tag: value for tag, value in self.moves.items() if now - value[0] <= 10}
        details = observation.get("score", {}).get("score_details", {})
        counters = {
            f"{side}_{category}": sum(
                details.get(f"{side}_{resource}", {}).get(category, 0) for resource in ("minerals", "vespene")
            )
            for side in ("lost", "killed")
            for category in ("army", "economy", "technology")
        }
        counters["killed_structures"] = details.get("killed_value_structures", 0)
        first = not self.high_water
        deltas = {}
        for name, value in counters.items():
            previous = self.high_water.get(name, 0)
            current = max(previous, value)
            self.high_water[name] = current
            deltas[name] = 0 if first else current - previous
        if any(deltas.values()) or missing_army or missing_economy:
            bucket = int(now // 15)
            window = self.windows.setdefault(
                bucket,
                {
                    "start": bucket * 15,
                    "end": (bucket + 1) * 15,
                    "objectives": Counter(),
                    "targets": set(),
                    "own_army_disappearances": Counter(),
                    "own_economy_disappearances": Counter(),
                    "local_advantage_min": None,
                    "health_min": None,
                    "last_army_center": None,
                    "observed_enemy_composition": {},
                    **dict.fromkeys(counters, 0),
                },
            )
            for name, delta in deltas.items():
                window[name] += delta
            window["objectives"][objective or "unknown"] += 1
            window["own_army_disappearances"].update(missing_army)
            window["own_economy_disappearances"].update(missing_economy)
            assessment = decision.get("assessment", {})
            for key, source in (("local_advantage_min", "local_advantage"), ("health_min", "health")):
                if source in assessment:
                    window[key] = (
                        min(window[key], assessment[source])
                        if window[key] is not None
                        else assessment[source]
                    )
            if wave.get("center"):
                window["last_army_center"] = wave["center"]
            window["observed_enemy_composition"] = (
                row.get("scouting", {}).get("intel", {}).get("composition_intel", {}).get("composition", {})
            )
            if target:
                window["targets"].add(target)

    def summary(self):
        all_windows = [
            {
                **w,
                "objectives": dict(w["objectives"]),
                "targets": sorted(w["targets"]),
                "own_army_disappearances": dict(w["own_army_disappearances"]),
                "own_economy_disappearances": dict(w["own_economy_disappearances"]),
            }
            for w in self.windows.values()
        ]
        windows = [
            w
            for w in all_windows
            if w["lost_army"] >= 300 and w["lost_army"] > max(200, w["killed_army"] * 1.5)
        ]
        windows.sort(key=lambda w: w["lost_army"] - w["killed_army"], reverse=True)
        movement = {
            key: self.movement[key]
            for key in (
                "offensive_target_switches",
                "short_target_reversals",
                "advance_regroup_transitions",
                "invalid_cohesion_samples",
                "sampled_long_move_orders",
                "sampled_long_move_reversals",
            )
        }
        return {
            "movement": movement,
            "resource_scores": dict(self.high_water),
            "army_trade_ratio": round(
                self.high_water.get("killed_army", 0) / max(1, self.high_water.get("lost_army", 0)), 3
            ),
            "bad_trade_window_count": len(windows),
            "corroborated_bad_trade_window_count": sum(bool(w["own_army_disappearances"]) for w in windows),
            "worst_trade_windows": windows[:5],
            "worst_economy_loss_windows": sorted(
                (w for w in all_windows if w["lost_economy"] >= 400),
                key=lambda w: w["lost_economy"],
                reverse=True,
            )[:3],
        }
