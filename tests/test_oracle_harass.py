import asyncio

import pytest
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.buff_id import BuffId as B
from sc2.ids.unit_typeid import UnitTypeId as U

from source.economy_assistant import ARMY_TARGETS
from source.oracle_harass import OracleHarass


def setup(bot, make_unit, populate, **kwargs):
    bot.settings.attack = bot.settings.oracle_harass = bot.settings.oracle_beam = True
    bot.state.game_loop = 6720
    oracle = make_unit(U.ORACLE, (40, 40), is_flying=True, energy=80, **kwargs)
    worker = make_unit(U.SCV, (43, 40), alliance=4)
    populate(make_unit(U.NEXUS), oracle, worker)
    bot.get_available_abilities.return_value = [A.BEHAVIOR_PULSARBEAMON, A.BEHAVIOR_PULSARBEAMOFF]
    return oracle, worker


def test_beam_activation_and_worker_attack_use_separate_observations(bot, make_unit, populate):
    oracle, worker = setup(bot, make_unit, populate)
    controller = OracleHarass()
    asyncio.run(controller.tick(bot))
    assert [a.ability for a in bot.actions] == [A.BEHAVIOR_PULSARBEAMON]
    assert U.ORACLE not in ARMY_TARGETS
    bot.actions.clear()
    bot._used.clear()
    bot.state.game_loop += 8
    # A fresh Unit is how real observations replace cached properties.
    oracle._proto.buff_ids.append(B.ORACLEWEAPON.value)
    observed_oracle = type(oracle)(oracle._proto, bot, base_build=90000)
    populate(bot.townhalls.first, observed_oracle, worker)
    asyncio.run(controller.tick(bot))
    assert [a.ability for a in bot.actions] == [A.ATTACK]
    assert bot.actions[0].target == worker


@pytest.mark.parametrize(
    "blocked",
    ["enabled", "attack", "oracle_harass", "oracle_beam", "manual", "selected", "released", "used", "script"],
)
def test_ownership_and_individual_permissions_stop_oracle_orders(bot, make_unit, populate, blocked):
    oracle, _ = setup(bot, make_unit, populate)
    if blocked == "manual":
        bot.settings.strategy = "defend"
    elif blocked == "script":
        bot.settings.strategy_script = "custom.py"
    elif blocked == "selected":
        oracle._proto.is_selected = True
    elif blocked == "released":
        bot.control.released.add(oracle.tag)
    elif blocked == "used":
        bot._used.add(oracle.tag)
    else:
        setattr(bot.settings, blocked, False)
    asyncio.run(OracleHarass().tick(bot))
    assert not bot.actions
    bot.get_available_abilities.assert_not_awaited()


@pytest.mark.parametrize("reason", ["anti_air", "low_shields", "empty", "lock_on", "emergency"])
def test_unsafe_raid_turns_off_beam_then_returns_home(bot, make_unit, populate, reason):
    oracle, worker = setup(bot, make_unit, populate, buff_ids=[B.ORACLEWEAPON.value])
    if reason == "anti_air":
        populate(*bot.all_own_units, worker, make_unit(U.MARINE, (44, 40), alliance=4))
    elif reason == "low_shields":
        oracle._proto.shield = 10
    elif reason == "empty":
        populate(*bot.all_own_units)
    elif reason == "lock_on":
        oracle._proto.buff_ids.append(B.LOCKON.value)
    else:
        bot.economic_emergency = True
    controller = OracleHarass()
    result = asyncio.run(controller.tick(bot))
    assert result["raids"][str(oracle.tag)]["phase"] == "recover"
    assert [a.ability for a in bot.actions] == [A.BEHAVIOR_PULSARBEAMOFF]
    bot.actions.clear()
    bot._used.clear()
    bot.state.game_loop += 8
    result = asyncio.run(controller.tick(bot))
    assert [a.ability for a in bot.actions] == [A.MOVE_MOVE]
    assert result["orders"][0]["action"] == "return_and_recharge"


def test_no_legal_beam_toggle_does_not_issue_one_or_attack_worker(bot, make_unit, populate):
    setup(bot, make_unit, populate)
    bot.get_available_abilities.return_value = []
    asyncio.run(OracleHarass().tick(bot))
    assert all(a.ability == A.MOVE_MOVE for a in bot.actions)
