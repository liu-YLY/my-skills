"""确定性场景身份与追溯失效传播；不修改历史证据。"""

import hashlib
import json

from .schemas import InvalidationReport


def stable_scenario_ref(sm, scenario):
    data = scenario.model_dump(mode="json", exclude={
        "id", "stable_ref", "title", "transition_id", "forbidden_id", "source", "notes", "trace_refs", "evidence_type"})
    for field in ["guard_conditions", "forbidden_states", "related_objects"]:
        data[field] = sorted(set(data[field]))
    key = json.dumps([sm.meta.object, data], ensure_ascii=False, sort_keys=True)
    return "SC-" + hashlib.sha256(key.encode()).hexdigest()[:20]


def deduplicate_scenarios(scenarios):
    seen, result = set(), []
    for scenario in scenarios:
        key = json.dumps(scenario.model_dump(mode="json", exclude={"id", "stable_ref"}), sort_keys=True)
        if key not in seen:
            seen.add(key)
            result.append(scenario)
    return result


def affected_by_change(context, changed_refs):
    known = {item.id for item in context.sources + context.artifacts}
    missing = set(changed_refs) - known
    roots = set(changed_refs) & known
    confirmed = {ref: set() for ref in known}
    candidates = {ref: set() for ref in known}
    source_index = {source.id: source for source in context.sources}
    uncorroborated = set()
    for link in context.links:
        if link.upstream not in known or link.downstream not in known:
            missing.update({link.upstream, link.downstream} - known)
            continue
        backed = bool(link.source.strip() and link.source_refs) and all(
            ref in source_index and source_index[ref].availability == "available"
            and bool(source_index[ref].version and source_index[ref].version.strip())
            and bool(source_index[ref].location.strip()) for ref in link.source_refs)
        missing.update(set(link.source_refs) - set(source_index))
        if link.confirmation == "confirmed" and not backed:
            uncorroborated.add(f"{link.upstream}→{link.downstream}: 缺少关联依据或可核验来源版本")
        graph = confirmed if link.confirmation == "confirmed" and backed else candidates
        graph[link.upstream].add(link.downstream)
        for ref in link.source_refs:
            if ref in known:
                graph[ref].add(link.downstream)
    affected, frontier = set(roots), list(roots)
    while frontier:
        for target in confirmed[frontier.pop()] - affected:
            affected.add(target)
            frontier.append(target)
    possible = set()
    for source in affected:
        possible.update(candidates[source])
    frontier = list(possible)
    while frontier:
        source = frontier.pop()
        for target in (confirmed[source] | candidates[source]) - possible:
            possible.add(target)
            frontier.append(target)
    return InvalidationReport(affected=sorted(affected - roots),
                              candidate_impacts=sorted(possible - affected), unmatched_refs=sorted(missing),
                              uncorroborated_links=sorted(uncorroborated))
