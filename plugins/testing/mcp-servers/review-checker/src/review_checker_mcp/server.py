"""MCP Server 入口（v0.2.0 实现）。

v0.1.0 仅提供 validators 确定性校验逻辑，MCP 协议层注册（@mcp.tool）
待 v0.2.0 实现。当前可通过 Python import 直接调用 validators.validate_all。
"""

from __future__ import annotations


def main() -> None:
    """MCP Server 启动入口（v0.2.0 实现）。"""
    raise NotImplementedError(
        "MCP Server 协议层注册待 v0.2.0。"
        "v0.1.0 请通过 from review_checker_mcp.validators import validate_all 直接调用。"
    )
