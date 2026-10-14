import math
import re
from collections import Counter
from decimal import Decimal, localcontext

from .common import Budget, comparable, json_equal, timestamp, typed
from .generators import schedule
from .profile import inspect_profile


class Results:
    def __init__(self, ids, detail_limit):
        self.checks = {key: {"evaluated": 0, "applicable": 0, "failed": 0, "not_evaluable": 0} for key in ids}
        self.error_count = 0
        self.errors = []
        self.violation_ids = set()
        self.detail_limit = detail_limit

    def add(self, key, valid, entity=None, index=None, field=None, expected=None, actual=None, applicable=True):
        check = self.checks[key]
        if valid is None:
            check["not_evaluable"] += 1
            return
        check["evaluated"] += 1
        check["applicable"] += int(applicable)
        if not valid:
            check["failed"] += 1
            self.error_count += 1
            self.violation_ids.add(key)
            if len(self.errors) < self.detail_limit:
                if isinstance(actual, str) and len(actual) > 160:
                    actual = actual[:160] + "…"
                self.errors.append({"rule_id": key, "entity": entity, "record_index": index,
                                    "field": field, "expected": expected, "actual": safe_observation(actual)})


def safe_observation(value):
    if isinstance(value, float) and not math.isfinite(value):
        return {"invalid_number": str(value)}
    if isinstance(value, list):
        return [safe_observation(item) for item in value]
    if isinstance(value, dict):
        return {key: safe_observation(item) for key, item in value.items()}
    return value


def predicate_matches(predicate, row, fields):
    name, op = predicate["field"], predicate["op"]
    if name not in row:
        return None
    value = row[name]
    if not typed(value, dict(fields[name], nullable=True)):
        return None
    if op == "is_null":
        return value is None
    if op == "not_null":
        return value is not None
    left = comparable(value, fields[name])
    if "other_field" in predicate:
        other = predicate["other_field"]
        if other not in row or not typed(row[other], dict(fields[other], nullable=True)):
            return None
        right = comparable(row[other], fields[other])
    elif op == "in":
        return left in [comparable(v, fields[name]) for v in predicate["value"]]
    else:
        right = comparable(predicate["value"], fields[name])
    if op == "eq":
        return left == right
    if left is None or right is None:
        return None
    return left >= right if op == "gte" else left <= right


def scenario_matches(profile, scenario, row, fields, index):
    for name, value in (scenario or {}).get("set", {}).items():
        if name not in row or not json_equal(row[name], value):
            return False
    for name, generator in (scenario or {}).get("generators", {}).items():
        if name not in row:
            return False
        value, kind = row[name], generator["kind"]
        if kind == "constant" and not json_equal(value, generator["value"]):
            return False
        if kind == "choice":
            candidates = generator.get("values", fields[name].get("enum", [False, True]))
            if not any(json_equal(value, item) for item in candidates):
                return False
        if kind == "sequence":
            expected = generator.get("prefix", "") + str(generator.get("start", 1) + index).zfill(generator["width"])
            if value != expected:
                return False
        if kind in ("datetime_window", "relative_datetime"):
            base = profile["generation"].get("reference_datetime") if kind == "datetime_window" else row.get(generator["field"])
            if not typed(value, {"type": "datetime"}) or not typed(base, {"type": "datetime"}):
                return None
            low, high = ((generator["min_offset_seconds"], generator["max_offset_seconds"]) if kind == "datetime_window"
                         else (generator["min_seconds"], generator["max_seconds"]))
            if not low <= (timestamp(value) - timestamp(base)).total_seconds() <= high:
                return False
    return True


