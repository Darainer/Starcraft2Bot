"""Research/morph support, protected Prism phasing, and resource-aware warp-ins."""

import math

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G

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
        self.last_report = {"phase": "waiting_for_tech"}

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

    async def tick(self, bot, waves):
        if not bot.settings.attack or not bot.settings.warp_reinforcement:
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
        anchor = None
        phase = "home_warp_in"
        if prisms:
            prism = prisms.first
            threats = bot.enemy_units.filter(
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
        self.last_report = {
            "phase": phase,
            "queued_warp_in_orders": self.warpins,
            "anchor": list(anchor) if anchor is not None else None,
        }
        if anchor is None or bot.supply_left < 6:
            return
        choices = [
            kind
            for kind, (_, setting) in WARP_UNITS.items()
            if getattr(bot.settings, setting) > 0
            and bot.units(kind).amount + bot.already_pending(kind) < getattr(bot.settings, setting)
        ]
        choices.sort(
            key=lambda kind: (
                (bot.units(kind).amount + bot.already_pending(kind))
                / getattr(bot.settings, WARP_UNITS[kind][1])
            )
        )
        for gate in bot.structures(U.WARPGATE).ready.idle:
            if not bot.available(gate) or bot.time - self.last_issued.get(gate.tag, -100) < 4:
                continue
            abilities = await bot.get_available_abilities(gate)
            for kind in choices:
                ability = WARP_UNITS[kind][0]
                if (
                    ability not in abilities
                    or not bot.affordable(kind)
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
                    return
