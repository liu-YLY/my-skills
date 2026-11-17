#!/usr/bin/env python3
"""Deterministic G0 structural checks for P0 artifacts.

This is intentionally not a quality judge. It only answers: can the artifact be
parsed, does it follow the output contract, and is traceability present?
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REQ_ID = re.compile(r"\b(?:BR-[A-Z]+-\d+|ORDER-F\d+|AC-ORDER-\d+)\b")
TC_HEADER = re.compile(r"^### (TC_[A-Z]+_.+_\d{3}): .+$", re.MULTILINE)
FORBIDDEN = ["准备相关数据", "执行对应操作", "功能正常", "符合预期"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_review(text: str) -> dict:
    issues = []
    for section in ["需求理解", "问题清单", "风险", "验收标准"]:
        if section not in text:
            issues.append(f"missing section: {section}")
    qids = sorted(set(re.findall(r"\bQ[-_]?\d{1,3}\b", text)))
    if len(qids) < 5:
        issues.append(f"too few Q_IDs: {len(qids)}")
    return {"g0_pass": not issues, "issues": issues, "item_count": len(qids)}


def check_test_points(text: str) -> dict:
    issues = []
    rows = [line for line in text.splitlines() if line.strip().startswith("| TP")]
    if not rows:
        issues.append("no test point rows")
    ids = []
    traceable = 0
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if cells:
            ids.append(cells[0])
        if REQ_ID.search(row):
            traceable += 1
    if len(ids) != len(set(ids)):
        issues.append("duplicate TP_ID")
    trace_rate = traceable / len(rows) if rows else 0.0
    if trace_rate < 0.8:
        issues.append(f"traceability below 80%: {trace_rate:.2f}")
    return {
        "g0_pass": not issues,
        "issues": issues,
        "item_count": len(rows),
        "traceability_rate": round(trace_rate, 3),
    }


def check_test_cases(text: str) -> dict:
    issues = []
    blocks = TC_HEADER.findall(text)
    if len(blocks) < 10:
        issues.append(f"too few case blocks: {len(blocks)}")
    required = ["前置条件", "测试数据", "步骤", "预期结果", "优先级", "关联需求ID"]
    missing = []
    for field in required:
        if field not in text:
            missing.append(field)
    if missing:
        issues.append("missing fields: " + ", ".join(missing))
    traceable = len(REQ_ID.findall(text))
    trace_rate = min(1.0, traceable / max(len(blocks), 1))
    if trace_rate < 0.8:
        issues.append(f"traceability below 80%: {trace_rate:.2f}")
    return {
        "g0_pass": not issues,
        "issues": issues,
        "item_count": len(blocks),
        "traceability_rate": round(trace_rate, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", default="2026-11-17-p0")
    args = parser.parse_args()

    batch = BASE / "runs" / args.batch_id
    plan = json.loads((batch / "run-plan.json").read_text(encoding="utf-8"))
    results = []
    for run in plan:
        path = batch / run["output_path"]
        if not path.exists():
            results.append({**run, "exists": False, "g0_pass": False, "issues": ["missing output"]})
            continue
        text = path.read_text(encoding="utf-8")
        if run["task_type"] == "requirement_review":
            checked = check_review(text)
        elif run["task_type"] == "test_points":
            checked = check_test_points(text)
        else:
            checked = check_test_cases(text)
        forbidden = [p for p in FORBIDDEN if p in text]
        results.append(
            {
                **run,
                "exists": True,
                "characters": len(text),
                "sha256": sha256(path),
                "forbidden_hits": forbidden,
                **checked,
            }
        )

    out = batch / "checks.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in results:
        status = "PASS" if r.get("g0_pass") else "FAIL"
        print(
            f"{status} {r['run_id']:<32} items={r.get('item_count', 0):<3} "
            f"trace={r.get('traceability_rate', '-')} issues={r.get('issues', [])}"
        )
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
