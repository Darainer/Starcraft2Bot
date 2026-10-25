"""Split a large late-game army to finish known structures and search enemy-side sites."""

from statistics import median

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

WEIGHTS = {0: 0.6, 1: 0.2, 2: 0.2}
BASE_TYPES = {
    U.COMMANDCENTER,
    U.ORBITALCOMMAND,
    U.PLANETARYFORTRESS,
    U.NEXUS,
    U.HATCHERY,
    U.LAIR,
    U.HIVE,
}
DEFENSE_TYPES = {
    U.BUNKER,
    U.MISSILETURRET,
    U.PHOTONCANNON,
    U.PLANETARYFORTRESS,
    U.SPINECRAWLER,
    U.SPORECRAWLER,
    U.AUTOTURRET,
}


def group_center(units):
    return Point2((median(unit.position.x for unit in units), median(unit.position.y for unit in units)))


def exposed_base_target(bot, buildings, attackers):
    """Prefer a visible, weakly defended resource center that this squad can hit."""
    bases = buildings.filter(lambda unit: unit.is_visible and unit.type_id in BASE_TYPES)
    visible_combat = bot.enemy_units.filter(lambda unit: unit.is_visible and unit.can_attack)
    visible_defenses = buildings.filter(lambda unit: unit.is_visible and unit.type_id in DEFENSE_TYPES)
    candidates = []
    for base in bases:
        if base.is_flying and not any(unit.can_attack_air for unit in attackers):
            continue
        combat = visible_combat.closer_than(18, base)
        defenses = visible_defenses.closer_than(22, base)
        exposure = 100 / (1 + len(combat) + 2 * len(defenses))
        distance = min((unit.distance_to(base) for unit in attackers), default=0)
        candidates.append((exposure - distance * 0.05, base))
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


