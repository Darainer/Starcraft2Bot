from dataclasses import replace
from types import SimpleNamespace

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U

from source.game_assessment import GameAssessment
from source.tactics import TacticalController


def setup(bot, unit):
    bot.settings.attack = True
    bot.settings.strategy = "auto"
    controller = TacticalController()
    controller.active_mode = "retreat"
    controller._micro_allowed = True
    controller._automatic_recovery = True
    controller.last_assessment = SimpleNamespace(home=(-20, 0))
    controller.missions.records = {
        "main": {"phase": "recover", "members": [unit.tag], "retreat_goal": [-20, 0]}
    }
    return controller


def test_automatic_recovery_moves_fires_and_resumes_escape_across_observations(bot, make_unit, populate):
    unit = make_unit(U.STALKER, weapon_cooldown=4)
    enemy = make_unit(U.MARINE, (3, 0), alliance=4)
    populate(unit, enemy)
    controller = setup(bot, unit)
    for cooldown, expected in ((4, "recovery_escape"), (0, "recovery_volley"), (4, "recovery_escape")):
        unit._proto.weapon_cooldown = cooldown
        bot._used.clear()
        bot.actions.clear()
        bot.state.game_loop += 8
        decisions = controller.micro(bot)
        assert decisions == [{"unit_tag": unit.tag, "action": expected}]
        assert len(bot.actions) == 1
        if cooldown:
            assert bot.actions[0].ability == A.MOVE_MOVE
            assert bot.actions[0].target.distance_to(enemy.position) > unit.distance_to(enemy)
        else:
            assert bot.actions[0].target == enemy
        controller.micro(bot)
        assert len(bot.actions) == 1


def test_recovery_never_chases_out_of_range_target_and_critical_actor_escapes(bot, make_unit, populate):
    unit = make_unit(U.STALKER, weapon_cooldown=0)
    enemy = make_unit(U.MARINE, (20, 0), alliance=4)
    populate(unit, enemy)
    controller = setup(bot, unit)
    assert controller.micro(bot)[0]["action"] == "recovery_escape"
    assert bot.actions[0].ability == A.MOVE_MOVE
    bot._used.clear()
    bot.actions.clear()
    unit._proto.health, unit._proto.shield = 10, 0
    enemy._proto.pos.x = 3
    assert controller.micro(bot)[0]["action"] == "individual_retreat"
    assert bot.actions[0].ability == A.MOVE_MOVE


def test_manual_overrides_and_released_ownership_suppress_recovery_fire(bot, make_unit, populate):
    unit = make_unit(U.STALKER)
    populate(unit, make_unit(U.MARINE, (3, 0), alliance=4))
    controller = setup(bot, unit)
    for strategy in ("retreat", "regroup"):
        bot.settings.strategy = strategy
        assert not controller.micro(bot)
        assert not bot.actions
    bot.settings.strategy = "auto"
    controller._micro_allowed = False  # Resolved scripted retreat overrides configured auto.
    assert not controller.micro(bot)
    assert not bot.actions

    controller._micro_allowed = True
    controller._automatic_recovery = False
    assert not controller.micro(bot)
    assert not bot.actions
    controller._automatic_recovery = True
    bot.control.released.add(unit.tag)
    assert not controller.micro(bot)
    assert not bot.actions


def test_strategic_recovery_hands_actor_budget_to_same_observation_micro(bot, make_unit, populate):
    units = [make_unit(U.STALKER) for _ in range(7)]
    enemy = make_unit(U.MARINE, (3, 0), alliance=4)
    populate(*units, make_unit(U.NEXUS, (30, 0)), enemy)
    bot.settings.attack = True
    bot.settings.strategy = "auto"
    state = replace(GameAssessment().observe(bot, bot.units), trade_bad=True, local_advantage=1.2)
    controller = TacticalController()
    controller.assessor.observe = lambda *_: state
    result = controller.tick(bot)
    assert result["missions"]["main"]["phase"] == "recover"
    assert not bot.actions  # Movement does not consume the volley actor budget.
    decisions = controller.micro(bot)
    assert len(decisions) == len(units)
    assert all(d["action"] == "recovery_volley" for d in decisions)
    assert len(bot.actions) == len({a.unit.tag for a in bot.actions}) == len(units)
