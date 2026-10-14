from collections import Counter

from .common import Budget, ProfileError, canonical, random_for
from .generators import generate_entity, schedule
from .profile import inspect_profile


def requirements(profile, relation):
    entity = relation["child"]["entity"]
    fields = profile["entities"][entity]["fields"]
    result = []
    for scenario in schedule(profile, entity):
        fixed = (scenario or {}).get("set", {})
        overrides = (scenario or {}).get("generators", {})
        restriction = {}
        for name in relation["child"]["fields"]:
            generator = overrides.get(name, fields[name]["generator"])
            if name in fixed:
                restriction[name] = fixed[name]
            elif generator["kind"] == "constant":
                restriction[name] = generator["value"]
            elif generator["kind"] != "reference" or generator["relation"] != relation["id"]:
                raise ProfileError(f"{relation['id']}: relation fields require reference or constant generators")
        nulls = [name for name, value in restriction.items() if value is None]
        if nulls and len(nulls) != len(relation["child"]["fields"]):
            raise ProfileError(f"{relation['id']}: partial-null composite references are unsupported")
        result.append(None if nulls else restriction)
    return result


def bounds(profile, relation):
    child = profile["entities"][relation["child"]["entity"]]
    keys = [child["primary_key"], *child.get("unique_keys", []),
            *[[name] for name, field in child["fields"].items() if field.get("unique")]]
    high = relation.get("max_children")
    if any(set(key) <= set(relation["child"]["fields"]) for key in keys):
        high = min(high, 1) if high is not None else 1
    return relation.get("min_children", 0), high


def check_capacity(profile, relation):
    restrictions = requirements(profile, relation)
    count = sum(item is not None for item in restrictions)
    parents = profile["entities"][relation["parent"]["entity"]]["count"]
    low, high = bounds(profile, relation)
    if count and not parents or count < parents * low or high is not None and count > parents * high:
        raise ProfileError(f"{relation['id']}: infeasible parent/child counts")


def allocate(profile, relation, parent_rows, budget):
    check_capacity(profile, relation)
    parent_fields = relation["parent"]["fields"]
    child_fields = relation["child"]["fields"]
    keys = sorted([tuple(row[name] for name in parent_fields) for row in parent_rows], key=canonical)
    if any(None in key for key in keys) or len(set(keys)) != len(keys):
        raise ProfileError(f"{relation['id']}: parent keys must be non-null and unique")
    low, high = bounds(profile, relation)
    restrictions = requirements(profile, relation)
    eligible = {}
    for restriction in restrictions:
        budget.check()
        if restriction is not None:
            marker = canonical(restriction)
            if marker not in eligible:
                eligible[marker] = [i for i, key in enumerate(keys)
                                    if all(key[child_fields.index(name)] == value
                                           for name, value in restriction.items())]
            if not eligible[marker]:
                raise ProfileError(f"{relation['id']}: no parent key satisfies fixed child fields")
    result = [None] * len(restrictions)
    unassigned = [i for i, restriction in enumerate(restrictions) if restriction is not None]
    unassigned.sort(key=lambda i: len(eligible[canonical(restrictions[i])]))
    counts = Counter()
    rng = random_for(profile["generation"]["seed"], relation["id"], "allocation")
    for parent in range(len(keys)):
        while counts[parent] < low:
            budget.check()
            row = next((i for i in unassigned if parent in eligible[canonical(restrictions[i])]), None)
            if row is None:
                raise ProfileError(f"{relation['id']}: fixed fields prevent lower-bound allocation")
            result[row] = keys[parent]
            counts[parent] += 1
            unassigned.remove(row)
    for row in unassigned:
        budget.check()
        candidates = eligible[canonical(restrictions[row])]
        if high is not None:
            candidates = [p for p in candidates if counts[p] < high]
        if not candidates:
            raise ProfileError(f"{relation['id']}: fixed fields prevent upper-bound allocation")
        parent = rng.choice(candidates)
        result[row] = keys[parent]
        counts[parent] += 1
    return result


def generate_dataset(profile, budget=None):
    plan = inspect_profile(profile)
    budget = budget or Budget(profile["generation"]["limits"])
    for relation in profile["relations"]:
        check_capacity(profile, relation)
    data, scenario_ids = {}, {}
    for entity in plan["entity_order"]:
        assignments = {}
        for relation in profile["relations"]:
            if relation["child"]["entity"] == entity:
                assignments[relation["id"]] = allocate(profile, relation, data[relation["parent"]["entity"]], budget)
        data[entity], scenario_ids[entity] = generate_entity(profile, entity, assignments, budget)
    return data, scenario_ids, plan
