#!/usr/bin/env python3
"""Create blind copies, reviewer score sheets, and reviewer reference sheets.

The blind key must be kept away from reviewers. Reviewers only see blind/S*.md,
the score sheets, and the reference sheets.
"""

import argparse
import csv
import json
import random
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STRIP = re.compile(r"(运行：|with_skill|no_skill|A/A)", re.IGNORECASE)
PRIORITY_WEIGHT = {"critical": 3, "high": 2, "medium": 1}


def write_references(reviewer_dir: Path) -> None:
    bench = json.loads((BASE / "benchmark-v1.json").read_text(encoding="utf-8"))

    order_items = [m for m in bench["must_cover"] if m["module"] == "ORDER"]
    lines = [
        "# ORDER must-cover 清单（评审用）",
        "",
        "> 对每份 `TP-ORDER` / `TC-ORDER` 产物，逐条判断是否覆盖，记 0 / 0.5 / 1。",
        "> 不要求逐字匹配，要求产物中有对应测试行为且预期可判定。",
        "",
        "权重：`critical=3`、`high=2`、`medium=1`。",
        "",
        "```text",
        "coverage_recall = Σ(hit × weight) / Σ(weight)",
        "```",
        "",
        "| ID | 优先级 | 权重 | 判定标准 |",
        "|---|---|---:|---|",
    ]
    for m in order_items:
        w = PRIORITY_WEIGHT[m["priority"]]
        lines.append(f"| {m['id']} | {m['priority']} | {w} | {m['criterion']} |")
    lines += [
        "",
        "## 如何填 coverage_recall",
        "",
        "1. 逐条标 0 / 0.5 / 1。",
        "2. 用上面的公式算加权召回。",
        "3. 把 0-1 的结果填入 CSV 的 `coverage_recall`。",
        "4. 只写结果，不需要在 CSV 里列出每条命中；证据写进 `notes`。",
        "",
    ]
    (reviewer_dir / "must-cover-order.md").write_text("\n".join(lines), encoding="utf-8")

    related_findings = []
    for f in bench["open_findings"]:
        refs = f.get("requirement_ids", [])
        if any(r.startswith("BR-ORDER") or r in {"OQ-02", "OQ-07", "OQ-08"} for r in refs):
            related_findings.append(f)
    checks = [c for c in bench["review_checks"] if c["module"] == "ORDER"]

    lines = [
        "# 需求评审检查清单（REV-ORDER 用）",
        "",
        "## 1. 开放问题（相关 3 条）",
        "",
        "| ID | 主题 | 期望动作 |",
        "|---|---|---|",
    ]
    for f in related_findings:
        lines.append(f"| {f['id']} | {f['topic']} | {f['expected']} |")
    lines += [
        "",
        "## 2. 风险检查（4 条）",
        "",
        "| ID | 检查项 |",
        "|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c['id']} | {c['criterion']} |")
    lines += [
        "",
        "## 如何填 coverage_recall",
        "",
        "```text",
        "open_finding_rate = 命中的开放问题数 / 3",
        "risk_check_rate = 命中/部分命中的风险检查加权 / 4",
        "coverage_recall = 0.5 × open_finding_rate + 0.5 × risk_check_rate",
        "```",
        "",
        "命中记 1，部分命中记 0.5，未命中记 0。",
        "",
    ]
    (reviewer_dir / "review-checks-order.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", default="2026-11-17-p0")
    parser.add_argument("--seed", type=int, default=20261117)
    args = parser.parse_args()

    batch = BASE / "runs" / args.batch_id
    plan = json.loads((batch / "run-plan.json").read_text(encoding="utf-8"))
    reviewer_dir = batch / "reviewer"
    blind_dir = reviewer_dir / "blind"
    reviewer_dir.mkdir(exist_ok=True)
    blind_dir.mkdir(exist_ok=True)

    entries = []
    for run in plan:
        text = (batch / run["output_path"]).read_text(encoding="utf-8")
        cleaned = "\n".join(line for line in text.splitlines() if not STRIP.search(line))
        entries.append({**run, "text": cleaned})

    random.Random(args.seed).shuffle(entries)
    key = []
    pack_lines = [
        "# P0 盲评阅读包",
        "",
        "> 这里汇总了 18 份盲产物全文，方便连续阅读；分数仍填 `score-sheet-R1.csv` / `score-sheet-R2.csv`。",
        "> 不要根据顺序猜 variant；顺序是随机的。",
        "",
    ]
    for i, entry in enumerate(entries, start=1):
        blind_id = f"S{i:02d}"
        (blind_dir / f"{blind_id}.md").write_text(entry["text"], encoding="utf-8")
        pack_lines += [
            f"## {blind_id}（{entry['task_id']} / {entry['task_type']}）",
            "",
            entry["text"],
            "",
            "---",
            "",
        ]
        key.append(
            {
                "blind_id": blind_id,
                "run_id": entry["run_id"],
                "task_id": entry["task_id"],
                "task_type": entry["task_type"],
            }
        )
    (reviewer_dir / "review-pack.md").write_text("\n".join(pack_lines), encoding="utf-8")

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

    write_references(reviewer_dir)

    guide = f"""# P0 评审员包

> 批次：`{args.batch_id}`
> 目标：2 名评审员独立评分 18 份盲产物，计算二次加权 kappa。

## 一、评分表怎么用（推荐 Excel 工作簿）

- **CSV 只是打分表，不含产物正文**。产物正文在 `P0-review-workbook-R1.xlsx` 的 S01-S18 工作表，或 `review-pack.md` / `blind/`。
- `P0-review-workbook-R1.xlsx` 给**评审员 A**；`P0-review-workbook-R2.xlsx` 给**评审员 B**。一个工作簿已含评分表、说明、清单和 18 份全文。
- 如果坚持用 CSV：`score-sheet-R1.csv` 给 A，`score-sheet-R2.csv` 给 B；先读 `blind/Sxx.md` 再填。
- 不要由同一个人填两份；两位评审员不要互相讨论分数。
- 用 Excel / WPS / Numbers 打开，保存时保持 CSV 与 UTF-8。
- 不要改 `blind_id`、`task_id`、`task_type`；不要增删行；不要改列名。
- 每行对应一份产物。先读产物，再填这一行。

## 二、列怎么填

| 列 | 填什么 |
|---|---|
| `blind_id` / `task_id` / `task_type` | 已预填，不要改 |
| `D1`-`D6` | 0-4 整数；D1 覆盖、D2 正确、D3 可执行、D4 风险异常、D5 追溯优先级、D6 结构可读 |
| `R1`-`R4` | **仅 `task_type=test_cases` 填**，0-4；其他任务留空 |
| `R_total` | 可留空；脚本按 R1-R4 平均计算 |
| `R4_pass_rate` | **仅 `test_cases` 填**，0-1；例如 5 条中 4 条能在 3-5 秒复述，填 `0.8` |
| `coverage_recall` | 0-1；TP/TC 用 `must-cover-order.md` 计算，REV 用 `review-checks-order.md` 计算 |
| `S1` / `S2` / `S3` | 该产物中对应严重度的错误条数；没有填 `0` |
| `notes` | 关键证据、扣分原因；至少写 1 条，不要只写「良好」 |

## 三、评分步骤

1. 读 [评分卡](../../../scoring-rubric.md) 和 [需求文档](../../../requirements-pdd-auth-cart-order.md)。
2. **推荐直接用 Excel 打开 `P0-review-workbook-R1.xlsx`（评审员 A）或 `P0-review-workbook-R2.xlsx`（评审员 B）**：里面已经包含“评分表”、说明、must-cover、review-checks、R1-R4 和 S01-S18 全文。
3. 如果不使用工作簿，再读 `review-pack.md`（18 份产物全文），或按 `blind/S01.md` ~ `blind/S18.md` 逐个打开。
4. 先用 `must-cover-order.md` / `review-checks-order.md` 算 `coverage_recall`。
5. 再给 D1-D6；用例任务额外给 R1-R4。
6. 数 S1/S2/S3，写 notes。
7. 全部填完后，把“评分表”另存为 CSV UTF-8，交给运行负责人执行：

```bash
python3 scripts/p0_import_review.py --r1 runs/2026-11-17-p0/reviewer/score-sheet-R1.csv --r2 runs/2026-11-17-p0/reviewer/score-sheet-R2.csv
```

## 四、一个填写示例

TP 产物：

```text
S01,TP-ORDER,test_points,3,3,2,3,3,3,,,,,,0.82,0,0,1,"缺少对账补偿；其余主流程覆盖完整"
```

TC 产物：

```text
S05,TC-ORDER,test_cases,3,3,3,3,3,3,4,3,4,4,3.75,0.8,0.86,0,0,1,"3-5秒抽查4/5通过；支付回调幂等证据充分"
```

> 示例值仅演示格式，不要照抄分数。

## 五、评分口径

- D1 覆盖、D2 正确、D3 可执行、D4 风险与异常、D5 追溯与优先级、D6 结构与可读。
- 每项 0-4，必须有证据；备注里写证据位置，不要只写结论。
- S1 是认证绕过、金额/支付错误、超卖、越权、状态损坏、敏感数据泄露；出现即封顶 59。
- 只评产物质量，不猜它来自哪个 variant。

## 六、用例业务可读性专项（task_type=test_cases）

除 D1-D6 外，用例产物还要填 R1-R4（0-4）：

- R1 业务贴合：是否用业务语言描述业务行为，而不是技术实现语言。
- R2 精准简洁：标题与预期是否一句话说清，无空话、无模糊指代。
- R3 无自创晦涩词：是否出现 PRD 未定义的黑话、缩写或生造词。
- R4 3-5 秒理解：只看标题 + 预期首句，能否在 3-5 秒内说出「测什么、为什么、预期是什么」。

3-5 秒抽查：每份用例集随机抽 5 条，只看标题、关联需求 ID、预期首句，复述三件事，记录 pass/partial/fail。`R4_pass_rate` 填 0-1 的通过率。若 R1-R4 平均 < 2，D6 最高只能给 2 分。

## 七、提交前自检

- [ ] 18 行都有 `blind_id`，且只填了 S01-S18。
- [ ] D1-D6 都是 0-4 整数，没有空值。
- [ ] `task_type=test_cases` 的 R1-R4、R4_pass_rate 已填；其他任务留空。
- [ ] `coverage_recall` 是 0-1 的小数。
- [ ] S1/S2/S3 是整数，没有填空。
- [ ] notes 至少写了一条证据。
- [ ] 没有改列名、没有增删行、没有打开 blind-key.json。

## 八、文件

- `P0-review-workbook-R1.xlsx` / `P0-review-workbook-R2.xlsx`：推荐入口，内含评分表、说明、清单与 18 份产物全文。
- `review-pack.md`：18 份产物全文，适合连续阅读。
- `blind/`：18 份去标识产物，按 S01-S18 拆分。
- `score-sheet-R1.csv` / `score-sheet-R2.csv`：如果不想用 Excel 工作簿，可直接填这两个 CSV。
- `must-cover-order.md`：TP/TC 覆盖率检查清单。
- `review-checks-order.md`：REV 覆盖率检查清单。
- `../blind-key.json`：仅运行负责人可见，评审员不要打开。

## 九、已知限制

- 本轮 runner 与评审者可能同源；若无法满足独立性，报告必须标注「未独立」。
- 评分卡为 v1.1.1；评分期间不要修改。
"""
    (reviewer_dir / "README.md").write_text(guide, encoding="utf-8")
    print(f"wrote {len(key)} blind artifacts, score sheets, and reference sheets to {reviewer_dir}")


if __name__ == "__main__":
    main()
