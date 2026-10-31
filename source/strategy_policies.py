"""Candidate operations with explicit risk, travel, and opportunity costs."""

from dataclasses import dataclass

from source.game_ontology import parameter
from source.strategic_plan import Assessment, MissionSpec, StrategicPlan, active_combat_window
from source.strategy_profiles import PROFILES


@dataclass(frozen=True)
class Candidate:
    objective: str
    target_id: str
    score: float
    reason: str


def production_from_beliefs(state):
    """Small, reversible supply transfers from fresh confirmed counter evidence."""
    beliefs = state.opponent_beliefs
    targets = dict(state.production)
    if beliefs is None or beliefs.time > state.time:
        return state.production, "Scouting composition overlay; strategy uncertainty unavailable", ()
    requests = tuple(
        name for name, value in sorted(beliefs.questions(), key=lambda q: -q[1]) if value >= 0.6
    )[:2]
    if not state.belief_control or not state.adaptive_composition or state.time < 240:
        return state.production, "Preserve user targets and opening defense", requests

    def supported(signal):
        return (
            signal.support is not None
            and signal.support >= parameter("counter_minimum_support")
            and signal.uncertainty <= parameter("counter_maximum_uncertainty")
            and signal.evidence_age is not None
            and signal.evidence_age + state.time - beliefs.time <= parameter("army_memory_seconds")
        )

    air, armor = supported(beliefs.air), supported(beliefs.armored_ground)
    floor = 12 if supported(beliefs.light_ground) else 4
    preferred = "stalkers" if air else "immortals" if armor else None
    if preferred is None or targets.get(preferred, 0) <= 0 or targets.get("zealots", 0) - floor < 4:
        return (
            state.production,
            "Retain targets: insufficient fresh counter evidence or transferable supply",
            requests,
        )
    increment = 4 if preferred == "stalkers" else 2
    if preferred == "immortals" and targets[preferred] + increment > 10:
        return state.production, "Armored-ground counter target already at bounded ceiling", requests
    targets[preferred] += increment
    targets["zealots"] -= 4
    return (
        tuple(targets.items()),
        f"Fresh {'air' if air else 'armored-ground'} evidence: transfer eight target supply to {preferred}",
        requests,
    )


def candidates(state: Assessment, continuing=False):
    policy = PROFILES[state.profile]
    result = [Candidate("develop", "rally", 10, "Assemble, scout, and develop sustainable production")]
    if state.threat_supply:
        result.append(Candidate("stabilize", "threat", 100, "Protect a threatened base"))
    elif state.rush_warning:
        result.append(Candidate("stabilize", "rally", 100, "Prepare defenders for scouted early aggression"))
    if active_combat_window(state.combat_window, state.time) and state.health >= 0.6:
        result.append(Candidate("stabilize", "combat_window", 130, state.combat_window.reason))
    # Loss accounting describes the preceding 12 seconds, which may already
    # have reversed. Heuristic override: at least 80% army health and 1.5x
    # current main-force power allow fighting through that trailing score.
    # Ten is also the no-contact sentinel, so it never proves a safe fight.
    favorable_current_fight = (
        state.engagement_evidence_schema_version == 1
        and state.local_fight_observed
        and state.health >= 0.8
        and 1.5 <= state.local_advantage < 10
    )
    if (
        state.health < policy["retreat_health"]
        or state.local_advantage < 0.85
        or (state.trade_bad and not favorable_current_fight)
    ):
        result.append(Candidate("recover", "home", 120, "Recover from an unfavorable engagement"))
    if state.rush_warning:
        return result
    threshold = max(8, policy["continue_supply"]) if continuing else max(16, policy["attack_supply"])
    if state.army_supply < threshold or state.army_count < (4 if continuing else 6):
        return result
    for target in state.targets:
        age = state.time - target.seen_at
        # Unseen sites are reconnaissance objectives, never confirmed free bases.
        uncertainty = 8 if not target.visible else 0
        score = target.value - target.travel * 0.12 - uncertainty - min(25, age * 0.1)
        if (
            state.belief_control
            and state.opponent_beliefs is not None
            and state.opponent_beliefs.time <= state.time
        ):
            # Unknown global strength carries a cost; it never establishes a
            # free attack. Local fight evidence/emergency overrides remain intact.
            score -= max(0, state.opponent_beliefs.enemy_army.uncertainty - 0.4) * 20
        if target.defense and target.advantage < 1.2:
            result.append(Candidate("contain", target.id, 15, "Avoid fortified approach; scout and contain"))
            continue
        score += 8 if state.profile == "pressure" else -5 if state.profile == "fortress" else 0
        score += 18 if target.expansion else 0
        score += 6 if state.timing_ready else 0
        objective = "counterattack" if state.recently_defended else "pressure"
        # Cleanup requires recent winning trades, not merely few visible buildings.
        if state.local_advantage >= 3 and state.army_supply >= 60 and state.cleanup_ready:
            objective = "finish"
        result.append(
            Candidate(
                objective,
                target.id,
                score,
                "Deny a scouted expansion"
                if target.expansion
                else "Exploit reachable economic value and local strength",
            )
        )
    return result


