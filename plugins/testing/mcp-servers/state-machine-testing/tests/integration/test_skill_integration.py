"""skill 协作契约测试。

验证 state-machine-test-engineer skill 增强模式依赖的两条 MCP 侧契约：
1. 阶段 3 → 阶段 4 流水线：validate_state_machine → generate_scenarios
   可通过协议连续调用，返回结构符合 skill 消费预期（9 项检查 /
   场景清单含依据类型标注）。
2. 降级信号：MCP Server 不可达时，客户端得到可判定异常（而非挂死），
   对应 skill SKILL.md 失败模式表「MCP 探测失败 → 降级独立模式」。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "state_machine_testing_mcp.server"],
    )


async def test_skill_validate_then_generate() -> None:
    """skill 阶段 3 校验 → 阶段 4 穷举的协作契约（真实协议调用）。"""
    sm = json.loads(
        (FIXTURES_DIR / "order_refund_state_machine.json").read_text("utf-8")
    )
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # skill 阶段 3：完整性检查（模型由 skill 阶段 2 产出）
            validate = await session.call_tool(
                "validate_state_machine",
                {"state_machine": sm, "strict": False},
            )
            assert not validate.isError
            report = json.loads(validate.content[0].text)
            assert report["overall_status"] in ("pass", "warn")
            assert len(report["checks"]) == 9

            # skill 阶段 4：10 类场景穷举
            generate = await session.call_tool(
                "generate_scenarios",
                {"state_machine": sm},
            )
            assert not generate.isError
            scenarios = json.loads(generate.content[0].text)
            assert len(scenarios["scenarios"]) >= 10
            # 依据类型强制标注是 skill 消费的核心字段
            assert all(
                s["evidence_type"] in ("需求明确", "合理推理", "待确认")
                for s in scenarios["scenarios"]
            )


async def test_skill_fallback_on_mcp_failure() -> None:
    """MCP Server 不可达时客户端快速失败，skill 据此降级独立模式。"""
    params = StdioServerParameters(
        command=sys.executable,
        args=["-c", "raise SystemExit(1)"],
    )
    # 异常类型随 SDK 版本可能为 ExceptionGroup / ConnectionError 等，
    # 断言核心契约：得到可判定异常（触发 skill 的降级分支），而非无限挂起
    with pytest.raises(BaseException):
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
