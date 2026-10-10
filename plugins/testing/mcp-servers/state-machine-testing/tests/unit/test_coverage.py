"""check_coverage 单元测试。"""

from __future__ import annotations

import json
from pathlib import Path

from state_machine_testing_mcp.coverage import check_coverage
from state_machine_testing_mcp.generators import generate_scenarios
from state_machine_testing_mcp.schemas import StateMachine

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_order_refund() -> StateMachine:
    fixture = FIXTURES_DIR / "order_refund_state_machine.json"
    return StateMachine.model_validate(json.loads(fixture.read_text(encoding="utf-8")))


def test_coverage_report_fields() -> None:
    """覆盖度报告应包含所有必填字段。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    report = check_coverage(sm, scenarios)
    assert 0.0 <= report.transition_coverage <= 1.0
    assert 0.0 <= report.forbidden_coverage <= 1.0
    assert "legal_transition" in report.scenario_type_coverage
    assert "需求明确" in report.evidence_distribution


def test_transition_coverage_full() -> None:
    """generate_scenarios 默认生成 legal_transition，覆盖率应为 1.0。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    report = check_coverage(sm, scenarios)
    assert report.transition_coverage == 1.0


def test_missing_scenario_types_empty_by_default() -> None:
    """默认生成 10 类，missing_scenario_types 应为空（或仅缺少无触发条件的类）。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    report = check_coverage(sm, scenarios)
    # 订单退款 fixture 涉及回调/异步/超时/管理员，多数类型应能生成
    # access_control 可能因为 fixture 没有显式管理员事件而为空
    assert "legal_transition" not in report.missing_scenario_types
    assert "failure_recovery" not in report.missing_scenario_types


def test_uncovered_transitions_empty_when_legal_generated() -> None:
    """生成 legal_transition 后，uncovered_transitions 应为空。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    report = check_coverage(sm, scenarios)
    assert report.uncovered_transitions == []



def test_applicability_separates_missing_excluded_and_unknown():
    from state_machine_testing_mcp.schemas import ScenarioList
    sm = _load_order_refund()
    data = sm.model_dump(by_alias=True)
    data["scenario_applicability"] = {
        "message_reorder": {"status": "not_applicable", "reason": "同步无消息", "source": "PRD §1"},
        "idempotency": {"status": "applicable", "reason": "回调会重复", "source": "PRD §2"}}
    sm = StateMachine.model_validate(data)
    report = check_coverage(sm, ScenarioList(scenarios=[]))
    assert "legal_transition" in report.applicable_missing_scenario_types
    assert "idempotency" in report.applicable_missing_scenario_types
    assert "message_reorder" in report.not_applicable_scenario_types
    assert "access_control" in report.unknown_scenario_types
    assert "access_control" not in report.applicable_missing_scenario_types
    assert report.scenario_type_coverage["access_control"] == 0
    assert "access_control" in report.missing_scenario_types


def test_markdown_keeps_applicability_unknown_visible():
    from state_machine_testing_mcp.exporters import export_to_markdown
    sm = _load_order_refund()
    output = export_to_markdown(sm, generate_scenarios(sm))
    assert "适用性" in output
    assert "access_control | unknown" in output



def test_applicable_missing_ignores_wrong_structural_match_and_pending_candidates():
    from state_machine_testing_mcp.schemas import ScenarioList
    data = _load_order_refund().model_dump(by_alias=True)
    data["scenario_applicability"] = {"idempotency": {"status": "applicable",
        "reason": "需求要求幂等", "source": "PRD §2"}}
    sm = StateMachine.model_validate(data)
    generated = generate_scenarios(sm, ["legal_transition", "idempotency"])
    raw = generated.model_dump(mode="json")
    for scenario in raw["scenarios"]:
        if scenario["risk_type"] == "legal_transition":
            scenario["guard_conditions"] = ["不存在的守卫"]
        else:
            scenario["expected_target_state"] = "待确认"
            scenario["expected_target_state_reason"] = "重复事件结果规则未明确"
            scenario["evidence_type"] = "待确认"
    report = check_coverage(sm, ScenarioList.model_validate(raw))
    assert report.scenario_type_coverage["legal_transition"] > 0
    assert report.scenario_type_coverage["idempotency"] > 0
    assert "legal_transition" in report.applicable_missing_scenario_types
    assert "idempotency" in report.applicable_missing_scenario_types
