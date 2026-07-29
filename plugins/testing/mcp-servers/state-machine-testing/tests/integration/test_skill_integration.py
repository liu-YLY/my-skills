"""skill 协作测试 — v0.2.0 开发占位。

当前状态（v0.1.0）：MCP 协议层未实现，skill 始终以独立模式运行。
这些测试为 v0.2.0 协议层完成后 skill-MCP 协作的路线图占位。
不构成当前能力声明：这些测试被 skip 不代表 skill-MCP 协作已通过验证。

v0.2.0 完成后测试内容：
- skill 阶段 3 调用 validate_state_machine → 阶段 4 调用 generate_scenarios
- MCP 调用失败时 skill 降级到独立模式
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="v0.2.0 开发占位：MCP 协议层未实现，当前不构成能力声明")


def test_skill_validate_then_generate() -> None:
    """v0.2.0: skill 阶段 3 校验 → 阶段 4 穷举的协作。"""
    pass


def test_skill_fallback_on_mcp_failure() -> None:
    """v0.2.0: MCP 失败时 skill 应降级到独立模式。"""
    pass
