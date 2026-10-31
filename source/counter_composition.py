"""SC2 counter recipes from timestamped fielded forces, not configured AI builds.

Supply shares and thresholds are experimental priors, not combat predictions.
The adapter supplies legal observations and native supply costs.
"""

from dataclasses import dataclass
from math import ceil, floor, isfinite

COMPOSITION_POLICIES = ("legacy", "scouted")
SUPPLY = {
    "zealots": 2,
    "stalkers": 2,
    "sentries": 2,
    "immortals": 4,
    "colossi": 6,
    "voidrays": 4,
    "high_templar": 2,
    "oracles": 3,
    "archons": 4,
    "observers": 1,
    "warp_prisms": 2,
}
CAPS = {
    "zealots": 20,
    "stalkers": 44,
    "immortals": 12,
    "colossi": 4,
    "voidrays": 8,
    "high_templar": 4,
    "archons": 8,
}
SUPPORT = {"MEDIVAC", "RAVEN", "OVERSEER", "OBSERVER", "WARPPRISM", "OVERLORD"}
SIEGE = {"SIEGETANK", "SIEGETANKSIEGED", "LURKERMP", "LURKERMPBURROWED"}
VIKINGS = {"VIKINGFIGHTER"}
AIR_ARMOR = {"CORRUPTOR", "BROODLORD", "BATTLECRUISER", "CARRIER", "TEMPEST", "VOIDRAY"}


@dataclass(frozen=True)
class CounterPlan:
    family: str
    time: float
    evidence_time: float
    targets: tuple[tuple[str, int], ...]
    priority: tuple[str, ...]
    minimums: tuple[tuple[str, int], ...]
    tech_goals: tuple[str, ...]
    upgrade_focus: str
    supply_budget: float
    allocated_supply: float
    splash_required: bool
    splash_constraint: str
    late_game: bool
    uncertainty: float
    evidence: tuple[str, ...]
    morph_inputs: tuple[tuple[str, int], ...] = ()


