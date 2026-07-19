"""MCP 协议合规测试（待 mcp SDK 集成后完善）。"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="MCP 协议测试待 mcp SDK 集成后完善")


def test_mcp_server_starts() -> None:
    """MCP Server 应能启动。"""
    # TODO: 启动 Server 子进程，验证 stdio 协议握手
    pass


def test_five_tools_registered() -> None:
    """5 个工具应都注册。"""
    # TODO: 调用 tools/list，验证 5 个工具名
    pass
