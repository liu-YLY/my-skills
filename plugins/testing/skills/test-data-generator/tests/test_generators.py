import copy
from decimal import Decimal

import pytest

from engine.common import ProfileError, ResourceError, timestamp
from engine.generators import generate_entity
from engine.profile import inspect_profile, normalize
from engine.validator import validate_data


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


def test_nullable_unique_choice_can_repeat_null_beyond_nonnull_capacity():
    profile = simple({"code": {"type": "string", "nullable": True, "unique": True,
                               "generator": {"kind": "choice", "values": [None, "one"]}}}, 30)
    rows, _ = generate_entity(profile, "item")
    assert sum(row["code"] is None for row in rows) >= 29
    assert len([row for row in rows if row["code"] == "one"]) <= 1


def test_scenario_fixed_unique_keys_override_default_generator_capacity():
    profile = simple({}, 1)
    profile["entities"]["item"]["count"] = 3
    profile["entities"]["item"]["fields"]["id"]["generator"] = {"kind": "constant", "value": "default"}
    profile["scenarios"] = [{"id": f"case-{i}", "entity": "item", "kind": "normal", "count": 1,
                             "set": {"id": f"key-{i}"}} for i in range(3)]
    inspect_profile(profile)
    assert {row["id"] for row in generate_entity(profile, "item")[0]} == {"key-0", "key-1", "key-2"}


def test_timezone_offsets_are_normalized_and_naive_times_rejected():
    profile = simple({
        "created": {"type": "datetime", "generator": {"kind": "datetime_window", "min_offset_seconds": 0, "max_offset_seconds": 0}},
        "paid": {"type": "datetime", "generator": {"kind": "relative_datetime", "field": "created", "min_seconds": 60, "max_seconds": 60}}}, 1)
    profile["generation"]["reference_datetime"] = "2026-10-14T08:00:00+08:00"
    rows, _ = generate_entity(profile, "item")
    assert rows[0]["created"] == "2026-10-14T00:00:00Z"
    assert rows[0]["paid"] == "2026-10-14T00:01:00Z"
    profile["entities"]["item"]["fields"]["created"]["generator"] = {"kind": "constant", "value": "2026-10-14T08:00:00"}
    with pytest.raises(ProfileError, match="incompatible type"):
        inspect_profile(profile)


def test_finite_rules_constrain_boolean_choice_and_decimal_sampling():
    profile = simple({"enabled": {"type": "boolean", "nullable": True,
                                  "generator": {"kind": "choice", "values": [None, False, True]}},
                      "amount": {"type": "decimal", "scale": 2, "min": "0.00", "max": "9.99", "generator": {"kind": "decimal"}}}, 50)
    profile["rules"] = [{"id": "enabled", "entity": "item", "assert": {"field": "enabled", "op": "eq", "value": True}},
                        {"id": "minimum", "entity": "item", "assert": {"field": "amount", "op": "gte", "value": "1.234"}},
                        {"id": "maximum", "entity": "item", "assert": {"field": "amount", "op": "lte", "value": "1.259"}}]
    plan = inspect_profile(profile)
    rows, _ = generate_entity(profile, "item")
    assert all(row["enabled"] is True and row["amount"] in {"1.24", "1.25"} for row in rows)
    assert plan["planned_rule_ids"] == ["enabled", "maximum", "minimum"]
    assert validate_data(profile, {"item": rows})["validation_status"] == "passed"


def test_impossible_decimal_equality_is_not_rounded_into_another_rule():
    profile = simple({"amount": {"type": "decimal", "scale": 2, "min": "0.00", "max": "9.99", "generator": {"kind": "decimal"}}}, 1)
    profile["rules"] = [{"id": "precise", "entity": "item", "assert": {"field": "amount", "op": "eq", "value": "1.234"}}]
    with pytest.raises(ProfileError, match="infeasible"):
        inspect_profile(profile)


@pytest.mark.parametrize("locale", ["en_US", "zh_CN"])
def test_faker_is_seeded_per_field_and_email_is_nonroutable(locale):
    pytest.importorskip("faker")
    profile = simple({"name": {"type": "string", "generator": {"kind": "faker", "provider": "name", "locale": locale}},
                      "email": {"type": "string", "unique": True,
                                "generator": {"kind": "faker", "provider": "email", "locale": locale}}}, 20)
    first, _ = generate_entity(profile, "item")
    assert first == generate_entity(copy.deepcopy(profile), "item")[0]
    assert all(row["email"].endswith("@example.invalid") for row in first)
    assert len({row["email"] for row in first}) == 20
    assert all(isinstance(row["name"], str) and row["name"] for row in first)


@pytest.mark.parametrize("field,point,expected", [
    ({"type": "integer", "min": -2, "max": 5}, "min", -2),
    ({"type": "decimal", "min": "0.01", "max": "9.99", "scale": 2}, "max", "9.99"),
    ({"type": "string", "min_length": 2, "max_length": 5}, "max_length", "00000"),
    ({"type": "string", "nullable": True}, "null", None),
])
def test_boundary_recipes_use_declared_contract(field, point, expected):
    profile = simple({"value": dict(field, generator={"kind": "boundary", "point": point, "fill": "0"})}, 1)
    rows, _ = generate_entity(profile, "item")
    assert rows[0]["value"] == expected
    assert validate_data(profile, {"item": rows})["validation_status"] == "passed"


@pytest.mark.parametrize("generator", [{"kind": "choice", "values": ["A"]}, {"kind": "constant", "value": "A"}])
def test_scene_overrides_do_not_inherit_default_sampling_domain(generator):
    profile = simple({"value": {"type": "string", "enum": ["A", "B"], "generator": generator}}, 1)
    profile["scenarios"] = [{"id": "overridden", "entity": "item", "kind": "normal", "count": 1, "set": {"value": "B"}}]
    profile["rules"] = [{"id": "only-B", "entity": "item", "assert": {"field": "value", "op": "eq", "value": "B"}}]
    inspect_profile(profile)
    rows, _ = generate_entity(profile, "item")
    assert rows[0]["value"] == "B" and validate_data(profile, {"item": rows})["validation_status"] == "passed"


def test_ordered_literal_rule_excludes_null_from_nullable_choice():
    profile = simple({"value": {"type": "integer", "nullable": True, "generator": {"kind": "choice", "values": [None, 1]}}}, 10)
    profile["rules"] = [{"id": "minimum", "entity": "item", "assert": {"field": "value", "op": "gte", "value": 1}}]
    rows, _ = generate_entity(profile, "item")
    assert all(row["value"] == 1 for row in rows)
    assert validate_data(profile, {"item": rows})["validation_status"] == "passed"


def test_datetime_literal_domain_is_sampled_within_declared_window():
    profile = simple({"value": {"type": "datetime", "generator": {"kind": "datetime_window", "min_offset_seconds": 0,
                                                                 "max_offset_seconds": 86400}}}, 10)
    profile["rules"] = [{"id": "midday", "entity": "item", "assert": {"field": "value", "op": "eq", "value": "2026-10-14T12:00:00Z"}}]
    rows, _ = generate_entity(profile, "item")
    assert all(row["value"] == "2026-10-14T12:00:00Z" for row in rows)
    assert validate_data(profile, {"item": rows})["validation_status"] == "passed"
