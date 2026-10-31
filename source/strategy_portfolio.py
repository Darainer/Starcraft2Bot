"""SC2 response repertoire selected from causal scouting, separate from objectives.

Race restricts compatibility; it does not establish an opponent's gameplan.
Missing vision is unknown. Support and uncertainty are heuristic, not calibrated.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Playbook:
    race: str | None
    response: str
    tactic: str
    source: str
    fund_bay: bool = False
    complete_colossus: bool = False


PLAYBOOKS = {
    "baseline": Playbook(None, "baseline", "formation", "67ed0f7"),
    "zerg_early_robotics": Playbook("Zerg", "early_robotics", "formation", "b3aff99"),
    "terran_counter_tech": Playbook("Terran", "counter_tech", "formation", "a7cefe1", True, True),
    "terran_counter_range": Playbook("Terran", "counter_tech", "local_range", "287dbd5", True, True),
    "zerg_counter_completion": Playbook(
        "Zerg", "counter_completion", "formation", "portfolio-v1", False, True
    ),
}
PLAYBOOK_CHOICES = ("auto", *PLAYBOOKS)
GROUND_UNITS = frozenset(
    {
        "MARINE",
        "MARAUDER",
        "REAPER",
        "HELLION",
        "HELLIONTANK",
        "SIEGETANK",
        "SIEGETANKSIEGED",
        "THOR",
        "CYCLONE",
    }
)
GROUND_TECH = frozenset({"BARRACKS", "FACTORY", "BARRACKSTECHLAB", "FACTORYTECHLAB"})


@dataclass(frozen=True)
class Selection:
    id: str = "baseline"
    until: float = 0
    uncertainty: float = 1
    reason: str = "Insufficient positive scouting; retain baseline and gather evidence"
    evidence: tuple[str, ...] = ()

    @property
    def playbook(self):
        return PLAYBOOKS[self.id]


def fresh(now, item, age):
    seen = item.get("seen_seconds")
    return (
        isinstance(seen, (int, float))
        and not isinstance(seen, bool)
        and isfinite(seen)
        and 0 <= now - seen < age
    )


def select_playbook(now, race, intel, requested="auto", ready_tech=()):
    """Choose a response package; configured AI builds/outcomes are never consulted."""
    if requested not in PLAYBOOK_CHOICES or not isfinite(now) or now < 0:
        raise ValueError("Invalid playbook request or assessment time")
    if requested != "auto":
        item = PLAYBOOKS[requested]
        if item.race is not None and item.race != race:
            return Selection(reason="Requested experiment is incompatible with observed opponent race")
        if requested == "baseline":
            return Selection(reason="Explicit baseline comparison")
        return Selection(
            requested,
            now + 20,
            1,
            "Explicit experimental playbook override",
            ("User-selected experiment; no inferred opponent intent",),
        )
    if race == "Zerg":
        response = intel.get("zerg_opening_response", {})
        if (
            response.get("response") == "early_robotics"
            and 0 <= response.get("time", -1) <= now < response.get("valid_until", 0)
            and response.get("evidence")
        ):
            return Selection(
                "zerg_early_robotics",
                response["valid_until"],
                response.get("uncertainty", 1),
                response.get("reason", "Positive Zerg opening evidence"),
                tuple(response["evidence"]),
            )
        light = {
            str(u["tag"]): u
            for u in intel.get("enemy_unit_evidence", [])
            if "tag" in u and u.get("light") and not u.get("air") and fresh(now, u, 45)
        }
        if "ROBOTICSBAY" in ready_tech and len(light) >= 8:
            return Selection(
                "zerg_counter_completion",
                max(u["seen_seconds"] for u in light.values()) + 45,
                0.4,
                "Fresh light ground force and ready Bay support completing requested splash counter",
                ("Observed light ground contacts >= 8 within 45 seconds", "Own Robotics Bay ready"),
            )
        return Selection(reason=response.get("reason", Selection().reason))
    if race != "Terran":
        return Selection()
    # Every contact has its own age. An unrelated fresh unit cannot refresh tech.
    units = {
        str(u["tag"]): u
        for u in intel.get("enemy_unit_evidence", [])
        if "tag" in u and u.get("kind") in GROUND_UNITS and fresh(now, u, 45)
    }
    tech = [
        t
        for t in intel.get("known_enemy_tech_evidence", [])
        if t.get("kind") in GROUND_TECH and fresh(now, t, 90)
    ]
    supply = sum(max(0, u.get("supply", 0)) for u in units.values())
    if supply >= 4:
        return Selection(
            "terran_counter_range",
            max(u["seen_seconds"] for u in units.values()) + 45,
            0.35,
            "Fresh Terran ground force supports funded counters and local range closing",
            ("Observed Terran ground supply >= 4 within 45 seconds",),
        )
    if tech:
        return Selection(
            "terran_counter_tech",
            max(t["seen_seconds"] for t in tech) + 90,
            0.65,
            "Observed Terran ground production supports bounded counter-tech investment",
            tuple(sorted({f"Observed {t['kind']} within 90 seconds" for t in tech})),
        )
    return Selection()


def active_playbook(bot):
    """Execution checks apply to all component consumers, including macro helpers."""
    settings = bot.settings
    plan = getattr(bot, "strategic_plan", None)
    if (
        plan is None
        or not hasattr(plan, "playbook_id")
        or not (settings.enabled and settings.attack and settings.adaptive_composition)
        or settings.strategy != "auto"
        or settings.strategy_script
        or settings.playbook not in {"auto", plan.playbook_id}
        or not plan.created_at <= bot.time < plan.expires_at
    ):
        return PLAYBOOKS["baseline"]
    item = PLAYBOOKS.get(getattr(plan, "playbook_id", "baseline"), PLAYBOOKS["baseline"])
    race = getattr(getattr(bot, "enemy_race", None), "name", None)
    if item.race != race or plan.response_policy != item.response or bot.time >= plan.response_policy_until:
        return PLAYBOOKS["baseline"]
    return item
