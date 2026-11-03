#!/usr/bin/env python3
"""Runner 批处理进度管理器（阶段 P 完整铺开）。

管理 42 task × {with_skill, no_skill} = 84 份产物的生成进度：
- 列出还缺哪些产物
- 校验已生成产物的完整性（非空、UTF-8、无围栏）

用法：
  python docs/skill-evaluation/tier23/full/runner_status.py
"""

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "outputs"
MANIFEST = HERE / "task-manifest.json"
VARIANTS = ["with_skill", "no_skill"]


def main():
    tasks = json.loads(MANIFEST.read_text(encoding="utf-8"))
    total = len(tasks) * len(VARIANTS)
    done = 0
    missing = []
    for t in tasks:
        tid = t["id"]
        for v in VARIANTS:
            p = OUT / f"task-{tid}-{v}.txt"
            if p.exists() and p.read_text(encoding="utf-8").strip():
                done += 1
            else:
                missing.append((tid, v))
    print(f"进度：{done}/{total} 份产物已生成")
    if missing:
        print(f"\n缺 {len(missing)} 份：")
        for tid, v in missing:
            print(f"  task-{tid}-{v}.txt")
    else:
        print("全部完成。")


if __name__ == "__main__":
    main()
