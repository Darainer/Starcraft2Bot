"""Validated settings and in-game commands; independent of the SC2 runtime."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path
from typing import Protocol

COMBAT_POWERS = ("blink", "storm", "feedback", "guardian_shield", "voidray_alignment")
ECONOMY = ("workers", "allocation", "supply", "gas", "expansion", "construction", "production", "upgrades")


class SelectableUnit(Protocol):
    @property
    def tag(self) -> int: ...

    @property
    def is_selected(self) -> bool: ...


@dataclass
class AssistantSettings:
    enabled: bool = True
    workers: bool = True
    allocation: bool = True
    supply: bool = True
    gas: bool = True
    expansion: bool = True
    construction: bool = True
    production: bool = True
    upgrades: bool = True
    chrono: bool = True
    blink: bool = False
    storm: bool = False
    feedback: bool = False
    guardian_shield: bool = False
    voidray_alignment: bool = False
    hud: bool = True
    reserve_minerals: int = 0
    reserve_gas: int = 0
    bases: int = 3
    max_workers: int = 70
    zealots: int = 12
    stalkers: int = 40
    sentries: int = 2
    immortals: int = 6
    high_templar: int = 0
    colossi: int = 0
    voidrays: int = 0

    def validate(self) -> AssistantSettings:
        defaults = type(self)()
        for field in fields(self):
            value, default = getattr(self, field.name), getattr(defaults, field.name)
            if type(value) is not type(default):
                raise ValueError(f"{field.name} must be {type(default).__name__}")
            if type(value) is int:
                limit = 10000 if field.name.startswith("reserve_") else 200
                minimum = 1 if field.name == "bases" else 0
                if not minimum <= value <= limit:
                    raise ValueError(f"{field.name} must be between {minimum} and {limit}")
        return self

    @classmethod
    def load(cls, path: str | Path) -> AssistantSettings:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object")
        unknown = set(data) - set(asdict(cls()))
        if unknown:
            raise ValueError(f"Unknown settings: {', '.join(sorted(unknown))}")
        return cls(**data).validate()


class Control:
    def __init__(self, settings: AssistantSettings | None = None) -> None:
        self.settings = (settings or AssistantSettings()).validate()
        self.released: set[int] = set()

    def eligible(self, unit: SelectableUnit) -> bool:
        return not unit.is_selected and unit.tag not in self.released

    def status(self) -> str:
        enabled = [f.name for f in fields(self.settings) if getattr(self.settings, f.name) is True]
        s = self.settings
        return (
            f"{'RUNNING' if s.enabled else 'PAUSED'} | on: {', '.join(enabled)} | "
            f"reserve {s.reserve_minerals}m/{s.reserve_gas}g | bases {s.bases} | "
            f"released {len(self.released)}"
        )

    def command(self, text: str, selected_tags: Sequence[int] = ()) -> str | None:
        words = text.lower().split()
        if not words or words[0] != "!assist":
            return None
        args = words[1:]
        if not args or args == ["status"]:
            return self.status()
        if args == ["help"]:
            return (
                "!assist pause/resume/status; <toggle> on/off; economy/spells on/off; "
                "reserve <minerals> <gas>; set <setting> <number>; release/claim/claim-all. "
                "Toggles: " + ", ".join(ECONOMY + ("chrono",) + COMBAT_POWERS + ("hud",))
            )
        if args in (["release"], ["claim"]):
            if args[0] == "release":
                self.released.update(selected_tags)
            else:
                self.released.difference_update(selected_tags)
            return f"{args[0]}: {len(selected_tags)} selected units; {len(self.released)} released"
        if args == ["claim-all"]:
            self.released.clear()
            return "All released units returned to assistant eligibility"
        candidate = replace(self.settings)
        try:
            if args in (["pause"], ["resume"]):
                candidate.enabled = args[0] == "resume"
            elif len(args) == 2 and args[1] in ("on", "off"):
                name, value = args[0], args[1] == "on"
                names = ECONOMY if name == "economy" else COMBAT_POWERS if name == "spells" else (name,)
                for name in names:
                    if not hasattr(candidate, name) or type(getattr(candidate, name)) is not bool:
                        raise ValueError("Unknown toggle; use !assist help")
                    setattr(candidate, name, value)
            elif len(args) == 3 and args[0] == "reserve":
                candidate.reserve_minerals, candidate.reserve_gas = int(args[1]), int(args[2])
            elif len(args) == 3 and args[0] == "set":
                if not hasattr(candidate, args[1]) or type(getattr(candidate, args[1])) is not int:
                    raise ValueError("Unknown numeric setting")
                setattr(candidate, args[1], int(args[2]))
            else:
                raise ValueError("Unknown command; use !assist help")
            candidate.validate()
        except ValueError as exc:
            return f"Rejected: {exc}"
        self.settings = candidate
        return self.status()


def within_budget(
    minerals: float,
    gas: float,
    cost_minerals: float,
    cost_gas: float,
    settings: AssistantSettings,
    extra_minerals: float = 0,
) -> bool:
    return (
        minerals - cost_minerals >= settings.reserve_minerals + extra_minerals
        and gas - cost_gas >= settings.reserve_gas
    )
