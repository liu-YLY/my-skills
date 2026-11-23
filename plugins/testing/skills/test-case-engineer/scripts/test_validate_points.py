"""validate_points.py 的单元测试。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_points import check  # noqa: E402

HEADER = (
    "## 测试点清单\n\n"
    "| 编号 | 测试点 | 维度 | 设计方法 | 优先级 | 用例数（估） | 需求引用 | 来源 | 裁剪说明 |\n"
    "|------|--------|------|----------|--------|-------------|----------|------|----------|\n"
)
GOLD = Path(__file__).resolve().parents[5] / "docs/skill-evaluation/gold/test-points"


def codes(text: str, requirements: dict | None = None, budget: int | None = None) -> set[str]:
    issues, _ = check(text, requirements, budget)
    return {i.code for i in issues}


def test_gold_points_pass() -> None:
    for i in range(1, 6):
        text = (GOLD / f"TP-0{i}.md").read_text(encoding="utf-8")
        issues, _ = check(text, None, None)
        assert [i for i in issues if i.level == "error"] == [], (i, issues)


def test_detects_five_seeded_defects() -> None:
    text = HEADER + (
        "| TP-01-01 | 验证登录成功并且页面展示正确 | 正向功能 | 场景法 | P0 | 2 | 登录 | 需求 | - |\n"
        "| TP-01-02 | 验证登录成功并且页面展示正确 | 正向功能 | 场景法 | P0 | 2 | 登录 | 需求 | - |\n"
        "| TP-01-03 | 密码错误锁定 | 状态联动 | 状态迁移 | P0 | 0 | - | 需求 | - |\n"
    )
    found = codes(text)
    assert {"TP_SINGLE_TARGET", "TP_DUPLICATE", "TP_PRIORITY_ALL_P0",
            "TP_TRACE_MISSING", "TP_CUT_RATIONALE"}.issubset(found)


def test_short_tp_id_is_valid() -> None:
    text = HEADER + (
        "| TP-03 | 登录成功 | 正向功能 | 场景法 | P0 | 1 | 登录 | 需求 | - |\n"
        "| TP-03-02 | 密码错误 | 反向校验 | 等价类+边界值 | P1 | 1 | 密码 | 需求 | - |\n"
    )
    assert "TP_ID_FORMAT" not in codes(text)


def test_budget_warning() -> None:
    text = HEADER + (
        "| TP-01-01 | 登录成功 | 正向功能 | 场景法 | P0 | 5 | 登录 | 需求 | - |\n"
        "| TP-01-02 | 密码错误 | 反向校验 | 等价类+边界值 | P1 | 5 | 密码 | 需求 | - |\n"
    )
    assert "TP_BUDGET" in codes(text, None, budget=8)


def test_requirement_coverage_error() -> None:
    text = HEADER + (
        "| TP-01-01 | 登录成功 | 正向功能 | 场景法 | P0 | 1 | 登录 | 需求 | - |\n"
    )
    requirements = {"requirement_items": ["登录", "未覆盖的退款规则"], "out_of_scope": []}
    assert "TP_REQUIREMENT_COVERAGE" in codes(text, requirements)
