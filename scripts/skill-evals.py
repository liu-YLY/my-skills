"""Validate evaluation cases and summarize externally produced model results."""

import argparse
import hashlib
import math
import json
from collections import Counter
from pathlib import Path


RESULT_VARIANTS = {"with_skill", "baseline", "old", "new", "no_skill"}
TRIGGER_CATEGORIES = {"positive", "negative", "near_miss", "skill_conflict"}


def read_cases(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = [("task", data)] if isinstance(data, list) else [
        ("task", data.get("evals", data.get("prompts", data.get("task_cases", [])))),
        ("trigger", data.get("trigger_evals", [dict(row["original"], id=row["id"], skill=row["skill"])
                                               for row in data.get("original_trigger_cases", [])])),
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
                              should_trigger=row.get("should_trigger"),
                              category=row.get("category")))
    return cases


def validate_trigger_coverage(cases: list[dict]) -> None:
    """Require routing coverage for every skill represented by task cases."""
    skills = {case["skill"] for case in cases if case["kind"] == "task"}
    for skill in sorted(skills):
        triggers = [case for case in cases
                    if case["skill"] == skill and case["kind"] == "trigger"]
        categories = {case["category"] for case in triggers}
        missing = sorted(TRIGGER_CATEGORIES - categories)
        if missing:
            raise ValueError(f"{skill}: missing trigger categories {missing}")
        if not any(case["should_trigger"] for case in triggers):
            raise ValueError(f"{skill}: trigger suite has no positive label")
        if not any(not case["should_trigger"] for case in triggers):
            raise ValueError(f"{skill}: trigger suite has no negative label")


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
        output_path = row.get("output_path")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0:
            raise ValueError(f"{path}:{line_number}: invalid duration_seconds")
        if not isinstance(output_chars, int) or isinstance(output_chars, bool) or output_chars < 0:
            raise ValueError(f"{path}:{line_number}: invalid output_characters")
        if not isinstance(output_path, str) or not output_path.strip():
            raise ValueError(f"{path}:{line_number}: output_path must be a non-empty string")
        errors = []
        if not math.isfinite(duration):
            errors.append("duration_seconds is not finite")
        output = Path(output_path)
        if not output.is_absolute():
            output = path.parent / output
        try:
            content = output.read_bytes()
            if len(content.decode("utf-8")) != output_chars:
                errors.append("output_characters does not match artifact")
            actual_hash = hashlib.sha256(content).hexdigest()
            if row.get("output_sha256", actual_hash) != actual_hash:
                errors.append("output_sha256 does not match artifact")
        except (OSError, UnicodeError) as error:
            errors.append(f"output artifact unavailable: {error}")
        row["evidence_errors"] = errors
        row["artifact_verified"] = not errors
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
    return results


