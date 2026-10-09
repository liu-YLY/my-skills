"""check_coverage 单元测试。"""

from __future__ import annotations

import json
from pathlib import Path

from state_machine_testing_mcp.coverage import check_coverage
from state_machine_testing_mcp.generators import generate_scenarios
from state_machine_testing_mcp.schemas import StateMachine

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_order_refund() -> StateMachine:
    fixture = FIXTURES_DIR / "order_refund_state_machine.json"
    return StateMachine.model_validate(json.loads(fixture.read_text(encoding="utf-8")))


def test_coverage_report_fields() -> None:
    """覆盖度报告应包含所有必填字段。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    report = check_coverage(sm, scenarios)
    assert 0.0 <= report.transition_coverage <= 1.0
    assert 0.0 <= report.forbidden_coverage <= 1.0
    assert "legal_transition" in report.scenario_type_coverage
    assert "需求明确" in report.evidence_distribution


def test_transition_coverage_full() -> None:
    """generate_scenarios 默认生成 legal_transition，覆盖率应为 1.0。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    report = check_coverage(sm, scenarios)
    assert report.transition_coverage == 1.0


def test_missing_scenario_types_empty_by_default() -> None:
    """默认生成 10 类，missing_scenario_types 应为空（或仅缺少无触发条件的类）。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    report = check_coverage(sm, scenarios)
    # 订单退款 fixture 涉及回调/异步/超时/管理员，多数类型应能生成
    # access_control 可能因为 fixture 没有显式管理员事件而为空
    assert "legal_transition" not in report.missing_scenario_types
    assert "failure_recovery" not in report.missing_scenario_types


def test_uncovered_transitions_empty_when_legal_generated() -> None:
    """生成 legal_transition 后，uncovered_transitions 应为空。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    report = check_coverage(sm, scenarios)
    assert report.uncovered_transitions == []



def test_applicability_separates_missing_excluded_and_unknown():
    from state_machine_testing_mcp.schemas import ScenarioList
    sm = _load_order_refund()
    data = sm.model_dump(by_alias=True)
    data["scenario_applicability"] = {
        "message_reorder": {"status": "not_applicable", "reason": "同步无消息", "source": "PRD §1"},
        "idempotency": {"status": "applicable", "reason": "回调会重复", "source": "PRD §2"}}
    sm = StateMachine.model_validate(data)
    report = check_coverage(sm, ScenarioList(scenarios=[]))
    assert "legal_transition" in report.applicable_missing_scenario_types
    assert "idempotency" in report.applicable_missing_scenario_types
    assert "message_reorder" in report.not_applicable_scenario_types
    assert "access_control" in report.unknown_scenario_types
    assert "access_control" not in report.applicable_missing_scenario_types
    assert report.scenario_type_coverage["access_control"] == 0
    assert "access_control" in report.missing_scenario_types


def test_markdown_keeps_applicability_unknown_visible():
    from state_machine_testing_mcp.exporters import export_to_markdown
    sm = _load_order_refund()
    output = export_to_markdown(sm, generate_scenarios(sm))
    assert "适用性" in output
    assert "access_control | unknown" in output



def test_applicable_missing_ignores_wrong_structural_match_and_pending_candidates():
    from state_machine_testing_mcp.schemas import ScenarioList
    data = _load_order_refund().model_dump(by_alias=True)
    data["scenario_applicability"] = {"idempotency": {"status": "applicable",
        "reason": "需求要求幂等", "source": "PRD §2"}}
    sm = StateMachine.model_validate(data)
    generated = generate_scenarios(sm, ["legal_transition", "idempotency"])
    raw = generated.model_dump(mode="json")
    for scenario in raw["scenarios"]:
        if scenario["risk_type"] == "legal_transition":
            scenario["guard_conditions"] = ["不存在的守卫"]
        else:
            scenario["expected_target_state"] = "待确认"
            scenario["expected_target_state_reason"] = "重复事件结果规则未明确"
            scenario["evidence_type"] = "待确认"
    report = check_coverage(sm, ScenarioList.model_validate(raw))
    assert report.scenario_type_coverage["legal_transition"] > 0
    assert report.scenario_type_coverage["idempotency"] > 0
    assert "legal_transition" in report.applicable_missing_scenario_types
    assert "idempotency" in report.applicable_missing_scenario_types


