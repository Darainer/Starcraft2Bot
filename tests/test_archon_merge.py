import asyncio
from types import SimpleNamespace

import pytest
from sc2.action import combine_actions
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G

from source.composition import archon_committed, production_target
from source.counter_composition import SUPPLY, propose_counter_plan
from source.tactics import TacticalController


def setup(bot, make_unit, populate, count=2, keep=0):
    bot.control.command("!assist economy off")
    bot.settings.attack = bot.settings.archon_merge = True
    bot.settings.archons = 2
    bot.settings.high_templar = keep
    bot.state.game_loop = 6720
    templars = [make_unit(U.HIGHTEMPLAR, (i, 0), energy=i * 20) for i in range(count)]
    populate(make_unit(U.NEXUS), *templars)
    bot.get_available_abilities.return_value = [[A.MORPH_ARCHON], [A.MORPH_ARCHON]]
    return templars


def test_exactly_two_tags_serialize_without_extra_resource_or_supply_charge(bot, make_unit, populate):
    templars = setup(bot, make_unit, populate, count=4)
    bot.minerals = bot.vespene = 0
    before = bot.minerals, bot.vespene, bot.supply_left
    result = asyncio.run(bot.archon_controller.tick(bot))
    wire = list(combine_actions(bot.actions))
    assert len(wire) == 1 and wire[0].unit_command.ability_id == A.MORPH_ARCHON.value
    assert set(wire[0].unit_command.unit_tags) == {templars[0].tag, templars[1].tag}
    assert wire[0].unit_command.WhichOneof("target") is None
    assert (bot.minerals, bot.vespene, bot.supply_left) == before
    assert result["events"][0]["result"] == "merge_queued_not_confirmed"
    asyncio.run(bot.archon_controller.tick(bot))
    assert len(bot.actions) == 2  # Never another pair in this observation.
    assert all(not bot.available(unit) for unit in templars[:2])
    bot._used.clear()
    assert all(not bot.available(unit) for unit in templars[:2])


@pytest.mark.parametrize(
    "blocked",
    [
        "enabled",
        "attack",
        "archon_merge",
        "manual",
        "script",
        "selected",
        "released",
        "used",
        "threat",
        "hallucination",
        "legal",
        "separated",
        "goal_met",
    ],
)
def test_pair_admission_requires_permission_ownership_legality_and_safe_position(
    bot, make_unit, populate, blocked
):
    templars = setup(bot, make_unit, populate)
    if blocked in {"enabled", "attack", "archon_merge"}:
        setattr(bot.settings, blocked, False)
    elif blocked == "manual":
        bot.settings.strategy = "push"
    elif blocked == "script":
        bot.settings.strategy_script = "custom.py"
    elif blocked == "selected":
        templars[0]._proto.is_selected = True
    elif blocked == "released":
        bot.control.released.add(templars[0].tag)
    elif blocked == "used":
        bot._used.add(templars[0].tag)
    elif blocked == "threat":
        populate(*bot.all_own_units, make_unit(U.MARINE, (3, 0), alliance=4))
    elif blocked == "hallucination":
        templars[0]._proto.is_hallucination = True
    elif blocked == "legal":
        bot.game_data.abilities[A.MORPH_ARCHON.value]._proto.available = False
    elif blocked == "separated":
        templars[1]._proto.pos.x = 40
    else:
        bot.settings.archons = 0
    asyncio.run(bot.archon_controller.tick(bot))
    assert not bot.actions


def test_high_energy_storm_caster_reserve_survives_merge_before_other_controllers(bot, make_unit, populate):
    templars = setup(bot, make_unit, populate, count=4, keep=2)
    bot.settings.storm = True
    asyncio.run(bot.on_step(0))
    assert {action.unit.tag for action in bot.actions if action.ability == A.MORPH_ARCHON} == {
        unit.tag for unit in templars[:2]
    }
    controller = TacticalController()
    controller.tick(bot)
    assert controller.last_assessment.army_count == 2
    bot._used.clear()
    bot.state.game_loop += 8
    controller.tick(bot)
    assert not any(
        action.unit.tag in bot._archon_reserved_tags and action.ability != A.MORPH_ARCHON
        for action in bot.actions
    )


def test_per_unit_ability_omission_does_not_block_verified_group_command(bot, make_unit, populate):
    setup(bot, make_unit, populate)
    bot.get_available_abilities.return_value = [[], []]
    result = asyncio.run(bot.archon_controller.tick(bot))
    assert result["pending_pairs"]
    wire = list(combine_actions(bot.actions))
    assert len(wire) == 1 and len(wire[0].unit_command.unit_tags) == 2
    assert wire[0].unit_command.ability_id == A.MORPH_ARCHON.value


