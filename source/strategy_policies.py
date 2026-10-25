"""Candidate operations with explicit risk, travel, and opportunity costs."""

from dataclasses import dataclass

from source.strategic_plan import Assessment, MissionSpec, StrategicPlan
from source.strategy_profiles import PROFILES


@dataclass(frozen=True)
class Candidate:
    objective: str
    target_id: str
    score: float
    reason: str


def candidates(state: Assessment):
    policy = PROFILES[state.profile]
    result = [Candidate("develop", "rally", 10, "Assemble, scout, and develop sustainable production")]
    if state.threat_supply:
        result.append(Candidate("stabilize", "threat", 100, "Protect a threatened base"))
    if state.health < policy["retreat_health"] or state.local_advantage < 0.85 or state.trade_bad:
        result.append(Candidate("recover", "home", 120, "Recover from an unfavorable engagement"))
    if state.army_supply < max(16, policy["attack_supply"]) or state.army_count < 6:
        return result
    for target in state.targets:
        age = state.time - target.seen_at
        # Unseen sites are reconnaissance objectives, never confirmed free bases.
        uncertainty = 8 if not target.visible else 0
        score = target.value - target.travel * 0.12 - uncertainty - min(25, age * 0.1)
        if target.defense and target.advantage < 1.2:
            result.append(Candidate("contain", target.id, 15, "Avoid fortified approach; scout and contain"))
            continue
        score += 8 if state.profile == "pressure" else -5 if state.profile == "fortress" else 0
        score += 6 if state.timing_ready else 0
        objective = "counterattack" if state.recently_defended else "pressure"
        # Cleanup requires recent winning trades, not merely few visible buildings.
        if state.local_advantage >= 3 and state.army_supply >= 60 and state.cleanup_ready:
            objective = "finish"
        result.append(
            Candidate(objective, target.id, score, "Exploit reachable economic value and local strength")
        )
    return result


def compose(state, choice, plan_id, ranked):
    targets = {target.id: target for target in state.targets}
    objective = choice.objective
    remaining = state.army_supply
    missions = []
    defending = objective == "stabilize"
    # A small home raid can coexist with pressure only when the remaining army
    # and the allocated response can each do useful work.
    split = (
        defending
        and state.threat_supply <= min(12, remaining * 0.2)
        and remaining >= 40
        and state.home_advantage >= 1.2
    )
    if split:
        budget = min(remaining * 0.3, max(8, state.threat_supply * 1.5))
        missions.append(MissionSpec("home-defense", "defend", "threat", state.threat, budget, 2, 90))
        remaining -= budget
        attacks = [c for c in ranked if c.objective in {"pressure", "counterattack", "finish"}]
        choice = (
            max(attacks, key=lambda c: c.score)
            if attacks
            else Candidate("develop", "rally", 10, "Keep reserve")
        )
        objective = choice.objective
    point = {"home": state.home, "rally": state.rally, "threat": state.threat}.get(choice.target_id)
    if choice.target_id in targets:
        point = targets[choice.target_id].position
    mode = "move" if objective in {"develop", "recover", "contain"} else "attack"
    if objective == "stabilize" and state.home_advantage < 0.85:
        point, mode = state.home, "move"
        choice = Candidate("stabilize", "home", choice.score, "Concentrate defenders at a safe base")
    if objective == "contain":
        # The mission executor chooses a safe offset; retain the evidence target.
        mode = "move"
    if objective in {"pressure", "counterattack", "contain", "finish"} and not state.threat_supply:
        alternatives = [
            target
            for target in state.targets
            if target.id != choice.target_id and target.economic and target.visible and target.defense == 0
        ]
        if alternatives and remaining >= 48:
            target = max(alternatives, key=lambda target: target.value - target.travel * 0.15)
            budget = min(12, remaining * 0.2)
            missions.append(
                MissionSpec("denial", "deny", target.id, target.position, budget, 6, 60, require_visible=True)
            )
            remaining -= budget
    minimum = min(remaining, max(16, PROFILES[state.profile]["attack_supply"]))
    missions.append(MissionSpec("main", "main", choice.target_id, point, remaining, minimum, 50, mode))
    return StrategicPlan(
        plan_id,
        state.version,
        state.time,
        state.time + 20,
        objective,
        tuple(missions),
        state.production,
        not state.threat_supply and objective != "recover",
        choice.reason,
        tuple((f"{c.objective}:{c.target_id}", round(c.score, 2)) for c in ranked),
    )
