"""skill 协作契约测试。

验证 state-machine-test-engineer skill 增强模式依赖的两条 MCP 侧契约：
1. 阶段 3 → 阶段 4 流水线：validate_state_machine → generate_scenarios
   可通过协议连续调用，返回结构符合 skill 消费预期（10 项检查 /
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
            assert len(report["checks"]) == 10

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


def test_skill_model_example_parses_and_passes_structure():
    import re
    import yaml
    from state_machine_testing_mcp.schemas import StateMachine
    from state_machine_testing_mcp.validators import validate_state_machine

    core = (Path(__file__).resolve().parents[4] /
            "skills/state-machine-test-engineer/state-machine-core.md")
    match = re.search(r"```yaml\n(state_machine:\n.*?)```", core.read_text(), re.S)
    assert match, "state-machine-core.md must contain the canonical state_machine example"
    block = match.group(1)
    sm = StateMachine.model_validate(yaml.safe_load(block)["state_machine"])
    report = validate_state_machine(sm)
    assert report.overall_status == "pass"
    assert report.manual_review_required



def test_all_scenario_knowledge_examples_validate_and_match_references():
    import re
    import yaml
    from state_machine_testing_mcp.schemas import Scenario, StateMachine, ScenarioList
    from state_machine_testing_mcp.coverage import check_coverage
    knowledge = (Path(__file__).resolve().parents[4] /
                 "skills/state-machine-test-engineer/knowledge/scenario-types.md").read_text()
    blocks = [yaml.safe_load(block) for block in re.findall(r"```yaml\n(.*?)```", knowledge, re.S)]
    sm = StateMachine.model_validate(next(b["state_machine"] for b in blocks if isinstance(b, dict)))
    scenarios = [Scenario.model_validate(item) for block in blocks if isinstance(block, list) for item in block]
    assert len(scenarios) == 10
    assert all(s.expected_target_state == "待确认" or s.expected_target_state in {x.name for x in sm.states}
               for s in scenarios)
    assert all(s.source for s in scenarios)
    report = check_coverage(sm, ScenarioList(scenarios=scenarios))
    assert report.unmatched_scenarios == []
    assert report.transition_coverage == report.forbidden_coverage == 1


def test_forbidden_source_survives_validation_and_export():
    from state_machine_testing_mcp.schemas import ForbiddenTransition
    item = ForbiddenTransition.model_validate({"from": "A", "to": "B", "reason": "禁止",
                                              "source": "PRD §1", "evidence_type": "需求明确"})
    assert item.model_dump()["source"] == "PRD §1"



def test_industry_scenario_examples_use_the_same_complete_contract():
    import re
    import yaml
    from state_machine_testing_mcp.builders import AVAILABLE_TEMPLATES, _build_industry_template
    from state_machine_testing_mcp.schemas import ScenarioList
    from state_machine_testing_mcp.coverage import check_coverage
    base = Path(__file__).resolve().parents[4] / "skills/state-machine-test-engineer/knowledge/industry-templates"
    for name in AVAILABLE_TEMPLATES:
        sm = _build_industry_template(name)
        for block in re.findall(r"```yaml\n(.*?)```", (base / (name + ".md")).read_text(), re.S):
            data = yaml.safe_load(block)
            if not isinstance(data, dict) or "scenarios" not in data:
                continue
            scenarios = ScenarioList.model_validate(data)
            assert len(scenarios.scenarios) == 10
            for s in scenarios.scenarios:
                assert s.expected_target_state == "待确认" or s.expected_target_state in {x.name for x in sm.states}
                assert s.source
            assert check_coverage(sm, scenarios).unmatched_scenarios == [], name


def test_unknown_permission_examples_do_not_assert_rejection_targets():
    import re
    import yaml
    from state_machine_testing_mcp.schemas import Scenario
    knowledge = Path(__file__).resolve().parents[4] / "skills/state-machine-test-engineer/knowledge"
    paths = [knowledge / "scenario-types.md", *sorted((knowledge / "industry-templates").glob("*.md"))]
    for path in paths:
        for block in re.findall(r"```yaml\n(.*?)```", path.read_text(), re.S):
            data = yaml.safe_load(block)
            raw = data if isinstance(data, list) else data.get("scenarios", []) if isinstance(data, dict) else []
            for item in raw:
                if item.get("risk_type") == "access_control" and item.get("evidence_type") == "待确认":
                    scenario = Scenario.model_validate(item)
                    assert scenario.expected_target_state == "待确认", str(path)
                    assert scenario.expected_target_state_reason and scenario.forbidden_states == []
