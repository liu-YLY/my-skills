#!/usr/bin/env python3
"""解析覆盖率诊断：找出「含用例但没被解析出来」的文件。

校验器最大的风险不是误报，是__静默漏检__——文件里有用例，
但格式变体没被 parse_cases 识别，于是 check 阶段完全跳过它，
结果看起来「0 error」，实际根本没检查。

本脚本只输出计数与文件名，不打印任何用例正文，避免把用例内容带出工作区。

用法：
    python scripts/check_coverage.py <用例目录或文件> [--show 12]
退出码：0 覆盖率 100%；1 存在未被解析的文件
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_cases import parse_cases  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SUFFIXES = {".md", ".markdown", ".txt"}
TC_RE = re.compile(r"TC_[A-Za-z0-9_]+")
HEAD_HINT = re.compile(r"^.{0,16}TC_[A-Za-z0-9_]+.*$", re.M)


def collect(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(
        p for p in target.rglob("*")
        if p.suffix.lower() in SUFFIXES and p.is_file()
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="用例解析覆盖率诊断")
    ap.add_argument("target")
    ap.add_argument("--show", type=int, default=12, help="最多列出多少个未解析文件")
    args = ap.parse_args(argv)

    files = collect(Path(args.target).resolve())
    with_tc = parsed = 0
    unparsed: list[tuple[str, int]] = []
    total_cases = 0

    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        hits = TC_RE.findall(text)
        if not hits:
            continue
        with_tc += 1
        cases = parse_cases(text)
        if cases:
            parsed += 1
            total_cases += len(cases)
        else:
            unparsed.append((str(f), len(hits)))

    rate = parsed / with_tc * 100 if with_tc else 100.0
    print(f"扫描 {len(files)} 个文件")
    print(f"含 TC_ 标识   {with_tc}")
    print(f"解析出用例    {parsed}")
    print(f"解析为 0      {len(unparsed)}")
    print(f"解析覆盖率    {rate:.1f}%")
    print(f"识别用例总数  {total_cases}")

    if unparsed:
        print(f"\n未被解析的文件（前 {args.show} 个，仅文件名与计数）：")
        for path, cnt in unparsed[: args.show]:
            print(f"  {Path(path).name[:52]:52} TC_×{cnt}")
        print("\n提示：这些文件里的用例没有被任何规则检查，属于静默漏检。")
        print("      若是合法的新格式变体，应扩展 parse_cases；若是无效产出，应视为不合格。")

    return 0 if not unparsed else 1


if __name__ == "__main__":
    sys.exit(main())