def test_layered_coverage_distinguishes_missing_and_explicit_empty_baselines():
    from state_machine_testing_mcp.schemas import CoverageContext, CoverageBaseline
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    missing = check_coverage(sm, scenarios)
    assert missing.transition_coverage == 1
    assert missing.layers["requirements"].status == "not_assessed"
    assert missing.layers["execution"].ratio is None
    context = CoverageContext(requirement_baseline=CoverageBaseline(
        source="PRD", version="1", items=[]))
    empty = check_coverage(sm, scenarios, context)
    assert empty.layers["requirements"].status == "not_applicable"
    assert empty.layers["requirements"].denominator == 0
    assert empty.layers["requirements"].ratio is None


def test_design_coverage_never_claims_execution_and_duplicate_evidence_counts_once():
    from state_machine_testing_mcp.schemas import CoverageContext
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm, ["legal_transition"])
    ref = scenarios.scenarios[0].stable_ref
    context = CoverageContext.model_validate({
        "requirement_baseline": {"source": "PRD", "version": "1", "items": ["REQ-1"]},
        "requirement_links": [{"item_id": "REQ-1", "scenario_ref": ref, "confirmation": "confirmed"}],
        "design_baseline": {"source": "适用场景基线", "version": "1", "items": [ref]},
        "case_baseline": {"source": "用例基线", "version": "1", "items": ["TC-1"]}, "execution_records": []})
    designed = check_coverage(sm, scenarios, context)
    assert designed.layers["requirements"].ratio == designed.layers["scenario_design"].ratio == 1
    assert designed.layers["execution"].ratio == 0
    assert designed.layers["execution_pass"].status == "not_assessed"
    record = {"case_id": "TC-1", "baseline_version": "1", "run_id": "run-1",
              "status": "passed", "evidence_ref": "output/run-1", "evidence_status": "verified", "evidence_check_source": "原始报告核验"}
    data = context.model_dump()
    data["execution_records"] = [record, record]
    completed = check_coverage(sm, scenarios, CoverageContext.model_validate(data))
    assert completed.layers["execution"].numerator == 1
    assert completed.layers["execution_pass"].ratio == 1
    data["execution_records"] = [record, dict(record, status="failed")]
    conflicting = check_coverage(sm, scenarios, CoverageContext.model_validate(data))
    assert conflicting.layers["execution_pass"].ratio is None
    assert conflicting.layers["execution"].unassessed_items == ["TC-1"]


def test_empty_execution_scope_is_distinct_from_missing_execution():
    from state_machine_testing_mcp.schemas import CoverageContext
    sm = _load_order_refund()
    context = CoverageContext.model_validate({"case_baseline": {"source": "本批无可执行用例", "version": "1", "items": []}})
    report = check_coverage(sm, generate_scenarios(sm), context)
    assert report.layers["execution_pass"].status == "not_applicable"
    assert report.layers["execution_pass"].denominator == 0


def test_retracting_evidence_cannot_increase_confirmed_requirement_coverage():
    from state_machine_testing_mcp.schemas import CoverageContext
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm, ["legal_transition"])
    ref = scenarios.scenarios[0].stable_ref
    context = CoverageContext.model_validate({"requirement_baseline": {"source": "PRD", "version": "1", "items": ["R"]},
        "requirement_links": [{"item_id": "R", "scenario_ref": ref, "confirmation": "confirmed"}]})
    assert check_coverage(sm, scenarios, context).layers["requirements"].ratio == 1
    data = sm.model_dump(by_alias=True)
    data["transitions"][0]["evidence_type"] = "待确认"
    sm = StateMachine.model_validate(data)
    changed = generate_scenarios(sm, ["legal_transition"])
    assert check_coverage(sm, changed, context).layers["requirements"].ratio == 0


