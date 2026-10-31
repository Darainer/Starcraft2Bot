"""Short, exposure-scored formation moves before committing to visible siege.

Costs and the six/ten-second latches are experimental heuristics. This is not
a battle simulator or a rule forbidding all entry into enemy weapon range.
"""

from math import ceil, cos, pi, sin

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2


def approach_siege(bot, squad, contacts, goal, previous, geometry):
    ground = [unit for unit in squad if not unit.is_flying and unit.can_attack]
    tanks = [enemy for enemy in contacts if enemy.is_visible and enemy.type_id == U.SIEGETANKSIEGED]
    if (
        not ground
        or not tanks
        or not any(
            unit.distance_to(tank) <= tank.ground_range + tank.radius + unit.radius + 4
            for unit in ground
            for tank in tanks
        )
    ):
        return None
    tags = sorted(tank.tag for tank in tanks)
    if any(unit.target_in_range(tank) for unit in ground for tank in tanks):
        return {"siege_phase": "commit", "siege_commit_until": bot.time + 10, "siege_tags": tags}
    if previous.get("siege_commit_until", 0) > bot.time:
        return {
            "siege_phase": "commit",
            "siege_commit_until": previous["siege_commit_until"],
            "siege_tags": tags,
        }
    anchor = squad.center
    if previous.get("siege_phase") == "approach":
        point = Point2(previous["approach_goal"])
        if bot.time >= previous["approach_until"] or anchor.distance_to(point) <= 3:
            return {"siege_phase": "commit", "siege_commit_until": bot.time + 10, "siege_tags": tags}
        return {
            key: previous[key]
            for key in (
                "siege_phase",
                "approach_goal",
                "approach_until",
                "approach_members",
                "siege_tags",
                "approach_cost",
            )
        }
    area = getattr(bot.game_info, "playable_area", None)

    def walkable(point):
        return (
            area is None
            or area.x <= point.x < area.x + area.width
            and area.y <= point.y < area.y + area.height
        ) and bot.in_pathing_grid(point)

    direction = goal - anchor
    length = max(1, direction.length)
    dx, dy = direction.x / length, direction.y / length
    candidates = []
    for angle in (0, pi / 3, -pi / 3, pi / 2, -pi / 2, pi):
        step = 4 if angle == pi else 8
        delta = Point2(
            (step * (dx * cos(angle) - dy * sin(angle)), step * (dx * sin(angle) + dy * cos(angle)))
        )
        point = anchor.offset(delta)
        if not bot.is_visible(point) or not all(
            walkable(unit.position.offset((delta.x * i / ceil(step), delta.y * i / ceil(step))))
            for unit in ground
            for i in range(1, ceil(step) + 1)
        ):
            continue
        exposed = sorted(
            ground, key=lambda unit: min(unit.distance_to(tank) - tank.ground_range for tank in tanks)
        )[:5]
        risk = 0.0
        for unit in exposed:
            for fraction in (0.25, 0.5, 0.75, 1):
                position = unit.position.offset((delta.x * fraction, delta.y * fraction))
                risk += sum(
                    gd * max(0, gr + er + unit.radius + 1 - position.distance_to(Point2((x, y))))
                    for x, y, er, gr, ar, gd, ad, hits_ground, hits_air in geometry
                    if hits_ground
                )
        health = max(1, sum(unit.health + unit.shield for unit in exposed))
        cost = risk / health + point.distance_to(goal) * 0.12
        candidates.append((cost, point.x, point.y, point))
    if not candidates:
        return None  # No claimed safe path; existing abort/retreat controllers retain authority.
    cost, _, _, point = min(candidates)
    return {
        "siege_phase": "approach",
        "approach_goal": list(point),
        "approach_until": bot.time + 6,
        "approach_members": [unit.tag for unit in ground],
        "siege_tags": tags,
        "approach_cost": cost,
    }
