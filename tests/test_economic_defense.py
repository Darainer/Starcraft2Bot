import json
from dataclasses import replace

import pytest
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.army_waves import ArmyWaves
from source.combat_assessment import visible_threats
from source.economic_defense import EconomicDefense, force_metrics
from source.game_assessment import GameAssessment
from source.missions import MissionPlanner, local_regroup_goal, retreat_geometry
from source.replay_strategy import assessment_from_dict
from source.strategic_plan import active_combat_window, validate_plan
from source.strategy_director import StrategicDirector
from source.tactics import TacticalController


def setup(bot, make_unit, populate, *, own=10, enemy=14, productive=True, health=100, shield=80):
    bot.settings.attack = True
    bot.settings.defend_assets = True
    bot.settings.profile = "pressure"
    bot.state.game_loop = 6720
    bot.supply_workers = 40
    base = make_unit(
        U.NEXUS,
        (30, 0),
        health=1000,
        health_max=1000,
        shield=0,
        shield_max=0,
        assigned_harvesters=16 if productive else 0,
    )
    army = [make_unit(U.STALKER, (24, 0), health=health, shield=shield) for _ in range(own)]
    enemies = [make_unit(U.MARINE, (35, 0), alliance=4) for _ in range(enemy)]
    populate(make_unit(U.NEXUS), base, *army, *enemies)
    return base, army, enemies


def damaged_observation(bot, base, populate, army, enemies, damage=30):
    bot.state.game_loop += 22
    base._proto.health -= damage
    observed = type(base)(base._proto, bot, base_build=90000)
    other_bases = [u for u in bot.townhalls if u.tag != base.tag]
    populate(*other_bases, observed, *army, *enemies)
    return observed


def test_productive_base_under_fire_justifies_bounded_larger_force_defense(bot, make_unit, populate):
    base, army, enemies = setup(bot, make_unit, populate)
    assessor = GameAssessment()
    assert assessor.observe(bot, bot.units).combat_window is None
    damaged_observation(bot, base, populate, army, enemies)
    state = assessor.observe(bot, bot.units)
    assert 0.6 < state.home_advantage < 0.85
    assert state.combat_window.kind == "asset_defense"
    assert "Full enemy potential DPS 84" in state.combat_window.evidence[1]
    assert "no DPS discount" in state.combat_window.evidence[2]
    plan = StrategicDirector().decide(state)
    assert plan.objective == "stabilize" and plan.combat_window == state.combat_window
    assert plan.missions[0].mode == "attack"
    assert plan.missions[0].target_id == "combat_window"
    assert plan.expires_at == state.combat_window.expires_at
    missions = MissionPlanner()
    # An old generic recovery hold must not silently veto the typed opportunity.
    missions.records["main"] = {"phase": "recover", "recover_until": bot.time + 8}
    result = missions.execute(bot, bot.units, plan, state, ArmyWaves())
    assert result["missions"]["main"]["phase"] == "hold"
    assert any(order["action"] == "attack" for order in result["orders"])
    assert assessment_from_dict(json.loads(json.dumps(state.to_dict()))) == state
    with pytest.raises(ValueError, match="combat window"):
        validate_plan(plan, replace(state, time=plan.expires_at))


@pytest.mark.parametrize(
    "blocked",
    ["off", "empty_base", "critical_army", "hopeless", "doomed_asset", "no_damage", "manual", "no_attackers"],
)
def test_economic_value_never_authorizes_every_losing_fight(bot, make_unit, populate, blocked):
    base, army, enemies = setup(
        bot,
        make_unit,
        populate,
        own=4 if blocked == "hopeless" else 10,
        productive=blocked != "empty_base",
        health=20 if blocked == "critical_army" else 100,
        shield=0 if blocked == "critical_army" else 80,
    )
    if blocked == "off":
        bot.settings.defend_assets = False
    if blocked == "manual":
        bot.settings.strategy = "defend"
    defense = EconomicDefense()
    defense.observe(bot, bot.units, visible_threats(bot), {})
    if blocked == "no_attackers":
        enemies = []
    damaged_observation(
        bot,
        base,
        populate,
        army,
        enemies,
        damage=0 if blocked == "no_damage" else 970 if blocked == "doomed_asset" else 30,
    )
    assert defense.observe(bot, bot.units, visible_threats(bot), {}) is None


def test_rapid_own_health_loss_closes_asset_window(bot, make_unit, populate):
    base, army, enemies = setup(bot, make_unit, populate, own=12)
    defense = EconomicDefense()
    defense.observe(bot, bot.units, visible_threats(bot), {})
    base = damaged_observation(bot, base, populate, army, enemies)
    assert defense.observe(bot, bot.units, visible_threats(bot), {})
    for unit in army:
        unit._proto.shield = 60
    army = [type(unit)(unit._proto, bot, base_build=90000) for unit in army]
    damaged_observation(bot, base, populate, army, enemies)
    assert defense.observe(bot, bot.units, visible_threats(bot), {}) is None


