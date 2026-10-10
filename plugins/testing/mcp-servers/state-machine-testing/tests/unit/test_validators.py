"""validate_state_machine 单元测试（9 项完整性检查）。"""

from __future__ import annotations

from state_machine_testing_mcp.schemas import (
    EvidenceType,
    State,
    StateMachine,
    StateMachineMeta,
    Transition,
)
from state_machine_testing_mcp.validators import validate_state_machine


def _make_minimal_state_machine(
    states: list[State] | None = None,
    transitions: list[Transition] | None = None,
) -> StateMachine:
    return StateMachine(
        meta=StateMachineMeta(object="Test"),
        states=states
        or [
            State(name="待支付", meaning="订单已创建", is_initial=True),
            State(name="已支付", meaning="订单已支付", is_terminal=True),
        ],
        transitions=transitions
        or [
            Transition(
                from_state="待支付",
                to_state="已支付",
                event="支付成功回调",
                evidence_type=EvidenceType.EXPLICIT,
            )
        ],
    )


def test_validate_minimal_pass() -> None:
    """最小合法状态机应 pass（C5 默认 warn，所以 overall 为 warn）。"""
    sm = _make_minimal_state_machine()
    report = validate_state_machine(sm, strict=False)
    assert report.overall_status == "warn"  # C5 默认 warn
    assert len(report.checks) == 10


def test_c1_empty_meaning_fails() -> None:
    """C1: meaning 为空应 fail。"""
    sm = _make_minimal_state_machine(
        states=[
            State(name="待支付", meaning="", is_initial=True),
            State(name="已支付", meaning="已支付", is_terminal=True),
        ]
    )
    report = validate_state_machine(sm, strict=False)
    c1 = next(c for c in report.checks if c.check_id == "C1")
    assert c1.status == "fail"


def test_c2_unreachable_state_warns() -> None:
    """C2: 非初始态无进入条件应 warn。"""
    sm = _make_minimal_state_machine(
        states=[
            State(name="待支付", meaning="初始", is_initial=True),
            State(name="孤立状态", meaning="无进入条件", is_terminal=True),
            State(name="已支付", meaning="已支付", is_terminal=True),
        ]
    )
    report = validate_state_machine(sm, strict=False)
    c2 = next(c for c in report.checks if c.check_id == "C2")
    assert c2.status == "warn"


def test_c3_deadlock_warns() -> None:
    """C3: 非终态无退出路径应 warn。"""
    sm = _make_minimal_state_machine(
        states=[
            State(name="待支付", meaning="初始", is_initial=True),
            State(name="死锁态", meaning="无出边", is_terminal=False),  # 无出边非终态
            State(name="已支付", meaning="已支付", is_terminal=True),
        ]
    )
    report = validate_state_machine(sm, strict=False)
    c3 = next(c for c in report.checks if c.check_id == "C3")
    assert c3.status == "warn"


def test_c4_terminal_with_outgoing_fails() -> None:
    """C4: 终态有出边应 fail。"""
    sm = StateMachine(
        meta=StateMachineMeta(object="Test"),
        states=[
            State(name="待支付", meaning="初始", is_initial=True),
            State(name="已支付", meaning="终态", is_terminal=True),
        ],
        transitions=[
            Transition(
                from_state="待支付",
                to_state="已支付",
                event="支付",
                evidence_type=EvidenceType.EXPLICIT,
            ),
            Transition(  # 终态 → 其他，违反 C4
                from_state="已支付",
                to_state="待支付",
                event="回退",
                evidence_type=EvidenceType.INFERRED,
            ),
        ],
    )
    report = validate_state_machine(sm, strict=False)
    c4 = next(c for c in report.checks if c.check_id == "C4")
    assert c4.status == "fail"
    assert len(report.contradictions) > 0


def test_c7_missing_evidence_type_fails() -> None:
    """C7: 缺 evidence_type 应 fail。

    pydantic Schema 已强制必填，所以本测试主要验证 validator 兜底逻辑。
    """
    sm = _make_minimal_state_machine()
    # 手动绕过 Schema 把 evidence_type 设为空
    sm.transitions[0].evidence_type = None  # type: ignore[assignment]
    report = validate_state_machine(sm, strict=False)
    c7 = next(c for c in report.checks if c.check_id == "C7")
    assert c7.status == "fail"


def test_strict_mode_warn_becomes_fail() -> None:
    """strict=True 时 warn 应升级为 fail。"""
    sm = _make_minimal_state_machine()
    report = validate_state_machine(sm, strict=True)
    # C5 默认 warn，strict 模式下 overall 应为 fail
    assert report.overall_status == "fail"


