"""generate_scenarios 单元测试（10 类场景穷举）。"""

from __future__ import annotations

import json
from pathlib import Path

from state_machine_testing_mcp.generators import (
    ALL_SCENARIO_TYPES,
    generate_scenarios,
)
from state_machine_testing_mcp.schemas import StateMachine

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_order_refund() -> StateMachine:
    """加载订单退款 fixture。"""
    fixture = FIXTURES_DIR / "order_refund_state_machine.json"
    return StateMachine.model_validate(json.loads(fixture.read_text(encoding="utf-8")))


def test_generate_all_10_types() -> None:
    """默认应生成 10 类场景（部分类型可能为 0 条，但 type_coverage 应包含 10 类键）。"""
    sm = _load_order_refund()
    result = generate_scenarios(sm)
    assert set(result.coverage_summary.keys()) == set(ALL_SCENARIO_TYPES)


def test_legal_transitions_generated() -> None:
    """每条 transition 应生成 1 个 legal_transition 场景。"""
    sm = _load_order_refund()
    result = generate_scenarios(sm, scenario_types=["legal_transition"])
    assert len(result.scenarios) == len(sm.transitions)


def test_illegal_transitions_generated() -> None:
    """每条 forbidden 应生成 1 个 illegal_transition 场景。"""
    sm = _load_order_refund()
    result = generate_scenarios(sm, scenario_types=["illegal_transition"])
    assert len(result.scenarios) == len(sm.forbidden)


def test_failure_recovery_always_generated() -> None:
    """每条 transition 都应生成 failure_recovery 场景。"""
    sm = _load_order_refund()
    result = generate_scenarios(sm, scenario_types=["failure_recovery"])
    assert len(result.scenarios) == len(sm.transitions)
    assert all(s.risk_type == "failure_recovery" for s in result.scenarios)
    assert all(s.evidence_type.value == "待确认" for s in result.scenarios)


def test_idempotency_only_for_callbacks() -> None:
    """idempotency 仅对涉及外部回调的 transition 生成。"""
    sm = _load_order_refund()
    result = generate_scenarios(sm, scenario_types=["idempotency"])
    # 订单退款 fixture 中，"支付成功回调"/"退款成功回调"/"退款失败回调" 都涉及回调
    assert len(result.scenarios) > 0
    for s in result.scenarios:
        assert "回调" in s.trigger_event or "重复" in s.trigger_event


def test_evidence_filter() -> None:
    """evidence_filter 应按依据类型过滤。"""
    sm = _load_order_refund()
    result = generate_scenarios(sm, evidence_filter="待确认")
    for s in result.scenarios:
        assert s.evidence_type.value == "待确认"


def test_scenario_ids_unique() -> None:
    """场景 ID 应唯一且格式为 SM-{三位序号}。"""
    sm = _load_order_refund()
    result = generate_scenarios(sm)
    ids = [s.id for s in result.scenarios]
    assert len(ids) == len(set(ids))  # 无重复
    for sid in ids:
        assert sid.startswith("SM-")
        assert len(sid) == 6  # SM-XXX


def test_pending_confirmation_correct() -> None:
    """pending_confirmation 应包含所有 evidence_type=待确认 的场景。"""
    sm = _load_order_refund()
    result = generate_scenarios(sm)
    pending_ids = {s.id for s in result.pending_confirmation}
    for s in result.scenarios:
        if s.evidence_type.value == "待确认":
            assert s.id in pending_ids
