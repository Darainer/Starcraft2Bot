"""Observable-state tactical policies; all orders retain human ownership checks."""

from dataclasses import asdict, dataclass

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.army_waves import ArmyWaves
from source.economy_assistant import ARMY_TARGETS
from source.endgame_sweep import EndgameSweep, exposed_base_target
from source.strategy_profiles import PROFILES
from source.strategy_scripts import run_strategy_script

WORKER_TYPES = {U.PROBE, U.SCV, U.DRONE}


@dataclass(frozen=True)
class TacticalSituation:
    army_supply: float
    army_count: int
    health_fraction: float
    nearby_enemy_strength: float
    own_strength: float
    base_threat: bool
    previous: str = "regroup"
    enemy_supply: float = 0
    local_friendly_supply: float = 0
    outmatched: bool = False
    trade_disadvantage: bool = False


def choose_strategy(state: TacticalSituation, requested: str, policy=None) -> tuple[str, str]:
    policy = policy or PROFILES["balanced"]
    if requested != "auto":
        return requested, "Manually selected strategy"
    if not state.army_count:
        return "regroup", "No combat units available"
    if state.trade_disadvantage:
        return "retreat", "Recent army losses exceeded enemy losses; regroup and rebuild before trading again"
    if state.base_threat and state.outmatched:
        return "retreat", "Enemy force exceeds nearby defenders; regroup and rebuild before engaging"
    if state.base_threat:
        return "defend", "Visible hostile force approaching a base"
    if (
        state.health_fraction < policy["retreat_health"]
        or state.nearby_enemy_strength > state.own_strength / policy["danger_ratio"]
    ):
        return "retreat", "Army depleted or locally outmatched"
    threshold = policy["continue_supply"] if state.previous == "push" else policy["attack_supply"]
    if state.army_supply >= threshold:
        return "push", "Army reached attack threshold"
    return "regroup", "Build and assemble army before attacking"


