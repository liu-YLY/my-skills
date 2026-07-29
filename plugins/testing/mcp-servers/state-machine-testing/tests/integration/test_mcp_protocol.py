"""MCP 协议合规测试 — v0.2.0 开发占位。

当前状态（v0.1.0）：MCP 协议层未实现，这些测试为 v0.2.0 开发路线图占位。
不构成当前能力声明：这些测试被 skip 不代表 MCP 协议已通过验证。

v0.2.0 完成协议层注册后，取消 skip 并实现以下测试：
- Server stdio 握手
- tools/list 返回 5 个工具
- 每个工具的 call_tool 协议调用
- 错误返回的协议合规性
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="v0.2.0 开发占位：MCP 协议层未实现，当前不构成能力声明")


def test_mcp_server_starts() -> None:
    """v0.2.0: 启动 Server 子进程，验证 stdio 协议握手。"""
    pass


def test_five_tools_registered() -> None:
    """v0.2.0: 调用 tools/list，验证 5 个工具名。"""
    pass