def summarize_results(results: list[dict], cases: list[dict], expected_runs: int = 1,
                      variants: list[str] | None = None) -> dict:
    """Produce deterministic task and trigger metrics grouped by variant."""
    if isinstance(expected_runs, bool) or not isinstance(expected_runs, int) or expected_runs < 1:
        raise ValueError("expected_runs must be a positive integer")
    variants = variants or (["old", "new", "no_skill"] if any(
        row["variant"] in {"old", "new", "no_skill"} for row in results) else ["with_skill", "baseline"])
    if len(set(variants)) != len(variants) or not set(variants) <= RESULT_VARIANTS:
        raise ValueError("invalid or duplicate variants")
    case_map = {(case["skill"], case["id"], case["kind"]): case for case in cases}
    expected_keys = set(case_map)
    expected_run_keys = {(*key, run) for key in expected_keys for run in range(1, expected_runs + 1)}
    def run_key(row):
        return (str(row["skill"]), str(row["id"]), row["kind"], row["run"])
    valid_keys = {variant: {run_key(row) for row in results if row["variant"] == variant
                           and row.get("artifact_verified", False)} & expected_run_keys
                  for variant in variants}
    paired_keys = expected_run_keys.intersection(*(valid_keys[variant] for variant in variants))
    def labels(keys):
        return [f"{skill}:{kind}:{case_id}:run-{run}" for skill, case_id, kind, run in sorted(keys)]
    summaries = {}
    for variant in sorted(variants):
        invalid_rows = [row for row in results if row["variant"] == variant
                        and not row.get("artifact_verified", False)]
        rows = [row for row in results if row["variant"] == variant
                and row.get("artifact_verified", False)]
        metric_rows = [row for row in rows if run_key(row) in paired_keys]
        task_rows = [row for row in metric_rows if row["kind"] == "task"]
        trigger_rows = [row for row in metric_rows if row["kind"] == "trigger"]
        check_values = [value for row in task_rows for value in row["check_results"]]
        completed_keys = {key for key in expected_keys if all(
            (*key, run) in valid_keys[variant] for run in range(1, expected_runs + 1))}
        missing_keys = sorted(expected_keys - completed_keys)
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
        expected_count = len(expected_keys)
        completed_count = len(completed_keys)
        summaries[variant] = {
            "runs": len(valid_keys[variant]),
            "expected_runs": len(expected_run_keys),
            "repetitions_per_case": expected_runs,
            "completed_runs": len(valid_keys[variant]),
            "run_completion_rate": len(valid_keys[variant]) / len(expected_run_keys) if expected_run_keys else None,
            "missing_runs": labels(expected_run_keys - valid_keys[variant]),
            "unpaired_runs": labels(valid_keys[variant] - paired_keys),
            "unexpected_runs": labels({run_key(row) for row in rows} - expected_run_keys),
            "invalid_runs": [{"id": row["id"], "kind": row["kind"], "run": row["run"],
                              "errors": row.get("evidence_errors", ["artifact not verified"])}
                             for row in invalid_rows],
            "expected_cases": expected_count,
            "completed_cases": completed_count,
            "completion_rate": completed_count / expected_count if expected_count else None,
            "missing_cases": [f"{skill}:{kind}:{case_id}"
                              for skill, case_id, kind in missing_keys],
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
            "mean_duration_seconds": (
                sum(row["duration_seconds"] for row in metric_rows) / len(metric_rows) if metric_rows else None
            ),
            "mean_output_characters": (
                sum(row["output_characters"] for row in metric_rows) / len(metric_rows) if metric_rows else None
            ),
        }
    status = "evaluated" if all(
        summary["run_completion_rate"] == 1.0 and not summary["invalid_runs"]
        and not summary["unexpected_runs"] for summary in summaries.values()
    ) else "partial"
    return {"status": status, "variants": summaries}


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
    parser.add_argument("--cases-file", type=Path, help="Use an explicitly frozen selected suite")
    parser.add_argument("--expected-runs", type=int, default=1, help="Required repeats per case; formal evaluation uses 3")
    parser.add_argument("--variants", nargs="+", choices=sorted(RESULT_VARIANTS))
    parser.add_argument("--json", action="store_true", help="Emit normalized cases for a model runner")
    parser.add_argument("--results", type=Path,
                        help="Validate JSONL model results and print a deterministic summary")
    args = parser.parse_args()
    if args.expected_runs < 1:
        parser.error("--expected-runs must be positive")
    cases = read_cases(args.cases_file) if args.cases_file else load_cases(args.root, args.skill)
    if args.cases_file and args.skill:
        cases = [case for case in cases if case["skill"] == args.skill]
    if not cases:
        parser.error("No evaluation cases found")
    if not args.cases_file:
        validate_trigger_coverage(cases)
    if args.results:
        results = read_results(args.results, cases)
        print(json.dumps(summarize_results(results, cases, args.expected_runs, args.variants), ensure_ascii=False, indent=2))
    elif args.json:
        print(json.dumps(cases, ensure_ascii=False, indent=2))
    else:
        counts = Counter((case["skill"], case["kind"]) for case in cases)
        for (skill, kind), count in sorted(counts.items()):
            print(f"{skill}: {count} {kind}")
        print("Input validation only; model behavior has not been evaluated by this command.")


if __name__ == "__main__":
    main()
