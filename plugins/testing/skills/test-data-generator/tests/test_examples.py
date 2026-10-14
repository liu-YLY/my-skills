import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from engine.pipeline import generate_bundle, validate_bundle
from engine.profile import load_profile

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", ["basic-fields", "tenant-rbac", "logistics-events"])
def test_business_examples_generate_and_validate(name, tmp_path):
    profile = load_profile(ROOT / "examples" / f"{name}.yaml")
    result = generate_bundle(profile, tmp_path)
    assert result["validation_status"] == "passed"
    assert validate_bundle(profile, result["output_directory"])["validation_status"] == "passed"


def test_ten_thousand_orders_have_exact_scenarios_and_repeatable_artifacts(tmp_path):
    profile = load_profile(ROOT / "examples/order-member.yaml")
    first = generate_bundle(profile, tmp_path)
    second = generate_bundle(profile, tmp_path)
    assert first["normal_rows"] == 11000 and first["negative_cases"] == 4
    assert first["validation_status"] == second["validation_status"] == "passed"
    path = Path(first["output_directory"])
    orders = json.loads((path / "data/order.json").read_text())
    members = json.loads((path / "data/member.json").read_text())
    assert len(members) == 1000 and len(orders) == 10000
    assert Counter(order["status"] for order in orders) == {"pending": 3000, "paid": 5000, "cancelled": 2000}
    assert orders[7998]["amount"] == "0.01" and orders[7999]["amount"] == "99999.99"
    for relative in ["data/order.json", "data/order.csv", "data/member.json", "data/member.csv", "negative/cases.jsonl"]:
        assert (path / relative).read_bytes() == (Path(second["output_directory"]) / relative).read_bytes()
    report = json.loads((path / "validation-report.json").read_text())
    assert report["negative_summary"]["completed_cases"] == 4 and report["negative_summary"]["mismatches"] == 0


def test_copied_skill_runs_without_repository_paths(tmp_path):
    copied = tmp_path / "installed skills/test-data-generator"
    shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    command = [sys.executable, str(copied / "scripts/run_data.py"), "generate", "--profile",
               str(copied / "examples/tenant-rbac.yaml"), "--output-root", str(tmp_path / "outputs")]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    outcome = json.loads(result.stdout)
    assert outcome["normal_rows"] == 14 and outcome["negative_cases"] == 2
    assert outcome["system_execution_status"] == "not_run"
