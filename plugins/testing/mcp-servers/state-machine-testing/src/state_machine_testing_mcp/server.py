"""MCP Server 入口：注册 5 个工具。

启动方式：python -m state_machine_testing_mcp.server
"""

from __future__ import annotations

import argparse
import sys
from typing import Literal

from .builders import build_state_machine as _build_state_machine
from .coverage import check_coverage as _check_coverage
from .exporters import export_artifacts as _export_artifacts
from .generators import generate_scenarios as _generate_scenarios
from .schemas import (
    CoverageReport,
    ExportResult,
    ScenarioList,
    StateMachine,
    StateMachineBuildResult,
    ValidationReport,
)
from .validators import validate_state_machine as _validate_state_machine

__all__ = [
    "build_state_machine",
    "validate_state_machine",
    "generate_scenarios",
    "export_artifacts",
    "check_coverage",
    "main",
]


def build_state_machine(
    requirement: str,
    object_hint: str | None = None,
    industry_template: str | None = None,
) -> StateMachineBuildResult:
    """确定性加载行业模板作为建模起点；自由文本建模由调用方 LLM 完成。"""
    return _build_state_machine(requirement, object_hint, industry_template)


def validate_state_machine(state_machine: StateMachine, strict: bool = True) -> ValidationReport:
    """校验状态机完整性与一致性（9 项检查）。"""
    return _validate_state_machine(state_machine, strict)


def generate_scenarios(
    state_machine: StateMachine,
    scenario_types: list[str] | None = None,
    evidence_filter: str | None = None,
) -> ScenarioList:
    """基于状态机穷举 10 类场景。"""
    return _generate_scenarios(state_machine, scenario_types, evidence_filter)


def export_artifacts(
    state_machine: StateMachine,
    scenarios: ScenarioList | None = None,
    formats: list[Literal["markdown", "json", "mermaid"]] | None = None,
    output_dir: str = "./state-machine-outputs",
) -> ExportResult:
    """导出为 Markdown / JSON / Mermaid。"""
    return _export_artifacts(state_machine, scenarios, formats, output_dir)


def check_coverage(state_machine: StateMachine, scenarios: ScenarioList) -> CoverageReport:
    """覆盖度检查。"""
    return _check_coverage(state_machine, scenarios)


def _register_mcp_tools(mcp_server) -> None:
    """向 MCP Server 注册 5 个工具。

    本函数在 mcp SDK 可用时调用，将上述函数注册为 MCP 工具。
    若 mcp SDK 不可用，本函数不会被调用，模块仍可以作为普通 Python 库使用。
    """
    @mcp_server.tool()
    def build_state_machine(
        requirement: str,
        object_hint: str | None = None,
        industry_template: str | None = None,
    ) -> StateMachineBuildResult:
        """确定性加载行业模板作为建模起点；自由文本建模由调用方 LLM 完成。"""
        return _build_state_machine(requirement, object_hint, industry_template)

    @mcp_server.tool()
    def validate_state_machine(
        state_machine: StateMachine,
        strict: bool = True,
    ) -> ValidationReport:
        """校验状态机完整性与一致性。"""
        return _validate_state_machine(state_machine, strict)

    @mcp_server.tool()
    def generate_scenarios(
        state_machine: StateMachine,
        scenario_types: list[str] | None = None,
        evidence_filter: str | None = None,
    ) -> ScenarioList:
        """基于状态机穷举 10 类场景。"""
        return _generate_scenarios(state_machine, scenario_types, evidence_filter)

    @mcp_server.tool()
    def export_artifacts(
        state_machine: StateMachine,
        scenarios: ScenarioList | None = None,
        formats: list[Literal["markdown", "json", "mermaid"]] | None = None,
        output_dir: str = "./state-machine-outputs",
    ) -> ExportResult:
        """导出为 Markdown / JSON / Mermaid。"""
        return _export_artifacts(state_machine, scenarios, formats, output_dir)

    @mcp_server.tool()
    def check_coverage(
        state_machine: StateMachine,
        scenarios: ScenarioList,
    ) -> CoverageReport:
        """覆盖度检查。"""
        return _check_coverage(state_machine, scenarios)


def main() -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        prog="state-machine-testing-mcp",
        description="State Machine Testing MCP Server v0.2.0",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="传输方式（默认 stdio）",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP 传输监听地址（默认 127.0.0.1）",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP 传输监听端口（默认 8000）",
    )
    parser.add_argument(
        "--help-tools",
        action="store_true",
        help="打印 5 个工具的帮助信息后退出",
    )
    args = parser.parse_args()

    if args.help_tools:
        print("State Machine Testing MCP Server - 5 工具")
        print()
        print("1. build_state_machine(requirement, object_hint?, industry_template?)")
        print("   - 确定性加载行业模板作为建模起点；自由文本建模由调用方 LLM 完成")
        print()
        print("2. validate_state_machine(state_machine, strict=True)")
        print("   - 校验状态机完整性与一致性（9 项检查）")
        print()
        print("3. generate_scenarios(state_machine, scenario_types?, evidence_filter?)")
        print("   - 基于状态机穷举 10 类场景")
        print()
        print("4. export_artifacts(state_machine, scenarios?, formats?, output_dir?)")
        print("   - 导出为 Markdown / JSON / Mermaid")
        print()
        print("5. check_coverage(state_machine, scenarios)")
        print("   - 覆盖度检查")
        return 0

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "mcp SDK 未安装。请运行: pip install 'mcp>=0.9.0,<2.0.0'",
            file=sys.stderr,
        )
        return 1

    mcp_server = FastMCP("state-machine-testing")
    _register_mcp_tools(mcp_server)

    if args.transport == "http":
        mcp_server.settings.host = args.host
        mcp_server.settings.port = args.port
        mcp_server.run(transport="streamable-http")
        return 0

    mcp_server.run(transport="stdio")

    return 0


if __name__ == "__main__":
    sys.exit(main())
