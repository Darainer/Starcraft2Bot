import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G
from sc2.position import Point2

from source.layout import find_spaced_placement, layout_clear, preserves_local_paths, segment_distance


def test_layout_keeps_mining_routes_and_building_aisles(bot, make_unit, populate):
    populate(
        make_unit(U.NEXUS),
        make_unit(U.PROBE),
        make_unit(U.MINERALFIELD, (-8, 0), alliance=3, mineral_contents=1000),
    )
    assert not layout_clear(bot, U.PYLON, Point2((-5, 0)))
    assert not layout_clear(bot, U.PYLON, Point2((7, 7)))  # Main exit lane.
    assert layout_clear(bot, U.PYLON, Point2((-6, 6)))
    assert segment_distance(Point2((3, 4)), Point2((0, 0)), Point2((0, 0))) == 5


def test_production_exit_and_narrow_gap_rejected(bot, make_unit, populate):
    populate(make_unit(U.GATEWAY, (10, 10)))
    assert not layout_clear(bot, U.PYLON, Point2((14, 14)))
    assert not layout_clear(bot, U.PYLON, Point2((13, 10)))
    assert layout_clear(bot, U.PYLON, Point2((4, 10)))


def test_local_path_check_rejects_sealing_a_corridor(make_unit):
    class Corridor:
        width = height = 40

        def __getitem__(self, point):
            return 7 <= point.y <= 10

    soldier = make_unit(U.STALKER, (9, 8))

    # Two blockers close the west edge, making the right exit the only path.
    class DeadEnd(Corridor):
        def __getitem__(self, point):
            return super().__getitem__(point) and point.x >= 6

    assert not preserves_local_paths(DeadEnd(), Point2((15, 9)), 1.5, [soldier])
    assert preserves_local_paths(Corridor(), Point2((15, 9)), 1.5, [soldier])
    assert preserves_local_paths(None, Point2((15, 9)), 1.5, [soldier])
    assert preserves_local_paths(DeadEnd(), Point2((15, 9)), 1.5, [])


def test_powered_gateway_candidates_include_six_tile_ring(bot, make_unit, populate):
    populate(make_unit(U.PYLON))
    bot.find_placement = AsyncMock(side_effect=lambda kind, near, **kw: near if near.length <= 6.5 else None)
    result = asyncio.run(find_spaced_placement(bot, U.GATEWAY, Point2((0, 0)), 12))
    assert result is not None and 4.5 <= result.length <= 6.5
    assert result.x % 1 == result.y % 1 == 0.5
    assert layout_clear(bot, U.GATEWAY, result)


def test_upgrade_preempts_additional_construction_when_overdue(bot, make_unit, populate):
    populate(make_unit(U.NEXUS), make_unit(U.FORGE))
    bot.control.command("!assist economy off")
    bot.settings.upgrades = bot.settings.construction = True
    ability = bot.game_data.upgrades[G.PROTOSSGROUNDWEAPONSLEVEL1.value].research_ability.id
    bot.get_available_abilities = AsyncMock(return_value=[ability])
    bot.construct = AsyncMock(return_value=True)
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == ability
    bot.construct.assert_not_awaited()


def test_producer_placement_failure_has_retry_cooldown(bot, make_unit, populate):
    producer = make_unit(U.GATEWAY)
    populate(producer)
    bot.state.action_errors = [SimpleNamespace(unit_tag=producer.tag, ability_id=1, result=41)]
    bot.settings.enabled = False
    asyncio.run(bot.on_step(0))
    assert not bot.produce(0)
    bot.state.game_loop += 22.4 * 16
    assert bot.produce(0)


def test_upgrade_can_reach_level_three_and_air_research(bot, make_unit, populate):
    populate(make_unit(U.FORGE), make_unit(U.CYBERNETICSCORE))
    ability = bot.game_data.upgrades[G.PROTOSSGROUNDWEAPONSLEVEL3.value].research_ability.id
    bot.get_available_abilities = AsyncMock(return_value=[ability])
    assert asyncio.run(bot.upgrade(0))
    assert bot.actions[0].ability == ability
    bot.actions.clear()
    bot._used.clear()
    bot.settings.voidrays = 10
    ability = bot.game_data.upgrades[G.PROTOSSAIRWEAPONSLEVEL1.value].research_ability.id
    bot.get_available_abilities = AsyncMock(return_value=[ability])
    assert asyncio.run(bot.upgrade(0))
    assert bot.actions[0].ability == ability


def test_research_compares_exact_query_id_with_generic_game_data(bot, make_unit, populate):
    from sc2.ids.ability_id import AbilityId as A

    populate(make_unit(U.FORGE))
    exact = A.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1
    generic = A.RESEARCH_PROTOSSGROUNDWEAPONS
    bot.game_data.abilities[exact.value]._proto.remaps_to_ability_id = generic.value
    bot.get_available_abilities = AsyncMock(return_value=[exact])
    assert asyncio.run(bot.upgrade(0))
    assert bot.actions[0].ability == exact


def test_supply_tries_another_base_when_main_layout_is_full(bot, make_unit, populate):
    populate(make_unit(U.NEXUS), make_unit(U.NEXUS, (30, 0)), make_unit(U.PROBE))
    bot.supply_left = 1
    bot.build_structure = AsyncMock(side_effect=[False, True])
    asyncio.run(bot.macro())
    assert bot.build_structure.await_count == 2
