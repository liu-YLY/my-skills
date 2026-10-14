import copy
from decimal import Decimal

import pytest

from engine.common import ProfileError, ResourceError, timestamp
from engine.generators import generate_entity
from engine.profile import inspect_profile, normalize


def simple(fields, count=30):
    profile = normalize({"schema_version": "1.0", "profile_id": "scalar-tests",
        "default_source_ids": ["contract"], "sources": [{"id": "contract", "kind": "example", "reference": "test"}],
        "generation": {"seed": 42, "reference_datetime": "2026-10-14T00:00:00Z"},
        "entities": {"item": {"count": count, "primary_key": ["id"], "fields": {
            "id": {"type": "string", "generator": {"kind": "sequence", "width": 4}}, **fields}}}})
    inspect_profile(profile)
    return profile


def test_precise_decimal_integer_boolean_and_choice():
    profile = simple({
        "money": {"type": "decimal", "min": "0.01", "max": "99999.99", "scale": 2, "generator": {"kind": "decimal"}},
        "number": {"type": "integer", "min": -3, "max": 3, "generator": {"kind": "integer"}},
        "enabled": {"type": "boolean", "generator": {"kind": "choice"}},
        "label": {"type": "string", "enum": ["中文", "comma,value"], "generator": {"kind": "choice"}}})
    rows, _ = generate_entity(profile, "item")
    assert rows == generate_entity(copy.deepcopy(profile), "item")[0]
    assert len(rows) == 30 and len({r["id"] for r in rows}) == 30
    assert all(Decimal("0.01") <= Decimal(r["money"]) <= Decimal("99999.99") for r in rows)
    assert all(len(r["money"].split(".")[1]) == 2 for r in rows)
    assert all(isinstance(r["enabled"], bool) and -3 <= r["number"] <= 3 for r in rows)


def test_relative_times_follow_field_dependency_not_alphabet():
    profile = simple({
        "z_create": {"type": "datetime", "generator": {"kind": "datetime_window", "min_offset_seconds": 0, "max_offset_seconds": 10}},
        "a_pay": {"type": "datetime", "generator": {"kind": "relative_datetime", "field": "z_create", "min_seconds": 0, "max_seconds": 60}}})
    rows, _ = generate_entity(profile, "item")
    assert all(0 <= (timestamp(r["a_pay"]) - timestamp(r["z_create"])).total_seconds() <= 60 for r in rows)


def test_exact_scenarios_and_boundary_values():
    profile = simple({"amount": {"type": "decimal", "min": "0.01", "max": "9.99", "scale": 2, "generator": {"kind": "decimal"}}}, 4)
    profile["scenarios"] = [{"id": "min", "entity": "item", "kind": "boundary", "count": 2, "set": {"amount": "0.01"}},
                            {"id": "max", "entity": "item", "kind": "boundary", "count": 2, "set": {"amount": "9.99"}}]
    inspect_profile(profile)
    rows, ids = generate_entity(profile, "item")
    assert ids == ["min", "min", "max", "max"]
    assert [r["amount"] for r in rows] == ["0.01", "0.01", "9.99", "9.99"]
    assert len({r["id"] for r in rows}) == 4


def test_nullable_constant_and_bounded_impossible_values():
    profile = simple({"note": {"type": "string", "nullable": True, "generator": {"kind": "constant", "value": None}}}, 1)
    assert generate_entity(profile, "item")[0][0]["note"] is None
    profile["entities"]["item"]["fields"]["note"] = {"type": "string", "pattern": "^valid$", "generator": {"kind": "constant", "value": "invalid"}}
    with pytest.raises(ResourceError, match="128"):
        generate_entity(profile, "item")


def test_unique_integer_capacity_and_datetime_cycles():
    profile = simple({"slot": {"type": "integer", "min": 0, "max": 29, "unique": True, "generator": {"kind": "integer"}}})
    assert len({r["slot"] for r in generate_entity(profile, "item")[0]}) == 30
    profile["entities"]["item"]["fields"]["slot"]["max"] = 1
    with pytest.raises(ProfileError, match="capacity"):
        inspect_profile(profile)
    profile = simple({}, 1)
    fields = profile["entities"]["item"]["fields"]
    fields["a"] = {"type": "datetime", "generator": {"kind": "relative_datetime", "field": "b", "min_seconds": 0, "max_seconds": 1}}
    fields["b"] = {"type": "datetime", "generator": {"kind": "relative_datetime", "field": "a", "min_seconds": 0, "max_seconds": 1}}
    with pytest.raises(ProfileError, match="cycle"):
        inspect_profile(profile)
