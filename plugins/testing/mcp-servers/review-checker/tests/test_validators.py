"""9 维度校验逻辑单元测试。"""

from __future__ import annotations

from review_checker_mcp.schemas import (
    Priority,
    ScenarioType,
    TestCase,
    TestCaseSet,
)
from review_checker_mcp.validators import (
    check_automation,
    check_coverage,
    check_executability,
    check_field_completeness,
    check_maintainability,
    check_priority_balance,
    check_redundancy,
    check_test_data_dependency,
    check_traceability,
    validate_all,
)


def _make_case(
    id: str = "TC_test_001",
    title: str = "登录-手机号有效密码-跳转首页",
    priority: Priority = Priority.P1,
    scenario: ScenarioType | None = ScenarioType.POSITIVE,
    steps: list[str] | None = None,
    expected_results: str = "页面跳转至首页，顶部显示用户名",
    preconditions: list[str] | None = None,
    test_point_id: str = "TP_001",
    notes: str = "",
) -> TestCase:
    return TestCase(
        id=id,
        title=title,
        priority=priority,
        type="功能测试",
        scenario=scenario,
        steps=steps or [f"步骤-{id}", "输入手机号 13800138000", "输入密码 Abc12345", "点击登录"],
        expected_results=expected_results,
        preconditions=preconditions or [],
        test_point_id=test_point_id,
        notes=notes,
    )


def _make_set(cases: list[TestCase], test_point_ids: list[str] | None = None) -> TestCaseSet:
    return TestCaseSet(cases=cases, test_point_ids=test_point_ids or ["TP_001"])


class TestCoverage:
    """覆盖度维度。"""

    def test_all_four_types_present_no_issue(self):
        cases = [
            _make_case(id="TC_001", scenario=ScenarioType.POSITIVE),
            _make_case(id="TC_002", scenario=ScenarioType.NEGATIVE),
            _make_case(id="TC_003", scenario=ScenarioType.BOUNDARY),
            _make_case(id="TC_004", scenario=ScenarioType.EXCEPTION),
        ]
        issues = check_coverage(_make_set(cases))
        assert len(issues) == 0

    def test_missing_exception_type_triggers_p0(self):
        cases = [
            _make_case(id="TC_001", scenario=ScenarioType.POSITIVE),
            _make_case(id="TC_002", scenario=ScenarioType.NEGATIVE),
            _make_case(id="TC_003", scenario=ScenarioType.BOUNDARY),
        ]
        issues = check_coverage(_make_set(cases))
        assert len(issues) == 1
        assert issues[0].severity.value == "P0"
        assert "异常" in issues[0].evidence

    def test_scenario_inferred_from_title_when_missing(self):
        case = _make_case(title="登录-网络超时-提示重试", scenario=None)
        issues = check_coverage(_make_set([case]))
        # 单条用例无法覆盖全部 4 类，应触发 P0
        assert any(i.severity.value == "P0" for i in issues)