def validate_data(profile, data, budget=None, detail_limit=200, check_scenarios=True):
    plan = inspect_profile(profile, for_generation=False)
    results = Results(plan["check_ids"], detail_limit)
    budget = budget or Budget(profile["generation"]["limits"])
    entities = profile["entities"]
    results.add("N-dataset-entities", isinstance(data, dict) and set(data) == set(entities),
                expected=sorted(entities), actual=sorted(data) if isinstance(data, dict) else "not an object")
    data = data if isinstance(data, dict) else {}
    for entity, spec in entities.items():
        raw = data.get(entity)
        rows = raw if isinstance(raw, list) else []
        results.add(f"N-{entity}-count", isinstance(raw, list) and len(rows) == spec["count"], entity,
                    expected=spec["count"], actual=len(rows) if isinstance(raw, list) else "missing or not an array")
        fields = spec["fields"]
        unique_groups = [(f"K-{entity}-primary", spec["primary_key"]),
                         *[(f"K-{entity}-unique-{i}", key) for i, key in enumerate(spec.get("unique_keys", []))],
                         *[(f"F-{entity}.{name}-unique", [name]) for name, field in fields.items() if field.get("unique")]]
        seen = {key: set() for key, _ in unique_groups}
        expected_scenarios = schedule(profile, entity)
        for index, raw_row in enumerate(rows):
            budget.check()
            valid_row = isinstance(raw_row, dict)
            results.add(f"F-{entity}-record", valid_row, entity, index, expected="object", actual=type(raw_row).__name__)
            row = raw_row if valid_row else {}
            results.add(f"F-{entity}-fields", set(row) <= set(fields), entity, index,
                        expected="only declared fields", actual=sorted(set(row) - set(fields)))
            for name, field in fields.items():
                prefix = f"F-{entity}.{name}"
                present = name in row
                results.add(f"{prefix}-required", present, entity, index, name, "present", "present" if present else "missing")
                if not present:
                    continue
                value = row[name]
                results.add(f"{prefix}-nullable", value is not None or field.get("nullable", False), entity, index, name,
                            "nullable" if field.get("nullable") else "non-null", value)
                type_ok = typed(value, dict(field, nullable=True))
                results.add(f"{prefix}-type", type_ok, entity, index, name, field["type"], value)
                if type_ok and value is None:
                    for suffix, keys in {"enum": ("enum",), "range": ("min", "max"), "scale": ("scale",),
                                         "length": ("min_length", "max_length"), "pattern": ("pattern",)}.items():
                        if any(key in field for key in keys):
                            results.add(f"{prefix}-{suffix}", True, applicable=False)
                if not type_ok or value is None:
                    continue
                if "enum" in field:
                    results.add(f"{prefix}-enum", value in field["enum"], entity, index, name, field["enum"], value)
                if "min" in field or "max" in field:
                    number = comparable(value, field)
                    valid = ("min" not in field or number >= comparable(field["min"], field)) and (
                        "max" not in field or number <= comparable(field["max"], field))
                    results.add(f"{prefix}-range", valid, entity, index, name,
                                {k: field[k] for k in ("min", "max") if k in field}, value)
                if "scale" in field:
                    with localcontext() as ctx:
                        ctx.prec = 100
                        valid = format(Decimal(value), f".{field['scale']}f") == value
                    results.add(f"{prefix}-scale", valid, entity, index, name, field["scale"], value)
                if "min_length" in field or "max_length" in field:
                    results.add(f"{prefix}-length", field.get("min_length", 0) <= len(value) <= field.get("max_length", 10000),
                                entity, index, name, {k: field[k] for k in ("min_length", "max_length") if k in field}, len(value))
                if "pattern" in field:
                    results.add(f"{prefix}-pattern", bool(re.search(field["pattern"], value)), entity, index, name, field["pattern"], value)
            for key_id, names in unique_groups:
                if any(name not in row or not typed(row[name], dict(fields[name], nullable=True)) for name in names):
                    results.add(key_id, None)
                    continue
                key = tuple(row[name] for name in names)
                if None in key:
                    results.add(key_id, True, applicable=False)
                    continue
                results.add(key_id, key not in seen[key_id], entity, index, names, "unique", list(key))
                seen[key_id].add(key)
            if check_scenarios:
                scenario = expected_scenarios[index] if index < len(expected_scenarios) else None
                match = scenario_matches(profile, scenario, row, fields, index) if index < len(expected_scenarios) else False
                results.add(f"S-{entity}-distribution", match, entity, index,
                            expected={"scenario": (scenario or {}).get("id"), "set": (scenario or {}).get("set", {}),
                                      "generators": (scenario or {}).get("generators", {})}, actual="matched" if match else "scenario constraints differ")
            for rule in profile["rules"]:
                if rule["entity"] != entity:
                    continue
                condition = predicate_matches(rule["when"], row, fields) if "when" in rule else True
                if condition is False:
                    results.add(rule["id"], True, applicable=False)
                elif condition is None:
                    results.add(rule["id"], None)
                else:
                    assertion = predicate_matches(rule["assert"], row, fields)
                    if assertion is None and rule["assert"]["field"] in row and row[rule["assert"]["field"]] is None:
                        assertion = False
                    results.add(rule["id"], assertion, entity, index, rule["assert"]["field"],
                                rule["assert"], row.get(rule["assert"]["field"]))
    for relation in profile["relations"]:
        budget.check()
        parent, child = relation["parent"], relation["child"]
        parent_rows = data.get(parent["entity"], [])
        child_rows = data.get(child["entity"], [])
        parent_rows = parent_rows if isinstance(parent_rows, list) else []
        child_rows = child_rows if isinstance(child_rows, list) else []
        parent_fields = entities[parent["entity"]]["fields"]
        child_fields = entities[child["entity"]]["fields"]
        keys = set()
        for row in parent_rows:
            if isinstance(row, dict) and all(name in row and row[name] is not None and typed(row[name], parent_fields[name]) for name in parent["fields"]):
                key = tuple(row[name] for name in parent["fields"])
                keys.add(key)
        counts = Counter()
        for index, row in enumerate(child_rows):
            budget.check()
            if not isinstance(row, dict) or any(name not in row or not typed(row[name], dict(child_fields[name], nullable=True)) for name in child["fields"]):
                results.add(relation["id"], None)
                continue
            key = tuple(row[name] for name in child["fields"])
            if all(value is None for value in key):
                results.add(relation["id"], True, applicable=False)
                continue
            valid = None not in key and key in keys
            results.add(relation["id"], valid, child["entity"], index, child["fields"], "existing parent key", list(key))
            if valid:
                counts[key] += 1
        low, high = relation.get("min_children", 0), relation.get("max_children")
        for key in sorted(keys, key=str):
            results.add(relation["id"], counts[key] >= low and (high is None or counts[key] <= high),
                        parent["entity"], field=parent["fields"], expected={"min_children": low, "max_children": high}, actual=counts[key])
    scenario_ids = {f"S-{entity}-distribution" for entity in entities}
    unexecuted = [key for key, counts in results.checks.items() if not counts["evaluated"]
                  and (check_scenarios or key not in scenario_ids)]
    incomplete = sorted(key for key, counts in results.checks.items() if counts["not_evaluable"]
                        and (check_scenarios or key not in scenario_ids))
    status = "failed" if results.error_count else "incomplete" if plan["issues"] or unexecuted or incomplete else "passed"
    budget.check()
    return {"schema_version": "1.0", "profile_id": profile["profile_id"], "profile_hash": plan["profile_hash"],
            "generation_status": "not_run", "validation_status": status, "system_execution_status": "not_run",
            "error_count": results.error_count, "errors": results.errors,
            "errors_truncated": results.error_count > len(results.errors), "violation_ids": sorted(results.violation_ids),
            "checks": results.checks, "issues": plan["issues"],
            "unexecuted_checks": sorted(unexecuted),
            "incomplete_checks": incomplete,
            "rule_summary": {"declared": len(results.checks), "implemented": len(results.checks),
                             "executed": sum(item["evaluated"] > 0 for item in results.checks.values()),
                             "not_evaluable": sum(item["not_evaluable"] for item in results.checks.values()),
                             "pending": len(plan["issues"])}}
