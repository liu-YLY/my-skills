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
