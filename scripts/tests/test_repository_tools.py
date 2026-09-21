import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("skill_evals", ROOT / "scripts/skill-evals.py")
evals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evals)


@pytest.mark.parametrize("payload", [
    [{"id": 1, "prompt": "task", "expected": "observable result"}],
    {"evals": [{"id": 1, "prompt": "task", "expectations": ["observable result"]}]},
    {"prompts": [{"id": 1, "prompt": "task", "expected_behavior": "observable result",
                   "validation_points": ["evidence"]}]},
])
def test_eval_formats_preserve_prompt_and_expectations(tmp_path, payload):
    path = tmp_path / "test-prompts.json"
    path.write_text(json.dumps(payload))
    cases = evals.read_cases(path)
    assert cases[0]["prompt"] == "task"
    assert "observable result" in cases[0]["checks"]


def test_eval_reader_rejects_duplicate_ids(tmp_path):
    path = tmp_path / "test-prompts.json"
    sample = dict(id=1, prompt="task", expected="result")
    path.write_text(json.dumps([sample, sample]))
    with pytest.raises(ValueError, match="duplicate"):
        evals.read_cases(path)


def test_eval_reader_preserves_negative_trigger(tmp_path):
    path = tmp_path / "test-prompts.json"
    path.write_text(json.dumps({"trigger_evals": [{"query": "translate", "should_trigger": False}]}))
    assert evals.read_cases(path)[0]["should_trigger"] is False


def test_model_results_are_validated_and_summarized(tmp_path):
    cases = [
        dict(skill="sample", id="task-1", kind="task", prompt="do it",
             checks=["complete", "grounded"], should_trigger=None),
        dict(skill="sample", id="trigger-1", kind="trigger", prompt="route it",
             checks=[], should_trigger=True),
        dict(skill="sample", id="trigger-2", kind="trigger", prompt="translate it",
             checks=[], should_trigger=False),
    ]
    rows = [
        dict(skill="sample", id="task-1", kind="task", variant="with_skill", run=1,
             duration_seconds=2.0, output_characters=100, check_results=[True, False]),
        dict(skill="sample", id="trigger-1", kind="trigger", variant="with_skill", run=1,
             duration_seconds=1.0, output_characters=20, predicted_trigger=True),
        dict(skill="sample", id="trigger-2", kind="trigger", variant="with_skill", run=1,
             duration_seconds=1.0, output_characters=20, predicted_trigger=False),
    ]
    path = tmp_path / "results.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    results = evals.read_results(path, cases)
    summary = evals.summarize_results(results, cases)["variants"]["with_skill"]
    assert summary["checks_passed"] == 1
    assert summary["checks_total"] == 2
    assert summary["trigger_precision"] == 1.0
    assert summary["trigger_recall"] == 1.0
    assert summary["mean_duration_seconds"] == pytest.approx(4 / 3)


@pytest.mark.parametrize("field,value,message", [
    ("run", 0, "positive integer"),
    ("variant", "unknown", "invalid variant"),
    ("check_results", [True], "2 booleans"),
])
def test_model_results_reject_invalid_contract(tmp_path, field, value, message):
    cases = [dict(skill="sample", id="task-1", kind="task", prompt="do it",
                  checks=["complete", "grounded"], should_trigger=None)]
    row = dict(skill="sample", id="task-1", kind="task", variant="with_skill", run=1,
               duration_seconds=2.0, output_characters=100, check_results=[True, True])
    row[field] = value
    path = tmp_path / "results.jsonl"
    path.write_text(json.dumps(row), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        evals.read_results(path, cases)
