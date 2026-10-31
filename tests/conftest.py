"""Synthetic SC2 protocol objects, with real SDK units and command accounting."""

from itertools import count
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from s2clientprotocol import data_pb2, raw_pb2, sc2api_pb2
from sc2.data import Race
from sc2.dicts.unit_research_abilities import RESEARCH_INFO
from sc2.dicts.unit_train_build_abilities import TRAIN_INFO
from sc2.game_data import GameData
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from source.assistant_control import AssistantSettings
from source.economy_assistant import EconomyAssistant

STRUCTURE_TYPES = {
    U.NEXUS,
    U.PYLON,
    U.ASSIMILATOR,
    U.GATEWAY,
    U.WARPGATE,
    U.CYBERNETICSCORE,
    U.ROBOTICSFACILITY,
    U.TWILIGHTCOUNCIL,
    U.TEMPLARARCHIVE,
    U.ROBOTICSBAY,
    U.STARGATE,
    U.FORGE,
    U.BUNKER,
    U.PHOTONCANNON,
    U.SHIELDBATTERY,
}


@pytest.fixture
def bot():
    bot = EconomyAssistant(AssistantSettings(hud=False, allocation=False, chrono=False))
    bot.state = SimpleNamespace(game_loop=224, chat=[], action_errors=[], upgrades=set())
    bot.state.psionic_matrix = SimpleNamespace(covers=lambda point: True)
    bot.game_info = SimpleNamespace(player_start_location=Point2((0, 0)), map_center=Point2((40, 40)))
    bot.game_info.start_locations = [Point2((100, 100))]
    bot._expansion_positions_list = [Point2((30, 0)), Point2((80, 80))]
    bot.player_id = 1
    bot.race = Race.Protoss
    bot._distances_override_functions(0)
    bot.client = SimpleNamespace(debug_text_screen=Mock())
    bot.chat_send = AsyncMock()
    bot.already_pending = Mock(return_value=0)
    bot.already_pending_upgrade = Mock(return_value=0)
    bot.tech_requirement_progress = Mock(return_value=1)
    bot.get_available_abilities = AsyncMock(return_value=[])
    bot.find_placement = AsyncMock(side_effect=lambda kind, near, **kwargs: near)
    bot.can_place = AsyncMock(side_effect=lambda ability, points: [True] * len(points))
    bot.is_visible = lambda point: True
    bot.in_pathing_grid = lambda point: True
    bot.get_next_expansion = AsyncMock(return_value=Point2((30, 0)))
    abilities = [data_pb2.AbilityData(ability_id=a.value, link_name=a.name) for a in A if a.value]
    creation = {}
    for producer in (U.PROBE, U.NEXUS, U.GATEWAY, U.ROBOTICSFACILITY, U.STARGATE):
        creation.update({kind: info["ability"] for kind, info in TRAIN_INFO[producer].items()})
    costs = {
        U.PROBE: (50, 0, 1),
        U.PYLON: (100, 0, 0),
        U.NEXUS: (400, 0, 0),
        U.ASSIMILATOR: (75, 0, 0),
        U.GATEWAY: (150, 0, 0),
        U.CYBERNETICSCORE: (150, 0, 0),
        U.ROBOTICSFACILITY: (150, 100, 0),
        U.ROBOTICSBAY: (150, 150, 0),
        U.STARGATE: (150, 150, 0),
        U.STALKER: (125, 50, 2),
        U.ZEALOT: (100, 0, 2),
        U.HIGHTEMPLAR: (50, 150, 2),
        U.IMMORTAL: (275, 100, 4),
        U.COLOSSUS: (300, 200, 6),
        U.WARPPRISM: (250, 0, 2),
        U.OBSERVER: (25, 75, 1),
    }
    units = []
    kinds = set(creation) | {
        U.MARINE,
        U.GHOST,
        U.MINERALFIELD,
        U.VESPENEGEYSER,
        U.WARPGATE,
        U.BUNKER,
        U.MUTALISK,
        U.SIEGETANK,
        U.SIEGETANKSIEGED,
        U.ZERGLING,
        U.ROACH,
        U.PHOTONCANNON,
    }
    for kind in kinds:
        # Supply-consuming producers are interpreted as morph sources by the
        # SDK. Giving a Robotics Facility the default two supply incorrectly
        # subtracts its cost from every Robotics unit's training price.
        default_supply = 0 if kind in STRUCTURE_TYPES or kind in {U.MINERALFIELD, U.VESPENEGEYSER} else 2
        m, g, supply = costs.get(kind, (100, 100, default_supply))
        units.append(
            data_pb2.UnitTypeData(
                unit_id=kind.value,
                available=True,
                name=kind.name,
                ability_id=creation[kind].value if kind in creation else 0,
                mineral_cost=m,
                vespene_cost=g,
                food_required=supply,
                race=Race.Protoss.value,
                weapons=[data_pb2.Weapon(type=3, damage=6, attacks=1, range=5, speed=1)],
            )
        )
    upgrades = [
        data_pb2.UpgradeData(
            upgrade_id=upgrade.value, ability_id=info["ability"].value, mineral_cost=100, vespene_cost=100
        )
        for kind in (U.FORGE, U.TEMPLARARCHIVE, U.TWILIGHTCOUNCIL, U.CYBERNETICSCORE, U.ROBOTICSBAY)
        for upgrade, info in RESEARCH_INFO[kind].items()
    ]
    bot.game_data = GameData(sc2api_pb2.ResponseData(abilities=abilities, units=units, upgrades=upgrades))
    bot.unit_supplies = {kind: data._proto.food_required for kind, data in bot.game_data.units.items()}
    bot.minerals, bot.vespene, bot.supply_left = 1000, 1000, 20
    return bot


@pytest.fixture
def make_unit(bot):
    tags = count(1)

    def make(kind, position=(0, 0), **kwargs):
        data = dict(
            unit_type=kind.value,
            tag=next(tags),
            alliance=1,
            display_type=1,
            cloak=3,
            build_progress=1,
            health=100,
            health_max=100,
            shield=80,
            shield_max=80,
            radius=0.5,
            is_powered=True,
        )
        data.update(kwargs)
        proto = raw_pb2.Unit(**data)
        proto.pos.x, proto.pos.y = position
        return Unit(proto, bot, base_build=90000)

    return make


@pytest.fixture
def populate(bot):
    def apply(*units):
        structures = STRUCTURE_TYPES
        own = [u for u in units if u.is_mine]
        bot.all_own_units = Units(own, bot)
        bot.structures = Units([u for u in own if u.type_id in structures], bot)
        bot.units = Units([u for u in own if u.type_id not in structures], bot)
        bot.workers = bot.units(U.PROBE)
        bot.townhalls = bot.structures(U.NEXUS)
        bot.gas_buildings = bot.structures(U.ASSIMILATOR)
        bot.enemy_units = Units([u for u in units if u.is_enemy and u.type_id not in structures], bot)
        bot.enemy_structures = Units([u for u in units if u.is_enemy and u.type_id in structures], bot)
        bot.mineral_field = Units([u for u in units if u.type_id == U.MINERALFIELD], bot)
        bot.vespene_geyser = Units([u for u in units if u.type_id == U.VESPENEGEYSER], bot)

    return apply
