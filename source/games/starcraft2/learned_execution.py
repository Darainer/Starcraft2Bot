"""Versioned fixed skills for the independent learned controller.

Available abilities, affordability and permissions constrain macro choices;
attack strength, opening scripts and profile spending priorities do not.
Placement and actor selection can still fail after sampling and are recorded.
"""

from dataclasses import replace

from sc2.dicts.unit_research_abilities import RESEARCH_INFO
from sc2.dicts.unit_train_build_abilities import TRAIN_INFO
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as G

from source.action_intents import ActionIntent
from source.economy_assistant import ARMY_TARGETS
from source.games.starcraft2.learned_actions import FEATURE_VERSION, MACRO_ACTIONS
from source.layout import find_spaced_placement
from source.strategy_core.contracts import Feature
from source.tactics import TacticalController

# (command family, live game-data item, actor type). The catalog order is frozen
# in learned_actions; these are mechanical commands, not build-order templates.
SPECS = {
    "probe": ("train", U.PROBE, U.NEXUS),
    "pylon": ("build", U.PYLON, U.PROBE),
    "assimilator": ("build", U.ASSIMILATOR, U.PROBE),
    "nexus": ("build", U.NEXUS, U.PROBE),
    "gateway": ("build", U.GATEWAY, U.PROBE),
    "cybernetics_core": ("build", U.CYBERNETICSCORE, U.PROBE),
    "robotics_facility": ("build", U.ROBOTICSFACILITY, U.PROBE),
    "robotics_bay": ("build", U.ROBOTICSBAY, U.PROBE),
    "stargate": ("build", U.STARGATE, U.PROBE),
    "forge": ("build", U.FORGE, U.PROBE),
    "twilight_council": ("build", U.TWILIGHTCOUNCIL, U.PROBE),
    "templar_archive": ("build", U.TEMPLARARCHIVE, U.PROBE),
    "zealot": ("train", U.ZEALOT, U.GATEWAY),
    "stalker": ("train", U.STALKER, U.GATEWAY),
    "sentry": ("train", U.SENTRY, U.GATEWAY),
    "immortal": ("train", U.IMMORTAL, U.ROBOTICSFACILITY),
    "colossus": ("train", U.COLOSSUS, U.ROBOTICSFACILITY),
    "voidray": ("train", U.VOIDRAY, U.STARGATE),
    "high_templar": ("train", U.HIGHTEMPLAR, U.GATEWAY),
    "observer": ("train", U.OBSERVER, U.ROBOTICSFACILITY),
    "ground_weapons_1": ("research", G.PROTOSSGROUNDWEAPONSLEVEL1, U.FORGE),
    "ground_armor_1": ("research", G.PROTOSSGROUNDARMORSLEVEL1, U.FORGE),
    "shields_1": ("research", G.PROTOSSSHIELDSLEVEL1, U.FORGE),
    "air_weapons_1": ("research", G.PROTOSSAIRWEAPONSLEVEL1, U.CYBERNETICSCORE),
    "air_armor_1": ("research", G.PROTOSSAIRARMORSLEVEL1, U.CYBERNETICSCORE),
    "blink": ("research", G.BLINKTECH, U.TWILIGHTCOUNCIL),
    "charge": ("research", G.CHARGE, U.TWILIGHTCOUNCIL),
    "thermal_lance": ("research", G.EXTENDEDTHERMALLANCE, U.ROBOTICSBAY),
    "storm": ("research", G.PSISTORMTECH, U.TEMPLARARCHIVE),
}
ECONOMY_FEATURES = ("own.supply_remaining", "own.supply_capacity", "intent.gas_staffing") + tuple(
    f"macro.{name}.{field}" for name in MACRO_ACTIONS for field in ("available", "completed", "pending")
)


