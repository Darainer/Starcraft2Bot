"""Exclusive, explicitly permitted Oracle worker raids with bounded exposure.

Enemy orders are unavailable. Visible anti-air envelopes are risk evidence;
missing anti-air is not evidence of safety. Beam state comes from our own buff,
never Oracle.can_attack (which the SDK special-cases even with the beam off).
"""

from collections import deque

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.buff_id import BuffId as B
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.combat_assessment import WORKERS, visible_threats
from source.composition import oracle_permitted
from source.harass_targets import oracle_inspection
from source.missions import retreat_geometry, retreat_waypoint


class OracleHarass:
    def __init__(self):
        self.raids = {}
        self.blocked = {}
        self.history = deque(maxlen=128)
        self.worker_lines = {}

    async def tick(self, bot):
        if not oracle_permitted(bot):
            self.raids.clear()
            self.worker_lines.clear()
            return {"enabled": False, "orders": [], "raids": {}, "history": list(self.history)}
        contacts = visible_threats(bot)
        # A visible townhall with zero currently visible workers does not erase
        # the earlier worker-line sighting. Its own timestamp still expires.
        for base in bot.scout_report.get("known_enemy_bases", []):
            if base.get("workers_nearby", 0) >= 3 and 0 <= bot.time - base.get("seen_seconds", -999) <= 120:
                key = str(base.get("tag", tuple(base["position"])))
                if base["seen_seconds"] >= self.worker_lines.get(key, {}).get("seen_seconds", -999):
                    self.worker_lines[key] = dict(base)
        self.worker_lines = {
            key: line
            for key, line in self.worker_lines.items()
            if 0 <= bot.time - line["seen_seconds"] <= 120
        }
        anti_air = contacts.filter(lambda unit: unit.can_attack_air or unit.type_id == U.BUNKER)
        workers = bot.enemy_units.filter(
            lambda unit: unit.is_visible and not unit.is_hallucination and unit.type_id in WORKERS
        )
        geometry = tuple(
            (*shape[:4], max(6, shape[4]), shape[5], max(24, shape[6]), shape[7], True)
            if enemy.type_id == U.BUNKER
            else shape
            for enemy, shape in zip(contacts, retreat_geometry(contacts), strict=True)
        )
        oracles = bot.units(U.ORACLE).ready
        self.raids = {tag: record for tag, record in self.raids.items() if tag in oracles.tags}
        orders = []
        for oracle in oracles:
            if not bot.available(oracle):
                self.raids.pop(oracle.tag, None)
                continue
            record = self.raids.setdefault(oracle.tag, {"phase": "recover", "until": 0, "toggle": -999})
            home = (
                bot.townhalls.ready.closest_to(oracle).position if bot.townhalls.ready else bot.start_location
            )
            active = oracle.has_buff(B.ORACLEWEAPON)
            shield = oracle.shield / max(1, oracle.shield_max)
            health = oracle.health / max(1, oracle.health_max)
            threatened = any(
                enemy.distance_to(oracle)
                <= max(6 if enemy.type_id == U.BUNKER else 0, enemy.air_range)
                + enemy.radius
                + oracle.radius
                + 3
                for enemy in anti_air
            )
            safe_workers = workers.filter(
                lambda worker: (
                    not any(
                        enemy.distance_to(worker)
                        < max(6 if enemy.type_id == U.BUNKER else 0, enemy.air_range) + enemy.radius + 6
                        for enemy in anti_air
                    )
                )
            )
            clustered = safe_workers.filter(
                lambda unit, oracle=oracle: (
                    workers.closer_than(6, unit).amount >= 3 or unit.distance_to(oracle) <= 10
                )
            )
            target = clustered.closest_to(oracle) if clustered else None
            if (
                record["phase"] == "recover"
                and target is None
                and bot.time >= record["until"]
                and shield >= 0.75
                and health >= 0.8
                and oracle.energy >= 50
                and not threatened
                and not bot.economic_emergency
            ):
                mission = oracle_inspection(bot, oracle, anti_air, self.blocked, self.worker_lines.values())
                if mission is not None:
                    record.update(
                        phase="transit",
                        mission=mission,
                        transit_until=bot.time + 45,
                        reason="Inspect a positively scouted economic target",
                    )
                    self.history.append(
                        {
                            "time": bot.time,
                            "unit_tag": oracle.tag,
                            "action": "inspection_admitted",
                            "mission": mission,
                        }
                    )
            mission = record.get("mission")
            if target is not None and record["phase"] in {"transit", "inspect"}:
                record.update(phase="raid", started=bot.time, reason="Workers reacquired in current vision")
            if (
                mission
                and record["phase"] == "transit"
                and oracle.distance_to(Point2(mission["position"])) <= 9
            ):
                record.update(phase="inspect", inspect_until=bot.time + 6)
            reason = ""
            if oracle.has_buff(B.LOCKON) or threatened:
                reason = "visible_anti_air_or_lock_on"
            elif mission and any(
                enemy.distance_to(Point2(mission["position"])) <= max(6, enemy.air_range) + enemy.radius + 6
                for enemy in anti_air
            ):
                reason = "inspection_destination_defended"
            elif shield < 0.35 or health < 0.65 or oracle.energy < 18:
                reason = "shield_health_or_energy_limit"
            elif bot.economic_emergency:
                reason = "home_emergency"
            elif record["phase"] == "transit" and bot.time >= record["transit_until"]:
                reason = "inspection_transit_expired"
            elif record["phase"] == "inspect" and bot.time >= record["inspect_until"]:
                reason = "inspection_expired"
            elif (
                target is None
                and mission
                and record["phase"] in {"transit", "inspect"}
                and bot.is_visible(Point2(mission["position"]))
                and not workers.closer_than(10, Point2(mission["position"]))
            ):
                reason = "inspected_point_has_no_visible_workers"
            elif target is None and record["phase"] not in {"transit", "inspect"}:
                reason = "no_visible_worker_opportunity"
            elif not active and oracle.energy < 50 and record["phase"] == "raid":
                reason = "beam_activation_reserve"
            elif record["phase"] == "raid" and bot.time - record["started"] >= 30:
                reason = "exposure_time_limit"
            if reason:
                if record["phase"] != "recover":
                    record["until"] = bot.time + 12
                    self.history.append(
                        {
                            "time": bot.time,
                            "unit_tag": oracle.tag,
                            "action": "mission_ended",
                            "reason": reason,
                        }
                    )
                    if mission:
                        self.blocked[mission["id"]] = bot.time + 30
                record.pop("mission", None)
                record.update(phase="recover", reason=reason)
            elif (
                record["phase"] == "recover"
                and bot.time >= record["until"]
                and shield >= 0.75
                and health >= 0.8
                and oracle.energy >= 50
                and target is not None
            ):
                record.update(phase="raid", started=bot.time, reason="visible_workers; anti_air_uncertain")
            abilities = await bot.get_available_abilities(oracle)
            command, action = None, ""
            raiding = record["phase"] == "raid" and target is not None
            close = raiding and oracle.distance_to(target) <= 6
            if (
                active
                and not close
                and A.BEHAVIOR_PULSARBEAMOFF in abilities
                and bot.time - record["toggle"] >= 1
            ):
                command, action = oracle(A.BEHAVIOR_PULSARBEAMOFF), "beam_off"
            elif raiding:
                if (
                    close
                    and not active
                    and oracle.energy >= 50
                    and A.BEHAVIOR_PULSARBEAMON in abilities
                    and bot.time - record["toggle"] >= 1
                ):
                    command, action = oracle(A.BEHAVIOR_PULSARBEAMON), "beam_on"
                elif active and oracle.distance_to(target) <= 4:
                    command, action = oracle.attack(target), "attack_worker"
                else:
                    goal = oracle.position.towards(target.position, min(6, oracle.distance_to(target)))
                    command = oracle.move(retreat_waypoint(bot, oracle, goal, contacts, geometry))
                    action = "approach_visible_workers"
            elif record["phase"] in {"transit", "inspect"}:
                point = Point2(record["mission"]["position"])
                destination = point.towards(
                    home, min(4 if record["phase"] == "inspect" else 8, point.distance_to(home))
                )
                goal = oracle.position.towards(destination, min(6, oracle.distance_to(destination)))
                command = oracle.move(retreat_waypoint(bot, oracle, goal, contacts, geometry))
                action = "inspect_scouted_worker_line"
            elif oracle.distance_to(home) > 5 or threatened:
                goal = oracle.position.towards(home, min(8, oracle.distance_to(home)))
                command = oracle.move(retreat_waypoint(bot, oracle, goal, contacts, geometry))
                action = "return_and_recharge"
            if command is not None and bot.issue(command):
                if action in {"beam_on", "beam_off"}:
                    record["toggle"] = bot.time
                orders.append({"unit_tag": oracle.tag, "action": action})
                self.history.append(
                    {"time": bot.time, "unit_tag": oracle.tag, "action": action, "phase": record["phase"]}
                )
        return {
            "enabled": True,
            "orders": orders,
            "raids": {str(tag): dict(record) for tag, record in self.raids.items()},
            "history": list(self.history),
        }