@pytest.mark.parametrize("ended", ["error", "death", "release", "timeout", "transformed"])
def test_merge_reservation_cleanup_and_failure_retry_bound(bot, make_unit, populate, ended):
    templars = setup(bot, make_unit, populate)
    asyncio.run(bot.archon_controller.tick(bot))
    bot._used.clear()
    bot.actions.clear()
    bot.state.game_loop += 8
    if ended == "error":
        bot.state.action_errors = [SimpleNamespace(unit_tag=templars[0].tag, ability_id=A.MORPH_ARCHON.value)]
    elif ended == "death":
        populate(bot.townhalls.first, templars[1])
    elif ended == "release":
        bot.control.released.add(templars[0].tag)
    elif ended == "timeout":
        bot.state.game_loop += 448
    else:
        populate(bot.townhalls.first, make_unit(U.ARCHON))
    result = asyncio.run(bot.archon_controller.tick(bot))
    assert not result["pending_pairs"] and not bot._archon_reserved_tags and not bot.actions
    if ended == "transformed":
        assert archon_committed(bot) == 1


def test_templar_feedstock_target_replaces_final_archon_supply_without_double_counting(
    bot, make_unit, populate
):
    templars = setup(bot, make_unit, populate, count=4, keep=2)
    assert production_target(bot, "high_templar") == 6  # 2 casters + 4 merge inputs.
    asyncio.run(bot.archon_controller.tick(bot))
    assert production_target(bot, "high_templar") == 6  # 2 in-flight sources still occupy the count.
    populate(bot.townhalls.first, *templars[2:], make_unit(U.ARCHON, build_progress=0.5))
    bot.state.game_loop += 8
    asyncio.run(bot.archon_controller.tick(bot))
    assert production_target(bot, "high_templar") == 4  # 2 casters + 2 inputs for missing second Archon.
    bot.settings.archon_merge = False
    assert production_target(bot, "high_templar") == 2


def test_archon_counter_plan_has_air_splash_without_storm_and_budgeted_inputs():
    contacts = [dict(tag=str(i), kind="MUTALISK", seen_seconds=900, supply=2, air=True) for i in range(12)]
    p = propose_counter_plan(
        900,
        "Zerg",
        contacts,
        max_workers=70,
        workers=60,
        bases=3,
        own_army=60,
        support_targets={},
        archon_merge=True,
    )
    targets = dict(p.targets)
    assert targets["archons"] >= 2 and targets["high_templar"] == 0
    assert targets["colossi"] == 0 and "short range" in p.splash_constraint
    assert dict(p.morph_inputs)["high_templar"] == 2 * targets["archons"]
    assert p.allocated_supply == sum(SUPPLY[k] * v for k, v in targets.items()) <= 130
    assert "TEMPLARARCHIVE" in p.tech_goals and "archons" in p.priority


def test_archon_micro_prefers_reachable_cluster_over_isolated_low_health_target(bot, make_unit, populate):
    archon = make_unit(U.ARCHON, health=10, health_max=10, shield=350, shield_max=350)
    isolated = make_unit(U.MARINE, (2, -2), alliance=4, health=5, shield=0)
    cluster = [make_unit(U.MARINE, (2, i * 0.2), alliance=4) for i in range(4)]
    populate(archon, isolated, *cluster)
    bot.settings.attack = True
    controller = TacticalController()
    controller._micro_allowed = True
    controller.active_mode = "push"
    assert controller.micro(bot)
    assert bot.actions[0].target in cluster


def test_archon_force_prioritizes_shields_before_ground_armor(bot, make_unit, populate):
    setup(bot, make_unit, populate, count=0)
    bot.settings.composition_policy = "scouted"
    bot.enemy_race = Race.Zerg
    bot.supply_workers, bot.supply_army = 40, 40
    bot.scout_report = {
        "enemy_unit_evidence": [
            dict(tag=str(i), kind="ZERGLING", supply=0.5, seen_seconds=300) for i in range(16)
        ]
    }
    populate(bot.townhalls.first, make_unit(U.FORGE), *(make_unit(U.ARCHON) for _ in range(5)))
    bot.already_pending_upgrade.side_effect = lambda upgrade: int(upgrade == G.PROTOSSGROUNDWEAPONSLEVEL1)
    shields = bot.game_data.upgrades[G.PROTOSSSHIELDSLEVEL1.value].research_ability.id
    armor = bot.game_data.upgrades[G.PROTOSSGROUNDARMORSLEVEL1.value].research_ability.id
    bot.get_available_abilities.return_value = [shields, armor]
    assert asyncio.run(bot.upgrade(0))
    assert bot.actions[0].ability == shields


