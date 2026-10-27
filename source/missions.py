"""Persistent, disjoint squads; local execution can abort one operation at a time."""

from collections import deque
from math import atan2, ceil, cos, hypot, pi, sin

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.action_intents import ActionExecutor, ActionIntent
from source.army_waves import center
from source.combat_assessment import favorable, visible_threats
from source.endgame_sweep import EndgameSweep
from source.strategy_profiles import PROFILES


def retreat_geometry(contacts):
    """Cache SDK weapon data once per observation, outside the route search."""
    return tuple(
        (
            e.position.x,
            e.position.y,
            e.radius,
            max(6 if e.type_id == U.BUNKER else 0, e.ground_range),
            e.air_range,
            max(24 if e.type_id == U.BUNKER else 1, e.ground_dps),
            max(1, e.air_dps),
            e.can_attack_ground or e.type_id == U.BUNKER,
            e.can_attack_air,
        )
        for e in contacts
    )


def retreat_waypoint(bot, unit, goal, contacts, geometry=None):
    """Choose a short traversable escape using only currently visible weapons."""
    origin = unit.position
    ox, oy = origin
    flying, radius = unit.is_flying, unit.radius
    geometry = retreat_geometry(contacts) if geometry is None else geometry
    threats = [
        (x, y, (ar if flying else gr) + er + radius + 3, ad if flying else gd)
        for x, y, er, gr, ar, gd, ad, ground, air in geometry
        if (air if flying else ground) and hypot(x - ox, y - oy) < max(gr, ar) + 18
    ]
    area = getattr(bot.game_info, "playable_area", None)

    def traversable(point):
        x, y = point
        if area and not (area.x <= x < area.x + area.width and area.y <= y < area.y + area.height):
            return False
        if flying:
            return True
        steps = max(1, ceil(hypot(x - ox, y - oy)))
        return all(
            bot.in_pathing_grid(Point2((ox + (x - ox) * i / steps, oy + (y - oy) * i / steps)))
            for i in range(1, steps + 1)
        )

    if not threats and traversable(goal):
        return goal

    def danger(x, y):
        return sum(dps * max(0, reach - hypot(ex - x, ey - y)) for ex, ey, reach, dps in threats)

    direction = atan2(goal.y - oy, goal.x - ox)
    distance = 10 if threats else min(10, hypot(goal.x - ox, goal.y - oy))
    candidates = [origin]
    for i in range(16):
        angle = direction + i * pi / 8
        point = Point2((ox + cos(angle) * distance, oy + sin(angle) * distance))
        if traversable(point):
            candidates.append(point)

    def cost(point):
        x, y = point
        exposure = sum(danger(ox + (x - ox) * f, oy + (y - oy) * f) for f in (0.25, 0.5, 0.75, 1))
        return exposure + danger(x, y) * 4 + hypot(x - goal.x, y - goal.y) * 0.15

    return min(candidates, key=cost)


