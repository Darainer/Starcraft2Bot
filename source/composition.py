"""Bounded production overlays from recent scouting; preserve user settings."""

NAMES = ("zealots", "stalkers", "sentries", "immortals", "colossi", "voidrays", "high_templar")


def composition_targets(bot):
    targets = {name: getattr(bot.settings, name) for name in NAMES}
    if not (bot.settings.enabled and bot.settings.attack and bot.settings.adaptive_composition):
        return targets
    intel = bot.scout_report.get("composition_intel", {})
    if bot.time - intel.get("seen_seconds", -999) > 90:
        return targets
    air = intel.get("air_supply", 0)
    ground = intel.get("armored_ground_supply", 0)
    light = intel.get("light_ground_count", 0)
    if air >= 8:
        share = air / max(1, intel.get("supply", 0))
        targets["stalkers"] = max(targets["stalkers"], 36 if share < 0.5 else 44)
        # Don't add slow ground tech to counter an exclusively flying army.
        if share >= 0.65:
            targets["zealots"] = min(targets["zealots"], 4)
            targets["immortals"] = min(targets["immortals"], 2)
            targets["colossi"] = 0
        if intel.get("armored_air_supply", 0) >= 8:
            targets["voidrays"] = max(targets["voidrays"], 6)
    if ground >= 8:
        targets["immortals"] = max(targets["immortals"], min(10, 2 + int(ground / 4)))
    if light >= 8:
        targets["colossi"] = max(targets["colossi"], 3)
        targets["zealots"] = max(targets["zealots"], 12)
    return targets


def production_target(bot, name):
    plan = getattr(bot, "strategic_plan", None)
    if (
        plan is not None
        and plan.expires_at > bot.time
        and bot.settings.enabled
        and bot.settings.attack
        and bot.settings.adaptive_composition
    ):
        targets = dict(plan.production)
        if name in targets:
            return targets[name]
    return composition_targets(bot).get(name, getattr(bot.settings, name))
