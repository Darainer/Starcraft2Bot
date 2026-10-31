"""Exactly one explicitly permitted two-Templar merge per observation."""

from sc2.ids.ability_id import AbilityId as A
from sc2.ids.unit_typeid import UnitTypeId as U

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
        bot._archon_reserved_tags = {tag for pair in self.pending for tag in pair}
        enabled = archon_permitted(bot)
        target = planned_target(bot, "archons") if enabled else 0
        if (
            not enabled
            or self.issued_loop == bot.state.game_loop
            or bot.time < self.retry_at
            or archon_committed(bot) >= target
        ):
            return self.report(enabled, events)
        contacts = visible_threats(bot)
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
                lambda other, first=first: other.tag != first.tag and other.distance_to(first) <= 6
            )
            if not partners:
                continue
            second = min(partners, key=lambda unit: (unit.energy, unit.distance_to(first), unit.tag))
            legal = await bot.get_available_abilities([first, second])
            if len(legal) != 2 or any(A.MORPH_ARCHON not in abilities for abilities in legal):
                continue
            # No await between prevalidation and the adjacent commands. Pinned
            # Burny combines these two into ONE targetless raw action. A second
            # pair in this observation would incorrectly combine four actors.
            if not bot.available(first) or not bot.available(second):
                continue
            accepted = [bot.issue(unit(A.MORPH_ARCHON)) for unit in (first, second)]
            if not all(accepted):
                raise RuntimeError("Prevalidated unpaid Archon pair could not be queued atomically")
            pair = (first.tag, second.tag)
            self.pending[pair] = {"until": bot.time + 15, "issued": bot.time}
            bot._archon_reserved_tags.update(pair)
            self.issued_loop = bot.state.game_loop
            events.append({"pair": list(pair), "result": "merge_queued_not_confirmed"})
            break
        return self.report(enabled, events)

    def report(self, enabled, events):
        return {
            "enabled": enabled,
            "events": events,
            "pending_pairs": [{"tags": list(pair), **record} for pair, record in self.pending.items()],
        }
