"""generate_scenarios 实现：基于状态机穷举 10 类场景。

10 类场景穷举规则详见 state-machine-test-engineer/knowledge/scenario-types.md。
"""

from __future__ import annotations

from .schemas import (
    EvidenceType,
    Scenario,
    ScenarioList,
    StateMachine,
)

# 10 类场景类型常量
ALL_SCENARIO_TYPES = [
    "legal_transition",
    "illegal_transition",
    "guard_violation",
    "idempotency",
    "concurrency",
    "message_reorder",
    "timeout_retry",
    "data_consistency",
    "access_control",
    "failure_recovery",
]


def _next_scenario_id(existing: list[str]) -> str:
    """生成下一个场景 ID（SM-001 起编）。"""
    max_num = 0
    for sid in existing:
        if sid.startswith("SM-"):
            try:
                num = int(sid[3:])
                max_num = max(max_num, num)
            except ValueError:
                pass
    return f"SM-{max_num + 1:03d}"


def _is_external_callback(event: str) -> bool:
    """判断事件是否涉及外部回调（用于 idempotency 场景生成条件）。"""
    keywords = ["回调", "通知", "消息", "callback", "notify", "message"]
    return any(kw in event.lower() for kw in keywords)


def _is_async_event(event: str) -> bool:
    """判断事件是否涉及异步消息（用于 message_reorder 场景生成条件）。"""
    keywords = ["回调", "消息", "异步", "callback", "async", "message"]
    return any(kw in event.lower() for kw in keywords)


def _is_timeout_event(event: str) -> bool:
    """判断事件是否涉及超时/重试（用于 timeout_retry 场景生成条件）。"""
    keywords = ["超时", "重试", "timeout", "retry", "定时"]
    return any(kw in event.lower() for kw in keywords)


def _generate_legal_transitions(sm: StateMachine) -> list[Scenario]:
    """生成 legal_transition 场景。"""
    scenarios: list[Scenario] = []
    for i, t in enumerate(sm.transitions, 1):
        scenarios.append(
            Scenario(
                id=f"SM-{i:03d}",
                title=f"{t.from_state} 收到 {t.event} 后转为 {t.to_state}",
                current_state=t.from_state,
                trigger_event=t.event,
                precondition=f"{t.from_state} 状态，{t.event}",
                expected_target_state=t.to_state,
                forbidden_states=[],
                risk_type="legal_transition",
                related_objects=[],
                evidence_type=t.evidence_type,
                source=t.source or "状态机 transitions",
                notes="验证转换后副作用已执行",
            )
        )
    return scenarios


def _generate_illegal_transitions(sm: StateMachine) -> list[Scenario]:
    """生成 illegal_transition 场景。"""
    scenarios: list[Scenario] = []
    base = len(sm.transitions)
    for i, f in enumerate(sm.forbidden, 1):
        target = "任意状态" if f.to_state == "*" else f.to_state
        scenarios.append(
            Scenario(
                id=f"SM-{base + i:03d}",
                title=f"{f.from_state} 尝试转到 {target} 应被拒绝",
                current_state=f.from_state,
                trigger_event=f"尝试进入 {target}",
                precondition=f"{f.from_state} 状态",
                expected_target_state=f.from_state,
                forbidden_states=[target] if f.to_state != "*" else [],
                risk_type="illegal_transition",
                related_objects=[],
                evidence_type=f.evidence_type,
                source=f"状态机 forbidden 规则: {f.reason}",
                notes=f"reason: {f.reason}",
            )
        )
    return scenarios


def _generate_guard_violations(sm: StateMachine) -> list[Scenario]:
    """生成 guard_violation 场景。"""
    scenarios: list[Scenario] = []
    base = len(sm.transitions) + len(sm.forbidden)
    idx = 0
    for t in sm.transitions:
        if not t.guards:
            continue
        for guard in t.guards:
            idx += 1
            scenarios.append(
                Scenario(
                    id=f"SM-{base + idx:03d}",
                    title=f"{t.from_state} 收到 {t.event} 但 guard '{guard}' 不满足应被拒绝",
                    current_state=t.from_state,
                    trigger_event=t.event,
                    precondition=f"{t.from_state} 状态，{guard} 不满足",
                    expected_target_state=t.from_state,
                    forbidden_states=[t.to_state],
                    risk_type="guard_violation",
                    related_objects=[],
                    evidence_type=EvidenceType.INFERRED,
                    source=f"状态机 transitions 中 guard '{guard}' 的反向",
                )
            )
    return scenarios


