from dataclasses import replace
from types import SimpleNamespace

import pytest
from s2clientprotocol import data_pb2, raw_pb2
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G

from source.action_intents import ActionExecutor, ActionIntent
from source.army_waves import ArmyWaves
from source.combat_assessment import favorable, home_threats, power, visible_threats
from source.composition import composition_targets, production_target
from source.game_assessment import GameAssessment
from source.missions import MissionPlanner
from source.strategic_plan import MissionSpec
from source.strategy_director import StrategicDirector
from source.tactics import TacticalController


def weapon(bot, kind, domain=3, distance=5, damage=6):
    proto = bot.game_data.units[kind.value]._proto
    del proto.weapons[:]
    if damage:
        proto.weapons.append(data_pb2.Weapon(type=domain, damage=damage, attacks=1, range=distance, speed=1))


def setup_army(bot, make_unit, populate, count=30, position=(10, 10)):
    weapon(bot, U.NEXUS, damage=0)
    army = [make_unit(U.STALKER, position) for _ in range(count)]
    targets = [make_unit(U.NEXUS, (80, 80), alliance=4), make_unit(U.NEXUS, (60, 60), alliance=4)]
    populate(make_unit(U.NEXUS), *army, *targets)
    bot.settings.attack = True
    bot.settings.scouting = False
    bot.settings.profile = "pressure"
    bot.supply_army = count * 2
    bot.scout_report = {"enemy_seen": True}
    return army, targets


def test_fight_power_respects_domains_static_defense_and_workers(bot, make_unit, populate):
    weapon(bot, U.ZEALOT, domain=1)
    weapon(bot, U.BUNKER, damage=0)
    weapon(bot, U.STALKER, domain=2)
    zealot = make_unit(U.ZEALOT)
    flying = make_unit(U.MUTALISK, is_flying=True, alliance=4)
    colossus = make_unit(U.COLOSSUS)
    stalker = make_unit(U.STALKER)
    bunker = make_unit(U.BUNKER, (10, 10), alliance=4)
    worker = make_unit(U.PROBE, alliance=4)
    assert power([zealot], [flying]) == 0
    assert power([stalker], [colossus]) > 0
    assert not favorable([zealot], [flying])
    assert favorable([zealot], [])
    assert power([worker], [zealot]) == 0
    assert power([bunker], [zealot]) > 0
    populate(make_unit(U.NEXUS), bunker, worker, flying)
    assert bunker in visible_threats(bot) and worker not in visible_threats(bot)
    assert bunker in home_threats(bot, visible_threats(bot))
    assert not bot.safe_at(bunker.position)


def test_assessment_memory_expiry_and_local_support(bot, make_unit, populate):
    army, _ = setup_army(bot, make_unit, populate)
    local = army[:10]
    distant = [make_unit(U.STALKER, (100, 0)) for _ in range(20)]
    enemy = [make_unit(U.MARINE, (11, 11), alliance=4) for _ in range(15)]
    populate(make_unit(U.NEXUS), *local, *distant, *enemy)
    bot.scout_report["known_enemy_bases"] = [{"position": [80, 80], "seen_seconds": bot.time}]
    bot.is_visible = lambda point: False
    tracker = GameAssessment()
    state = tracker.observe(bot, bot.units)
    assert 0 < state.local_advantage < 1
    assert state.threat_supply > 0
    assert any(t.id.startswith("memory:") and not t.visible for t in state.targets)
    bot.state.game_loop += 22_400
    state = tracker.observe(bot, bot.units)
    assert not any(t.id.startswith("memory:") for t in state.targets)
    # A tiny detached fight must not force a global retreat.
    populate(make_unit(U.NEXUS), *local[:2], *distant, *enemy)
    assert tracker.observe(bot, bot.units).local_advantage == 10


def test_recent_trades_and_visibility_are_required_for_cleanup(bot, make_unit, populate):
    army, targets = setup_army(bot, make_unit, populate)
    tracker = GameAssessment()
    bot.state.score = SimpleNamespace(lost_minerals_army=0, killed_minerals_army=0)
    threat = make_unit(U.MARINE, (8, 8), alliance=4)
    populate(make_unit(U.NEXUS), *army, *targets, threat)
    tracker.observe(bot, bot.units)
    bot.state.game_loop += 224
    populate(make_unit(U.NEXUS), *army, *targets)
    assert not tracker.observe(bot, bot.units).recently_defended
    bot.state.score.killed_minerals_army = 1000
    bot.scout_report.update(last_seen_seconds=bot.time, composition_intel={"supply": 0})
    bot.state.upgrades.add(G.PROTOSSGROUNDWEAPONSLEVEL1)
    state = tracker.observe(bot, bot.units)
    assert state.recently_defended and state.cleanup_ready and state.timing_ready
    bot.state.score.lost_minerals_army = 2000
    assert tracker.observe(bot, bot.units).trade_bad
    bot.state.game_loop += 22_400
    assert not tracker.observe(bot, bot.units).cleanup_ready


