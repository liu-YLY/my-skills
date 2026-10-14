import copy

from engine.generators import generate_entity
from engine.profile import inspect_profile
from engine.relations import generate_dataset
from engine.validator import validate_data
from test_generators import simple
from test_relations import linked


def test_independent_validator_finds_range_type_precision_and_duplicates():
    profile = simple({"amount": {"type": "decimal", "min": "0.01", "max": "9.99", "scale": 2, "generator": {"kind": "decimal"}}}, 4)
    rows, _ = generate_entity(profile, "item")
    assert validate_data(profile, {"item": rows})["validation_status"] == "passed"
    rows[0]["amount"] = "0.00"
    rows[1]["amount"] = 1.5
    rows[2]["amount"] = "1.234"
    rows[3]["id"] = rows[0]["id"]
    report = validate_data(profile, {"item": rows})
    assert set(report["violation_ids"]) == {"F-item.amount-range", "F-item.amount-type", "F-item.amount-scale", "K-item-primary"}
    assert report["error_count"] == 4 and report["system_execution_status"] == "not_run"


def test_deleted_field_and_invalid_record_are_reported_without_crash():
    profile = simple({}, 2)
    report = validate_data(profile, {"item": [{}, False]})
    assert report["validation_status"] == "failed"
    assert "F-item.id-required" in report["violation_ids"]
    assert "F-item-record" in report["violation_ids"]
    assert report["rule_summary"]["not_evaluable"] > 0


def test_cross_tenant_fk_and_wrong_child_count():
    profile = linked(True)
    data, _, _ = generate_dataset(profile)
    data["child"][0]["tenant"] = "unknown"
    report = validate_data(profile, data)
    assert report["validation_status"] == "failed" and "belongs" in report["violation_ids"]
    data["child"].pop()
    assert "N-child-count" in validate_data(profile, data)["violation_ids"]


def test_conditional_timestamp_rules_and_not_evaluable_operands():
    profile = simple({
        "status": {"type": "string", "enum": ["pending", "paid"], "generator": {"kind": "constant", "value": "paid"}},
        "created": {"type": "datetime", "generator": {"kind": "constant", "value": "2026-10-14T00:00:00Z"}},
        "paid": {"type": "datetime", "nullable": True, "generator": {"kind": "constant", "value": "2026-10-14T00:00:00Z"}}}, 2)
    profile["rules"] = [{"id": "needs-pay", "entity": "item", "when": {"field": "status", "op": "eq", "value": "paid"},
                         "assert": {"field": "paid", "op": "not_null"}},
                        {"id": "time-order", "entity": "item", "when": {"field": "paid", "op": "not_null"},
                         "assert": {"field": "paid", "op": "gte", "other_field": "created"}}]
    inspect_profile(profile)
    rows, _ = generate_entity(profile, "item")
    assert validate_data(profile, {"item": rows})["validation_status"] == "passed"
    rows[0]["paid"] = None
    rows[1]["paid"] = "not-a-date"
    report = validate_data(profile, {"item": rows})
    assert set(report["violation_ids"]) == {"needs-pay", "F-item.paid-type"}
    assert report["checks"]["time-order"]["not_evaluable"] == 1


def test_preview_never_claims_pass_and_error_detail_limit_keeps_full_counts():
    profile = simple({}, 3)
    profile["sources"][0]["kind"] = "sample"
    profile["generation"]["mode"] = "preview"
    rows, _ = generate_entity(profile, "item")
    assert validate_data(profile, {"item": rows})["validation_status"] == "incomplete"
    rows = [{}, {}, {}]
    report = validate_data(profile, {"item": rows}, detail_limit=1)
    assert report["error_count"] == 3 and len(report["errors"]) == 1 and report["errors_truncated"]


def test_manifest_or_entity_claim_does_not_replace_data_checks():
    profile = simple({}, 1)
    rows, _ = generate_entity(profile, "item")
    data = {"item": rows, "unexpected": []}
    report = validate_data(profile, data)
    assert report["violation_ids"] == ["N-dataset-entities"]
    valid = copy.deepcopy(data)
    del valid["unexpected"]
    assert validate_data(profile, valid)["validation_status"] == "passed"
