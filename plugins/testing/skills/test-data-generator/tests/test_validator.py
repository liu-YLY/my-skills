import copy

from engine.generators import generate_entity
from engine.profile import inspect_profile
from engine.relations import generate_dataset
from engine.validator import validate_data
from test_generators import simple
from test_relations import linked


def test_partially_unevaluable_rule_cannot_pass():
    profile = simple({"left": {"type": "integer", "generator": {"kind": "constant", "value": 1}},
                      "right": {"type": "integer", "nullable": True,
                                "generator": {"kind": "constant", "value": 1}}}, 2)
    profile["rules"] = [{"id": "ordered", "entity": "item",
                         "assert": {"field": "left", "op": "gte", "other_field": "right"}}]
    report = validate_data(profile, {"item": [{"id": "0001", "left": 1, "right": None},
                                             {"id": "0002", "left": 1, "right": 1}]})
    assert report["validation_status"] == "incomplete"
    assert report["incomplete_checks"] == ["ordered"]


def test_scenario_generator_constants_and_time_offsets_are_checked():
    profile = simple({"label": {"type": "string", "generator": {"kind": "constant", "value": "A"}},
                      "created": {"type": "datetime", "generator": {"kind": "constant", "value": "2026-10-14T00:00:00Z"}},
                      "expires": {"type": "datetime", "generator": {"kind": "relative_datetime", "field": "created",
                                                                           "min_seconds": 3600, "max_seconds": 3600}}}, 1)
    profile["scenarios"] = [{"id": "one-hour", "entity": "item", "kind": "boundary", "count": 1,
                             "generators": {"label": {"kind": "constant", "value": "A"},
                                            "expires": {"kind": "relative_datetime", "field": "created",
                                                        "min_seconds": 3600, "max_seconds": 3600}}}]
    rows, _ = generate_entity(profile, "item")
    rows[0].update(label="B", expires="2026-10-14T02:00:00Z")
    report = validate_data(profile, {"item": rows})
    assert report["validation_status"] == "failed"
    assert "S-item-distribution" in report["violation_ids"]


def test_explicit_time_delta_rule_is_independent_of_generator():
    profile = simple({"created": {"type": "datetime", "generator": {"kind": "constant", "value": "2026-10-14T00:00:00Z"}},
                      "expires": {"type": "datetime", "generator": {"kind": "constant", "value": "2026-10-14T01:00:00Z"}}}, 1)
    profile["rules"] = [{"id": "one-hour", "entity": "item", "assert": {"field": "expires", "op": "time_delta",
                        "other_field": "created", "min_seconds": 3600, "max_seconds": 3600}}]
    rows, _ = generate_entity(profile, "item")
    assert validate_data(profile, {"item": rows})["validation_status"] == "passed"
    rows[0]["expires"] = "2026-10-14T02:00:00Z"
    assert validate_data(profile, {"item": rows})["violation_ids"] == ["one-hour"]


def test_a_target_rule_with_no_applicable_records_is_incomplete():
    profile = simple({"active": {"type": "boolean", "generator": {"kind": "constant", "value": False}}}, 2)
    profile["rules"] = [{"id": "active-branch", "entity": "item", "when": {"field": "active", "op": "eq", "value": True},
                         "assert": {"field": "id", "op": "not_null"}}]
    profile["scenarios"] = [{"id": "branch", "entity": "item", "kind": "normal", "count": 2,
                             "target_check_ids": ["active-branch"]}]
    rows, _ = generate_entity(profile, "item")
    report = validate_data(profile, {"item": rows})
    assert report["validation_status"] == report["scenario_summary"][0]["validation_status"] == "incomplete"
    assert report["scenario_summary"][0]["target_checks"]["active-branch"]["applicable"] == 0


def test_s_prefix_business_rule_is_not_skipped_with_scenario_checks_disabled():
    profile = simple({"left": {"type": "integer", "generator": {"kind": "constant", "value": 1}},
                      "right": {"type": "integer", "nullable": True, "generator": {"kind": "constant", "value": 1}}}, 1)
    profile["rules"] = [{"id": "S-business", "entity": "item", "assert": {"field": "left", "op": "gte", "other_field": "right"}}]
    report = validate_data(profile, {"item": [{"id": "0001", "left": 1, "right": None}]}, check_scenarios=False)
    assert report["validation_status"] == "incomplete" and report["incomplete_checks"] == ["S-business"]


def test_n_prefix_business_rule_keeps_scene_applicability():
    profile = simple({"active": {"type": "boolean", "generator": {"kind": "choice"}}}, 2)
    profile["rules"] = [{"id": "N-business", "entity": "item", "when": {"field": "active", "op": "eq", "value": True},
                         "assert": {"field": "id", "op": "not_null"}}]
    profile["scenarios"] = [{"id": "off", "entity": "item", "kind": "normal", "count": 1, "set": {"active": False},
                             "target_check_ids": ["N-business"]},
                            {"id": "on", "entity": "item", "kind": "normal", "count": 1, "set": {"active": True}}]
    rows, _ = generate_entity(profile, "item")
    report = validate_data(profile, {"item": rows})
    assert report["validation_status"] == report["scenario_summary"][0]["validation_status"] == "incomplete"
    assert report["scenario_summary"][0]["target_checks"]["N-business"]["applicable"] == 0


def test_relation_target_includes_parent_cardinality_failure():
    profile = linked()
    profile["scenarios"] = [{"id": "children", "entity": "child", "kind": "normal", "count": 12, "target_check_ids": ["belongs"]}]
    data, _, _ = generate_dataset(profile)
    for row in data["child"]:
        row["id"] = data["parent"][0]["id"]
    report = validate_data(profile, data)
    scene = report["scenario_summary"][0]
    assert scene["validation_status"] == "failed"
    assert scene["target_checks"]["belongs"]["scope"] == "relation"
    assert scene["target_checks"]["belongs"]["failed"] > 0


def test_null_reference_scene_cannot_borrow_relation_coverage():
    profile = linked()
    profile["entities"]["child"]["fields"]["id"]["nullable"] = True
    profile["relations"][0]["min_children"] = 1
    profile["scenarios"] = [{"id": "empty", "entity": "child", "kind": "normal", "count": 4, "set": {"id": None},
                             "target_check_ids": ["belongs"]}, {"id": "present", "entity": "child", "kind": "normal", "count": 8}]
    data, _, _ = generate_dataset(profile)
    report = validate_data(profile, data)
    assert report["scenario_summary"][0]["validation_status"] == "incomplete"
    assert report["scenario_summary"][0]["target_checks"]["belongs"]["scene_applicable"] == 0


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


def test_zero_records_leave_required_checks_unexecuted_and_incomplete():
    profile = simple({}, 0)
    report = validate_data(profile, {"item": []})
    assert report["validation_status"] == "incomplete"
    assert "K-item-primary" in report["unexecuted_checks"]
    assert not report["error_count"]