@pytest.mark.parametrize(
    "intel,expected",
    [
        (
            {"air_supply": 20, "supply": 20, "armored_air_supply": 20},
            {"stalkers": 44, "colossi": 0, "voidrays": 6},
        ),
        ({"air_supply": 10, "supply": 30}, {"stalkers": 40}),
        ({"armored_ground_supply": 40}, {"immortals": 10}),
        ({"light_ground_count": 20}, {"colossi": 3, "zealots": 12}),
    ],
)
def test_composition_overlay_is_bounded_and_reversible(bot, intel, expected):
    bot.settings.attack = True
    bot.scout_report = {"composition_intel": {**intel, "seen_seconds": bot.time}}
    original = bot.settings.stalkers
    targets = composition_targets(bot)
    for key, value in expected.items():
        assert targets[key] == value
    assert bot.settings.stalkers == original
    bot.state.game_loop += 22400
    assert composition_targets(bot)["stalkers"] == original
    bot.settings.adaptive_composition = False
    assert production_target(bot, "observers") == bot.settings.observers


def test_action_intent_revoked_on_assignment_or_human_takeover(bot, make_unit, populate):
    unit = make_unit(U.STALKER)
    populate(unit)
    bot.settings.attack = True
    executor = ActionExecutor()
    executor.assign({unit.tag: "main"})
    intent = ActionIntent(unit.tag, executor.assignments[unit.tag][1], 224, 230, "attack", (40, 40))
    executor.assign({unit.tag: "main"})
    assert executor.execute(bot, intent)
    assert not executor.execute(bot, intent)  # One actor, one order this observation.
    bot._used.clear()
    executor.assign({unit.tag: "defense"})
    assert not executor.execute(bot, intent)
    assert executor.outcomes[-1]["result"] == "assignment_revoked"
    intent = replace(intent, revision=executor.assignments[unit.tag][1])
    bot.control.released.add(unit.tag)
    assert not executor.execute(bot, intent)
    assert executor.outcomes[-1]["result"] == "actor_unavailable"
    bot.control.released.clear()
    bot.settings.enabled = False
    assert not executor.execute(bot, intent)
    assert executor.outcomes[-1]["result"] == "automation_disabled"


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"source_loop": 300}, "observation_expired"),
        ({"expires_loop": 200}, "observation_expired"),
        ({"action": "spell"}, "unsupported_action"),
        ({"target": (float("nan"), 0)}, "invalid_target"),
        ({"target": (0,)}, "invalid_target"),
        ({"target": (200, 0)}, "outside_map"),
        ({"action": "move", "target": (0, 0)}, "at_destination"),
    ],
)
def test_intent_rejection_reasons(bot, make_unit, populate, change, reason):
    unit = make_unit(U.STALKER)
    populate(unit)
    bot.settings.attack = True
    bot.game_info.playable_area = SimpleNamespace(x=0, y=0, width=120, height=120)
    executor = ActionExecutor()
    executor.assign({unit.tag: "main"})
    intent = ActionIntent(unit.tag, executor.assignments[unit.tag][1], 224, 230, "attack", (40, 40))
    assert not executor.execute(bot, replace(intent, **change))
    assert executor.outcomes[-1]["result"] == reason


def test_retreat_replaces_attack_move_but_matching_orders_are_preserved(bot, make_unit, populate):
    order = raw_pb2.UnitOrder(ability_id=A.ATTACK.value)
    order.target_world_space_pos.x = order.target_world_space_pos.y = 40
    unit = make_unit(U.STALKER, orders=[order])
    populate(unit)
    bot.settings.attack = True
    executor = ActionExecutor()
    executor.assign({unit.tag: "main"})
    intent = ActionIntent(unit.tag, executor.assignments[unit.tag][1], 224, 230, "attack", (40, 40))
    assert not executor.execute(bot, intent)
    assert executor.outcomes[-1]["result"] == "standing_order"
    assert executor.execute(bot, replace(intent, action="move"))