class EndgameSweep:
    def __init__(self):
        self.active = False
        self.assignments = {}
        self.site_indices = {0: 0, 1: 1, 2: 2}
        self.visited_sites = set()
        self.denial_sites = {}

    def start(self):
        self.active = True
        self.assignments.clear()
        self.site_indices = {0: 0, 1: 1, 2: 2}
        self.visited_sites.clear()
        self.denial_sites.clear()

    def _sites(self, bot):
        if not bot.enemy_start_locations:
            return [bot.game_info.map_center]
        enemy_start = bot.enemy_start_locations[0]
        sites = [enemy_start]
        for location in sorted(bot.expansion_locations_list, key=enemy_start.distance_to):
            if any(location.distance_to(base) < 12 for base in bot.townhalls.ready):
                continue
            if all(location.distance_to(existing) >= 8 for existing in sites):
                sites.append(location)
        return sites or [enemy_start]

    def plan(self, bot, army, buildings, threats, bases):
        units = army.filter(bot.available)
        alive = {unit.tag for unit in units}
        self.assignments = {tag: group for tag, group in self.assignments.items() if tag in alive}
        group_supply = {group: 0 for group in WEIGHTS}
        for unit in units:
            group = self.assignments.get(unit.tag)
            if group is not None:
                group_supply[group] += bot.calculate_supply_cost(unit.type_id)
        for unit in sorted(units, key=lambda item: item.tag):
            if unit.tag in self.assignments:
                continue
            group = min(WEIGHTS, key=lambda key: group_supply[key] / WEIGHTS[key])
            self.assignments[unit.tag] = group
            group_supply[group] += bot.calculate_supply_cost(unit.type_id)

        groups = {
            group: units.filter(lambda unit, group=group: self.assignments[unit.tag] == group)
            for group in WEIGHTS
        }
        sites = self._sites(bot)
        visible_buildings = buildings.filter(lambda unit: unit.is_visible)
        scouting_complete = len(self.visited_sites) >= len(sites)
        enemy_anchor = bot.enemy_start_locations[0] if bot.enemy_start_locations else bot.game_info.map_center
        raid_target = None
        if threats and bases:
            raid_target = min(
                threats,
                key=lambda enemy: min(enemy.distance_to(base) for base in bases),
            )
        destinations = {}
        report = {
            "mode": "split_search",
            "groups": [],
            "visited_sites": sorted(self.visited_sites),
            "site_count": len(sites),
            "scouting_complete": scouting_complete,
            "denial_sites": {str(group): index for group, index in self.denial_sites.items()},
        }

        for group_id, group_units in groups.items():
            if not group_units:
                continue
            anchor = group_center(group_units)
            index = self.site_indices[group_id] % len(sites)
            site = sites[index]
            if anchor.distance_to(site) <= 10 and bot.is_visible(site):
                self.visited_sites.add(index)
                if not visible_buildings.closer_than(8, site):
                    index = (index + len(WEIGHTS)) % len(sites)
                    self.site_indices[group_id] = index
                    site = sites[index]
            scouting_complete = len(self.visited_sites) >= len(sites)

            local_buildings = visible_buildings.closer_than(12, site)
            if group_id == 0 and visible_buildings:
                building = exposed_base_target(bot, visible_buildings, group_units)
                if building is None:
                    building = visible_buildings.closest_to(anchor)
            elif local_buildings:
                building = exposed_base_target(bot, local_buildings, group_units)
                if building is None:
                    building = local_buildings.closest_to(anchor)
            else:
                building = None

            if scouting_complete and group_id in {1, 2}:
                available_sites = [
                    site_index
                    for site_index, candidate in enumerate(sites)
                    if not visible_buildings.closer_than(8, candidate)
                ]
                available_sites.sort(key=lambda site_index: sites[site_index].distance_to(enemy_anchor))
                if available_sites:
                    denial_index = self.denial_sites.get(group_id)
                    if denial_index not in available_sites:
                        denial_index = available_sites[min(group_id - 1, len(available_sites) - 1)]
                        self.denial_sites[group_id] = denial_index
                    site = sites[denial_index]
                    local_buildings = visible_buildings.closer_than(12, site)
                    building = exposed_base_target(bot, local_buildings, group_units)
                    if building is None and local_buildings:
                        building = local_buildings.closest_to(anchor)
            target = building.position if building is not None else site
            phase = (
                "clear_visible_structure"
                if building is not None
                else "deny_expansion"
                if scouting_complete and group_id in {1, 2}
                else "search_site"
            )

            if group_id == 2 and raid_target is not None:
                target = raid_target.position
                building = None
                phase = "respond_to_base_raid"

            supply = sum(bot.calculate_supply_cost(unit.type_id) for unit in group_units)
            cohesion = sum(
                bot.calculate_supply_cost(unit.type_id)
                for unit in group_units
                if unit.distance_to(anchor) <= 9
            ) / max(1, supply)
            waypoint = (
                anchor if cohesion < 0.75 else anchor.towards(target, min(10, anchor.distance_to(target)))
            )
            direction = target - anchor
            length = max(direction.length, 1)
            forward = Point2((direction.x / length, direction.y / length))
            for offset, unit in enumerate(sorted(group_units, key=lambda item: item.tag)):
                depth = (offset // 4) * 1.8
                lateral = (offset % 4 - 1.5) * 1.8
                slot = waypoint.offset(
                    (forward.x * depth - forward.y * lateral, forward.y * depth + forward.x * lateral)
                )
                move = not unit.can_attack or cohesion < 0.75 or anchor.distance_to(target) > 12
                if building is not None and building.is_flying and not unit.can_attack_air:
                    move = True
                if raid_target is not None and group_id == 2 and unit.can_attack:
                    move = not (unit.can_attack_air if raid_target.is_flying else unit.can_attack_ground)
                maximum = unit.health_max + unit.shield_max
                if maximum and (unit.health + unit.shield) / maximum < 0.25:
                    move, slot = True, bases.closest_to(unit).position if bases else bot.start_location
                destinations[unit.tag] = ("move" if move else "attack", slot)

            report["groups"].append(
                {
                    "id": group_id,
                    "members": sorted(unit.tag for unit in group_units),
                    "supply": supply,
                    "center": list(anchor),
                    "target": list(target),
                    "site_index": index,
                    "phase": phase,
                    "cohesion": cohesion,
                }
            )
        report.update(
            visited_sites=sorted(self.visited_sites),
            site_count=len(sites),
            scouting_complete=len(self.visited_sites) >= len(sites),
            denial_sites={str(group): index for group, index in self.denial_sites.items()},
        )
        return destinations, report
