from collections import Counter, deque

from .common import Budget, ProfileError, ResourceError, canonical, random_for
from .generators import generate_entity, generation_fields, permitted, schedule
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


def matching_flows(groups, eligible, parent_count, low, high, budget):
    total = sum(len(rows) for rows in groups.values())
    markers = sorted(groups)
    sink = len(markers) + parent_count + 1
    start, finish = sink + 1, sink + 2
    graph = [[] for _ in range(finish + 1)]
    demands = [0] * len(graph)

    def edge(left, right, minimum, maximum):
        forward = [right, len(graph[right]), maximum - minimum]
        reverse = [left, len(graph[left]), 0]
        graph[left].append(forward)
        graph[right].append(reverse)
        demands[left] -= minimum
        demands[right] += minimum
        return forward

    references = {}
    for index, marker in enumerate(markers):
        count, node = len(groups[marker]), index + 1
        edge(0, node, count, count)
        references[marker] = {parent: edge(node, len(markers) + parent + 1, 0, count) for parent in eligible[marker]}
    for parent in range(parent_count):
        edge(len(markers) + parent + 1, sink, low, total if high is None else high)
    edge(sink, 0, 0, total)
    required = 0
    for node, demand in enumerate(demands):
        if demand > 0:
            edge(start, node, 0, demand)
            required += demand
        elif demand < 0:
            edge(node, finish, 0, -demand)
    flow = 0
    while flow < required:
        budget.check()
        levels = [-1] * len(graph)
        levels[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            budget.check()
            for target, _, capacity in graph[node]:
                if capacity and levels[target] < 0:
                    levels[target] = levels[node] + 1
                    queue.append(target)
        if levels[finish] < 0:
            raise ProfileError("infeasible constrained parent/child matching")
        cursors = [0] * len(graph)
        while flow < required:
            nodes, path = [(start, required - flow)], []
            while nodes and nodes[-1][0] != finish:
                budget.check()
                node, capacity = nodes[-1]
                while cursors[node] < len(graph[node]):
                    candidate = graph[node][cursors[node]]
                    if candidate[2] and levels[candidate[0]] == levels[node] + 1:
                        path.append((node, cursors[node]))
                        nodes.append((candidate[0], min(capacity, candidate[2])))
                        break
                    cursors[node] += 1
                else:
                    levels[node] = -1
                    nodes.pop()
                    if path:
                        previous, _ = path.pop()
                        cursors[previous] += 1
            if not nodes:
                break
            pushed = nodes[-1][1]
            for node, index in path:
                candidate = graph[node][index]
                candidate[2] -= pushed
                graph[candidate[0]][candidate[1]][2] += pushed
            flow += pushed
    return {marker: {parent: len(groups[marker]) - candidate[2] for parent, candidate in references[marker].items()}
            for marker in markers}


def allocate(profile, relation, parent_rows, budget):
    check_capacity(profile, relation)
    parent_fields = relation["parent"]["fields"]
    child_fields = relation["child"]["fields"]
    keys = sorted([tuple(row[name] for name in parent_fields) for row in parent_rows], key=canonical)
    if any(None in key for key in keys) or len(set(keys)) != len(keys):
        raise ProfileError(f"{relation['id']}: parent keys must be non-null and unique")
    low, high = bounds(profile, relation)
    restrictions = requirements(profile, relation)
    fields = generation_fields(profile, relation["child"]["entity"], for_sampling=False)
    groups = {}
    for index, restriction in enumerate(restrictions):
        if restriction is not None:
            groups.setdefault(canonical(restriction), []).append(index)
    budget.consume_relation_candidates(len(groups) * len(keys))
    eligible = {}
    for marker, rows in groups.items():
        budget.check()
        restriction = restrictions[rows[0]]
        eligible[marker] = [i for i, key in enumerate(keys)
                            if all(key[child_fields.index(name)] == value for name, value in restriction.items())
                            and all(permitted(value, fields[name]) for name, value in zip(child_fields, key))]
        if not eligible[marker]:
            raise ProfileError(f"{relation['id']}: infeasible fixed child fields or field constraints")
    result = [None] * len(restrictions)
    rng = random_for(profile["generation"]["seed"], relation["id"], "allocation")
    if len(groups) == 1:
        marker = next(iter(groups))
        rows, candidates = groups[marker], list(eligible[marker])
        if low and len(candidates) != len(keys) or high is not None and len(rows) > len(candidates) * high:
            raise ProfileError(f"{relation['id']}: infeasible restricted parent/child counts")
        counts = Counter()
        offset = 0
        for parent in candidates:
            for _ in range(low):
                result[rows[offset]] = keys[parent]
                counts[parent] += 1
                offset += 1
        pool = [parent for parent in candidates if high is None or counts[parent] < high]
        for row in rows[offset:]:
            budget.check()
            slot = rng.randrange(len(pool))
            parent = pool[slot]
            result[row] = keys[parent]
            counts[parent] += 1
            if high is not None and counts[parent] == high:
                pool[slot] = pool[-1]
                pool.pop()
    elif groups:
        allocations = matching_flows(groups, eligible, len(keys), low, high, budget)
        for marker, rows in groups.items():
            offset = 0
            parents = list(allocations[marker])
            rng.shuffle(parents)
            for parent in parents:
                for _ in range(allocations[marker][parent]):
                    budget.check()
                    result[rows[offset]] = keys[parent]
                    offset += 1
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
