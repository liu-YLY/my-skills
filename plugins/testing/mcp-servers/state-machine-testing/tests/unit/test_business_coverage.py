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
