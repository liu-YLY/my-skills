from state_machine_testing_mcp.coverage import check_coverage
from state_machine_testing_mcp.generators import generate_scenarios
from state_machine_testing_mcp.schemas import StateMachine, ScenarioList
from state_machine_testing_mcp.validators import validate_state_machine


def model():
    return StateMachine.model_validate({
        "meta": {"object": "审批"},
        "states": [
            {"name": "待审", "meaning": "等待审批", "is_initial": True},
            {"name": "通过", "meaning": "审批通过", "is_terminal": True},
            {"name": "拒绝", "meaning": "审批拒绝", "is_terminal": True},
        ],
        "transitions": [
            {"from": "待审", "to": target, "event": "审批", "guards": [guard],
             "side_effects": ["记录审批结果"], "evidence_type": "需求明确"}
            for target, guard in [("通过", "同意"), ("拒绝", "不同意")]
        ],
        "forbidden": [{"from": "通过", "to": "*", "reason": "终态不可变更",
                       "evidence_type": "需求明确"}],
    })


def legal_cases(sm):
    return generate_scenarios(sm, ["legal_transition"])


def test_complete_model_passes_structural_checks_but_requires_manual_review():
    report = validate_state_machine(model())
    assert report.overall_status == "pass"
    assert report.manual_review_required
    assert next(c for c in report.checks if c.check_id == "C5").status == "not_checked"


def test_both_guard_branches_are_covered():
    sm = model()
    scenarios = legal_cases(sm)
    assert check_coverage(sm, scenarios).transition_coverage == 1
    assert {s.precondition for s in scenarios.scenarios} == {"待审 状态，同意", "待审 状态，不同意"}


def test_reference_does_not_hide_wrong_target_or_guard():
    sm = model()
    scenarios = legal_cases(sm)
    scenarios.scenarios[0].expected_target_state = "待审"
    scenarios.scenarios[1].guard_conditions = ["同意"]
    report = check_coverage(sm, scenarios)
    assert report.transition_coverage == 0
    assert len(report.unmatched_scenarios) == 2


def test_identical_event_and_target_still_require_the_correct_guard():
    sm = model()
    sm.transitions[1].to_state = "通过"
    scenarios = legal_cases(sm)
    scenarios.scenarios = scenarios.scenarios[:1]
    assert check_coverage(sm, scenarios).transition_coverage == 0.5


def test_no_reference_requires_unique_complete_match():
    sm = model()
    scenarios = legal_cases(sm)
    for scenario in scenarios.scenarios:
        scenario.transition_id = None
    assert check_coverage(sm, scenarios).transition_coverage == 1
    scenarios.scenarios[0].guard_conditions = []
    assert check_coverage(sm, scenarios).transition_coverage == 0.5


def test_duplicate_model_edges_cannot_gain_coverage_by_ambiguity():
    sm = model()
    sm.transitions.append(sm.transitions[0].model_copy())
    scenarios = legal_cases(sm)
    assert check_coverage(sm, scenarios).transition_coverage < 1
    assert validate_state_machine(sm).overall_status == "fail"


def test_forbidden_rule_requires_target_and_unchanged_state():
    sm = model()
    scenarios = generate_scenarios(sm, ["illegal_transition"])
    assert check_coverage(sm, scenarios).forbidden_coverage == 1
    scenarios.scenarios = scenarios.scenarios[:1]
    scenarios.scenarios[0].expected_target_state = "拒绝"
    assert check_coverage(sm, scenarios).forbidden_coverage == 0


def test_invalid_endpoints_initial_state_and_duplicate_state_fail():
    sm = model()
    sm.states[0].is_initial = False
    sm.states.append(sm.states[0].model_copy())
    sm.transitions[0].to_state = "不存在"
    sm.forbidden[0].from_state = "不存在"
    report = validate_state_machine(sm, strict=False)
    assert report.overall_status == "fail"
    detail = next(c.detail for c in report.checks if c.check_id == "C0")
    assert "初始态" in detail and "重复" in detail and "端点" in detail


def test_legal_and_forbidden_edge_conflict_is_structural_failure():
    sm = model()
    sm.forbidden[0].from_state = "待审"
    assert validate_state_machine(sm, strict=False).overall_status == "fail"


def test_empty_coverage_is_not_full_coverage():
    assert check_coverage(model(), ScenarioList(scenarios=[])).transition_coverage == 0


def test_wildcard_is_not_a_concrete_attempt_target():
    sm = model()
    scenarios = generate_scenarios(sm, ["illegal_transition"])
    scenarios.scenarios = scenarios.scenarios[:1]
    scenarios.scenarios[0].attempted_target_state = "*"
    report = check_coverage(sm, scenarios)
    assert report.forbidden_coverage == 0
    assert report.unmatched_scenarios == [scenarios.scenarios[0].id]



def test_guard_failure_cannot_choose_or_forbid_a_sibling_target():
    sm = model()
    for same_target in (False, True):
        if same_target:
            sm.transitions[1].to_state = sm.transitions[0].to_state
        result = generate_scenarios(sm, ["guard_violation"])
        assert len(result.scenarios) == 2
        for scenario, transition in zip(result.scenarios, sm.transitions):
            assert scenario.expected_target_state == "待确认"
            assert scenario.expected_target_state_reason
            assert scenario.forbidden_states == []
            assert scenario.transition_id == transition.id
            assert scenario.violated_guard in transition.guards
            assert scenario.guard_conditions == transition.guards


