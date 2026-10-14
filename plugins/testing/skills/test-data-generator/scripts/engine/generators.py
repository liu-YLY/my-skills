import re
from datetime import timedelta
from decimal import Decimal, localcontext

from .common import Budget, ProfileError, ResourceError, canonical, comparable, random_for, timestamp, typed
from .profile import field_order


def schedule(profile, entity):
    scenarios = [s for s in profile["scenarios"] if s["entity"] == entity]
    if not scenarios:
        return [None] * profile["entities"][entity]["count"]
    return [scenario for scenario in scenarios for _ in range(scenario["count"])]


def scalar(field, generator, rng, index, row, settings, reference=None):
    kind = generator["kind"]
    if kind == "constant":
        return generator["value"]
    if kind == "sequence":
        number = generator.get("start", 1) + index
        if number >= 10 ** generator["width"]:
            raise ProfileError("sequence capacity exhausted")
        return generator.get("prefix", "") + str(number).zfill(generator["width"])
    if kind == "choice":
        return rng.choice(generator.get("values", field.get("enum", [False, True])))
    if kind == "integer":
        return rng.randint(field["min"], field["max"])
    if kind == "decimal":
        with localcontext() as ctx:
            ctx.prec = 100
            factor = Decimal(10) ** field["scale"]
            units = rng.randint(int(Decimal(field["min"]) * factor), int(Decimal(field["max"]) * factor))
            return format(Decimal(units) / factor, f".{field['scale']}f")
    if kind in ("datetime_window", "relative_datetime"):
        if kind == "datetime_window":
            base = timestamp(settings["reference_datetime"])
            low, high = generator["min_offset_seconds"], generator["max_offset_seconds"]
        else:
            if row.get(generator["field"]) is None:
                raise ProfileError("relative datetime base is missing or null")
            base = timestamp(row[generator["field"]])
            low, high = generator["min_seconds"], generator["max_seconds"]
        return (base + timedelta(seconds=rng.randint(low, high))).isoformat().replace("+00:00", "Z")
    if kind == "reference":
        if reference is None:
            raise ProfileError("reference generator requires a planned parent key assignment")
        return reference[0]
    raise ProfileError(f"unsupported generator: {kind}")


def permitted(value, field):
    if not typed(value, field):
        return False
    if value is None:
        return True
    if "enum" in field and value not in field["enum"]:
        return False
    if field["type"] in ("integer", "decimal"):
        number = comparable(value, field)
        if "min" in field and number < comparable(field["min"], field):
            return False
        if "max" in field and number > comparable(field["max"], field):
            return False
    if field["type"] == "decimal" and format(Decimal(value), f".{field['scale']}f") != value:
        return False
    if field["type"] == "string":
        if not field.get("min_length", 0) <= len(value) <= field.get("max_length", 10000):
            return False
        if "pattern" in field and not re.search(field["pattern"], value):
            return False
    return True


def unique_values(profile, entity, scenarios, groups, budget):
    """Sample finite single-column keys without replacement or a full range allocation."""
    spec = profile["entities"][entity]
    values_by_field = {}
    for names in groups:
        if len(names) != 1 or names[0] in values_by_field:
            continue
        name = names[0]
        if any(name in (s or {}).get("set", {}) or name in (s or {}).get("generators", {}) for s in scenarios):
            continue
        field = spec["fields"][name]
        kind = field["generator"]["kind"]
        candidates = None
        if kind == "choice" or (kind in ("integer", "decimal") and "enum" in field):
            raw = field["generator"].get("values", field.get("enum", [False, True]))
            if None in raw:  # nullable unique keys permit repeated nulls
                continue
            candidates = list({canonical(v): v for v in raw if permitted(v, field)}.values())
            capacity = len(candidates)
        elif kind in ("integer", "decimal"):
            with localcontext() as ctx:
                ctx.prec = 100
                factor = Decimal(10) ** field.get("scale", 0)
                low = int(Decimal(field["min"]) * factor)
                capacity = int(Decimal(field["max"]) * factor) - low + 1
        else:
            continue
        if spec["count"] > capacity:
            raise ResourceError(f"{entity}.{name}: unique permitted capacity exhausted")
        rng = random_for(profile["generation"]["seed"], entity, name, "unique-pool")
        swaps, values = {}, []
        for index in range(spec["count"]):
            budget.check()
            remaining = capacity - index
            slot = rng.randrange(remaining)
            selected = swaps.get(slot, slot)
            swaps[slot] = swaps.get(remaining - 1, remaining - 1)
            swaps.pop(remaining - 1, None)
            if candidates is not None:
                value = candidates[selected]
            elif kind == "integer":
                value = low + selected
            else:
                with localcontext() as ctx:
                    ctx.prec = 100
                    value = format(Decimal(low + selected) / factor, f".{field['scale']}f")
            values.append(value)
        values_by_field[name] = values
    return values_by_field


def generate_entity(profile, entity, assignments=None, budget=None):
    spec = profile["entities"][entity]
    fields = spec["fields"]
    budget = budget or Budget(profile["generation"]["limits"])
    assignments = assignments or {}
    relations = {r["id"]: r for r in profile["relations"]}
    groups = [spec["primary_key"], *spec.get("unique_keys", []),
              *[[name] for name, field in fields.items() if field.get("unique")]]
    seen = [set() for _ in groups]
    scenarios = schedule(profile, entity)
    planned_values = unique_values(profile, entity, scenarios, groups, budget)
    rows, scenario_ids = [], []
    orders = {}
    for index, scenario in enumerate(scenarios):
        budget.check()
        scenario_id = scenario["id"] if scenario else None
        if scenario_id not in orders:
            orders[scenario_id] = field_order(profile, entity, scenario)
        fixed = (scenario or {}).get("set", {})
        overrides = (scenario or {}).get("generators", {})
        for attempt in range(128):
            budget.check()
            row = {}
            for name in orders[scenario_id]:
                field = fields[name]
                generator = overrides.get(name, field["generator"])
                if name in fixed:
                    value = fixed[name]
                elif name in planned_values:
                    value = planned_values[name][index]
                else:
                    reference = None
                    if generator["kind"] == "reference":
                        relation = relations[generator["relation"]]
                        if generator["relation"] not in assignments:
                            raise ProfileError(f"{entity}.{name}: missing relation assignments")
                        key = assignments[generator["relation"]][index]
                        value_index = relation["child"]["fields"].index(name)
                        reference = (key[value_index] if key is not None else None,)
                    value = scalar(field, generator,
                                   random_for(profile["generation"]["seed"], entity, name, index, attempt),
                                   index, row, profile["generation"], reference)
                row[name] = value
            valid = all(permitted(row[name], field) for name, field in fields.items())
            keys = [tuple(row[name] for name in group) for group in groups]
            duplicate = any(None not in key and key in known for key, known in zip(keys, seen))
            if valid and not duplicate:
                budget.consume_record(row)
                for key, known in zip(keys, seen):
                    if None not in key:
                        known.add(key)
                rows.append({name: row[name] for name in sorted(fields)})
                scenario_ids.append(scenario_id)
                break
        else:
            raise ResourceError(f"{entity} row {index}: constraints or uniqueness unsatisfied after 128 attempts")
    budget.check()
    return rows, scenario_ids
