"""Protoss economy and abilities; tactical orders live in the separate controller."""

import math

from loguru import logger
from sc2.bot_ai import BotAI
from sc2.data import Race
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G
from sc2.unit_command import UnitCommand

from source.assistant_control import Control, within_budget
from source.combat_assessment import visible_threats
from source.composition import composition_targets, production_target
from source.layout import find_spaced_placement
from source.strategy_profiles import PROFILES

ARMY_TARGETS = {
    U.ZEALOT: "zealots",
    U.STALKER: "stalkers",
    U.SENTRY: "sentries",
    U.IMMORTAL: "immortals",
    U.HIGHTEMPLAR: "high_templar",
    U.COLOSSUS: "colossi",
    U.VOIDRAY: "voidrays",
}
PRODUCERS = {
    U.GATEWAY: (U.STALKER, U.ZEALOT, U.SENTRY, U.HIGHTEMPLAR),
    U.ROBOTICSFACILITY: (U.OBSERVER, U.WARPPRISM, U.IMMORTAL, U.COLOSSUS),
    U.STARGATE: (U.VOIDRAY,),
}
PRODUCTION_TARGETS = {**ARMY_TARGETS, U.WARPPRISM: "warp_prisms", U.OBSERVER: "observers"}
SPELLS = {
    A.EFFECT_BLINK_STALKER,
    A.PSISTORM_PSISTORM,
    A.FEEDBACK_FEEDBACK,
    A.GUARDIANSHIELD_GUARDIANSHIELD,
    A.EFFECT_VOIDRAYPRISMATICALIGNMENT,
}
GROUND_UPGRADES = tuple(
    getattr(G, f"{family}{level}")
    for level in range(1, 4)
    for family in ("PROTOSSGROUNDWEAPONSLEVEL", "PROTOSSGROUNDARMORSLEVEL", "PROTOSSSHIELDSLEVEL")
)
AIR_UPGRADES = tuple(
    getattr(G, f"{family}{level}")
    for level in range(1, 4)
    for family in ("PROTOSSAIRWEAPONSLEVEL", "PROTOSSAIRARMORSLEVEL")
)


def storm_target(caster, enemies, friends, existing):
    """Conservative targeting: visible clusters, cast range, no nearby friendlies."""
    best, count = None, 2
    for enemy in enemies:
        point = enemy.position
        if caster.distance_to(point) > 9:
            continue
        if any(point.distance_to(old) < 3.5 for old in existing):
            continue
        if any(friend.distance_to(point) < 1.75 + friend.radius for friend in friends):
            continue
        hits = sum(other.distance_to(point) <= 1.5 for other in enemies)
        if hits > count:
            best, count = point, hits
    return best


