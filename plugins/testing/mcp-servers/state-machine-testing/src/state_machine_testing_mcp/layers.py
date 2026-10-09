"""覆盖分层只使用输入的基线、确认关联和实际执行证据。"""

from .schemas import CoverageContext, CoverageLayer


def _metric(baseline, covered, unassessed=()):
    if baseline is None:
        return CoverageLayer(status="not_assessed")
    items = set(baseline.items)
    return CoverageLayer(status="assessed" if items else "not_applicable",
                         numerator=len(items & set(covered)), denominator=len(items),
                         ratio=round(len(items & set(covered)) / len(items), 3) if items else None,
                         baseline_source=baseline.source, baseline_version=baseline.version,
                         unassessed_items=sorted(set(unassessed)))


def layered_coverage(sm, scenarios, context, covered_transitions, unmatched):
    context = context or CoverageContext()
    resolved = {s.stable_ref or s.id for s in scenarios.scenarios
                if s.id not in unmatched and s.evidence_type.value != "待确认"
                and s.expected_target_state in {state.name for state in sm.states}
                and (s.failure_semantics is None or (
                    s.failure_semantics.phase != "unknown" and s.failure_semantics.evidence_type.value != "待确认"))}
    requirements = {link.item_id for link in context.requirement_links
                    if link.confirmation == "confirmed" and link.scenario_ref in resolved}
    result = {
        "requirements": _metric(context.requirement_baseline, requirements,
                                set(context.requirement_baseline.items) - requirements if context.requirement_baseline else []),
        "model": CoverageLayer(status="assessed" if sm.transitions else "not_applicable",
                               numerator=len(covered_transitions), denominator=len(sm.transitions),
                               ratio=round(len(covered_transitions) / len(sm.transitions), 3) if sm.transitions else None,
                               baseline_source=sm.meta.source or "state_machine.transitions", baseline_version=sm.meta.version),
        "scenario_design": _metric(context.design_baseline, resolved,
                                   set(context.design_baseline.items) - resolved if context.design_baseline else []),
        "execution": _metric(context.case_baseline, set()),
        "execution_pass": CoverageLayer(status="not_assessed"),
    }
    if context.case_baseline is None:
        result["execution"].unassessed_items = sorted({record.case_id for record in context.execution_records or []})
        return result
    if not context.case_baseline.items:
        result["execution_pass"] = _metric(context.case_baseline, set())
        return result
    if context.execution_records is None:
        result["execution"] = CoverageLayer(status="not_assessed", baseline_source=context.case_baseline.source,
                                            baseline_version=context.case_baseline.version,
                                            unassessed_items=sorted(set(context.case_baseline.items)))
        result["execution_pass"].baseline_source = context.case_baseline.source
        result["execution_pass"].baseline_version = context.case_baseline.version
        result["execution_pass"].unassessed_items = sorted(set(context.case_baseline.items))
        return result
    cases, by_run, unassessed = set(context.case_baseline.items), {}, set()
    for record in context.execution_records:
        if record.case_id not in cases or record.baseline_version != context.case_baseline.version:
            unassessed.add(record.case_id)
            continue
        if (record.status not in {"passed", "failed"} or record.evidence_status != "verified"
                or not record.evidence_ref or record.evidence_ref.strip().lower() in {"unknown", "待确认", "?"}
                or not record.evidence_check_source or record.evidence_check_source.strip().lower() in {"unknown", "待确认", "?"}):
            unassessed.add(record.case_id)
            continue
        key = (record.case_id, record.run_id)
        by_run.setdefault(key, set()).add(record.status)
    conflicts = {case for (case, run), statuses in by_run.items() if len(statuses) != 1}
    unassessed.update(conflicts)
    completed = {case for case, run in by_run if case not in conflicts}
    passed = {case for case in completed if all(statuses == {"passed"}
                                               for (item, run), statuses in by_run.items() if item == case)}
    result["execution"] = _metric(context.case_baseline, completed, unassessed)
    if completed:
        result["execution_pass"] = CoverageLayer(
            status="assessed", numerator=len(passed), denominator=len(completed),
            ratio=round(len(passed) / len(completed), 3), baseline_source=context.case_baseline.source,
            baseline_version=context.case_baseline.version, unassessed_items=sorted(unassessed))
    else:
        result["execution_pass"].baseline_source = context.case_baseline.source
        result["execution_pass"].baseline_version = context.case_baseline.version
        result["execution_pass"].unassessed_items = sorted(unassessed)
    return result
