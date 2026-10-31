"""Positive scouted economic targets authorize inspection, never fog attacks."""

from math import isfinite

from sc2.position import Point2


def oracle_inspection(bot, oracle, anti_air, blocked, worker_lines=None):
    choices = []
    for base in worker_lines if worker_lines is not None else bot.scout_report.get("known_enemy_bases", []):
        seen = base.get("seen_seconds", -999)
        if not isinstance(seen, (int, float)) or not isfinite(seen) or not 0 <= bot.time - seen <= 120:
            continue
        if base.get("workers_nearby", 0) < 3 or base.get("build_progress", 1) < 0.9:
            continue
        point = Point2(base.get("worker_line_position", base["position"]))
        key = str(base.get("tag", tuple(point)))
        if blocked.get(key, 0) > bot.time:
            continue
        if any(enemy.distance_to(point) <= max(6, enemy.air_range) + enemy.radius + 6 for enemy in anti_air):
            continue
        score = (
            min(16, base["workers_nearby"]) * 2
            - oracle.distance_to(point) * 0.12
            - (bot.time - seen) * 0.12
            - base.get("visible_defense_buildings", 0) * 8
        )
        choices.append(
            (
                score,
                {
                    "id": key,
                    "position": list(point),
                    "seen_seconds": seen,
                    "evidence": "Previously observed workers; current occupancy and air defense uncertain",
                },
            )
        )
    return max(choices, key=lambda item: item[0])[1] if choices else None
