"""Convert the current player's SDK observation into immutable strategic facts."""

from collections import deque

from sc2.position import Point2

from source.combat_assessment import home_threats, observed_supply, power, visible_threats
from source.composition import composition_targets
from source.endgame_sweep import BASE_TYPES
from source.strategic_plan import Assessment, Opportunity
from source.strategy_profiles import PROFILES


def ratio(friends, foes):
    return min(10.0, power(friends, foes) / max(1, power(foes, friends))) if foes else 10.0


class GameAssessment:
    def __init__(self):
        self.trades = deque()
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
        rally = front.towards(
            bot.game_info.map_center, max(8, PROFILES[bot.settings.profile]["rally_distance"])
        )
        if self.had_threat and not incoming:
            self.defended_at = bot.time
        self.had_threat = bool(incoming)
        threat = incoming.closest_to(front).position if incoming else None
        defenders = fighters.closer_than(26, threat) if threat is not None else fighters
        home_advantage = ratio(defenders, incoming)
        # Each local contact gets local support only. A distant army cannot
        # subsidize a losing skirmish on the other side of the map.
        local_advantage = 10.0
        army_supply = sum(bot.calculate_supply_cost(u.type_id) for u in fighters)
        remaining = list(contacts)
        while remaining:
            enemy = remaining.pop()
            friends = fighters.closer_than(18, enemy)
            if not friends:
                continue
            if sum(bot.calculate_supply_cost(u.type_id) for u in friends) < min(8, army_supply * 0.3):
                # Small detached fights are handled by that mission's controller.
                continue
            group = contacts.closer_than(14, enemy)
            local_advantage = min(local_advantage, ratio(friends, group))
            grouped = group.tags
            remaining = [unit for unit in remaining if unit.tag not in grouped]
        score = getattr(bot.state, "score", None)
        lost = sum(getattr(score, f"lost_{kind}_army", 0) for kind in ("minerals", "vespene"))
        killed = sum(getattr(score, f"killed_{kind}_army", 0) for kind in ("minerals", "vespene"))
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
            defenders_at_target = contacts.closer_than(20, building)
            targets.append(
                Opportunity(
                    str(building.tag),
                    tuple(building.position),
                    bot.time,
                    True,
                    economic,
                    (65 if economic else 28) + (12 if building.build_progress < 1 else 0),
                    power(defenders_at_target, fighters),
                    ratio(fighters, defenders_at_target),
                    min(
                        (unit.distance_to(building) for unit in fighters), default=front.distance_to(building)
                    ),
                )
            )
        for info in bot.scout_report.get("known_enemy_bases", []):
            point = Point2(tuple(info["position"]))
            if any(point.distance_to(Point2(target.position)) < 5 for target in targets):
                continue
            if bot.time - info["seen_seconds"] <= 90 and not bot.is_visible(point):
                targets.append(
                    Opportunity(
                        f"memory:{point}",
                        tuple(point),
                        info["seen_seconds"],
                        False,
                        True,
                        55,
                        0,
                        1,
                        front.distance_to(point),
                    )
                )
        sites = list(bot.enemy_start_locations) + list(bot.expansion_locations_list)
        for index, site in enumerate(sites):
            if any(base.distance_to(site) < 12 for base in bases):
                continue
            if any(unit.distance_to(site) < 6 for unit in fighters) and bot.is_visible(site):
                self.visited[tuple(site)] = bot.time
            if any(site.distance_to(Point2(t.position)) < 10 for t in targets):
                continue
            if bot.time - self.visited.get(tuple(site), -999) < 60:
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
                    front.distance_to(site),
                )
            )
        maximum = sum(unit.health_max + unit.shield_max for unit in fighters)
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
        )
