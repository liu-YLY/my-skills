"""validate_requirement_review.py 的单元测试。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_requirement_review import check  # noqa: E402

GOLD = Path(__file__).resolve().parents[5] / "docs/skill-evaluation/gold/requirement-review"


def codes(report: str, prd: str) -> set[str]:
    issues, _ = check(report, prd)
    return {i.code for i in issues}


def test_gold_reports_pass() -> None:
    for i in range(1, 6):
        report = (GOLD / f"RR-0{i}.md").read_text(encoding="utf-8")
        prd = (GOLD / "prd" / f"RR-0{i}.md").read_text(encoding="utf-8")
        issues, _ = check(report, prd)
        assert [i for i in issues if i.level == "error"] == [], (i, issues)


def test_missing_evidence_is_error() -> None:
    report = (GOLD / "RR-01.md").read_text(encoding="utf-8")
    prd = (GOLD / "prd" / "RR-01.md").read_text(encoding="utf-8")
    broken = report.replace("缺少时限/指标；影响对应测试点与用例设计", "-", 1)
    assert "RR_FIELD_REQUIRED" in codes(broken, prd)


def test_fabricated_quote_is_error() -> None:
    report = (GOLD / "RR-01.md").read_text(encoding="utf-8")
    prd = (GOLD / "prd" / "RR-01.md").read_text(encoding="utf-8")
    broken = report.replace("快速响应", "必须在 200ms 内响应", 1)
    assert "RR_QUOTE_NOT_FOUND" in codes(broken, prd)


def test_summary_mismatch_is_error() -> None:
    report = (GOLD / "RR-01.md").read_text(encoding="utf-8")
    prd = (GOLD / "prd" / "RR-01.md").read_text(encoding="utf-8")
    broken = re.sub(r"confirmed 5（P0 0", "confirmed 99（P0 0", report, count=1)
    assert "RR_SUMMARY_MISMATCH" in codes(broken, prd)


def test_missing_dimension_is_error() -> None:
    report = (GOLD / "RR-01.md").read_text(encoding="utf-8")
    prd = (GOLD / "prd" / "RR-01.md").read_text(encoding="utf-8")
    broken = re.sub(r"\| 范围与追溯 \| 是 \| \d+ \| - \|\n", "", report, count=1)
    assert "RR_DIMENSION_MISSING" in codes(broken, prd)
