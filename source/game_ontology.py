"""Validated, source-linked knowledge shared by inference, planning and evaluation."""

import json
from dataclasses import dataclass
from functools import cache, lru_cache
from importlib.resources import files

from sc2.ids.unit_typeid import UnitTypeId as U


@dataclass(frozen=True)
class UnitRole:
    name: str
    unit: str
    supply: float
    domains: tuple[str, ...]
    roles: tuple[str, ...]
    producers: tuple[str, ...]
    prerequisites: tuple[str, ...]
    sources: tuple[str, ...]
    status: str
    requires_opt_in: str | None = None


def validate_document(data):
    if data.get("schema_version") != 1 or not data.get("ontology_id"):
        raise ValueError("Unsupported game ontology")
    sources = data["sources"]
    if not sources or any(not source["url"].startswith("https://") for source in sources.values()):
        raise ValueError("Ontology sources require explicit HTTPS provenance")
    dimensions = {entry["id"] for entry in data["belief_dimensions"]}
    questions = {entry["id"] for entry in data["scouting_questions"]}
    if len(dimensions) != len(data["belief_dimensions"]) or len(questions) != len(data["scouting_questions"]):
        raise ValueError("Duplicate ontology concept")
    names = set()
    for entry in data["unit_roles"]:
        if entry["name"] in names or entry["supply"] <= 0:
            raise ValueError("Invalid or duplicate unit role")
        names.add(entry["name"])
        for unit in (entry["unit"], *entry["producers"], *entry["prerequisites"]):
            if unit not in U.__members__:
                raise ValueError(f"Unknown unit reference: {unit}")
        if any(domain not in {"ground", "air"} for domain in entry["domains"]):
            raise ValueError("Unknown weapon domain")
    for section in ("belief_dimensions", "technology_signals", "unit_roles", "scouting_questions"):
        for entry in data[section]:
            if not entry.get("sources") or any(source not in sources for source in entry["sources"]):
                raise ValueError("Dangling ontology source reference")
    for entry in data["belief_dimensions"]:
        if entry["question"] not in questions:
            raise ValueError("Unknown scouting question")
    for entry in data["technology_signals"]:
        if entry["dimension"] not in dimensions or any(
            unit not in U.__members__ for unit in entry["structures"]
        ):
            raise ValueError("Unknown technology evidence relation")
    return data


@lru_cache(maxsize=1)
def _document_text():
    text = files("source").joinpath("data/game_ontology.v1.json").read_text(encoding="utf-8")
    validate_document(json.loads(text))
    return text


def ontology_document():
    # Return a fresh copy: a policy cannot mutate the shared knowledge catalog.
    return json.loads(_document_text())


@lru_cache(maxsize=1)
def unit_roles():
    return tuple(
        UnitRole(
            **{
                **entry,
                **{
                    key: tuple(entry[key])
                    for key in ("domains", "roles", "producers", "prerequisites", "sources")
                },
            }
        )
        for entry in ontology_document()["unit_roles"]
    )


@cache
def technology_signals(dimension):
    return frozenset(
        unit
        for entry in ontology_document()["technology_signals"]
        if entry["dimension"] == dimension
        for unit in entry["structures"]
    )


@cache
def parameter(name):
    return ontology_document()["inference_parameters"][name]
