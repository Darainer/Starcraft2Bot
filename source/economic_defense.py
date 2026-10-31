"""Observed asset damage and bounded re-engagement opportunities.

No enemy orders, cooldowns or engaged-target fields are read. The SC2 protocol
does not expose them. Every enemy retains its full potential DPS in the bound.
"""

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.combat_assessment import power
from source.strategic_plan import CombatWindow

PRODUCTION = {U.GATEWAY, U.WARPGATE, U.ROBOTICSFACILITY, U.STARGATE}


def force_metrics(bot, squad, enemies, anchor):
    maximum = sum(unit.health_max + unit.shield_max for unit in squad)
    return {
        "health": sum(unit.health + unit.shield for unit in squad) / max(1, maximum),
        "supply": sum(bot.calculate_supply_cost(unit.type_id) for unit in squad if unit.can_attack),
        "enemy_power": power(enemies, squad),
        "advantage": min(10, power(squad, enemies) / max(1, power(enemies, squad))) if enemies else 10,
        "cohesion": sum(unit.distance_to(anchor) < 8 for unit in squad) / max(1, len(squad)),
        "weapon_ready": sum(unit.weapon_cooldown <= 0 for unit in squad if unit.can_attack)
        / max(1, sum(unit.can_attack for unit in squad)),
    }


class EconomicDefense:
    def __init__(self):
        self.assets = {}
        self.last_probe = -999
        self.probe_times = []
        self.window_health = {}

    def observe(self, bot, army, contacts, recovery):
        automatic = (
            bot.settings.enabled
            and bot.settings.attack
            and bot.settings.strategy == "auto"
            and not bot.settings.strategy_script
        )
        if not automatic:
            self.assets.clear()
            self.window_health.clear()
            return None
        candidates = []
        if bot.settings.defend_assets:
            for asset in bot.structures.ready:
                productive = (
                    asset.type_id == U.NEXUS
                    and (asset.assigned_harvesters >= 4 or bot.workers.closer_than(10, asset).amount >= 4)
                ) or (
                    asset.type_id in PRODUCTION
                    and asset.is_powered
                    and bot.settings.production
                    and bot.supply_workers >= 12
                )
                hp = asset.health + asset.shield
                previous = self.assets.get(asset.tag)
                self.assets[asset.tag] = (bot.time, hp)
                if (
                    not productive
                    or previous is None
                    or not 0 < bot.time - previous[0] <= 3
                    or hp >= previous[1]
                ):
                    continue
                attackers = contacts.filter(
                    lambda enemy, asset=asset: (
                        (enemy.can_attack_ground or enemy.type_id == U.BUNKER)
                        and enemy.distance_to(asset)
                        <= max(6 if enemy.type_id == U.BUNKER else 0, enemy.ground_range)
                        + enemy.radius
                        + asset.radius
                        + 1
                    )
                )
                enemies = contacts.closer_than(20, asset)
                defenders = army.closer_than(26, asset)
                if not attackers or not defenders:
                    continue
                anchor = defenders.center
                metrics = force_metrics(bot, defenders, enemies, anchor)
                if metrics["supply"] < 8 or metrics["health"] < 0.6 or not 0.6 <= metrics["advantage"] < 10:
                    continue
                # Rapid own-force deterioration closes the opportunity even if
                # trailing economic value still makes the base look attractive.
                old_health = self.window_health.get(asset.tag)
                self.window_health[asset.tag] = (bot.time, metrics["health"])
                if old_health and bot.time - old_health[0] <= 3 and old_health[1] - metrics["health"] >= 0.08:
                    continue
                observed_dps = (previous[1] - hp) / (bot.time - previous[0])
                potential_dps = sum(
                    max(24 if enemy.type_id == U.BUNKER else 0, enemy.ground_dps) for enemy in attackers
                )
                survival = hp / max(1, observed_dps, potential_dps)
                arrivals = sorted(
                    max(0, unit.distance_to(asset) - unit.ground_range - asset.radius)
                    / max(1, unit.movement_speed)
                    for unit in defenders
                )
                eta = arrivals[min(len(arrivals) - 1, int(len(arrivals) * 0.75))]
                if eta + 2 >= survival:
                    continue
                point = attackers.center
                if point.distance_to(asset) > 12:
                    point = asset.position.towards(point, 12)
                candidates.append(
                    (
                        100 if asset.type_id == U.NEXUS else 60,
                        CombatWindow(
                            "asset_defense",
                            tuple(point),
                            tuple(asset.position),
                            bot.time,
                            bot.time + 2,
                            metrics["advantage"],
                            metrics["health"],
                            "Protect productive assets during observed damage",
                            (
                                f"Own asset {asset.tag} lost {previous[1] - hp:g} HP/shields in {bot.time - previous[0]:g}s",
                                f"Full enemy potential DPS {potential_dps:g}; observed loss rate {observed_dps:g}; conservative survival {survival:.1f}s; defender ETA {eta:.1f}s",
                                "Enemy fire targets unknown; no DPS discount; reevaluate local losses and stay near asset",
                            ),
                        ),
                    )
                )
            self.assets = {tag: record for tag, record in self.assets.items() if bot.time - record[0] <= 3}
        if candidates:
            return max(candidates, key=lambda item: item[0])[1]
        if not bot.settings.local_regroup or recovery.get("phase") != "recover":
            return None
        regroup = recovery.get("local_regroup")
        if not regroup or not 3 <= bot.time - regroup["since"] <= 12 or bot.time - self.last_probe < 20:
            return None
        army = army.closer_than(20, Point2(regroup["goal"]))
        anchor = army.center if army else Point2(regroup["anchor"])
        enemies = contacts.closer_than(20, anchor)
        if not enemies:
            return None
        metrics = force_metrics(bot, army, enemies, anchor)
        if metrics["health"] < 0.6 or metrics["supply"] < 8 or not 0.6 <= metrics["advantage"] < 10:
            return None
        baseline = regroup["metrics"]
        changes = []
        if metrics["supply"] >= baseline["supply"] + 4:
            changes.append("reinforcements arrived")
        if metrics["health"] >= baseline["health"] + 0.08:
            changes.append("health/shields recovered")
        if metrics["cohesion"] >= baseline["cohesion"] + 0.15:
            changes.append("cohesion improved")
        if metrics["enemy_power"] <= baseline["enemy_power"] * 0.8:
            changes.append("observed enemy power reduced")
        if (
            anchor.distance_to(Point2(regroup["goal"])) < 4
            and anchor.distance_to(Point2(regroup["anchor"])) >= 5
            and metrics["weapon_ready"] >= 0.6
        ):
            changes.append("short regroup reached; weapons ready")
        self.probe_times = [time for time in self.probe_times if bot.time - time < 60]
        if not changes or len(self.probe_times) >= 2:
            return None
        self.last_probe = bot.time
        self.probe_times.append(bot.time)
        return CombatWindow(
            "regroup_probe",
            tuple(enemies.closest_to(anchor).position),
            tuple(anchor),
            bot.time,
            bot.time + 2,
            metrics["advantage"],
            metrics["health"],
            "Re-engage after a short local regroup with changed conditions",
            tuple(changes),
        )
