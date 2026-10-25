import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from s2clientprotocol import sc2api_pb2
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G
from sc2.position import Point2

from source.analyze_session import summarize
from source.army_waves import ArmyWaves
from source.assistant_control import AssistantSettings
from source.game_assessment import GameAssessment
from source.replay_strategy import main, replay
from source.runtime import RuntimeAssistant
from source.scouting import ScoutController
from source.strategy_director import StrategicDirector
from source.strategy_profiles import PROFILES
from source.warp_reinforcement import WarpReinforcement


def test_opening_tech_precedes_continuous_probe_spending(bot, make_unit, populate):
    populate(make_unit(U.NEXUS, ideal_harvesters=16), make_unit(U.PYLON, (5, 5)), make_unit(U.PROBE))
    bot.minerals = 150
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_GATEWAY
    assert len(bot.actions) == 1


def test_first_combat_units_precede_natural_saving(bot, make_unit, populate):
    populate(
        make_unit(U.NEXUS),
        make_unit(U.PYLON),
        make_unit(U.GATEWAY),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.PROBE),
    )
    bot.settings.attack = True
    bot.settings.workers = bot.settings.gas = False
    bot.supply_workers = 20
    bot.minerals = 400
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.GATEWAYTRAIN_STALKER
    assert bot.minerals == 275


def test_existing_warpgates_do_not_restart_gateway_opening(bot, make_unit, populate):
    populate(
        make_unit(U.NEXUS),
        make_unit(U.PYLON),
        make_unit(U.WARPGATE),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.PROBE),
    )
    bot.control.command("!assist economy off")
    bot.settings.construction = True
    bot.construct = AsyncMock(return_value=False)
    asyncio.run(bot.macro())
    assert not bot.actions
    bot.construct.assert_awaited_once()


def test_emergency_spends_on_defenders_and_never_expands(bot, make_unit, populate):
    populate(
        make_unit(U.NEXUS),
        make_unit(U.GATEWAY),
        make_unit(U.CYBERNETICSCORE),
        make_unit(U.PROBE),
        make_unit(U.MARINE, (5, 5), alliance=4),
    )
    bot.settings.attack = True
    bot.economic_emergency = True
    bot.supply_workers = 24
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.GATEWAYTRAIN_STALKER
    bot._used.clear()
    bot.actions.clear()
    bot.settings.production = False
    asyncio.run(bot.macro())
    assert not bot.actions


def test_supply_buffer_does_not_build_to_200_prematurely(bot, make_unit, populate):
    populate(*(make_unit(U.NEXUS, (x, 0)) for x in (0, 30, 60)), make_unit(U.PROBE))
    bot.control.command("!assist economy off")
    bot.settings.supply = True
    bot.supply_left, bot.supply_cap = 18, 100
    asyncio.run(bot.macro())
    assert not bot.actions
    bot.supply_left = 1
    asyncio.run(bot.macro())
    assert bot.actions[0].ability == A.PROTOSSBUILD_PYLON


def test_no_implicit_expansion_or_worker_cap_raise_late_game(bot, make_unit, populate):
    populate(make_unit(U.NEXUS, ideal_harvesters=16), make_unit(U.CYBERNETICSCORE), make_unit(U.PROBE))
    bot.control.command("!assist economy off")
    bot.settings.expansion = bot.settings.workers = True
    bot.settings.bases, bot.settings.max_workers = 1, 16
    bot.supply_workers = 16
    bot.state.game_loop = 22400
    asyncio.run(bot.macro())
    assert not bot.actions


def test_reserved_expansion_money_cannot_be_spent_on_warpin(bot, make_unit, populate):
    gate = make_unit(U.WARPGATE)
    populate(gate, make_unit(U.PYLON, (10, 10)))
    bot.settings.attack = True
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    bot._macro_reserve = 400
    bot.minerals = 500
    bot.get_available_abilities = AsyncMock(return_value=[A.WARPGATETRAIN_STALKER])
    reinforcement = WarpReinforcement()
    asyncio.run(reinforcement.tick(bot, ArmyWaves()))
    assert not bot.actions
    bot.minerals = 525
    asyncio.run(reinforcement.tick(bot, ArmyWaves()))
    assert bot.actions and bot.minerals == 400


def test_critical_supply_reservation_blocks_cheap_warpin(bot, make_unit, populate):
    populate(make_unit(U.NEXUS), make_unit(U.PROBE), make_unit(U.WARPGATE), make_unit(U.PYLON))
    bot.control.command("!assist economy off")
    bot.settings.attack = bot.settings.supply = True
    bot.minerals, bot.supply_cap, bot.supply_left = 75, 40, 4
    asyncio.run(bot.macro())
    assert bot._macro_reserve == 100 and not bot.actions


def test_prism_can_escape_even_when_macro_spends(bot, make_unit, populate):
    prism = make_unit(U.WARPPRISM, (50, 50), is_flying=True, health=10, shield=0)
    populate(prism)
    bot.settings.attack = True
    bot.state.upgrades.add(G.WARPGATERESEARCH)
    bot._paid_action_issued = True
    asyncio.run(WarpReinforcement().tick(bot, ArmyWaves(), allow_spending=False))
    assert bot.actions[0].unit.tag == prism.tag and bot.actions[0].target == bot.start_location