class TestPriorityBalance:
    """优先级合理性维度。"""

    def test_balanced_priority_no_issue(self):
        cases = []
        for i in range(12):
            cases.append(_make_case(id=f"TC_{i:03d}", priority=Priority.P0))
        for i in range(32):
            cases.append(_make_case(id=f"TC_{i:03d}", priority=Priority.P1))
        for i in range(32):
            cases.append(_make_case(id=f"TC_{i:03d}", priority=Priority.P2))
        for i in range(12):
            cases.append(_make_case(id=f"TC_{i:03d}", priority=Priority.P3))
        issues = check_priority_balance(_make_set(cases))
        assert len(issues) == 0

    def test_p0_ratio_too_high_triggers_p1(self):
        cases = [_make_case(id=f"TC_{i:03d}", priority=Priority.P0) for i in range(10)]
        cases += [_make_case(id=f"TC_{i:03d}", priority=Priority.P2) for i in range(10, 20)]
        issues = check_priority_balance(_make_set(cases))
        assert any(i.severity.value == "P1" and "P0" in i.evidence for i in issues)

    def test_p0_p1_sum_below_50_percent_triggers_p1(self):
        cases = [_make_case(id=f"TC_{i:03d}", priority=Priority.P0) for i in range(2)]
        cases += [_make_case(id=f"TC_{i:03d}", priority=Priority.P1) for i in range(2)]
        cases += [_make_case(id=f"TC_{i:03d}", priority=Priority.P2) for i in range(6)]
        issues = check_priority_balance(_make_set(cases))
        assert any("P0+P1" in i.rule for i in issues)

    def test_p3_not_supported_no_issue(self):
        cases = [_make_case(id=f"TC_{i:03d}", priority=Priority.P0) for i in range(15)]
        cases += [_make_case(id=f"TC_{i:03d}", priority=Priority.P1) for i in range(35)]
        cases += [_make_case(id=f"TC_{i:03d}", priority=Priority.P2) for i in range(50)]
        case_set = TestCaseSet(cases=cases, test_point_ids=["TP_001"], supports_p3=False)
        issues = check_priority_balance(case_set)
        assert not any("P3" in i.evidence for i in issues)


class TestFieldCompleteness:
    """字段规范维度。"""

    def test_complete_case_no_issue(self):
        issues = check_field_completeness(_make_case())
        assert len(issues) == 0

    def test_missing_expected_results_triggers_p0(self):
        case = _make_case(expected_results="")
        issues = check_field_completeness(case)
        assert any(i.severity.value == "P0" and "expected_results" in i.evidence for i in issues)

    def test_vague_word_in_title_triggers_p1(self):
        case = _make_case(title="登录-正确操作-等")
        issues = check_field_completeness(case)
        assert any(i.severity.value == "P1" and "模糊词" in i.rule for i in issues)


class TestTitleLengthGuideline:
    """标题长度软指导（对齐 test-standards.md 超长标题例外判定）。"""

    def test_short_title_no_issue(self):
        # 短标题（≤ 40 字符）不应触发长度规则
        case = _make_case(title="登录-手机号有效密码-跳转首页")
        issues = check_field_completeness(case)
        assert not any("标题长度" in i.rule for i in issues)

    def test_long_title_without_exception_triggers_p2(self):
        # 超长标题（> 40 字符）且 notes 未记录例外 → P2
        long_title = "登录-手机号有效密码-跳转首页-夜间模式-弱网环境-v2接口-多端同步-用户身份验证完整流程"
        case = _make_case(title=long_title)
        issues = check_field_completeness(case)
        title_issues = [i for i in issues if "标题长度" in i.rule]
        assert len(title_issues) == 1
        assert title_issues[0].severity.value == "P2"
        assert "未记录例外" in title_issues[0].evidence

    def test_long_title_with_exception_keyword_no_issue(self):
        # 超长标题 + notes 记录例外关键词 → 不报
        long_title = "登录-手机号有效密码-跳转首页-夜间模式-弱网环境-v2接口-多端同步-用户身份验证完整流程"
        case = _make_case(
            title=long_title,
            notes="保留：场景可区分性优先，删除夜间模式会与基础登录用例重复",
        )
        issues = check_field_completeness(case)
        assert not any("标题长度" in i.rule for i in issues)

    def test_long_title_with_environment_marker_no_issue(self):
        # 超长标题 + notes 含「环境标识」关键词 → 不报
        long_title = "登录-手机号有效密码-跳转首页-夜间模式-弱网环境-v2接口-多端同步-用户身份验证完整流程"
        case = _make_case(
            title=long_title,
            notes="保留：环境标识（夜间模式/弱网/v2 接口）必要",
        )
        issues = check_field_completeness(case)
        assert not any("标题长度" in i.rule for i in issues)

    def test_long_title_with_empty_notes_triggers_p2(self):
        # 超长标题 + notes 为空 → P2（默认 notes 为空）
        long_title = "登录-手机号有效密码-跳转首页-夜间模式-弱网环境-v2接口-多端同步-用户身份验证完整流程"
        case = _make_case(title=long_title)  # notes 默认 ""
        issues = check_field_completeness(case)
        assert any(i.severity.value == "P2" and "标题长度" in i.rule for i in issues)

    def test_long_title_with_irrelevant_notes_triggers_p2(self):
        # 超长标题 + notes 含内容但无例外关键词 → 仍触发 P2
        long_title = "登录-手机号有效密码-跳转首页-夜间模式-弱网环境-v2接口-多端同步-用户身份验证完整流程"
        case = _make_case(title=long_title, notes="这条用例很重要")
        issues = check_field_completeness(case)
        assert any(i.severity.value == "P2" and "标题长度" in i.rule for i in issues)


