"""Extract normative statements from priority skills for slim-safe review.

The output is a first-pass inventory, not an automatic deletion list. D1-D5
classes are heuristics and must be confirmed during the corresponding batch.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from skill_context import load_config

MARKERS = ("必须", "禁止", "不得", "严禁", "强制", "不允许", "不可", "应当", "须")
EXCLUDED_FILES = {"README.md", "CHANGELOG.md"}
MOVE_FILES = {
    "knowledge/prompt-strategy.md",
    "knowledge/readability.md",
    "knowledge/writing-examples.md",
    "knowledge/large-scale-review.md",
    "knowledge/review-plan.md",
    "knowledge/report-template.md",
    "knowledge/usage-examples.md",
    "knowledge/mcp-enhancement.md",
}
REFERENCE_PREFIXES = (
    "knowledge/products/",
    "knowledge/industry-templates/",
    "templates/",
    "integrations/",
)
CONFLICT_PATTERNS = (
    ("评级阈值与 P0 规则", re.compile(r"已确认\s*P0|整体评级.*D|评级.*P0")),
    ("抽样模式口径", re.compile(r"sampled|抽样评审")),
)
KNOWN_CONFLICTS = (
    ("#13 评级阈值", "eval check 写 A/B/C/D 阈值，skill 另有「已确认 P0 → 整体评级 D」；需在判定口径中明确 P0 优先"),
    ("#7/#19 抽样标注", "eval check 期望 >100 条标注「抽样评审」，skill 的 S2 全量分批不实际抽样；需改为按策略判定"),
    ("check 术语依赖", "部分 check 要求出现「10 维度」「CHECKPOINT R3」等流程术语，偏向流程存在性而非产物质量"),
    ("软预算口径", "8/15/25 条软预算需与 check、writing-rules、prompt-strategy 三处保持一致"),
)
CLASS_RULES = {
    "D1": "纯重复：保留单一权威源，其余删为指针",
    "D2": "按需化：默认路径中的移出，已在按需的保留并标注",
    "D3": "过时/冲突：人工核对，按优先级修复，不直接删",
    "D4": "参考/示例：评估是否保留为按需材料，无证据不删",
    "D5": "行为规则：默认保留；删除需配对评测",
}


def normalize(text: str) -> str:
    text = re.sub(r"^\s*(?:[-*+]|\d+[.)]|>)\s*", "", text)
    return re.sub(r"\s+", "", text)


def is_normative(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 8:
        return False
    if re.match(r"^#{1,6}\s", stripped):
        return False
    if re.match(r"^\|?[\s:|-]+\|?$", stripped):
        return False
    if not any(marker in stripped for marker in MARKERS):
        return False
    substantive = re.sub(r"[`*#>\-|:：\s]", "", stripped)
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", substantive)) >= 8


def classify(rel: str, statement: str, duplicate_files: set[str],
             default_files: set[str]) -> tuple[str, str]:
    for label, pattern in CONFLICT_PATTERNS:
        if pattern.search(statement):
            return "D3", f"命中冲突关键词：{label}"
    if len(duplicate_files) >= 2:
        return "D1", f"在 {len(duplicate_files)} 个文件中重复"
    if rel.startswith(("knowledge/products/", "knowledge/industry-templates/", "templates/")):
        return "D4", "参考/示例材料"
    if rel in MOVE_FILES or rel.startswith(REFERENCE_PREFIXES):
        if rel in default_files:
            return "D2", "当前在默认路径，可评估按需化"
        return "D4", "已在按需文件，保留并核对读取时机"
    return "D5", "工作流/输出/安全等行为规则"


def escape_cell(text: str) -> str:
    text = text.replace("|", "\\|").replace("\n", " ")
    # Keep the statement readable without letting check-md-links parse the
    # original markdown links relative to the generated report.
    text = text.replace("[", "&#91;").replace("]", "&#93;")
    return text if len(text) <= 240 else text[:237] + "…"


def extract_skill(skill_dir: Path, skill: str, default_files: set[str]) -> list[dict]:
    rows = []
    occurrences = defaultdict(set)
    files = [
        path for path in skill_dir.rglob("*.md")
        if path.name not in EXCLUDED_FILES
    ]
    for path in sorted(files):
        rel = path.relative_to(skill_dir).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not is_normative(line):
                continue
            statement = line.strip()
            occurrences[normalize(statement)].add(rel)
    for path in sorted(files):
        rel = path.relative_to(skill_dir).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not is_normative(line):
                continue
            statement = line.strip()
            klass, reason = classify(
                rel, statement, occurrences[normalize(statement)], default_files
            )
            rows.append({
                "id": f"{skill}-{len(rows) + 1:03d}",
                "skill": skill,
                "file": rel,
                "line": line_number,
                "statement": statement,
                "class": klass,
                "reason": reason,
                "action": CLASS_RULES[klass],
                "review": "待复核",
            })
    return rows


def write_skill_report(path: Path, skill: str, rows: list[dict]) -> None:
    counts = Counter(row["class"] for row in rows)
    lines = [
        f"# 规范语句清单：{skill}",
        "",
        "> 由 `scripts/extract-rule-inventory.py` 生成。分类为启发式初筛，删除/移位前必须人工复核。",
        f"> 共 {len(rows)} 条：D1 重复 {counts.get('D1', 0)} / D2 移位 {counts.get('D2', 0)} / "
        f"D3 冲突 {counts.get('D3', 0)} / D4 参考 {counts.get('D4', 0)} / D5 行为 {counts.get('D5', 0)}",
        "",
        "| ID | 位置 | 规范语句 | 类别 | 判定依据 | 处置 | 复核 |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['id']} | `{row['file']}:{row['line']}` | {escape_cell(row['statement'])} | "
            f"{row['class']} | {row['reason']} | {row['action']} | {row['review']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--skills", nargs="+", default=[
        "test-case-engineer",
        "state-machine-test-engineer",
        "change-impact-analyzer",
        "testing-bundle",
    ])
    args = parser.parse_args()
    out = args.out or args.root / "docs/skill-evaluation/rule-inventory"
    out.mkdir(parents=True, exist_ok=True)
    config = load_config()
    default_files = {
        name: {
            item
            for mode in data.get("modes", {}).values()
            for item in mode.get("files", [])
        }
        for name, data in config["skills"].items()
    }
    all_rows = []
    summary = []
    for skill in args.skills:
        matches = sorted(args.root.glob(f"plugins/*/skills/{skill}"))
        if not matches:
            raise FileNotFoundError(f"skill not found: {skill}")
        rows = extract_skill(matches[0], skill, default_files.get(skill, set()))
        all_rows.extend(rows)
        write_skill_report(out / f"{skill}.md", skill, rows)
        summary.append((skill, len(rows), Counter(row["class"] for row in rows)))
    (out / "rule-inventory.json").write_text(
        json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    readme = [
        "# 规范语句清单索引",
        "",
        "> 由 `scripts/extract-rule-inventory.py` 生成；用于瘦身前确认每条规则的处置方式。",
        "> D1–D5 分类为启发式初筛，删除或移位前必须人工复核。",
        "",
        "| Skill | 条数 | D1 重复 | D2 移位 | D3 冲突 | D4 参考 | D5 行为 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for skill, count, counts in summary:
        readme.append(
            f"| [{skill}]({skill}.md) | {count} | {counts.get('D1', 0)} | {counts.get('D2', 0)} | "
            f"{counts.get('D3', 0)} | {counts.get('D4', 0)} | {counts.get('D5', 0)} |"
        )
    readme.extend([
        "",
        "## 已知冲突观察（来自 2026-11 评测报告，需在 1-8 逐条核对）",
        "",
        *[f"- **{name}**：{note}" for name, note in KNOWN_CONFLICTS],
        "",
        "## 处置类别",
        "",
        *[f"- **{key}**：{value}" for key, value in CLASS_RULES.items()],
        "",
        "## 使用方式",
        "",
        "1. 每个瘦身批次先在本清单中勾选对应条目，写明「保留 / 移动 / 合并 / 删除」。",
        "2. D1 条目必须指出保留的单一权威源。",
        "3. D2 条目必须在新位置保留摘要和链接，并通过 `check-knowledge-count.py`。",
        "4. D3 条目必须写明冲突双方和裁决优先级，不直接删。",
        "5. D4/D5 条目删除前必须有配对评测证据；否则只允许压缩措辞。",
    ])
    (out / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    for skill, count, counts in summary:
        print(f"{skill}: {count} rules; " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
