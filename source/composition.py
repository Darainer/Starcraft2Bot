"""Bounded production overlays from recent scouting; preserve user settings."""

from dataclasses import replace

from sc2.ids.unit_typeid import UnitTypeId as U

from source.counter_composition import SUPPLY, propose_counter_plan

NAMES = ("zealots", "stalkers", "sentries", "immortals", "colossi", "voidrays", "high_templar")
UNIT_NAMES = dict(
    zip(
        (*NAMES, "oracles", "observers", "warp_prisms"),
        (
            U.ZEALOT,
            U.STALKER,
            U.SENTRY,
            U.IMMORTAL,
            U.COLOSSUS,
            U.VOIDRAY,
            U.HIGHTEMPLAR,
            U.ORACLE,
            U.OBSERVER,
            U.WARPPRISM,
        ),
        strict=True,
    )
)
WORKERS = {U.PROBE, U.SCV, U.DRONE, U.MULE}


def oracle_permitted(bot):
    s = bot.settings
    return (
        s.enabled
        and s.attack
        and s.oracle_harass
        and s.oracle_beam
        and s.strategy == "auto"
        and not s.strategy_script
    )


def scouted_counter_plan(bot):
    s = bot.settings
    if not (
        s.enabled
        and s.attack
        and s.adaptive_composition
        and s.composition_policy == "scouted"
        and s.strategy == "auto"
        and not s.strategy_script
    ):
        return None
    evidence = list(bot.scout_report.get("enemy_unit_evidence", []))
    for unit in bot.enemy_units:
        if unit.is_visible and not unit.is_hallucination and unit.type_id not in WORKERS:
            evidence.append(
                {
                    "tag": str(unit.tag),
                    "kind": unit.type_id.name,
                    "supply": bot.game_data.units[unit.type_id.value]._proto.food_required,
                    "seen_seconds": bot.time,
                    "air": unit.is_flying,
                    "armored": unit.is_armored,
                    "light": unit.is_light,
                }
            )
    opportunity = any(
        0 <= bot.time - base.get("seen_seconds", -999) < 30
        and base.get("workers_nearby", 0) >= 3
        and base.get("visible_defense_buildings", 0) == 0
        for base in bot.scout_report.get("known_enemy_bases", [])
    )
    costs = {name: bot.calculate_supply_cost(kind) for name, kind in UNIT_NAMES.items()}
    costs = {name: value if value > 0 else SUPPLY[name] for name, value in costs.items()}
    support = {
        "observers": s.observers if s.scouting else 0,
        "warp_prisms": s.warp_prisms if s.warp_reinforcement else 0,
        "oracles": s.oracles,
    }
    context = (
        getattr(bot.enemy_race, "name", "Unknown"),
        bot.economic_emergency,
        s.profile,
        s.max_workers,
        s.storm,
        s.oracle_harass,
        s.oracle_beam,
        s.scouting,
        s.warp_reinforcement,
        s.observers,
        s.warp_prisms,
        s.oracles,
    )
    old = getattr(bot, "counter_plan", None) if getattr(bot, "_counter_context", None) == context else None
    proposed = propose_counter_plan(
        bot.time,
        getattr(bot.enemy_race, "name", "Unknown"),
        evidence,
        max_workers=s.max_workers,
        workers=bot.supply_workers,
        bases=bot.townhalls.ready.amount,
        own_army=bot.supply_army,
        support_targets=support,
        storm=s.storm,
        oracle_allowed=oracle_permitted(bot) and not bot.economic_emergency,
        worker_opportunity=opportunity,
        supply_costs=costs,
    )
    if proposed is None and old is not None and 0 <= bot.time - old.evidence_time < 75:
        return replace(
            old,
            uncertainty=max(0.7, old.uncertainty),
            evidence=old.evidence + ("Stale vision: bounded plan hold; request new scouting",),
        )
    if (
        proposed is not None
        and old is not None
        and proposed.family != old.family
        and 0 <= bot.time - old.time < 12
        and not (proposed.family.endswith("_air") or proposed.family == "zerg_lurker")
    ):
        return old
    bot.counter_plan, bot._counter_context = proposed, context
    return proposed


def composition_targets(bot):
    targets = {name: getattr(bot.settings, name) for name in NAMES}
    if not (bot.settings.enabled and bot.settings.attack and bot.settings.adaptive_composition):
        return targets
    counter = scouted_counter_plan(bot)
    if counter is not None:
        return dict(counter.targets)
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
