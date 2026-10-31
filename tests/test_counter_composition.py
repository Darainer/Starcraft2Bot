import asyncio
from dataclasses import asdict

import pytest
from sc2.data import Race
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G

from source.composition import composition_targets, scouted_counter_plan
from source.counter_composition import SUPPLY, propose_counter_plan


def force(kind, count=16, *, supply=2, armored=False, air=False, now=300):
    return [
        dict(tag=str(i), kind=kind, seen_seconds=now, supply=supply, armored=armored, air=air)
        for i in range(count)
    ]


def plan(race="Terran", evidence=None, **kwargs):
    args = dict(
        max_workers=70, workers=40, bases=2, own_army=40, support_targets={"observers": 1, "warp_prisms": 1}
    )
    args.update(kwargs)
    now = args.pop("now", 300)
    return propose_counter_plan(now, race, evidence or force("MARINE"), **args)


def test_scouted_race_and_fielded_mix_choose_distinct_replacements():
    bio = plan()
    roach = plan("Zerg", force("ROACH", armored=True))
    lurker = plan("Zerg", force("LURKERMPBURROWED", armored=True))
    swarm = plan("Zerg", force("ZERGLING", supply=0.5))
    siege = plan(evidence=force("SIEGETANKSIEGED", armored=True))
    assert len({p.family for p in (bio, roach, lurker, swarm, siege)}) == 5
    assert dict(roach.targets)["immortals"] > dict(swarm.targets)["immortals"]
    assert dict(swarm.targets)["colossi"] > dict(roach.targets)["colossi"]
    assert dict(lurker.targets)["observers"] >= 2
    assert all(
        p.splash_required and dict(p.targets)["colossi"] >= 2 for p in (bio, roach, lurker, swarm, siege)
    )


def test_air_mass_needs_domain_correct_splash_and_upgrades_for_our_units():
    air = force("MUTALISK", air=True)
    p = plan("Zerg", air)
    assert dict(p.targets)["colossi"] == 0
    assert p.splash_required and "ground-only" in p.splash_constraint
    assert dict(p.targets)["high_templar"] == 0
    assert p.upgrade_focus == "ground"  # Stalkers still use ground upgrades against air.
    permitted = plan("Zerg", air, storm=True)
    assert dict(permitted.targets)["high_templar"] > 0
    assert "TEMPLARARCHIVE" in permitted.tech_goals


def test_late_game_replacements_keep_splash_and_reduce_gateway_filler():
    early = plan()
    late = plan(evidence=force("MARINE", now=900), now=900)
    assert late.late_game and not early.late_game
    assert dict(late.targets)["zealots"] < dict(early.targets)["zealots"]
    assert dict(late.targets)["colossi"] >= 3
    assert late.upgrade_focus == "ground"


@pytest.mark.parametrize("workers", [40, 70, 100, 150])
def test_combined_supply_budget_includes_support_and_harassment(workers):
    p = plan(max_workers=workers, oracle_allowed=True, worker_opportunity=True)
    assert p.allocated_supply == sum(SUPPLY[k] * v for k, v in p.targets)
    assert p.allocated_supply + workers <= 200
    assert dict(p.targets)["oracles"] == 1


def test_oracle_needs_both_permission_and_positive_economic_opportunity():
    assert dict(plan(worker_opportunity=True).targets)["oracles"] == 0
    assert dict(plan(oracle_allowed=True).targets)["oracles"] == 0
    assert dict(plan(oracle_allowed=True, worker_opportunity=True).targets)["oracles"] == 1


@pytest.mark.parametrize("now", [254, 301, float("nan")])
def test_individual_stale_future_and_invalid_contacts_are_not_evidence(now):
    assert plan(evidence=force("MARINE", now=now)) is None


def test_duplicate_tags_do_not_inflate_force_or_force_splash():
    contacts = force("MARINE", count=2, supply=2)
    p = plan(evidence=contacts * 20)
    assert not p.splash_required
    assert "Observed 4 supply" in p.evidence[0]
    assert plan("Protoss") is None


def configure(bot, make_unit, populate):
    bot.settings.attack = True
    bot.settings.composition_policy = "scouted"
    bot.enemy_race = Race.Zerg
    bot.supply_workers, bot.supply_army = 40, 40
    bot.state.game_loop = 6720
    for name, cost in SUPPLY.items():
        from source.composition import UNIT_NAMES

        bot.game_data.units[UNIT_NAMES[name].value]._proto.food_required = cost
    populate(make_unit(U.NEXUS), make_unit(U.NEXUS, (30, 0)))
    bot.scout_report = {"enemy_unit_evidence": force("ROACH", armored=True)}


def test_adapter_preserves_settings_and_expires_without_fresh_scouts(bot, make_unit, populate):
    configure(bot, make_unit, populate)
    before = asdict(bot.settings)
    targets = composition_targets(bot)
    assert scouted_counter_plan(bot).family == "zerg_armored"
    assert asdict(bot.settings) == before
    bot.state.game_loop = 8960  # 400 seconds, older than bounded hold.
    assert scouted_counter_plan(bot) is None
    assert composition_targets(bot)["immortals"] == bot.settings.immortals
    assert targets["immortals"] > bot.settings.immortals


def test_lost_splash_is_replaced_after_first_tech_latch_was_satisfied(bot, make_unit, populate):
    configure(bot, make_unit, populate)
    bot.settings.scouting = False
    bot.scout_report = {"enemy_unit_evidence": force("ZERGLING", supply=0.5)}
    bot._first_tech_combat_seen = {U.STALKER, U.IMMORTAL, U.COLOSSUS}
    populate(*bot.all_own_units, make_unit(U.ROBOTICSFACILITY), make_unit(U.ROBOTICSBAY))
    producer, kind = bot.first_tech_combat()
    assert kind == U.COLOSSUS
    producer._proto.is_selected = True
    assert bot.first_tech_combat() is None


def test_ground_counter_upgrade_precedes_air_even_when_enemy_is_flying(bot, make_unit, populate):
    configure(bot, make_unit, populate)
    bot.scout_report = {"enemy_unit_evidence": force("BROODLORD", air=True, armored=True)}
    bot.settings.warp_reinforcement = False
    populate(*bot.all_own_units, make_unit(U.CYBERNETICSCORE), make_unit(U.FORGE))
    ground = bot.game_data.upgrades[G.PROTOSSGROUNDWEAPONSLEVEL1.value].research_ability.id
    air = bot.game_data.upgrades[G.PROTOSSAIRWEAPONSLEVEL1.value].research_ability.id
    bot.get_available_abilities.return_value = [ground, air]
    assert asyncio.run(bot.upgrade(0))
    assert bot.actions[0].ability == ground


@pytest.mark.parametrize(
    "disabled", ["attack", "enabled", "adaptive_composition", "manual", "script", "legacy"]
)
def test_new_targets_respect_control_modes(bot, make_unit, populate, disabled):
    configure(bot, make_unit, populate)
    if disabled == "manual":
        bot.settings.strategy = "retreat"
    elif disabled == "script":
        bot.settings.strategy_script = "custom.py"
    elif disabled == "legacy":
        bot.settings.composition_policy = "legacy"
    else:
        setattr(bot.settings, disabled, False)
    assert scouted_counter_plan(bot) is None
