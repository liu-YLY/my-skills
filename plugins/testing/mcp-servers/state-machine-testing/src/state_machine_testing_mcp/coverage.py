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
    # A reference narrows candidates; it never bypasses structural matching.
    covered_transitions: set[int] = set()
    covered_forbidden: set[int] = set()
    unmatched: list[str] = []
    for scenario in scenarios.scenarios:
        matches: list[int] = []
        if scenario.risk_type == "legal_transition":
            for index, transition in enumerate(state_machine.transitions):
                if scenario.transition_id and scenario.transition_id != transition.id:
                    continue
                if (scenario.current_state == transition.from_state
                        and scenario.trigger_event == transition.event
                        and scenario.expected_target_state == transition.to_state
                        and set(scenario.guard_conditions) == set(transition.guards)):
                    matches.append(index)
            if len(matches) == 1:
                covered_transitions.add(matches[0])
            else:
                unmatched.append(scenario.id)
        elif scenario.risk_type == "illegal_transition":
            for index, forbidden in enumerate(state_machine.forbidden):
                if scenario.forbidden_id and scenario.forbidden_id != forbidden.id:
                    continue
                target = scenario.attempted_target_state
                target_matches = target == forbidden.to_state and target != "*"
                if forbidden.to_state == "*" and target in {s.name for s in state_machine.states}:
                    target_matches = True
                if (scenario.current_state == forbidden.from_state
                        and scenario.expected_target_state == forbidden.from_state
                        and target is not None and target_matches):
                    matches.append(index)
            if len(matches) == 1:
                covered_forbidden.add(matches[0])
            else:
                unmatched.append(scenario.id)

    total_transitions = len(state_machine.transitions)
    transition_coverage = len(covered_transitions) / total_transitions if total_transitions else 0.0
    total_forbidden = len(state_machine.forbidden)
    forbidden_coverage = len(covered_forbidden) / total_forbidden if total_forbidden else 0.0
    uncovered_transitions = [
        f"{t.id}: {t.from_state}→{t.to_state}:{t.event} guards={t.guards}"
        for index, t in enumerate(state_machine.transitions) if index not in covered_transitions
    ]

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
        unmatched_scenarios=unmatched,
    )
