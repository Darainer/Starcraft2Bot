"""Plan commitment and a nonblocking boundary for future policy backends."""

import asyncio
from collections import deque

from source.strategic_plan import validate_plan
from source.strategy_policies import candidates, compose

OFFENSIVE = {"pressure", "contain", "counterattack", "finish"}


class StrategicDirector:
    def __init__(self):
        self.active = None
        self.sequence = 0
        self.committed_until = -1
        self.profile = None
        self.history = deque(maxlen=32)
        self.blocked_targets = {}

    def report_failure(self, target, now):
        if target not in {"home", "rally", "threat"}:
            self.blocked_targets[target] = now + 30
        self.committed_until = -1

    def decide(self, state):
        continuing = self.active is not None and self.active.objective in {
            "pressure",
            "contain",
            "counterattack",
            "finish",
        }
        ranked = candidates(state, continuing=continuing)
        ranked = [c for c in ranked if self.blocked_targets.get(c.target_id, -1) <= state.time]
        choice = max(ranked, key=lambda candidate: candidate.score)
        urgent = choice.objective in {"stabilize", "recover"}
        if self.active and self.profile == state.profile and not urgent:
            main = next(m for m in self.active.missions if m.role == "main")
            previous = next(
                (
                    c
                    for c in ranked
                    if c.target_id == main.target_id
                    and (
                        c.objective == self.active.objective
                        or c.objective in OFFENSIVE
                        and self.active.objective in OFFENSIVE
                    )
                ),
                None,
            )
            targets = {target.id: target for target in state.targets}
            old_target, new_target = targets.get(main.target_id), targets.get(choice.target_id)
            confirmed_opportunity = (
                old_target is not None
                and not old_target.economic
                and new_target is not None
                and new_target.economic
                and new_target.visible
            )
            # Losing sight can change pressure into safe containment; it must
            # not send the army across the map toward a speculative search site.
            if (
                previous
                and not confirmed_opportunity
                and (state.time < self.committed_until or previous.score + 12 >= choice.score)
            ):
                choice = previous
        changed = not self.active or (
            self.active.objective,
            self.active.missions[-1].target_id,
            self.profile,
        ) != (choice.objective, choice.target_id, state.profile)
        self.sequence += 1
        proposal = validate_plan(compose(state, choice, self.sequence, ranked), state)
        target_changed = (
            not self.active
            or self.profile != state.profile
            or self.active.missions[-1].target_id != proposal.missions[-1].target_id
        )
        if changed:
            if target_changed:
                self.committed_until = state.time + (20 if proposal.objective in OFFENSIVE else 8)
            self.history.append(
                {"time": state.time, "objective": proposal.objective, "reason": proposal.reason}
            )
        self.active, self.profile = proposal, state.profile
        return proposal


class DeferredPolicy:
    """One asynchronous request at a time; no provider/network dependency.

    A future backend implements async propose(assessment). Polling never waits
    for inference. Interrupt revokes the request even if a backend ignores cancel.
    """

    def __init__(self, backend, timeout=5, max_requests=60):
        self.backend = backend
        self.timeout = timeout
        self.max_requests = max_requests
        self.requests = 0
        self.pending = None
        self.requested_state = None
        self.last_error = None

    def request(self, state):
        if self.pending is not None:
            return False
        if self.requests >= self.max_requests:
            self.last_error = "Request budget exhausted"
            return False
        self.requests += 1
        self.requested_state = state
        self.pending = asyncio.create_task(self._propose(state))
        return True

    async def _propose(self, state):
        return await asyncio.wait_for(self.backend.propose(state), self.timeout)

    def interrupt(self):
        if self.pending is not None:
            self.pending.cancel()
            self.pending.add_done_callback(lambda task: task.exception() if not task.cancelled() else None)
            self.pending = None

    def poll(self, state):
        if self.pending is None or not self.pending.done():
            return None
        task, self.pending = self.pending, None
        try:
            proposal = task.result()
            origin = self.requested_state
            if (
                state.profile != origin.profile
                or state.threat_supply > max(origin.threat_supply * 1.5, origin.threat_supply + 4)
                or (state.trade_bad and not origin.trade_bad)
                or state.army_supply < origin.army_supply * 0.7
            ):
                raise ValueError("Assessment superseded by a material event")
            result = validate_plan(proposal, state)
        except (Exception, asyncio.CancelledError) as exc:
            self.last_error = str(exc) or "Request cancelled"
            return None
        self.last_error = None
        return result