def test_tactical_tick_honors_window_and_preserves_selected_and_critical_actors(bot, make_unit, populate):
    base, army, enemies = setup(bot, make_unit, populate, own=12)
    controller = TacticalController()
    controller.tick(bot)
    bot._used.clear()
    bot.actions.clear()
    army[0]._proto.is_selected = True
    army[1]._proto.health, army[1]._proto.shield = 10, 0
    army = [type(unit)(unit._proto, bot, base_build=90000) for unit in army]
    damaged_observation(bot, base, populate, army, enemies)
    result = controller.tick(bot)
    assert result["plan"]["combat_window"]["kind"] == "asset_defense"
    assert all(action.unit.tag != army[0].tag for action in bot.actions)
    assert any(
        action.unit.tag == army[1].tag and action.ability.name == "MOVE_MOVE" for action in bot.actions
    )


def regroup_scene(bot, make_unit, populate):
    base, army, enemies = setup(bot, make_unit, populate)
    bot.settings.defend_assets = False
    bot.settings.local_regroup = True
    return base, army, enemies


def test_short_regroup_prefers_local_safe_step_and_has_finite_hold(bot, make_unit, populate):
    base, army, enemies = regroup_scene(bot, make_unit, populate)
    state = GameAssessment().observe(bot, bot.units)
    plan = StrategicDirector().decide(state)
    assert plan.objective == "recover"
    missions = MissionPlanner()
    result = missions.execute(bot, bot.units, plan, state, ArmyWaves())
    record = result["missions"]["main"]
    regroup = record["local_regroup"]
    assert Point2(regroup["goal"]).distance_to(bot.units.center) <= 14
    assert Point2(regroup["goal"]).distance_to(Point2(state.home)) > 5
    assert record["recover_until"] == bot.time + 3
    bot.state.game_loop += 224
    bot._used.clear()
    # The original hold is not extended indefinitely by each unfavorable tick.
    result = missions.execute(bot, bot.units, plan, state, ArmyWaves())
    assert result["missions"]["main"]["recover_until"] == regroup["since"] + 3
    bot.state.game_loop += 224
    result = missions.execute(bot, bot.units, plan, state, ArmyWaves())
    assert "local_regroup" not in result["missions"]["main"]


@pytest.mark.parametrize("change", ["none", "shields", "reinforce", "position", "enemy", "distant_reinforce"])
def test_regroup_reengagement_requires_local_changed_conditions(bot, make_unit, populate, change):
    base, army, enemies = regroup_scene(bot, make_unit, populate)
    metrics = force_metrics(bot, bot.units, visible_threats(bot), bot.units.center)
    baseline = dict(metrics)
    if change == "shields":
        baseline["health"] -= 0.1
    elif change == "reinforce":
        baseline["supply"] -= 4
    elif change == "enemy":
        baseline["enemy_power"] *= 1.3
    elif change == "distant_reinforce":
        populate(*bot.all_own_units, *enemies, *(make_unit(U.STALKER, (90, 90)) for _ in range(5)))
    record = {
        "phase": "recover",
        "local_regroup": {
            "since": bot.time - 4,
            "anchor": [30, 0] if change == "position" else [24, 0],
            "goal": [24, 0] if change == "position" else [14, 0],
            "metrics": baseline,
        },
    }
    defense = EconomicDefense()
    result = defense.observe(bot, bot.units, visible_threats(bot), record)
    if change in {"none", "distant_reinforce"}:
        assert result is None
    else:
        assert result.kind == "regroup_probe" and active_combat_window(result, bot.time)
        assert result.evidence
        assert defense.observe(bot, bot.units, visible_threats(bot), record) is None


def test_failed_reengagement_probes_have_a_budget(bot, make_unit, populate):
    regroup_scene(bot, make_unit, populate)
    defense = EconomicDefense()
    metrics = force_metrics(bot, bot.units, visible_threats(bot), bot.units.center)
    metrics["supply"] -= 4
    for offset, permitted in ((0, True), (21, True), (42, False)):
        bot.state.game_loop = int((300 + offset) * 22.4)
        record = {
            "phase": "recover",
            "local_regroup": {"since": bot.time - 4, "anchor": [24, 0], "goal": [14, 0], "metrics": metrics},
        }
        result = defense.observe(bot, bot.units, visible_threats(bot), record)
        assert (result is not None) is permitted


def test_no_traversable_short_route_falls_back_without_inventing_one(bot, make_unit, populate):
    _, army, enemies = regroup_scene(bot, make_unit, populate)
    bot.in_pathing_grid = lambda point: False
    assert (
        local_regroup_goal(
            bot,
            bot.units,
            visible_threats(bot),
            bot.units.center,
            bot.start_location,
            retreat_geometry(visible_threats(bot)),
        )
        is None
    )
