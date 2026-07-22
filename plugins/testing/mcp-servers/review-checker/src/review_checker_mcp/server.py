"""MCP Server 入口：注册评审校验工具。

启动方式：python -m review_checker_mcp.server

v0.2.0 新增 MCP 协议层注册，将 9 维度校验逻辑暴露为 MCP 工具，
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
    TestCaseSet,
)
from .validators import validate_all as _validate_all

__all__ = [
    "review_test_cases",
    "generate_report",
    "main",
]

# 9 维度顺序（用于维度统计的稳定输出）
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
    issue_case_ids = {i.case_id for i in issues if i.case_id != "-"}
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


def _register_mcp_tools(mcp_server) -> None:
    """向 MCP Server 注册评审校验工具。

    本函数在 mcp SDK 可用时调用，将上述函数注册为 MCP 工具。
    若 mcp SDK 不可用或 Server API 不兼容，本函数安全返回，
    模块仍可以作为普通 Python 库使用。
    """
    try:
        from mcp.server import Server  # type: ignore  # noqa: F401
    except ImportError:
        return

    # 防御性检查：不同 mcp SDK 版本的 Server API 可能不同
    # 真实 SDK 使用 list_tools/call_tool 装饰器，这里仅声明工具签名供 Host 发现
    if not hasattr(mcp_server, "tool"):
        return

    @mcp_server.tool()
    def review_test_cases_tool(case_set: TestCaseSet) -> list[Issue]:
        """对用例集执行 9 维度评审，返回全部 Issue。"""
        return review_test_cases(case_set)

    @mcp_server.tool()
    def generate_report_tool(case_set: TestCaseSet) -> ReviewReport:
        """基于评审结果生成度量报告（通过率/问题密度/评级/维度分布/严重等级分布）。"""
        return generate_report(case_set)


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
        print("Review Checker MCP Server v0.2.0 - 2 工具")
        print()
        print("1. review_test_cases(case_set)")
        print("   - 对用例集执行 9 维度评审，返回全部 Issue")
        print()
        print("2. generate_report(case_set)")
        print("   - 基于评审结果生成度量报告（通过率/问题密度/评级/维度分布/严重等级分布）")
        return 0

    try:
        from mcp.server import Server  # type: ignore
        from mcp.server.stdio import stdio_server  # type: ignore
    except ImportError:
        print(
            "mcp SDK 未安装。请运行: pip install mcp>=0.9.0",
            file=sys.stderr,
        )
        return 1

    mcp_server = Server("review-checker")
    _register_mcp_tools(mcp_server)

    if args.transport == "stdio":
        import asyncio

        async def run() -> None:
            async with stdio_server() as (read_stream, write_stream):
                await mcp_server.run(read_stream, write_stream)

        asyncio.run(run())
    else:
        print("HTTP 传输待 v0.3.0 实现，当前仅支持 stdio", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