class MacroSkill:
    def __init__(self):
        self.abilities = {}
        self.choice = 0
        self.consumed = True
        self.gas_staffing = 0
        self.feedback = []

    async def refresh(self, bot):
        actors = [
            u
            for u in bot.all_own_units
            if bot.available(u)
            and u.is_ready
            and (
                (u.type_id == U.PROBE and (u.is_idle or u.is_gathering))
                or (u.type_id in {spec[2] for spec in SPECS.values()} and u.is_idle)
            )
        ]
        available = (
            await bot.get_available_abilities(actors, ignore_resource_requirements=True) if actors else []
        )
        if len(available) != len(actors):
            raise ValueError("Incomplete live macro ability query")
        self.abilities = {u.tag: frozenset(values) for u, values in zip(actors, available, strict=True)}

    def actors(self, bot, name):
        family, item, actor_type = SPECS[name]
        ability = (RESEARCH_INFO if family == "research" else TRAIN_INFO)[actor_type][item]["ability"]
        return [
            u
            for u in bot.all_own_units
            if u.type_id == actor_type
            and u.is_ready
            and bot.available(u)
            and ability in self.abilities.get(u.tag, ())
            and ((u.is_idle or u.is_gathering) if family == "build" else u.is_idle)
        ]

    def geysers(self, bot):
        return [
            g
            for g in bot.vespene_geyser
            if g.vespene_contents > 0
            and bot.townhalls.ready.closer_than(12, g)
            and not bot.gas_buildings.closer_than(1, g)
        ]

    def allowed(self, bot, name):
        if name == "wait":
            return True
        family, item, _ = SPECS[name]
        s = bot.settings
        permission = (
            s.upgrades
            if family == "research"
            else s.workers
            if item == U.PROBE
            else s.supply
            if item == U.PYLON
            else s.gas and s.construction
            if item == U.ASSIMILATOR
            else s.expansion and s.construction
            if item == U.NEXUS
            else s.construction
            if family == "build"
            else s.production
        )
        if not s.enabled or not permission or not bot.affordable(item) or not self.actors(bot, name):
            return False
        if family == "research":
            return item not in bot.state.upgrades and not bot.already_pending_upgrade(item)
        if family == "train":
            return bot.can_feed(item)
        if item == U.ASSIMILATOR:
            return bool(self.geysers(bot))
        if item == U.NEXUS:
            return any(not bot.townhalls.closer_than(10, p) for p in bot.expansion_locations_list)
        return True

    def observe(self, bot, belief):
        mask = tuple(bool(self.allowed(bot, name)) for name in MACRO_ACTIONS)
        values = {
            "own.supply_remaining": bot.supply_left / 200,
            "own.supply_capacity": bot.supply_cap / 200,
            "intent.gas_staffing": self.gas_staffing / 3,
        }
        for name, allowed in zip(MACRO_ACTIONS, mask, strict=True):
            complete = pending = 0
            if name in SPECS:
                family, item, _ = SPECS[name]
                if family == "research":
                    complete, pending = int(item in bot.state.upgrades), bot.already_pending_upgrade(item)
                else:
                    complete = len(bot.all_own_units.of_type({item}).ready)
                    pending = bot.already_pending(item)
            values.update(
                {
                    f"macro.{name}.available": float(allowed),
                    f"macro.{name}.completed": complete / 20,
                    f"macro.{name}.pending": pending / 20,
                }
            )
        return replace(
            belief,
            macro_mask=mask,
            shared=replace(
                belief.shared,
                feature_version=FEATURE_VERSION,
                features=belief.shared.features
                + tuple(Feature(n, v, "fraction", 0, 0) for n, v in values.items()),
                capabilities=belief.shared.capabilities
                + (("resource_allocation", bool(bot.settings.enabled and bot.settings.allocation)),),
            ),
        )

    def propose(self, decoded):
        sample = decoded.sampled
        self.choice = sample.action.macro
        self.consumed = bool(decoded.override_reasons)
        if not decoded.override_reasons and decoded.execution_masks.active[3]:
            self.gas_staffing = sample.action.gas
        elif decoded.override_reasons and self.choice:
            self.feedback.append({"action": MACRO_ACTIONS[self.choice], "status": "decoder_rejected"})

    async def execute(self, bot):
        if self.consumed:
            return
        self.consumed = True  # one attempt per sampled decision, never an automatic retry/build order
        name = MACRO_ACTIONS[self.choice]
        accepted = False
        status = "wait" if not self.choice else "no_longer_available"
        if self.choice and not bot._paid_action_issued and self.allowed(bot, name):
            family, item, _ = SPECS[name]
            actors = self.actors(bot, name)
            if family == "train":
                accepted = bot.issue(actors[0].train(item), paid=True, supply=True)
            elif family == "research":
                accepted = bot.issue(actors[0].research(item), paid=True)
            else:
                home = (
                    bot.townhalls.closest_to(bot.start_location).position
                    if bot.townhalls
                    else bot.start_location
                )
                if item == U.ASSIMILATOR:
                    target = min(self.geysers(bot), key=home.distance_to)
                    actor = min(actors, key=lambda u: u.distance_to(target))
                    accepted = bot.issue(actor.build_gas(target), paid=True)
                else:
                    near = (
                        await bot.get_next_expansion()
                        if item == U.NEXUS
                        else home.towards(bot.game_info.map_center, 6)
                    )
                    if item not in {U.NEXUS, U.PYLON}:
                        pylons = bot.structures(U.PYLON).ready
                        near = pylons.closest_to(home).position if pylons else None
                    point = (
                        (near if item == U.NEXUS else await find_spaced_placement(bot, item, near, 20))
                        if near is not None
                        else None
                    )
                    if point is not None:
                        for actor in sorted(actors, key=lambda u: u.distance_to(point))[:4]:
                            if actor.distance_to(point) >= 3 and not await bot.client.query_pathing(
                                actor, point
                            ):
                                continue
                            if bot.issue(actor.build(item, point), paid=True):
                                bot.construction_reservations[actor.tag] = (item, point, bot.time + 45)
                                accepted = True
                                break
            status = "queued" if accepted else "execution_failed"
        self.feedback.append({"action": name, "status": status, "time": bot.time})

    async def allocate(self, bot):
        # The actor owns gas staffing. Fixed routing preserves human ownership,
        # carrying workers and builders; it does not impose an economy priority.
        gases = bot.gas_buildings.ready.filter(lambda g: g.vespene_contents > 0)
        counts = {g.tag: g.assigned_harvesters for g in gases}
        minerals = bot.mineral_field.filter(
            lambda m: m.mineral_contents > 0 and bot.townhalls.ready.closer_than(10, m)
        )
        for worker in bot.workers:
            if (
                not bot.available(worker)
                or not (worker.is_idle or worker.is_gathering)
                or worker.is_carrying_resource
            ):
                continue
            origin = worker.order_target if worker.is_gathering else None
            if origin in counts and counts[origin] <= self.gas_staffing:
                continue
            needs = [g for g in gases if counts[g.tag] < self.gas_staffing]
            destination = min(needs, key=worker.distance_to) if needs else None
            if destination is None and minerals and (worker.is_idle or origin in counts):
                destination = minerals.closest_to(worker)
            if destination is not None and bot.issue(worker.gather(destination)):
                if origin in counts:
                    counts[origin] -= 1
                if destination.tag in counts:
                    counts[destination.tag] += 1


