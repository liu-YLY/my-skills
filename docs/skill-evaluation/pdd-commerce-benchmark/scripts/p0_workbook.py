#!/usr/bin/env python3
"""Build Excel review workbooks for P0 reviewers.

Each workbook contains:
- 评分表: the 20-column score sheet (also exportable as CSV)
- 说明: how to fill and submit
- must-cover / review-checks: coverage checklists
- R1-R4: readability criteria
- S01..S18: full blind artifacts
"""

import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

BASE = Path(__file__).resolve().parents[1]
HEADER = [
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
WIDTHS = [10, 14, 18, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 8, 12, 14, 6, 6, 6, 60]


def guide_lines() -> list[str]:
    return [
        "P0 评审工作簿使用说明",
        "",
        "重要：CSV 只是打分表，不含产物正文；本工作簿的 S01-S18 工作表才是被评内容。",
        "",
        "1. 本工作簿给一名评审员使用；另一名评审员使用另一份工作簿。",
        "2. 先读“说明”，再按 S01-S18 逐个读产物，最后在“评分表”填分。",
        "3. 不要打开 blind-key.json，不要与其他评审员讨论分数。",
        "",
        "评分表列说明：",
        "D1-D6：0-4 整数。D1 覆盖、D2 正确、D3 可执行、D4 风险异常、D5 追溯优先级、D6 结构可读。",
        "R1-R4：仅 task_type=test_cases 填，0-4。R1 业务贴合、R2 精准简洁、R3 无自创词、R4 3-5 秒理解。",
        "R_total：可留空，导入脚本会按 R1-R4 平均计算。",
        "R4_pass_rate：仅 test_cases 填，0-1。例如 5 条中 4 条通过，填 0.8。",
        "coverage_recall：0-1，用 must-cover / review-checks 表计算。",
        "S1/S2/S3：该产物中对应严重度的错误条数，没有填 0。",
        "notes：写证据或扣分原因，至少一条。",
        "",
        "提交方式：",
        "1. 只保留“评分表”为当前工作表。",
        "2. 文件 -> 另存为 -> CSV UTF-8（逗号分隔）。",
        "3. 文件名改为 score-sheet-R1.csv 或 score-sheet-R2.csv。",
        "4. 交给运行负责人执行 p0_import_review.py。",
        "",
        "coverage_recall 公式：",
        "TP/TC：Σ(命中档位 × 权重) / Σ(权重)，权重 critical=3、high=2、medium=1；命中档位 0/0.5/1。",
        "REV：0.5 × 开放问题命中率 + 0.5 × 风险检查命中率。",
        "",
        "注意：评分卡为 v1.1.1，评分期间不要修改。",
    ]


def add_text_sheet(wb: Workbook, title: str, lines: list[str], width: int = 120) -> None:
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = width
    for i, line in enumerate(lines, start=1):
        cell = ws.cell(row=i, column=1, value=line)
        cell.alignment = Alignment(wrap_text=True, vertical="top")


def add_artifact_sheet(wb: Workbook, blind_id: str, meta: dict, text: str, blind_dir: Path) -> None:
    ws = wb.create_sheet(blind_id)
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 130
    ws["A1"] = f"{blind_id} | {meta['task_id']} | {meta['task_type']}"
    ws["A1"].font = Font(bold=True, size=12)
    ws["A2"] = "以下为产物全文；评分请回到“评分表”。"
    ws["A2"].font = Font(italic=True, color="666666")
    for i, line in enumerate(text.splitlines(), start=4):
        ws.cell(row=i, column=1, value=line).alignment = Alignment(wrap_text=True, vertical="top")


def add_reference_sheets(wb: Workbook, bench: dict) -> None:
    must_lines = [
        "ORDER must-cover 清单（TP/TC 用）",
        "",
        "逐条判断是否覆盖，记 0 / 0.5 / 1；coverage_recall = Σ(hit×weight)/Σ(weight)。",
        "",
        "ID | 优先级 | 权重 | 判定标准",
    ]
    pw = {"critical": 3, "high": 2, "medium": 1}
    for m in bench["must_cover"]:
        if m["module"] == "ORDER":
            must_lines.append(f"{m['id']} | {m['priority']} | {pw[m['priority']]} | {m['criterion']}")
    add_text_sheet(wb, "must-cover", must_lines)

    related = []
    for f in bench["open_findings"]:
        refs = f.get("requirement_ids", [])
        if any(r.startswith("BR-ORDER") or r in {"OQ-02", "OQ-07", "OQ-08"} for r in refs):
            related.append(f)
    checks = [c for c in bench["review_checks"] if c["module"] == "ORDER"]
    rev_lines = [
        "REV-ORDER 检查清单",
        "",
        "开放问题（3 条）：",
    ]
    rev_lines += [f"{f['id']} | {f['topic']} | {f['expected']}" for f in related]
    rev_lines += ["", "风险检查（4 条）："]
    rev_lines += [f"{c['id']} | {c['criterion']}" for c in checks]
    rev_lines += [
        "",
        "coverage_recall = 0.5 × 开放问题命中率 + 0.5 × 风险检查命中率。",
        "命中 1，部分 0.5，未命中 0。",
    ]
    add_text_sheet(wb, "review-checks", rev_lines)

    r_lines = [
        "用例业务可读性 R1-R4（仅 test_cases）",
        "",
        "R1 业务贴合：用业务语言，不用技术实现语言。",
        "R2 精准简洁：标题与预期一句话说清，无空话、无模糊指代。",
        "R3 无自创晦涩词：不用 PRD 未定义的黑话、缩写、生造词。",
        "R4 3-5 秒理解：只看标题 + 预期首句，能说出测什么/为什么/预期是什么。",
        "",
        "3-5 秒抽查：每份用例集随机抽 5 条，只看标题、关联需求 ID、预期首句；",
        "三项都能复述记 pass，两项 partial，一项及以下 fail；通过率填入 R4_pass_rate。",
        "R1-R4 平均 < 2 时，D6 最高 2 分。",
    ]
    add_text_sheet(wb, "R1-R4", r_lines)


def build(path: Path, key: list[dict], blind_dir: Path, bench: dict) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "评分表"
    ws.sheet_view.showGridLines = False
    ws.append(HEADER)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="2F5597")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for i, width in enumerate(WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width
    for row in key:
        ws.append([row["blind_id"], row["task_id"], row["task_type"]] + [None] * 17)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:T{len(key) + 1}"

    dv_0_4 = DataValidation(type="whole", operator="between", formula1="0", formula2="4", allow_blank=True)
    dv_0_1 = DataValidation(type="decimal", operator="between", formula1="0", formula2="1", allow_blank=True)
    dv_nonneg = DataValidation(type="whole", operator="greaterThanOrEqual", formula1="0", allow_blank=True)
    ws.add_data_validation(dv_0_4)
    ws.add_data_validation(dv_0_1)
    ws.add_data_validation(dv_nonneg)
    dv_0_4.add(f"D2:I{len(key) + 1}")
    dv_0_4.add(f"J2:M{len(key) + 1}")
    dv_0_1.add(f"O2:P{len(key) + 1}")
    dv_nonneg.add(f"Q2:S{len(key) + 1}")

    add_text_sheet(wb, "说明", guide_lines())
    add_reference_sheets(wb, bench)
    for row in key:
        text = (blind_dir / f"{row['blind_id']}.md").read_text(encoding="utf-8")
        add_artifact_sheet(wb, row["blind_id"], row, text, blind_dir)
    wb.save(path)


def main() -> None:
    batch = BASE / "runs" / "2026-11-17-p0"
    reviewer_dir = batch / "reviewer"
    blind_dir = reviewer_dir / "blind"
    key = json.loads((batch / "blind-key.json").read_text(encoding="utf-8"))
    bench = json.loads((BASE / "benchmark-v1.json").read_text(encoding="utf-8"))
    for name in ["P0-review-workbook-R1.xlsx", "P0-review-workbook-R2.xlsx"]:
        build(reviewer_dir / name, key, blind_dir, bench)
        print("wrote", reviewer_dir / name)


if __name__ == "__main__":
    main()
