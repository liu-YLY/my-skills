"""Report skill default-path context size by mode.

Usage:
    python scripts/skill-context-report.py
    python scripts/skill-context-report.py --skill test-case-engineer --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_context import count_tokens, load_config, measure_all, measure_files, skill_dir


def print_table(report: dict) -> None:
    print("| Skill / Mode | 字符 | 行数 | Token(估) | 当前门槛 | 目标 | 距门槛 |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    total_modes = 0
    total_markdown = 0
    for skill, data in report["skills"].items():
        total_markdown += data["total_markdown_characters"]
        entry = data.get("entry")
        if entry:
            budget = entry["budget"]
            target = entry["target"]
            print(
                f"| {skill} / entry | {entry['characters']:,} | {entry['lines']:,} | "
                f"{entry['tokens']:,} | {budget:,} | {target:,} | {budget - entry['characters']:+,} |"
            )
        for name, mode in data["modes"].items():
            total_modes += mode["characters"]
            budget = mode["budget"] or 0
            target = mode["target"] or 0
            print(
                f"| {skill} / {name} | {mode['characters']:,} | {mode['lines']:,} | "
                f"{mode['tokens']:,} | {budget:,} | {target:,} | {budget - mode['characters']:+,} |"
            )
    print()
    print(f"默认路径合计：{total_modes:,} 字符")
    print(f"目录内全部 Markdown：{total_markdown:,} 字符")
    methods = {
        mode["token_method"]
        for data in report["skills"].values()
        for mode in data["modes"].values()
    }
    print(f"Token 口径：{', '.join(sorted(methods))}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--skill")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config) if args.config else load_config()
    report = measure_all(args.root, config, args.skill)
    for skill, data in report["skills"].items():
        entry = config["skills"][skill].get("entry")
        if entry:
            measured = measure_files(args.root, skill, [entry["file"]])
            measured["mode"] = "entry"
            measured["budget"] = entry["budget"]
            measured["target"] = entry["target"]
            entry_path = skill_dir(args.root, skill) / entry["file"]
            tokens = count_tokens(entry_path.read_text(encoding="utf-8")) if entry_path.exists() else None
            measured["tokens"] = tokens if tokens is not None else round(measured["characters"] / 1.55)
            measured["token_method"] = (
                "tiktoken:o200k_base" if tokens is not None else "fallback:characters/1.55"
            )
            data["entry"] = measured
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_table(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
