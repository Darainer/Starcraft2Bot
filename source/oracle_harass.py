"""Exclusive, explicitly permitted Oracle worker raids with bounded exposure.

Enemy orders are unavailable. Visible anti-air envelopes are risk evidence;
missing anti-air is not evidence of safety. Beam state comes from our own buff,
never Oracle.can_attack (which the SDK special-cases even with the beam off).
"""

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.buff_id import BuffId as B
from sc2.ids.unit_typeid import UnitTypeId as U

from source.combat_assessment import WORKERS, visible_threats
from source.composition import oracle_permitted
from source.missions import retreat_geometry, retreat_waypoint


class OracleHarass:
    def __init__(self):
        self.raids = {}

    async def tick(self, bot):
        if not oracle_permitted(bot):
            self.raids.clear()
            return {"enabled": False, "orders": [], "raids": {}}
        contacts = visible_threats(bot)
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
            target = safe_workers.closest_to(oracle) if safe_workers else None
            reason = ""
            if oracle.has_buff(B.LOCKON) or threatened:
                reason = "visible_anti_air_or_lock_on"
            elif shield < 0.35 or health < 0.65 or oracle.energy < 18:
                reason = "shield_health_or_energy_limit"
            elif bot.economic_emergency:
                reason = "home_emergency"
            elif target is None:
                reason = "no_visible_worker_opportunity"
            elif not active and oracle.energy < 50 and record["phase"] == "raid":
                reason = "beam_activation_reserve"
            elif record["phase"] == "raid" and bot.time - record["started"] >= 30:
                reason = "exposure_time_limit"
            if reason:
                if record["phase"] != "recover":
                    record["until"] = bot.time + 12
                record.update(phase="recover", reason=reason)
            elif (
                record["phase"] == "recover"
                and bot.time >= record["until"]
                and shield >= 0.75
                and health >= 0.8
                and oracle.energy >= 50
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
            elif oracle.distance_to(home) > 5 or threatened:
                goal = oracle.position.towards(home, min(8, oracle.distance_to(home)))
                command = oracle.move(retreat_waypoint(bot, oracle, goal, contacts, geometry))
                action = "return_and_recharge"
            if command is not None and bot.issue(command):
                if action in {"beam_on", "beam_off"}:
                    record["toggle"] = bot.time
                orders.append({"unit_tag": oracle.tag, "action": action})
        return {
            "enabled": True,
            "orders": orders,
            "raids": {str(tag): dict(record) for tag, record in self.raids.items()},
        }