class TestExecutability:
    """可执行性维度。"""

    def test_placeholder_in_steps_triggers_p0(self):
        case = _make_case(steps=["输入手机号 xxx", "点击登录"])
        issues = check_executability(case)
        assert any(i.severity.value == "P0" and "占位符" in i.rule for i in issues)

    def test_vague_expected_triggers_p1(self):
        case = _make_case(expected_results="功能正常")
        issues = check_executability(case)
        assert any(i.severity.value == "P1" and "模糊预期" in i.rule for i in issues)

    def test_too_many_steps_triggers_p2(self):
        case = _make_case(steps=[f"步骤{i}" for i in range(8)])
        issues = check_executability(case)
        assert any(i.severity.value == "P2" and "步骤数" in i.rule for i in issues)


class TestRedundancy:
    """冗余维度。"""

    def test_same_title_triggers_p1(self):
        cases = [
            _make_case(id="TC_001", title="重复标题"),
            _make_case(id="TC_002", title="重复标题"),
        ]
        issues = check_redundancy(_make_set(cases))
        assert any(i.severity.value == "P1" and "title 相同" in i.rule for i in issues)

    def test_same_first_three_steps_triggers_p1(self):
        cases = [
            _make_case(id="TC_001", title="标题A", steps=["步骤1", "步骤2", "步骤3", "步骤4"]),
            _make_case(id="TC_002", title="标题B", steps=["步骤1", "步骤2", "步骤3", "步骤5"]),
        ]
        issues = check_redundancy(_make_set(cases))
        assert any(i.severity.value == "P1" and "前 3 步一致" in i.rule for i in issues)

    def test_too_many_cases_per_test_point_triggers_p2(self):
        cases = [
            _make_case(id=f"TC_{i:03d}", test_point_id="TP_001") for i in range(4)
        ]
        issues = check_redundancy(_make_set(cases))
        assert any(i.severity.value == "P2" and "同测试点" in i.rule for i in issues)


class TestTraceability:
    """溯源维度。"""

    def test_valid_test_point_no_issue(self):
        issues = check_traceability(_make_case(test_point_id="TP_001"), ["TP_001"])
        assert len(issues) == 0

    def test_empty_test_point_id_triggers_p0(self):
        issues = check_traceability(_make_case(test_point_id=""), ["TP_001"])
        assert any(i.severity.value == "P0" and "为空" in i.evidence for i in issues)

    def test_test_point_not_in_list_triggers_p0(self):
        issues = check_traceability(_make_case(test_point_id="TP_999"), ["TP_001"])
        assert any(i.severity.value == "P0" and "不在清单" in i.evidence for i in issues)


class TestMaintainability:
    """可维护性维度。"""

    def test_cross_ref_without_precond_triggers_p2(self):
        case = _make_case(steps=["执行 TC_001 后继续操作"])
        issues = check_maintainability(case)
        assert any(i.severity.value == "P2" and "跨用例引用" in i.evidence for i in issues)

    def test_cross_ref_with_precond_no_issue(self):
        case = _make_case(
            steps=["执行 TC_001 后继续操作"],
            preconditions=["依赖 TC_001 执行完成"],
        )
        issues = check_maintainability(case)
        assert not any("跨用例引用" in i.evidence for i in issues)

    def test_absolute_coordinates_triggers_p2(self):
        case = _make_case(steps=["点击坐标 (100, 200)"])
        issues = check_maintainability(case)
        assert any(i.severity.value == "P2" and "绝对坐标" in i.rule for i in issues)