def test_very_hard_launches_coherent_small_pressure_force(bot, make_unit, populate):
    populate(*(make_unit(U.STALKER, (10, 10)) for _ in range(8)))
    bot.settings.profile = "pressure"
    bot.opponent_difficulty = "VeryHard"
    bot.scout_report = {"enemy_seen": True}
    _, state = ArmyWaves().plan(bot, bot.units, Point2((80, 80)), Point2((10, 10)), PROFILES["pressure"])
    assert state["phase"] == "advance"
    assert state["core_supply"] == 16
    assert state["enemy_force_supply_gate"] is None


def test_observer_answers_pending_attack_question(bot, make_unit, populate):
    populate(
        make_unit(U.NEXUS),
        make_unit(U.OBSERVER, (20, 20)),
        *(make_unit(U.STALKER, (10, 10)) for _ in range(12)),
    )
    bot.settings.attack = True
    bot.is_visible = lambda point: False
    state = GameAssessment().observe(bot, bot.units(U.STALKER))
    bot.strategic_plan = StrategicDirector().decide(state)
    result = ScoutController()._observer_tick(bot)
    assert result["phase"] == "scouting_mission_approach"
    main = bot.strategic_plan.missions[-1]
    assert Point2(result["target"]).distance_to(Point2(main.target)) <= 8.1


def test_dead_sightings_are_removed_and_never_double_counted(bot, make_unit, populate):
    unit = make_unit(U.STALKER, (80, 80), alliance=4)
    populate(unit)
    bot.settings.attack = True
    controller = ScoutController()
    for _ in range(2):
        controller.tick(bot)
    assert bot.scout_report["composition_intel"]["supply"] == 2
    populate()
    bot.state.dead_units = {unit.tag}
    controller.tick(bot)
    assert bot.scout_report["composition_intel"]["supply"] == 0


def test_runtime_control_cadence_is_independent_of_snapshot_clock():
    bot = RuntimeAssistant(AssistantSettings(), SimpleNamespace())
    bot.state = SimpleNamespace(game_loop=0, response_observation=sc2api_pb2.ResponseObservation())
    bot.all_own_units = []
    bot.scouting = SimpleNamespace(tick=Mock(return_value={}))
    bot.tactics = SimpleNamespace(tick=Mock(return_value={"strategy": "manual"}), micro=Mock(return_value=[]))
    bot.client = SimpleNamespace(available_ability_snapshot=AsyncMock(return_value={}))
    asyncio.run(bot.on_tactical_step())
    bot.state.game_loop = 4
    asyncio.run(bot.on_tactical_step())
    assert bot.tactics.tick.call_count == 1 and bot.tactics.micro.call_count == 2
    # A user toggle applies on this observation, before the next scheduled plan.
    bot.settings.enabled = False
    asyncio.run(bot.on_tactical_step())
    assert bot.tactics.tick.call_count == 2
    bot.state.game_loop = 28
    asyncio.run(bot.on_tactical_step())
    assert bot.tactics.tick.call_count == 3
    bot.client.available_ability_snapshot.assert_not_awaited()


def test_replay_and_sampled_metrics_do_not_issue_game_orders(bot, make_unit, populate, tmp_path, capsys):
    populate(make_unit(U.NEXUS), *(make_unit(U.STALKER) for _ in range(12)))
    state = GameAssessment().observe(bot, bot.units)
    path = tmp_path / "report.json"
    path.write_text('{"phase":"ended","result":"Tie"}')
    events = [{"time": 10, "result": "unfavorable_fight", "mission": "denial"}]
    row = {
        "game_loop": 224,
        "decision": {
            "strategy": "push",
            "assessment": state.to_dict(),
            "plan": {"objective": "pressure"},
            "missions": {"main": {"phase": "advance"}},
            "controller_ms": 2,
            "events": events,
        },
        "observation": {
            "observation": {
                "player_common": {"minerals": 600, "vespene": 300, "food_cap": 40, "food_used": 40},
                "raw_data": {
                    "units": [{"unit_type": U.GATEWAY.value, "alliance": "Self", "build_progress": 1}]
                },
            }
        },
    }
    snapshots = path.with_suffix(".state.jsonl")
    snapshots.write_text(json.dumps(row) + "\n" + json.dumps({**row, "game_loop": 448}) + "\n")
    result = replay(snapshots)
    assert result["samples"] == 2 and not bot.actions
    metrics = summarize(path)["performance"]
    assert metrics["sampled_supply_block_seconds"] == 10
    assert metrics["sampled_idle_facility_seconds"] == 10
    assert metrics["mission_outcomes"]["unfavorable_fight"] == 1
    assert metrics["first_offensive_advance_seconds"] == 10
    assert metrics["controller_ms_p95"] == 2
    main([str(snapshots)])
    assert json.loads(capsys.readouterr().out)["samples"] == 2
    output = tmp_path / "comparison.json"
    main([str(snapshots), "--output", str(output)])
    assert json.loads(output.read_text())["samples"] == 2
    snapshots.write_text('\n{"decision": {}}\n')
    assert replay(snapshots)["skipped_legacy_samples"] == 1
    snapshots.write_text("invalid")
    with pytest.raises(SystemExit):
        main([str(snapshots)])