def test_squads_are_disjoint_persistent_and_release_human_units(bot, make_unit, populate):
    army, targets = setup_army(bot, make_unit, populate)
    controller = TacticalController()
    first = controller.tick(bot)
    missions = first["missions"]
    assert set(missions) == {"denial", "main"}
    assert not set(missions["denial"]["members"]) & set(missions["main"]["members"])
    assert sum(m["supply"] for m in missions.values()) == 60
    bot._used.clear()
    second = controller.tick(bot)
    assert second["missions"]["denial"]["members"] == missions["denial"]["members"]
    released = missions["denial"]["members"][0]
    bot.control.released.add(released)
    bot._used.clear()
    bot.actions.clear()
    third = controller.tick(bot)
    assert all(released not in mission["members"] for mission in third["missions"].values())
    assert all(action.unit.tag != released for action in bot.actions)
    assert production_target(bot, "stalkers") == dict(bot.strategic_plan.production)["stalkers"]
    bot.settings.attack = False
    controller.tick(bot)
    assert not controller.missions.records and bot.strategic_plan is None


def test_denial_aborts_locally_without_recalling_main(bot, make_unit, populate):
    army, targets = setup_army(bot, make_unit, populate)
    state = GameAssessment().observe(bot, bot.units)
    plan = StrategicDirector().decide(state)
    raid = next(m for m in plan.missions if m.role == "deny")
    enemy = [make_unit(U.MARINE, raid.target, alliance=4) for _ in range(20)]
    populate(make_unit(U.NEXUS), *army, *targets, *enemy)
    missions, waves = MissionPlanner(), ArmyWaves()
    report = missions.execute(bot, bot.units, plan, state, waves)
    assert report["missions"]["denial"]["phase"] == "recover"
    assert report["missions"]["main"]["phase"] != "recover"
    assert report["events"][-1]["result"] == "unfavorable_fight"
    populate(make_unit(U.NEXUS), *army, *targets)
    bot._used.clear()
    report = missions.execute(bot, bot.units, plan, state, waves)
    assert report["missions"]["denial"]["phase"] == "recover"


def test_mission_admission_returns_unfillable_budget_to_main(bot, make_unit, populate):
    setup_army(bot, make_unit, populate, count=5)
    state = GameAssessment().observe(bot, bot.units)
    plan = StrategicDirector().decide(state)
    impossible = MissionSpec("denial", "deny", "rally", state.rally, 1, 1, 90)
    plan = replace(plan, missions=(impossible, replace(plan.missions[-1], supply_budget=9)))
    report = MissionPlanner().execute(bot, bot.units, plan, state, ArmyWaves())
    assert set(report["missions"]) == {"main"}
    assert report["missions"]["main"]["supply"] == 10
    assert report["events"][-1]["result"] == "insufficient_force"


@pytest.mark.parametrize("objective", ["develop", "recover", "stabilize", "finish", "contain", "pressure"])
def test_each_mission_lifecycle_executes(bot, make_unit, populate, objective):
    setup_army(bot, make_unit, populate)
    state = GameAssessment().observe(bot, bot.units)
    plan = StrategicDirector().decide(state)
    main = replace(plan.missions[-1], supply_budget=60)
    plan = replace(plan, objective=objective, missions=(main,))
    if objective == "pressure":
        bot.settings.army_waves = False
    report = MissionPlanner().execute(bot, bot.units, plan, state, ArmyWaves())
    assert report["missions"]["main"]["phase"]
    assert report["orders"]


def test_micro_kites_and_resumes_fire_without_extra_spells(bot, make_unit, populate):
    weapon(bot, U.ZERGLING, domain=1, distance=0.1)
    soldier = make_unit(U.STALKER, (20, 20), weapon_cooldown=10)
    enemy = make_unit(U.ZERGLING, (24, 20), alliance=4)
    populate(soldier, enemy)
    bot.settings.attack = True
    controller = TacticalController()
    controller.active_mode = "push"
    assert controller.micro(bot)[0]["action"] == "kite_melee"
    assert bot.actions[0].target.distance_to(enemy.position) > soldier.distance_to(enemy)
    order = raw_pb2.UnitOrder(ability_id=A.MOVE.value)
    moved = make_unit(U.STALKER, (17, 20), weapon_cooldown=2, orders=[order])
    populate(moved, enemy)
    bot._used.clear()
    assert controller.micro(bot)[0]["action"] == "resume_attack"
