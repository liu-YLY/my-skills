#!/usr/bin/env python3
"""Create blind copies and reviewer score sheets for P0.

The blind key must be kept away from reviewers. Reviewers only see blind/S*.md
and the rubric/requirement documents.
"""

import argparse
import csv
import json
import random
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STRIP = re.compile(r"(运行：|with_skill|no_skill|A/A)", re.IGNORECASE)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", default="2026-11-17-p0")
    parser.add_argument("--seed", type=int, default=20261117)
    args = parser.parse_args()

    batch = BASE / "runs" / args.batch_id
    plan = json.loads((batch / "run-plan.json").read_text(encoding="utf-8"))
    blind_dir = batch / "blind"
    reviewer_dir = batch / "reviewer"
    blind_dir.mkdir(exist_ok=True)
    reviewer_dir.mkdir(exist_ok=True)

    entries = []
    for run in plan:
        text = (batch / run["output_path"]).read_text(encoding="utf-8")
        cleaned = "\n".join(line for line in text.splitlines() if not STRIP.search(line))
        entries.append({**run, "text": cleaned})

    random.Random(args.seed).shuffle(entries)
    key = []
    for i, entry in enumerate(entries, start=1):
        blind_id = f"S{i:02d}"
        (blind_dir / f"{blind_id}.md").write_text(entry["text"], encoding="utf-8")
        key.append(
            {
                "blind_id": blind_id,
                "run_id": entry["run_id"],
                "task_id": entry["task_id"],
                "task_type": entry["task_type"],
            }
        )

    (batch / "blind-key.json").write_text(
        json.dumps(key, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    header = [
        "blind_id",
        "task_id",
        "task_type",
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "R1",
        "R2",
        "R3",
        "R4",
        "R_total",
        "R4_pass_rate",
        "coverage_recall",
        "S1",
        "S2",
        "S3",
        "notes",
    ]
    for name in ["score-sheet-R1.csv", "score-sheet-R2.csv"]:
        with (reviewer_dir / name).open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in key:
                writer.writerow([row["blind_id"], row["task_id"], row["task_type"]] + [""] * 17)

    guide = f"""# P0 评审员包

> 批次：`{args.batch_id}`
> 目标：2 名评审员独立评分 18 份盲产物，计算二次加权 kappa。

## 你要做什么

1. 阅读 [评分卡](../../../scoring-rubric.md) 与 [需求文档](../../../requirements-pdd-auth-cart-order.md)。
2. 按 `blind/S01.md` ~ `blind/S18.md` 逐份评分。
3. 在 `score-sheet-R1.csv` 或 `score-sheet-R2.csv` 填写 D1-D6（0-4）、R1-R4（仅用例任务）、coverage_recall（0-1）、S1/S2/S3 数量与备注。
4. 不要打开 `blind-key.json`；不要与其他评审员讨论分数。
5. 评分完成后交给运行负责人，用 `p0_kappa.py` 计算一致性。

## 评分口径

- D1 覆盖、D2 正确、D3 可执行、D4 风险与异常、D5 追溯与优先级、D6 结构与可读。
- 每项 0-4，必须有证据；备注里写证据位置，不要只写结论。
- S1 是认证绕过、金额/支付错误、超卖、越权、状态损坏、敏感数据泄露；出现即封顶 59。
- 只评产物质量，不猜它来自哪个 variant。

## 用例业务可读性专项（task_type=test_cases）

除 D1-D6 外，用例产物还要填 R1-R4（0-4）：

- R1 业务贴合：是否用业务语言描述业务行为，而不是技术实现语言。
- R2 精准简洁：标题与预期是否一句话说清，无空话、无模糊指代。
- R3 无自创晦涩词：是否出现 PRD 未定义的黑话、缩写或生造词。
- R4 3-5 秒理解：只看标题 + 预期首句，能否在 3-5 秒内说出「测什么、为什么、预期是什么」。

3-5 秒抽查：每份用例集随机抽 5 条，只看标题、关联需求 ID、预期首句，复述三件事，记录 pass/partial/fail。`R4_pass_rate` 填 0-1 的通过率，`R_total` 填 R1-R4 平均值。若 R_total < 2，D6 最高只能给 2 分。

## 文件

- `blind/`：18 份去标识产物。
- `score-sheet-R1.csv` / `score-sheet-R2.csv`：两名评审员各用一份。
- `blind-key.json`：仅运行负责人可见。

## 已知限制

- 本轮 runner 与评审者可能同源；若无法满足独立性，报告必须标注「未独立」。
- 评分卡为 v1.0.0；评分期间不要修改。
"""
    (reviewer_dir / "README.md").write_text(guide, encoding="utf-8")
    print(f"wrote {len(key)} blind artifacts and reviewer sheets to {reviewer_dir}")


if __name__ == "__main__":
    main()
