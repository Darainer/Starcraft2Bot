"""Assign an opening Probe and a persistent Observer patrol for enemy-force warnings."""

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.endgame_sweep import BASE_TYPES, DEFENSE_TYPES

WORKERS = {U.PROBE, U.SCV, U.DRONE}


class ScoutController:
    def __init__(self):
        self.worker_tag = None
        self.last_assignment = -120
        self.worker_route_index = 0
        self.observer_route_index = 0

    def _observer_route(self, bot):
        return self._patrol_route(bot, include_enemy_expansions=True)

    def _worker_route(self, bot):
        return self._patrol_route(bot, include_enemy_expansions=False)

    def _patrol_route(self, bot, include_enemy_expansions):
        enemy = bot.enemy_start_locations[0] if bot.enemy_start_locations else bot.game_info.map_center
        bases = bot.townhalls.ready or [bot.start_location]
        points = []
        for base in bases:
            origin = base.position
            direction = enemy - origin
            length = max(direction.length, 1)
            forward = Point2((direction.x / length, direction.y / length))
            flank = Point2((-forward.y * 8, forward.x * 8))
            screen = origin.offset((forward.x * 18, forward.y * 18))
            points.extend((screen, screen.offset(flank), screen.offset((-flank.x, -flank.y))))

        if include_enemy_expansions:
            own_bases = [base.position for base in bases]
            sites = sorted(
                bot.expansion_locations_list,
                key=lambda location: enemy.distance_to(location),
            )
            for site in sites:
                if all(site.distance_to(base) > 12 for base in own_bases):
                    points.append(site)
            points.append(enemy)

        area = getattr(bot.game_info, "playable_area", None)
        if area is None:
            return points or [enemy]
        route = []
        for point in points:
            point = Point2(
                (
                    min(area.x + area.width - 2, max(area.x + 2, point.x)),
                    min(area.y + area.height - 2, max(area.y + 2, point.y)),
                )
            )
            if all(point.distance_to(existing) >= 6 for existing in route):
                route.append(point)
        return route or [bot.game_info.map_center]

    def _observer_tick(self, bot):
        all_observers = bot.units(U.OBSERVER).ready
        observer = all_observers.find_by_tag(next((u.tag for u in all_observers if bot.available(u)), -1))
        if observer is None:
            if all_observers:
                return {"phase": "human_owned", "unit_tag": all_observers.first.tag}
            return {"phase": "waiting_for_observer" if bot.settings.scouting else "disabled"}

        home = (
            bot.townhalls.ready.closest_to(bot.start_location).position
            if bot.townhalls.ready
            else bot.start_location
        )
        air_threats = bot.enemy_units.filter(
            lambda unit: unit.is_visible and unit.can_attack_air and unit.distance_to(observer) < 14
        )
        damaged = observer.health + observer.shield < (observer.health_max + observer.shield_max) * 0.55
        if air_threats or damaged:
            target = home
            phase = "retreating_from_air_threat" if air_threats else "retreating_damaged"
        else:
            route = self._observer_route(bot)
            self.observer_route_index %= len(route)
            if observer.distance_to(route[self.observer_route_index]) < 6:
                self.observer_route_index = (self.observer_route_index + 1) % len(route)
            target = route[self.observer_route_index]
            phase = "patrolling_approach"

        if observer.is_idle or not observer.orders or observer.distance_to(target) > 6:
            bot.issue(observer.move(target))
        return {
            "phase": phase,
            "unit_tag": observer.tag,
            "route_index": self.observer_route_index,
            "target": list(target),
            "visible_air_threats": len(air_threats),
        }

    def tick(self, bot):
        enemies = bot.enemy_units.filter(lambda unit: unit.is_visible)
        buildings = bot.enemy_structures.filter(lambda unit: unit.is_visible)
        report = getattr(bot, "scout_report", {})
        report.pop("composition_adjustment", None)
        enemy_force = enemies.filter(lambda unit: unit.type_id not in WORKERS)
        combat = enemy_force.filter(lambda unit: unit.can_attack)
        defenses = buildings.filter(lambda unit: unit.type_id in DEFENSE_TYPES)
        report["enemy_bases"] = [
            {
                "unit_type": base.type_id.name,
                "position": list(base.position),
                "visible_defenders": len(combat.closer_than(18, base)),
                "visible_defense_buildings": len(defenses.closer_than(22, base)),
                "workers_nearby": len(
                    enemies.filter(
                        lambda unit, base=base: unit.type_id in WORKERS and unit.distance_to(base) < 14
                    )
                ),
                "exposure_score": round(
                    100 / (1 + len(combat.closer_than(18, base)) + 2 * len(defenses.closer_than(22, base))),
                    1,
                ),
            }
            for base in buildings
            if base.type_id in BASE_TYPES
        ]
        composition = {}
        for unit in enemy_force:
            composition[unit.type_id.name] = composition.get(unit.type_id.name, 0) + 1
        force_supply = sum(bot.calculate_supply_cost(unit.type_id) for unit in enemy_force)
        air_supply = sum(bot.calculate_supply_cost(unit.type_id) for unit in enemy_force if unit.is_flying)
        armored_air_supply = sum(
            bot.calculate_supply_cost(unit.type_id)
            for unit in enemy_force
            if unit.is_flying and unit.is_armored
        )
        armored_ground_supply = sum(
            bot.calculate_supply_cost(unit.type_id)
            for unit in enemy_force
            if not unit.is_flying and unit.is_armored and unit.can_attack
        )
        light_ground_count = sum(
            unit.is_light and not unit.is_flying and unit.can_attack for unit in enemy_force
        )
        visible_force = (
            {
                "seen_seconds": bot.time,
                "unit_count": len(enemy_force),
                "supply": force_supply,
                "air_supply": air_supply,
                "armored_air_supply": armored_air_supply,
                "armored_ground_supply": armored_ground_supply,
                "light_ground_count": light_ground_count,
                "composition": composition,
                "estimated_strength": sum(
                    (unit.health + unit.shield) * max(unit.ground_dps, unit.air_dps, 1)
                    for unit in enemy_force
                ),
                "centroid": [
                    sum(unit.position.x for unit in enemy_force) / len(enemy_force),
                    sum(unit.position.y for unit in enemy_force) / len(enemy_force),
                ],
            }
            if enemy_force
            else None
        )
        report["visible_enemy_force"] = visible_force
        if visible_force:
            report["last_enemy_force"] = visible_force
            peak_force = report.get("peak_enemy_force")
            if peak_force is None or visible_force["supply"] > peak_force.get("supply", 0):
                report["peak_enemy_force"] = visible_force
        peak_force = report.get("peak_enemy_force")
        if peak_force and bot.time - peak_force.get("seen_seconds", -999) > 180:
            report.pop("peak_enemy_force", None)
        last_force = report.get("last_enemy_force")
        report["force_intel_ready"] = bool(
            last_force
            and bot.time - last_force["seen_seconds"] <= 90
            and (last_force["unit_count"] >= 3 or last_force["supply"] >= 6)
        )
        if enemies or buildings:
            report.update(
                enemy_seen=True,
                last_seen_seconds=bot.time,
                flying=sum(unit.is_flying for unit in enemies),
                armored=sum(unit.is_armored for unit in enemies),
                enemy_units=len(enemies),
                enemy_buildings=len(buildings),
            )
            if bot.settings.enabled and bot.settings.attack and bot.settings.adaptive_composition:
                total_supply = max(1, force_supply)
                air_share = air_supply / total_supply
                mixed_ground = armored_ground_supply >= 8 or light_ground_count >= 8
                if air_supply >= 8 and mixed_ground:
                    targets = {
                        "stalkers": 48 if air_share >= 0.35 else 40,
                        "voidrays": 8 if armored_air_supply >= 6 else 6,
                        "immortals": 6 if armored_ground_supply >= 8 else 4,
                        "colossi": 2,
                    }
                elif air_supply >= 8:
                    targets = {
                        "stalkers": 48 if air_share >= 0.4 else 40,
                        "voidrays": 8 if armored_air_supply >= 6 else 6,
                        "immortals": 4,
                        "colossi": 2,
                    }
                else:
                    targets = {
                        "stalkers": 32
                        if sum(unit.is_flying for unit in combat) >= 2
                        else bot.settings.stalkers,
                        "voidrays": bot.settings.voidrays,
                        "immortals": 10 if armored_ground_supply >= 8 else bot.settings.immortals,
                        "colossi": 4 if light_ground_count >= 8 else bot.settings.colossi,
                    }
                changes = {}
                for name, target in targets.items():
                    if getattr(bot.settings, name) != target:
                        setattr(bot.settings, name, target)
                        changes[name] = target
                if changes:
                    report["composition_adjustment"] = {
                        "enemy_composition": composition,
                        "targets": changes,
                    }

        bases = bot.townhalls.ready
        incoming = enemy_force.filter(lambda unit: any(unit.distance_to(base) < 120 for base in bases))
        incoming_supply = sum(bot.calculate_supply_cost(unit.type_id) for unit in incoming)
        report["incoming_force"] = (
            {
                "seen_seconds": bot.time,
                "unit_count": len(incoming),
                "supply": incoming_supply,
                "positions": [list(unit.position) for unit in incoming],
                "unit_types": [unit.type_id.name for unit in incoming],
            }
            if len(incoming) >= 3 and incoming_supply >= 6
            else None
        )
        bot.scout_report = report

        worker_status = self._worker_scout(bot, enemies, report)
        observer_status = self._observer_tick(bot) if bot.settings.scouting else {"phase": "disabled"}
        return {"phase": worker_status, "observer": observer_status, "intel": report}

    def _worker_scout(self, bot, enemies, report):
        if not bot.settings.enabled or not bot.settings.attack or not bot.settings.scouting:
            return "disabled"
        scout = bot.workers.find_by_tag(self.worker_tag) if self.worker_tag else None
        if scout is None:
            bot.scout_tag = None
            if bot.supply_workers >= 12 and bot.time - self.last_assignment >= 90:
                candidates = bot.workers.filter(
                    lambda unit: bot.available(unit) and (unit.is_idle or unit.is_gathering)
                )
                if candidates:
                    scout = candidates.closest_to(bot.game_info.map_center)
                    self.worker_tag = bot.scout_tag = scout.tag
                    self.last_assignment = bot.time
        if scout is None:
            return "observing" if report.get("enemy_seen") else "waiting_for_scout"
        if not bot.control.eligible(scout):
            return "human_owned"
        threatened = enemies.filter(lambda unit: unit.can_attack_ground and unit.distance_to(scout) < 8)
        if threatened or scout.health + scout.shield < 30:
            target = bot.start_location
            if scout.distance_to(target) <= 6:
                self.worker_tag = bot.scout_tag = None
                return "returned"
            phase = "returning"
        elif bot.enemy_start_locations:
            route = self._worker_route(bot)
            self.worker_route_index %= len(route)
            if scout.distance_to(route[self.worker_route_index]) < 6:
                self.worker_route_index = (self.worker_route_index + 1) % len(route)
            target = route[self.worker_route_index]
            phase = "scouting_enemy_start"
        else:
            return "no_known_start"
        if scout.is_idle or not scout.orders or scout.distance_to(target) > 5:
            bot.issue(scout.move(target), scout_order=True)
        return phase