class TacticalController:
    def __init__(self):
        self.previous = "regroup"
        self.active_mode = "manual"
        self.enemy_buildings = {}
        self.waves = ArmyWaves()
        self.endgame_sweep = EndgameSweep()
        self.last_incoming_seconds = -999
        self.last_incoming_position = None
        self.economic_emergency_until = -999
        self.trade_emergency_until = -999
        self.trade_totals = None

    def tick(self, bot, observation=None, available_abilities=None):
        self.active_mode = "manual"
        policy = PROFILES[bot.settings.profile]
        army = bot.units.of_type(set(ARMY_TARGETS)).ready
        fighters = army.filter(lambda unit: unit.can_attack)
        bases = bot.townhalls.ready
        visible_enemies = bot.enemy_units.filter(lambda unit: unit.is_visible)
        enemies = visible_enemies.filter(lambda unit: unit.can_attack and unit.type_id not in WORKER_TYPES)
        enemy_force = visible_enemies.filter(lambda unit: unit.type_id not in WORKER_TYPES)
        close_threats = enemies.filter(lambda unit: any(unit.distance_to(base) < 22 for base in bases))
        incoming_force = enemy_force.filter(lambda unit: any(unit.distance_to(base) < 120 for base in bases))
        incoming = enemies.filter(lambda unit: any(unit.distance_to(base) < 120 for base in bases))
        incoming_supply = sum(bot.calculate_supply_cost(unit.type_id) for unit in incoming_force)
        group_approach = len(incoming_force) >= 3 and incoming_supply >= 6
        threat_units = incoming if group_approach else close_threats
        if group_approach:
            center_x = sum(unit.position.x for unit in incoming_force) / len(incoming_force)
            center_y = sum(unit.position.y for unit in incoming_force) / len(incoming_force)
            force_center = Point2((center_x, center_y))
        elif close_threats:
            closest_contact = min(
                close_threats,
                key=lambda unit: min((unit.distance_to(base) for base in bases), default=0),
            )
            force_center = closest_contact.position
        else:
            force_center = None
        local_fighters = (
            fighters.filter(lambda unit: unit.distance_to(force_center) < 45)
            if force_center is not None
            else fighters
        )
        local_supply = sum(bot.calculate_supply_cost(unit.type_id) for unit in local_fighters)
        incoming_strength = sum(
            (unit.health + unit.shield) * max(unit.ground_dps, unit.air_dps, 1) for unit in incoming
        )
        local_strength = sum(
            (unit.health + unit.shield) * max(unit.ground_dps, unit.air_dps, 1) for unit in local_fighters
        )
        outmatched = (
            group_approach
            and incoming_supply >= 8
            and (incoming_supply > local_supply * 1.15 or incoming_strength > local_strength * 1.15)
        )
        score_details = (observation or {}).get("observation", {}).get("score", {}).get("score_details", {})
        army_losses = score_details.get("lost_minerals", {}).get("army", 0) + score_details.get(
            "lost_vespene", {}
        ).get("army", 0)
        army_kills = score_details.get("killed_minerals", {}).get("army", 0) + score_details.get(
            "killed_vespene", {}
        ).get("army", 0)
        if self.trade_totals is None:
            loss_delta = kill_delta = 0
        else:
            loss_delta = max(0, army_losses - self.trade_totals[0])
            kill_delta = max(0, army_kills - self.trade_totals[1])
        if loss_delta >= 250 and loss_delta > max(200, kill_delta * 1.25):
            self.trade_emergency_until = bot.time + 60
        self.trade_totals = (army_losses, army_kills)
        trade_disadvantage = bot.time <= self.trade_emergency_until
        if group_approach:
            self.last_incoming_seconds = bot.time
            self.last_incoming_position = list(force_center)
        recent_raid = bot.time - self.last_incoming_seconds <= 35
        threats = threat_units
        threat_contacts = incoming if incoming else close_threats
        threatened_base = None
        if bases and threat_contacts:

            def base_pressure(base):
                nearby = threat_contacts.closer_than(35, base)
                pressure = sum(bot.calculate_supply_cost(unit.type_id) for unit in nearby)
                distance = min((unit.distance_to(base) for unit in threat_contacts), default=999)
                return pressure, -distance

            threatened_base = max(bases, key=base_pressure)
        elif bases and recent_raid and self.last_incoming_position:
            threatened_base = bases.closest_to(Point2(tuple(self.last_incoming_position)))
        if outmatched or trade_disadvantage:
            self.economic_emergency_until = max(
                self.economic_emergency_until, bot.time + (45 if outmatched else 60)
            )
        emergency = bot.time <= self.economic_emergency_until
        outmatched_latched = outmatched or emergency
        bot.economic_emergency = bool(
            emergency
            and bot.settings.enabled
            and bot.settings.attack
            and bot.settings.strategy == "auto"
            and not bot.settings.strategy_script
        )
        nearby = enemies.filter(lambda enemy: any(enemy.distance_to(unit) < 18 for unit in fighters))
        maximum = sum(unit.health_max + unit.shield_max for unit in fighters)
        health = sum(unit.health + unit.shield for unit in fighters)
        strength = lambda units: sum(  # noqa: E731
            (unit.health + unit.shield) * max(unit.ground_dps, unit.air_dps, 1) for unit in units
        )
        active_wave = fighters.filter(lambda unit: unit.tag in self.waves.members) if nearby else []
        engagement_fighters = local_fighters if group_approach else active_wave if active_wave else fighters
        state = TacticalSituation(
            bot.supply_army,
            len(fighters),
            health / maximum if maximum else 1,
            strength(nearby),
            strength(engagement_fighters),
            bool(close_threats or group_approach or recent_raid),
            self.previous,
            incoming_supply,
            local_supply,
            outmatched_latched,
            trade_disadvantage,
        )
        strategy, reason = choose_strategy(state, bot.settings.strategy, policy)
        decision = {
            "strategy": strategy,
            "reason": reason,
            "situation": asdict(state),
            "profile": bot.settings.profile,
            "force_comparison": {
                "enemy_supply": incoming_supply,
                "local_friendly_supply": local_supply,
                "enemy_to_friendly_strength_ratio": round(incoming_strength / max(1, local_strength), 3),
                "outmatched": outmatched,
                "economic_emergency": bot.economic_emergency,
                "recent_army_loss_value": loss_delta,
                "recent_enemy_kill_value": kill_delta,
                "cumulative_trade_ratio": round(army_kills / max(1, army_losses), 3),
                "trade_disadvantage": trade_disadvantage,
            },
            "orders": [],
        }
        decision["incoming_force"] = (
            {
                "unit_count": len(incoming),
                "supply": incoming_supply,
                "nearest_base_distance": min(
                    (unit.distance_to(base) for unit in incoming for base in bases),
                    default=None,
                ),
            }
            if group_approach
            else (
                {
                    "unit_count": 0,
                    "supply": 0,
                    "last_seen_seconds": self.last_incoming_seconds,
                    "last_position": self.last_incoming_position,
                    "latched": True,
                }
                if recent_raid
                else None
            )
        )
        decision["threatened_base"] = (
            {"tag": threatened_base.tag, "position": list(threatened_base.position)}
            if threatened_base is not None
            else None
        )
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
                        "available_abilities": available_abilities,
                        "previous_strategy": self.previous,
                        "wave": self.waves.last_state,
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
        if (
            self.endgame_sweep.active
            and strategy == "defend"
            and bot.settings.strategy == "auto"
            and not bot.settings.strategy_script
        ):
            strategy = "push"
            reason = "Keep endgame search groups moving; dispatch one group to the base raid"
            decision.update(strategy=strategy, reason=reason)
        split_defense = None
        if (
            strategy == "defend"
            and bot.settings.strategy == "auto"
            and not bot.settings.strategy_script
            and bot.settings.army_waves
            and self.waves.members
            and threats
            and bases
        ):
            active_wave = fighters.filter(lambda unit: unit.tag in self.waves.members)
            active_supply = sum(bot.calculate_supply_cost(unit.type_id) for unit in active_wave)
            if active_supply >= max(24, policy["continue_supply"]):
                defense_base = threatened_base or min(
                    bases,
                    key=lambda base: min(enemy.distance_to(base) for enemy in threats),
                )
                threat = threats.closest_to(defense_base)
                local_threats = enemies.filter(lambda enemy: enemy.distance_to(defense_base) < 22)
                enemy_supply = sum(bot.calculate_supply_cost(unit.type_id) for unit in local_threats)
                keep_attacking = max(8, active_supply * 0.55)
                defense_goal = min(
                    max(0, active_supply - keep_attacking),
                    max(8, enemy_supply * 1.5),
                )
                compatible = active_wave.filter(
                    lambda unit: unit.can_attack_air if threat.is_flying else unit.can_attack_ground
                ).sorted_by_distance_to(threat)
                defenders = []
                defense_supply = 0
                if enemy_supply < active_supply * 0.55:
                    for unit in compatible:
                        if not bot.available(unit):
                            continue
                        defenders.append(unit)
                        defense_supply += bot.calculate_supply_cost(unit.type_id)
                        if defense_supply >= defense_goal:
                            break
                if defenders:
                    split_defense = {
                        "target": list(threat.position),
                        "members": [unit.tag for unit in defenders],
                        "supply": defense_supply,
                        "enemy_supply": enemy_supply,
                    }
                    strategy = "push"
                    reason = "Keep the main wave advancing; detach a local defense squad"
                    decision.update(strategy=strategy, reason=reason)
        self.previous = strategy
        home = bases.closest_to(bot.start_location).position if bases else bot.start_location
        front = bases.closest_to(bot.game_info.map_center).position if bases else home
        retreat_target = threatened_base.position if threatened_base is not None else home
        target = (
            retreat_target
            if strategy == "retreat"
            else front.towards(bot.game_info.map_center, policy["rally_distance"])
        )
        if strategy == "defend" and threats:
            target = threats.closest_to(threatened_base or front).position
        elif strategy == "defend" and self.last_incoming_position:
            target = Point2(tuple(self.last_incoming_position))
        elif strategy == "push":
            buildings = bot.enemy_structures.filter(lambda unit: unit.is_visible)
            for building in buildings:
                self.enemy_buildings[building.tag] = building.position
            for tag, position in list(self.enemy_buildings.items()):
                if bot.is_visible(position) and not any(b.distance_to(position) < 3 for b in buildings):
                    del self.enemy_buildings[tag]
            sweep_minimum = {
                "MediumHard": 40,
                "Hard": 64,
                "Harder": 72,
                "VeryHard": 96,
                "CheatVision": 96,
                "CheatMoney": 96,
                "CheatInsane": 112,
            }.get(getattr(bot, "opponent_difficulty", "Medium"), 48)
            if self.endgame_sweep.active and bot.supply_army < sweep_minimum:
                self.endgame_sweep.active = False
                self.endgame_sweep.assignments.clear()
            if (
                not self.endgame_sweep.active
                and bot.settings.strategy == "auto"
                and not bot.settings.strategy_script
                and bot.time >= 900
                and bot.supply_army >= sweep_minimum
                and len(buildings) <= 4
            ):
                self.endgame_sweep.start()
                self.waves.reset()
            if buildings:
                base_target = exposed_base_target(bot, buildings, army)
                if base_target is not None:
                    target = base_target.position
                    decision["resource_denial_target"] = {
                        "unit_type": base_target.type_id.name,
                        "position": list(base_target.position),
                        "priority": "most_exposed_visible_base",
                    }
                else:
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
        destinations = {}
        if bot.settings.army_waves and strategy == "push":
            if self.endgame_sweep.active and not bot.settings.strategy_script:
                destinations, sweep = self.endgame_sweep.plan(bot, army, bot.enemy_structures, threats, bases)
                decision["endgame_sweep"] = sweep
                decision["wave"] = {"phase": "endgame_sweep", "reason": "Search in parallel groups"}
                if any(group["phase"] == "respond_to_base_raid" for group in sweep["groups"]):
                    decision["defense_response"] = {"mode": "endgame_squad", "group": 2}
            else:
                rally = front.towards(bot.game_info.map_center, max(10, policy["rally_distance"]))
                destinations, wave = self.waves.plan(bot, army, target, rally, policy)
                decision["wave"] = wave
                if split_defense is not None:
                    for tag in split_defense["members"]:
                        destinations[tag] = ("attack", Point2(tuple(split_defense["target"])))
                    decision["defense_response"] = {
                        "mode": "split",
                        **split_defense,
                    }
                if wave["phase"] not in {"advance", "engage"}:
                    self.active_mode = "assemble"
        elif strategy in {"retreat", "regroup"}:
            self.waves.reset()
        for unit in army:
            if not bot.available(unit):
                continue
            move = strategy in {"retreat", "regroup"} or not unit.can_attack
            destination = target
            if unit.tag in destinations:
                mode, destination = destinations[unit.tag]
                move = mode == "move"
            maximum = unit.health_max + unit.shield_max
            if maximum and (unit.health + unit.shield) / maximum < 0.25:
                move, destination = True, home
            if move and unit.distance_to(destination) < 2:
                continue
            # Don't replace a matching standing order every polling interval.
            if unit.orders:
                order = unit.orders[0]
                if isinstance(order.target, Point2) and order.target.distance_to(destination) < 2:
                    continue
            command = unit.move(destination) if move else unit.attack(destination)
            if bot.issue(command):
                decision["orders"].append(
                    {
                        "unit_tag": unit.tag,
                        "action": "move" if move else "attack",
                        "target": list(destination),
                    }
                )
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