def _generate_idempotency(sm: StateMachine) -> list[Scenario]:
    """生成 idempotency 场景。"""
    scenarios: list[Scenario] = []
    base = len(sm.transitions) + len(sm.forbidden)
    idx = 0
    for t in sm.transitions:
        if not _is_external_callback(t.event):
            continue
        idx += 1
        scenarios.append(
            Scenario(
                id=f"SM-{base + idx:03d}",
                title=f"{t.event} 重复到达不应重复触发 {t.from_state} → {t.to_state}",
                current_state=t.to_state,
                trigger_event=f"{t.event}（重复）",
                precondition=f"已是 {t.to_state} 状态，收到第二次 {t.event}",
                expected_target_state=t.to_state,
                forbidden_states=[],
                risk_type="idempotency",
                related_objects=[],
                evidence_type=EvidenceType.INFERRED,
                source="业务常识（外部回调可能重复到达）",
            )
        )
    return scenarios


def _generate_concurrency(sm: StateMachine) -> list[Scenario]:
    """生成 concurrency 场景。"""
    scenarios: list[Scenario] = []
    base = len(sm.transitions) + len(sm.forbidden) + 100
    idx = 0
    # 找涉及用户操作 + 系统回调的 transition 对
    user_events = [t for t in sm.transitions if "用户" in t.event]
    system_events = [t for t in sm.transitions if _is_external_callback(t.event)]
    for t in user_events + system_events:
        idx += 1
        scenarios.append(
            Scenario(
                id=f"SM-{base + idx:03d}",
                title=f"{t.event} 与其他事件并发时 {t.from_state} 最终状态正确",
                current_state=t.from_state,
                trigger_event=f"{t.event} + 其他事件（并发）",
                precondition=f"{t.from_state} 状态，{t.event} 与其他事件同时到达",
                expected_target_state="待确认",
                forbidden_states=[],
                risk_type="concurrency",
                related_objects=[],
                evidence_type=EvidenceType.PENDING,
                source="PRD 通常未说明并发处理规则",
            )
        )
    return scenarios


def _generate_message_reorder(sm: StateMachine) -> list[Scenario]:
    """生成 message_reorder 场景。"""
    scenarios: list[Scenario] = []
    base = 200
    idx = 0
    for t in sm.transitions:
        if not _is_async_event(t.event):
            continue
        idx += 1
        scenarios.append(
            Scenario(
                id=f"SM-{base + idx:03d}",
                title=f"{t.event} 乱序到达时 {t.from_state} 状态正确",
                current_state=t.from_state,
                trigger_event=f"{t.event}（乱序）",
                precondition=f"{t.from_state} 状态，{t.event} 消息乱序",
                expected_target_state="待确认",
                forbidden_states=[],
                risk_type="message_reorder",
                related_objects=[],
                evidence_type=EvidenceType.PENDING,
                source="PRD 通常未说明消息乱序处理规则",
            )
        )
    return scenarios


def _generate_timeout_retry(sm: StateMachine) -> list[Scenario]:
    """生成 timeout_retry 场景。"""
    scenarios: list[Scenario] = []
    base = 300
    idx = 0
    for t in sm.transitions:
        if not _is_timeout_event(t.event) and not any(
            "超时" in g or "retry" in g.lower() for g in t.guards
        ):
            continue
        idx += 1
        scenarios.append(
            Scenario(
                id=f"SM-{base + idx:03d}",
                title=f"{t.from_state} 超时后 {t.event} 的状态正确",
                current_state=t.from_state,
                trigger_event=f"{t.event}（超时触发）",
                precondition=f"{t.from_state} 状态，超时后触发",
                expected_target_state=t.to_state,
                forbidden_states=[],
                risk_type="timeout_retry",
                related_objects=[],
                evidence_type=EvidenceType.INFERRED,
                source="业务常识",
            )
        )
    return scenarios


def _generate_data_consistency(sm: StateMachine) -> list[Scenario]:
    """生成 data_consistency 场景。"""
    scenarios: list[Scenario] = []
    base = 400
    idx = 0
    for t in sm.transitions:
        if not t.side_effects:
            continue
        idx += 1
        scenarios.append(
            Scenario(
                id=f"SM-{base + idx:03d}",
                title=f"{t.from_state} → {t.to_state} 后关联对象数据一致",
                current_state=t.from_state,
                trigger_event=t.event,
                precondition=f"{t.from_state} 状态，{t.event}",
                expected_target_state=t.to_state,
                forbidden_states=["关联对象与主对象状态不一致"],
                risk_type="data_consistency",
                related_objects=t.side_effects,
                evidence_type=EvidenceType.INFERRED,
                source="状态机 transitions 中 side_effects 的验证",
            )
        )
    return scenarios


