"""Local, target-domain-aware heuristics; deliberately not a combat simulator."""

from sc2.ids.unit_typeid import UnitTypeId as U

WORKERS = {U.PROBE, U.SCV, U.DRONE, U.MULE}


def observed_supply(bot, unit):
    """Existing-unit supply from the adapter, not incremental morph cost."""
    supplies = getattr(bot, "unit_supplies", {})
    if unit.type_id in supplies:
        return supplies[unit.type_id]
    return bot.calculate_supply_cost(unit.type_id)


def fighting(unit):
    # A loaded bunker has no weapon in the raw unit data. Treat its unknown
    # cargo conservatively rather than interpreting it as a harmless building.
    return unit.type_id not in WORKERS and (unit.can_attack or unit.type_id == U.BUNKER)


def power(units, opponents):
    """Weight current HP by DPS that can actually hit the opposing force."""
    opponents = list(opponents)
    if not opponents:
        return 0.0
    result = 0.0
    for unit in units:
        if not fighting(unit):
            continue
        # A Colossus can be hit by either weapon, but not both simultaneously.
        dps = sum(
            max(
                unit.ground_dps if not target.is_flying else 0,
                unit.air_dps if target.is_flying or target.type_id == U.COLOSSUS else 0,
            )
            for target in opponents
        ) / len(opponents)
        if unit.type_id == U.BUNKER:
            dps = max(dps, 24.0)  # Conservative occupancy assumption, not observed cargo.
        result += (unit.health + unit.shield) * dps
    return result


def visible_threats(bot):
    return (bot.enemy_units | bot.enemy_structures).filter(lambda unit: unit.is_visible and fighting(unit))


def home_threats(bot, units):
    """Screen our approaches, not the opposing army anywhere on the map."""
    bases = bot.townhalls.ready
    return units.filter(lambda unit: any(unit.distance_to(base) < 32 for base in bases))


def favorable(friends, enemies, margin=1.2):
    enemies = list(enemies)
    return not enemies or power(friends, enemies) >= max(1, power(enemies, friends)) * margin
