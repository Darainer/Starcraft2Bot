"""Causal SC2 facts from legal observations; no strategy labels or inferred beliefs.

First recorded sightings are sampling bounds, not inferred construction starts.
Remembered units are last-seen contacts, not a claim that they remain alive.
"""

from collections import defaultdict
from math import isfinite

BASES = {"HATCHERY", "LAIR", "HIVE", "COMMANDCENTER", "ORBITALCOMMAND", "PLANETARYFORTRESS", "NEXUS"}
ORDINARY = BASES | {"EXTRACTOR", "REFINERY", "ASSIMILATOR", "PYLON", "SUPPLYDEPOT", "SUPPLYDEPOTLOWERED"}


class ScoutingFacts:
    def __init__(self, unit_metadata):
        self.metadata = unit_metadata
        self.by_kind = {item["kind"]: item for item in unit_metadata.values()}
        self.contacts = {}
        self.tech = {}
        self.expansions = {}
        self.last_time = -1

    def _remember(self, meta, tag, seen, progress=None):
        prior = self.contacts.get(tag)
        if prior is None or seen >= prior["last_seen"]:
            self.contacts[tag] = {**meta, "last_seen": seen}
        if meta["structure"]:
            entry = self.tech.setdefault(
                meta["kind"], {"first_recorded_seen": seen, "first_observed_progress": progress}
            )
            entry["first_recorded_seen"] = min(seen, entry["first_recorded_seen"])
            if progress is not None and "first_progress_recorded_at" not in entry:
                entry.update(first_observed_progress=progress, first_progress_recorded_at=seen)
            if seen >= entry.get("last_recorded_seen", -1):
                entry["last_recorded_seen"] = seen
                if progress is not None:
                    entry["last_observed_progress"] = progress
                    entry["last_progress_recorded_at"] = seen

    def observe(self, row):
        now = row["game_loop"] / 22.4
        if not isfinite(now) or now < 0 or now <= self.last_time:
            raise ValueError("Fact observations must advance in game time")
        if row.get("visibility_scope", "player_observation_fog_of_war") != "player_observation_fog_of_war":
            raise ValueError("Facts require player-perspective fog-of-war observations")
        self.last_time = now
        observation = row["observation"]["observation"]
        raw = observation.get("raw_data", {})
        intel = row.get("scouting", {}).get("intel", {})
        dead = {str(tag) for tag in raw.get("event", {}).get("dead_units", [])}
        for tag in dead:
            self.contacts.pop(tag, None)
        for item in (*intel.get("known_enemy_tech_evidence", []), *intel.get("enemy_unit_evidence", [])):
            seen = item.get("seen_seconds", -999)
            meta = self.by_kind.get(item.get("kind"))
            tag = str(item.get("tag"))
            if meta is not None and tag not in dead and isinstance(seen, (int, float)) and 0 <= seen <= now:
                self._remember(meta, tag, seen)
        for unit in raw.get("units", []):
            if (
                unit.get("alliance") != "Enemy"
                or unit.get("display_type") != "Visible"
                or unit.get("is_blip")
                or unit.get("is_hallucination")
            ):
                continue
            meta = self.metadata.get(unit["unit_type"])
            if meta is None:
                continue
            tag = str(unit["tag"])
            if tag not in dead:
                self._remember(meta, tag, now, unit.get("build_progress", 0))
        self.contacts = {
            tag: item
            for tag, item in self.contacts.items()
            if now - item["last_seen"] <= (180 if item["structure"] else 90)
        }
        grouped = defaultdict(list)
        for contact in self.contacts.values():
            grouped[contact["kind"]].append(contact)
        units = []
        for kind, contacts in sorted(grouped.items()):
            ages = [now - contact["last_seen"] for contact in contacts]
            units.append(
                {
                    "kind": kind,
                    "visible_count": sum(age == 0 for age in ages),
                    "recent_30s_count": sum(age <= 30 for age in ages),
                    "remembered_count": len(contacts),
                    "newest_age_seconds": min(ages),
                    "oldest_age_seconds": max(ages),
                    "supply_per_unit": contacts[0]["supply"],
                    "combat_nonworker": contacts[0]["combat"],
                }
            )
        # These are timestamped positive base sightings from the player-view
        # controller. Never refresh an old contact from the current clock.
        for base in intel.get("known_enemy_bases", []):
            seen = base.get("seen_seconds", -999)
            if base.get("expansion") and isinstance(seen, (int, float)) and 0 <= seen <= now:
                key = tuple(base["position"])
                entry = self.expansions.setdefault(key, {"first_recorded_seen": seen})
                entry["last_recorded_seen"] = max(seen, entry.get("last_recorded_seen", seen))
        sites = []
        for site in intel.get("expansion_sites", []):
            seen = site.get("last_checked", -999)
            valid = isinstance(seen, (int, float)) and 0 <= seen <= now
            sites.append(
                {
                    "position": list(site["position"]),
                    "status": site.get("status", "unknown") if valid else "unknown",
                    "last_checked": seen if valid else None,
                    "age_seconds": now - seen if valid else None,
                    "scope": "Site center visible; empty does not certify the entire expansion area",
                }
            )
        recent_force = [c for c in self.contacts.values() if c["combat"] and now - c["last_seen"] <= 30]
        supply = sum(c["supply"] for c in recent_force)
        own = {
            key: observation["player_common"].get(key, 0) if "player_common" in observation else None
            for key in ("food_army", "food_workers", "food_cap", "minerals", "vespene")
        }
        return {
            "schema_version": "sc2-observed-facts-v1",
            "time_seconds": now,
            "own": own,
            "enemy_contacts": units,
            "technology_history": [{"kind": kind, **entry} for kind, entry in sorted(self.tech.items())],
            "expansion_history": [
                {"position": list(position), **entry} for position, entry in sorted(self.expansions.items())
            ],
            "site_inspections": sorted(sites, key=lambda site: site["position"]),
            "recent_observed_enemy_combat_supply": supply,
            "observed_supply_ratio": supply / own["food_army"]
            if own["food_army"] is not None and own["food_army"] > 0
            else None,
            "fact_presence": {
                "fresh_army_contact": supply > 0,
                "fresh_force": supply >= 4,
                "fresh_technology": any(
                    c["structure"] and c["kind"] not in ORDINARY and now - c["last_seen"] <= 60
                    for c in self.contacts.values()
                ),
                "fresh_expansion": any(now - e["last_recorded_seen"] <= 60 for e in self.expansions.values()),
                "fresh_site_inspection": any(
                    site["age_seconds"] is not None and site["age_seconds"] <= 60 for site in sites
                ),
            },
        }
