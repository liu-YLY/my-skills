"""Validate evaluation cases and summarize externally produced model results."""

import argparse
import json
from collections import Counter
from pathlib import Path


RESULT_VARIANTS = {"with_skill", "baseline"}


def read_cases(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = [("task", data)] if isinstance(data, list) else [
        ("task", data.get("evals", data.get("prompts", []))),
        ("trigger", data.get("trigger_evals", [])),
    ]
    cases = []
    seen = set()
    for kind, rows in groups:
        for index, row in enumerate(rows, 1):
            case_id = str(row.get("id", index))
            prompt = row.get("prompt", row.get("query", ""))
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError(f"{path}: {case_id} has no prompt")
            key = (kind, case_id)
            if key in seen:
                raise ValueError(f"{path}: duplicate {key}")
            seen.add(key)
            checks = row.get("expectations", row.get("validation_points", []))
            expected = row.get("expected", row.get("expected_behavior"))
            if not isinstance(checks, list) or not all(isinstance(v, str) for v in checks):
                raise ValueError(f"{path}: {case_id} has invalid expectations")
            if expected:
                if not isinstance(expected, str):
                    raise ValueError(f"{path}: {case_id} has invalid expected text")
                checks = [expected, *checks]
            if kind == "task" and not checks:
                raise ValueError(f"{path}: {case_id} has no expectations")
            if kind == "trigger" and not isinstance(row.get("should_trigger"), bool):
                raise ValueError(f"{path}: {case_id} has no trigger label")
            cases.append(dict(skill=row.get("skill", path.parent.name), id=case_id, kind=kind,
                              prompt=prompt, checks=checks,
                              should_trigger=row.get("should_trigger")))
    return cases


def read_results(path: Path, cases: list[dict]) -> list[dict]:
    """Validate JSONL model results against normalized evaluation cases."""
    case_map = {(case["skill"], case["id"], case["kind"]): case for case in cases}
    results = []
    seen = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {error.msg}") from error
        key = (str(row.get("skill", "")), str(row.get("id", "")), row.get("kind"))
        if key not in case_map:
            raise ValueError(f"{path}:{line_number}: unknown evaluation case {key}")
        variant = row.get("variant")
        run = row.get("run")
        result_key = (*key, variant, run)
        if variant not in RESULT_VARIANTS:
            raise ValueError(f"{path}:{line_number}: invalid variant {variant!r}")
        if not isinstance(run, int) or isinstance(run, bool) or run < 1:
            raise ValueError(f"{path}:{line_number}: run must be a positive integer")
        if result_key in seen:
            raise ValueError(f"{path}:{line_number}: duplicate result {result_key}")
        seen.add(result_key)
        duration = row.get("duration_seconds")
        output_chars = row.get("output_characters")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0:
            raise ValueError(f"{path}:{line_number}: invalid duration_seconds")
        if not isinstance(output_chars, int) or isinstance(output_chars, bool) or output_chars < 0:
            raise ValueError(f"{path}:{line_number}: invalid output_characters")
        case = case_map[key]
        if key[2] == "task":
            checks = row.get("check_results")
            if (not isinstance(checks, list) or
                    len(checks) != len(case["checks"]) or
                    not all(isinstance(value, bool) for value in checks)):
                raise ValueError(
                    f"{path}:{line_number}: check_results must contain "
                    f"{len(case['checks'])} booleans"
                )
        else:
            if not isinstance(row.get("predicted_trigger"), bool):
                raise ValueError(f"{path}:{line_number}: predicted_trigger must be boolean")
        results.append(row)
    if not results:
        raise ValueError(f"{path}: no model results found")
    return results


def summarize_results(results: list[dict], cases: list[dict]) -> dict:
    """Produce deterministic task and trigger metrics grouped by variant."""
    case_map = {(case["skill"], case["id"], case["kind"]): case for case in cases}
    summaries = {}
    for variant in sorted(RESULT_VARIANTS):
        rows = [row for row in results if row["variant"] == variant]
        if not rows:
            continue
        task_rows = [row for row in rows if row["kind"] == "task"]
        trigger_rows = [row for row in rows if row["kind"] == "trigger"]
        check_values = [value for row in task_rows for value in row["check_results"]]
        confusion = Counter()
        for row in trigger_rows:
            case = case_map[(row["skill"], str(row["id"]), "trigger")]
            expected = case["should_trigger"]
            predicted = row["predicted_trigger"]
            confusion[(expected, predicted)] += 1
        tp = confusion[(True, True)]
        fp = confusion[(False, True)]
        fn = confusion[(True, False)]
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        summaries[variant] = {
            "runs": len(rows),
            "task_runs": len(task_rows),
            "checks_passed": sum(check_values),
            "checks_total": len(check_values),
            "trigger_runs": len(trigger_rows),
            "trigger_confusion": {
                "true_positive": tp,
                "false_positive": fp,
                "true_negative": confusion[(False, False)],
                "false_negative": fn,
            },
            "trigger_precision": precision,
            "trigger_recall": recall,
            "mean_duration_seconds": sum(row["duration_seconds"] for row in rows) / len(rows),
            "mean_output_characters": sum(row["output_characters"] for row in rows) / len(rows),
        }
    return {"status": "evaluated", "variants": summaries}


def load_cases(root: Path, skill: str | None = None) -> list[dict]:
    cases = []
    paths = sorted(root.glob("plugins/*/skills/*/test-prompts.json"))
    regressions = root / "docs/skill-evaluation/business-regressions.json"
    if regressions.exists():
        paths.append(regressions)
    for path in paths:
        cases.extend(case for case in read_cases(path)
                     if skill is None or skill == case["skill"])
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--skill")
    parser.add_argument("--json", action="store_true", help="Emit normalized cases for a model runner")
    parser.add_argument("--results", type=Path,
                        help="Validate JSONL model results and print a deterministic summary")
    args = parser.parse_args()
    cases = load_cases(args.root, args.skill)
    if not cases:
        parser.error("No evaluation cases found")
    if args.results:
        results = read_results(args.results, cases)
        print(json.dumps(summarize_results(results, cases), ensure_ascii=False, indent=2))
    elif args.json:
        print(json.dumps(cases, ensure_ascii=False, indent=2))
    else:
        counts = Counter((case["skill"], case["kind"]) for case in cases)
        for (skill, kind), count in sorted(counts.items()):
            print(f"{skill}: {count} {kind}")
        print("Input validation only; model behavior has not been evaluated by this command.")


if __name__ == "__main__":
    main()
