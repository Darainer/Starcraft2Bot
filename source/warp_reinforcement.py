"""Research/morph support, protected Prism phasing, and resource-aware warp-ins."""

import math

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G

from source.combat_assessment import observed_supply
from source.combat_assessment import visible_threats as combat_threats
from source.composition import (
    archon_committed,
    archon_permitted,
    merging_templar,
    planned_target,
    production_target,
    scouted_counter_plan,
)

WARP_UNITS = {
    U.STALKER: (A.WARPGATETRAIN_STALKER, "stalkers"),
    U.ZEALOT: (A.WARPGATETRAIN_ZEALOT, "zealots"),
    U.SENTRY: (A.WARPGATETRAIN_SENTRY, "sentries"),
    U.HIGHTEMPLAR: (A.WARPGATETRAIN_HIGHTEMPLAR, "high_templar"),
}


class WarpReinforcement:
    def __init__(self):
        self.warpins = 0
        self.last_issued = {}
        self.reserved_positions = []
        self.gate_positions = {}
        self.defense_signature = ()
        self.defense_supply_queued = 0
        self.last_report = {"phase": "waiting_for_tech"}
        self.archon_input_report = {"phase": "not_requested"}
        self.archon_input_started = None
        self.archon_input_retry = -999

    async def first_archon_input(self, bot):
        """Fund one legal rear warp-in after earlier counter milestones.

        The old first-counter path only trains from Gateways. Converted
        Warpgates need their own bounded reservation and paid placement path.
        """
        self.archon_input_report = {"phase": "not_requested"}
        counter = scouted_counter_plan(bot) if archon_permitted(bot) else None
        if (
            counter is None
            or not bot.settings.production
            or not bot.settings.warp_reinforcement
            or G.WARPGATERESEARCH not in bot.state.upgrades
            or not bot.structures(U.TEMPLARARCHIVE).ready
            or bot.supply_workers < 24
            or bot.supply_army < 24
            or bot.supply_left < 2
        ):
            self.archon_input_started = None
            return False
        missing = max(0, dict(counter.minimums).get("archons", 0) - archon_committed(bot))
        sources = sum(merging_templar(bot, unit) for unit in bot.units(U.HIGHTEMPLAR))
        needed = planned_target(bot, "high_templar") + 2 * int(missing) + sources
        if not missing or bot.units(U.HIGHTEMPLAR).amount + bot.already_pending(U.HIGHTEMPLAR) >= needed:
            self.archon_input_started = None
            return False
        if self.archon_input_started is not None and bot.time - self.archon_input_started >= 24:
            self.archon_input_retry = bot.time + 8
            self.archon_input_started = None
        if bot.time < self.archon_input_retry:
            self.archon_input_report = {"phase": "reservation_cooldown", "until": self.archon_input_retry}
            return False
        prior = getattr(bot, "_first_tech_reservation", None)
        if prior is not None and prior[0] != U.HIGHTEMPLAR:
            return False
        cost = bot.calculate_cost(U.HIGHTEMPLAR)
        if bot.vespene < cost.vespene + bot.settings.reserve_gas and not (
            bot.settings.gas
            and any(g.assigned_harvesters > 0 and g.vespene_contents > 0 for g in bot.gas_buildings.ready)
        ):
            return False
        pylons = bot.structures(U.PYLON).ready.filter(lambda pylon: bot.safe_at(pylon.position, 12))
        if not pylons:
            return False
        anchor = pylons.closest_to(bot.start_location).position
        ability = A.WARPGATETRAIN_HIGHTEMPLAR
        for gate in bot.structures(U.WARPGATE).ready.idle:
            if (
                not gate.is_powered
                or not bot.available(gate)
                or bot.time - self.last_issued.get(gate.tag, -100) < 4
            ):
                continue
            potential = await bot.get_available_abilities(gate, ignore_resource_requirements=True)
            if ability not in potential:
                continue
            point = await self.placement(bot, ability, anchor)
            if point is None or not bot.safe_at(point, 12):
                continue
            if self.archon_input_started is None:
                self.archon_input_started = bot.time
            if not bot.affordable(U.HIGHTEMPLAR):
                bot._first_tech_reservation = (U.HIGHTEMPLAR, cost.vespene)
                bot._macro_reserve = max(getattr(bot, "_macro_reserve", 0), cost.minerals)
                self.archon_input_report = {
                    "phase": "funding",
                    "until": self.archon_input_started + 24,
                    "missing_archons": missing,
                }
                return True
            legal = await bot.get_available_abilities(gate)
            if ability in legal and bot.issue_warp_in(gate.warp_in(U.HIGHTEMPLAR, point), U.HIGHTEMPLAR):
                self.warpins += 1
                self.last_issued[gate.tag] = bot.time
                self.gate_positions[gate.tag] = point
                self.reserved_positions.append((point, bot.time + 13))
                self.archon_input_started = None
                self.archon_input_report = {
                    "phase": "input_queued_not_confirmed",
                    "time": bot.time,
                    "gate": gate.tag,
                    "position": list(point),
                }
                return True
        return False

    def reject(self, failure, now):
        if failure["result"] == 41:
            for tag in failure["unit_tags"]:
                if tag in self.gate_positions:
                    self.reserved_positions.append((self.gate_positions[tag], now + 30))

    async def placement(self, bot, ability, anchor):
        self.reserved_positions = [(p, expiry) for p, expiry in self.reserved_positions if expiry > bot.time]
        points = []
        for radius in (2, 3, 4):
            for index in range(12):
                angle = (index + self.warpins) * math.pi / 6
                point = anchor.offset((radius * math.cos(angle), radius * math.sin(angle)))
                if not bot.state.psionic_matrix.covers(point) or not bot.is_visible(point):
                    continue
                if any(point.distance_to(p) < 1.5 for p, expiry in self.reserved_positions):
                    continue
                if any(not u.is_flying and u.distance_to(point) < u.radius + 0.75 for u in bot.all_own_units):
                    continue
                points.append(point)
        if not points:
            return None
        allowed = await bot.can_place(ability, points)
        return next((point for point, valid in zip(points, allowed, strict=False) if valid), None)

    async def tick(self, bot, waves, allow_spending=True):
        if not bot.settings.enabled or not bot.settings.attack or not bot.settings.warp_reinforcement:
            self.last_report = {"phase": "disabled"}
            return
        if G.WARPGATERESEARCH not in bot.state.upgrades:
            return
        for gateway in bot.structures(U.GATEWAY).ready.idle:
            if bot.available(gateway):
                abilities = await bot.get_available_abilities(gateway)
                if A.MORPH_WARPGATE in abilities:
                    bot.issue(gateway(A.MORPH_WARPGATE))
        prism_types = {U.WARPPRISM, U.WARPPRISMPHASING}
        prisms = bot.units.of_type(prism_types).ready
        home = bot.start_location
        visible_threats = combat_threats(bot)
        bases = bot.townhalls.ready
        base_threats = visible_threats.filter(lambda unit: any(unit.distance_to(base) < 22 for base in bases))
        raid_supply = sum(observed_supply(bot, unit) for unit in base_threats)
        small_raid = len(base_threats) <= 6 and raid_supply <= 12
        emergency_raid = bool(base_threats and getattr(bot, "economic_emergency", False))
        defense_base = None
        defense_threat = None
        if (small_raid or emergency_raid) and base_threats and bases:
            defense_threat = min(
                base_threats,
                key=lambda enemy: min(enemy.distance_to(base) for base in bases),
            )
            defense_base = bases.closest_to(defense_threat)
            signature = defense_base.tag
            if signature != self.defense_signature:
                self.defense_signature = signature
                self.defense_supply_queued = 0
        else:
            self.defense_signature = ()
            self.defense_supply_queued = 0
        anchor = None
        phase = "home_warp_in"
        if prisms:
            prism = prisms.first
            threats = visible_threats.filter(
                lambda u: u.is_visible and u.can_attack_air and u.distance_to(prism) < 11
            )
            exposed = (
                bool(threats) or prism.health + prism.shield < (prism.health_max + prism.shield_max) * 0.5
            )
            center = waves.center
            deployed = bool(waves.members) and center is not None and waves.phase in {"advance", "engage"}
            desired = center.towards(home, min(8, center.distance_to(home))) if deployed else home
            abilities = await bot.get_available_abilities(prism) if bot.available(prism) else []
            if prism.type_id == U.WARPPRISMPHASING:
                if exposed or not deployed or prism.distance_to(desired) > 18:
                    if A.MORPH_WARPPRISMTRANSPORTMODE in abilities:
                        bot.issue(prism(A.MORPH_WARPPRISMTRANSPORTMODE))
                    phase = "unphase_and_reposition"
                else:
                    anchor = prism.position
                    phase = "forward_warp_in"
            elif bot.available(prism):
                if exposed:
                    bot.issue(prism.move(home))
                    phase = "prism_retreat"
                elif deployed and prism.distance_to(desired) < 4 and bot.is_visible(desired):
                    if A.MORPH_WARPPRISMPHASINGMODE in abilities:
                        bot.issue(prism(A.MORPH_WARPPRISMPHASINGMODE))
                    phase = "phasing"
                elif prism.distance_to(desired) > 4:
                    bot.issue(prism.move(desired))
                    phase = "following_wave" if deployed else "staging_prism"
        if anchor is None:
            pylons = bot.structures(U.PYLON).ready.filter(lambda u: bot.safe_at(u.position))
            if pylons:
                anchor = pylons.closest_to(home).position
        defense_anchor_available = False
        if defense_base is not None:
            pylons = bot.structures(U.PYLON).ready.filter(lambda u: bot.safe_at(u.position, 8))
            if pylons:
                anchor = pylons.closest_to(defense_base).position
                phase = "home_defense_warp_in"
                defense_anchor_available = True
        defense_limit = min(20 if emergency_raid else 8, raid_supply) if defense_threat is not None else 0
        defense_kind = None
        if defense_threat is not None:
            if defense_threat.is_flying:
                preferred = (U.STALKER, U.SENTRY)
            elif defense_threat.is_armored:
                preferred = (U.STALKER, U.ZEALOT)
            else:
                preferred = (U.ZEALOT, U.STALKER)
            defense_kind = next(
                (kind for kind in preferred if production_target(bot, WARP_UNITS[kind][1]) > 0),
                None,
            )
        self.last_report = {
            "phase": phase,
            "archon_input": self.archon_input_report,
            "queued_warp_in_orders": self.warpins,
            "anchor": list(anchor) if anchor is not None else None,
            "small_base_raid": {
                "enemy_tags": sorted(unit.tag for unit in base_threats),
                "enemy_supply": raid_supply,
                "queued_defense_supply": self.defense_supply_queued,
                "base_tag": defense_base.tag if defense_base is not None else None,
                "emergency": emergency_raid,
            }
            if defense_threat is not None
            else None,
            "defense_warp_in_skipped": bool(defense_threat is not None and not defense_anchor_available),
        }
        if anchor is None or bot.supply_left < 2 or not bot.settings.production or not allow_spending:
            return
        choices = [
            kind
            for kind, (_, setting) in WARP_UNITS.items()
            if production_target(bot, setting) > 0
            and bot.units(kind).amount + bot.already_pending(kind) < production_target(bot, setting)
        ]
        choices.sort(
            key=lambda kind: (
                (bot.units(kind).amount + bot.already_pending(kind))
                / production_target(bot, WARP_UNITS[kind][1])
            )
        )
        if (
            defense_threat is not None
            and defense_anchor_available
            and self.defense_supply_queued < defense_limit
            and defense_kind in WARP_UNITS
            and production_target(bot, WARP_UNITS[defense_kind][1]) > 0
        ):
            choices = [defense_kind]
        for gate in bot.structures(U.WARPGATE).ready.idle:
            if not bot.available(gate) or bot.time - self.last_issued.get(gate.tag, -100) < 4:
                continue
            abilities = await bot.get_available_abilities(gate)
            for kind in choices:
                ability = WARP_UNITS[kind][0]
                if (
                    ability not in abilities
                    or not bot.affordable(kind, getattr(bot, "_macro_reserve", 0))
                    or bot.tech_requirement_progress(kind) < 1
                ):
                    continue
                position = await self.placement(bot, ability, anchor)
                if (
                    position is not None
                    and bot.safe_at(position, 12)
                    and bot.issue_warp_in(gate.warp_in(kind, position), kind)
                ):
                    self.warpins += 1
                    self.last_issued[gate.tag] = bot.time
                    self.gate_positions[gate.tag] = position
                    self.reserved_positions.append(
                        (position, bot.time + (5 if phase == "forward_warp_in" else 13))
                    )
                    self.last_report.update(queued_warp_in_orders=self.warpins, last_unit=kind.name)
                    if defense_threat is not None and kind == defense_kind:
                        self.defense_supply_queued += bot.calculate_supply_cost(kind)
                        self.last_report["small_base_raid"]["queued_defense_supply"] = (
                            self.defense_supply_queued
                        )
                    return