class MissionPlanner:
    def __init__(self):
        self.records = {}
        self.executor = ActionExecutor()
        self.events = deque(maxlen=32)
        self.sweep = EndgameSweep()

    def reset(self):
        self.records.clear()
        self.executor.assign({})
        self.sweep.active = False

    def execute(self, bot, army, plan, state, waves, preserve_combat=True):
        available = army.filter(bot.control.eligible)
        contacts = visible_threats(bot)
        geometry = retreat_geometry(contacts)
        remaining = set(available.tags)
        destinations, assignments, records, retreat_goals = {}, {}, {}, {}
        wave_report = None
        evidence = {target.id for target in state.targets}
        for mission_id, old in self.records.items():
            old_id = old.get("target_id", "")
            if (
                old_id.isdecimal()
                and old_id not in evidence
                and bot.is_visible(Point2(old["target"]))
                and bot.enemy_structures.find_by_tag(int(old_id)) is None
            ):
                self.events.append(
                    {"mission": mission_id, "target_id": old_id, "time": bot.time, "result": "target_cleared"}
                )
        for spec in sorted(plan.missions, key=lambda m: -m.priority):
            old = self.records.get(spec.id, {})
            target = Point2(spec.target)
            candidates = available.filter(lambda u: u.tag in remaining)
            if spec.role == "deny":
                candidates = candidates.of_type({U.ZEALOT, U.STALKER, U.ADEPT})
            if spec.role != "main":
                threats = contacts.closer_than(20, target)
                candidates = candidates.filter(
                    lambda u, threats=threats: (
                        u.can_attack
                        and (
                            not threats
                            or any(u.can_attack_air if e.is_flying else u.can_attack_ground for e in threats)
                        )
                    )
                )
            ordered = sorted(
                candidates, key=lambda u: (u.tag not in old.get("members", []), u.distance_to(target), u.tag)
            )
            tags, supply = [], 0
            for unit in ordered:
                cost = bot.calculate_supply_cost(unit.type_id) if unit.can_attack else 0
                if spec.role == "main" or supply + cost <= spec.supply_budget:
                    tags.append(unit.tag)
                    supply += cost
            if spec.role != "main" and supply < spec.minimum_supply:
                self.events.append({"mission": spec.id, "time": bot.time, "result": "insufficient_force"})
                continue
            remaining.difference_update(tags)
            squad = available.tags_in(tags)
            phase = "assemble"
            record = {
                "members": tags,
                "target": list(target),
                "target_id": spec.target_id,
                "role": spec.role,
                "supply": supply,
            }
            if not squad:
                records[spec.id] = {**record, "phase": phase}
                continue
            anchor = center(squad)
            nearby = contacts.closer_than(16, anchor)
            local = squad.closer_than(20, anchor)
            damaged = (
                sum(u.health + u.shield for u in local)
                < sum(u.health_max + u.shield_max for u in local) * 0.35
            )
            lost_members = old.get("supply", supply) - supply
            abort = (nearby and not favorable(local, nearby, 0.85)) or damaged
            if spec.role == "deny":
                abort |= bool(contacts.closer_than(20, target)) and not favorable(
                    squad, contacts.closer_than(20, target), 1.3
                )
                abort |= lost_members >= 4
            if (
                abort
                or (spec.role == "main" and plan.objective == "recover")
                or (old.get("phase") == "recover" and bot.time < old.get("recover_until", 0))
            ):
                phase = "recover"
                goal = Point2(old.get("retreat_goal", state.home))
                if spec.target_id == "script" and plan.objective == "recover":
                    goal = target
                elif (
                    old.get("phase") != "recover"
                    or not bot.townhalls.ready.closer_than(2, goal)
                    or contacts.closer_than(14, goal)
                ):
                    safe_bases = bot.townhalls.ready.filter(lambda base: not contacts.closer_than(14, base))
                    goal = safe_bases.closest_to(anchor).position if safe_bases else Point2(state.home)
                record["retreat_goal"] = list(goal)
                until = old.get("recover_until", bot.time + 8)
                record["recover_until"] = max(until, bot.time + 8 if abort else until)
                if old.get("phase") != "recover":
                    self.events.append(
                        {
                            "mission": spec.id,
                            "target_id": spec.target_id,
                            "time": bot.time,
                            "result": "unfavorable_fight",
                        }
                    )
                for unit in squad:
                    retreat_goals[unit.tag] = goal
                    destinations[unit.tag] = ("move", retreat_waypoint(bot, unit, goal, contacts, geometry))
                if spec.role == "main":
                    waves.reset()
            elif spec.role == "main":
                if plan.objective in {"develop", "recover", "stabilize"}:
                    waves.reset()
                    phase = "recover" if plan.objective == "recover" else "hold"
                    for unit in squad:
                        destinations[unit.tag] = (spec.mode if unit.can_attack else "move", target)
                elif plan.objective == "finish":
                    if not self.sweep.active:
                        self.sweep.start()
                    orders, report = self.sweep.plan(
                        bot, squad, bot.enemy_structures, contacts, bot.townhalls.ready
                    )
                    destinations.update(orders)
                    phase = "search"
                    record["sweep"] = report
                elif bot.settings.army_waves:
                    self.sweep.active = False
                    if plan.objective == "contain":
                        guards = contacts.closer_than(22, target)
                        distance = max(
                            (max(u.ground_range, u.air_range) + u.radius + 10 for u in guards), default=16
                        )
                        target = target.towards(Point2(state.home), distance)
                    orders, wave_report = waves.plan(
                        bot, squad, target, Point2(state.rally), PROFILES[bot.settings.profile]
                    )
                    destinations.update(orders)
                    phase = wave_report["phase"]
                else:
                    waves.reset()
                    phase = "engage"
                    for unit in squad:
                        destinations[unit.tag] = (spec.mode if unit.can_attack else "move", target)
            else:
                coherent = sum(u.distance_to(anchor) < 10 for u in squad) / len(squad) >= 0.8
                phase = "engage" if nearby else "travel" if coherent else "assemble"
                destination = target if coherent else anchor
                for unit in squad:
                    destinations[unit.tag] = ("attack" if coherent else "move", destination)
            for unit in squad:
                assignments[unit.tag] = f"{spec.id}:{spec.target_id}:{phase == 'recover'}"
            records[spec.id] = {**record, "phase": phase}
        self.records = records
        self.executor.assign(assignments)
        orders = []
        for tag, (mode, target) in destinations.items():
            unit = available.find_by_tag(tag)
            if unit is None:
                continue
            critical = unit.health + unit.shield < (unit.health_max + unit.shield_max) * 0.25
            if critical and tag not in retreat_goals:
                mode, target = "move", retreat_waypoint(bot, unit, Point2(state.home), contacts, geometry)
            # Preserve weapon execution between tactical updates.
            fighting = mode == "attack" or (
                preserve_combat and not critical and not assignments[tag].endswith(":True")
            )
            if fighting and any(unit.target_in_range(enemy) for enemy in contacts):
                continue
            intent = ActionIntent(
                tag,
                self.executor.assignments[tag][1],
                bot.state.game_loop,
                bot.state.game_loop + 8,
                mode,
                tuple(target),
            )
            if self.executor.execute(bot, intent):
                orders.append({"unit_tag": tag, "action": mode, "target": list(target)})
        return {"missions": records, "wave": wave_report, "orders": orders, "events": list(self.events)}