def _generate_access_control(sm: StateMachine) -> list[Scenario]:
    """生成 access_control 场景。"""
    scenarios: list[Scenario] = []
    base = 500
    idx = 0
    # 涉及管理员/审批人/特定角色的 transition
    for t in sm.transitions:
        if not any(kw in t.event for kw in ["管理员", "审批人", "客服", "admin"]):
            continue
        idx += 1
        scenarios.append(
            Scenario(
                id=f"SM-{base + idx:03d}",
                title=f"非授权角色尝试 {t.event} 应被拒绝",
                current_state=t.from_state,
                trigger_event=f"{t.event}（非授权角色）",
                precondition=f"{t.from_state} 状态，操作者为非授权角色",
                expected_target_state=t.from_state,
                forbidden_states=[t.to_state],
                risk_type="access_control",
                related_objects=[],
                evidence_type=EvidenceType.PENDING,
                source="PRD 通常未说明权限矩阵",
            )
        )
    return scenarios


def _generate_failure_recovery(sm: StateMachine) -> list[Scenario]:
    """生成 failure_recovery 场景。"""
    scenarios: list[Scenario] = []
    base = 600
    for i, t in enumerate(sm.transitions, 1):
        scenarios.append(
            Scenario(
                id=f"SM-{base + i:03d}",
                title=f"{t.from_state} → {t.to_state} 执行失败后状态恢复路径",
                current_state=t.from_state,
                trigger_event=f"{t.event}（执行失败）",
                precondition=f"{t.from_state} 状态，{t.event} 执行失败",
                expected_target_state="待确认",
                forbidden_states=[],
                risk_type="failure_recovery",
                related_objects=t.side_effects,
                evidence_type=EvidenceType.PENDING,
                source="PRD 通常未说明失败后状态",
            )
        )
    return scenarios


def generate_scenarios(
    state_machine: StateMachine,
    scenario_types: list[str] | None = None,
    evidence_filter: str | None = None,
) -> ScenarioList:
    """基于状态机穷举 10 类场景。

    Args:
        state_machine: 状态机模型
        scenario_types: 指定生成的场景类型，None 表示全部 10 类
        evidence_filter: 按依据类型过滤（需求明确/合理推理/待确认）

    Returns:
        ScenarioList: 场景清单
    """
    types_to_generate = scenario_types or ALL_SCENARIO_TYPES

    all_scenarios: list[Scenario] = []

    if "legal_transition" in types_to_generate:
        all_scenarios.extend(_generate_legal_transitions(state_machine))
    if "illegal_transition" in types_to_generate:
        all_scenarios.extend(_generate_illegal_transitions(state_machine))
    if "guard_violation" in types_to_generate:
        all_scenarios.extend(_generate_guard_violations(state_machine))
    if "idempotency" in types_to_generate:
        all_scenarios.extend(_generate_idempotency(state_machine))
    if "concurrency" in types_to_generate:
        all_scenarios.extend(_generate_concurrency(state_machine))
    if "message_reorder" in types_to_generate:
        all_scenarios.extend(_generate_message_reorder(state_machine))
    if "timeout_retry" in types_to_generate:
        all_scenarios.extend(_generate_timeout_retry(state_machine))
    if "data_consistency" in types_to_generate:
        all_scenarios.extend(_generate_data_consistency(state_machine))
    if "access_control" in types_to_generate:
        all_scenarios.extend(_generate_access_control(state_machine))
    if "failure_recovery" in types_to_generate:
        all_scenarios.extend(_generate_failure_recovery(state_machine))

    # 按依据类型过滤
    if evidence_filter:
        all_scenarios = [s for s in all_scenarios if s.evidence_type.value == evidence_filter]

    # 重新编号（避免 ID 冲突）
    for i, s in enumerate(all_scenarios, 1):
        s.id = f"SM-{i:03d}"

    # 覆盖度统计
    type_coverage: dict[str, int] = {t: 0 for t in ALL_SCENARIO_TYPES}
    evidence_dist: dict[str, int] = {"需求明确": 0, "合理推理": 0, "待确认": 0}
    pending: list[Scenario] = []
    for s in all_scenarios:
        type_coverage[s.risk_type] = type_coverage.get(s.risk_type, 0) + 1
        evidence_dist[s.evidence_type.value] = evidence_dist.get(s.evidence_type.value, 0) + 1
        if s.evidence_type == EvidenceType.PENDING:
            pending.append(s)

    return ScenarioList(
        scenarios=all_scenarios,
        coverage_summary=type_coverage,
        pending_confirmation=pending,
    )
