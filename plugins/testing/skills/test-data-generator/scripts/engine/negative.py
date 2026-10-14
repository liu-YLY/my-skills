import copy

from .common import Budget, ProfileError, digest, json_equal
from .validator import validate_data


def expected_cases(profile, scenario_ids):
    result = {}
    for scenario in profile["negative_scenarios"]:
        base = next(s for s in profile["scenarios"] if s["id"] == scenario["base_scenario"])
        entity = base["entity"]
        indexes = [i for i, value in enumerate(scenario_ids[entity]) if value == base["id"]]
        if len(indexes) < scenario["count"]:
            raise ProfileError(f"{scenario['id']}: insufficient legal baseline records")
        for ordinal, index in enumerate(indexes[:scenario["count"]]):
            result[f"{scenario['id']}:{ordinal + 1}"] = (scenario, entity, index)
    return result


def changed_record(record, mutations):
    result = copy.deepcopy(record)
    for mutation in mutations:
        if mutation["op"] == "set":
            result[mutation["field"]] = mutation["value"]
        else:
            result.pop(mutation["field"], None)
    return result


def build_negative_cases(profile, data, scenario_ids, budget=None):
    budget = budget or Budget(profile["generation"]["limits"])
    baseline = validate_data(profile, data, budget)
    if baseline["error_count"]:
        raise ProfileError("negative samples require a validated legal baseline")
    dataset_id = digest(data)
    cases = []
    for case_id, (scenario, entity, index) in expected_cases(profile, scenario_ids).items():
        budget.check()
        record = data[entity][index]
        cases.append({"case_id": case_id, "scenario_id": scenario["id"], "entity": entity,
                      "record_index": index, "base_dataset_id": dataset_id,
                      "base_key": [record[name] for name in profile["entities"][entity]["primary_key"]],
                      "input_record": changed_record(record, scenario["mutations"]),
                      "mutations": scenario["mutations"],
                      "expected_rule_violations": sorted(scenario["expected_rule_violations"]),
                      "expected_system_result": "pending-confirmation"})
    return cases


def validate_negative_cases(profile, data, scenario_ids, cases, budget=None):
    budget = budget or Budget(profile["generation"]["limits"])
    expected = expected_cases(profile, scenario_ids)
    actual = {}
    issues = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("case_id"), str):
            issues.append("invalid negative case envelope")
            continue
        if case["case_id"] in actual:
            issues.append(f"duplicate negative case: {case['case_id']}")
        actual[case["case_id"]] = case
    if set(actual) != set(expected):
        issues.append("negative case IDs or count differ from the profile")
    dataset_id = digest(data)
    results = []
    for case_id, (scenario, entity, index) in expected.items():
        budget.check()
        case = actual.get(case_id)
        if case is None:
            continue
        record = data[entity][index]
        expected_ids = sorted(scenario["expected_rule_violations"])
        metadata_ok = (case.get("entity") == entity and type(case.get("record_index")) is int
                       and case.get("record_index") == index
                       and case.get("scenario_id") == scenario["id"]
                       and case.get("base_dataset_id") == dataset_id
                       and json_equal(case.get("base_key"), [record[name] for name in profile["entities"][entity]["primary_key"]])
                       and json_equal(case.get("expected_rule_violations"), expected_ids)
                       and json_equal(case.get("mutations"), scenario["mutations"])
                       and json_equal(case.get("input_record"), changed_record(record, scenario["mutations"])))
        context = dict(data)
        context[entity] = list(data[entity])
        context[entity][index] = case.get("input_record")
        report = validate_data(profile, context, budget, check_scenarios=False)
        observed = report["violation_ids"]
        matched = metadata_ok and observed == expected_ids
        results.append({"case_id": case_id, "matched": matched, "metadata_valid": metadata_ok,
                        "expected_rule_violations": expected_ids, "observed_rule_violations": observed,
                        "not_evaluable": report["rule_summary"]["not_evaluable"],
                        "expected_system_result": "pending-confirmation"})
    mismatches = sum(not result["matched"] for result in results)
    budget.check()
    return {"validation_status": "failed" if issues or mismatches else "passed",
            "expected_cases": len(expected), "completed_cases": len(results),
            "mismatches": mismatches, "issues": issues, "cases": results}
