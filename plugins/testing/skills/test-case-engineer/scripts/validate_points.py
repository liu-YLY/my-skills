#!/usr/bin/env python3
"""测试点清单静态校验器（D 类规则）。

校验对象：按 core.md 阶段 2 模板输出的 Markdown 测试点清单。
只校验可布尔判定的规则：结构、字段、枚举、重复、追溯、优先级分布、裁剪说明、预算。
不做语义判断——测试点是否真正覆盖需求由评审 agent 负责。

用法：
    python scripts/validate_points.py <points.md> [--requirements case.json --case-id TP-01]
                                      [--budget N] [--json] [--strict]
退出码：0 无 error；1 有 error；2 参数或解析错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RULES: dict[str, tuple[str, str]] = {
    "TP_SECTION": ("测试点清单缺失", "error"),
    "TP_HEADER": ("表头列不完整", "error"),
    "TP_ROW_COLUMNS": ("表格列数不符", "error"),
    "TP_ID_FORMAT": ("测试点 ID 格式", "error"),
    "TP_ID_UNIQUE": ("测试点 ID 唯一", "error"),
    "TP_FIELD_REQUIRED": ("必填字段缺失", "error"),
    "TP_DIMENSION_ENUM": ("维度枚举", "error"),
    "TP_PRIORITY_ENUM": ("优先级枚举", "error"),
    "TP_SINGLE_TARGET": ("单点单目标", "warning"),
    "TP_DUPLICATE": ("重复测试点", "error"),
    "TP_TRACE_MISSING": ("需求追溯缺失", "error"),
    "TP_PRIORITY_ALL_P0": ("优先级分布", "error"),
    "TP_CUT_RATIONALE": ("裁剪说明缺失", "error"),
    "TP_BUDGET": ("用例数预算", "warning"),
    "TP_REQUIREMENT_COVERAGE": ("需求条目覆盖", "error"),
    "TP_OUT_OF_SCOPE": ("范围外候选", "warning"),
}

DIMENSIONS = {"正向功能", "反向校验", "权限", "角色", "状态联动",
              "边界与限制", "UI 交互", "异常与容错", "权限/角色"}
HEADER = ["编号", "测试点", "维度", "设计方法", "优先级", "用例数", "需求引用", "来源", "裁剪说明"]
HEADER_LABELS = {"用例数": "用例数（估）", "裁剪说明": "裁剪说明"}
HEADER_ALIASES = {
    "编号": "编号", "测试点": "测试点", "维度": "维度", "设计方法": "设计方法",
    "优先级": "优先级", "用例数（估）": "用例数", "用例数": "用例数",
    "需求引用": "需求引用", "需求追溯": "需求引用", "来源": "来源",
    "裁剪说明": "裁剪说明", "裁剪理由": "裁剪说明",
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


def find_table(text: str) -> tuple[list[str], list[list[str]], int] | None:
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## 测试点清单")
    except StopIteration:
        start = -1
        for i, line in enumerate(lines):
            if "| 编号 |" in line and "测试点" in line:
                start = i - 1
                break
        if start < 0:
            return None
    i = start + 1
    while i < len(lines) and not lines[i].strip().startswith("|"):
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


def load_requirements(path: Path, case_id: str | None) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "cases" in data:
        if not case_id:
            raise SystemExit("--requirements 为种子集时必须提供 --case-id")
        for case in data["cases"]:
            if case.get("id") == case_id:
                return case
        raise SystemExit(f"找不到 case-id：{case_id}")
    return data


def check(text: str, requirements: dict | None, budget: int | None) -> tuple[list[Issue], dict]:
    issues: list[Issue] = []
    table = find_table(text)
    if not table:
        issues.append(Issue("TP_SECTION", "error", 0, "缺少「## 测试点清单」表格"))
        return issues, {}
    header, rows, first_row = table

    col: dict[str, int] = {}
    for idx, cell in enumerate(header):
        key = HEADER_ALIASES.get(cell.strip())
        if key:
            col[key] = idx
    missing = [HEADER_LABELS.get(h, h) for h in HEADER if h not in col]
    if missing:
        issues.append(Issue("TP_HEADER", "error", 0, f"表头缺少列：{'、'.join(missing)}"))
        return issues, {}

    ids: set[str] = set()
    seen: set[str] = set()
    priorities: Counter[str] = Counter()
    total_cases = 0
    covered_items: set[str] = set()
    point_texts: list[str] = []

    for offset, cells in enumerate(rows):
        line = first_row + offset
        if len(cells) != len(header):
            issues.append(Issue("TP_ROW_COLUMNS", "error", line, f"列数 {len(cells)} != 表头 {len(header)}", " | ".join(cells)))
            continue
        data = {key: cells[idx] for key, idx in col.items()}
        pid = data["编号"]
        if not re.fullmatch(r"TP-(?:\d{2,3}|[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{2,3})", pid):
            issues.append(Issue("TP_ID_FORMAT", "error", line, f"编号「{pid}」不符合 TP-序号 或 TP-模块-序号 格式"))
        elif pid in ids:
            issues.append(Issue("TP_ID_UNIQUE", "error", line, f"编号「{pid}」重复"))
        ids.add(pid)

        empty = [k for k in ["测试点", "维度", "设计方法", "优先级", "需求引用", "来源"] if not data[k].strip()]
        if empty:
            issues.append(Issue("TP_FIELD_REQUIRED", "error", line, f"必填字段为空：{'、'.join(empty)}"))

        if data["维度"] not in DIMENSIONS:
            issues.append(Issue("TP_DIMENSION_ENUM", "error", line, f"维度「{data['维度']}」不在 7 维度内"))
        if data["优先级"] not in {"P0", "P1", "P2", "P3"}:
            issues.append(Issue("TP_PRIORITY_ENUM", "error", line, f"优先级「{data['优先级']}」不是 P0–P3"))
        priorities[data["优先级"]] += 1

        if re.search(r"并且|同时|，并|；", data["测试点"]):
            issues.append(Issue("TP_SINGLE_TARGET", "warning", line, "测试点含并列/分号，可能验证多个目标", data["测试点"]))

        key = normalize(data["测试点"])
        if key in seen:
            issues.append(Issue("TP_DUPLICATE", "error", line, "测试点文本重复"))
        seen.add(key)
        point_texts.append(data["测试点"])

        trace = data["需求引用"].strip()
        if not trace or trace == "-":
            issues.append(Issue("TP_TRACE_MISSING", "error", line, "需求引用为空或 -"))

        try:
            cases = int(re.sub(r"\D", "", data["用例数"]) or 0)
        except ValueError:
            cases = 0
        total_cases += cases
        if cases == 0 and (not data["裁剪说明"].strip() or data["裁剪说明"].strip() == "-"):
            issues.append(Issue("TP_CUT_RATIONALE", "error", line, "用例数为 0 但未写裁剪说明"))

    if rows and all(p == "P0" for p in priorities) and len(rows) > 1:
        issues.append(Issue("TP_PRIORITY_ALL_P0", "error", 0, "所有测试点均为 P0，缺少优先级区分"))
    elif rows and priorities.get("P0", 0) / len(rows) > 0.8:
        issues.append(Issue("TP_PRIORITY_ALL_P0", "warning", 0, "P0 占比 >80%，需核对业务依据"))

    if budget is not None and total_cases > budget:
        issues.append(Issue("TP_BUDGET", "warning", 0, f"用例数合计 {total_cases} 超过预算 {budget}"))

    if requirements:
        for item in requirements.get("requirement_items", []):
            item_norm = normalize(item)
            if item_norm not in normalize(text):
                issues.append(Issue("TP_REQUIREMENT_COVERAGE", "error", 0,
                                    f"需求条目「{item}」未出现在任何测试点或需求引用中；如裁剪请在裁剪说明写明"))
            else:
                covered_items.add(item)
        for scope in requirements.get("out_of_scope", []):
            scope_norm = normalize(scope)
            for offset, cells in enumerate(rows):
                if len(cells) != len(header):
                    continue
                data = {key: cells[idx] for key, idx in col.items()}
                if scope_norm and scope_norm in normalize(data["测试点"]) and (
                        not data["裁剪说明"].strip() or data["裁剪说明"].strip() == "-"):
                    issues.append(Issue("TP_OUT_OF_SCOPE", "warning", first_row + offset,
                                        f"疑似范围外项「{scope}」但未写裁剪说明", data["测试点"]))

    return issues, {"rows": len(rows), "cases": total_cases,
                    "p0": priorities.get("P0", 0), "covered_items": len(covered_items)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="测试点清单静态校验器（D 类规则）")
    ap.add_argument("points", help="测试点清单 Markdown")
    ap.add_argument("--requirements", help="需求种子 JSON（case 或含 cases 的种子集）")
    ap.add_argument("--case-id", help="种子集中的 case id，如 TP-01")
    ap.add_argument("--budget", type=int, help="用例数预算上限")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--strict", action="store_true", help="warning 也视为失败")
    args = ap.parse_args(argv)

    path = Path(args.points)
    if not path.is_file():
        print("测试点清单路径不存在", file=sys.stderr)
        return 2
    requirements = load_requirements(Path(args.requirements), args.case_id) if args.requirements else None
    issues, stats = check(path.read_text(encoding="utf-8"), requirements, args.budget)
    errors = [i for i in issues if i.level == "error"]
    warns = [i for i in issues if i.level == "warning"]
    failed = bool(errors) or (args.strict and bool(warns))

    if args.json:
        print(json.dumps({
            "summary": {"issues": len(issues), "errors": len(errors), "warnings": len(warns),
                        "rows": stats.get("rows", 0), "cases": stats.get("cases", 0),
                        "p0": stats.get("p0", 0), "failed": failed},
            "by_rule": dict(Counter(i.code for i in issues).most_common()),
            "issues": [{"code": i.code, "level": i.level, "line": i.row, "msg": i.msg,
                        "evidence": i.evidence} for i in issues],
        }, ensure_ascii=False, indent=2))
    else:
        for i in issues:
            print(f"{'ERROR' if i.level == 'error' else 'WARN ':5} {i.code:24} L{i.row:<4} {i.msg}"
                  + (f"  ⏎ {i.evidence}" if i.evidence else ""))
        print("─" * 62)
        print(f"问题 {len(issues)}  ERROR {len(errors)}  WARN {len(warns)}  "
              f"测试点 {stats.get('rows', 0)}  用例数 {stats.get('cases', 0)}")
        if not issues:
            print("✓ 测试点清单 D 类规则通过（不代表覆盖质量达标）")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
