"""Spaced building placement, mining corridors, and local ground connectivity."""

import math
from collections import deque

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

PRODUCTION = {U.GATEWAY, U.WARPGATE, U.ROBOTICSFACILITY, U.STARGATE}


def half_size(kind):
    return 2.5 if kind == U.NEXUS else 1 if kind == U.PYLON else 1.5


def segment_distance(point, start, end):
    dx, dy = end.x - start.x, end.y - start.y
    length = dx * dx + dy * dy
    fraction = max(0, min(1, ((point.x - start.x) * dx + (point.y - start.y) * dy) / length)) if length else 0
    return point.distance_to(Point2((start.x + fraction * dx, start.y + fraction * dy)))


def layout_clear(bot, kind, point):
    radius = half_size(kind)
    for building in bot.structures:
        clearance = radius + half_size(building.type_id) + 2
        if abs(point.x - building.position.x) < clearance and abs(point.y - building.position.y) < clearance:
            return False
    for base in bot.townhalls:
        resources = list(bot.mineral_field.closer_than(12, base))
        resources += list(bot.vespene_geyser.closer_than(12, base))
        if any(
            segment_distance(point, base.position, resource.position) < radius + 1.5 for resource in resources
        ):
            return False
        exit_point = base.position.towards(bot.game_info.map_center, 18)
        if segment_distance(point, base.position, exit_point) < radius + 2:
            return False
    for building in bot.structures.of_type(PRODUCTION):
        exit_point = building.position.towards(bot.game_info.map_center, 8)
        if segment_distance(point, building.position, exit_point) < radius + 2:
            return False
    return True


def preserves_local_paths(grid, point, radius, units):
    if grid is None:
        return True
    x0, y0 = int(point.x), int(point.y)
    left, right = max(1, x0 - 14), min(grid.width - 2, x0 + 14)
    bottom, top = max(1, y0 - 14), min(grid.height - 2, y0 + 14)

    def reachable(block):
        def walkable(x, y):
            if block and abs(x - point.x) < radius + 0.75 and abs(y - point.y) < radius + 0.75:
                return False
            return all(grid[Point2((x + dx, y + dy))] for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)))

        edge = [(x, y) for x in range(left, right + 1) for y in (bottom, top)]
        edge += [(x, y) for y in range(bottom, top + 1) for x in (left, right)]
        seen = {p for p in edge if walkable(*p)}
        queue = deque(seen)
        while queue:
            x, y = queue.popleft()
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if left <= nx <= right and bottom <= ny <= top and (nx, ny) not in seen and walkable(nx, ny):
                    seen.add((nx, ny))
                    queue.append((nx, ny))
        return seen

    origins = [
        (int(u.position.x), int(u.position.y)) for u in units if not u.is_flying and u.distance_to(point) < 12
    ]
    if not origins:
        return True
    before, after = reachable(False), reachable(True)
    return all(origin not in before or origin in after for origin in origins)


async def find_spaced_placement(bot, kind, near, max_distance):
    if kind == U.NEXUS:
        return await bot.find_placement(kind, near, max_distance=max_distance, random_alternative=False)
    for distance in range(0, max_distance + 1, 2):
        for index in range(8 if distance else 1):
            angle = index * math.pi / 4
            anchor = near.offset((round(distance * math.cos(angle)), round(distance * math.sin(angle))))
            if not layout_clear(bot, kind, anchor):
                continue
            placement = await bot.find_placement(kind, anchor, max_distance=0, random_alternative=False)
            if placement is None or not layout_clear(bot, kind, placement):
                continue
            if preserves_local_paths(
                getattr(bot.game_info, "pathing_grid", None), placement, half_size(kind), bot.units
            ):
                return placement
    return None
