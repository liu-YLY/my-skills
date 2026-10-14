import copy
import json
import re
from decimal import Decimal, localcontext
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .common import ProfileError, canonical, decimal_value, digest, timestamp, typed

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schemas/profile.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
CHECKER = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


class StrictLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise ProfileError("YAML aliases are unsupported; expand the profile explicitly")
        self.profile_depth = getattr(self, "profile_depth", 0) + 1
        if self.profile_depth > 64:
            raise ProfileError("profile depth exceeds 64")
        try:
            return super().compose_node(parent, index)
        finally:
            self.profile_depth -= 1


def mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ProfileError("configuration keys must be strings")
        if key in result:
            raise ProfileError(f"duplicate configuration key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProfileError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_profile(path):
    path = Path(path)
    if path.stat().st_size > 1048576:
        raise ProfileError("profile exceeds 1 MiB")
    text = path.read_text(encoding="utf-8")
    try:
        raw = (json.loads(text, object_pairs_hook=json_pairs) if path.suffix == ".json"
               else yaml.load(text, Loader=StrictLoader))
    except (yaml.YAMLError, json.JSONDecodeError, RecursionError) as error:
        raise ProfileError(f"invalid profile syntax: {error}") from error
    return normalize(raw)


def normalize(raw):
    stack = [(raw, 0)]
    nodes = 0
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if depth > 64 or nodes > 20000:
            raise ProfileError("profile depth or expanded node limit exceeded")
        if isinstance(value, dict):
            stack.extend((item, depth + 1) for item in value.values())
        elif isinstance(value, list):
            stack.extend((item, depth + 1) for item in value)
    try:
        canonical(raw)
    except (TypeError, ValueError, RecursionError) as error:
        raise ProfileError("profile must contain finite JSON-compatible values") from error
    errors = sorted(CHECKER.iter_errors(raw), key=lambda e: str(list(e.path)))
    if errors:
        error = errors[0]
        raise ProfileError(f"{'/'.join(map(str, error.path)) or 'profile'}: {error.message}")
    def integers(value):
        if isinstance(value, dict):
            return {key: integers(item) for key, item in value.items()}
        if isinstance(value, list):
            return [integers(item) for item in value]
        return int(value) if isinstance(value, float) and value.is_integer() else value
    profile = integers(raw)
    profile.setdefault("profile_version", "1.0.0")
    profile.setdefault("purpose", "test")
    for key in ("relations", "rules", "scenarios", "negative_scenarios"):
        profile.setdefault(key, [])
    settings = profile.setdefault("generation", {})
    settings.setdefault("mode", "strict")
    settings.setdefault("seed", 0)
    settings.setdefault("output_formats", ["json"])
    limits = settings.setdefault("limits", {})
    for key, value in {"max_total_rows": 100000, "max_output_bytes": 104857600,
                       "max_relation_candidates": 200000,
                       "timeout_seconds": 120}.items():
        limits.setdefault(key, value)
    return profile


def unique_ids(items, label):
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ProfileError(f"duplicate {label} ID")
    return {item["id"]: item for item in items}


def order_graph(nodes, dependencies, label):
    remaining = {name: set(dependencies.get(name, ())) for name in nodes}
    result = []
    while remaining:
        ready = sorted(name for name, deps in remaining.items() if not deps)
        if not ready:
            raise ProfileError(f"{label} dependency cycle: {', '.join(sorted(remaining))}")
        for name in ready:
            result.append(name)
            del remaining[name]
        for deps in remaining.values():
            deps.difference_update(ready)
    return result


def check_generator(profile, entity, name, field, generator, for_generation=True):
    fields = profile["entities"][entity]["fields"]
    kind = generator["kind"]
    required_type = {"sequence": "string", "integer": "integer", "decimal": "decimal",
                     "datetime_window": "datetime", "relative_datetime": "datetime", "faker": "string"}.get(kind)
    if required_type and field["type"] != required_type:
        raise ProfileError(f"{entity}.{name}: {kind} requires {required_type}")
    if kind == "constant" and not typed(generator["value"], field):
        raise ProfileError(f"{entity}.{name}: constant has incompatible type or nullability")
    if kind == "choice":
        values = generator.get("values", field.get("enum"))
        if values is None and field["type"] == "boolean":
            values = [False, True]
        if not values or any(not typed(value, field) for value in values):
            raise ProfileError(f"{entity}.{name}: choice requires compatible values or enum")
    if kind in ("integer", "decimal") and not {"min", "max"} <= field.keys():
        raise ProfileError(f"{entity}.{name}: numeric generator needs min and max")
    if kind == "sequence" and for_generation:
        last = generator.get("start", 1) + profile["entities"][entity]["count"] - 1
        if last >= 10 ** generator["width"]:
            raise ProfileError(f"{entity}.{name}: sequence capacity exhausted")
        length = len(generator.get("prefix", "")) + generator["width"]
        if length > field.get("max_length", 10000) or length < field.get("min_length", 0):
            raise ProfileError(f"{entity}.{name}: sequence conflicts with length constraints")
    if kind == "datetime_window":
        if "reference_datetime" not in profile["generation"]:
            raise ProfileError("datetime_window requires reference_datetime")
        timestamp(profile["generation"]["reference_datetime"])
        low, high = generator["min_offset_seconds"], generator["max_offset_seconds"]
        if low > high:
            raise ProfileError(f"{entity}.{name}: reversed datetime window")
    if kind == "relative_datetime":
        base = generator["field"]
        if base not in fields or fields[base]["type"] != "datetime":
            raise ProfileError(f"{entity}.{name}: missing datetime base {base}")
        if generator["min_seconds"] > generator["max_seconds"]:
            raise ProfileError(f"{entity}.{name}: reversed relative window")
    if kind == "reference":
        relation = next((r for r in profile["relations"] if r["id"] == generator["relation"]), None)
        if not relation or relation["child"]["entity"] != entity or name not in relation["child"]["fields"]:
            raise ProfileError(f"{entity}.{name}: invalid reference generator")
    if kind == "faker" and for_generation:
        from .generators import faker_instance
        faker_instance(generator["locale"])
    if kind == "boundary":
        from .generators import boundary_value, permitted
        if not permitted(boundary_value(field, generator), field, check_pattern=False):
            raise ProfileError(f"{entity}.{name}: boundary conflicts with field constraints; use a negative scenario")


def field_order(profile, entity, scenario=None):
    fields = profile["entities"][entity]["fields"]
    fixed = (scenario or {}).get("set", {})
    overrides = (scenario or {}).get("generators", {})
    dependencies = {}
    for name, field in fields.items():
        generator = overrides.get(name, field["generator"])
        if name not in fixed and generator["kind"] == "relative_datetime":
            dependencies[name] = [generator["field"]]
    return order_graph(fields, dependencies, f"{entity} field")


def field_check_ids(entity, name, field):
    prefix = f"F-{entity}.{name}"
    ids = [f"{prefix}-required", f"{prefix}-type", f"{prefix}-nullable"]
    for label, keys in {"range": ("min", "max"), "length": ("min_length", "max_length"),
                        "enum": ("enum",), "pattern": ("pattern",), "scale": ("scale",)}.items():
        if any(key in field for key in keys):
            ids.append(f"{prefix}-{label}")
    if field.get("unique"):
        ids.append(f"{prefix}-unique")
    return ids


def inspect_profile(profile, for_generation=True):
    entities = profile["entities"]
    if len({name.casefold() for name in entities}) != len(entities):
        raise ProfileError("entity file names conflict on case-insensitive filesystems")
    sources = unique_ids(profile["sources"], "source")
    relations = unique_ids(profile["relations"], "relation")
    rules = unique_ids(profile["rules"], "rule")
    scenarios = unique_ids(profile["scenarios"], "scenario")
    unique_ids(profile["negative_scenarios"], "negative scenario")
    dependencies = {}
    check_ids = ["N-dataset-entities"]
    issues = []

    def provenance(item, label, inherited=None):
        ids = item.get("source_ids", inherited or profile.get("default_source_ids", []))
        if not ids or any(key not in sources for key in ids):
            raise ProfileError(f"{label}: missing or unknown source")
        default = "candidate" if all(sources[key]["kind"] == "sample" for key in ids) else "confirmed"
        status = item.get("confirmation", default)
        if status != "confirmed":
            issues.append({"target": label, "confirmation": status, "source_ids": ids})
        return ids

    if any(key not in sources for key in profile.get("default_source_ids", [])):
        raise ProfileError("unknown default source")
    for entity, spec in entities.items():
        source_ids = provenance(spec, entity)
        fields = spec["fields"]
        entity_scenarios = [item for item in scenarios.values() if item["entity"] == entity]
        for key in [spec["primary_key"], *spec.get("unique_keys", [])]:
            if any(name not in fields for name in key):
                raise ProfileError(f"{entity}: unknown key field")
        if any(fields[name].get("nullable", False) for name in spec["primary_key"]):
            raise ProfileError(f"{entity}: primary keys cannot be nullable")
        check_ids.extend([f"N-{entity}-count", f"K-{entity}-primary", f"S-{entity}-distribution",
                          f"F-{entity}-record", f"F-{entity}-fields"])
        check_ids.extend(f"K-{entity}-unique-{i}" for i, _ in enumerate(spec.get("unique_keys", [])))
        for name, field in fields.items():
            provenance(field, f"{entity}.{name}", source_ids)
            kind = field["type"]
            if any(k in field for k in ("min", "max")):
                if kind not in ("integer", "decimal"):
                    raise ProfileError(f"{entity}.{name}: range requires integer or decimal")
                for bound in ("min", "max"):
                    if bound in field and not typed(field[bound], field):
                        raise ProfileError(f"{entity}.{name}: invalid {bound}")
                if {"min", "max"} <= field.keys():
                    low, high = field["min"], field["max"]
                    if kind == "decimal":
                        low, high = decimal_value(low), decimal_value(high)
                    if low > high:
                        raise ProfileError(f"{entity}.{name}: reversed range")
            if "scale" in field and kind != "decimal":
                raise ProfileError(f"{entity}.{name}: scale requires decimal")
            if kind == "decimal":
                field.setdefault("scale", 2)
                with localcontext() as ctx:
                    ctx.prec = 100
                    factor = Decimal(10) ** field["scale"]
                    for bound in ("min", "max"):
                        if bound in field and decimal_value(field[bound]) * factor % 1:
                            raise ProfileError(f"{entity}.{name}: range exceeds decimal scale")
            if any(k in field for k in ("min_length", "max_length", "pattern")) and kind != "string":
                raise ProfileError(f"{entity}.{name}: string constraint on non-string")
            if field.get("min_length", 0) > field.get("max_length", 10000):
                raise ProfileError(f"{entity}.{name}: reversed length range")
            if "pattern" in field:
                try:
                    re.compile(field["pattern"])
                except re.error as error:
                    raise ProfileError(f"{entity}.{name}: invalid pattern") from error
            if "enum" in field and any(not typed(value, field) for value in field["enum"]):
                raise ProfileError(f"{entity}.{name}: incompatible enum")
            if for_generation and "generator" not in field:
                raise ProfileError(f"{entity}.{name}: generation requires a generator")
            uses_default = not entity_scenarios or any(name not in item.get("set", {}) and name not in item.get("generators", {}) for item in entity_scenarios)
            if for_generation and uses_default:
                check_generator(profile, entity, name, field, field["generator"])
            values = field.get("generator", {}).get("values", field.get("enum"))
            if for_generation and (field.get("unique") or name in spec["primary_key"] and len(spec["primary_key"]) == 1):
                capacity = len(values) if values else None
                if field["generator"]["kind"] == "constant" and field["generator"]["value"] is not None:
                    capacity = 1
                if field["generator"]["kind"] == "choice" and kind == "boolean" and values is None:
                    capacity = 2
                if field["generator"]["kind"] == "integer" and {"min", "max"} <= field.keys():
                    capacity = field["max"] - field["min"] + 1
                if field["generator"]["kind"] == "decimal" and {"min", "max"} <= field.keys():
                    with localcontext() as ctx:
                        ctx.prec = 100
                        capacity = int((decimal_value(field["max"]) - decimal_value(field["min"])) * Decimal(10) ** field["scale"]) + 1
                overridden = any(s["entity"] == entity and (name in s.get("set", {}) or name in s.get("generators", {}))
                                 for s in profile["scenarios"])
                allows_null = field.get("nullable", False) and (
                    field["generator"]["kind"] == "choice" and values is not None and None in values
                    or field["generator"]["kind"] == "constant" and field["generator"]["value"] is None)
                if capacity is not None and capacity < spec["count"] and not overridden and not allows_null:
                    raise ProfileError(f"{entity}.{name}: unique capacity exhausted")
            check_ids.extend(field_check_ids(entity, name, field))
        if for_generation and not entity_scenarios:
            field_order(profile, entity)
    occupied = set()
    for relation in relations.values():
        provenance(relation, relation["id"])
        for endpoint in (relation["child"], relation["parent"]):
            entity = endpoint["entity"]
            if entity not in entities or any(name not in entities[entity]["fields"] for name in endpoint["fields"]):
                raise ProfileError(f"{relation['id']}: unknown endpoint field")
        child, parent = relation["child"], relation["parent"]
        if len(child["fields"]) != len(parent["fields"]):
            raise ProfileError(f"{relation['id']}: mismatched key arity")
        parent_spec = entities[parent["entity"]]
        declared_keys = [parent_spec["primary_key"], *parent_spec.get("unique_keys", [])]
        if len(parent["fields"]) == 1 and parent_spec["fields"][parent["fields"][0]].get("unique"):
            declared_keys.append(parent["fields"])
        if parent["fields"] not in declared_keys:
            raise ProfileError(f"{relation['id']}: parent fields must be a declared unique key")
        for left, right in zip(child["fields"], parent["fields"]):
            target = (child["entity"], left)
            if for_generation and target in occupied:
                raise ProfileError(f"{relation['id']}: overlapping relation fields are unsupported")
            occupied.add(target)
            if entities[child["entity"]]["fields"][left]["type"] != parent_spec["fields"][right]["type"]:
                raise ProfileError(f"{relation['id']}: incompatible key types")
        low, high = relation.get("min_children", 0), relation.get("max_children")
        if high is not None and low > high:
            raise ProfileError(f"{relation['id']}: reversed child bounds")
        dependencies.setdefault(child["entity"], []).append(parent["entity"])
        check_ids.append(relation["id"])
    scenario_counts = {}
    for scenario in scenarios.values():
        provenance(scenario, scenario["id"])
        entity = scenario["entity"]
        if entity not in entities:
            raise ProfileError(f"{scenario['id']}: unknown entity")
        fields = entities[entity]["fields"]
        fixed, overrides = scenario.get("set", {}), scenario.get("generators", {})
        if set(fixed) & set(overrides) or not (set(fixed) | set(overrides)) <= fields.keys():
            raise ProfileError(f"{scenario['id']}: conflicting or unknown field overrides")
        for name, value in fixed.items():
            if not typed(value, fields[name]):
                raise ProfileError(f"{scenario['id']}: incompatible value for {name}")
        for name, generator in overrides.items():
            check_generator(profile, entity, name, fields[name], generator, for_generation)
        if for_generation:
            field_order(profile, entity, scenario)
        scenario_counts[entity] = scenario_counts.get(entity, 0) + scenario["count"]
    for entity, count in scenario_counts.items():
        if count != entities[entity]["count"]:
            raise ProfileError(f"{entity}: scenario counts do not match entity count")
    for rule in rules.values():
        provenance(rule, rule["id"])
        if rule["entity"] not in entities:
            raise ProfileError(f"{rule['id']}: unknown entity")
        fields = entities[rule["entity"]]["fields"]
        for predicate in (rule.get("when"), rule["assert"]):
            if predicate is None:
                continue
            if predicate["field"] not in fields or predicate.get("other_field", predicate["field"]) not in fields:
                raise ProfileError(f"{rule['id']}: unknown predicate field")
            field = fields[predicate["field"]]
            if "other_field" in predicate and fields[predicate["other_field"]]["type"] != field["type"]:
                raise ProfileError(f"{rule['id']}: incompatible predicate types")
            if predicate["op"] in ("gte", "lte") and field["type"] not in ("integer", "decimal", "datetime"):
                raise ProfileError(f"{rule['id']}: ordered comparison requires numeric or datetime fields")
            values = predicate.get("value", [])
            if "value" in predicate:
                values = values if predicate["op"] == "in" else [values]
                if any(not typed(value, dict(field, nullable=True)) for value in values):
                    raise ProfileError(f"{rule['id']}: incompatible predicate value")
        check_ids.append(rule["id"])
    if len(check_ids) != len(set(check_ids)):
        raise ProfileError("rule IDs conflict with generated check IDs")
    for case in profile["negative_scenarios"]:
        provenance(case, case["id"])
        base = scenarios.get(case["base_scenario"])
        if not base or case["count"] > base["count"]:
            raise ProfileError(f"{case['id']}: missing or insufficient base scenario")
        if any(m["field"] not in entities[base["entity"]]["fields"] for m in case["mutations"]):
            raise ProfileError(f"{case['id']}: unknown mutation field")
        for mutation in case["mutations"]:
            if mutation["op"] == "boundary":
                from .generators import boundary_value
                boundary_value(entities[base["entity"]]["fields"][mutation["field"]], mutation)
        if not set(case["expected_rule_violations"]) <= set(check_ids):
            raise ProfileError(f"{case['id']}: unknown expected violation")
    total = sum(spec["count"] for spec in entities.values()) + sum(case["count"] for case in profile["negative_scenarios"])
    if total > profile["generation"]["limits"]["max_total_rows"]:
        raise ProfileError("total record limit exceeded")
    entity_order = order_graph(entities, dependencies, "entity") if for_generation else sorted(entities)
    if issues and profile["generation"]["mode"] == "strict":
        raise ProfileError(f"unconfirmed constraints: {canonical(issues)}")
    if for_generation and relations:
        from .relations import check_capacity
        for relation in relations.values():
            check_capacity(profile, relation)
    planned = []
    if for_generation:
        from .generators import generation_fields, planned_rules
        for entity in entities:
            scopes = [item for item in scenarios.values() if item["entity"] == entity] or [None]
            for scope in scopes:
                fields = generation_fields(profile, entity, scope)
                count = scope["count"] if scope else entities[entity]["count"]
                for name, field in fields.items():
                    if field["generator"]["kind"] == "constant" and field["generator"]["value"] is not None and count > 1:
                        single_key = entities[entity]["primary_key"] == [name] or [name] in entities[entity].get("unique_keys", []) or field.get("unique")
                        if single_key:
                            raise ProfileError(f"{entity}.{name}: unique constant capacity exhausted")
            planned.extend(rule["id"] for rule in planned_rules(profile, entity))
    return {"schema_version": "1.0", "profile_id": profile["profile_id"], "profile_hash": digest(profile),
            "entity_order": entity_order, "total_rows": total,
            "entity_counts": {name: spec["count"] for name, spec in entities.items()},
            "check_ids": sorted(check_ids), "issues": issues,
            "operation": "generate" if for_generation else "validate",
            "planned_rule_ids": sorted(planned), "validation_only_rule_ids": sorted(set(rules) - set(planned)),
            "generation_status": "not_run",
            "validation_status": "not_run", "system_execution_status": "not_run"}
