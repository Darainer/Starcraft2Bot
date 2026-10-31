"""Assign an opening Probe and a persistent Observer patrol for enemy-force warnings."""

from sc2.data import Race
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.combat_assessment import home_threats, observed_supply, visible_threats
from source.composition import composition_targets
from source.endgame_sweep import BASE_TYPES, DEFENSE_TYPES
from source.expansion_intel import expansion_sites, is_expansion
from source.opponent_beliefs import OpponentBeliefModel
from source.opponent_strategy import OpponentStrategyModel
from source.scouting_costs import ScoutCosts
from source.zerg_responses import ZergResponseSelector

WORKERS = {U.PROBE, U.SCV, U.DRONE}


class ScoutController:
    def __init__(self, revisit=False):
        self.worker_tag = None
        self.last_assignment = -120
        self.worker_route_index = 0
        self.observer_route_index = 0
        self.unit_memory = {}
        self.base_memory = {}
        self.tech_memory = {}
        self.opening_complete = False
        self.returning = False
        self.observer_visits = {}
        self.expansion_checks = {}
        self.observer_blocked = {}
        self.observer_goal = None
        self.opponent_model = OpponentStrategyModel()
        self.belief_model = OpponentBeliefModel()
        self.zerg_responses = ZergResponseSelector()
        self.revisit = revisit
        self.revisit_started = False
        self.revisit_active = False
        self.revisit_until = 0
        self.revisit_health = None
        self.costs = ScoutCosts()

    def _rush_warning(self, bot, combat, buildings, report):
        """Short-lived opening alerts from visible evidence, never opponent settings."""
        homes = [base.position for base in bot.townhalls.ready] or [bot.start_location]
        approaching = combat.filter(lambda u: any(u.distance_to(home) < 60 for home in homes))
        supply = sum(observed_supply(bot, unit) for unit in approaching)
        production = buildings.filter(lambda u: u.type_id in {U.BARRACKS, U.GATEWAY, U.WARPGATE})
        proxy = buildings.filter(
            lambda u: (
                u.type_id in {U.BARRACKS, U.GATEWAY, U.BUNKER, U.PHOTONCANNON, U.SPINECRAWLER}
                and any(u.distance_to(home) < 45 for home in homes)
            )
        )
        reason = None
        if bot.time < 300 and supply >= 4:
            reason = "Early combat force on our approaches"
        elif bot.time < 300 and proxy:
            reason = "Forward enemy production or static defense near home"
        elif bot.time < 150 and len(production) >= 2:
            reason = "Multiple early enemy production structures"
        warning = report.get("rush_warning", {})
        if reason:
            warning = {
                "reason": reason,
                "seen_seconds": bot.time,
                "expires_at": min(360, bot.time + (40 if supply >= 4 else 90)),
                "approaching_supply": supply,
                "evidence_tags": [str(u.tag) for u in (approaching if supply >= 4 else proxy or production)],
            }
        warning["active"] = bot.time < warning.get("expires_at", 0)
        report["rush_warning"] = warning

    def _update_expansion_sites(self, bot):
        bases = bot.enemy_structures.filter(lambda u: u.is_visible and u.type_id in BASE_TYPES)
        sites = expansion_sites(bot)
        for site in sites:
            key = tuple(site)
            info = self.expansion_checks.setdefault(
                key, {"position": list(site), "last_checked": -999, "status": "unknown"}
            )
            if bot.is_visible(site):
                info.update(
                    last_checked=bot.time,
                    status="occupied" if bases.closer_than(8, site) else "empty",
                )
        return [self.expansion_checks[tuple(site)] for site in sites]

    def _expansion_target(self, bot, observer, sites):
        due = [
            info
            for info in sites
            if bot.time - info["last_checked"] >= (20 if info["status"] == "occupied" else 45)
            and bot.time >= self.observer_blocked.get(tuple(info["position"]), 0)
        ]
        if not due:
            self.observer_goal = None
            return None
        # Finish the chosen inspection before reprioritizing; a moving Observer
        # must not oscillate between equally old sites.
        current = next((info for info in due if tuple(info["position"]) == self.observer_goal), None)
        enemy = bot.enemy_start_locations[0] if bot.enemy_start_locations else bot.game_info.map_center
        chosen = current or max(
            due,
            key=lambda info: (
                min(120, bot.time - info["last_checked"]) * 0.3
                + (30 if info["status"] == "occupied" else 0)
                - enemy.distance_to(Point2(info["position"])) * 0.4
                - observer.distance_to(Point2(info["position"])) * 0.2
            ),
        )
        self.observer_goal = tuple(chosen["position"])
        return Point2(self.observer_goal)

    def _observer_route(self, bot):
        return self._patrol_route(bot, include_enemy_expansions=True)

    def _worker_route(self, bot):
        if not bot.enemy_start_locations:
            return []
        enemy = bot.enemy_start_locations[0]
        sites = sorted(bot.expansion_locations_list, key=enemy.distance_to)
        natural = next((site for site in sites if site.distance_to(enemy) > 8), None)
        return ([natural] if natural is not None else []) + [enemy]

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
            enemy_sites = [site for site in sites if all(site.distance_to(base) > 12 for base in own_bases)]
            points = enemy_sites + [enemy] + points

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
        if not bot.settings.enabled or not bot.settings.attack or not bot.settings.scouting:
            return {"phase": "disabled"}
        sites = self._update_expansion_sites(bot)
        all_observers = bot.units(U.OBSERVER).ready
        observer = all_observers.find_by_tag(next((u.tag for u in all_observers if bot.available(u)), -1))
        if observer is None:
            if all_observers:
                return {"phase": "human_owned", "unit_tag": all_observers.first.tag}
            return {"phase": "waiting_for_observer" if bot.settings.scouting else "disabled"}

        self.costs.register(bot, observer, "observer")

        home = (
            bot.townhalls.ready.closest_to(bot.start_location).position
            if bot.townhalls.ready
            else bot.start_location
        )
        air_threats = visible_threats(bot).filter(
            lambda unit: unit.is_visible and unit.can_attack_air and unit.distance_to(observer) < 14
        )
        damaged = observer.health + observer.shield < (observer.health_max + observer.shield_max) * 0.55
        if air_threats or damaged:
            if self.observer_goal is not None:
                self.observer_blocked[self.observer_goal] = bot.time + 30
                self.observer_goal = None
            target = home
            phase = "retreating_from_air_threat" if air_threats else "retreating_damaged"
        else:
            route = [
                point
                for point in self._observer_route(bot)
                if bot.time >= self.observer_blocked.get(tuple(point), 0)
            ] or [home]
            self.observer_route_index %= len(route)
            if observer.distance_to(route[self.observer_route_index]) < 6:
                self.observer_route_index = (self.observer_route_index + 1) % len(route)
            target = route[self.observer_route_index]
            phase = "patrolling_approach"
            expansion = self._expansion_target(bot, observer, sites)
            if expansion is not None:
                target, phase = expansion, "scouting_expansion"
            plan = getattr(bot, "strategic_plan", None)
            if (
                expansion is None
                and plan is not None
                and plan.expires_at > bot.time
                and plan.objective in {"pressure", "contain", "counterattack"}
            ):
                main = next(m for m in plan.missions if m.role == "main")
                goal = Point2(main.target)
                if (
                    not bot.is_visible(goal)
                    and bot.time - self.observer_visits.get(tuple(goal), -999) >= 20
                    and bot.time >= self.observer_blocked.get(tuple(goal), 0)
                ):
                    target = goal.towards(home, min(8, goal.distance_to(home)))
                    phase = "scouting_mission_approach"
                    if observer.distance_to(target) < 4:
                        self.observer_visits[tuple(goal)] = bot.time

        if not isinstance(observer.order_target, Point2) or observer.order_target.distance_to(target) > 2:
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
        self._rush_warning(bot, combat, buildings, report)
        report["enemy_bases"] = [
            {
                "tag": str(base.tag),
                "unit_type": base.type_id.name,
                "position": list(base.position),
                "expansion": is_expansion(bot, base.position),
                "build_progress": base.build_progress,
                "defender_supply": sum(observed_supply(bot, u) for u in combat.closer_than(20, base)),
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
        force_supply = sum(observed_supply(bot, unit) for unit in enemy_force)
        air_supply = sum(observed_supply(bot, unit) for unit in enemy_force if unit.is_flying)
        armored_air_supply = sum(
            observed_supply(bot, unit) for unit in enemy_force if unit.is_flying and unit.is_armored
        )
        armored_ground_supply = sum(
            observed_supply(bot, unit)
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
                flying=sum(unit.is_flying for unit in combat),
                enemy_units=len(enemies),
                enemy_buildings=len(buildings),
            )
        self._remember(bot, combat, buildings, report)
        report["expansion_sites"] = self._update_expansion_sites(bot)
        bot.scout_report = report
        targets = composition_targets(bot)
        report["production_targets"] = targets
        report["composition_adjustment"] = {
            "enemy_composition": report["composition_intel"]["composition"],
            "targets": {
                name: value for name, value in targets.items() if value != getattr(bot.settings, name)
            },
        }

        incoming = home_threats(bot, enemy_force)
        incoming_supply = sum(observed_supply(bot, unit) for unit in incoming)
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
        report["opponent_strategy"] = self.opponent_model.observe(bot.time, report)
        report["opponent_beliefs"] = self.belief_model.observe(bot.time, report, bot.supply_army).to_dict()
        if bot.enemy_race == Race.Zerg:
            report["zerg_opening_response"] = self.zerg_responses.observe(bot.time, report)
        else:
            report.pop("zerg_opening_response", None)
        observer_status = self._observer_tick(bot) if bot.settings.scouting else {"phase": "disabled"}
        report["scouting_costs"] = self.costs.observe(bot, self.worker_tag)
        report["scout_revisit"] = {
            "enabled": self.revisit,
            "started": self.revisit_started,
            "active": self.revisit_active,
            "until": self.revisit_until,
        }
        return {"phase": worker_status, "observer": observer_status, "intel": report}

    def _remember(self, bot, combat, buildings, report):
        dead = getattr(bot.state, "dead_units", set())
        for unit in combat:
            self.unit_memory[unit.tag] = {
                "seen_seconds": bot.time,
                "kind": unit.type_id.name,
                "supply": observed_supply(bot, unit),
                "air": unit.is_flying,
                "armored": unit.is_armored,
                "light": unit.is_light,
            }
        self.unit_memory = {
            tag: info
            for tag, info in self.unit_memory.items()
            if tag not in dead and bot.time - info["seen_seconds"] <= 90
        }
        composition = {}
        for info in self.unit_memory.values():
            composition[info["kind"]] = composition.get(info["kind"], 0) + 1
        remembered = list(self.unit_memory.values())
        report["composition_intel"] = {
            "seen_seconds": max((u["seen_seconds"] for u in remembered), default=-999),
            "composition": composition,
            "supply": sum(u["supply"] for u in remembered),
            "air_supply": sum(u["supply"] for u in remembered if u["air"]),
            "armored_air_supply": sum(u["supply"] for u in remembered if u["air"] and u["armored"]),
            "armored_ground_supply": sum(u["supply"] for u in remembered if not u["air"] and u["armored"]),
            "light_ground_count": sum(not u["air"] and u["light"] for u in remembered),
        }
        for info in report["enemy_bases"]:
            self.base_memory[tuple(info["position"])] = {**info, "seen_seconds": bot.time}
        for position, info in list(self.base_memory.items()):
            point = Point2(position)
            if bot.time - info["seen_seconds"] > 180 or (
                bot.is_visible(point)
                and not any(b.type_id in BASE_TYPES and b.distance_to(point) < 5 for b in buildings)
            ):
                del self.base_memory[position]
        report["known_enemy_bases"] = list(self.base_memory.values())
        for building in buildings:
            self.tech_memory[building.tag] = (building.type_id.name, bot.time)
        self.tech_memory = {
            tag: value
            for tag, value in self.tech_memory.items()
            if tag not in dead and bot.time - value[1] <= 180
        }
        report["known_enemy_tech"] = sorted({value[0] for value in self.tech_memory.values()})
        report["known_enemy_tech_evidence"] = [
            {"tag": str(tag), "kind": kind, "seen_seconds": seen}
            for tag, (kind, seen) in self.tech_memory.items()
        ]
        report["enemy_unit_evidence"] = [{"tag": str(tag), **info} for tag, info in self.unit_memory.items()]

    def _worker_scout(self, bot, enemies, report):
        if not bot.settings.enabled or not bot.settings.attack or not bot.settings.scouting:
            self.worker_tag = bot.scout_tag = None
            return "disabled"
        scout = bot.workers.find_by_tag(self.worker_tag) if self.worker_tag else None
        if scout is None:
            bot.scout_tag = None
            if self.opening_complete:
                if not self._begin_revisit(bot, enemies, report):
                    return "opening_complete"
                scout = bot.workers.find_by_tag(self.worker_tag)
            if bot.supply_workers >= 12 and bot.time - self.last_assignment >= 90:
                candidates = bot.workers.filter(
                    lambda unit: bot.available(unit) and (unit.is_idle or unit.is_gathering)
                )
                if candidates:
                    scout = candidates.closest_to(bot.game_info.map_center)
                    self.worker_tag = bot.scout_tag = scout.tag
                    self.last_assignment = bot.time
                    self.costs.register(bot, scout, "worker")
        if scout is None:
            return "observing" if report.get("enemy_seen") else "waiting_for_scout"
        if not bot.control.eligible(scout):
            return "human_owned"
        threatened = enemies.filter(
            lambda unit: (
                unit.can_attack_ground
                and unit.distance_to(scout) < 8
                and (not self.revisit_active or unit.type_id not in WORKERS)
            )
        )
        health = scout.health + scout.shield
        worker_pressure = False
        damaged = False
        if self.revisit_active:
            worker_pressure = (
                len(
                    enemies.filter(
                        lambda unit: (
                            unit.type_id in WORKERS and unit.can_attack_ground and unit.distance_to(scout) < 8
                        )
                    )
                )
                >= 2
            )
            damaged = self.revisit_health is not None and health < self.revisit_health - 0.001
            self.revisit_health = health
        self.returning |= bool(threatened) or worker_pressure or damaged or health < 30
        route = self._worker_route(bot)
        if self.revisit_active:
            route = route[:1]
            self.returning |= bot.time >= self.revisit_until or bool(bot.units(U.OBSERVER).ready)
        if not route and not self.returning:
            self.returning = True
            return "no_known_start"
        if (
            not self.returning
            and scout.distance_to(route[self.worker_route_index % len(route)]) < 6
            and (not self.revisit_active or bot.is_visible(route[self.worker_route_index % len(route)]))
        ):
            self.worker_route_index += 1
            self.returning = self.worker_route_index >= len(route)
        if self.returning:
            target = bot.start_location
            if scout.distance_to(target) <= 6:
                self.costs.release(scout.tag)
                self.worker_tag = bot.scout_tag = None
                self.opening_complete = True
                self.revisit_active = False
                return "returned"
            phase = "returning"
        else:
            target = route[self.worker_route_index % len(route)]
            phase = "revisiting_enemy_natural" if self.revisit_active else "scouting_enemy_start"
        if not isinstance(scout.order_target, Point2) or scout.order_target.distance_to(target) > 2:
            bot.issue(scout.move(target), scout_order=True)
        return phase

    def _begin_revisit(self, bot, enemies, report):
        """One existing Probe, one natural inspection, bounded by time and safety."""
        if (
            not self.revisit
            or self.revisit_started
            or not 150 <= bot.time <= 210
            or bot.supply_workers < 16
            or bot.economic_emergency
            or bot.settings.strategy != "auto"
            or bot.settings.strategy_script
            or bot.units(U.OBSERVER).ready
            or enemies.filter(
                lambda unit: unit.can_attack_ground and unit.distance_to(bot.start_location) < 32
            )
        ):
            return False
        route = self._worker_route(bot)
        if len(route) < 2:
            return False
        if any(
            route[0].distance_to(Point2(site["position"])) < 8 and 0 <= bot.time - site["last_checked"] < 45
            for site in report.get("expansion_sites", [])
        ):
            return False
        workers = bot.workers.filter(
            lambda unit: (
                bot.available(unit)
                and (unit.is_idle or unit.is_gathering)
                and unit.health + unit.shield >= 0.85 * (unit.health_max + unit.shield_max)
            )
        )
        if not workers:
            return False
        worker = workers.closest_to(route[0])
        self.worker_tag = bot.scout_tag = worker.tag
        self.last_assignment = bot.time
        self.worker_route_index = 0
        self.returning = False
        self.revisit_started = self.revisit_active = True
        self.revisit_until = bot.time + 60
        self.revisit_health = worker.health + worker.shield
        self.costs.register(bot, worker, "worker")
        return True
