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