def test_unknown_or_stale_execution_evidence_never_counts_as_executed():
    from state_machine_testing_mcp.schemas import CoverageContext
    sm = _load_order_refund()
    base = {"case_baseline": {"source": "用例基线", "version": "2", "items": ["TC", "TC"]}}
    record = {"case_id": "TC", "baseline_version": "2", "run_id": "1", "status": "passed", "evidence_ref": "raw/result"}
    for change in [{}, {"evidence_status": "unreachable"}, {"evidence_status": "verified", "baseline_version": "1"},
                   {"evidence_status": "verified", "evidence_ref": "待确认"}]:
        report = check_coverage(sm, generate_scenarios(sm), CoverageContext.model_validate(
            dict(base, execution_records=[dict(record, **change)])))
        assert report.layers["execution"].numerator == 0
        assert report.layers["execution"].denominator == 1
        assert report.layers["execution_pass"].ratio is None


def test_unmatched_and_unknown_failure_scenarios_cannot_gain_requirement_coverage():
    from state_machine_testing_mcp.schemas import CoverageContext, ScenarioList
    sm = _load_order_refund()
    for kind in ["legal_transition", "illegal_transition", "failure_recovery"]:
        data = generate_scenarios(sm, [kind]).model_dump(mode="json")
        item = data["scenarios"][0]
        item["evidence_type"] = "需求明确"
        if kind == "legal_transition":
            item["guard_conditions"] = ["错误守卫"]
        elif kind == "illegal_transition":
            item["attempted_target_state"] = "不存在"
        else:
            item["expected_target_state"] = "待支付"
        ref = item["stable_ref"]
        context = CoverageContext.model_validate({
            "requirement_baseline": {"source": "PRD", "version": "1", "items": ["R", "R"]},
            "requirement_links": [{"item_id": "R", "scenario_ref": ref, "confirmation": "confirmed"}]})
        report = check_coverage(sm, ScenarioList.model_validate(data), context)
        assert report.layers["requirements"].numerator == 0, kind
        assert report.layers["requirements"].denominator == 1



def test_pending_matched_legal_keeps_legacy_ratio_but_not_new_model_numerator():
    sm = _load_order_refund()
    raw = generate_scenarios(sm, ["legal_transition"]).model_dump(mode="json")
    for case in raw["scenarios"]: case["evidence_type"] = "待确认"
    from state_machine_testing_mcp.schemas import ScenarioList
    report = check_coverage(sm, ScenarioList.model_validate(raw))
    assert report.transition_coverage == 1
    assert report.layers["model"].numerator == 0 and report.layers["model"].ratio == 0


def test_execution_input_is_three_state_and_checked_basis_is_required():
    from state_machine_testing_mcp.schemas import CoverageContext
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    base = {"case_baseline": {"source": "用例基线", "version": "1", "items": ["TC"]}}
    missing = check_coverage(sm, scenarios, CoverageContext.model_validate(base))
    assert missing.layers["execution"].status == "not_assessed" and missing.layers["execution"].ratio is None
    empty = check_coverage(sm, scenarios, CoverageContext.model_validate(dict(base, execution_records=[])))
    assert empty.layers["execution"].status == "assessed" and empty.layers["execution"].ratio == 0
    record = {"case_id": "TC", "baseline_version": "1", "run_id": "1", "status": "passed",
              "evidence_ref": "run/output", "evidence_status": "verified"}
    unknown = check_coverage(sm, scenarios, CoverageContext.model_validate(dict(base, execution_records=[record])))
    assert unknown.layers["execution"].numerator == 0
    record["evidence_check_source"] = "原始执行报告核验"
    known = check_coverage(sm, scenarios, CoverageContext.model_validate(dict(base, execution_records=[record])))
    assert known.layers["execution"].numerator == 1



