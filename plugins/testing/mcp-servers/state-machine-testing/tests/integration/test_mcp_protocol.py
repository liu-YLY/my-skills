"""MCP 协议合规测试：stdio 握手 / 工具清单 / 工具调用 / 错误返回 / HTTP 传输。

v0.2.0 起为真实协议调用：通过 mcp SDK 客户端 spawn Server 子进程，
走完整 stdio / streamable-http 通道。
"""

from __future__ import annotations

import asyncio
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

EXPECTED_TOOLS = {
    "build_state_machine",
    "validate_state_machine",
    "generate_scenarios",
    "export_artifacts",
    "check_coverage",
}


def _server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "state_machine_testing_mcp.server"],
    )


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / f"{name}.json").read_text("utf-8"))


async def test_stdio_handshake_and_tool_list() -> None:
    """Server stdio 启动、协议握手、tools/list 返回 5 个工具。"""
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            assert init.serverInfo.name == "state-machine-testing"

            tools = await session.list_tools()
            assert {t.name for t in tools.tools} == EXPECTED_TOOLS


async def test_call_validate_state_machine() -> None:
    """call_tool: validate_state_machine 返回 9 项检查报告。"""
    sm = _load_fixture("order_refund_state_machine")
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "validate_state_machine",
                {"state_machine": sm, "strict": False},
            )
            assert not result.isError
            payload = json.loads(result.content[0].text)
            assert payload["overall_status"] in ("pass", "warn")
            assert len(payload["checks"]) == 9


async def test_call_build_state_machine_with_template() -> None:
    """call_tool: build_state_machine 确定性加载行业模板。"""
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "build_state_machine",
                {"requirement": "电商订单退款流程", "industry_template": "order-refund"},
            )
            assert not result.isError
            payload = json.loads(result.content[0].text)
            assert payload["state_machine"]["meta"]["object"] == "Order"
            assert len(payload["state_machine"]["states"]) == 6
            assert payload["mermaid_diagram"].startswith("stateDiagram-v2")


async def test_call_tool_invalid_payload_returns_error() -> None:
    """call_tool: 非法 payload 返回协议级 isError，而非崩溃。"""
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "validate_state_machine",
                {"state_machine": {"meta": {}}},
            )
            assert result.isError


async def test_http_transport_tool_list() -> None:
    """HTTP (streamable-http) 传输：握手 + tools/list。"""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "state_machine_testing_mcp.server",
            "--transport",
            "http",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                await asyncio.sleep(0.2)
        else:
            pytest.fail("HTTP server 未在 10s 内就绪")

        async with streamable_http_client(f"http://127.0.0.1:{port}/mcp") as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert {t.name for t in tools.tools} == EXPECTED_TOOLS
    finally:
        proc.terminate()
        proc.wait(timeout=10)
