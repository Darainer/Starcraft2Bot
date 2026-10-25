"""One explicitly assigned economy scout, then observable composition intelligence."""

from sc2.ids.unit_typeid import UnitTypeId as U


class ScoutController:
    def __init__(self):
        self.worker_tag = None
        self.last_assignment = -120

    def tick(self, bot):
        enemies = bot.enemy_units.filter(lambda unit: unit.is_visible)
        buildings = bot.enemy_structures.filter(lambda unit: unit.is_visible)
        report = getattr(bot, "scout_report", {})
        combat = enemies.filter(lambda u: u.type_id not in {U.PROBE, U.SCV, U.DRONE} and u.can_attack)
        if enemies or buildings:
            report.update(
                enemy_seen=True,
                last_seen_seconds=bot.time,
                flying=sum(u.is_flying for u in enemies),
                armored=sum(u.is_armored for u in enemies),
                enemy_units=len(enemies),
                enemy_buildings=len(buildings),
            )
            if bot.settings.enabled and bot.settings.attack and bot.settings.adaptive_composition:
                changes = {}
                if sum(u.is_flying for u in combat) >= 2 and bot.settings.stalkers < 24:
                    bot.settings.stalkers = changes["stalkers"] = 24
                if bot.settings.profile != "air":
                    if sum(u.is_armored for u in combat) >= 4 and bot.settings.immortals < 8:
                        bot.settings.immortals = changes["immortals"] = 8
                    if sum(u.is_light and not u.is_flying for u in combat) >= 8 and bot.settings.colossi < 2:
                        bot.settings.colossi = changes["colossi"] = 2
                if changes:
                    report["composition_adjustment"] = changes
        bot.scout_report = report
        if not bot.settings.enabled or not bot.settings.attack or not bot.settings.scouting:
            return {"phase": "disabled"}
        scout = bot.workers.find_by_tag(self.worker_tag) if self.worker_tag else None
        if scout is None:
            bot.scout_tag = None
            if (
                not report.get("enemy_seen")
                and bot.supply_workers >= 16
                and bot.time - self.last_assignment >= 120
            ):
                candidates = bot.workers.filter(lambda u: bot.available(u) and (u.is_idle or u.is_gathering))
                if candidates:
                    scout = candidates.closest_to(bot.game_info.map_center)
                    self.worker_tag = bot.scout_tag = scout.tag
                    self.last_assignment = bot.time
        if scout is None:
            return {
                "phase": "observing" if report.get("enemy_seen") else "waiting_for_scout",
                "intel": report,
            }
        if not bot.control.eligible(scout):
            return {"phase": "human_owned", "worker_tag": scout.tag, "intel": report}
        threatened = enemies.filter(lambda u: u.can_attack_ground and u.distance_to(scout) < 8)
        if report.get("enemy_seen") or threatened or scout.health + scout.shield < 30:
            target = bot.start_location
            if scout.distance_to(target) <= 6:
                self.worker_tag = bot.scout_tag = None
                return {"phase": "returned", "intel": report}
            phase = "returning"
        elif bot.enemy_start_locations:
            target = bot.enemy_start_locations[0]
            phase = "scouting_enemy_start"
        else:
            return {"phase": "no_known_start"}
        if scout.is_idle or not scout.orders or scout.distance_to(target) > 5:
            bot.issue(scout.move(target), scout_order=True)
        return {"phase": phase, "worker_tag": scout.tag, "target": list(target), "intel": report}
