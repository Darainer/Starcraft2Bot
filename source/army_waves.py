"""Persistent army cohorts, assembly gates, role formations and reinforcement batches."""

from collections import Counter
from statistics import median

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2


def center(units):
    return Point2((median(u.position.x for u in units), median(u.position.y for u in units)))


class ArmyWaves:
    def __init__(self):
        self.members = set()
        self.reinforcements = set()
        self.wave_id = 0
        self.phase = "assemble"
        self.center = None
        self.last_state = {}

    def reset(self):
        self.members.clear()
        self.reinforcements.clear()
        self.phase = "assemble"
        self.center = None

    def plan(self, bot, army, objective, rally, policy):
        units = army.filter(bot.control.eligible)
        alive = {u.tag for u in units}
        self.members.intersection_update(alive)
        self.reinforcements.intersection_update(alive)
        core = units.filter(lambda u: u.tag in self.members)

        def supply(group):
            return sum(bot.calculate_supply_cost(u.type_id) for u in group)

        difficulty = getattr(bot, "opponent_difficulty", "Medium")
        hard_supply = {
            "MediumHard": 40,
            "Hard": 64,
            "Harder": 72,
            "VeryHard": 96,
            "CheatVision": 96,
            "CheatMoney": 96,
            "CheatInsane": 112,
        }.get(difficulty, 0)
        minimum_supply = max(24, policy["attack_supply"], hard_supply)
        minimum_units = (
            {
                "MediumHard": 10,
                "Hard": 16,
                "Harder": 18,
                "VeryHard": 24,
                "CheatVision": 24,
                "CheatMoney": 24,
                "CheatInsane": 28,
            }.get(difficulty, 12)
            if hard_supply
            else (8 if bot.settings.profile == "pressure" else 10)
        )
        composition_ok = (
            bot.settings.profile != "robotics" or bool(units.of_type({U.IMMORTAL, U.COLOSSUS}))
        ) and (bot.settings.profile != "air" or units(U.VOIDRAY).amount >= 4)
        if hard_supply:
            heavy_ready = (
                bot.settings.immortals > 0 and units(U.IMMORTAL).amount >= min(2, bot.settings.immortals)
            ) or (bot.settings.colossi > 0 and units(U.COLOSSUS).amount >= min(2, bot.settings.colossi))
            composition_ok = composition_ok and heavy_ready
        intel = getattr(bot, "scout_report", {})
        force_intel = intel.get("peak_enemy_force") or intel.get("last_enemy_force") or {}
        enemy_gate = None
        if (
            hard_supply
            and intel.get("force_intel_ready")
            and bot.time - force_intel.get("seen_seconds", -999) <= 180
        ):
            # Scale against the largest recent sighting; fresh intel is still
            # required to launch, so an old partial sighting cannot clear the gate.
            enemy_gate = min(96, int(force_intel.get("supply", 0) * 1.05 + 0.999))
            minimum_supply = max(minimum_supply, enemy_gate)
        if intel.get("flying", 0) >= 2 and len(units.filter(lambda u: u.can_attack_air)) < 2:
            composition_ok = False
        if force_intel.get("air_supply", 0) >= 8:
            anti_air = units.filter(lambda unit: unit.can_attack_air)
            anti_air_supply = supply(anti_air)
            composition_ok = composition_ok and anti_air_supply >= min(
                32, max(16, int(force_intel["air_supply"] * 0.75 + 0.999))
            )
        # A complete high-difficulty force should not camp forever if the scout
        # loses contact. Use the large army gate as a bounded launch fallback.
        scouting_timeout = hard_supply and bot.time >= 600 and supply(units) >= minimum_supply
        scouted = not bot.settings.scouting or bool(intel.get("force_intel_ready")) or scouting_timeout
        readiness = sum(bot.calculate_supply_cost(u.type_id) for u in units if u.distance_to(rally) <= 10)
        fraction = readiness / max(1, supply(units))
        reason = "Assemble a complete, scouted attack wave"
        cohesion_fraction = 0
        if core and supply(core) < policy["continue_supply"]:
            self.reset()
            core = units.filter(lambda u: False)
            reason = "Wave losses require rebuilding and regrouping"
        if not core and (
            len(units) >= minimum_units
            and supply(units) >= minimum_supply
            and fraction >= 0.8
            and composition_ok
            and scouted
        ):
            self.members = {u.tag for u in units}
            core = units
            self.wave_id += 1
            self.phase = "advance"
            reason = "Assembled wave launched"
        destinations = {}
        if not core:
            self.phase = "assemble"
            for index, unit in enumerate(sorted(units, key=lambda u: u.tag)):
                destinations[unit.tag] = ("move", rally.offset(((index % 5 - 2) * 1.8, (index // 5) * 1.8)))
        else:
            anchor = center(core)
            self.center = anchor
            reserves = units.filter(lambda u: u.tag not in self.members)
            # Nearby warp-ins can safely join the existing force; remote units
            # remain in staging until they form a reinforcement group.
            for unit in reserves:
                if unit.distance_to(anchor) <= 12:
                    self.members.add(unit.tag)
            core = units.filter(lambda u: u.tag in self.members)
            anchor = center(core)
            self.center = anchor
            reserves = units.filter(lambda u: u.tag not in self.members)
            batch = reserves.filter(lambda u: u.tag in self.reinforcements)
            if not batch and len(reserves) >= 6 and supply(reserves) >= 12:
                gathered = reserves.filter(lambda u: u.distance_to(rally) <= 10)
                if len(gathered) >= 6:
                    self.reinforcements = {u.tag for u in gathered}
                    batch = gathered
            cohesion = sum(bot.calculate_supply_cost(u.type_id) for u in core if u.distance_to(anchor) <= 9)
            coherent = cohesion / max(1, supply(core)) >= 0.8
            cohesion_fraction = cohesion / max(1, supply(core))
            engaged = any(
                u.is_visible and u.can_attack and u.distance_to(anchor) < 10 for u in bot.enemy_units
            )
            self.phase = "engage" if engaged else "advance" if coherent else "regroup"
            waypoint = (
                anchor.towards(objective, min(12, anchor.distance_to(objective))) if coherent else anchor
            )
            if engaged:
                waypoint = anchor
            direction = objective - anchor
            length = max(direction.length, 1)
            forward = Point2((direction.x / length, direction.y / length))
            for index, unit in enumerate(sorted(core, key=lambda u: u.tag)):
                depth = (
                    2 if unit.type_id == U.ZEALOT else -4 if unit.type_id in {U.SENTRY, U.HIGHTEMPLAR} else -1
                )
                lateral = (index % 5 - 2) * 1.8
                slot = waypoint.offset(
                    (forward.x * depth - forward.y * lateral, forward.y * depth + forward.x * lateral)
                )
                destinations[unit.tag] = (
                    "attack" if (coherent or engaged) and unit.can_attack else "move",
                    slot,
                )
            for index, unit in enumerate(reserves):
                target = rally.offset(((index % 5 - 2) * 1.8, (index // 5) * 1.8))
                if unit.tag in self.reinforcements:
                    batch_center = center(batch) if batch else rally
                    target = batch_center.towards(anchor, min(12, batch_center.distance_to(anchor)))
                destinations[unit.tag] = ("move", target)
            reason = (
                "Engage as a wave"
                if engaged
                else "Advance the coherent wave"
                if coherent
                else "Wait for stragglers before advancing"
            )
        state = {
            "id": self.wave_id,
            "phase": self.phase,
            "reason": reason,
            "members": sorted(self.members),
            "reinforcement_members": sorted(self.reinforcements),
            "minimum_supply": minimum_supply,
            "enemy_force_supply_gate": enemy_gate,
            "minimum_units": minimum_units,
            "opponent_difficulty": difficulty,
            "assembled_fraction": fraction,
            "composition_ready": composition_ok,
            "scouted": scouted,
            "scouting_timeout": bool(scouting_timeout),
            "enemy_force_intel": intel.get("last_enemy_force"),
            "center": list(self.center) if self.center is not None else None,
            "cohesion_fraction": cohesion_fraction,
            "core_supply": supply(core),
            "composition": dict(Counter(unit.type_id.name for unit in units)),
        }
        self.last_state = state
        return destinations, state
