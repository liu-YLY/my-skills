"""Fail when a skill default-path context exceeds its configured budget.

Default mode checks the current gate (budget). Use --target after slimming to
check the final target; failures before slimming are expected.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_context import load_config, measure_files, measure_mode, skill_dir


def check(root: Path, config: dict, skill: str | None, use_target: bool) -> list[dict]:
    rows = []
    names = [skill] if skill else sorted(config["skills"])
    for name in names:
        skill_config = config["skills"][name]
        entry = skill_config.get("entry")
        if entry:
            measured = measure_files(root, name, [entry["file"]])
            limit = entry["target" if use_target else "budget"]
            rows.append({
                "skill": name,
                "mode": "entry",
                "characters": measured["characters"],
                "limit": limit,
                "over": measured["characters"] > limit,
                "missing": measured["missing"],
            })
        for mode_name, mode in skill_config.get("modes", {}).items():
            measured = measure_mode(root, name, mode)
            limit = mode["target" if use_target else "budget"]
            rows.append({
                "skill": name,
                "mode": mode_name,
                "characters": measured["characters"],
                "limit": limit,
                "over": measured["characters"] > limit,
                "missing": measured["missing"],
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--skill")
    parser.add_argument("--target", action="store_true", help="Check final targets instead of current gates")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config) if args.config else load_config()
    rows = check(args.root, config, args.skill, args.target)
    failures = [row for row in rows if row["over"] or row["missing"]]
    if args.json:
        print(json.dumps({"status": "fail" if failures else "pass", "rows": rows}, ensure_ascii=False, indent=2))
    else:
        label = "目标" if args.target else "门槛"
        print(f"| Skill / Mode | 字符 | {label} | 结果 |")
        print("|---|---:|---:|---|")
        for row in rows:
            status = "FAIL" if row["over"] else "ok"
            if row["missing"]:
                status = "MISSING"
            print(f"| {row['skill']} / {row['mode']} | {row['characters']:,} | {row['limit']:,} | {status} |")
        if failures:
            print()
            for row in failures:
                if row["missing"]:
                    print(f"missing files: {row['skill']} / {row['mode']}: {', '.join(row['missing'])}")
                if row["over"]:
                    print(
                        f"over {label}: {row['skill']} / {row['mode']}: "
                        f"{row['characters']:,} > {row['limit']:,}"
                    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