def test_reserved_inputs_rendezvous_then_merge_without_army_reassignment(bot, make_unit, populate):
    templars = setup(bot, make_unit, populate)
    templars[1]._proto.pos.x = 20
    result = asyncio.run(bot.archon_controller.tick(bot))
    assert len(result["rendezvous"]) == 1 and not result["pending_pairs"]
    assert all(action.ability == A.MOVE_MOVE for action in bot.actions)
    assert {unit.tag for unit in templars} == bot._archon_reserved_tags
    assert archon_committed(bot) == 1
    bot._used.clear()
    bot.actions.clear()
    bot.state.game_loop += 224
    for unit in templars:
        unit._proto.pos.x = 6
    templars = [type(unit)(unit._proto, bot, base_build=90000) for unit in templars]
    populate(bot.townhalls.first, *templars)
    result = asyncio.run(bot.archon_controller.tick(bot))
    assert not result["rendezvous"] and len(result["pending_pairs"]) == 1
    assert result["pending_pairs"][0]["until"] == bot.time + 15
    assert list(combine_actions(bot.actions))[0].unit_command.ability_id == A.MORPH_ARCHON.value
    assert any(event["result"] == "rendezvous_reserved" for event in result["history"])


@pytest.mark.parametrize("cancel", ["threat", "release", "deadline", "goal"])
def test_rendezvous_revokes_unsafe_or_withdrawn_orders(bot, make_unit, populate, cancel):
    templars = setup(bot, make_unit, populate)
    templars[1]._proto.pos.x = 20
    asyncio.run(bot.archon_controller.tick(bot))
    bot._used.clear()
    bot.actions.clear()
    bot.state.game_loop += 448 if cancel == "deadline" else 8
    if cancel == "threat":
        populate(*bot.all_own_units, make_unit(U.MARINE, (6, 0), alliance=4))
    elif cancel == "release":
        bot.control.released.add(templars[0].tag)
    elif cancel == "goal":
        bot.settings.archons = 0
    result = asyncio.run(bot.archon_controller.tick(bot))
    assert not result["rendezvous"] and not bot._archon_reserved_tags and not bot.actions


def test_rendezvous_rejects_unreachable_ground_routes(bot, make_unit, populate):
    from unittest.mock import AsyncMock

    templars = setup(bot, make_unit, populate)
    templars[1]._proto.pos.x = 20
    bot.client.query_pathing = AsyncMock(return_value=0)
    result = asyncio.run(bot.archon_controller.tick(bot))
    assert not result["rendezvous"] and not bot.actions and not bot._archon_reserved_tags


def test_scouted_archon_goal_trains_paid_templar_inputs_and_honors_reserves(bot, make_unit, populate):
    setup(bot, make_unit, populate, count=0)
    bot.settings.production = True
    bot.settings.scouting = False
    bot.settings.composition_policy = "scouted"
    bot.enemy_race = Race.Zerg
    bot.supply_workers, bot.supply_army = 30, 24
    bot.scout_report = {
        "enemy_unit_evidence": [
            dict(tag=str(i), kind="MUTALISK", supply=2, air=True, seen_seconds=300) for i in range(12)
        ]
    }
    populate(
        bot.townhalls.first,
        make_unit(U.GATEWAY),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.TEMPLARARCHIVE),
        *(make_unit(U.STALKER) for _ in range(6)),
    )
    bot.settings.reserve_minerals = bot.settings.reserve_gas = 100
    bot.minerals, bot.vespene = 150, 250
    assert bot.produce(0)
    assert bot.actions[0].ability == A.GATEWAYTRAIN_HIGHTEMPLAR
    assert (bot.minerals, bot.vespene) == (100, 100)


@pytest.mark.parametrize("kind", [U.TWILIGHTCOUNCIL, U.TEMPLARARCHIVE])
def test_archon_tech_chain_receives_bounded_investment(bot, make_unit, populate, kind):
    setup(bot, make_unit, populate, count=0)
    bot.settings.production = bot.settings.construction = True
    bot.settings.composition_policy = "scouted"
    bot.enemy_race = Race.Zerg
    bot.supply_workers, bot.supply_army = 30, 24
    bot.scout_report = {
        "enemy_unit_evidence": [
            dict(tag=str(i), kind="MUTALISK", supply=2, air=True, seen_seconds=300) for i in range(12)
        ]
    }
    populate(
        bot.townhalls.first,
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.PYLON, (10, 0)),
        make_unit(U.PROBE, (8, 0)),
        *([make_unit(U.TWILIGHTCOUNCIL)] if kind == U.TEMPLARARCHIVE else []),
    )
    assert asyncio.run(bot.fund_first_robotics(bot.townhalls.first, 24, kind))
    assert (
        len(bot.actions) == 1
        and bot.actions[0].ability == bot.game_data.units[kind.value].creation_ability.id
    )