def test_pending_model_rule_cannot_be_promoted_by_an_explicit_scenario_label():
    from state_machine_testing_mcp.schemas import ScenarioList, CoverageContext
    data = _load_order_refund().model_dump(by_alias=True)
    data["transitions"][0]["evidence_type"] = "待确认"
    data["forbidden"][0]["evidence_type"] = "待确认"
    sm = StateMachine.model_validate(data)
    for kind in ["legal_transition", "illegal_transition"]:
        raw = generate_scenarios(sm, [kind]).model_dump(mode="json")
        raw["scenarios"] = raw["scenarios"][:1]
        raw["scenarios"][0]["evidence_type"] = "需求明确"
        ref = raw["scenarios"][0]["stable_ref"]
        context = CoverageContext.model_validate({"requirement_baseline": {"source": "PRD", "version": "1", "items": ["R"]},
            "requirement_links": [{"item_id": "R", "scenario_ref": ref, "confirmation": "confirmed"}]})
        report = check_coverage(sm, ScenarioList.model_validate(raw), context)
        assert report.layers["requirements"].numerator == 0, kind
        if kind == "legal_transition": assert report.layers["model"].numerator == 0



def test_withdrawing_a_failed_runs_evidence_cannot_raise_confirmed_pass_count():
    from state_machine_testing_mcp.schemas import CoverageContext
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm, ["legal_transition"])
    def report(second):
        return check_coverage(sm, scenarios, CoverageContext.model_validate({
            "case_baseline": {"source": "cases", "version": "v1", "items": ["C"]},
            "execution_records": [dict(case_id="C", baseline_version="v1", run_id="r1", status="passed",
                evidence_status="verified", evidence_ref="r1", evidence_check_source="read r1"), second]}))
    failed = dict(case_id="C", baseline_version="v1", run_id="r2", status="failed",
                  evidence_status="verified", evidence_ref="r2", evidence_check_source="read r2")
    known = report(failed)
    for update in [{"evidence_status": "unknown"}, {"evidence_status": "unreachable"},
                   {"evidence_ref": None}, {"evidence_check_source": None}]:
        after = report(dict(failed, **update))
        assert after.transition_coverage == known.transition_coverage == 1
        assert after.layers["execution"].numerator == after.layers["execution"].denominator == 1
        assert after.layers["execution_pass"].numerator == known.layers["execution_pass"].numerator == 0
        assert after.layers["execution_pass"].denominator == 1
        assert after.layers["execution_pass"].unassessed_items == ["C"]
    other_version = report(dict(failed, baseline_version="old", evidence_status="unknown"))
    assert other_version.layers["execution_pass"].ratio == 1
    assert other_version.layers["execution_pass"].unassessed_items == []



