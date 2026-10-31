"""Scoped movement intents with current-observation ownership and expiry checks."""

from collections import deque
from dataclasses import dataclass
from math import isfinite

from sc2.position import Point2


@dataclass(frozen=True)
class ActionIntent:
    actor: int
    revision: int
    source_loop: int
    expires_loop: int
    action: str
    target: tuple[float, float]


class ActionExecutor:
    def __init__(self):
        self.assignments = {}
        self.revision = 0
        self.outcomes = deque(maxlen=128)

    def assign(self, actors):
        """Each actor has exactly one mission; changed ownership revokes old work."""
        updated = {}
        for tag, mission in actors.items():
            prior = self.assignments.get(tag)
            if prior is None or prior[0] != mission:
                self.revision += 1
                prior = (mission, self.revision)
            updated[tag] = prior
        self.assignments = updated

    def execute(self, bot, intent):
        unit = bot.units.find_by_tag(intent.actor)
        assignment = self.assignments.get(intent.actor)
        reason = None
        if not bot.settings.enabled or not bot.settings.attack:
            reason = "automation_disabled"
        elif assignment is None or assignment[1] != intent.revision:
            reason = "assignment_revoked"
        elif not intent.source_loop <= bot.state.game_loop <= intent.expires_loop:
            reason = "observation_expired"
        elif unit is None or not bot.available(unit):
            reason = "actor_unavailable"
        elif intent.action not in {"move", "attack"}:
            reason = "unsupported_action"
        elif len(intent.target) != 2 or not all(
            type(v) in (int, float) and isfinite(v) for v in intent.target
        ):
            reason = "invalid_target"
        else:
            point = Point2(intent.target)
            area = getattr(bot.game_info, "playable_area", None)
            if area and not (
                area.x <= point.x < area.x + area.width and area.y <= point.y < area.y + area.height
            ):
                reason = "outside_map"
            elif intent.action == "move" and unit.distance_to(point) < 2 and not unit.orders:
                reason = "at_destination"
            elif (
                unit.orders
                and isinstance(unit.order_target, Point2)
                and unit.order_target.distance_to(point) < 1
                and (
                    unit.is_flying
                    or (
                        (
                            area is None
                            or (
                                area.x <= unit.order_target.x < area.x + area.width
                                and area.y <= unit.order_target.y < area.y + area.height
                            )
                        )
                        and bot.in_pathing_grid(unit.order_target)
                    )
                )
            ):
                # Only suppress a matching action; retreat must replace attack-move.
                current_move = unit.is_moving
                if current_move == (intent.action == "move"):
                    reason = "standing_order"
            if reason is None:
                command = unit.move(point) if intent.action == "move" else unit.attack(point)
                reason = "issued" if bot.issue(command) else "rejected"
        self.outcomes.append({"actor": intent.actor, "revision": intent.revision, "result": reason})
        return reason == "issued"
