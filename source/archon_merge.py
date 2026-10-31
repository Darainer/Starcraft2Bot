"""Reserve safe inputs, rendezvous, then merge exactly one pair per observation."""

from collections import deque

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.position import Point2

from source.combat_assessment import visible_threats
from source.composition import (
    MERGE_ORDERS,
    archon_committed,
    archon_permitted,
    merging_templar,
    planned_target,
)


class ArchonMerge:
    def __init__(self):
        self.pending = {}
        self.rendezvous = {}
        self.history = deque(maxlen=128)
        self.retry_at = -999
        self.issued_loop = None

    async def tick(self, bot):
        templars = bot.units(U.HIGHTEMPLAR).ready
        errors = {
            error.unit_tag
            for error in bot.state.action_errors
            if error.ability_id in {a.value for a in MERGE_ORDERS}
        }
        events = []
        for pair, record in list(self.pending.items()):
            reason = None
            if errors.intersection(pair):
                reason = "engine_rejected_merge"
                self.retry_at = bot.time + 10
            elif any(tag not in templars.tags for tag in pair):
                reason = "source_transformed_or_disappeared"
            elif any(not bot.control.eligible(templars.find_by_tag(tag)) for tag in pair):
                reason = "ownership_revoked"
            elif bot.time >= record["until"]:
                reason = "merge_reservation_expired"
                self.retry_at = bot.time + 10
            if reason:
                events.append({"pair": list(pair), "result": reason})
                del self.pending[pair]
        enabled = archon_permitted(bot)
        target = planned_target(bot, "archons") if enabled else 0
        contacts = visible_threats(bot)
        for pair, record in list(self.rendezvous.items()):
            actors = [templars.find_by_tag(tag) for tag in pair]
            reason = None
            if not enabled or target <= bot.units(U.ARCHON).ready.amount + len(self.pending):
                reason = "rendezvous_goal_withdrawn"
            elif any(unit is None for unit in actors):
                reason = "rendezvous_source_disappeared"
            elif any(not bot.control.eligible(unit) for unit in actors):
                reason = "rendezvous_ownership_revoked"
            elif bot.time >= record["until"]:
                reason = "rendezvous_expired"
            elif contacts.closer_than(12, Point2(record["point"])) or any(
                contacts.closer_than(12, unit)
                or unit.health + unit.shield < (unit.health_max + unit.shield_max) * 0.5
                for unit in actors
            ):
                reason = "rendezvous_became_unsafe"
            if reason:
                del self.rendezvous[pair]
                self.retry_at = max(self.retry_at, bot.time + 5)
                events.append({"pair": list(pair), "result": reason})
        self.reserve(bot)
        # Travel reservations count toward the target, so service them BEFORE
        # the admission guard. They have a separate lease from merge confirmation.
        for pair, record in list(self.rendezvous.items()):
            actors = [templars.find_by_tag(tag) for tag in pair]
            if actors[0].distance_to(actors[1]) <= 6:
                if self.issued_loop != bot.state.game_loop and await self.queue_merge(bot, actors):
                    del self.rendezvous[pair]
                    events.append({"pair": list(pair), "result": "merge_queued_not_confirmed"})
            else:
                for unit in actors:
                    self.move_reserved(bot, unit, Point2(record["point"]))
        if (
            not enabled
            or self.issued_loop == bot.state.game_loop
            or bot.time < self.retry_at
            or archon_committed(bot) >= target
        ):
            return self.report(enabled, events, bot.time)
        # Keep the requested caster force, favoring high-energy Storm Templars.
        controlled = templars.filter(
            lambda unit: bot.control.eligible(unit) and not merging_templar(bot, unit)
        )
        keep = planned_target(bot, "high_templar")
        protected = {
            unit.tag for unit in sorted(controlled, key=lambda unit: (-unit.energy, unit.tag))[:keep]
        }
        candidates = controlled.filter(
            lambda unit: (
                unit.tag not in protected
                and bot.available(unit)
                and not unit.is_hallucination
                and not any(order.ability.id in MERGE_ORDERS for order in unit.orders)
                and unit.health + unit.shield >= (unit.health_max + unit.shield_max) * 0.5
                and not contacts.closer_than(12, unit)
            )
        )
        for first in sorted(candidates, key=lambda unit: (unit.energy, unit.tag)):
            partners = candidates.filter(
                lambda other, first=first: other.tag != first.tag and other.distance_to(first) <= 28
            )
            if not partners:
                continue
            second = min(partners, key=lambda unit: (unit.energy, unit.distance_to(first), unit.tag))
            pair = (first.tag, second.tag)
            if first.distance_to(second) <= 6:
                if not await self.queue_merge(bot, [first, second]):
                    continue
                events.append({"pair": list(pair), "result": "merge_queued_not_confirmed"})
            else:
                point = first.position.towards(second.position, first.distance_to(second) * 0.5)
                if bot.townhalls.ready:
                    base = bot.townhalls.ready.closest_to(point)
                    point = point.towards(
                        base.position, min(4, max(0, point.distance_to(base) - base.radius - 3))
                    )
                if not bot.in_pathing_grid(point) or contacts.closer_than(12, point):
                    continue
                query = getattr(bot.client, "query_pathing", None)
                if query is not None:
                    distances = [
                        await query(unit, point) if unit.distance_to(point) > 1 else 1
                        for unit in (first, second)
                    ]
                    if not all(distances):
                        continue
                self.rendezvous[pair] = {"point": list(point), "issued": bot.time, "until": bot.time + 12}
                self.reserve(bot)
                for unit in (first, second):
                    self.move_reserved(bot, unit, point)
                events.append({"pair": list(pair), "result": "rendezvous_reserved", "point": list(point)})
            break
        return self.report(enabled, events, bot.time)

    def reserve(self, bot):
        bot._archon_reserved_tags = {tag for pair in (*self.pending, *self.rendezvous) for tag in pair}

    def move_reserved(self, bot, unit, point):
        bot._archon_reserved_tags.discard(unit.tag)
        try:
            if unit.distance_to(point) > 1:
                bot.issue(unit.move(point))
        finally:
            bot._archon_reserved_tags.add(unit.tag)

    async def queue_merge(self, bot, actors):
        legal = await bot.get_available_abilities(actors)
        if len(legal) != 2 or any(A.MORPH_ARCHON not in abilities for abilities in legal):
            return False
        pair = tuple(unit.tag for unit in actors)
        reserved = bot._archon_reserved_tags.intersection(pair)
        bot._archon_reserved_tags.difference_update(pair)
        try:
            if not all(bot.available(unit) for unit in actors):
                return False
            # Adjacent unpaid commands combine into one exact-two-tag action.
            if not all([bot.issue(unit(A.MORPH_ARCHON)) for unit in actors]):
                raise RuntimeError("Prevalidated unpaid Archon pair could not be queued atomically")
        finally:
            bot._archon_reserved_tags.update(reserved)
        self.pending[pair] = {"until": bot.time + 15, "issued": bot.time}
        bot._archon_reserved_tags.update(pair)
        self.issued_loop = bot.state.game_loop
        return True

    def report(self, enabled, events, now):
        self.history.extend({"time": now, **event} for event in events)
        return {
            "enabled": enabled,
            "events": events,
            "pending_pairs": [{"tags": list(pair), **record} for pair, record in self.pending.items()],
            "rendezvous": [{"tags": list(pair), **record} for pair, record in self.rendezvous.items()],
            "history": list(self.history),
        }
