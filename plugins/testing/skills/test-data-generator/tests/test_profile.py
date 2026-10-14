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
