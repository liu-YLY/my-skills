import json
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_review_schema_and_report_over_stdio():
    params = StdioServerParameters(command=sys.executable, args=["-m", "review_checker_mcp.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert {t.name for t in tools.tools} == {
                "review_test_cases", "generate_report", "check_semantic_conflicts"}
            result = await session.call_tool("generate_report", {"case_set": {"cases": [{
                "id": "TC_PAY_001", "title": "支付成功", "priority": "P1", "type": "functional",
                "steps": ["提交订单", "完成支付"], "expected_results": ["订单为已支付"],
                "checkpoints": [{"after_step": 1, "expected_results": ["订单为待支付"]}],
            }]}})
            assert not result.isError
            report = json.loads(result.content[0].text)
            assert report["grade"] == "A"
            assert report["total_issues"] == 0
            assert "覆盖度" in report["not_assessed"]