class LearnedTactics(TacticalController):
    """Direct model movement plus existing opt-in unit micro; no mission abort policy."""

    def tick(self, bot, observation=None, available_abilities=None):
        army = bot.units.of_type(set(ARMY_TARGETS)).ready.filter(bot.control.eligible)
        state = replace(
            self.assessor.observe(bot, army),
            response_policy="baseline",
            response_policy_until=0,
            response_evidence=(),
            response_reason="Learned strategy/economy controller",
        )
        self.last_assessment = state
        if self.director.active is None or bot.time - self._last_director >= 2:
            self.director.decide(state)
            self._last_director = bot.time
        plan = self.director.active
        bot.strategic_plan = plan
        decoded = bot.last_decoded
        intent = decoded.sampled.action.intent if not decoded.override_reasons else 0
        self.active_mode = "push" if intent == 2 else "regroup"
        self._micro_allowed = intent == 2
        self._automatic_recovery = False
        executor = self.missions.executor
        executor.assign({u.tag: "learned-main" for u in army} if intent else {})
        orders = []
        if intent and bot.settings.enabled and bot.settings.attack:
            for unit in army:
                revision = executor.assignments[unit.tag][1]
                command = ActionIntent(
                    unit.tag,
                    revision,
                    bot.state.game_loop,
                    bot.state.game_loop,
                    "attack" if intent == 2 else "move",
                    plan.missions[0].target,
                )
                if executor.execute(bot, command):
                    orders.append(unit.tag)
        return {
            "strategy": self.active_mode,
            "reason": plan.reason,
            "orders": orders,
            "assessment": state.to_dict(),
            "plan": plan.to_dict(),
            "decision_history": list(self.director.history),
            "wave": {"phase": "learned"},
        }


class DisabledReinforcement:
    """The independent catalog uses gateways; no second controller may spend."""

    last_report = {"phase": "disabled_for_learned_policy"}

    async def tick(self, *args, **kwargs):
        pass

    def reject(self, *args):
        pass
