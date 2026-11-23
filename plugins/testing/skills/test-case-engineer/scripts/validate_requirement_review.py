#!/usr/bin/env python3
"""需求评审报告静态校验器（D 类规则）。

校验对象：按 knowledge/requirement-review.md 模板输出的 Markdown 报告。
只校验可布尔判定的规则：结构、字段、枚举、摘要一致、维度覆盖、原文可回查。
不做语义判断——问题是否真实、级别是否合理由评审 agent 负责。

用法：
    python scripts/validate_requirement_review.py <report.md> --prd <prd.md> [--json] [--strict]
退出码：0 无 error；1 有 error；2 参数或解析错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RULES: dict[str, tuple[str, str]] = {
    "RR_SECTION": ("问题清单/维度覆盖缺失", "error"),
    "RR_HEADER": ("表头列不完整", "error"),
    "RR_ROW_COLUMNS": ("表格列数不符", "error"),
    "RR_ID_FORMAT": ("问题 ID 格式", "error"),
    "RR_ID_UNIQUE": ("问题 ID 唯一", "error"),
    "RR_FIELD_REQUIRED": ("必填字段缺失", "error"),
    "RR_TYPE_ENUM": ("问题类型枚举", "error"),
    "RR_SEVERITY_ENUM": ("严重级别枚举", "error"),
    "RR_STATUS_ENUM": ("状态枚举", "error"),
    "RR_LOCATION_FORMAT": ("位置格式", "warning"),
    "RR_QUOTE_NOT_FOUND": ("原文回查失败", "error"),
    "RR_DUPLICATE": ("重复问题", "warning"),
    "RR_SUMMARY_MISSING": ("问题统计缺失", "error"),
    "RR_SUMMARY_MISMATCH": ("统计与问题表不一致", "error"),
    "RR_DIMENSION_MISSING": ("维度覆盖缺失", "error"),
    "RR_DIMENSION_SUM": ("维度问题数合计不一致", "error"),
    "RR_UNASSESSED_REASON": ("未评估维度缺原因", "error"),
}

TYPES = {
    "模糊", "矛盾", "缺失", "不可测", "权限", "状态", "数据",
    "兼容性", "非功能", "依赖", "文案冲突", "安全", "体验", "安全/体验",
}
DIMENSIONS = [
    "完整性", "一致性", "明确性", "可测性", "状态与流程",
    "权限与角色", "数据与校验", "异常与容错", "非功能", "范围与追溯",
]
HEADER = ["ID", "位置", "原文", "类型", "级别", "影响", "问题", "待确认/建议", "状态"]
HEADER_ALIASES = {
    "ID": "ID", "位置": "位置", "原文": "原文", "类型": "类型",
    "级别": "级别", "严重级别": "级别", "影响": "影响", "问题": "问题",
    "待确认/建议": "待确认/建议", "待确认": "待确认/建议", "状态": "状态",
}


@dataclass
class Issue:
    code: str
    level: str
    row: int
    msg: str
    evidence: str = ""


def normalize(text: str) -> str:
    text = re.sub(r"[`\"'“”‘’]", "", text)
    return re.sub(r"\s+", "", text)


def split_row(line: str) -> list[str]:
    if line.strip().startswith("|"):
        line = line.strip()[1:]
    if line.rstrip().endswith("|"):
        line = line.rstrip()[:-1]
    return [cell.strip() for cell in line.split("|")]


def find_table(text: str, heading: str) -> tuple[list[str], list[list[str]], int] | None:
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return None
    i = start + 1
    while i < len(lines) and not lines[i].strip().startswith("|"):
        if lines[i].startswith("## "):
            return None
        i += 1
    if i >= len(lines):
        return None
    header = split_row(lines[i])
    table_start = i
    i += 1
    rows: list[list[str]] = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = split_row(lines[i])
        if not all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells):
            rows.append(cells)
        i += 1
    return header, rows, table_start + 1


def quote_segments(quote: str) -> list[str]:
    quote = quote.strip().strip("`")
    parts = [p.strip() for p in re.split(r"\s+/\s+|[；;]", quote) if p.strip()]
    return parts or [quote]


def check(report: str, prd: str) -> tuple[list[Issue], dict]:
    issues: list[Issue] = []
    table = find_table(report, "## 问题清单")
    if not table:
        issues.append(Issue("RR_SECTION", "error", 0, "缺少「## 问题清单」表格"))
        return issues, {}
    header, rows, first_row = table

    col: dict[str, int] = {}
    for idx, cell in enumerate(header):
        key = HEADER_ALIASES.get(cell.strip())
        if key:
            col[key] = idx
    missing = [h for h in HEADER if h not in col]
    if missing:
        issues.append(Issue("RR_HEADER", "error", 0, f"表头缺少列：{'、'.join(missing)}；需为 {' | '.join(HEADER)}"))
        return issues, {}

    ids: set[str] = set()
    seen: set[tuple[str, str, str]] = set()
    confirmed = 0
    candidate = 0
    severity_counter: Counter[str] = Counter()

    for offset, cells in enumerate(rows):
        line = first_row + offset
        if len(cells) != len(header):
            issues.append(Issue("RR_ROW_COLUMNS", "error", line, f"列数 {len(cells)} != 表头 {len(header)}", " | ".join(cells)))
            continue
        data = {key: cells[idx] for key, idx in col.items()}
        rid = data["ID"]
        if not re.fullmatch(r"RR-\d{3}", rid):
            issues.append(Issue("RR_ID_FORMAT", "error", line, f"ID「{rid}」不符合 RR-001 格式"))
        elif rid in ids:
            issues.append(Issue("RR_ID_UNIQUE", "error", line, f"ID「{rid}」重复"))
        ids.add(rid)

        required = ["位置", "原文", "类型", "级别", "影响", "问题", "待确认/建议", "状态"]
        empty = [k for k in required if not data[k].strip() or data[k].strip() == "-"]
        if empty:
            issues.append(Issue("RR_FIELD_REQUIRED", "error", line, f"必填字段为空：{'、'.join(empty)}"))

        type_value = data["类型"]
        if type_value not in TYPES and not any(t in type_value for t in TYPES):
            issues.append(Issue("RR_TYPE_ENUM", "error", line, f"类型「{type_value}」不在枚举内"))
        if data["级别"] not in {"P0", "P1", "P2", "P3"}:
            issues.append(Issue("RR_SEVERITY_ENUM", "error", line, f"级别「{data['级别']}」不是 P0–P3"))
        if data["状态"] not in {"confirmed", "candidate"}:
            issues.append(Issue("RR_STATUS_ENUM", "error", line, f"状态「{data['状态']}」不是 confirmed/candidate"))

        location = data["位置"]
        if not re.search(r"§\d|L\d+|全文|最后|行|[\w./-]+\.(md|txt|docx|pdf)", location):
            issues.append(Issue("RR_LOCATION_FORMAT", "warning", line, f"位置「{location}」缺少章节/行号/文件标识"))

        missing_segments = [seg for seg in quote_segments(data["原文"]) if normalize(seg) not in normalize(prd)]
        if missing_segments:
            issues.append(Issue("RR_QUOTE_NOT_FOUND", "error", line, f"原文回查失败：{' / '.join(missing_segments)}"))

        key = (normalize(location), normalize(data["原文"]), data["类型"], normalize(data["问题"]))
        if key in seen:
            issues.append(Issue("RR_DUPLICATE", "warning", line, "位置+原文+类型+问题重复"))
        seen.add(key)

        if data["状态"] == "confirmed":
            confirmed += 1
            severity_counter[data["级别"]] += 1
        else:
            candidate += 1

    summary_match = re.search(
        r"\*\*问题统计\*\*[：:]\s*confirmed\s+(\d+)\s*(?:[（(]P0\s*(\d+)\s*/\s*P1\s*(\d+)\s*/\s*P2\s*(\d+)\s*/\s*P3\s*(\d+)[）)])?\s*[；;]\s*candidate\s+(\d+)",
        report,
    )
    if not summary_match:
        issues.append(Issue("RR_SUMMARY_MISSING", "error", 0, "缺少「问题统计：confirmed N（P0 a / P1 b / P2 c / P3 d）；candidate M」"))
    else:
        claimed_confirmed = int(summary_match.group(1))
        claimed_sev = {f"P{i}": int(summary_match.group(i + 2) or 0) for i in range(4)}
        claimed_candidate = int(summary_match.group(6))
        if claimed_confirmed != confirmed or claimed_candidate != candidate:
            issues.append(Issue(
                "RR_SUMMARY_MISMATCH", "error", 0,
                f"统计 confirmed {claimed_confirmed}/candidate {claimed_candidate}，表内 confirmed {confirmed}/candidate {candidate}",
            ))
        elif any(claimed_sev[k] != severity_counter.get(k, 0) for k in claimed_sev):
            issues.append(Issue(
                "RR_SUMMARY_MISMATCH", "error", 0,
                f"严重级别统计 {claimed_sev} != 表内 {dict(severity_counter)}",
            ))

    dim_table = find_table(report, "## 维度覆盖")
    if not dim_table:
        issues.append(Issue("RR_DIMENSION_MISSING", "error", 0, "缺少「## 维度覆盖」表格"))
        return issues, {"confirmed": confirmed, "candidate": candidate, "rows": len(rows)}

    dim_header, dim_rows, dim_start = dim_table
    if not {"维度", "已检查", "问题数"}.issubset(set(dim_header)):
        issues.append(Issue("RR_HEADER", "error", 0, "维度覆盖表头需含 维度/已检查/问题数/未评估原因"))
    dim_sum = 0
    present: set[str] = set()
    for offset, cells in enumerate(dim_rows):
        line = dim_start + offset
        if len(cells) < 4:
            issues.append(Issue("RR_ROW_COLUMNS", "error", line, "维度覆盖表列数不足 4"))
            continue
        dim, checked, count, reason = cells[0], cells[1], cells[2], cells[3]
        present.add(dim)
        if checked not in {"是", "否"}:
            issues.append(Issue("RR_UNASSESSED_REASON", "error", line, f"已检查「{checked}」需为 是/否"))
        if checked == "否" and (not reason.strip() or reason.strip() == "-"):
            issues.append(Issue("RR_UNASSESSED_REASON", "error", line, f"维度「{dim}」未评估但未写原因"))
        try:
            dim_sum += int(count)
        except ValueError:
            issues.append(Issue("RR_DIMENSION_SUM", "error", line, f"问题数「{count}」不是整数"))
    missing_dims = [d for d in DIMENSIONS if d not in present]
    if missing_dims:
        issues.append(Issue("RR_DIMENSION_MISSING", "error", 0, f"缺少维度：{'、'.join(missing_dims)}"))
    if dim_sum != confirmed:
        issues.append(Issue("RR_DIMENSION_SUM", "error", 0, f"维度问题数合计 {dim_sum} != confirmed {confirmed}"))

    return issues, {"confirmed": confirmed, "candidate": candidate, "rows": len(rows)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="需求评审报告静态校验器（D 类规则）")
    ap.add_argument("report", help="评审报告 Markdown")
    ap.add_argument("--prd", required=True, help="PRD/需求文档，用于原文回查")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--strict", action="store_true", help="warning 也视为失败")
    args = ap.parse_args(argv)

    report_path = Path(args.report)
    prd_path = Path(args.prd)
    if not report_path.is_file() or not prd_path.is_file():
        print("报告或 PRD 路径不存在", file=sys.stderr)
        return 2
    issues, stats = check(report_path.read_text(encoding="utf-8"), prd_path.read_text(encoding="utf-8"))
    errors = [i for i in issues if i.level == "error"]
    warns = [i for i in issues if i.level == "warning"]
    failed = bool(errors) or (args.strict and bool(warns))

    if args.json:
        print(json.dumps({
            "summary": {"issues": len(issues), "errors": len(errors), "warnings": len(warns),
                        "confirmed": stats.get("confirmed"), "candidate": stats.get("candidate"),
                        "failed": failed},
            "by_rule": dict(Counter(i.code for i in issues).most_common()),
            "issues": [{"code": i.code, "level": i.level, "line": i.row, "msg": i.msg,
                        "evidence": i.evidence} for i in issues],
        }, ensure_ascii=False, indent=2))
    else:
        for i in issues:
            print(f"{'ERROR' if i.level == 'error' else 'WARN ':5} {i.code:22} L{i.row:<4} {i.msg}"
                  + (f"  ⏎ {i.evidence}" if i.evidence else ""))
        print("─" * 62)
        print(f"问题 {len(issues)}  ERROR {len(errors)}  WARN {len(warns)}  "
              f"confirmed {stats.get('confirmed', 0)}  candidate {stats.get('candidate', 0)}")
        if not issues:
            print("✓ 需求评审报告 D 类规则通过（不代表问题真实性与级别合理性）")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
