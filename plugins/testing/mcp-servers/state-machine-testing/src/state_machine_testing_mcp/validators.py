"""validate_state_machine 实现：9 项完整性检查。

与 skill 阶段 3 自检的 9 项完全对齐，详见
state-machine-test-engineer/knowledge/completeness-check.md。
"""

from __future__ import annotations

from .schemas import (
    CheckItem,
    Contradiction,
    EvidenceType,
    Gap,
    StateMachine,
    ValidationReport,
)


def _state_names(sm: StateMachine) -> set[str]:
    return {s.name for s in sm.states}


def _terminal_states(sm: StateMachine) -> set[str]:
    return {s.name for s in sm.states if s.is_terminal}


def _initial_states(sm: StateMachine) -> set[str]:
    return {s.name for s in sm.states if s.is_initial}


def _reachable_states(sm: StateMachine) -> set[str]:
    """从初始态出发的可达状态集（BFS）。"""
    initials = _initial_states(sm)
    if not initials:
        return set()

    reachable = set(initials)
    frontier = list(initials)
    while frontier:
        current = frontier.pop()
        for t in sm.transitions:
            if t.from_state == current and t.to_state not in reachable:
                reachable.add(t.to_state)
                frontier.append(t.to_state)
    return reachable


def check_c1_meaning(sm: StateMachine) -> CheckItem:
    """C1: 每个状态有明确含义。"""
    empty = [s.name for s in sm.states if not s.meaning or s.meaning in {"TODO", "待补充", "未知"}]
    if not empty:
        return CheckItem(check_id="C1", name="每个状态有明确含义", status="pass")
    return CheckItem(
        check_id="C1",
        name="每个状态有明确含义",
        status="fail",
        detail=f"状态缺少明确含义: {empty}",
    )


def check_c2_entry_condition(sm: StateMachine) -> tuple[CheckItem, list[Gap]]:
    """C2: 每个状态有进入条件（除初始态）。"""
    initials = _initial_states(sm)
    targets = {t.to_state for t in sm.transitions}
    unreachable: list[str] = []
    for s in sm.states:
        if s.name in initials:
            continue
        if s.name not in targets:
            unreachable.append(s.name)

    if not unreachable:
        return CheckItem(check_id="C2", name="每个状态有进入条件（除初始态）", status="pass"), []

    gaps = [
        Gap(
            id=f"GAP-C2-{i}",
            description=f"状态 '{name}' 无任何 transition 指向，疑似悬挂",
            related_state=name,
            related_check="C2",
        )
        for i, name in enumerate(unreachable, 1)
    ]
    return (
        CheckItem(
            check_id="C2",
            name="每个状态有进入条件（除初始态）",
            status="warn",
            detail=f"无进入条件的状态: {unreachable}",
        ),
        gaps,
    )


def check_c3_exit_path(sm: StateMachine) -> CheckItem:
    """C3: 每个非终态有退出路径。"""
    terminals = _terminal_states(sm)
    sources = {t.from_state for t in sm.transitions}
    deadlocked: list[str] = []
    for s in sm.states:
        if s.name in terminals:
            continue
        if s.name not in sources:
            deadlocked.append(s.name)

    if not deadlocked:
        return CheckItem(check_id="C3", name="每个非终态有退出路径", status="pass")
    return CheckItem(
        check_id="C3",
        name="每个非终态有退出路径",
        status="warn",
        detail=f"无退出路径的非终态: {deadlocked}",
    )


def check_c4_terminal_unchangeable(sm: StateMachine) -> tuple[CheckItem, list[Contradiction]]:
    """C4: 终态真的不可变化。"""
    terminals = _terminal_states(sm)
    violations: list[Contradiction] = []
    for t in sm.transitions:
        if t.from_state in terminals:
            violations.append(
                Contradiction(
                    id=f"CONTR-C4-{len(violations) + 1}",
                    description=(
                        f"终态 '{t.from_state}' 出现在 transition "
                        f"'{t.from_state} → {t.to_state}' 的 from 位置，与终态定义冲突"
                    ),
                    severity="high",
                    suggestion="检查是终态定义错误还是 transition 错误",
                    related_states=[t.from_state, t.to_state],
                    related_check="C4",
                )
            )

    if not violations:
        return CheckItem(check_id="C4", name="终态真的不可变化", status="pass"), []
    return (
        CheckItem(
            check_id="C4",
            name="终态真的不可变化",
            status="fail",
            detail=f"终态出现在 transition 的 from: {[v.related_states for v in violations]}",
        ),
        violations,
    )