class EconomyAssistant(BotAI):
    def __init__(self, settings=None):
        super().__init__()
        self.raw_affects_selection = False
        # Explicit queuing makes same-frame spending and actor ownership auditable.
        self.unit_command_uses_self_do = True
        self.control = Control(settings)
        self._last_macro = -10.0
        self._last_allocation = -10.0
        self._last_hud = -10.0
        self._used = set()
        self._casts = {}
        self._storms = []
        self._last_upgrade = -60.0
        self._blocked_producers = {}
        self.action_rejections = {}
        self._production_cursor = 0
        self.construction_reservations = {}
        self.scout_tag = None
        self.scout_report = {}
        self._paid_action_issued = False
        self.economic_emergency = False
        self._last_production = -10.0
        self.strategic_plan = None

    @property
    def settings(self):
        return self.control.settings

    async def on_start(self):
        await self.chat_send(
            "Assistant ready. Type !assist help; !assist attack off returns army control", team_only=True
        )

    def available(self, unit):
        return unit.tag != self.scout_tag and unit.tag not in self._used and self.control.eligible(unit)

    def issue(self, command, paid=False, supply=False, scout_order=False):
        if not isinstance(command, UnitCommand):
            return False
        eligible = self.available(command.unit) or (
            scout_order
            and command.unit.tag == self.scout_tag
            and command.unit.tag not in self._used
            and self.control.eligible(command.unit)
        )
        if not eligible:
            return False
        accepted = self.do(command, subtract_cost=paid, subtract_supply=supply, can_afford_check=paid)
        if accepted:
            self._used.add(command.unit.tag)
            self._paid_action_issued |= paid
        return accepted

    def affordable(self, item, extra_minerals=0):
        cost = self.calculate_cost(item)
        investment = getattr(self, "_first_tech_reservation", None)
        if (
            investment is not None
            and item != investment[0]
            and self.vespene - cost.vespene < self.settings.reserve_gas + investment[1]
        ):
            return False
        return self.can_afford(item) and within_budget(
            self.minerals, self.vespene, cost.minerals, cost.vespene, self.settings, extra_minerals
        )

    def issue_warp_in(self, command, kind):
        # Warp-in IDs have separate SDK cost lookup entries; use the live unit
        # price and supply explicitly so budgeting is charged exactly once.
        if not self.affordable(kind) or not self.can_feed(kind) or not self.issue(command):
            return False
        cost = self.calculate_cost(kind)
        supply = self.calculate_supply_cost(kind)
        self.minerals -= cost.minerals
        self.vespene -= cost.vespene
        self.supply_left -= supply
        self.supply_used += supply
        self._paid_action_issued = True
        return True

    async def on_step(self, iteration):
        self._used.clear()
        self._paid_action_issued = False
        selected = [unit.tag for unit in self.all_own_units if unit.is_selected]
        for message in self.state.chat:
            if message.player_id != self.player_id:
                continue
            reply = self.control.command(message.message, selected)
            if reply:
                logger.info("Assistant command: {} -> {}", message.message, reply)
                # SC2 chat messages are short; keep help/status readable.
                for start in range(0, len(reply), 120):
                    await self.chat_send(f"[Assistant] {reply[start : start + 120]}", team_only=True)
        live = {unit.tag for unit in self.all_own_units}
        self.control.released.intersection_update(live)
        for error in self.state.action_errors:
            key = f"{error.ability_id}:{error.result}"
            self.action_rejections[key] = self.action_rejections.get(key, 0) + 1
            if error.result == 41:
                self._blocked_producers[error.unit_tag] = self.time + 15
            logger.warning(
                "SC2 rejected action: unit={} ability={} result={}",
                error.unit_tag,
                error.ability_id,
                error.result,
            )
        if self.settings.enabled:
            await self.powers()
        await self.on_tactical_step()
        if self.settings.enabled:
            if self.time - self._last_macro >= 0.25:
                self._last_macro = self.time
                reinforcement = getattr(self, "reinforcement", None)
                await self.macro()
                if reinforcement is not None:
                    await reinforcement.tick(
                        self, self.tactics.waves, allow_spending=not self._paid_action_issued
                    )
            if self.settings.allocation and self.time - self._last_allocation >= 1:
                self._last_allocation = self.time
                await self.allocate_workers()
        if self.settings.hud and self.time - self._last_hud >= 0.5:
            self._last_hud = self.time
            s = self.settings
            self.client.debug_text_screen(
                f"Assistant {'ON' if s.enabled else 'PAUSED'} | !assist help\n"
                f"Workers {s.workers} Supply {s.supply} Build {s.construction} "
                f"Produce {s.production} Expand {s.expansion}\n"
                f"Chrono {s.chrono} Blink {s.blink} Storm {s.storm} "
                f"Feedback {s.feedback} Guardian {s.guardian_shield} Alignment {s.voidray_alignment}\n"
                f"Reserve {s.reserve_minerals}m/{s.reserve_gas}g | released {len(self.control.released)}",
                pos=(0.01, 0.08),
                size=12,
            )

    async def on_tactical_step(self):
        """Runtime hook after commands/ownership, before economic spending."""

    def safe_at(self, point, radius=18):
        return not any(enemy.distance_to(point) < radius for enemy in visible_threats(self))

    def builder(self, point):
        workers = self.workers.filter(lambda w: self.available(w) and (w.is_idle or w.is_gathering))
        return workers.closest_to(point) if workers else None

    async def safe_expansion_location(self, reference, require_minerals=False):
        preferred = await self.get_next_expansion()
        candidates = ([preferred] if preferred else []) + sorted(
            self.expansion_locations_list, key=reference.distance_to
        )
        for location in candidates:
            if require_minerals and not self.mineral_field.closer_than(10, location).filter(
                lambda patch: patch.mineral_contents > 0
            ):
                continue
            if any(base.distance_to(location) < 10 for base in self.townhalls):
                continue
            if self.enemy_structures.closer_than(10, location):
                continue
            if self.safe_at(location, 12):
                return location
        return None

    async def build_structure(self, kind, near, max_distance=12, allow_pending=False):
        if (self.already_pending(kind) and not allow_pending) or not self.affordable(kind):
            return False
        worker = self.builder(near)
        if worker is None:
            return False
        placement = await find_spaced_placement(self, kind, near, max_distance)
        if placement is None or not self.safe_at(placement):
            return False
        workers = self.workers.filter(
            lambda unit: self.available(unit) and (unit.is_idle or unit.is_gathering)
        ).sorted_by_distance_to(placement)
        query = getattr(self.client, "query_pathing", None)
        for candidate in workers[:4]:
            if (
                query is None or candidate.distance_to(placement) < 3 or await query(candidate, placement)
            ) and self.issue(candidate.build(kind, placement), paid=True):
                self.construction_reservations[candidate.tag] = (kind, placement, self.time + 45)
                return True
        return False

    async def allocate_workers(self):
        """Only idle/gathering probes; never pull a scouting, fighting or building probe."""
        bases = self.townhalls.ready.filter(lambda base: self.safe_at(base.position))
        if not bases:
            return
        gases = self.gas_buildings.ready.filter(
            lambda gas: gas.vespene_contents > 0 and self.safe_at(gas.position)
        )
        # A worker loss must not leave the surviving economy entirely on gas.
        # Reserve mineral income for replacement probes/buildings immediately,
        # rather than waiting for the stockpile threshold to release gas workers.
        mineral_floor = max(8, math.ceil(len(self.workers) * 0.6))
        gas_budget = max(0, len(self.workers) - mineral_floor)
        if self.vespene > max(500, self.minerals * 1.5):
            gas_budget = 0
        gas_targets = {}
        for gas in gases.sorted_by_distance_to(bases.closest_to(self.start_location)):
            gas_targets[gas.tag] = min(3, gas.ideal_harvesters, gas_budget)
            gas_budget -= gas_targets[gas.tag]
        gas_need = {gas.tag: max(0, gas_targets[gas.tag] - gas.assigned_harvesters) for gas in gases}
        base_need = {base.tag: max(0, base.ideal_harvesters - base.assigned_harvesters) for base in bases}
        excess = {
            unit.tag: max(0, unit.assigned_harvesters - unit.ideal_harvesters)
            for unit in self.townhalls.ready | self.gas_buildings.ready
        }
        for gas in gases:
            excess[gas.tag] = max(0, gas.assigned_harvesters - gas_targets[gas.tag])
        for worker in self.workers:
            if not self.available(worker) or not (worker.is_idle or worker.is_gathering):
                continue
            if worker.is_carrying_resource:
                continue
            origin = None
            if worker.is_gathering:
                target = worker.order_target
                gas_origin = next((gas for gas in self.gas_buildings if gas.tag == target), None)
                mineral = self.mineral_field.find_by_tag(target) if isinstance(target, int) else None
                if gas_origin:
                    origin = gas_origin.tag
                elif mineral and self.townhalls.ready:
                    origin = self.townhalls.ready.closest_to(mineral).tag
                else:
                    continue
                # Gas filling may borrow a mineral worker, but never drain balanced gas.
                if excess.get(origin, 0) <= 0 and (gas_origin or not any(gas_need.values())):
                    continue
            destination = next(
                (
                    gas
                    for gas in sorted(gases, key=worker.distance_to)
                    if gas_need[gas.tag] > 0 and gas.tag != origin
                ),
                None,
            )
            if destination:
                if self.issue(worker.gather(destination)):
                    gas_need[destination.tag] -= 1
                    if origin in base_need and excess.get(origin, 0) <= 0:
                        base_need[origin] += 1
            else:
                base = next(
                    (
                        base
                        for base in sorted(bases, key=worker.distance_to)
                        if base_need[base.tag] > 0 and base.tag != origin
                    ),
                    None,
                )
                # Idle workers should still mine if every safe base is saturated.
                if base is None and (worker.is_idle or (origin in gas_need and excess.get(origin, 0) > 0)):
                    base = bases.closest_to(worker)
                minerals = self.mineral_field.closer_than(10, base) if base else []
                if not minerals:
                    continue
                if self.issue(worker.gather(minerals.closest_to(worker))):
                    base_need[base.tag] = max(0, base_need[base.tag] - 1)
            if worker.tag in self._used and origin is not None:
                excess[origin] = max(0, excess.get(origin, 0) - 1)

    async def macro(self):
        """At most one paid action per macro tick, plus periodic worker allocation."""
        s = self.settings
        self._first_tech_reservation = None
        bases = self.townhalls.ready
        contacts = visible_threats(self)
        early_contact = self.time < 180 and any(
            any(enemy.distance_to(base) < 32 for base in bases) for enemy in contacts
        )
        completed_supply = sum(
            self.calculate_supply_cost(unit.type_id)
            for unit in self.units.of_type(set(ARMY_TARGETS)).ready
            if unit.can_attack
        )
        requested_supply = sum(
            production_target(self, name) * self.calculate_supply_cost(kind)
            for kind, name in ARMY_TARGETS.items()
            if kind in {U.ZEALOT, U.STALKER}
        )
        first_defender = (
            self.enemy_race == Race.Zerg
            and s.attack
            and s.production
            and self.time < 180
            and requested_supply > 0
            and (completed_supply < min(6, requested_supply) or early_contact)
        )
        self.opening_phase = (
            "defend" if first_defender and early_contact else "first_force" if first_defender else "complete"
        )
        self._opening_reserve = 0
        if not first_defender:
            self.opening_defense_anchor = None
        self._macro_reserve = 0
        base_target = s.bases
        capacity = len(self.structures.of_type(set(PRODUCERS) | {U.WARPGATE}))
        supply_buffer = min(20, max(4, len(bases) * 2 + capacity * 2))
        pending_supply = 8 * self.already_pending(U.PYLON)
        need_supply = self.supply_left + pending_supply <= supply_buffer
        pylon_target = min(3, max(1, math.ceil((supply_buffer - self.supply_left) / 8)))
        if not bases:
            if s.expansion and not self.townhalls and self.workers:
                await self.build_structure(U.NEXUS, self.start_location, max_distance=2)
            return
        home = bases.closest_to(self.start_location)
        safe_bases = bases.filter(lambda base: self.safe_at(base.position))
        core_priority = (
            first_defender
            and not early_contact
            and s.construction
            and self.units(U.ZEALOT).amount + self.already_pending(U.ZEALOT) >= 2
            and not self.structures(U.CYBERNETICSCORE)
            and not self.already_pending(U.CYBERNETICSCORE)
        )
        if first_defender and not core_priority and self.produce_opening_defender():
            return
        if not safe_bases:
            if first_defender and s.construction and await self.opening_battery(home, contacts):
                return
            if s.supply and self.supply_cap < 200 and need_supply:
                safe_pylons = self.structures(U.PYLON).ready.filter(
                    lambda pylon: self.safe_at(pylon.position)
                )
                if await self.build_supply_pylons([pylon.position for pylon in safe_pylons], pylon_target):
                    return
            if not first_defender and self.economic_emergency and s.production and self.produce(0):
                return
            if (
                s.expansion
                and self.townhalls.amount < base_target
                and not self.already_pending(U.NEXUS)
                and self.supply_workers >= 14
                and not self.economic_emergency
                and not first_defender
                and (self.strategic_plan is None or self.strategic_plan.expand)
            ):
                location = await self.safe_expansion_location(self.start_location)
                if (
                    location
                    and self.builder(location)
                    and await self.build_structure(U.NEXUS, location, max_distance=2)
                ):
                    return
            return
        home = safe_bases.closest_to(home)
        # Saturation falls as mineral patches disappear. Saving for a replacement
        # mineral line must not require training up to the normal expansion gate:
        # that same depleted saturation also prevents producing more workers.
        depleted_income = (
            self.time >= 360
            and any(base.ideal_harvesters < 8 for base in safe_bases)
            and sum(base.ideal_harvesters for base in safe_bases) < max(8, self.supply_workers * 0.6)
        )
        if (
            depleted_income
            and s.expansion
            and self.townhalls.amount < base_target
            and not self.already_pending(U.NEXUS)
            and self.supply_workers >= 14
            and not self.economic_emergency
            and (self.strategic_plan is None or self.strategic_plan.expand)
            and (not s.attack or self.supply_army >= 12)
        ):
            location = await self.safe_expansion_location(home.position, require_minerals=True)
            if location and self.builder(location):
                self._macro_reserve = 400
                if not self.affordable(U.NEXUS):
                    return  # Retain the remaining bank instead of spending the recovery fund.
                if await self.build_structure(U.NEXUS, location, max_distance=2):
                    return
        # Spending/building first prevents allocation from claiming every idle builder.
        if (
            s.supply
            and self.supply_cap < 200
            and need_supply
            and self.already_pending(U.PYLON) < pylon_target
        ):
            # Spread supply/power across bases and around existing power rather
            # than exhausting one small search ring at the original Nexus.
            anchors = [base.position.towards(self.game_info.map_center, 5) for base in safe_bases]
            anchors += [p.position for p in self.structures(U.PYLON).ready]
            if await self.build_supply_pylons(anchors, pylon_target):
                return
            if not self.already_pending(U.PYLON) and not self.affordable(U.PYLON):
                self._macro_reserve = self.calculate_cost(U.PYLON).minerals
                return  # Save for supply instead of repeatedly spending on probes.
        if first_defender and s.construction:
            gateways = self.structures(U.GATEWAY) | self.structures(U.WARPGATE)
            count = len(gateways) + sum(
                kind == U.GATEWAY and expiry > self.time and not gateways.closer_than(2, point)
                for kind, point, expiry in self.construction_reservations.values()
            )
            if count == 1 and self.structures(U.PYLON).ready:
                self._macro_reserve = 150
                if self.affordable(U.GATEWAY):
                    pylons = self.structures(U.PYLON).ready.filter(lambda p: self.safe_at(p.position))
                    if pylons:
                        await self.build_structure(
                            U.GATEWAY, pylons.closest_to(home).position, allow_pending=True
                        )
                return  # Complete parallel capacity before Core/worker/natural investment.
        if s.construction:
            for kind, prerequisite in ((U.GATEWAY, U.PYLON), (U.CYBERNETICSCORE, U.GATEWAY)):
                if (
                    not self.structures(kind)
                    and not (kind == U.GATEWAY and self.structures(U.WARPGATE))
                    and not self.already_pending(kind)
                    and self.structures(prerequisite).ready
                ):
                    self._macro_reserve = self.calculate_cost(kind).minerals
                    pylons = self.structures(U.PYLON).ready.filter(lambda p: self.safe_at(p.position))
                    # The opening can hold production while funding this tech.
                    # A crowded closest Pylon must not hide another powered site.
                    for pylon in pylons.sorted_by_distance_to(home):
                        if await self.build_structure(kind, pylon.position):
                            return
                    if self.minerals < self.calculate_cost(kind).minerals:
                        return
        # A legal first tech counter is an explicit investment, not an
        # affordability fallback. Urgent supply and depleted-income recovery
        # above retain priority; powerless/human-owned/blocked tech never locks
        # this budget. Very low worker counts retain their recovery economy.
        investment = self.first_tech_combat()
        if investment is not None and not (early_contact and completed_supply < 6):
            self._macro_reserve = self.calculate_cost(investment[1]).minerals
            self.produce(0)
            return
        if self.economic_emergency and not first_defender:
            if s.production and self.produce(0):
                return
            if s.construction and await self.construct(home, 0, army_only=True):
                return
            # A defensive response still needs income and gas to rebuild.
        worker_cap = s.max_workers
        worker_target = min(
            worker_cap, sum(base.ideal_harvesters for base in bases) + 3 * len(self.gas_buildings.ready)
        )
        if s.workers and self.supply_workers + self.already_pending(U.PROBE) < worker_target:
            for nexus in safe_bases.idle:
                if (
                    self.available(nexus)
                    and self.affordable(U.PROBE, self._opening_reserve)
                    and self.issue(nexus.train(U.PROBE), paid=True, supply=True)
                ):
                    return
        gas_limit = min(2 * len(bases), max(1, int((self.supply_workers - 12) / 8)))
        active_gases = self.gas_buildings.filter(lambda gas: not gas.is_ready or gas.vespene_contents > 0)
        if (
            s.gas
            and (self.structures(U.GATEWAY) or self.structures(U.CYBERNETICSCORE))
            and len(active_gases) < gas_limit
            and (not active_gases or self.vespene < max(300, self.minerals))
            and not self.already_pending(U.ASSIMILATOR)
        ):
            for base in safe_bases:
                for geyser in self.vespene_geyser.closer_than(10, base):
                    if geyser.vespene_contents <= 0 or self.gas_buildings.closer_than(1, geyser):
                        continue
                    worker = self.builder(geyser)
                    if (
                        worker
                        and self.affordable(U.ASSIMILATOR)
                        and self.issue(worker.build_gas(geyser), paid=True)
                    ):
                        return
        if first_defender:
            if s.construction and await self.opening_battery(home, contacts):
                return
            if (
                early_contact
                and s.construction
                and len(self.structures(U.GATEWAY) | self.structures(U.WARPGATE)) < 2
                and not self.already_pending(U.GATEWAY)
                and self.affordable(U.GATEWAY, self._opening_reserve)
            ):
                pylons = self.structures(U.PYLON).ready.filter(lambda p: self.safe_at(p.position))
                if pylons:
                    await self.build_structure(U.GATEWAY, pylons.closest_to(home).position)
            return  # Retain the defense fund; do not buy technology or a natural.
        # Get a useful opening defense before saving for a natural in auto play.
        if s.attack and s.production and self.structures(U.CYBERNETICSCORE).ready:
            fighting_supply = sum(
                self.calculate_supply_cost(u.type_id) for u in self.units if u.type_id in ARMY_TARGETS
            )
            if fighting_supply < 6 and self.produce(0):
                return
        expansion_reserve = 0
        if (
            s.expansion
            and self.townhalls.amount < base_target
            and not self.already_pending(U.NEXUS)
            and not self.economic_emergency
            and not first_defender
            and (self.strategic_plan is None or self.strategic_plan.expand)
            and (self.structures(U.GATEWAY) or self.structures(U.CYBERNETICSCORE))
            and self.supply_workers >= (16 if len(bases) == 1 else 20 * len(bases) - 2)
            and (len(bases) == 1 or not s.attack or self.supply_army >= 12)
        ):
            location = await self.safe_expansion_location(home.position)
            if location and self.builder(location):
                expansion_reserve = self._macro_reserve = 400
                if await self.build_structure(U.NEXUS, location, max_distance=2):
                    return
        # Keep idle production working. Reserve periodic opportunities for tech
        # and infrastructure, rather than starving either behind the other.
        if s.production and self.time - self._last_production >= 1 and self.produce(expansion_reserve):
            self._last_production = self.time
            return
        if (
            s.upgrades
            and not self.economic_emergency
            and self.time - self._last_upgrade >= 30
            and await self.upgrade(expansion_reserve)
        ):
            return
        if s.construction and await self.construct(
            home, expansion_reserve, army_only=self.economic_emergency
        ):
            return
        if s.production:
            self.produce(expansion_reserve)
        # Also runs in on_step after paid actions via the separate allocation clock.

    def produce_opening_defender(self):
        """A legal first force; avoid spending its Stalker gas on support units."""
        gateways = self.structures(U.GATEWAY).ready.idle.filter(
            lambda gateway: (
                gateway.is_powered
                and self.available(gateway)
                and self._blocked_producers.get(gateway.tag, 0) <= self.time
            )
        )
        if not gateways:
            return False
        kinds = [U.STALKER, U.ZEALOT] if self.structures(U.CYBERNETICSCORE).ready else [U.ZEALOT]
        for kind in kinds:
            target = production_target(self, ARMY_TARGETS[kind])
            if target <= self.units(kind).amount + self.already_pending(kind):
                continue
            if self.tech_requirement_progress(kind) < 1:
                continue
            self._opening_reserve = self.calculate_cost(kind).minerals
            if self.affordable(kind) and self.issue(gateways.first.train(kind), paid=True, supply=True):
                self._last_production = self.time
                return True
            return False  # Preserve this legal defender's budget instead of buying a Sentry.
        return False

    async def opening_battery(self, home, contacts):
        """Protected powered placements; the front Pylon need not hug the Nexus."""
        batteries = self.structures(U.SHIELDBATTERY).closer_than(14, home)
        ready = batteries.ready.filter(lambda battery: battery.is_powered)
        if ready:
            battery = ready.closest_to(home)
            if battery.distance_to(home) <= 6 + home.radius:
                anchor = battery.position.towards(home.position, min(3, battery.distance_to(home)))
                if self.in_pathing_grid(anchor) and self.is_visible(anchor):
                    self.opening_defense_anchor = tuple(anchor)
        if batteries or self.already_pending(U.SHIELDBATTERY):
            return False
        direction = contacts.closest_to(home).position if contacts else self.game_info.map_center
        hold = home.position.towards(
            self.game_info.map_center, max(8, PROFILES[self.settings.profile]["rally_distance"])
        )
        forward = self.structures(U.PYLON).ready.closest_to(hold) if self.structures(U.PYLON).ready else None
        anchors = [home.position.towards(forward.position, 3.5)] if forward else []
        anchors += [home.position.offset(offset) for offset in ((6, 0), (-6, 0), (0, 6), (0, -6))]
        anchors.sort(key=lambda point: max(point.distance_to(home), point.distance_to(hold)))
        if self.structures(U.CYBERNETICSCORE).ready and self.affordable(
            U.SHIELDBATTERY, self._opening_reserve
        ):
            for anchor in anchors:
                point = await find_spaced_placement(self, U.SHIELDBATTERY, anchor, 4)
                if (
                    point is not None
                    and self.state.psionic_matrix.covers(point)
                    and point.distance_to(home) <= 6 + home.radius
                    and self.safe_at(point)
                    and await self.build_structure(U.SHIELDBATTERY, point, max_distance=0)
                ):
                    return True
        # Protect a location before contact makes the exposed front power unusable.
        if self.settings.supply and not self.already_pending(U.PYLON):
            rear = home.position.towards(direction, -8)
            if not self.state.psionic_matrix.covers(rear) and self.affordable(U.PYLON, self._opening_reserve):
                return await self.build_structure(U.PYLON, rear, max_distance=4)
        return False

    async def build_supply_pylons(self, anchors, target):
        if self.already_pending(U.PYLON) >= target:
            return False
        for anchor in anchors:
            if await self.build_structure(U.PYLON, anchor, max_distance=18, allow_pending=True):
                return True
        return False

    async def construct(self, home, reserve, army_only=False):
        s = self.settings
        targets = composition_targets(self)
        bases = self.townhalls.ready.amount
        gateway_target = min(10, max(1, 2 * bases - 1) + int(self.minerals >= 700))
        opening_defense = army_only and self.time < 360 and self.supply_army < 12
        if opening_defense:
            gateway_target = max(2, gateway_target)
        pylons = self.structures(U.PYLON).ready.filter(lambda p: self.safe_at(p.position))
        if not pylons:
            return False
        anchors = [p.position for p in pylons.sorted_by_distance_to(home)]
        plan = [
            (U.GATEWAY, 1, U.PYLON),
            (U.CYBERNETICSCORE, 1, U.GATEWAY),
            (
                U.ROBOTICSFACILITY,
                int(
                    targets["immortals"] > 0
                    or targets["colossi"] > 0
                    or (s.attack and (s.scouting or s.warp_reinforcement))
                )
                + int(targets["immortals"] + targets["colossi"] >= 8 and bases >= 3),
                U.CYBERNETICSCORE,
            ),
            (U.STARGATE, min(3, (targets["voidrays"] + 5) // 6, bases), U.CYBERNETICSCORE),
            (U.GATEWAY, gateway_target, U.CYBERNETICSCORE),
            (U.ROBOTICSBAY, int(targets["colossi"] > 0), U.ROBOTICSFACILITY),
            (
                U.TWILIGHTCOUNCIL,
                int(s.blink or targets["high_templar"] > 0 or (s.upgrades and self.supply_army >= 20)),
                U.CYBERNETICSCORE,
            ),
            (U.TEMPLARARCHIVE, int(targets["high_templar"] > 0), U.TWILIGHTCOUNCIL),
            (
                U.FORGE,
                int(s.upgrades and self.supply_army >= 12) * (1 + int(self.supply_army >= 60)),
                U.CYBERNETICSCORE,
            ),
            (
                U.FLEETBEACON,
                int(targets["voidrays"] > 0 and s.upgrades and self.supply_army >= 60),
                U.STARGATE,
            ),
        ]
        if opening_defense:
            # Add affordable parallel defenders before new expensive tech.
            plan.insert(2, (U.GATEWAY, gateway_target, U.CYBERNETICSCORE))
        for kind, target, prerequisite in plan:
            if opening_defense and kind in {U.ROBOTICSFACILITY, U.STARGATE}:
                continue
            if army_only and kind not in {U.GATEWAY, U.ROBOTICSFACILITY, U.STARGATE}:
                continue
            count = self.structures(kind).amount
            if kind == U.GATEWAY:
                count += self.structures(U.WARPGATE).amount
            if count >= target or self.already_pending(kind) or not self.structures(prerequisite).ready:
                continue
            if self.affordable(kind, reserve):
                for near in anchors:
                    if await self.build_structure(kind, near):
                        return True
        return await self.build_base_battery(reserve)

    async def build_base_battery(self, reserve):
        if not self.structures(U.CYBERNETICSCORE).ready or not self.affordable(U.SHIELDBATTERY, reserve):
            return False
        for base in self.townhalls.ready:
            if self.structures(U.SHIELDBATTERY).closer_than(10, base):
                continue
            local_pylons = self.structures(U.PYLON).ready.filter(
                lambda pylon, base=base: pylon.distance_to(base) < 5 and self.safe_at(pylon.position, 10)
            )
            if local_pylons and await self.build_structure(
                U.SHIELDBATTERY, local_pylons.closest_to(base).position, max_distance=6
            ):
                return True
        return False

    def first_tech_combat(self):
        """Choose an attainable first combat milestone; queued orders are not effects."""
        self._first_tech_reservation = None
        if not (self.settings.enabled and self.settings.attack and self.settings.production):
            return None
        seen = getattr(self, "_first_tech_combat_seen", set())
        for kind in (U.STALKER, U.IMMORTAL, U.OBSERVER):
            if self.units(kind):
                seen.add(kind)
        self._first_tech_combat_seen = seen
        if self.supply_workers < 12:
            return None
        if (
            self.economic_emergency
            and sum(
                self.calculate_supply_cost(u.type_id)
                for u in self.units.of_type(set(ARMY_TARGETS)).ready
                if u.can_attack
            )
            < 6
        ):
            return None
        choices = [(U.GATEWAY, U.STALKER)]
        if self.settings.scouting and production_target(self, "observers") > 0 and U.OBSERVER not in seen:
            choices.append((U.ROBOTICSFACILITY, U.OBSERVER))
        choices.append((U.ROBOTICSFACILITY, U.IMMORTAL))
        for producer, kind in choices:
            if (
                kind in seen
                or self.already_pending(kind)
                or production_target(self, PRODUCTION_TARGETS[kind]) <= 0
            ):
                continue
            prerequisite = U.CYBERNETICSCORE if kind == U.STALKER else U.ROBOTICSFACILITY
            if not self.structures(prerequisite).ready or self.tech_requirement_progress(kind) < 1:
                continue
            buildings = self.structures(producer).ready.idle.filter(
                lambda b: (
                    b.is_powered and self.available(b) and self._blocked_producers.get(b.tag, 0) <= self.time
                )
            )
            if not buildings or self.supply_left < self.calculate_supply_cost(kind):
                continue
            cost = self.calculate_cost(kind)
            # Do not mortgage minerals/gas that cannot currently be earned.
            # Allocation and replacement gas must be allowed to establish income.
            mineral_need = cost.minerals + self.settings.reserve_minerals
            gas_need = cost.vespene + self.settings.reserve_gas
            if self.minerals < mineral_need and not any(
                b.ideal_harvesters > 0 and b.assigned_harvesters > 0 for b in self.townhalls.ready
            ):
                continue
            if self.vespene < gas_need and not (
                self.settings.gas
                and any(
                    g.vespene_contents > 0 and g.assigned_harvesters > 0 for g in self.gas_buildings.ready
                )
            ):
                continue
            self._first_tech_reservation = (kind, cost.vespene)
            return buildings.first, kind
        return None

    def produce(self, reserve):
        investment = self.first_tech_combat()
        if investment is not None:
            building, kind = investment
            self._macro_reserve = max(getattr(self, "_macro_reserve", 0), self.calculate_cost(kind).minerals)
            if self.affordable(kind, reserve) and self.issue(building.train(kind), paid=True, supply=True):
                self._last_production = self.time
                return True
            return False
        producers = list(PRODUCERS.items())
        order = producers[self._production_cursor :] + producers[: self._production_cursor]
        for producer, kinds in order:
            candidates = [
                kind
                for kind in kinds
                if (kind != U.WARPPRISM or (self.settings.attack and self.settings.warp_reinforcement))
                and (kind != U.OBSERVER or self.settings.scouting)
                and not (self.economic_emergency and kind == U.WARPPRISM and self.supply_army < 20)
                and production_target(self, PRODUCTION_TARGETS[kind]) > 0
                and self.units(kind).amount
                + self.already_pending(kind)
                + (self.units(U.WARPPRISMPHASING).amount if kind == U.WARPPRISM else 0)
                < production_target(self, PRODUCTION_TARGETS[kind])
            ]
            candidates.sort(
                key=lambda kind: (
                    (self.units(kind).amount + self.already_pending(kind))
                    / production_target(self, PRODUCTION_TARGETS[kind])
                )
            )
            for building in self.structures(producer).ready.idle:
                if (
                    self._blocked_producers.get(building.tag, 0) > self.time
                    or not building.is_powered
                    or not self.available(building)
                ):
                    continue
                for kind in candidates:
                    if self.tech_requirement_progress(kind) < 1 or not self.affordable(kind, reserve):
                        continue
                    if self.issue(building.train(kind), paid=True, supply=True):
                        self._last_production = self.time
                        self._production_cursor = (list(PRODUCERS).index(producer) + 1) % len(PRODUCERS)
                        return True
        return False

    async def upgrade(self, reserve):
        plan = []
        if self.settings.storm:
            plan.append((G.PSISTORMTECH, U.TEMPLARARCHIVE))
        if self.settings.blink:
            plan.append((G.BLINKTECH, U.TWILIGHTCOUNCIL))
        if self.settings.attack and self.settings.warp_reinforcement:
            plan.append((G.WARPGATERESEARCH, U.CYBERNETICSCORE))
        if production_target(self, "colossi") and self.units(U.COLOSSUS):
            plan.append((G.EXTENDEDTHERMALLANCE, U.ROBOTICSBAY))
        if (
            self.settings.attack
            and production_target(self, "zealots") >= 8
            and self.units(U.ZEALOT).amount >= 4
        ):
            plan.append((G.CHARGE, U.TWILIGHTCOUNCIL))
        if production_target(self, "voidrays"):
            plan += [(upgrade, U.CYBERNETICSCORE) for upgrade in AIR_UPGRADES]
        plan += [(upgrade, U.FORGE) for upgrade in GROUND_UPGRADES]
        for upgrade, kind in plan:
            if self.already_pending_upgrade(upgrade) or not self.affordable(upgrade, reserve):
                continue
            for building in self.structures(kind).ready.idle:
                if not building.is_powered or not self.available(building):
                    continue
                if upgrade.value not in self.game_data.upgrades:
                    continue
                ability = self.game_data.upgrades[upgrade.value].research_ability.id
                available = await self.get_available_abilities(building)
                # Query replies may use exact research IDs while game data uses
                # a generic research-family remap. Compare the same namespace.
                available = {self.game_data.abilities[a.value].id for a in available if a.value}
                if ability in available and self.issue(building.research(upgrade), paid=True):
                    self._last_upgrade = self.time
                    logger.info("Research queued: {} at {}", upgrade.name, building.tag)
                    return True
        return False

    async def powers(self):
        if self.settings.chrono:
            await self.chrono()
        s = self.settings
        types = set()
        if s.blink:
            types.add(U.STALKER)
        if s.storm or s.feedback:
            types.add(U.HIGHTEMPLAR)
        if s.guardian_shield:
            types.add(U.SENTRY)
        if s.voidray_alignment:
            types.add(U.VOIDRAY)
        if not types:
            return
        units = self.units.of_type(types).filter(
            lambda unit: (
                self.available(unit)
                and self.time - self._casts.get(unit.tag, -100) >= 1
                and not any(order.ability.id in SPELLS for order in unit.orders)
            )
        )
        if not units:
            return
        abilities = await self.get_available_abilities(units)
        enemies = self.enemy_units.filter(lambda unit: unit.is_visible and unit.can_be_attacked)
        self._storms = [(time, point) for time, point in self._storms if self.time - time < 3]
        shield_active = any(unit.has_buff(BuffId.GUARDIANSHIELD) for unit in self.units)
        feedback_targets = set()
        for unit, available in zip(units, abilities, strict=True):
            command = None
            if unit.type_id == U.HIGHTEMPLAR:
                if s.storm and A.PSISTORM_PSISTORM in available:
                    target = storm_target(
                        unit, enemies, self.all_own_units, [point for _, point in self._storms]
                    )
                    if target is not None:
                        command = unit(A.PSISTORM_PSISTORM, target)
                if command is None and s.feedback and A.FEEDBACK_FEEDBACK in available:
                    targets = enemies.filter(
                        lambda enemy, unit=unit: (
                            enemy.energy >= 50
                            and unit.distance_to(enemy) <= 9
                            and enemy.tag not in feedback_targets
                        )
                    )
                    if targets:
                        command = unit(A.FEEDBACK_FEEDBACK, max(targets, key=lambda enemy: enemy.energy))
            elif (
                unit.type_id == U.SENTRY
                and s.guardian_shield
                and not shield_active
                and A.GUARDIANSHIELD_GUARDIANSHIELD in available
            ):
                threats = enemies.filter(
                    lambda enemy, unit=unit: (
                        enemy.can_attack and enemy.ground_range > 1 and enemy.distance_to(unit) <= 8
                    )
                )
                allies = self.units.filter(
                    lambda ally, unit=unit: (
                        not ally.is_flying and ally.can_attack and ally.distance_to(unit) <= 4.5
                    )
                )
                if threats and len(allies) >= 3:
                    command = unit(A.GUARDIANSHIELD_GUARDIANSHIELD)
            elif (
                unit.type_id == U.STALKER
                and s.blink
                and A.EFFECT_BLINK_STALKER in available
                and unit.shield_percentage <= 0.1
                and unit.health_percentage <= 0.65
            ):
                threats = enemies.filter(
                    lambda enemy, unit=unit: enemy.can_attack_ground and enemy.distance_to(unit) <= 6
                )
                if threats and self.townhalls.ready:
                    home = self.townhalls.ready.closest_to(unit)
                    target = unit.position.towards(home.position, min(6, unit.distance_to(home)))
                    if (
                        unit.distance_to(target) > 1
                        and self.in_pathing_grid(target)
                        and self.is_visible(target)
                        and min(enemy.distance_to(target) for enemy in threats)
                        > min(enemy.distance_to(unit) for enemy in threats)
                    ):
                        command = unit(A.EFFECT_BLINK_STALKER, target)
            elif (
                unit.type_id == U.VOIDRAY
                and s.voidray_alignment
                and A.EFFECT_VOIDRAYPRISMATICALIGNMENT in available
            ):
                if unit.is_attacking and any(
                    enemy.is_armored and unit.target_in_range(enemy) for enemy in enemies
                ):
                    command = unit(A.EFFECT_VOIDRAYPRISMATICALIGNMENT)
            if command is not None and self.issue(command):
                self._casts[unit.tag] = self.time
                if command.ability == A.PSISTORM_PSISTORM:
                    self._storms.append((self.time, command.target))
                if command.ability == A.GUARDIANSHIELD_GUARDIANSHIELD:
                    shield_active = True
                if command.ability == A.FEEDBACK_FEEDBACK:
                    feedback_targets.add(command.target.tag)

    async def chrono(self):
        targets = self.structures.ready.filter(
            lambda building: (
                not building.is_idle
                and not building.has_buff(BuffId.CHRONOBOOSTENERGYCOST)
                and self.control.eligible(building)
            )
        )
        if not targets:
            return
        for nexus in self.townhalls.ready:
            if not self.available(nexus):
                continue
            if A.EFFECT_CHRONOBOOSTENERGYCOST in await self.get_available_abilities(nexus):
                # One cast per observation avoids duplicate Chrono on a stale target.
                self.issue(nexus(A.EFFECT_CHRONOBOOSTENERGYCOST, targets.first))
                return
