"""与 state-machine-test-engineer skill 的协作测试（mock）。"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="skill 协作测试待 mock 框架完善后实现")


def test_skill_validate_then_generate() -> None:
    """skill 阶段 3 校验 → 阶段 4 穷举的协作。"""
    # TODO: mock skill 调用 MCP validate_state_machine，再调用 generate_scenarios
    pass


def test_skill_fallback_on_mcp_failure() -> None:
    """MCP 失败时 skill 应降级到独立模式。"""
    # TODO: mock MCP 调用失败，验证 skill 仍输出完整结果
    pass
