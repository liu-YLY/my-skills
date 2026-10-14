import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from engine.common import ProfileError
from engine.profile import inspect_profile, load_profile, normalize

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def profile():
    return normalize({"schema_version": "1.0", "profile_id": "sample", "sources": [
        {"id": "request", "kind": "user", "reference": "synthetic test contract"}],
        "default_source_ids": ["request"], "entities": {"item": {"count": 3,
        "primary_key": ["id"], "fields": {"id": {"type": "string", "generator": {
            "kind": "sequence", "prefix": "I", "width": 3}}}}}})


def test_inspection_is_repeatable_and_has_no_execution_claim(profile):
    first = inspect_profile(profile)
    assert first == inspect_profile(copy.deepcopy(profile))
    assert first["total_rows"] == 3
    assert first["validation_status"] == first["system_execution_status"] == "not_run"


@pytest.mark.parametrize("change", [
    lambda p: p.update(schema_version="2.0"),
    lambda p: p.update(unknown=True),
    lambda p: p["entities"]["item"].update(count=True),
    lambda p: p["entities"]["item"]["fields"]["id"]["generator"].update(kind="python"),
])
def test_schema_rejects_unknown_or_invalid_configuration(profile, change):
    change(profile)
    with pytest.raises(ProfileError):
        normalize(profile)


@pytest.mark.parametrize("suffix,text", [
    (".yaml", "schema_version: '1.0'\nschema_version: '1.0'\n"),
    (".json", '{"schema_version":"1.0","schema_version":"1.0"}'),
    (".yaml", "!!python/object/apply:os.system ['echo unexpected']"),
])
def test_load_rejects_duplicate_keys_and_yaml_objects(tmp_path, suffix, text):
    path = tmp_path / ("profile" + suffix)
    path.write_text(text)
    with pytest.raises(ProfileError):
        load_profile(path)


def test_missing_source_and_unconfirmed_rules_do_not_pass(profile):
    profile["default_source_ids"] = ["missing"]
    with pytest.raises(ProfileError, match="source"):
        inspect_profile(profile)
    profile["default_source_ids"] = ["request"]
    profile["sources"][0]["kind"] = "sample"
    with pytest.raises(ProfileError, match="unconfirmed"):
        inspect_profile(profile)
    profile["generation"]["mode"] = "preview"
    assert inspect_profile(profile)["issues"]


def test_sequence_capacity_and_total_limit(profile):
    profile["entities"]["item"]["count"] = 1001
    with pytest.raises(ProfileError, match="capacity"):
        inspect_profile(profile)
    profile["entities"]["item"]["count"] = 3
    profile["generation"]["limits"]["max_total_rows"] = 2
    with pytest.raises(ProfileError, match="record limit"):
        inspect_profile(profile)


def test_scenario_distribution_and_unknown_expected_ids(profile):
    profile["scenarios"] = [{"id": "base", "entity": "item", "kind": "normal", "count": 2}]
    with pytest.raises(ProfileError, match="counts"):
        inspect_profile(profile)
    profile["scenarios"][0]["count"] = 3
    profile["negative_scenarios"] = [{"id": "bad", "base_scenario": "base", "count": 1,
        "mutations": [{"op": "remove", "field": "id"}], "expected_rule_violations": ["missing"]}]
    with pytest.raises(ProfileError, match="expected violation"):
        inspect_profile(profile)


def test_cli_inspect_outside_repository(profile, tmp_path):
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(profile))
    result = subprocess.run([sys.executable, str(ROOT / "scripts/run_data.py"), "inspect",
                             "--profile", str(path)], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["total_rows"] == 3
    assert sorted(p.name for p in tmp_path.iterdir()) == ["profile.json"]


def test_integral_configuration_numbers_are_normalized(profile):
    profile["entities"]["item"]["count"] = 3.0
    profile["entities"]["item"]["fields"]["id"]["generator"]["width"] = 3.0
    normalized = normalize(profile)
    assert type(normalized["entities"]["item"]["count"]) is int
    assert type(normalized["entities"]["item"]["fields"]["id"]["generator"]["width"]) is int


def test_requirement_and_sample_sources_do_not_become_sample_only(profile):
    profile["sources"].append({"id": "sample", "kind": "sample", "reference": "synthetic sample"})
    profile["default_source_ids"].append("sample")
    assert not inspect_profile(profile)["issues"]


def test_validation_contract_needs_no_executable_generator(profile):
    del profile["entities"]["item"]["fields"]["id"]["generator"]
    profile = normalize(profile)
    assert inspect_profile(profile, for_generation=False)["total_rows"] == 3
    with pytest.raises(ProfileError, match="generator"):
        inspect_profile(profile)


def test_case_insensitive_entity_names_are_rejected_before_export(profile):
    profile["entities"]["Item"] = copy.deepcopy(profile["entities"]["item"])
    with pytest.raises(ProfileError, match="file name"):
        inspect_profile(profile)


def test_yaml_aliases_and_deep_profiles_are_bounded(tmp_path, profile):
    path = tmp_path / "aliases.yaml"
    path.write_text("base: &base [a, b]\nrepeat: [*base, *base]\n")
    with pytest.raises(ProfileError, match="alias"):
        load_profile(path)
    value = "leaf"
    for _ in range(70):
        value = [value]
    profile["unexpected"] = value
    with pytest.raises(ProfileError, match="depth"):
        normalize(profile)


def test_negative_scan_work_is_bounded_before_execution(profile):
    profile["scenarios"] = [{"id": "base", "entity": "item", "kind": "normal", "count": 3}]
    profile["negative_scenarios"] = [{"id": "missing", "base_scenario": "base", "count": 3,
                                     "mutations": [{"op": "remove", "field": "id"}],
                                     "expected_rule_violations": ["F-item.id-required"]}]
    profile["generation"]["limits"]["max_validation_rows"] = 12
    with pytest.raises(ProfileError, match="validation row budget"):
        inspect_profile(profile)
    assert inspect_profile(profile, for_generation=False)["estimated_validation_rows"] == 12


def test_generated_long_check_ids_are_valid_target_and_negative_references(profile):
    entity, name = "E" * 64, "F" * 64
    spec = profile["entities"].pop("item")
    spec["fields"][name] = spec["fields"].pop("id")
    spec["primary_key"] = [name]
    profile["entities"][entity] = spec
    check_id = f"F-{entity}.{name}-required"
    profile["scenarios"] = [{"id": "long", "entity": entity, "kind": "normal", "count": 3, "target_check_ids": [check_id]}]
    profile["negative_scenarios"] = [{"id": "missing", "base_scenario": "long", "count": 1,
                                     "mutations": [{"op": "remove", "field": name}], "expected_rule_violations": [check_id]}]
    assert check_id in inspect_profile(normalize(profile))["check_ids"]
