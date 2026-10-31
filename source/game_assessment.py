"""Convert the current player's SDK observation into immutable strategic facts."""

from collections import deque

from sc2.data import Race
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.combat_assessment import home_threats, observed_supply, power, visible_threats
from source.composition import composition_targets
from source.endgame_sweep import BASE_TYPES
from source.expansion_intel import is_expansion
from source.opponent_beliefs import beliefs_from_dict
from source.strategic_plan import Assessment, Opportunity
from source.strategy_profiles import PROFILES


def ratio(friends, foes):
    return min(10.0, power(friends, foes) / max(1, power(foes, friends))) if foes else 10.0


class GameAssessment:
    def __init__(self):
        self.trades = deque()
        self.loss_high_water = 0
        self.defended_at = -999
        self.had_threat = False
        self.upgrades = set()
        self.upgraded_at = -999
        self.visited = {}

    def observe(self, bot, army):
        fighters = army.filter(lambda unit: unit.can_attack)
        contacts = visible_threats(bot)
        incoming = home_threats(bot, contacts)
        bases = bot.townhalls.ready
        home = bot.start_location
        if bases:
            home = max(bases, key=lambda b: min((b.distance_to(e) for e in contacts), default=999)).position
        front = bases.closest_to(bot.game_info.map_center).position if bases else home
        # Search travel is paid by the army, which may already be across the
        # map. Home-relative costs repeatedly send it back to stale nearby sites.
        travel_origin = fighters.center if fighters else front
        rally = front.towards(
            bot.game_info.map_center, max(8, PROFILES[bot.settings.profile]["rally_distance"])
        )
        opening_hold = None
        opening_phase = getattr(bot, "opening_phase", None)
        if (
            bot.enemy_race == Race.Zerg
            and bot.settings.enabled
            and bot.settings.attack
            and bot.settings.production
            and bot.settings.strategy == "auto"
            and bot.time < 180
            and opening_phase in {"first_force", "defend"}
        ):
            rally = home.towards(bot.game_info.map_center, 3.5)
            opening_anchor = getattr(bot, "opening_defense_anchor", None)
            if opening_anchor:
                point = Point2(opening_anchor)
                batteries = bot.structures(U.SHIELDBATTERY).ready.filter(
                    lambda battery: battery.is_powered and battery.distance_to(point) <= 5.5
                )
                if batteries and bot.in_pathing_grid(point) and bot.is_visible(point):
                    home = rally = point
            opening_hold = tuple(rally)
        if self.had_threat and not incoming:
            self.defended_at = bot.time
        self.had_threat = bool(incoming)
        threat = incoming.closest_to(front).position if incoming else None
        defenders = fighters.closer_than(26, threat) if threat is not None else fighters
        home_advantage = ratio(defenders, incoming)
        # Each local contact gets local support only. A distant army cannot
        # subsidize a losing skirmish on the other side of the map.
        local_advantage = 10.0
        local_fight_observed = False
        army_supply = sum(bot.calculate_supply_cost(u.type_id) for u in fighters)
        remaining = list(contacts)
        while remaining:
            enemy = remaining.pop()
            friends = fighters.closer_than(18, enemy)
            if not friends:
                continue
            if sum(bot.calculate_supply_cost(u.type_id) for u in friends) < min(
                army_supply, max(8, army_supply * 0.3)
            ):
                # Small detached fights are handled by that mission's controller.
                continue
            local_fight_observed = True
            group = contacts.closer_than(14, enemy)
            local_advantage = min(local_advantage, ratio(friends, group))
            grouped = group.tags
            remaining = [unit for unit in remaining if unit.tag not in grouped]
        response_tags, response_supply = [], 0
        response = fighters.tags_in(set())
        budget = min(army_supply * 0.3, max(8, sum(observed_supply(bot, e) for e in incoming) * 1.5))
        # A projected remote response is distinct from defenders already nearby.
        # Require every selected actor to hit all observed attacking domains.
        if incoming and threat is not None:
            capable = fighters.filter(
                lambda u: all(u.can_attack_air if e.is_flying else u.can_attack_ground for e in incoming)
            )
            for unit in capable.sorted_by_distance_to(threat):
                cost = bot.calculate_supply_cost(unit.type_id)
                if response_supply + cost <= budget:
                    response_tags.append(unit.tag)
                    response_supply += cost
            response = fighters.tags_in(response_tags)
        response_advantage = ratio(response, incoming) if response else 0
        score = getattr(bot.state, "score", None)
        lost = sum(getattr(score, f"lost_{kind}_army", 0) for kind in ("minerals", "vespene"))
        killed = sum(getattr(score, f"killed_{kind}_army", 0) for kind in ("minerals", "vespene"))
        # Retail loss totals can dip during production accounting and rebound
        # without casualties. Count only new cumulative losses, not that rebound.
        self.loss_high_water = max(self.loss_high_water, lost)
        lost = self.loss_high_water
        self.trades.append((bot.time, lost, killed))
        while len(self.trades) > 1 and self.trades[1][0] < bot.time - 12:
            self.trades.popleft()
        loss, kills = lost - self.trades[0][1], killed - self.trades[0][2]
        trade_bad = loss >= 300 and loss > max(200, kills * 1.5)
        if bot.state.upgrades - self.upgrades:
            self.upgraded_at = bot.time
        self.upgrades = set(bot.state.upgrades)
        buildings = bot.enemy_structures.filter(lambda unit: unit.is_visible)
        targets = []
        for building in buildings:
            if building.is_flying and not any(unit.can_attack_air for unit in fighters):
                continue
            economic = building.type_id in BASE_TYPES
            expansion = economic and is_expansion(bot, building.position)
            defenders_at_target = contacts.closer_than(20, building)
            base_info = next(
                (
                    info
                    for info in bot.scout_report.get("enemy_bases", [])
                    if info.get("tag") == str(building.tag)
                ),
                {},
            )
            targets.append(
                Opportunity(
                    str(building.tag),
                    tuple(building.position),
                    bot.time,
                    True,
                    economic,
                    (65 if economic else 28)
                    + (20 if economic and building.build_progress < 1 else 0)
                    + min(12, base_info.get("workers_nearby", 0)),
                    power(defenders_at_target, fighters),
                    ratio(fighters, defenders_at_target),
                    min(
                        (unit.distance_to(building) for unit in fighters), default=front.distance_to(building)
                    ),
                    expansion=expansion,
                    defender_supply=sum(observed_supply(bot, u) for u in defenders_at_target),
                    static_defense=any(u.is_structure and u.can_attack_ground for u in defenders_at_target)
                    or base_info.get("visible_defense_buildings", 0) > 0,
                )
            )
        for info in bot.scout_report.get("known_enemy_bases", []):
            point = Point2(tuple(info["position"]))
            if any(point.distance_to(Point2(target.position)) < 5 for target in targets):
                continue
            if bot.time - info["seen_seconds"] <= 90 and not bot.is_visible(point):
                targets.append(
                    Opportunity(
                        info.get("tag", f"memory:{point}"),
                        tuple(point),
                        info["seen_seconds"],
                        False,
                        True,
                        55,
                        float(info.get("visible_defenders", 0) + info.get("visible_defense_buildings", 0)),
                        1,
                        travel_origin.distance_to(point),
                        expansion=info.get("expansion", is_expansion(bot, point)),
                        defender_supply=info.get("defender_supply", 0),
                        static_defense=info.get("visible_defense_buildings", 0) > 0,
                    )
                )
        sites = list(bot.enemy_start_locations) + list(bot.expansion_locations_list)
        checked = {tuple(info["position"]): info for info in bot.scout_report.get("expansion_sites", [])}
        for index, site in enumerate(sites):
            if any(base.distance_to(site) < 12 for base in bases):
                continue
            if any(unit.distance_to(site) < 6 for unit in fighters) and bot.is_visible(site):
                self.visited[tuple(site)] = bot.time
            if any(site.distance_to(Point2(t.position)) < 10 for t in targets):
                continue
            if bot.time - self.visited.get(tuple(site), -999) < 60:
                continue
            inspection = checked.get(tuple(site), {})
            if inspection.get("status") == "empty" and bot.time - inspection["last_checked"] < 45:
                continue
            targets.append(
                Opportunity(
                    f"site:{index}",
                    tuple(site),
                    bot.time,
                    False,
                    False,
                    40 if index == 0 else 32,
                    0,
                    1,
                    travel_origin.distance_to(site),
                )
            )
        maximum = sum(unit.health_max + unit.shield_max for unit in fighters)
        beliefs = beliefs_from_dict(bot.scout_report.get("opponent_beliefs"))
        return Assessment(
            bot.state.game_loop,
            bot.time,
            bot.settings.profile,
            sum(bot.calculate_supply_cost(u.type_id) for u in fighters),
            len(fighters),
            sum(u.health + u.shield for u in fighters) / maximum if maximum else 1,
            local_advantage,
            sum(max(1, observed_supply(bot, u)) for u in incoming),
            home_advantage,
            tuple(home),
            tuple(rally),
            tuple(threat) if threat is not None else None,
            tuple(targets),
            bot.time - bot.scout_report.get("last_seen_seconds", -999),
            bot.minerals,
            bot.vespene,
            bot.supply_workers,
            len(bases),
            tuple(composition_targets(bot).items()),
            trade_bad,
            bot.time - self.defended_at <= 30 and kills >= max(100, loss),
            bot.time - self.upgraded_at <= 30,
            # Strong recent trades plus fresh evidence of a depleted army.
            # Absence of visible enemies alone never authorizes dispersal.
            kills >= max(800, loss * 3)
            and bot.time - bot.scout_report.get("last_seen_seconds", -999) <= 10
            and bot.scout_report.get("composition_intel", {}).get("supply", 999) < army_supply * 0.2,
            rush_warning=bot.time < bot.scout_report.get("rush_warning", {}).get("expires_at", 0),
            local_fight_observed=local_fight_observed,
            raid_response_tags=tuple(response_tags),
            raid_response_supply=response_supply,
            raid_response_advantage=response_advantage,
            opening_hold=opening_hold,
            opponent_beliefs=beliefs.relative_to(army_supply) if beliefs is not None else None,
            adaptive_composition=bot.settings.adaptive_composition,
        )
