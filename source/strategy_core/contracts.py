"""Versioned, immutable actor inputs. Missing values are never numeric zero."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any

SHARED_ONTOLOGY = "strategic-semantics-v1"


@dataclass(frozen=True)
class Feature:
    name: str
    value: float | None
    unit: str
    uncertainty: float = 1.0
    age_seconds: float | None = None
    evidence: tuple[str, ...] = ()
    supported: bool = True

    def __post_init__(self) -> None:
        if not self.name or not self.unit or not isfinite(self.uncertainty) or not 0 <= self.uncertainty <= 1:
            raise ValueError("Invalid semantic feature")
        if self.value is not None and (not self.supported or not isfinite(self.value)):
            raise ValueError("Unsupported or nonfinite feature value")
        if self.age_seconds is not None and (not isfinite(self.age_seconds) or self.age_seconds < 0):
            raise ValueError("Invalid evidence age")
        if not isinstance(self.evidence, tuple) or any(
            not isinstance(e, str) or not e for e in self.evidence
        ):
            raise ValueError("Evidence must be immutable opaque handles")


@dataclass(frozen=True)
class Candidate:
    handle: str
    role: str
    visible: bool
    age_seconds: float
    travel_fraction: float

    def __post_init__(self) -> None:
        if not self.handle or self.role not in {"home", "assembly", "threat", "economic_site", "search_site"}:
            raise ValueError("Invalid semantic candidate")
        if any(not isfinite(v) or v < 0 for v in (self.age_seconds, self.travel_fraction)):
            raise ValueError("Invalid candidate timing or travel")


@dataclass(frozen=True)
class StrategicStateV1:
    time_seconds: float
    elapsed_seconds: float
    episode_start: bool
    features: tuple[Feature, ...]
    candidates: tuple[Candidate, ...]
    capabilities: tuple[tuple[str, bool], ...]
    feature_version: str
    normalization_version: str
    schema_version: str = "strategic-state-v1"
    ontology_version: str = SHARED_ONTOLOGY

    def __post_init__(self) -> None:
        if self.schema_version != "strategic-state-v1" or self.ontology_version != SHARED_ONTOLOGY:
            raise ValueError("Unsupported shared contract")
        if any(not isfinite(v) or v < 0 for v in (self.time_seconds, self.elapsed_seconds)):
            raise ValueError("Invalid semantic time")
        if self.elapsed_seconds > self.time_seconds or (self.episode_start and self.elapsed_seconds != 0):
            raise ValueError("Invalid episode boundary")
        if not self.feature_version or not self.normalization_version:
            raise ValueError("Missing feature/normalization identity")
        for items in (self.features, self.candidates, self.capabilities):
            if not isinstance(items, tuple):
                raise ValueError("Shared state collections must be immutable")
        names = [f.name for f in self.features]
        handles = [c.handle for c in self.candidates]
        if len(set(names)) != len(names) or len(set(handles)) != len(handles):
            raise ValueError("Duplicate semantic feature or candidate")
        if len(dict(self.capabilities)) != len(self.capabilities) or any(
            not isinstance(pair, tuple) or not pair[0] or type(pair[1]) is not bool
            for pair in self.capabilities
        ):
            raise ValueError("Invalid capabilities")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StrategicStateV1:
        values = dict(data)
        values["features"] = tuple(
            Feature(**{**feature, "evidence": tuple(feature["evidence"])}) for feature in data["features"]
        )
        values["candidates"] = tuple(Candidate(**candidate) for candidate in data["candidates"])
        values["capabilities"] = tuple(tuple(pair) for pair in data["capabilities"])
        return cls(**values)
