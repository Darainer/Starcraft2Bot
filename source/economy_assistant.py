"""Protoss economy and abilities; tactical orders live in the separate controller."""

from loguru import logger
from sc2.bot_ai import BotAI
from sc2.ids.ability_id import AbilityId as A
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G
from sc2.unit_command import UnitCommand

from source.assistant_control import Control, within_budget
from source.layout import find_spaced_placement

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
    U.ROBOTICSFACILITY: (U.IMMORTAL, U.COLOSSUS),
    U.STARGATE: (U.VOIDRAY,),
}
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

    @property
    def settings(self):
        return self.control.settings

    async def on_start(self):
        await self.chat_send(
            "Assistant ready. Type !assist help; !assist attack off returns army control", team_only=True
        )

    def available(self, unit):
        return unit.tag not in self._used and self.control.eligible(unit)

    def issue(self, command, paid=False, supply=False):
        if not isinstance(command, UnitCommand) or not self.available(command.unit):
            return False
        accepted = self.do(command, subtract_cost=paid, subtract_supply=supply, can_afford_check=paid)
        if accepted:
            self._used.add(command.unit.tag)
        return accepted

    def affordable(self, item, extra_minerals=0):
        cost = self.calculate_cost(item)
        return self.can_afford(item) and within_budget(
            self.minerals, self.vespene, cost.minerals, cost.vespene, self.settings, extra_minerals
        )

    async def on_step(self, iteration):
        self._used.clear()
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
            if error.result == 41:
                self._blocked_producers[error.unit_tag] = self.time + 15
            logger.warning(
                "SC2 rejected action: unit={} ability={} result={}",
                error.unit_tag,
                error.ability_id,
                error.result,
            )
        if self.settings.enabled:
            if self.time - self._last_macro >= 0.5:
                self._last_macro = self.time
                await self.macro()
            await self.powers()
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

    def safe_at(self, point, radius=18):
        return not any(
            enemy.can_attack and enemy.distance_to(point) < radius
            for enemy in self.enemy_units
            if enemy.is_visible
        )

    def builder(self, point):
        workers = self.workers.filter(lambda w: self.available(w) and (w.is_idle or w.is_gathering))
        return workers.closest_to(point) if workers else None

    async def build_structure(self, kind, near, max_distance=12):
        if self.already_pending(kind) or not self.affordable(kind):
            return False
        worker = self.builder(near)
        if worker is None:
            return False
        placement = await find_spaced_placement(self, kind, near, max_distance)
        if placement is None or not self.safe_at(placement):
            return False
        return self.issue(worker.build(kind, placement), paid=True)

    async def allocate_workers(self):
        """Only idle/gathering probes; never pull a scouting, fighting or building probe."""
        bases = self.townhalls.ready.filter(lambda base: self.safe_at(base.position))
        if not bases:
            return
        gases = self.gas_buildings.ready.filter(
            lambda gas: gas.vespene_contents > 0 and self.safe_at(gas.position)
        )
        gas_need = {gas.tag: max(0, gas.ideal_harvesters - gas.assigned_harvesters) for gas in gases}
        base_need = {base.tag: max(0, base.ideal_harvesters - base.assigned_harvesters) for base in bases}
        excess = {
            unit.tag: max(0, unit.assigned_harvesters - unit.ideal_harvesters)
            for unit in self.townhalls.ready | self.gas_buildings.ready
        }
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
                if base is None and worker.is_idle:
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
        bases = self.townhalls.ready
        if not bases:
            if s.expansion and not self.townhalls and self.workers:
                await self.build_structure(U.NEXUS, self.start_location, max_distance=2)
            return
        home = bases.closest_to(self.start_location)
        safe_bases = bases.filter(lambda base: self.safe_at(base.position))
        if not safe_bases:
            return
        home = safe_bases.closest_to(home)
        # Spending/building first prevents allocation from claiming every idle builder.
        if s.supply and self.supply_cap < 200 and self.supply_left < max(5, len(bases) * 3):
            if await self.build_structure(U.PYLON, home.position.towards(self.game_info.map_center, 5)):
                return
            if not self.already_pending(U.PYLON) and not self.affordable(U.PYLON):
                return  # Save for supply instead of repeatedly spending on probes.
        worker_target = min(
            s.max_workers, sum(base.ideal_harvesters for base in bases) + 3 * len(self.gas_buildings.ready)
        )
        if s.workers and self.supply_workers + self.already_pending(U.PROBE) < worker_target:
            for nexus in safe_bases.idle:
                if (
                    self.available(nexus)
                    and self.affordable(U.PROBE)
                    and self.issue(nexus.train(U.PROBE), paid=True, supply=True)
                ):
                    return
        if s.gas and self.structures(U.CYBERNETICSCORE) and not self.already_pending(U.ASSIMILATOR):
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
        expansion_reserve = 0
        if (
            s.expansion
            and self.townhalls.amount < s.bases
            and not self.already_pending(U.NEXUS)
            and self.supply_workers >= 16 * len(bases)
            and self.structures(U.CYBERNETICSCORE).ready
        ):
            location = await self.get_next_expansion()
            if location and self.safe_at(location, 22) and self.builder(location):
                expansion_reserve = 400
                if await self.build_structure(U.NEXUS, location, max_distance=2):
                    return
        # Periodically give research priority over additional production buildings.
        # Worker/supply emergencies and explicit reserves still take precedence.
        if s.upgrades and self.time - self._last_upgrade >= 30 and await self.upgrade(expansion_reserve):
            return
        if s.construction and await self.construct(home, expansion_reserve):
            return
        if s.upgrades and await self.upgrade(expansion_reserve):
            return
        if s.production and self.produce(expansion_reserve):
            return
        # Also runs in on_step after paid actions via the separate allocation clock.

    async def construct(self, home, reserve):
        s = self.settings
        pylons = self.structures(U.PYLON).ready.filter(lambda p: self.safe_at(p.position))
        if not pylons:
            return False
        near = pylons.closest_to(home).position
        plan = [
            (U.GATEWAY, 1, U.PYLON),
            (U.CYBERNETICSCORE, 1, U.GATEWAY),
            (U.ROBOTICSFACILITY, int(s.immortals > 0 or s.colossi > 0), U.CYBERNETICSCORE),
            (U.FORGE, int(s.upgrades), U.CYBERNETICSCORE),
            (U.TWILIGHTCOUNCIL, int(s.upgrades or s.blink or s.high_templar > 0), U.CYBERNETICSCORE),
            (U.TEMPLARARCHIVE, int(s.high_templar > 0), U.TWILIGHTCOUNCIL),
            (U.ROBOTICSBAY, int(s.colossi > 0), U.ROBOTICSFACILITY),
            (U.STARGATE, int(s.voidrays > 0), U.CYBERNETICSCORE),
            (U.FLEETBEACON, int(s.voidrays > 0 and s.upgrades), U.STARGATE),
            (U.GATEWAY, min(6, 2 * self.townhalls.ready.amount), U.CYBERNETICSCORE),
        ]
        for kind, target, prerequisite in plan:
            count = self.structures(kind).amount
            if kind == U.GATEWAY:
                count += self.structures(U.WARPGATE).amount
            if count >= target or self.already_pending(kind) or not self.structures(prerequisite).ready:
                continue
            if self.affordable(kind, reserve) and await self.build_structure(kind, near):
                return True
        return False

    def produce(self, reserve):
        for producer, kinds in PRODUCERS.items():
            candidates = [
                kind
                for kind in kinds
                if getattr(self.settings, ARMY_TARGETS[kind]) > 0
                and self.units(kind).amount + self.already_pending(kind)
                < getattr(self.settings, ARMY_TARGETS[kind])
            ]
            candidates.sort(
                key=lambda kind: (
                    (self.units(kind).amount + self.already_pending(kind))
                    / getattr(self.settings, ARMY_TARGETS[kind])
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
                        return True
        return False

    async def upgrade(self, reserve):
        plan = []
        if self.settings.storm:
            plan.append((G.PSISTORMTECH, U.TEMPLARARCHIVE))
        if self.settings.blink:
            plan.append((G.BLINKTECH, U.TWILIGHTCOUNCIL))
        if self.settings.voidrays:
            plan += [(upgrade, U.CYBERNETICSCORE) for upgrade in AIR_UPGRADES]
        plan += [(upgrade, U.FORGE) for upgrade in GROUND_UPGRADES]
        for upgrade, kind in plan:
            if self.already_pending_upgrade(upgrade) or not self.affordable(upgrade, reserve):
                continue
            for building in self.structures(kind).ready.idle:
                if not building.is_powered or not self.available(building):
                    continue
                ability = self.game_data.upgrades[upgrade.value].research_ability.id
                if ability in await self.get_available_abilities(building) and self.issue(
                    building.research(upgrade), paid=True
                ):
                    self._last_upgrade = self.time
                    logger.info("Research queued: {} at {}", upgrade.name, building.tag)
                    return True
        return False

    async def powers(self):
        # Allocation has its own clock and runs even when macro() bought something.
        if self.settings.allocation and self.time - self._last_allocation >= 3:
            self._last_allocation = self.time
            await self.allocate_workers()
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