def propose_counter_plan(
    now,
    race,
    evidence,
    *,
    max_workers,
    workers,
    bases,
    own_army,
    support_targets,
    storm=False,
    archon_merge=False,
    oracle_allowed=False,
    worker_opportunity=False,
    supply_costs=None,
):
    """Reframe replacement targets inside the worker-adjusted supply envelope."""
    if race not in {"Terran", "Zerg"} or not isfinite(now) or now < 150 or workers < 16:
        return None
    contacts = {}
    for item in evidence:
        seen = item.get("seen_seconds")
        if (
            "tag" in item
            and isinstance(seen, (int, float))
            and not isinstance(seen, bool)
            and isfinite(seen)
            and 0 <= now - seen < 45
            and item.get("supply", 0) > 0
        ):
            contacts[str(item["tag"])] = item
    force = [u for u in contacts.values() if u.get("kind") not in SUPPORT]
    total = sum(u["supply"] for u in force)
    if total < 4:
        return None
    air = sum(u["supply"] for u in force if u.get("air"))
    ground = total - air
    armored = sum(u["supply"] for u in force if u.get("armored") and not u.get("air"))
    ground_count = sum(not u.get("air") for u in force)
    siege = any(u.get("kind") in SIEGE for u in force)
    lurker = any(u.get("kind") in {"LURKERMP", "LURKERMPBURROWED"} for u in force)
    vikings = sum(u["supply"] for u in force if u.get("kind") in VIKINGS)
    late = now >= 600 and workers >= 32 and bases >= 2
    splash = ground >= 24 or ground_count >= 12
    air_mass = air >= 16
    if air / total >= 0.5:
        family = f"{race.lower()}_air"
        weights = {"stalkers": 0.80, "voidrays": 0.15, "zealots": 0.05}
        if not any(u.get("kind") in AIR_ARMOR for u in force):
            weights = {"stalkers": 0.90, "zealots": 0.10}
        priority = ("stalkers", "voidrays")
    elif race == "Zerg" and lurker:
        family, weights = (
            "zerg_lurker",
            {"zealots": 0.08, "stalkers": 0.22, "immortals": 0.45, "colossi": 0.25},
        )
        priority = ("immortals", "colossi", "stalkers")
    elif race == "Zerg" and armored >= max(4, ground * 0.4):
        family, weights = (
            "zerg_armored",
            {"zealots": 0.10, "stalkers": 0.25, "immortals": 0.55, "colossi": 0.10},
        )
        priority = ("immortals", "colossi", "stalkers")
    elif race == "Zerg":
        family, weights = (
            "zerg_swarm",
            {"zealots": 0.18, "stalkers": 0.24, "immortals": 0.15, "colossi": 0.43},
        )
        priority = ("colossi", "stalkers", "immortals")
    elif siege:
        family, weights = (
            "terran_siege",
            {"zealots": 0.08, "stalkers": 0.20, "immortals": 0.52, "colossi": 0.20},
        )
        priority = ("immortals", "colossi", "stalkers")
    elif armored >= max(4, ground * 0.4):
        family, weights = (
            "terran_armored_bio",
            {"zealots": 0.12, "stalkers": 0.23, "immortals": 0.40, "colossi": 0.25},
        )
        priority = ("immortals", "colossi", "stalkers")
    else:
        family, weights = (
            "terran_bio",
            {"zealots": 0.18, "stalkers": 0.20, "immortals": 0.16, "colossi": 0.46},
        )
        priority = ("colossi", "immortals", "stalkers")
    if vikings >= 4 and ground:
        # Protect the splash investment with anti-air instead of requesting only more Colossi.
        weights["colossi"] = min(weights.get("colossi", 0), 0.15)
        weights["stalkers"] = weights.get("stalkers", 0) + 0.25
    if late:
        weights["zealots"] = weights.get("zealots", 0) * 0.5
        preferred = "stalkers" if air > ground else "immortals" if armored > ground * 0.4 else "colossi"
        weights[preferred] = weights.get(preferred, 0) + 0.15
    if storm and (splash or air_mass):
        weights["high_templar"] = 0.12
    archon_role = archon_merge and (
        family in {"zerg_swarm", "terran_bio", "terran_armored_bio", "zerg_armored"}
        or family == "zerg_air"
        and not any(unit.get("kind") == "BROODLORD" for unit in force)
    )
    if archon_role:
        weights["archons"] = 0.28 if family in {"zerg_swarm", "zerg_air"} else 0.15
        weights["zealots"] = weights.get("zealots", 0) * 0.5
        if family == "zerg_air":
            weights["stalkers"] *= 0.8
        else:
            weights["colossi"] *= 0.75
        priority = (
            ("archons", *priority) if family == "zerg_air" else (*priority[:1], "archons", *priority[1:])
        )
    costs = {**SUPPLY, **(supply_costs or {})}
    if any(not isfinite(value) or value <= 0 for value in costs.values()):
        raise ValueError("Native supply costs must be positive and finite")
    targets = dict.fromkeys(costs, 0)
    budget = max(0, 200 - max(max_workers, workers))
    targets["observers"] = max(support_targets.get("observers", 0), 2 if lurker else 0)
    targets["warp_prisms"] = support_targets.get("warp_prisms", 0)
    targets["sentries"] = 2 if ground else 0
    targets["oracles"] = (
        min(
            2,
            max(
                support_targets.get("oracles", 0),
                int(worker_opportunity and workers >= 20 and own_army >= 12),
            ),
        )
        if oracle_allowed
        else 0
    )
    reserved = sum(targets[k] * costs[k] for k in targets)
    if reserved > budget:
        return None
    remaining = budget - reserved
    denominator = sum(weights.values())
    for name, weight in weights.items():
        targets[name] = min(CAPS[name], floor(remaining * weight / denominator / costs[name]))
    # Splash must match the attacking domain. No implicit Storm permission.
    constraint = ""
    if splash:
        desired = 2 if vikings >= 4 else 3 if late else 2
        targets["colossi"] = max(targets["colossi"], desired)
    if archon_role and (splash or air_mass):
        targets["archons"] = max(2, targets["archons"])
    if air_mass:
        if archon_role:
            constraint = (
                "Archon air splash is short range; retain ranged anti-air and measure firing participation"
            )
        elif not storm:
            constraint = "Air mass: neither Archon merging nor Storm covers this plan; ground-only splash cannot cover this demand"

    def allocated():
        return sum(targets[name] * costs[name] for name in targets)

    protected = {
        "colossi": 2 if splash else 0,
        "archons": 2 if archon_role and (splash or air_mass) else 0,
        "observers": 2 if lurker else 0,
    }
    for name in (
        "zealots",
        "stalkers",
        "immortals",
        "voidrays",
        "high_templar",
        "archons",
        "colossi",
        "sentries",
        "warp_prisms",
        "oracles",
        "observers",
    ):
        while allocated() > budget and targets[name] > protected.get(name, 0):
            targets[name] -= 1
    if allocated() > budget:
        return None
    # Redistribute rounding/cap headroom by the recipe's supply shares. Filling
    # one priority to its cap first makes different recipes converge again.
    fill_caps = {
        name: CAPS[name]
        if name in {"stalkers", "zealots"}
        else min(CAPS[name], max(targets[name], ceil(remaining * weight / denominator / costs[name])))
        for name, weight in weights.items()
    }
    while candidates := [
        name
        for name, weight in weights.items()
        if weight > 0 and targets[name] < fill_caps[name] and allocated() + costs[name] <= budget
    ]:
        name = max(
            candidates,
            key=lambda name: (
                (remaining * weights[name] / denominator - targets[name] * costs[name]) / costs[name]
            ),
        )
        targets[name] += 1
    goals = []
    if targets["immortals"] or targets["colossi"] or targets["observers"]:
        goals.append("ROBOTICSFACILITY")
    if targets["colossi"]:
        goals.append("ROBOTICSBAY")
    if targets["voidrays"] or targets["oracles"]:
        goals.insert(0 if air > ground else len(goals), "STARGATE")
    if targets["high_templar"] or targets["archons"]:
        goals.extend(("TWILIGHTCOUNCIL", "TEMPLARARCHIVE"))
    minimums = {
        "colossi": min(2, targets["colossi"]) if splash else 0,
        "immortals": min(2, targets["immortals"]) if armored >= 4 else 0,
        "stalkers": min(8, targets["stalkers"]) if air >= 4 else 0,
        "archons": min(2, targets["archons"]) if splash or air_mass else 0,
    }
    return CounterPlan(
        family,
        now,
        max(u["seen_seconds"] for u in force),
        tuple(targets.items()),
        priority,
        tuple(minimums.items()),
        tuple(goals),
        "air"
        if targets["voidrays"] * costs["voidrays"]
        > sum(targets[name] * costs[name] for name in CAPS if name != "voidrays")
        else "ground",
        budget,
        allocated(),
        splash or air_mass,
        constraint,
        late,
        min(0.85, 0.25 + max(now - u["seen_seconds"] for u in force) / 90),
        (
            f"Observed {total:g} supply; ground {ground:g}, armored ground {armored:g}, air {air:g}",
            "Desired replacements; existing living units are retained",
            "Race-specific counter priors; combat/tech delivery requires validation",
        ),
        (("high_templar", 2 * targets["archons"]),) if targets["archons"] else (),
    )
