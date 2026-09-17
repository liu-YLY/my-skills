from review_checker_mcp.schemas import Issue, SemanticFacts, TestCase, TestCaseSet
from review_checker_mcp.server import generate_report, review_test_cases
from review_checker_mcp.validators import check_semantic_conflicts


def case(**changes):
    values = dict(id="TC_ORDER_001", title="支付回调幂等性", priority="P1",
                  type="functional", steps=["选择商品", "提交订单", "支付 100 元"],
                  expected_results=["订单为已支付", "支付记录金额为 100 元"])
    return TestCase(**(values | changes))


def test_business_results_do_not_require_equal_step_count():
    sample = case(checkpoints=[{"after_step": 2, "expected_results": ["订单为待支付"]}])
    assert not review_test_cases(TestCaseSet(cases=[sample]))


def test_cohesive_long_flow_is_not_a_defect():
    sample = case(steps=[f"处理第 {i} 个订单" for i in range(16)])
    assert not review_test_cases(TestCaseSet(cases=[sample]))


def test_empty_results_and_invalid_checkpoint_are_reported():
    sample = case(expected_results=["  "], checkpoints=[
        {"after_step": 4, "expected_results": ["订单为已支付"]}])
    issues = review_test_cases(TestCaseSet(cases=[sample]))
    assert any("expected_results" in i.evidence for i in issues)
    assert any("after_step" in i.evidence for i in issues)


def test_vague_checkpoint_is_reported():
    sample = case(checkpoints=[{"after_step": 2, "expected_results": ["功能正常"]}])
    assert any(i.dimension == "可执行性" for i in review_test_cases(TestCaseSet(cases=[sample])))


def test_legitimate_terms_are_not_vague_expectations():
    sample = case(expected_results=["正常订单显示为已支付，异常订单显示拒绝原因"])
    assert not review_test_cases(TestCaseSet(cases=[sample]))


def test_collection_p0_vetoes_grade_even_with_clean_case_ratio():
    samples = [case(id=f"TC_{i}") for i in range(20)]
    issue = Issue(case_id="-", dimension="覆盖度", severity="P0", rule="明确缺少资金校验",
                  evidence="需求要求核验支付金额，所有用例均未覆盖")
    report = generate_report(TestCaseSet(cases=samples), [issue])
    assert report.pass_rate == 1
    assert report.grade == "D"


def test_candidate_does_not_change_metrics():
    issue = Issue(case_id="TC_ORDER_001", dimension="冗余", severity="P1",
                  rule="标题相同", evidence="标题一致", confirmation="candidate")
    report = generate_report(TestCaseSet(cases=[case()]), [issue])
    assert report.total_issues == 0
    assert report.issue_cases == 0
    assert report.candidate_issues == [issue]
    assert report.issues == []


def test_missing_baseline_is_not_assessed_and_empty_set_has_no_grade():
    report = generate_report(TestCaseSet(cases=[case()]))
    assert "覆盖度" in report.not_assessed
    assert "溯源" in report.not_assessed
    assert "语义一致性" in report.not_assessed
    empty = generate_report(TestCaseSet(cases=[]))
    assert empty.grade == "未评估"
    assert empty.pass_rate is None


def test_only_declared_applicable_scenarios_are_required():
    dataset = TestCaseSet(cases=[case(scenario="正向")], required_scenarios=["正向", "逆向"])
    issues = review_test_cases(dataset)
    assert len(issues) == 1
    assert "逆向" in issues[0].evidence


def fact(case_id, state, outcome, **changes):
    values = dict(case_id=case_id, test_point_id="TP_VIEW", preconditions=[
        {"subject": "登录状态", "state": state, "polarity": "affirmative"}],
        inputs=[{"input_signature": "查看订单42", "expected_outcome": outcome}])
    return SemanticFacts(**(values | changes))


def test_different_business_contexts_are_not_conflicts():
    assert not check_semantic_conflicts([
        fact("TC_A", "已登录", "显示详情"), fact("TC_B", "未登录", "提示登录")])


def test_matching_context_with_different_outcome_is_only_a_candidate():
    issues = check_semantic_conflicts([
        fact("TC_A", "已登录", "显示详情"), fact("TC_B", "已登录", "提示登录")])
    assert len(issues) == 1
    assert issues[0].confirmation == "candidate"


def test_same_case_opposite_claims_are_detected():
    sample = fact("TC_A", "已登录", "显示详情")
    sample.preconditions.append(sample.preconditions[0].model_copy(update={"polarity": "negation"}))
    issues = check_semantic_conflicts([sample])
    assert len(issues) == 1
    assert issues[0].case_id == "TC_A"
    assert issues[0].severity == "P0"


def test_same_subject_different_states_are_not_opposite_claims():
    sample = fact("TC_A", "已登录", "显示详情")
    sample.preconditions.append(sample.preconditions[0].model_copy(
        update={"state": "被冻结", "polarity": "negation"}))
    assert not check_semantic_conflicts([sample])
