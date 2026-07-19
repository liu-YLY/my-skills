"""check_coverage 实现：覆盖度检查。"""

from __future__ import annotations

from .generators import ALL_SCENARIO_TYPES
from .schemas import CoverageReport, ScenarioList, StateMachine


def check_coverage(state_machine: StateMachine, scenarios: ScenarioList) -> CoverageReport:
    """覆盖度检查。

    Args:
        state_machine: 状态机模型
        scenarios: 场景清单

    Returns:
        CoverageReport: 覆盖度报告
    """
    # 1. transition_coverage: 每条转换至少有 1 个合法场景
    legal_scenarios = [s for s in scenarios.scenarios if s.risk_type == "legal_transition"]
    covered_transitions: set[str] = set()
    for s in legal_scenarios:
        # 通过 current_state + trigger_event 匹配 transition
        for t in state_machine.transitions:
            if t.from_state == s.current_state and t.event == s.trigger_event:
                covered_transitions.add(f"{t.from_state}→{t.to_state}:{t.event}")
                break

    total_transitions = len(state_machine.transitions)
    transition_coverage = (
        len(covered_transitions) / total_transitions if total_transitions > 0 else 0.0
    )

    uncovered_transitions = [
        f"{t.from_state}→{t.to_state}:{t.event}"
        for t in state_machine.transitions
        if f"{t.from_state}→{t.to_state}:{t.event}" not in covered_transitions
    ]

    # 2. forbidden_coverage: 每条禁止转换至少有 1 个非法场景
    illegal_scenarios = [s for s in scenarios.scenarios if s.risk_type == "illegal_transition"]
    covered_forbidden: set[str] = set()
    for s in illegal_scenarios:
        for f in state_machine.forbidden:
            target = "任意状态" if f.to_state == "*" else f.to_state
            if f.from_state == s.current_state and (
                f.to_state == "*" or target in s.trigger_event
            ):
                covered_forbidden.add(f"{f.from_state}→{target}:{f.reason}")
                break

    total_forbidden = len(state_machine.forbidden)
    forbidden_coverage = (
        len(covered_forbidden) / total_forbidden if total_forbidden > 0 else 0.0
    )

    # 3. scenario_type_coverage: 10 类场景类型分布
    type_coverage: dict[str, int] = {t: 0 for t in ALL_SCENARIO_TYPES}
    for s in scenarios.scenarios:
        type_coverage[s.risk_type] = type_coverage.get(s.risk_type, 0) + 1

    missing_scenario_types = [t for t, count in type_coverage.items() if count == 0]

    # 4. evidence_distribution: 依据类型分布
    evidence_dist: dict[str, int] = {"需求明确": 0, "合理推理": 0, "待确认": 0}
    for s in scenarios.scenarios:
        evidence_dist[s.evidence_type.value] = (
            evidence_dist.get(s.evidence_type.value, 0) + 1
        )

    return CoverageReport(
        transition_coverage=round(transition_coverage, 3),
        forbidden_coverage=round(forbidden_coverage, 3),
        scenario_type_coverage=type_coverage,
        evidence_distribution=evidence_dist,
        uncovered_transitions=uncovered_transitions,
        missing_scenario_types=missing_scenario_types,
    )
