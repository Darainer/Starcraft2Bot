"""Observable-state tactical policies; all orders retain human ownership checks."""

from dataclasses import asdict, dataclass, replace
from pathlib import Path

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.army_waves import ArmyWaves
from source.combat_assessment import visible_threats
from source.economy_assistant import ARMY_TARGETS
from source.game_assessment import GameAssessment
from source.missions import MissionPlanner, retreat_geometry, retreat_waypoint
from source.strategic_plan import MissionSpec, Opportunity, StrategicPlan, validate_plan
from source.strategy_director import StrategicDirector
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
        or state.nearby_enemy_strength > state.own_strength * policy["danger_ratio"]
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
        self.waves = ArmyWaves()
        self.assessor = GameAssessment()
        self.director = StrategicDirector()
        self.missions = MissionPlanner()
        self.last_assessment = None
        self._last_script = -999
        self._script_path = None
        self._script_stamp = None
        self._script_plan = None
        self._last_director = -999
        self._signature = None
        self._micro_allowed = True
        self._automatic_recovery = False

    def tick(self, bot, observation=None, available_abilities=None):
        self.active_mode = "manual"
        self._micro_allowed = False
        self._automatic_recovery = False
        if not bot.settings.enabled or not bot.settings.attack:
            self.missions.reset()
            self.waves.reset()
            self._signature = None
            bot.economic_emergency = False
            bot.strategic_plan = None
            return {
                "strategy": "manual",
                "reason": "Attack control disabled or assistant paused",
                "orders": [],
            }
        army = bot.units.of_type(set(ARMY_TARGETS)).ready.filter(bot.control.eligible)
        state = self.assessor.observe(bot, army, self.missions.records.get("main", {}))
        self.last_assessment = state
        legacy = TacticalSituation(
            state.army_supply,
            state.army_count,
            state.health,
            1,
            state.local_advantage,
            bool(state.threat_supply),
            self.previous,
            state.threat_supply,
            state.army_supply,
            state.home_advantage < 0.85,
            state.trade_bad,
        )
        requested = bot.settings.strategy
        script_target = None
        script_metadata = {}
        if bot.settings.strategy_script:
            try:
                info = Path(bot.settings.strategy_script).stat()
                stamp = (info.st_mtime_ns, info.st_size)
                if (
                    self._script_path != bot.settings.strategy_script
                    or stamp != self._script_stamp
                    or bot.time - self._last_script >= 5
                ):
                    self._script_stamp = stamp
                    self._last_script = bot.time
                    self._script_path = bot.settings.strategy_script
                    self._script_plan = None
                    self._script_plan = run_strategy_script(
                        bot.settings.strategy_script,
                        {
                            "schema_version": 1,
                            "situation": asdict(legacy),
                            "profile": PROFILES[bot.settings.profile],
                            "observation": observation,
                            "available_abilities": available_abilities,
                            "previous_strategy": self.previous,
                            "wave": self.waves.last_state,
                            "assessment": state.to_dict(),
                        },
                    )
                if self._script_plan is None:
                    raise ValueError("No valid script plan")
                requested = self._script_plan["strategy"]
                script_target = self._script_plan.get("target")
                script_metadata = self._script_plan
            except Exception as exc:
                self.missions.reset()
                self.waves.reset()
                bot.strategic_plan = None
                bot.economic_emergency = False
                return {
                    "strategy": "manual",
                    "reason": f"Strategy script rejected: {type(exc).__name__}: {exc}",
                    "orders": [],
                }
        if requested == "auto":
            signature = (
                bot.settings.profile,
                bool(state.threat_supply),
                state.rush_warning,
                state.trade_bad,
                state.local_advantage < 0.85,
                state.health < PROFILES[bot.settings.profile]["retreat_health"],
                int(state.army_supply // 4),
                state.production,
                state.response_policy,
                state.playbook_id,
                state.combat_window,
            )
            try:
                validate_plan(self.director.active, state)
                invalid = False
            except ValueError:
                invalid = True
            if invalid or signature != self._signature or bot.time - self._last_director >= 2:
                plan = self.director.decide(state)
                self._last_director, self._signature = bot.time, signature
            else:
                plan = self.director.active
            strategy = {"develop": "regroup", "recover": "retreat", "stabilize": "defend"}.get(
                plan.objective, "push"
            )
        else:
            strategy = requested
            objective = {
                "push": "pressure",
                "defend": "stabilize",
                "retreat": "recover",
                "regroup": "develop",
            }[strategy]
            target_id, point = "rally", state.rally
            if strategy == "retreat":
                target_id, point = "home", state.home
            elif strategy == "defend" and state.threat:
                target_id, point = "threat", state.threat
            elif strategy == "push" and state.targets:
                target = max(state.targets, key=lambda t: t.value - t.travel * 0.1)
                target_id, point = target.id, target.position
            if script_target is not None:
                point = tuple(script_target)
                area = bot.game_info.playable_area
                if not (
                    area.x <= point[0] < area.x + area.width and area.y <= point[1] < area.y + area.height
                ):
                    self.missions.reset()
                    self.waves.reset()
                    bot.strategic_plan = None
                    bot.economic_emergency = False
                    return {
                        "strategy": "manual",
                        "reason": "Script target outside playable map",
                        "orders": [],
                    }
                target_id = "script"
                state = replace(
                    state,
                    targets=state.targets
                    + (Opportunity(target_id, point, bot.time, False, False, 0, 0, 1, 0),),
                )
            spec = MissionSpec(
                "main",
                "main",
                target_id,
                point,
                state.army_supply,
                min(state.army_supply, PROFILES[bot.settings.profile]["attack_supply"]),
                50,
                "move" if strategy in {"regroup", "retreat"} else "attack",
            )
            plan = StrategicPlan(
                state.version,
                state.version,
                bot.time,
                bot.time + 10,
                objective,
                (spec,),
                state.production,
                strategy != "retreat",
                script_metadata.get("reason", "Manually selected strategy"),
            )
        bot.strategic_plan = plan
        bot.economic_emergency = requested == "auto" and (state.threat_supply >= 8 or state.rush_warning)
        self._micro_allowed = requested not in {"retreat", "regroup"}
        self._automatic_recovery = requested == "auto"
        result = self.missions.execute(
            bot,
            army,
            plan,
            state,
            self.waves,
            preserve_combat=self._micro_allowed,
            recovery_micro=self._automatic_recovery,
        )
        for event in result["events"]:
            if event["time"] == bot.time and event["result"] == "unfavorable_fight":
                self.director.report_failure(event["target_id"], bot.time)
        self.previous = self.active_mode = strategy
        main = plan.missions[-1]
        decision = {
            **script_metadata,
            **result,
            "strategy": strategy,
            "reason": plan.reason,
            "profile": bot.settings.profile,
            "situation": asdict(legacy),
            "target": list(main.target),
            "assessment": state.to_dict(),
            "plan": plan.to_dict(),
            "decision_history": list(self.director.history),
            "action_outcomes": list(self.missions.executor.outcomes),
            "counter_composition": (
                asdict(bot.counter_plan)
                if bot.settings.composition_policy == "scouted"
                and bot.settings.adaptive_composition
                and getattr(bot, "counter_plan", None) is not None
                else None
            ),
        }
        if decision["wave"] is None:
            decision["wave"] = {"phase": self.missions.records.get("main", {}).get("phase", "assemble")}
        return decision

    def micro(self, bot):
        """Execute immediate combat without waiting for strategic deliberation."""
        if (
            not bot.settings.enabled
            or not bot.settings.attack
            or not self._micro_allowed
            or bot.settings.strategy in {"retreat", "regroup"}
        ):
            return []
        if self.active_mode not in {"push", "defend", "regroup"} and not (
            self.active_mode == "retreat" and self._automatic_recovery and bot.settings.strategy == "auto"
        ):
            return []
        enemies = (bot.enemy_units | bot.enemy_structures).filter(
            lambda u: u.is_visible and u.can_be_attacked
        )
        contacts = visible_threats(bot)
        geometry = None
        recovering = {
            tag: mission
            for mission in self.missions.records.values()
            if mission["phase"] == "recover"
            for tag in mission["members"]
        }
        decisions, assigned_damage = [], {}
        window = getattr(getattr(bot, "strategic_plan", None), "combat_window", None)
        if window is not None and window.kind == "asset_defense":
            enemies = enemies.filter(lambda enemy: enemy.distance_to(Point2(window.anchor)) <= 16)
        for unit in bot.units.of_type(set(ARMY_TARGETS)).ready:
            if not bot.available(unit) or not unit.can_attack:
                continue
            targets = enemies.filter(lambda enemy, unit=unit: unit.target_in_range(enemy))
            command, reason = None, None
            if unit.health + unit.shield < (unit.health_max + unit.shield_max) * 0.25:
                home = (
                    Point2(recovering[unit.tag]["retreat_goal"])
                    if unit.tag in recovering and "retreat_goal" in recovering[unit.tag]
                    else (Point2(self.last_assessment.home) if self.last_assessment else bot.start_location)
                )
                if geometry is None:
                    geometry = retreat_geometry(contacts)
                waypoint = retreat_waypoint(bot, unit, home, contacts, geometry)
                command, reason = unit.move(waypoint), "individual_retreat"
            elif unit.tag in recovering:
                if bot.settings.strategy != "auto" or not self._automatic_recovery:
                    continue
                if targets and unit.weapon_cooldown == 0:
                    target = min(
                        targets,
                        key=lambda enemy: (
                            not enemy.can_attack,
                            enemy.health + enemy.shield,
                            unit.distance_to(enemy),
                        ),
                    )
                    command, reason = unit.attack(target), "recovery_volley"
                else:
                    goal = Point2(
                        recovering[unit.tag].get(
                            "retreat_goal",
                            self.last_assessment.home if self.last_assessment else bot.start_location,
                        )
                    )
                    if geometry is None:
                        geometry = retreat_geometry(contacts)
                    command = unit.move(retreat_waypoint(bot, unit, goal, contacts, geometry))
                    reason = "recovery_escape"
            elif targets and unit.weapon_cooldown == 0:
                target = min(
                    targets,
                    key=lambda e: (
                        assigned_damage.get(e.tag, 0) >= e.health + e.shield,
                        not e.can_attack,
                        e.health + e.shield,
                        unit.distance_to(e),
                    ),
                )
                damage = unit.calculate_damage_vs_target(target)[0]
                assigned_damage[target.tag] = assigned_damage.get(target.tag, 0) + damage
                if unit.order_target != target.tag:
                    command, reason = unit.attack(target), "focus_fire"
            elif unit.weapon_cooldown > 3:
                threats = contacts.closer_than(8, unit).filter(
                    lambda e, unit=unit: e.can_attack_air if unit.is_flying else e.can_attack_ground
                )
                if threats:
                    threat = threats.closest_to(unit)
                    own_range = unit.air_range if threat.is_flying else unit.ground_range
                    enemy_range = threat.air_range if unit.is_flying else threat.ground_range
                    if (
                        own_range >= 4
                        and enemy_range < own_range
                        and unit.distance_to(threat) < own_range + 1
                    ):
                        point = unit.position.towards(threat.position, -2)
                        if (
                            bot.is_visible(point)
                            and (unit.is_flying or bot.in_pathing_grid(point))
                            and all(point.distance_to(e) >= unit.distance_to(e) for e in threats)
                        ):
                            command, reason = unit.move(point), "kite_melee"
            elif unit.is_moving and unit.weapon_cooldown <= 3:
                nearby = enemies.closer_than(max(unit.ground_range, unit.air_range) + 3, unit).filter(
                    lambda e, unit=unit: unit.can_attack_air if e.is_flying else unit.can_attack_ground
                )
                if nearby:
                    command, reason = unit.attack(nearby.closest_to(unit)), "resume_attack"
            if command is not None and bot.issue(command):
                decisions.append({"unit_tag": unit.tag, "action": reason})
        return decisions
