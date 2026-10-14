"""build_state_machine 单元测试：模板确定性加载 / 无效模板 / 自由文本契约。"""

from __future__ import annotations

import pytest

from state_machine_testing_mcp.builders import (
    AVAILABLE_TEMPLATES,
    _build_industry_template,
    build_state_machine,
)


class TestIndustryTemplateLoading:
    """行业模板加载：4 个模板全部可解析且 schema 合规。"""

    @pytest.mark.parametrize("template_name", AVAILABLE_TEMPLATES)
    def test_template_loads_into_valid_state_machine(self, template_name: str) -> None:
        sm = _build_industry_template(template_name)
        assert sm is not None, f"模板 {template_name} 加载失败"
        assert len(sm.states) >= 5
        assert len(sm.transitions) >= 5
        assert sm.meta.object
        # 依据类型必填由 pydantic 保证：每条 transition 都有合法枚举值
        for t in sm.transitions:
            assert t.evidence_type.value in ("需求明确", "合理推理", "待确认")

    def test_unknown_template_returns_none(self) -> None:
        assert _build_industry_template("nonexistent") is None


class TestBuildStateMachine:
    """build_state_machine 工具入口。"""

    def test_with_industry_template_returns_template_model(self) -> None:
        result = build_state_machine(
            requirement="电商订单退款流程",
            industry_template="order-refund",
        )
        sm = result.state_machine
        assert sm.meta.object == "Order"
        assert len(sm.states) == 6
        assert result.extracted_objects == ["Order"]
        assert result.mermaid_diagram.startswith("stateDiagram-v2")
        # 适配提示为待确认歧义，不冒充已建模完成
        assert result.ambiguities[0].id == "AMB-TEMPLATE-ADAPT"
        assert result.ambiguities[0].evidence_type.value == "待确认"
        assert "order-refund" in result.build_notes

    def test_with_unknown_template_reports_available(self) -> None:
        result = build_state_machine(
            requirement="订单流程",
            industry_template="wrong-name",
        )
        ambiguity_ids = [a.id for a in result.ambiguities]
        assert "AMB-TEMPLATE-NOT-FOUND" in ambiguity_ids
        not_found = next(a for a in result.ambiguities if a.id == "AMB-TEMPLATE-NOT-FOUND")
        for name in AVAILABLE_TEMPLATES:
            assert name in not_found.question

    def test_plain_requirement_returns_skeleton_with_guidance(self) -> None:
        result = build_state_machine(
            requirement="订单有 待支付/已支付/已取消 三个状态",
            object_hint="Order",
        )
        assert result.state_machine.meta.object == "Order"
        assert result.state_machine.meta.confidence == "low"
        assert result.state_machine.states == []
        assert result.extracted_objects == ["Order"]
        # 诚实契约：不内置 LLM，指引调用方建模
        assert result.ambiguities[0].id == "AMB-001"
        assert "不内置 LLM" in result.ambiguities[0].question
        assert "validate_state_machine" in result.build_notes

    def test_plain_requirement_without_object_hint(self) -> None:
        result = build_state_machine(requirement="某个审批流程")
        assert result.state_machine.meta.object == "Unknown"
        assert result.extracted_objects == []
