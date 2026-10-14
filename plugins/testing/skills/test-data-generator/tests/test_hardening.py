import copy
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from engine.common import ProfileError, ResourceError, canonical
from engine.generators import generate_entity
from engine.negative import build_negative_cases, validate_negative_cases
from engine.relations import generate_dataset
from engine.profile import inspect_profile
from engine.validator import validate_data
from test_generators import simple
from test_negative import negative_profile

CLI = Path(__file__).resolve().parents[1] / "scripts/run_data.py"


@pytest.mark.parametrize("seed", [0, 1, 2, 42])
def test_unique_integer_full_capacity_succeeds_and_repeats(seed):
    profile = simple({}, 1000)
    profile["generation"]["seed"] = seed
    profile["entities"]["item"]["fields"]["id"] = {
        "type": "integer", "min": 0, "max": 999, "generator": {"kind": "integer"}}
    first, _ = generate_entity(profile, "item")
    assert {r["id"] for r in first} == set(range(1000))
    assert first == generate_entity(copy.deepcopy(profile), "item")[0]


@pytest.mark.parametrize("field, expected", [
    ({"type": "decimal", "min": "0.00", "max": "0.99", "scale": 2, "generator": {"kind": "decimal"}},
     {f"0.{i:02}" for i in range(100)}),
    ({"type": "string", "generator": {"kind": "choice", "values": [str(i) for i in range(100)]}},
     {str(i) for i in range(100)}),
])
def test_unique_decimal_and_choice_full_capacity(field, expected):
    profile = simple({"slot": dict(field, unique=True)}, 100)
    rows, _ = generate_entity(profile, "item")
    assert {r["slot"] for r in rows} == expected


@pytest.mark.parametrize("field, value", [("base_key", [True]), ("record_index", False)])
def test_negative_metadata_cannot_substitute_booleans_for_integers(field, value):
    profile = negative_profile()
    profile["entities"]["item"]["fields"]["id"] = {"type": "integer", "min": 1, "max": 3, "generator": {"kind": "integer"}}
    data, ids, _ = generate_dataset(profile)
    data["item"].sort(key=lambda row: row["id"])
    cases = build_negative_cases(profile, data, ids)
    assert cases[0]["base_key"] == [1] and cases[0]["record_index"] == 0
    cases[0][field] = value
    result = validate_negative_cases(profile, data, ids, cases)
    assert result["validation_status"] == "failed"
    assert not result["cases"][0]["metadata_valid"]


def run_cli(tmp_path, profile, command, location):
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(profile))
    return subprocess.run([sys.executable, str(CLI), command, "--profile", str(path),
                           "--output-root" if command == "generate" else "--dataset", str(location)],
                          cwd=tmp_path, text=True, capture_output=True, timeout=5)


@pytest.mark.parametrize("command", ["generate", "validate"])
def test_cli_terminates_blocking_regex_and_marks_partial_generation(tmp_path, command):
    profile = simple({"text": {"type": "string", "pattern": "^(a+)+b$|^a+!$",
                              "generator": {"kind": "constant", "value": "a" * 28 + "!"}}}, 1)
    profile["generation"]["limits"]["timeout_seconds"] = 0.03
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / "item.json").write_text(json.dumps([{"id": "0001", "text": "a" * 28 + "!"}]))
    started = time.monotonic()
    result = run_cli(tmp_path, profile, command, directory)
    assert time.monotonic() - started < 2
    assert result.returncode == 4, result.stdout + result.stderr
    assert "timeout" in json.loads(result.stdout)["error"]
    if command == "generate":
        failed = list(directory.glob("*.failed"))
        assert len(failed) == 1 and not list(directory.glob("*.tmp"))
        assert json.loads((failed[0] / "manifest.json").read_text())["generation_status"] == "failed"


def test_final_validator_check_catches_last_field_overrun(monkeypatch):
    profile = simple({"text": {"type": "string", "pattern": "a", "generator": {"kind": "constant", "value": "a"}}}, 1)
    def slow_search(*args):
        time.sleep(0.02)
        return True
    monkeypatch.setattr("engine.validator.re.search", slow_search)
    profile["generation"]["limits"]["timeout_seconds"] = 0.01
    with pytest.raises(ResourceError, match="timeout"):
        validate_data(profile, {"item": [{"id": "0001", "text": "a"}]})


@pytest.mark.parametrize("kind", ["json", "jsonl"])
def test_nonfinite_external_numbers_produce_strict_json_error(tmp_path, kind):
    profile = simple({"number": {"type": "integer", "min": 0, "max": 2, "generator": {"kind": "integer"}}}, 1)
    (tmp_path / f"item.{kind}").write_text('[{"id":"0001","number":NaN}]' if kind == "json" else '{"id":"0001","number":NaN}\n')
    result = run_cli(tmp_path, profile, "validate", tmp_path)
    assert result.returncode == 4
    def reject(value):
        pytest.fail(f"invalid JSON number in stdout: {value}")
    report = json.loads(result.stdout, parse_constant=reject)
    assert "nonfinite" in report["error"]


def test_direct_validator_nonfinite_observation_is_serializable():
    profile = simple({"number": {"type": "integer", "min": 0, "max": 2, "generator": {"kind": "integer"}}}, 1)
    report = validate_data(profile, {"item": [{"id": "0001", "number": float("nan")}]})
    assert report["validation_status"] == "failed"
    assert "F-item.number-type" in report["violation_ids"]
    canonical(report)


@pytest.mark.parametrize("value", ["1e1000", "1e-1000", "NaN", "Infinity"])
def test_decimal_exponents_and_nonfinite_bounds_are_configuration_errors(value):
    profile = simple({}, 1)
    profile["entities"]["item"]["fields"]["amount"] = {
        "type": "decimal", "min": value, "max": value, "scale": 2, "generator": {"kind": "decimal"}}
    with pytest.raises(ProfileError, match="invalid min"):
        inspect_profile(profile)
