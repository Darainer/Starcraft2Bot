from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.army_waves import ArmyWaves
from source.strategy_profiles import PROFILES


def wave(bot, make_unit, populate, count=10):
    units = [make_unit(U.STALKER, (10, 10)) for _ in range(count)]
    populate(*units)
    bot.settings.profile = "pressure"
    bot.state.game_loop = 6720
    bot.scout_report = {"enemy_seen": True}
    return ArmyWaves(), Point2((100, 100)), Point2((10, 10)), PROFILES["pressure"]


def test_new_wave_waits_for_observed_force_instead_of_one_counter_unit(bot, make_unit, populate):
    waves, target, rally, policy = wave(bot, make_unit, populate)
    bot.scout_report["enemy_unit_evidence"] = [
        {"tag": i, "supply": 2, "seen_seconds": 300} for i in range(12)
    ]
    _, state = waves.plan(bot, bot.units, target, rally, policy)
    assert state["enemy_force_supply_gate"] == 30 and state["phase"] == "assemble"
    populate(*bot.units, *[make_unit(U.STALKER, (10, 10)) for _ in range(6)])
    assert waves.plan(bot, bot.units, target, rally, policy)[1]["phase"] == "advance"


def test_stale_future_and_duplicate_contacts_never_inflate_force_gate(bot, make_unit, populate):
    waves, target, rally, policy = wave(bot, make_unit, populate)
    bot.scout_report["enemy_unit_evidence"] = [
        {"tag": 1, "supply": 8, "seen_seconds": 300},
        {"tag": 1, "supply": 8, "seen_seconds": 300},
        {"tag": 2, "supply": 100, "seen_seconds": 200},
        {"tag": 3, "supply": 100, "seen_seconds": 400},
    ]
    state = waves.plan(bot, bot.units, target, rally, policy)[1]
    assert state["enemy_force_supply_gate"] == 10 and state["phase"] == "advance"


def test_new_weak_sighting_does_not_refresh_the_old_army(bot, make_unit, populate):
    waves, target, rally, policy = wave(bot, make_unit, populate)
    bot.scout_report.update(
        last_enemy_force={"supply": 100, "seen_seconds": 300},
        enemy_unit_evidence=[
            {"tag": 1, "supply": 100, "seen_seconds": 200},
            {"tag": 2, "supply": 1, "seen_seconds": 300},
        ],
    )
    state = waves.plan(bot, bot.units, target, rally, policy)[1]
    assert state["enemy_force_supply_gate"] is None and state["phase"] == "advance"


def test_new_information_does_not_recall_an_already_active_wave(bot, make_unit, populate):
    waves, target, rally, policy = wave(bot, make_unit, populate)
    waves.plan(bot, bot.units, target, rally, policy)
    members = set(waves.members)
    bot.scout_report["last_enemy_force"] = {"supply": 100, "seen_seconds": 300}
    state = waves.plan(bot, bot.units, target, rally, policy)[1]
    assert state["minimum_supply"] == 80
    assert set(waves.members) == members and state["phase"] == "advance"