def compose(state, choice, plan_id, ranked):
    targets = {target.id: target for target in state.targets}
    objective = choice.objective
    remaining = state.army_supply
    missions = []
    window = state.combat_window if choice.target_id == "combat_window" else None
    defending = objective == "stabilize"
    # A small home raid can coexist with pressure only when the remaining army
    # and the allocated response can each do useful work.
    projected_response = (
        state.raid_response_schema_version == 1
        and bool(state.raid_response_tags)
        and 2 <= state.raid_response_supply <= min(remaining * 0.3, max(8, state.threat_supply * 1.5))
        and state.raid_response_advantage >= 1.2
    )
    split = (
        defending
        and window is None
        and not state.rush_warning
        and state.threat_supply > 0
        and state.threat_supply <= min(12, remaining * 0.2)
        and remaining >= 40
        and (state.home_advantage >= 1.2 or projected_response)
    )
    if split:
        budget = (
            state.raid_response_supply
            if projected_response
            else min(remaining * 0.3, max(8, state.threat_supply * 1.5))
        )
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
    if window is not None:
        point = window.position
    mode = "move" if objective in {"develop", "recover", "contain"} else "attack"
    if objective == "stabilize" and state.home_advantage < 0.85 and window is None:
        point, mode = state.home, "move"
        choice = Candidate("stabilize", "home", choice.score, "Concentrate defenders at a safe base")
    if objective == "stabilize" and state.opening_hold is not None and window is None:
        point, mode = tuple(state.opening_hold), "move"
        choice = Candidate(
            "stabilize", "rally", choice.score, "Hold opening defenders together near protected power"
        )
    if objective == "contain":
        # The mission executor chooses a safe offset; retain the evidence target.
        mode = "move"
    if objective in {"pressure", "counterattack", "contain", "finish"} and not state.threat_supply:
        budget = min(12, remaining * 0.25)
        alternatives = [
            target
            for target in state.targets
            if target.id != choice.target_id
            and target.economic
            and target.expansion
            and target.visible
            and not target.static_defense
            and (
                target.defense == 0
                or (0 < target.defender_supply <= budget * 0.5 and target.advantage >= 1.5)
            )
            and any(candidate.target_id == target.id for candidate in ranked)
        ]
        if alternatives and remaining >= 32:
            target = max(alternatives, key=lambda target: target.value - target.travel * 0.15)
            missions.append(
                MissionSpec("denial", "deny", target.id, target.position, budget, 6, 60, require_visible=True)
            )
            remaining -= budget
    minimum = min(remaining, max(16, PROFILES[state.profile]["attack_supply"]))
    missions.append(MissionSpec("main", "main", choice.target_id, point, remaining, minimum, 50, mode))
    production, production_reason, scouting_requests = production_from_beliefs(state)
    return StrategicPlan(
        plan_id,
        state.version,
        state.time,
        min(state.time + 20, window.expires_at) if window is not None else state.time + 20,
        objective,
        tuple(missions),
        production,
        not state.threat_supply and not state.rush_warning and objective != "recover",
        choice.reason,
        tuple((f"{c.objective}:{c.target_id}", round(c.score, 2)) for c in ranked),
        production_reason=production_reason,
        scouting_requests=scouting_requests,
        response_policy=state.response_policy,
        response_policy_until=state.response_policy_until,
        response_reason=state.response_reason,
        response_evidence=state.response_evidence,
        playbook_id=state.playbook_id,
        playbook_uncertainty=state.playbook_uncertainty,
        tactical_policy=state.tactical_policy,
        combat_window=window,
    )
