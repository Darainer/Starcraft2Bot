"""Check SDK-derived prices independently of the affordability implementation."""

import pytest
from sc2.ids.unit_typeid import UnitTypeId as U


@pytest.mark.parametrize(
    ("kind", "minerals", "gas", "supply"),
    [
        (U.ROBOTICSFACILITY, 150, 100, 0),
        (U.STARGATE, 150, 150, 0),
        (U.IMMORTAL, 275, 100, 4),
        (U.WARPPRISM, 250, 0, 2),
        (U.OBSERVER, 25, 75, 1),
        (U.STALKER, 125, 50, 2),
    ],
)
def test_sdk_costs_do_not_treat_buildings_as_morph_sources(bot, kind, minerals, gas, supply):
    cost = bot.calculate_cost(kind)
    assert (cost.minerals, cost.vespene) == (minerals, gas)
    assert bot.calculate_supply_cost(kind) == supply


def test_immortal_requires_gas_and_charges_full_training_cost(bot, make_unit, populate):
    populate(make_unit(U.ROBOTICSFACILITY))
    bot.minerals, bot.vespene = 275, 99
    assert not bot.affordable(U.IMMORTAL)
    bot.vespene = 100
    assert bot.affordable(U.IMMORTAL)
    assert bot.issue(bot.structures.first.train(U.IMMORTAL), paid=True, supply=True)
    assert (bot.minerals, bot.vespene, bot.supply_left) == (0, 0, 16)