def test_c8_unreachable_from_initial() -> None:
    """C8: 从初始态不可达的状态应 warn。"""
    sm = StateMachine(
        meta=StateMachineMeta(object="Test"),
        states=[
            State(name="A", meaning="初始", is_initial=True),
            State(name="B", meaning="可达", is_terminal=True),
            State(name="C", meaning="不可达", is_terminal=True),  # 无任何路径到达
        ],
        transitions=[
            Transition(
                from_state="A", to_state="B", event="e1", evidence_type=EvidenceType.EXPLICIT
            ),
        ],
    )
    report = validate_state_machine(sm, strict=False)
    c8 = next(c for c in report.checks if c.check_id == "C8")
    assert c8.status == "warn"
    assert any(g.related_state == "C" for g in report.gaps)


def test_order_refund_fixture_passes_validation() -> None:
    """订单退款 fixture 应通过校验（不含死锁/终态冲突）。"""
    import json
    from pathlib import Path

    fixture = Path(__file__).parent.parent / "fixtures" / "order_refund_state_machine.json"
    sm = StateMachine.model_validate(json.loads(fixture.read_text(encoding="utf-8")))
    report = validate_state_machine(sm, strict=False)
    # 不应有 fail 项
    assert all(c.status != "fail" for c in report.checks)


def _finite_cycle(exit_path=False, required=True):
    return StateMachine.model_validate({"meta": {"object": "审批"},
        "states": [{"name": "A", "meaning": "待审", "is_initial": True},
                   {"name": "B", "meaning": "复核"},
                   {"name": "Done", "meaning": "结束", "is_terminal": True}],
        "transitions": [{"from": f, "to": t, "event": f + t,
                         "side_effects": ["记录"], "evidence_type": "需求明确"}
                        for f, t in ([("A", "B"), ("B", "A")] + ([("B", "Done")] if exit_path else []))],
        "progress_requirement": {"required": required, "allowed_terminal_states": ["Done"],
                                 "source": "PRD §审批结束", "evidence_type": "需求明确"}})


def test_finite_cycle_without_exit_fails_and_with_exit_is_only_structural_pass():
    bad = validate_state_machine(_finite_cycle(), strict=False)
    item = next(c for c in bad.property_checks if c.check_id == "P-PROGRESS")
    assert item.status == "fail" and "A" in item.detail and "B" in item.detail
    good = validate_state_machine(_finite_cycle(True), strict=False)
    item = next(c for c in good.property_checks if c.check_id == "P-PROGRESS")
    assert item.status == "pass"
    assert "不证明时限内必达" in item.detail
    assert len(good.checks) == 10


def test_periodic_model_can_explicitly_exclude_termination_requirement():
    report = validate_state_machine(_finite_cycle(required=False), strict=False)
    assert next(c for c in report.property_checks if c.check_id == "P-PROGRESS").status == "not_applicable"


def test_safety_statement_is_preserved_without_claiming_a_proof():
    sm = _finite_cycle(True)
    data = sm.model_dump(by_alias=True)
    data["safety_properties"] = [{"id": "SAFE-PAY", "statement": "不重复扣款", "applies_to": ["A"],
                                 "source": "PRD §资金", "verification_method": "核对资金流水次数"}]
    report = validate_state_machine(StateMachine.model_validate(data), strict=False)
    item = next(c for c in report.property_checks if c.check_id == "SAFE-PAY")
    assert item.status == "not_checked" and "流水" in item.detail


def test_property_report_preserves_pending_basis_without_promoting_business_facts():
    report = validate_state_machine(_finite_cycle(True), strict=False)
    item = next(c for c in report.property_checks if c.check_id == "P-PROGRESS")
    assert item.evidence_type.value == "需求明确"
    sm = _finite_cycle(True)
    data = sm.model_dump(by_alias=True)
    data["progress_requirement"]["evidence_type"] = "待确认"
    report = validate_state_machine(StateMachine.model_validate(data), strict=False)
    assert next(c for c in report.property_checks if c.check_id == "P-PROGRESS").evidence_type.value == "待确认"


def test_progress_check_handles_a_long_model_without_recursion():
    size = 1500
    sm = StateMachine.model_validate({"meta": {"object": "长审批"},
        "states": [{"name": str(i), "meaning": "阶段", "is_initial": i == 0,
                    "is_terminal": i == size - 1} for i in range(size)],
        "transitions": [{"from": str(i), "to": str(i + 1), "event": "推进",
                         "side_effects": ["记录"], "evidence_type": "需求明确"} for i in range(size - 1)],
        "progress_requirement": {"required": True, "allowed_terminal_states": [str(size - 1)],
                                 "source": "模型基线", "evidence_type": "需求明确"}})
    report = validate_state_machine(sm, strict=False)
    assert next(c for c in report.property_checks if c.check_id == "P-PROGRESS").status == "pass"
