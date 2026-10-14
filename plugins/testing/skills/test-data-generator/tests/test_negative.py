import copy

import pytest

from engine.common import ProfileError
from engine.negative import build_negative_cases, validate_negative_cases
from engine.relations import generate_dataset
from test_generators import simple


def negative_profile():
    profile = simple({"amount": {"type": "decimal", "min": "0.01", "max": "9.99", "scale": 2, "generator": {"kind": "decimal"}}}, 3)
    profile["scenarios"] = [{"id": "base", "entity": "item", "kind": "normal", "count": 3}]
    profile["negative_scenarios"] = [
        {"id": "below-min", "base_scenario": "base", "count": 1,
         "mutations": [{"op": "set", "field": "amount", "value": "0.00"}], "expected_rule_violations": ["F-item.amount-range"]},
        {"id": "missing-id", "base_scenario": "base", "count": 1,
         "mutations": [{"op": "remove", "field": "id"}], "expected_rule_violations": ["F-item.id-required"]}]
    return profile


def test_negative_samples_replace_baseline_rows_without_duplicate_keys():
    profile = negative_profile()
    data, ids, _ = generate_dataset(profile)
    original = copy.deepcopy(data)
    cases = build_negative_cases(profile, data, ids)
    result = validate_negative_cases(profile, data, ids, cases)
    assert result["validation_status"] == "passed" and result["completed_cases"] == 2
    assert data == original and len(data["item"]) == 3
    assert result["cases"][0]["observed_rule_violations"] == ["F-item.amount-range"]
    assert result["cases"][1]["observed_rule_violations"] == ["F-item.id-required"]
    assert all(case["expected_system_result"] == "pending-confirmation" for case in cases)


def test_illegal_baseline_is_not_used_for_negative_samples():
    profile = negative_profile()
    data, ids, _ = generate_dataset(profile)
    data["item"][0]["amount"] = "0.00"
    with pytest.raises(ProfileError, match="legal baseline"):
        build_negative_cases(profile, data, ids)


@pytest.mark.parametrize("mutation", [
    lambda cases: cases.pop(),
    lambda cases: cases.append(copy.deepcopy(cases[0])),
    lambda cases: cases[0].update(expected_rule_violations=[]),
    lambda cases: cases[0].update(input_record={"id": "modified", "amount": "1.00"}),
    lambda cases: cases[0].update(record_index=2),
])
def test_missing_duplicate_or_forged_negative_evidence_fails(mutation):
    profile = negative_profile()
    data, ids, _ = generate_dataset(profile)
    cases = build_negative_cases(profile, data, ids)
    mutation(cases)
    result = validate_negative_cases(profile, data, ids, cases)
    assert result["validation_status"] == "failed"


def test_negative_boundary_recipe_uses_decimal_step_and_preserves_baseline():
    profile = negative_profile()
    profile["negative_scenarios"][0]["mutations"] = [{"op": "boundary", "field": "amount", "point": "below_min"}]
    data, ids, _ = generate_dataset(profile)
    baseline = copy.deepcopy(data)
    cases = build_negative_cases(profile, data, ids)
    assert cases[0]["input_record"]["amount"] == "0.00"
    assert validate_negative_cases(profile, data, ids, cases)["validation_status"] == "passed"
    assert data == baseline
