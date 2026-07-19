"""pydantic Schema 单元测试。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from state_machine_testing_mcp.schemas import (
    EvidenceType,
    ForbiddenTransition,
    Scenario,
    State,
    StateMachine,
    StateMachineMeta,
    Transition,
)


def _make_minimal_state_machine() -> StateMachine:
    return StateMachine(
        meta=StateMachineMeta(object="Test"),
        states=[
            State(name="待支付", meaning="订单已创建", is_initial=True),
            State(name="已支付", meaning="订单已支付", is_terminal=True),
        ],
        transitions=[
            Transition(
                from_state="待支付",
                to_state="已支付",
                event="支付成功回调",
                evidence_type=EvidenceType.EXPLICIT,
            )
        ],
    )


def test_state_machine_minimal_valid() -> None:
    """最小合法状态机应通过校验。"""
    sm = _make_minimal_state_machine()
    assert sm.meta.object == "Test"
    assert len(sm.states) == 2
    assert len(sm.transitions) == 1


def test_transition_evidence_type_required() -> None:
    """Transition 的 evidence_type 必填，缺失应抛 ValidationError。"""
    with pytest.raises(ValidationError):
        Transition(from_state="A", to_state="B", event="event")  # type: ignore[call-arg]


def test_forbidden_evidence_type_required() -> None:
    """ForbiddenTransition 的 evidence_type 必填。"""
    with pytest.raises(ValidationError):
        ForbiddenTransition(from_state="A", to_state="*", reason="终态吸收")  # type: ignore[call-arg]


def test_scenario_evidence_type_required() -> None:
    """Scenario 的 evidence_type 必填。"""
    with pytest.raises(ValidationError):
        Scenario(  # type: ignore[call-arg]
            id="SM-001",
            title="test",
            current_state="A",
            trigger_event="event",
            precondition="pre",
            expected_target_state="B",
            risk_type="legal_transition",
        )


def test_evidence_type_enum_values() -> None:
    """EvidenceType 枚举值正确。"""
    assert EvidenceType.EXPLICIT.value == "需求明确"
    assert EvidenceType.INFERRED.value == "合理推理"
    assert EvidenceType.PENDING.value == "待确认"


def test_state_defaults() -> None:
    """State 字段默认值正确。"""
    s = State(name="待支付", meaning="订单已创建")
    assert s.is_terminal is False
    assert s.is_initial is False
    assert s.entry_events == []
    assert s.invariants == []


def test_transition_alias_from_to() -> None:
    """Transition 支持 from/to 别名（避免 Python 关键字冲突）。"""
    t = Transition(
        **{
            "from": "待支付",
            "to": "已支付",
            "event": "支付成功回调",
            "evidence_type": EvidenceType.EXPLICIT,
        }
    )
    assert t.from_state == "待支付"
    assert t.to_state == "已支付"


def test_state_machine_empty_states_rejected() -> None:
    """空 states 列表应允许（pydantic 不强制非空），但语义上由 validator 检查。"""
    sm = StateMachine(meta=StateMachineMeta(object="Test"), states=[], transitions=[])
    assert len(sm.states) == 0  # 由 validator 而非 schema 拒绝
