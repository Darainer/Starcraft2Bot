from dataclasses import FrozenInstanceError

import pytest

from source.game_ontology import ontology_document, technology_signals, unit_roles, validate_document
from source.opponent_beliefs import OpponentBeliefModel, beliefs_from_dict


def test_knowledge_catalog_has_valid_provenance_and_is_immutable_to_consumers():
    document = ontology_document()
    assert validate_document(document) is document
    assert len(document["belief_dimensions"]) == 8
    document["sources"].clear()
    assert ontology_document()["sources"]
    roles = {role.name: role for role in unit_roles()}
    assert "air" in roles["stalkers"].domains
    assert "air" not in roles["immortals"].domains
    assert roles["high_templar"].requires_opt_in == "storm"
    assert roles["archons"].domains == ("ground", "air")
    assert roles["archons"].producers == ("HIGHTEMPLAR",)
    with pytest.raises(FrozenInstanceError):
        roles["immortals"].supply = 0


@pytest.mark.parametrize("broken", ["source", "unit", "question", "schema", "duplicate"])
def test_invalid_ontology_relations_fail_closed(broken):
    document = ontology_document()
    if broken == "source":
        document["unit_roles"][0]["sources"] = ["unverified"]
    elif broken == "unit":
        document["unit_roles"][0]["unit"] = "INVENTED_UNIT"
    elif broken == "question":
        document["belief_dimensions"][0]["question"] = "omniscient"
    elif broken == "duplicate":
        document["belief_dimensions"].append(document["belief_dimensions"][0])
    else:
        document["schema_version"] = 99
    with pytest.raises(ValueError):
        validate_document(document)


def test_live_beliefs_use_catalog_relations_and_record_ontology_identity():
    for kind in technology_signals("air"):
        belief = OpponentBeliefModel().observe(100, {"known_enemy_tech": [kind]})
        assert belief.air.support == 0.8
        assert belief.ontology_id == ontology_document()["ontology_id"]
    data = belief.to_dict()
    data["ontology_id"] = "future-incompatible"
    assert beliefs_from_dict(data) is None
