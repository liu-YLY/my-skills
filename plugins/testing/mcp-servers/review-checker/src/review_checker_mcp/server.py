"""MCP Server 入口：注册评审校验工具。

启动方式：python -m review_checker_mcp.server

v0.2.0 新增 MCP 协议层注册，将 10 维度校验逻辑暴露为 MCP 工具
（review_test_cases 9 维度用例级 + check_semantic_conflicts 第 10 维度语义一致性），
让 test-case-engineer 评审模式可通过 MCP 协议调用确定性校验。
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from typing import Literal

from .schemas import (
    DimensionStat,
    Issue,
    ReviewReport,
    SemanticFacts,
    TestCaseSet,
)
from .validators import (
    check_semantic_conflicts as _check_semantic_conflicts,
    validate_all as _validate_all,
)

__all__ = [
    "review_test_cases",
    "generate_report",
    "check_semantic_conflicts",
    "main",
]

# 10 维度顺序（用于维度统计的稳定输出；前 9 项由 review_test_cases 产出，第 10 项由 check_semantic_conflicts 产出）
DIMENSIONS = [
    "覆盖度",
    "优先级合理性",
    "字段规范",
    "可执行性",
    "冗余",
    "溯源",
    "可维护性",
    "可自动化",
    "测试数据依赖",
    "语义一致性",
]


def review_test_cases(case_set: TestCaseSet) -> list[Issue]:
    """对用例集执行 9 维度评审，返回全部 Issue。

    这是核心校验工具，将 review-mode.md R2 表的判定规则
    实现为确定性机器校验，不依赖 LLM 推理。
    """
    return _validate_all(case_set)


def generate_report(case_set: TestCaseSet, issues: list[Issue] | None = None) -> ReviewReport:
    """基于评审结果生成度量报告。

    含通过率、问题密度、整体评级（A/B/C/D）、维度分布、严重等级分布。
    """
    if issues is None:
        issues = review_test_cases(case_set)

    total_cases = len(case_set.cases)
    # 拆分逗号分隔的 case_id（语义冲突对/闭环），分别计入
    issue_case_ids: set[str] = set()
    for i in issues:
        if i.case_id == "-":
            continue
        for cid in i.case_id.split(","):
            cid = cid.strip()
            if cid:
                issue_case_ids.add(cid)
    issue_cases = len(issue_case_ids)
    pass_rate = (total_cases - issue_cases) / total_cases if total_cases > 0 else 0.0
    total_issues = len(issues)
    issue_density = total_issues / total_cases if total_cases > 0 else 0.0

    # 整体评级
    if pass_rate >= 0.95 and issue_density < 0.5:
        grade: Literal["A", "B", "C", "D"] = "A"
    elif pass_rate >= 0.80:
        grade = "B"
    elif pass_rate >= 0.60:
        grade = "C"
    else:
        grade = "D"

    # 维度统计
    dim_counts: Counter[str] = Counter(i.dimension for i in issues)
    dim_severity: dict[str, list[str]] = {}
    for issue in issues:
        dim_severity.setdefault(issue.dimension, []).append(issue.severity.value)

    dimension_stats: list[DimensionStat] = []
    for dim in DIMENSIONS:
        count = dim_counts.get(dim, 0)
        if count > 0:
            sev_counts = Counter(dim_severity[dim])
            main_sev = sev_counts.most_common(1)[0][0]
        else:
            main_sev = "-"
        dimension_stats.append(
            DimensionStat(dimension=dim, issue_count=count, main_severity=main_sev)
        )

    # 严重等级统计
    severity_counts: Counter[str] = Counter(i.severity.value for i in issues)
    severity_stats = {sev: severity_counts.get(sev, 0) for sev in ("P0", "P1", "P2")}

    return ReviewReport(
        total_cases=total_cases,
        issue_cases=issue_cases,
        pass_rate=round(pass_rate, 4),
        total_issues=total_issues,
        issue_density=round(issue_density, 4),
        grade=grade,
        issues=issues,
        dimension_stats=dimension_stats,
        severity_stats=severity_stats,
    )


def check_semantic_conflicts(facts: list[SemanticFacts]) -> list[Issue]:
    """第 10 维度：语义一致性冲突检测。

    接收 skill 侧 LLM 抽取的 SemanticFacts 列表，执行 3 类确定性冲突检测：
      ① 前置条件状态矛盾（P0）
      ② 同输入不同预期（P0）
      ③ 数据依赖闭环（P1）

    与 review_test_cases（9 维度）独立，skill 侧应分别调用后合并 issues
    传入 generate_report。
    """
    return _check_semantic_conflicts(facts)


def _register_mcp_tools(mcp_server) -> None:
    """向 MCP Server 注册评审校验工具。

    本函数在 mcp SDK 可用时调用，将上述函数注册为 MCP 工具。
    若 mcp SDK 不可用，本函数安全返回，模块仍可以作为普通 Python 库使用。
    """
    @mcp_server.tool()
    def review_test_cases(case_set: TestCaseSet) -> list[Issue]:
        """对用例集执行 9 维度评审，返回全部 Issue。"""
        return _validate_all(case_set)

    @mcp_server.tool()
    def generate_report(case_set: TestCaseSet, issues: list[Issue] | None = None) -> ReviewReport:
        """基于评审结果生成度量报告（通过率/问题密度/评级/维度分布/严重等级分布）。

        issues 参数可传入预计算的 Issue 列表（如合并了 9+10 维度的结果）；
        若不传则自动执行 9 维度评审。
        """
        if issues is None:
            issues = review_test_cases(case_set)

        total_cases = len(case_set.cases)
        issue_case_ids: set[str] = set()
        for i in issues:
            if i.case_id == "-":
                continue
            for cid in i.case_id.split(","):
                cid = cid.strip()
                if cid:
                    issue_case_ids.add(cid)
        issue_cases = len(issue_case_ids)
        pass_rate = (total_cases - issue_cases) / total_cases if total_cases > 0 else 0.0
        total_issues = len(issues)
        issue_density = total_issues / total_cases if total_cases > 0 else 0.0

        if pass_rate >= 0.95 and issue_density < 0.5:
            grade: Literal["A", "B", "C", "D"] = "A"
        elif pass_rate >= 0.80:
            grade = "B"
        elif pass_rate >= 0.60:
            grade = "C"
        else:
            grade = "D"

        dim_counts: Counter[str] = Counter(i.dimension for i in issues)
        dim_severity: dict[str, list[str]] = {}
        for issue in issues:
            dim_severity.setdefault(issue.dimension, []).append(issue.severity.value)

        dimension_stats: list[DimensionStat] = []
        for dim in DIMENSIONS:
            count = dim_counts.get(dim, 0)
            if count > 0:
                sev_counts = Counter(dim_severity[dim])
                main_sev = sev_counts.most_common(1)[0][0] if sev_counts else "-"
            else:
                main_sev = "-"
            dimension_stats.append(
                DimensionStat(dimension=dim, issue_count=count, main_severity=main_sev)
            )

        severity_counts: Counter[str] = Counter(i.severity.value for i in issues)
        severity_stats = {sev: severity_counts.get(sev, 0) for sev in ("P0", "P1", "P2")}

        return ReviewReport(
            total_cases=total_cases,
            issue_cases=issue_cases,
            pass_rate=round(pass_rate, 4),
            total_issues=total_issues,
            issue_density=round(issue_density, 4),
            grade=grade,
            issues=issues,
            dimension_stats=dimension_stats,
            severity_stats=severity_stats,
        )

    @mcp_server.tool()
    def check_semantic_conflicts(facts: list[SemanticFacts]) -> list[Issue]:
        """第 10 维度：语义一致性冲突检测（前置条件矛盾/同输入异预期/依赖闭环）。"""
        return _check_semantic_conflicts(facts)


def main() -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        prog="review-checker-mcp",
        description="Review Checker MCP Server v0.2.0",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="传输方式（默认 stdio）",
    )
    parser.add_argument(
        "--help-tools",
        action="store_true",
        help="打印工具帮助信息后退出",
    )
    args = parser.parse_args()

    if args.help_tools:
        print("Review Checker MCP Server v0.2.0 - 3 工具")
        print()
        print("1. review_test_cases(case_set)")
        print("   - 对用例集执行 9 维度评审，返回全部 Issue")
        print()
        print("2. generate_report(case_set, issues=None)")
        print("   - 基于评审结果生成度量报告（通过率/问题密度/评级/维度分布/严重等级分布）")
        print()
        print("3. check_semantic_conflicts(facts)")
        print("   - 第 10 维度：语义一致性冲突检测（前置条件矛盾/同输入异预期/依赖闭环）")
        return 0

    if args.transport == "http":
        print("HTTP 传输待 v0.3.0 实现，当前仅支持 stdio", file=sys.stderr)
        return 1

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "mcp SDK 未安装。请运行: pip install mcp>=0.9.0",
            file=sys.stderr,
        )
        return 1

    mcp_server = FastMCP("review-checker")
    _register_mcp_tools(mcp_server)
    mcp_server.run(transport="stdio")

    return 0


if __name__ == "__main__":
    sys.exit(main())
