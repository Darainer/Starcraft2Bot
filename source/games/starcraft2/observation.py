"""Complete player-view semantic inputs for the first small neural policy."""

from dataclasses import replace

from google.protobuf.json_format import MessageToDict

from source.games.starcraft2.encoding import from_assessment, opaque
from source.strategy_core.contracts import Entity, Feature

LIVE_FEATURES = (
    "own.income_primary",
    "own.income_secondary",
    "own.production_queues",
    "actors.eligible_fraction",
    "intent.aggressive",
    "intent.recovering",
    "intent.expansion",
    "intent.remaining_seconds",
    "execution.issued_count",
    "execution.observed_effect_count",
    "entities.controlled_omitted",
    "entities.contact_omitted",
)
ENTITY_FEATURES = (
    "capacity",
    "health",
    "primary_attack",
    "secondary_attack",
    "primary_range",
    "secondary_range",
    "mobility",
    "vertical_mobility",
    "sensor",
    "ready",
    "control_eligible",
    "x_offset",
    "y_offset",
    "queue_depth",
    "utility",
    "home",
    "assembly",
    "threat",
    "economic_site",
    "search_site",
)
ENTITY_LIMIT = 128
LIVE_FEATURE_VERSION = "sc2-semantic-features-v2"


def vector_features(values, evidence=(), age=0.0):
    return tuple(
        Feature(
            name,
            values.get(name),
            "fraction",
            0 if name in values else 1,
            age if name in values else None,
            evidence if name in values else (),
        )
        for name in ENTITY_FEATURES
    )


class ObservationAdapter:
    def __init__(self, fact_model):
        self.facts = fact_model
        self.last_facts = None

    def observe(self, bot, assessment, *, elapsed_seconds=0, episode_start=False, issued=(), effects=()):
        if self.last_facts is None or assessment.time > self.last_facts["time_seconds"]:
            self.last_facts = self.facts.observe(
                {
                    "game_loop": bot.state.game_loop,
                    "visibility_scope": "player_observation_fog_of_war",
                    "observation": MessageToDict(
                        bot.state.response_observation, preserving_proto_field_name=True
                    ),
                    "scouting": {"intel": bot.scout_report},
                }
            )
        belief = from_assessment(
            assessment,
            bot.settings,
            facts=self.last_facts,
            elapsed_seconds=elapsed_seconds,
            episode_start=episode_start,
        )
        own_start = bot.start_location
        entities = []

        def supply(unit):
            return self.facts.metadata.get(unit.type_id.value, {}).get("supply")

        own = sorted(bot.all_own_units, key=lambda u: (-(supply(u) or 0), u.tag))
        enemies = sorted(
            (bot.enemy_units | bot.enemy_structures).filter(lambda u: u.is_visible),
            key=lambda u: (u.distance_to(own_start), u.tag),
        )
        for group, units in (("controlled", own), ("contact", enemies)):
            for unit in units[:ENTITY_LIMIT]:
                eligible = group == "controlled" and bot.control.eligible(unit) and unit.tag != bot.scout_tag
                maximum = unit.health_max + unit.shield_max
                values = {
                    "health": (unit.health + unit.shield) / maximum if maximum else 0,
                    "primary_attack": unit.ground_dps / 100,
                    "secondary_attack": unit.air_dps / 100,
                    "primary_range": unit.ground_range / 15,
                    "secondary_range": unit.air_range / 15,
                    "mobility": unit.movement_speed / 6,
                    "vertical_mobility": float(unit.is_flying),
                    "sensor": float(unit.is_detector),
                    "ready": float(unit.is_ready),
                    "x_offset": (unit.position.x - own_start.x) / 200,
                    "y_offset": (unit.position.y - own_start.y) / 200,
                }
                if supply(unit) is not None:
                    values["capacity"] = supply(unit) / 200
                # Opponent orders/queues and control flags are not legal own-state inputs.
                if group == "controlled":
                    values.update(control_eligible=float(eligible), queue_depth=len(unit.orders) / 5)
                entities.append(
                    Entity(
                        opaque("u", str(unit.tag)),
                        group,
                        vector_features(values, (opaque("e", f"unit:{unit.tag}:{assessment.version}"),)),
                    )
                )
        for target in belief.targets:
            if target is not None:
                values = {
                    "x_offset": (target.position[0] - own_start.x) / 200,
                    "y_offset": (target.position[1] - own_start.y) / 200,
                    target.role: 1.0,
                }
                opportunity = next((t for t in assessment.targets if t.id == target.id), None)
                if opportunity is not None:
                    values["utility"] = opportunity.value / 100
                entities.append(
                    Entity(target.handle, "candidate", vector_features(values, age=target.age_seconds))
                )
        score = getattr(bot.state, "score", None)
        plan = bot.strategic_plan
        extra = {
            "own.income_primary": getattr(score, "collection_rate_minerals", None),
            "own.income_secondary": getattr(score, "collection_rate_vespene", None),
            "own.production_queues": sum(len(u.orders) for u in own if u.is_structure) / 30,
            "actors.eligible_fraction": sum(bot.control.eligible(u) and u.tag != bot.scout_tag for u in own)
            / max(1, len(own)),
            "intent.aggressive": float(plan.objective in {"pressure", "counterattack", "contain", "finish"})
            if plan
            else None,
            "intent.recovering": float(plan.objective == "recover") if plan else None,
            "intent.expansion": float(plan.expand) if plan else None,
            "intent.remaining_seconds": max(0, plan.expires_at - assessment.time) / 120 if plan else None,
            "execution.issued_count": len(issued) / 100,
            "execution.observed_effect_count": len(effects) / 100,
            "entities.controlled_omitted": max(0, len(own) - ENTITY_LIMIT),
            "entities.contact_omitted": max(0, len(enemies) - ENTITY_LIMIT),
        }
        for name in ("own.income_primary", "own.income_secondary"):
            if extra[name] is not None:
                extra[name] /= 1000
        unsupported_replaced = {
            "own.production_queues",
            "actors.entities",
            "actors.control_eligibility",
            "intent.current",
            "execution.observed_effects",
            "own.income",
        }
        features = tuple(f for f in belief.shared.features if f.name not in unsupported_replaced) + tuple(
            Feature(name, value, "fraction", 0 if value is not None else 1, 0 if value is not None else None)
            for name, value in extra.items()
        )
        shared = replace(
            belief.shared, features=features, entities=tuple(entities), feature_version=LIVE_FEATURE_VERSION
        )
        return replace(belief, shared=shared)
