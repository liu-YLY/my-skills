"""Read existing evaluation formats without rewriting their historical files."""

import argparse
import json
from collections import Counter
from pathlib import Path


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--skill")
    parser.add_argument("--json", action="store_true", help="Emit normalized cases for a model runner")
    args = parser.parse_args()
    cases = []
    paths = sorted(args.root.glob("plugins/*/skills/*/test-prompts.json"))
    regressions = args.root / "docs/skill-evaluation/business-regressions.json"
    if regressions.exists():
        paths.append(regressions)
    for path in paths:
        cases.extend(case for case in read_cases(path)
                     if args.skill is None or args.skill == case["skill"])
    if not cases:
        parser.error("No evaluation cases found")
    if args.json:
        print(json.dumps(cases, ensure_ascii=False, indent=2))
    else:
        counts = Counter((case["skill"], case["kind"]) for case in cases)
        for (skill, kind), count in sorted(counts.items()):
            print(f"{skill}: {count} {kind}")
        print("Input validation only; model behavior has not been evaluated by this command.")


if __name__ == "__main__":
    main()
