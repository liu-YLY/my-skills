import copy
from collections import Counter

import pytest

from engine.common import ProfileError
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
