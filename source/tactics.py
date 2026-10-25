"""Observable-state tactical policies; all orders retain human ownership checks."""

from dataclasses import asdict, dataclass

from sc2.position import Point2

from source.economy_assistant import ARMY_TARGETS
from source.strategy_profiles import PROFILES
from source.strategy_scripts import run_strategy_script


@dataclass(frozen=True)
class TacticalSituation:
    army_supply: float
    army_count: int
    health_fraction: float
    nearby_enemy_strength: float
    own_strength: float
    base_threat: bool
    previous: str = "regroup"


def choose_strategy(state: TacticalSituation, requested: str, policy=None) -> tuple[str, str]:
    policy = policy or PROFILES["balanced"]
    if requested != "auto":
        return requested, "Manually selected strategy"
    if not state.army_count:
        return "regroup", "No combat units available"
    if (
        state.health_fraction < policy["retreat_health"]
        or state.nearby_enemy_strength > state.own_strength * policy["danger_ratio"]
    ):
        return "retreat", "Army depleted or locally outmatched"
    if state.base_threat:
        return "defend", "Visible hostile combat units near a base"
    threshold = policy["continue_supply"] if state.previous == "push" else policy["attack_supply"]
    if state.army_supply >= threshold:
        return "push", "Army reached attack threshold"
    return "regroup", "Build and assemble army before attacking"


class TacticalController:
    def __init__(self):
        self.previous = "regroup"
        self.active_mode = "manual"
        self.enemy_buildings = {}

    def tick(self, bot, observation=None):
        self.active_mode = "manual"
        policy = PROFILES[bot.settings.profile]
        army = bot.units.of_type(set(ARMY_TARGETS)).ready
        fighters = army.filter(lambda unit: unit.can_attack)
        bases = bot.townhalls.ready
        enemies = bot.enemy_units.filter(lambda unit: unit.is_visible and unit.can_attack)
        threats = enemies.filter(lambda unit: any(unit.distance_to(base) < 22 for base in bases))
        nearby = enemies.filter(lambda enemy: any(enemy.distance_to(unit) < 18 for unit in fighters))
        maximum = sum(unit.health_max + unit.shield_max for unit in fighters)
        health = sum(unit.health + unit.shield for unit in fighters)
        strength = lambda units: sum(  # noqa: E731
            (unit.health + unit.shield) * max(unit.ground_dps, unit.air_dps, 1) for unit in units
        )
        state = TacticalSituation(
            bot.supply_army,
            len(fighters),
            health / maximum if maximum else 1,
            strength(nearby),
            strength(fighters),
            bool(threats),
            self.previous,
        )
        strategy, reason = choose_strategy(state, bot.settings.strategy, policy)
        decision = {
            "strategy": strategy,
            "reason": reason,
            "situation": asdict(state),
            "profile": bot.settings.profile,
            "orders": [],
        }
        if not bot.settings.enabled or not bot.settings.attack:
            decision.update(strategy="manual", reason="Attack control disabled or assistant paused")
            return decision
        script_target = None
        if bot.settings.strategy_script:
            try:
                plan = run_strategy_script(
                    bot.settings.strategy_script,
                    {
                        "schema_version": 1,
                        "situation": asdict(state),
                        "profile": policy,
                        "observation": observation,
                        "previous_strategy": self.previous,
                    },
                )
                strategy = plan["strategy"]
                decision.update(plan)
                script_target = plan.get("target")
            except Exception as exc:
                decision.update(
                    strategy="manual", reason=f"Strategy script rejected: {type(exc).__name__}: {exc}"
                )
                return decision
        self.previous = strategy
        home = bases.closest_to(bot.start_location).position if bases else bot.start_location
        front = bases.closest_to(bot.game_info.map_center).position if bases else home
        target = (
            home
            if strategy == "retreat"
            else front.towards(bot.game_info.map_center, policy["rally_distance"])
        )
        if strategy == "defend" and threats:
            target = threats.closest_to(front).position
        elif strategy == "push":
            buildings = bot.enemy_structures.filter(lambda unit: unit.is_visible)
            for building in buildings:
                self.enemy_buildings[building.tag] = building.position
            for tag, position in list(self.enemy_buildings.items()):
                if bot.is_visible(position) and not any(b.distance_to(position) < 3 for b in buildings):
                    del self.enemy_buildings[tag]
            if buildings:
                target = buildings.closest_to(front).position
            elif self.enemy_buildings:
                target = min(self.enemy_buildings.values(), key=front.distance_to)
            elif bot.enemy_start_locations:
                target = bot.enemy_start_locations[0]
                # Once the enemy spawn is visibly clear, search known expansion
                # locations; no hidden enemy state or remembered omniscient units.
                if bot.is_visible(target) and not enemies.closer_than(15, target):
                    locations = bot.expansion_locations_list
                    if locations:
                        target = locations[int(bot.time // 30) % len(locations)]
        if script_target is not None:
            target = Point2(tuple(script_target))
            area = bot.game_info.playable_area
            if not (area.x <= target.x <= area.x + area.width and area.y <= target.y <= area.y + area.height):
                decision.update(strategy="manual", reason="Script target outside playable map")
                return decision
        target = Point2((target.x, target.y))
        self.active_mode = strategy
        decision["target"] = list(target)
        for unit in army:
            if not bot.available(unit):
                continue
            move = strategy in {"retreat", "regroup"} or not unit.can_attack
            if move and unit.distance_to(target) < 3:
                continue
            # Don't replace a matching standing order every polling interval.
            if unit.orders:
                order = unit.orders[0]
                if isinstance(order.target, Point2) and order.target.distance_to(target) < 2:
                    continue
            command = unit.move(target) if move else unit.attack(target)
            if bot.issue(command):
                decision["orders"].append({"unit_tag": unit.tag, "action": "move" if move else "attack"})
        return decision

    def micro(self, bot):
        """Protect damaged units and focus reachable threats between strategy polls."""
        if not bot.settings.enabled or not bot.settings.attack or self.active_mode not in {"push", "defend"}:
            return []
        decisions = []
        enemies = bot.enemy_units.filter(lambda unit: unit.is_visible and unit.can_be_attacked)
        for unit in bot.units.of_type(set(ARMY_TARGETS)).ready:
            if not bot.available(unit) or not unit.can_attack:
                continue
            maximum = unit.health_max + unit.shield_max
            targets = enemies.filter(lambda enemy, unit=unit: unit.target_in_range(enemy))
            command, reason = None, None
            if maximum and (unit.health + unit.shield) / maximum < 0.25:
                home = (
                    bot.townhalls.ready.closest_to(unit).position
                    if bot.townhalls.ready
                    else bot.start_location
                )
                command, reason = unit.move(home), "individual_retreat"
            elif targets and unit.weapon_cooldown == 0:
                target = min(
                    targets,
                    key=lambda enemy: (
                        not enemy.can_attack,
                        enemy.health + enemy.shield,
                        unit.distance_to(enemy),
                    ),
                )
                if unit.order_target != target.tag:
                    command, reason = unit.attack(target), "focus_fire"
            elif targets and unit.weapon_cooldown > 0 and unit.ground_range >= 4:
                threat = targets.closest_to(unit)
                if threat.can_attack_ground and threat.ground_range < unit.ground_range:
                    destination = unit.position.towards(threat.position, -2)
                    if bot.is_visible(destination) and bot.in_pathing_grid(destination):
                        command, reason = unit.move(destination), "kite_melee"
            if command is not None and bot.issue(command):
                decisions.append({"unit_tag": unit.tag, "action": reason})
        return decisions