def test_individual_guard_failure_keeps_other_conditions_explicit():
    sm = model()
    sm.transitions = sm.transitions[:1]
    sm.transitions[0].guards = ["金额一致", "签名有效"]
    result = generate_scenarios(sm, ["guard_violation"])
    assert {s.violated_guard for s in result.scenarios} == {"金额一致", "签名有效"}
    for scenario in result.scenarios:
        other = next(g for g in sm.transitions[0].guards if g != scenario.violated_guard)
        assert other + " 满足" in scenario.precondition
        assert "联合可满足性未验证" in scenario.notes



def test_stable_scenario_refs_survive_reordering_filtering_and_id_only_changes():
    sm = model()
    before = generate_scenarios(sm, ["legal_transition"])
    refs = {s.expected_target_state: s.stable_ref for s in before.scenarios}
    sm.transitions.reverse()
    for t in sm.transitions:
        t.id = "RENAMED-" + t.id
    after = generate_scenarios(sm, ["legal_transition"], "需求明确")
    assert {s.expected_target_state: s.stable_ref for s in after.scenarios} == refs
    assert all(s.id.startswith("SM-") for s in after.scenarios)


def test_source_changes_invalidate_only_confirmed_descendants_and_keep_candidates_separate():
    from state_machine_testing_mcp.schemas import TraceabilityContext
    from state_machine_testing_mcp.provenance import affected_by_change
    context = TraceabilityContext.model_validate({
        "sources": [{"id": "SRC-OFFER", "location": "PRD", "version": "1", "availability": "available"}],
        "artifacts": [{"id": x, "kind": k} for x,k in [
            ("REQ-LIMIT", "requirement"), ("RISK-LIMIT", "risk"),
            ("SC-LIMIT", "scenario"), ("TC-LIMIT", "case"), ("TC-LOGIN", "case")]],
        "links": [{"upstream": a, "downstream": b, "confirmation": c,
                   "source": "PRD §优惠上限关联", "source_refs": ["SRC-OFFER"]} for a,b,c in [
            ("SRC-OFFER", "REQ-LIMIT", "confirmed"), ("REQ-LIMIT", "RISK-LIMIT", "confirmed"),
            ("RISK-LIMIT", "SC-LIMIT", "confirmed"), ("SC-LIMIT", "TC-LIMIT", "confirmed"),
            ("REQ-LIMIT", "TC-LOGIN", "candidate"), ("TC-LIMIT", "SC-LIMIT", "confirmed")]]})
    report = affected_by_change(context, ["SRC-OFFER"])
    assert set(report.affected) == {"REQ-LIMIT", "RISK-LIMIT", "SC-LIMIT", "TC-LIMIT"}
    assert report.candidate_impacts == ["TC-LOGIN"]
    context.links.reverse()
    assert affected_by_change(context, ["SRC-OFFER", "SRC-OFFER"]) == report
    assert affected_by_change(context, ["MISSING"]).unmatched_refs == ["MISSING"]


def test_deduplication_keeps_distinct_guards_and_targets():
    from state_machine_testing_mcp.provenance import deduplicate_scenarios
    scenarios = generate_scenarios(model(), ["guard_violation"]).scenarios
    duplicate = scenarios[0].model_copy(update={"id": "other"})
    assert len(deduplicate_scenarios(scenarios + [duplicate])) == 2



def test_unsubstantiated_or_unreachable_trace_links_are_only_candidate_impacts():
    from state_machine_testing_mcp.schemas import TraceabilityContext
    from state_machine_testing_mcp.provenance import affected_by_change
    base = {"sources": [{"id": "S", "location": "PRD", "version": "1", "availability": "available"}],
        "artifacts": [{"id": "R", "kind": "requirement"}],
        "links": [{"upstream": "S", "downstream": "R", "confirmation": "confirmed",
                   "source": "PRD §1明确关联", "source_refs": ["S"]}]}
    assert affected_by_change(TraceabilityContext.model_validate(base), ["S"]).affected == ["R"]
    for missing in ["basis", "unreachable", "refs", "version", "location"]:
        import copy
        data = copy.deepcopy(base)
        if missing == "basis": data["links"][0]["source"] = ""
        elif missing == "unreachable": data["sources"][0]["availability"] = "unreachable"
        elif missing == "version": data["sources"][0]["version"] = ""
        elif missing == "location": data["sources"][0]["location"] = ""
        else: data["links"][0]["source_refs"] = []
        report = affected_by_change(TraceabilityContext.model_validate(data), ["S"])
        assert report.affected == [] and report.candidate_impacts == ["R"]
        assert report.uncorroborated_links



def test_changed_mapping_source_reviews_its_downstream_without_affecting_unrelated_cases():
    from state_machine_testing_mcp.schemas import TraceabilityContext
    from state_machine_testing_mcp.provenance import affected_by_change
    import copy
    data = {"sources": [{"id": "SRC", "location": "req.md", "version": "v1", "availability": "available"}],
        "artifacts": [{"id": x, "kind": k} for x,k in [("REQ", "requirement"), ("SC", "scenario"),
                     ("TC", "case"), ("LOGIN", "case")]],
        "links": [{"upstream": a, "downstream": z, "confirmation": "confirmed",
                   "source": "明确映射依据", "source_refs": ["SRC"]} for a,z in [("REQ", "SC"), ("SC", "TC")]]}
    original = copy.deepcopy(data)
    context = TraceabilityContext.model_validate(data)
    by_source = affected_by_change(context, ["SRC"])
    assert by_source.affected == ["SC", "TC"] and by_source.candidate_impacts == []
    assert "LOGIN" not in by_source.affected
    assert affected_by_change(context, ["REQ"]).affected == ["SC", "TC"]
    data["sources"][0]["availability"] = "unreachable"
    candidate = affected_by_change(TraceabilityContext.model_validate(data), ["SRC"])
    assert candidate.affected == [] and candidate.candidate_impacts == ["SC", "TC"]
    assert context.model_dump(mode="json")["sources"] == original["sources"]