def test_failure_design_cannot_override_allowed_states_or_model_outcomes():
    from state_machine_testing_mcp.schemas import ScenarioList, CoverageContext
    import copy
    data = _load_order_refund().model_dump(by_alias=True)
    data["transitions"][0]["failure_outcomes"] = [{"phase": "committed_response_lost", "allowed_states": ["已支付"],
        "source": "PRD §支付", "evidence_type": "需求明确"}]
    sm = StateMachine.model_validate(data)
    legal = generate_scenarios(sm, ["legal_transition"]).model_dump(mode="json")["scenarios"]
    case = generate_scenarios(sm, ["failure_recovery"]).model_dump(mode="json")["scenarios"][0]
    ref = case["stable_ref"]
    context = CoverageContext.model_validate({"requirement_baseline": {"source": "PRD", "version": "1", "items": ["R"]},
        "requirement_links": [{"item_id": "R", "scenario_ref": ref, "confirmation": "confirmed"}],
        "design_baseline": {"source": "设计", "version": "1", "items": [ref]}})
    def report(item):
        return check_coverage(sm, ScenarioList.model_validate({"scenarios": legal + [item]}), context)
    good = report(case)
    assert good.layers["requirements"].numerator == good.layers["scenario_design"].numerator == 1
    for mutation in ["target", "empty", "conditional", "phase", "reference", "guard", "withdraw_evidence"]:
        wrong = copy.deepcopy(case)
        if mutation == "target": wrong["expected_target_state"] = "待支付"
        elif mutation == "empty": wrong["failure_semantics"]["allowed_states"] = []
        elif mutation == "conditional": wrong["failure_semantics"]["allowed_states"] = ["已支付", "待支付"]
        elif mutation == "phase": wrong["failure_semantics"]["phase"] = "pre_commit_failed"
        elif mutation == "reference": wrong["transition_id"] = sm.transitions[1].id
        elif mutation == "guard": wrong["guard_conditions"] = []
        else: wrong["failure_semantics"]["evidence_type"] = "待确认"
        result = report(wrong)
        assert result.transition_coverage == good.transition_coverage == 1
        assert result.forbidden_coverage == good.forbidden_coverage
        assert result.scenario_type_coverage["failure_recovery"] == 1
        assert "failure_recovery" in result.applicable_missing_scenario_types, mutation
        assert result.layers["requirements"].numerator == result.layers["scenario_design"].numerator == 0, mutation



def test_failure_without_model_outcomes_still_requires_unique_structural_transition():
    from state_machine_testing_mcp.schemas import ScenarioList, CoverageContext
    import copy
    data = _load_order_refund().model_dump(by_alias=True)
    data["scenario_applicability"] = {"failure_recovery": {"status": "applicable",
        "reason": "明确响应丢失场景", "source": "PRD §支付", "evidence_type": "需求明确"}}
    sm = StateMachine.model_validate(data)
    case = generate_scenarios(sm, ["failure_recovery"]).model_dump(mode="json")["scenarios"][0]
    case.update(evidence_type="需求明确", expected_target_state="已支付", transition_id=None)
    case["failure_semantics"] = {"phase": "committed_response_lost", "allowed_states": ["已支付"],
        "source": "明确场景事实", "evidence_type": "需求明确"}
    ref = case["stable_ref"]
    context = CoverageContext.model_validate({"requirement_baseline": {"source": "PRD", "version": "1", "items": ["R"]},
        "requirement_links": [{"item_id": "R", "scenario_ref": ref, "confirmation": "confirmed"}],
        "design_baseline": {"source": "设计", "version": "1", "items": [ref]}})
    def report(model, item):
        legal = generate_scenarios(model, ["legal_transition"]).scenarios
        return check_coverage(model, ScenarioList.model_validate({"scenarios": [s.model_dump(mode="json") for s in legal] + [item]}), context)
    good = report(sm, case)
    assert good.layers["requirements"].numerator == good.layers["scenario_design"].numerator == 1
    for field, value in [("trigger_event", "不存在事件"), ("current_state", "已支付"), ("guard_conditions", [])]:
        wrong = copy.deepcopy(case)
        wrong[field] = value
        result = report(sm, wrong)
        assert result.transition_coverage == good.transition_coverage == 1
        assert "failure_recovery" in result.applicable_missing_scenario_types
        assert result.layers["requirements"].numerator == result.layers["scenario_design"].numerator == 0
    changed = copy.deepcopy(data)
    changed["transitions"][1]["failure_outcomes"] = [{"phase": "pre_commit_failed", "allowed_states": ["待支付"],
        "source": "无关取消规则", "evidence_type": "需求明确"}]
    unaffected = report(StateMachine.model_validate(changed), case)
    assert unaffected.layers["requirements"].numerator == good.layers["requirements"].numerator == 1
    assert unaffected.layers["scenario_design"].numerator == 1