def check_c5_forbidden_complete(sm: StateMachine) -> CheckItem:
    """C5: 禁止转换无遗漏（无法自动判定，默认 warn）。"""
    terminals = _terminal_states(sm)
    forbidden_froms = {f.from_state for f in sm.forbidden}
    missing_terminals = terminals - forbidden_froms

    suggestions: list[str] = []
    if missing_terminals:
        suggestions.append(f"终态未加终态吸收 forbidden: {missing_terminals}")

    return CheckItem(
        check_id="C5",
        name="禁止转换无遗漏",
        status="warn",
        detail="需人工审视终态吸收规则与已知不可逆操作是否完整",
    )


def check_c6_side_effects(sm: StateMachine) -> CheckItem:
    """C6: 状态变化有副作用定义。"""
    missing = [
        f"{t.from_state} → {t.to_state}（{t.event}）"
        for t in sm.transitions
        if not t.side_effects
    ]
    if not missing:
        return CheckItem(check_id="C6", name="状态变化有副作用定义", status="pass")
    return CheckItem(
        check_id="C6",
        name="状态变化有副作用定义",
        status="warn",
        detail=f"无 side_effects 的 transition: {missing}",
    )


def check_c7_evidence_type(sm: StateMachine) -> CheckItem:
    """C7: 依据类型已标注。

    pydantic Schema 已强制 evidence_type 必填，所以本项极少 fail。
    保留此检查作为兜底（防止手动绕过 Schema）。
    """
    missing_transitions = [
        f"{t.from_state} → {t.to_state}" for t in sm.transitions if not t.evidence_type
    ]
    missing_forbidden = [
        f"{f.from_state} → {f.to_state}" for f in sm.forbidden if not f.evidence_type
    ]
    if not missing_transitions and not missing_forbidden:
        return CheckItem(check_id="C7", name="依据类型已标注", status="pass")
    return CheckItem(
        check_id="C7",
        name="依据类型已标注",
        status="fail",
        detail=f"缺 evidence_type: transitions={missing_transitions}, forbidden={missing_forbidden}",
    )


def check_c8_no_unreachable(sm: StateMachine) -> tuple[CheckItem, list[Gap]]:
    """C8: 无悬挂状态。"""
    reachable = _reachable_states(sm)
    unreachable = _state_names(sm) - reachable

    if not unreachable:
        return CheckItem(check_id="C8", name="无悬挂状态", status="pass"), []

    gaps = [
        Gap(
            id=f"GAP-C8-{i}",
            description=f"状态 '{name}' 从初始态不可达",
            related_state=name,
            related_check="C8",
        )
        for i, name in enumerate(sorted(unreachable), 1)
    ]
    return (
        CheckItem(
            check_id="C8",
            name="无悬挂状态",
            status="warn",
            detail=f"不可达状态: {sorted(unreachable)}",
        ),
        gaps,
    )


def check_c9_no_deadlock(sm: StateMachine) -> CheckItem:
    """C9: 无死锁状态（非终态但无出边）。

    与 C3 检查同一件事，只是表述角度不同。
    """
    return check_c3_exit_path(sm).model_copy(update={"check_id": "C9", "name": "无死锁状态"})


def validate_state_machine(state_machine: StateMachine, strict: bool = True) -> ValidationReport:
    """执行 9 项完整性检查。"""
    checks: list[CheckItem] = []
    gaps: list[Gap] = []
    contradictions: list[Contradiction] = []
    suggestions: list[str] = []

    # C1
    checks.append(check_c1_meaning(state_machine))

    # C2
    c2, c2_gaps = check_c2_entry_condition(state_machine)
    checks.append(c2)
    gaps.extend(c2_gaps)

    # C3
    checks.append(check_c3_exit_path(state_machine))

    # C4
    c4, c4_contradictions = check_c4_terminal_unchangeable(state_machine)
    checks.append(c4)
    contradictions.extend(c4_contradictions)

    # C5
    c5 = check_c5_forbidden_complete(state_machine)
    checks.append(c5)
    suggestions.append("检查所有终态是否都加了'终态吸收'forbidden")
    suggestions.append("检查'已取消 → 已支付'等已知不可逆操作是否在 forbidden 中")

    # C6
    checks.append(check_c6_side_effects(state_machine))

    # C7
    checks.append(check_c7_evidence_type(state_machine))

    # C8
    c8, c8_gaps = check_c8_no_unreachable(state_machine)
    checks.append(c8)
    gaps.extend(c8_gaps)

    # C9
    checks.append(check_c9_no_deadlock(state_machine))

    # 计算 overall_status
    statuses = [c.status for c in checks]
    if "fail" in statuses:
        overall = "fail"
    elif "warn" in statuses:
        overall = "warn"
    else:
        overall = "pass"

    # strict 模式下 warn 也升级为 fail
    if strict and overall == "warn":
        overall = "fail"

    return ValidationReport(
        overall_status=overall,
        checks=checks,
        gaps=gaps,
        contradictions=contradictions,
        suggestions=suggestions,
    )
