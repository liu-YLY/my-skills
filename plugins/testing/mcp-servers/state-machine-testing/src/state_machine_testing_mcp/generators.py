"""generate_scenarios 实现：基于状态机穷举 10 类场景。

10 类场景穷举规则详见 state-machine-test-engineer/knowledge/scenario-types.md。
"""

from __future__ import annotations

from .schemas import (
    EvidenceType,
    Scenario,
    ScenarioList,
    ScenarioApplicability,
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


def assess_applicability(sm: StateMachine) -> dict[str, ScenarioApplicability]:
    structural = {
        "legal_transition": (bool(sm.transitions), "transitions[]"),
        "illegal_transition": (bool(sm.forbidden), "forbidden[]"),
        "guard_violation": (any(t.guards for t in sm.transitions), "transitions[].guards"),
        "data_consistency": (any(t.side_effects for t in sm.transitions), "transitions[].side_effects"),
    }
    result = {}
    for risk in ALL_SCENARIO_TYPES:
        if risk in sm.scenario_applicability:
            result[risk] = sm.scenario_applicability[risk]
        elif risk in structural:
            present, field = structural[risk]
            result[risk] = ScenarioApplicability(
                status="applicable" if present else "not_applicable",
                reason="仅模型层结构判断，不证明业务需求完整性",
                source=f"状态机 {field}", evidence_type=EvidenceType.INFERRED)
        else:
            result[risk] = ScenarioApplicability(
                status="unknown", reason="模型未提供该类业务能力和适用范围依据",
                source="状态机缺少 scenario_applicability 明确声明",
                missing_information=[f"{risk} 的能力、范围及规则来源"])
    return result


def _explicitly_applicable(sm: StateMachine, risk: str) -> bool:
    item = sm.scenario_applicability.get(risk)
    return item is not None and item.status == "applicable"


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
                precondition=f"{t.from_state} 状态" + ("，" + "；".join(t.guards) if t.guards else ""),
                transition_id=t.id,
                guard_conditions=list(t.guards),
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
    for f in sm.forbidden:
        targets = [state.name for state in sm.states] if f.to_state == "*" else [f.to_state]
        for target in targets:
            scenarios.append(
                Scenario(
                    id=f"SM-{base + len(scenarios) + 1:03d}",
                    title=f"{f.from_state} 尝试转到 {target} 应被拒绝",
                    current_state=f.from_state,
                    trigger_event=f"尝试进入 {target}",
                    precondition=f"{f.from_state} 状态",
                    expected_target_state=f.from_state,
                    forbidden_states=[target],
                    risk_type="illegal_transition",
                    forbidden_id=f.id,
                    attempted_target_state=target,
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
        siblings = [other for other in sm.transitions
                    if other is not t and other.from_state == t.from_state and other.event == t.event]
        for guard in t.guards:
            idx += 1
            scenarios.append(
                Scenario(
                    id=f"SM-{base + idx:03d}",
                    title=f"{t.from_state} 收到 {t.event} 但 guard '{guard}' 不满足时该转换不执行",
                    current_state=t.from_state,
                    trigger_event=t.event,
                    precondition=f"{t.from_state} 状态，{guard} 不满足" + "".join(
                        f"，{other} 满足" for other in t.guards if other != guard),
                    transition_id=t.id,
                    guard_conditions=list(t.guards),
                    violated_guard=guard,
                    expected_target_state="待确认" if siblings else t.from_state,
                    expected_target_state_reason=(
                        "同源同事件存在其他分支；字符串守卫不能确定输入匹配的目标" if siblings else None),
                    forbidden_states=[],
                    risk_type="guard_violation",
                    related_objects=[],
                    evidence_type=EvidenceType.PENDING if siblings else EvidenceType.INFERRED,
                    source=f"状态机 transitions 中 guard '{guard}' 的反向；仅模型结构推断",
                    notes="其余守卫满足的输入联合可满足性未验证；仅证明该转换不执行",
                )
            )
    return scenarios


def _generate_idempotency(sm: StateMachine) -> list[Scenario]:
    """生成 idempotency 场景。"""
    scenarios: list[Scenario] = []
    base = len(sm.transitions) + len(sm.forbidden)
    idx = 0
    for t in sm.transitions:
        if not _is_external_callback(t.event) and not _explicitly_applicable(sm, "idempotency"):
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
    """生成 concurrency 场景。

    对任意一对「不同事件」的 transition 组合生成并发场景，而不是仅限
    「用户事件 + 回调事件」。事件无 actor 信息时，默认来自不同触发源
    （用户/回调/定时器），避免漏判。
    """
    scenarios: list[Scenario] = []
    base = len(sm.transitions) + len(sm.forbidden) + 100
    paires: list[tuple] = []
    for i, t1 in enumerate(sm.transitions):
        for t2 in sm.transitions[i + 1:]:
            if t1.from_state == t2.from_state and t1.event != t2.event:
                paires.append((t1, t2))
    for t1, t2 in paires[:20]:  # 限制数量，避免组合爆炸
        scenarios.append(
            Scenario(
                id=f"SM-{base + len(scenarios) + 1:03d}",
                title=f"{t1.event} 与 {t2.event} 并发时最终状态正确",
                current_state=t1.from_state,
                trigger_event=f"{t1.event} + {t2.event}（并发）",
                precondition=f"{t1.from_state} 状态，{t1.event} 与 {t2.event} 同时到达（触发源与同时成立条件待核实）",
                expected_target_state="待确认",
                expected_target_state_reason="PRD 未说明两个事件并发的目标态",
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
        if not _is_async_event(t.event) and not _explicitly_applicable(sm, "message_reorder"):
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
                expected_target_state_reason="PRD 通常未说明消息乱序后的目标态",
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
    """权限能力与拒绝规则未知时只生成待确认候选。"""
    return [Scenario(
        id=f"SM-{501 + index:03d}",
        title=f"{t.event} 的角色与权限边界需确认",
        current_state=t.from_state,
        trigger_event=f"{t.event}（权限边界）",
        precondition=f"{t.from_state} 状态，操作者与权限矩阵待确认",
        expected_target_state="待确认",
        expected_target_state_reason="模型未提供角色、授权矩阵及拒绝行为依据",
        risk_type="access_control", evidence_type=EvidenceType.PENDING,
        source="权限规则缺口候选；不证明存在越权或拒绝规则",
    ) for index, t in enumerate(sm.transitions[:1])]


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
                expected_target_state_reason="PRD 通常未说明执行失败后的恢复状态",
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
    applicability = assess_applicability(state_machine)
    types_to_generate = [risk for risk in (scenario_types or ALL_SCENARIO_TYPES)
                         if applicability[risk].status != "not_applicable"]

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

    for scenario in all_scenarios:
        item = applicability[scenario.risk_type]
        if item.status == "unknown":
            scenario.expected_target_state = "待确认"
            scenario.expected_target_state_reason = item.reason
            scenario.evidence_type = EvidenceType.PENDING
            scenario.forbidden_states = []
            scenario.notes += "；适用性未知，属于待确认候选，不证明业务规则"

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
        scenario_applicability=applicability,
        pending_confirmation=pending,
    )
