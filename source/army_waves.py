"""Persistent army cohorts, assembly gates, role formations and reinforcement batches."""

from collections import Counter
from math import ceil, cos, pi, sin
from statistics import median

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2


def center(units):
    return Point2((median(u.position.x for u in units), median(u.position.y for u in units)))


def staging_slot(index, total, rally):
    """Place a unit in a compact, centered square staging formation."""
    columns = max(1, int(total**0.5))
    if columns * columns < total:
        columns += 1
    rows = (total + columns - 1) // columns
    column = index % columns
    row = index // columns
    return rally.offset(((column - (columns - 1) / 2) * 1.8, (row - (rows - 1) / 2) * 1.8))


def terrain_destination(bot, unit, point, goal):
    """Use engine pathfinding to a real goal when a geometric slot crosses terrain."""
    area = getattr(bot.game_info, "playable_area", None)

    def inside(position):
        return area is None or (
            area.x <= position.x < area.x + area.width and area.y <= position.y < area.y + area.height
        )

    if unit.is_flying:
        if inside(point):
            return point
        if inside(goal):
            return goal
        return Point2(
            (
                min(max(goal.x, area.x), area.x + area.width - 0.001),
                min(max(goal.y, area.y), area.y + area.height - 0.001),
            )
        )

    def walkable(position):
        return (
            area is None
            or (area.x <= position.x < area.x + area.width and area.y <= position.y < area.y + area.height)
        ) and bot.in_pathing_grid(position)

    origin = unit.position
    steps = max(1, ceil(origin.distance_to(point)))
    if all(
        walkable(
            Point2((origin.x + (point.x - origin.x) * i / steps, origin.y + (point.y - origin.y) * i / steps))
        )
        for i in range(1, steps + 1)
    ):
        return point
    # The engine can route around the obstruction to this destination. Do not
    # substitute another straight-line intermediate on the same blocked ray.
    if walkable(goal):
        return goal
    for radius in (2, 4, 6, 8):
        candidates = [goal.offset((cos(i * pi / 8) * radius, sin(i * pi / 8) * radius)) for i in range(16)]
        valid = [candidate for candidate in candidates if walkable(candidate)]
        if valid:
            return min(valid, key=lambda candidate: (unit.distance_to(candidate), candidate.x, candidate.y))
    return origin


