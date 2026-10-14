import copy
from collections import Counter
from itertools import permutations, product

import pytest

from engine.common import Budget, ProfileError, ResourceError
from engine.profile import inspect_profile, normalize
from engine.relations import generate_dataset


def linked(composite=False):
    key_fields = ["tenant", "id"] if composite else ["id"]
    parent_fields = {"id": {"type": "string", "generator": {"kind": "sequence", "prefix": "P", "width": 3}}}
    if composite:
        parent_fields["tenant"] = {"type": "string", "enum": ["A", "B"], "generator": {"kind": "choice"}}
    child_fields = {name: {"type": "string", "generator": {"kind": "reference", "relation": "belongs"}} for name in key_fields}
    child_fields["child_id"] = {"type": "string", "generator": {"kind": "sequence", "width": 3}}
    return normalize({"schema_version": "1.0", "profile_id": "relations", "sources": [
        {"id": "contract", "kind": "example", "reference": "synthetic relation"}], "default_source_ids": ["contract"],
        "entities": {
            "parent": {"count": 4, "primary_key": key_fields, "fields": parent_fields},
            "child": {"count": 12, "primary_key": ["child_id"], "fields": child_fields}},
        "relations": [{"id": "belongs", "child": {"entity": "child", "fields": key_fields},
                       "parent": {"entity": "parent", "fields": key_fields}, "min_children": 2, "max_children": 4}]})


@pytest.mark.parametrize("composite", [False, True])
def test_keys_exist_and_cardinality_is_constructed(composite):
    profile = linked(composite)
    data, _, _ = generate_dataset(profile)
    names = profile["relations"][0]["parent"]["fields"]
    parents = {tuple(row[name] for name in names) for row in data["parent"]}
    counts = Counter(tuple(row[name] for name in names) for row in data["child"])
    assert set(counts) <= parents
    assert all(2 <= counts[key] <= 4 for key in parents)
    assert data == generate_dataset(copy.deepcopy(profile))[0]


def test_relation_candidate_budget_is_cumulative_across_relations():
    profile = linked()
    profile["generation"]["limits"]["max_relation_candidates"] = 7
    profile["entities"]["child2"] = copy.deepcopy(profile["entities"]["child"])
    profile["entities"]["child2"]["fields"]["id"]["generator"]["relation"] = "belongs2"
    relation = copy.deepcopy(profile["relations"][0])
    relation["id"], relation["child"]["entity"] = "belongs2", "child2"
    profile["relations"].append(relation)
    with pytest.raises(ResourceError, match="relation candidate budget"):
        generate_dataset(profile, Budget(profile["generation"]["limits"]))


@pytest.mark.parametrize("count", [1, 17])
def test_infeasible_counts_fail_before_child_generation(count):
    profile = linked()
    profile["entities"]["child"]["count"] = count
    with pytest.raises(ProfileError, match="infeasible"):
        generate_dataset(profile)


def test_empty_parent_pool_and_entity_cycle():
    profile = linked()
    profile["entities"]["parent"]["count"] = 0
    with pytest.raises(ProfileError, match="infeasible"):
        generate_dataset(profile)
    profile = linked()
    profile["relations"].append({"id": "back", "parent": {"entity": "child", "fields": ["child_id"]},
        "child": {"entity": "parent", "fields": ["id"]}})
    with pytest.raises(ProfileError, match="cycle"):
        inspect_profile(profile)


def test_composite_references_are_never_partially_null():
    profile = linked(True)
    profile["entities"]["child"]["fields"]["tenant"]["nullable"] = True
    profile["scenarios"] = [{"id": "partial", "entity": "child", "kind": "normal", "count": 12, "set": {"tenant": None}}]
    with pytest.raises(ProfileError, match="partial-null"):
        generate_dataset(profile)


def test_nullable_reference_does_not_count_as_a_child():
    profile = linked()
    profile["entities"]["child"]["fields"]["id"]["nullable"] = True
    profile["relations"][0]["min_children"] = 1
    profile["scenarios"] = [{"id": "empty", "entity": "child", "kind": "normal", "count": 4, "set": {"id": None}},
                            {"id": "linked", "entity": "child", "kind": "normal", "count": 8}]
    data, _, _ = generate_dataset(profile)
    assert sum(row["id"] is None for row in data["child"]) == 4
    counts = Counter(row["id"] for row in data["child"] if row["id"] is not None)
    assert all(1 <= counts[row["id"]] <= 4 for row in data["parent"])


def restricted_matching(restrictions, minimum=1):
    profile = linked(True)
    profile["entities"]["parent"]["count"] = profile["entities"]["child"]["count"] = 3
    profile["entities"]["parent"]["fields"]["tenant"]["enum"] = ["a", "d"]
    profile["relations"][0].update(min_children=minimum, max_children=1)
    profile["scenarios"] = [
        {"id": f"parent{i}", "entity": "parent", "kind": "normal", "count": 1, "set": dict(zip(["tenant", "id"], key))}
        for i, key in enumerate([("a", "b"), ("a", "c"), ("d", "b")])]
    profile["scenarios"].extend({"id": f"child{i}", "entity": "child", "kind": "normal", "count": 1, "set": fixed}
                                for i, fixed in enumerate(restrictions))
    return profile


@pytest.mark.parametrize("minimum", [0, 1])
def test_constrained_matching_agrees_with_small_exhaustive_oracle(minimum):
    parents = [{"tenant": "a", "id": "b"}, {"tenant": "a", "id": "c"}, {"tenant": "d", "id": "b"}]
    for restrictions in product([{}, {"tenant": "a"}, {"id": "b"}], repeat=3):
        feasible = any(all(all(parent[name] == value for name, value in fixed.items())
                           for parent, fixed in zip(order, restrictions)) for order in permutations(parents))
        profile = restricted_matching(restrictions, minimum)
        if not feasible:
            with pytest.raises(ProfileError, match="infeasible"):
                generate_dataset(profile)
            continue
        data, _, _ = generate_dataset(profile)
        counts = Counter((row["tenant"], row["id"]) for row in data["child"])
        assert len(counts) == 3 and set(counts.values()) == {1}
        assert all(all(row[name] == value for name, value in fixed.items())
                   for row, fixed in zip(data["child"], restrictions))
