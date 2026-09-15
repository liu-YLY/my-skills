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