class ArmyWaves:
    def __init__(self):
        self.members = set()
        self.reinforcements = set()
        self.wave_id = 0
        self.phase = "assemble"
        self.center = None
        self.last_state = {}
        self.regroup_anchor = None
        self.holding_positions = {}

    def reset(self):
        self.members.clear()
        self.reinforcements.clear()
        self.phase = "assemble"
        self.center = None
        self.last_state = {}
        self.regroup_anchor = None
        self.holding_positions.clear()

    def plan(self, bot, army, objective, rally, policy):
        units = army.filter(bot.control.eligible)
        alive = {u.tag for u in units}
        self.members.intersection_update(alive)
        self.reinforcements.intersection_update(alive)
        core = units.filter(lambda u: u.tag in self.members)

        def supply(group):
            return sum(bot.calculate_supply_cost(u.type_id) for u in group if u.can_attack)

        difficulty = getattr(bot, "opponent_difficulty", "Medium")
        minimum_supply = max(16, policy["attack_supply"])
        minimum_units = 6 if bot.settings.profile == "pressure" else 8
        composition_ok = (
            bot.settings.profile != "robotics" or bool(units.of_type({U.IMMORTAL, U.COLOSSUS}))
        ) and (bot.settings.profile != "air" or units(U.VOIDRAY).amount >= 4)
        intel = getattr(bot, "scout_report", {})
        force_intel = intel.get("composition_intel", {})
        if force_intel.get("air_supply", 0) >= 8 and bot.time - force_intel.get("seen_seconds", -999) <= 90:
            anti_air = units.filter(lambda unit: unit.can_attack_air)
            composition_ok &= supply(anti_air) >= min(16, force_intel["air_supply"] * 0.6)
        enemy_gate = None
        scouting_timeout = bot.time >= 120
        scouted = not bot.settings.scouting or bool(intel.get("enemy_seen")) or scouting_timeout
        ordered_units = sorted(units, key=lambda u: u.tag)
        readiness = sum(
            bot.calculate_supply_cost(unit.type_id)
            for index, unit in enumerate(ordered_units)
            if unit.can_attack
            and (
                unit.distance_to(rally) <= 10
                or unit.distance_to(staging_slot(index, len(ordered_units), rally)) <= 3
            )
        )
        fraction = readiness / max(1, supply(units))
        reason = "Assemble a complete, scouted attack wave"
        cohesion_fraction = 0
        if core and supply(core) < policy["continue_supply"]:
            self.reset()
            core = units.filter(lambda u: False)
            reason = "Wave losses require rebuilding and regrouping"
        if not core and (
            sum(unit.can_attack for unit in units) >= minimum_units
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
            for index, unit in enumerate(ordered_units):
                destinations[unit.tag] = ("move", staging_slot(index, len(ordered_units), rally))
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
            gathering = self.regroup_anchor if self.phase == "regroup" and self.regroup_anchor else anchor
            cohesion = supply(core.filter(lambda u: u.distance_to(gathering) <= 9))
            cohesion_fraction = cohesion / max(1, supply(core))
            coherent = cohesion_fraction >= (0.8 if self.phase == "regroup" else 0.7)
            engaged = any(
                u.is_visible and u.can_attack and u.distance_to(anchor) < 10 for u in bot.enemy_units
            )
            combat_targets = bot.enemy_units.filter(
                lambda enemy: (
                    enemy.is_visible
                    and enemy.can_be_attacked
                    and enemy.can_attack
                    and enemy.distance_to(anchor) < 20
                )
            )
            self.phase = "engage" if engaged else "advance" if coherent else "regroup"
            if self.phase == "regroup":
                self.regroup_anchor = gathering
                self.holding_positions = {
                    tag: point for tag, point in self.holding_positions.items() if tag in self.members
                }
                for unit in core.closer_than(9, gathering):
                    self.holding_positions.setdefault(unit.tag, unit.position)
            else:
                self.regroup_anchor = None
                self.holding_positions.clear()
            waypoint = (
                anchor.towards(objective, min(12, anchor.distance_to(objective))) if coherent else anchor
            )
            if engaged:
                waypoint = anchor
            direction = objective - anchor
            length = max(direction.length, 1)
            forward = Point2((direction.x / length, direction.y / length))
            for index, unit in enumerate(sorted(core, key=lambda u: u.tag)):
                if self.phase == "regroup":
                    destinations[unit.tag] = ("move", self.holding_positions.get(unit.tag, gathering))
                    continue
                depth = (
                    2 if unit.type_id == U.ZEALOT else -4 if unit.type_id in {U.SENTRY, U.HIGHTEMPLAR} else -1
                )
                lateral = (index % 5 - 2) * 1.8
                slot = waypoint.offset(
                    (forward.x * depth - forward.y * lateral, forward.y * depth + forward.x * lateral)
                )
                if engaged and unit.can_attack:
                    targets = combat_targets.filter(
                        lambda enemy, unit=unit: (
                            unit.can_attack_air if enemy.is_flying else unit.can_attack_ground
                        )
                    )
                    if targets and not any(unit.target_in_range(enemy) for enemy in targets):
                        # A formation slot around the stopped anchor may never
                        # bring this actor into weapon range. Close on a local
                        # combat contact; existing firing/retreat guards still
                        # arbitrate the order at mission and micro level.
                        slot = targets.closest_to(unit).position
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
        # Never leave an army attacking an unreachable geometric formation
        # slot: short points on a cliff can strand it beside the intended route.
        by_tag = {unit.tag: unit for unit in units}
        for tag, (mode, point) in list(destinations.items()):
            goal = (
                rally
                if self.phase == "assemble"
                else self.regroup_anchor or rally
                if self.phase == "regroup"
                else objective
                if tag in self.members
                else self.center or objective
                if tag in self.reinforcements
                else rally
            )
            destinations[tag] = (mode, terrain_destination(bot, by_tag[tag], point, goal))
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
