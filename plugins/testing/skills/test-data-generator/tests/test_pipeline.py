import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from engine.common import Budget, ResourceError
from engine.pipeline import generate_bundle, validate_bundle
from engine.profile import inspect_profile
from test_generators import simple
from test_negative import negative_profile

ROOT = Path(__file__).resolve().parents[1]


def test_all_formats_roundtrip_null_empty_unicode_and_escaped_strings(tmp_path):
    profile = simple({"note": {"type": "string", "nullable": True,
                              "generator": {"kind": "choice", "values": [None, "", "\\N", "中文,\"值\"\n换行", "0012", "\\path\\"]}}}, 100)
    profile["generation"]["output_formats"] = ["json", "jsonl", "csv"]
    first = generate_bundle(profile, tmp_path)
    assert first["validation_status"] == "passed"
    report = validate_bundle(profile, first["output_directory"])
    assert report["validation_status"] == "passed" and not report["integrity_issues"]
    second = generate_bundle(copy.deepcopy(profile), tmp_path)
    for kind in ("json", "csv", "jsonl"):
        name = f"data/item.{kind}"
        assert (Path(first["output_directory"]) / name).read_bytes() == (Path(second["output_directory"]) / name).read_bytes()


def test_negatives_and_manifest_are_rechecked_not_trusted(tmp_path):
    profile = negative_profile()
    result = generate_bundle(profile, tmp_path)
    directory = Path(result["output_directory"])
    assert validate_bundle(profile, directory)["validation_status"] == "passed"
    cases = directory / "negative/cases.jsonl"
    cases.write_text("")
    report = validate_bundle(profile, directory)
    assert report["validation_status"] == "failed"
    assert report["negative_summary"]["completed_cases"] == 0
    assert report["integrity_issues"]


def test_byte_limit_preserves_other_files_and_records_failure(tmp_path):
    profile = simple({}, 3)
    profile["generation"]["limits"]["max_output_bytes"] = 20
    sentinel = tmp_path / "user.txt"
    sentinel.write_text("keep")
    with pytest.raises(ResourceError, match="byte limit"):
        generate_bundle(profile, tmp_path)
    assert sentinel.read_text() == "keep"
    failed = list(tmp_path.glob("*.failed"))
    assert len(failed) == 1
    assert json.loads((failed[0] / "manifest.json").read_text())["generation_status"] == "failed"
    assert not list(tmp_path.glob("*.tmp"))


def test_timeout_and_interruption_leave_no_complete_claim(tmp_path, monkeypatch):
    profile = simple({}, 1)
    profile["generation"]["limits"]["timeout_seconds"] = 0.00000001
    with pytest.raises(ResourceError, match="timeout"):
        generate_bundle(profile, tmp_path)
    profile["generation"]["limits"]["timeout_seconds"] = 120
    def interrupt(*args):
        raise KeyboardInterrupt()
    monkeypatch.setattr("engine.pipeline.generate_dataset", interrupt)
    with pytest.raises(KeyboardInterrupt):
        generate_bundle(profile, tmp_path)
    assert all(json.loads((p / "manifest.json").read_text())["generation_status"] == "failed" for p in tmp_path.glob("*.failed"))


def test_dataset_path_traversal_is_rejected(tmp_path):
    profile = simple({}, 1)
    result = generate_bundle(profile, tmp_path)
    path = Path(result["output_directory"]) / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["files"]["../outside.json"] = {"sha256": "ignored", "bytes": 1}
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="escapes"):
        validate_bundle(profile, path.parent)


def test_cli_generates_and_validates_from_unrelated_directory(tmp_path):
    profile = negative_profile()
    path = tmp_path / "my profile.json"
    path.write_text(json.dumps(profile))
    command = [sys.executable, str(ROOT / "scripts/run_data.py")]
    result = subprocess.run([*command, "generate", "--profile", str(path), "--output-root", str(tmp_path / "output")],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    generated = json.loads(result.stdout)
    result = subprocess.run([*command, "validate", "--profile", str(path), "--dataset", generated["output_directory"]],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["system_execution_status"] == "not_run"


def test_external_csv_without_manifest_is_validated_using_declared_types(tmp_path):
    profile = simple({"code": {"type": "string", "generator": {"kind": "constant", "value": "0012"}}}, 1)
    (tmp_path / "item.csv").write_text("code,id\n0012,0001\n")
    assert validate_bundle(profile, tmp_path)["validation_status"] == "passed"
    (tmp_path / "item.csv").write_text("code,id\n0012,0001\n0012,0001\n")
    report = validate_bundle(profile, tmp_path)
    assert report["validation_status"] == "failed" and "N-item-count" in report["violation_ids"]


def test_existing_data_is_not_blocked_by_generator_capacity(tmp_path):
    profile = simple({}, 2)
    profile["entities"]["item"]["fields"]["id"]["generator"] = {"kind": "constant", "value": "dummy"}
    (tmp_path / "item.json").write_text('[{"id":"A"},{"id":"B"}]')
    assert validate_bundle(profile, tmp_path)["validation_status"] == "passed"


def test_cli_missing_dependency_has_structured_runtime_error(tmp_path):
    result = subprocess.run([sys.executable, "-S", str(ROOT / "scripts/run_data.py"), "inspect",
                             "--profile", str(tmp_path / "missing.json")], text=True, capture_output=True)
    assert result.returncode == 4
    assert json.loads(result.stdout)["validation_status"] == "not_run"
    assert "dependency" in json.loads(result.stdout)["error"]


def test_scenario_targets_have_actual_results_and_case_traceability(tmp_path):
    profile = simple({"active": {"type": "boolean", "generator": {"kind": "constant", "value": True}}}, 2)
    profile["rules"] = [{"id": "active-user", "entity": "item", "assert": {"field": "active", "op": "eq", "value": True}}]
    profile["scenarios"] = [{"id": "active", "entity": "item", "kind": "normal", "count": 2,
                             "case_ids": ["TC01"], "combination_id": "COMBO01", "target_check_ids": ["active-user"]}]
    output = generate_bundle(profile, tmp_path)
    report = validate_bundle(profile, output["output_directory"])
    scenario = report["scenario_summary"][0]
    assert scenario["case_ids"] == ["TC01"] and scenario["combination_id"] == "COMBO01"
    assert scenario["expected_rows"] == scenario["observed_rows"] == 2
    assert scenario["target_checks"]["active-user"]["applicable"] == 2
    assert scenario["validation_status"] == "passed"


def test_unused_faker_does_not_require_optional_runtime_version(tmp_path, monkeypatch):
    import engine.pipeline as pipeline
    from importlib.metadata import PackageNotFoundError

    profile = simple({"name": {"type": "string", "generator": {"kind": "constant", "value": "synthetic"}}}, 1)
    profile["entities"]["item"]["fields"]["name"]["generator"] = {"kind": "faker", "provider": "name", "locale": "en_US"}
    profile["scenarios"] = [{"id": "fixed", "entity": "item", "kind": "normal", "count": 1, "set": {"name": "synthetic"}}]
    original = pipeline.version

    def dependency_version(name):
        if name == "Faker":
            raise PackageNotFoundError(name)
        return original(name)

    monkeypatch.setattr(pipeline, "version", dependency_version)
    output = generate_bundle(profile, tmp_path)
    manifest = json.loads((Path(output["output_directory"]) / "manifest.json").read_text())
    assert output["validation_status"] == "passed" and "Faker" not in manifest["dependencies"]
