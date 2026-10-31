"""Observed scout costs; missing units are not assumed dead."""


class ScoutCosts:
    def __init__(self):
        self.units = {}
        self.last_time = None
        self.worker_seconds = 0.0

    def register(self, bot, unit, method):
        if unit.tag not in self.units:
            cost = bot.calculate_cost(unit.type_id)
            self.units[unit.tag] = {
                "method": method,
                "minerals": cost.minerals,
                "gas": cost.vespene,
                "status": "present",
                "active": True,
            }
        elif self.units[unit.tag]["status"] != "confirmed_dead":
            self.units[unit.tag].update(active=True, status="present")

    def release(self, tag):
        if tag in self.units:
            self.units[tag].update(active=False, status="returned")

    def observe(self, bot, worker_tag):
        elapsed = max(0, bot.time - self.last_time) if self.last_time is not None else 0
        self.last_time = bot.time
        live = {unit.tag: unit for unit in bot.all_own_units}
        dead = getattr(bot.state, "dead_units", set())
        for tag, entry in self.units.items():
            if not entry["active"]:
                continue
            if not (bot.settings.enabled and bot.settings.attack and bot.settings.scouting):
                entry.update(active=False, status="automation_disabled")
                continue
            unit = live.get(tag)
            if unit is not None and not bot.control.eligible(unit):
                entry.update(active=False, status="human_owned")
            elif tag in dead:
                entry.update(active=False, status="confirmed_dead", lost_seconds=bot.time)
            elif unit is None:
                entry["status"] = "missing"
            else:
                entry.update(status="present", last_seen_seconds=bot.time)
                if tag == worker_tag and unit.distance_to(bot.start_location) > 6:
                    self.worker_seconds += elapsed
        return {
            "units": [{"tag": str(tag), **entry} for tag, entry in self.units.items()],
            "worker_opportunity_seconds": self.worker_seconds,
            "confirmed_lost_minerals": sum(
                e["minerals"] for e in self.units.values() if e["status"] == "confirmed_dead"
            ),
            "confirmed_lost_gas": sum(
                e["gas"] for e in self.units.values() if e["status"] == "confirmed_dead"
            ),
            "scope": "Assigned scouts only; away-from-home worker time is an opportunity proxy, not measured lost income",
        }