class TestAutomation:
    """可自动化维度。"""

    def test_vague_assert_triggers_p2(self):
        case = _make_case(expected_results="页面显示正确")
        issues = check_automation(case)
        assert any(i.severity.value == "P2" and "模糊断言" in i.rule for i in issues)

    def test_strong_data_dependency_without_mock_triggers_p2(self):
        case = _make_case(
            preconditions=["数据库存在特定用户数据"],
        )
        issues = check_automation(case)
        assert any(i.severity.value == "P2" and "强数据依赖" in i.rule for i in issues)

    def test_strong_data_dependency_with_mock_no_issue(self):
        case = _make_case(
            preconditions=["数据库存在特定用户数据（通过 mock 造数）"],
        )
        issues = check_automation(case)
        assert not any("强数据依赖" in i.rule for i in issues)


class TestTestDataDependency:
    """测试数据依赖维度。"""

    def test_high_cost_data_without_alternative_triggers_p2(self):
        case = _make_case(preconditions=["需要生产环境数据"])
        issues = check_test_data_dependency(case)
        assert any(i.severity.value == "P2" and "高成本造数" in i.rule for i in issues)

    def test_high_cost_data_with_mock_no_issue(self):
        case = _make_case(preconditions=["需要生产环境数据（使用 stub 替代）"])
        issues = check_test_data_dependency(case)
        assert len(issues) == 0


class TestValidateAll:
    """全维度集成校验。"""

    def test_clean_case_set_minimal_issues(self):
        cases = []
        idx = 0
        for i in range(12):
            cases.append(_make_case(
                id=f"TC_{idx:03d}", title=f"正向用例-{idx}", priority=Priority.P0,
                scenario=ScenarioType.POSITIVE, test_point_id=f"TP_{idx:03d}",
            ))
            idx += 1
        for i in range(32):
            cases.append(_make_case(
                id=f"TC_{idx:03d}", title=f"逆向用例-{idx}", priority=Priority.P1,
                scenario=ScenarioType.NEGATIVE, test_point_id=f"TP_{idx:03d}",
            ))
            idx += 1
        for i in range(32):
            cases.append(_make_case(
                id=f"TC_{idx:03d}", title=f"边界用例-{idx}", priority=Priority.P2,
                scenario=ScenarioType.BOUNDARY, test_point_id=f"TP_{idx:03d}",
            ))
            idx += 1
        for i in range(12):
            cases.append(_make_case(
                id=f"TC_{idx:03d}", title=f"异常用例-{idx}", priority=Priority.P3,
                scenario=ScenarioType.EXCEPTION, test_point_id=f"TP_{idx:03d}",
            ))
            idx += 1
        tps = [f"TP_{i:03d}" for i in range(idx)]
        issues = validate_all(_make_set(cases, tps))
        # 干净用例集不应有 P0/P1 问题
        assert not any(i.severity.value == "P0" for i in issues), \
            f"意外 P0: {[i.evidence for i in issues if i.severity.value == 'P0']}"
        assert not any(i.severity.value == "P1" for i in issues), \
            f"意外 P1: {[i.evidence for i in issues if i.severity.value == 'P1']}"

    def test_problematic_case_set_has_issues(self):
        case = _make_case(
            id="TC_bad_001",
            title="登录-等",
            priority=Priority.P0,
            scenario=None,
            steps=["输入 xxx", "点击登录"],
            expected_results="功能正常",
            preconditions=["需要生产环境数据"],
            test_point_id="",
        )
        issues = validate_all(_make_set([case]))
        severities = [i.severity.value for i in issues]
        assert "P0" in severities  # 字段缺失/占位符/溯源
        assert "P1" in severities  # 模糊词/模糊预期
        assert "P2" in severities  # 测试数据依赖
