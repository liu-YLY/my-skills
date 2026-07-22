"""server.py 工具函数单元测试。"""

from __future__ import annotations

import subprocess
import sys

from review_checker_mcp.schemas import (
    Priority,
    ScenarioType,
    TestCase,
    TestCaseSet,
)
from review_checker_mcp.server import (
    DIMENSIONS,
    _register_mcp_tools,
    generate_report,
    review_test_cases,
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
    )


def _make_clean_set() -> TestCaseSet:
    """构造一个干净的用例集（无 P0/P1 问题）。"""
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
    return TestCaseSet(cases=cases, test_point_ids=tps)


class TestReviewTestCases:
    """review_test_cases 工具。"""

    def test_returns_issues_for_problematic_case(self):
        case = _make_case(
            id="TC_bad_001",
            title="登录-等",
            steps=["输入 xxx"],
            expected_results="功能正常",
            test_point_id="",
        )
        case_set = TestCaseSet(cases=[case], test_point_ids=["TP_001"])
        issues = review_test_cases(case_set)
        assert len(issues) > 0
        severities = [i.severity.value for i in issues]
        assert "P0" in severities

    def test_returns_empty_for_clean_case(self):
        case_set = _make_clean_set()
        issues = review_test_cases(case_set)
        p0_p1 = [i for i in issues if i.severity.value in ("P0", "P1")]
        assert len(p0_p1) == 0


class TestGenerateReport:
    """generate_report 工具。"""

    def test_clean_set_gets_grade_a_or_b(self):
        case_set = _make_clean_set()
        report = generate_report(case_set)
        assert report.grade in ("A", "B")
        assert report.total_cases == 88
        assert report.pass_rate > 0.80

    def test_problematic_set_gets_low_grade(self):
        case = _make_case(
            id="TC_bad_001",
            title="登录-等",
            steps=["输入 xxx"],
            expected_results="功能正常",
            test_point_id="",
        )
        case_set = TestCaseSet(cases=[case], test_point_ids=["TP_001"])
        report = generate_report(case_set)
        assert report.grade in ("C", "D")
        assert report.total_issues > 0
        assert report.issue_density > 0

    def test_dimension_stats_cover_all_nine(self):
        case_set = _make_clean_set()
        report = generate_report(case_set)
        assert len(report.dimension_stats) == 9
        dims = [s.dimension for s in report.dimension_stats]
        assert dims == DIMENSIONS

    def test_severity_stats_has_p0_p1_p2(self):
        case = _make_case(
            id="TC_bad_001",
            title="登录-等",
            steps=["输入 xxx"] * 8,
            expected_results="功能正常",
            test_point_id="",
            preconditions=["需要生产环境数据"],
        )
        case_set = TestCaseSet(cases=[case], test_point_ids=["TP_001"])
        report = generate_report(case_set)
        assert "P0" in report.severity_stats
        assert "P1" in report.severity_stats
        assert "P2" in report.severity_stats
        assert report.severity_stats["P0"] > 0
        assert report.severity_stats["P1"] > 0

    def test_empty_case_set(self):
        case_set = TestCaseSet(cases=[], test_point_ids=[])
        report = generate_report(case_set)
        assert report.total_cases == 0
        assert report.pass_rate == 0.0
        assert report.grade == "D"

    def test_accepts_precomputed_issues(self):
        case_set = _make_clean_set()
        issues = review_test_cases(case_set)
        report = generate_report(case_set, issues=issues)
        # 传入预计算 issues 应与自动计算结果一致
        assert report.total_issues == len(issues)


class TestGradeThresholds:
    """评级阈值边界测试。"""

    def test_grade_a_requires_both_conditions(self):
        # 通过率≥95% 但 问题密度≥0.5 → 不应是 A
        cases = []
        for i in range(20):
            cases.append(_make_case(
                id=f"TC_{i:03d}", title=f"用例-{i}",
                priority=Priority.P1, scenario=ScenarioType.POSITIVE,
                test_point_id=f"TP_{i:03d}",
            ))
        # 1 条有问题（通过率 95%），但制造多个 P2 问题使密度≥0.5
        cases[0] = _make_case(
            id="TC_000", title="用例-0", priority=Priority.P1,
            scenario=ScenarioType.POSITIVE, test_point_id="TP_000",
            steps=[f"步骤-{i}" for i in range(8)],  # 步骤>7 → P2
            preconditions=["需要生产环境数据"],  # 测试数据依赖 → P2
        )
        case_set = TestCaseSet(cases=cases, test_point_ids=[f"TP_{i:03d}" for i in range(20)])
        report = generate_report(case_set)
        # 通过率 95% 但问题密度可能≥0.5，不应是 A
        if report.issue_density >= 0.5:
            assert report.grade != "A"


class TestRegisterMcpTools:
    """_register_mcp_tools 安全降级。"""

    def test_returns_none_without_mcp_sdk(self, monkeypatch):
        # mcp SDK 不可用时，_register_mcp_tools 应安全返回 None，不抛异常
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name.startswith("mcp"):
                raise ImportError("simulated: mcp not installed")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        class DummyServer:
            def tool(self):
                def decorator(func):
                    return func
                return decorator

        # 应直接 return（不抛异常）
        result = _register_mcp_tools(DummyServer())
        assert result is None


class TestMainCli:
    """main() 命令行入口。"""

    def test_help_tools_prints_tools_and_exits_zero(self, capsys):
        from review_checker_mcp.server import main

        # 模拟 --help-tools 参数
        sys.argv = ["review-checker-mcp", "--help-tools"]
        try:
            rc = main()
        except SystemExit as e:
            rc = e.code
        captured = capsys.readouterr()
        assert rc == 0
        assert "2 工具" in captured.out
        assert "review_test_cases" in captured.out
        assert "generate_report" in captured.out

    def test_http_transport_returns_one(self, capsys):
        from review_checker_mcp.server import main

        sys.argv = ["review-checker-mcp", "--transport", "http"]
        try:
            rc = main()
        except SystemExit as e:
            rc = e.code
        captured = capsys.readouterr()
        # HTTP 待 v0.3.0，应拒绝并打印提示
        assert rc == 1
        assert "HTTP" in captured.err or "v0.3.0" in captured.err


class TestIncrementalReviewScenarios:
    """增量评审场景下的 generate_report 行为。

    增量评审典型场景：变更用例数少（1-5 条），需要正确计算评级与密度。
    review-mode.md 增量评审子模式要求「用例总数 = 变更用例数」。
    """

    def test_single_clean_changed_case_pass_rate_one(self):
        # 增量评审：1 条变更用例且无字段问题 → pass_rate == 1.0
        # 注意：单条用例会触发覆盖度 P0（缺其他 3 类场景），但覆盖度问题 case_id="-"
        # 不计入 issue_cases，故 pass_rate 仍为 1.0；但 issue_density > 0 → 评级非 A
        case = _make_case(id="TC_001", title="登录-正向", test_point_id="TP_001")
        case_set = TestCaseSet(cases=[case], test_point_ids=["TP_001"])
        report = generate_report(case_set)
        assert report.total_cases == 1
        assert report.pass_rate == 1.0
        assert report.issue_cases == 0
        # 覆盖度 P0 存在但 case_id="-"，不影响 pass_rate
        assert report.issue_density > 0  # 覆盖度问题使密度 > 0
        assert report.grade == "B"  # pass_rate 100% 但密度高 → B 非 A

    def test_single_problematic_changed_case_gets_low_grade(self):
        # 增量评审：1 条变更用例且有问题 → D 级（通过率 0%）
        case = _make_case(
            id="TC_001", title="登录-等", steps=["输入 xxx"],
            expected_results="功能正常", test_point_id="",
        )
        case_set = TestCaseSet(cases=[case], test_point_ids=["TP_001"])
        report = generate_report(case_set)
        assert report.total_cases == 1
        assert report.pass_rate == 0.0
        assert report.grade == "D"
        assert report.issue_density > 0

    def test_small_batch_mixed_cases_grade(self):
        # 增量评审：5 条变更用例，3 条干净 2 条有问题 → 通过率 60% → C 级
        cases = []
        for i in range(3):
            cases.append(_make_case(
                id=f"TC_{i:03d}", title=f"正向用例-{i}",
                test_point_id=f"TP_{i:03d}",
            ))
        # 2 条有问题
        cases.append(_make_case(
            id="TC_003", title="登录-等", steps=["输入 xxx"],
            expected_results="功能正常", test_point_id="TP_003",
        ))
        cases.append(_make_case(
            id="TC_004", title="登录-之类", steps=["输入 某个"],
            expected_results="结果正确", test_point_id="TP_004",
        ))
        tps = [f"TP_{i:03d}" for i in range(5)]
        case_set = TestCaseSet(cases=cases, test_point_ids=tps)
        report = generate_report(case_set)
        assert report.total_cases == 5
        assert report.issue_cases == 2
        assert report.pass_rate == 0.6
        assert report.grade == "C"

    def test_incremental_report_has_full_dimension_stats(self):
        # 增量评审报告仍应包含全部 9 维度统计（即使多数为 0）
        case = _make_case(id="TC_001", title="登录-正向", test_point_id="TP_001")
        case_set = TestCaseSet(cases=[case], test_point_ids=["TP_001"])
        report = generate_report(case_set)
        assert len(report.dimension_stats) == 9
        # 单条干净用例不应有覆盖度问题（因为只有 1 条正向，其他 3 类为 0 → P0）
        # 实际上单条用例会触发覆盖度 P0，验证 dimension_stats 正确反映
        coverage_stat = next(s for s in report.dimension_stats if s.dimension == "覆盖度")
        assert coverage_stat.issue_count > 0


class TestMcpIntegration:
    """MCP 工具端到端集成测试。

    验证 review_test_cases → generate_report 链路一致性，
    以及预计算 issues 与自动计算结果一致。
    """

    def test_precomputed_issues_match_auto_computed(self):
        # 预计算 issues 传入 generate_report，应与自动计算结果一致
        case_set = _make_clean_set()
        auto_report = generate_report(case_set)
        precomputed_issues = review_test_cases(case_set)
        manual_report = generate_report(case_set, issues=precomputed_issues)
        assert auto_report.total_issues == manual_report.total_issues
        assert auto_report.pass_rate == manual_report.pass_rate
        assert auto_report.issue_density == manual_report.issue_density
        assert auto_report.grade == manual_report.grade

    def test_dimension_stats_consistent_with_issues(self):
        # dimension_stats 的 issue_count 应与 issues 列表按维度分组计数一致
        case = _make_case(
            id="TC_001", title="登录-等", steps=["输入 xxx", "输入 yyy"],
            expected_results="功能正常", test_point_id="",
            preconditions=["需要生产环境数据"],
        )
        case_set = TestCaseSet(cases=[case], test_point_ids=["TP_001"])
        issues = review_test_cases(case_set)
        report = generate_report(case_set, issues=issues)
        from collections import Counter
        dim_counts = Counter(i.dimension for i in issues)
        for stat in report.dimension_stats:
            assert stat.issue_count == dim_counts.get(stat.dimension, 0), \
                f"维度 {stat.dimension} 统计不一致"

    def test_severity_stats_consistent_with_issues(self):
        # severity_stats 应与 issues 列表按严重等级计数一致
        case = _make_case(
            id="TC_001", title="登录-等", steps=["输入 xxx"] * 8,
            expected_results="功能正常", test_point_id="",
            preconditions=["需要生产环境数据"],
        )
        case_set = TestCaseSet(cases=[case], test_point_ids=["TP_001"])
        issues = review_test_cases(case_set)
        report = generate_report(case_set, issues=issues)
        from collections import Counter
        sev_counts = Counter(i.severity.value for i in issues)
        for sev in ("P0", "P1", "P2"):
            assert report.severity_stats[sev] == sev_counts.get(sev, 0), \
                f"严重等级 {sev} 统计不一致"

    def test_issue_cases_count_matches_unique_case_ids(self):
        # issue_cases 应等于有问题的唯一用例 ID 数（排除 case_id="-" 的集合级问题）
        cases = [
            _make_case(id="TC_001", title="登录-等", test_point_id="TP_001"),
            _make_case(id="TC_002", title="登录-之类", test_point_id="TP_002"),
            _make_case(id="TC_003", title="登录成功-跳转首页", test_point_id="TP_003"),
        ]
        case_set = TestCaseSet(cases=cases, test_point_ids=["TP_001", "TP_002", "TP_003"])
        report = generate_report(case_set)
        # TC_001 和 TC_002 有字段规范 P1 问题，TC_003 无字段问题
        # 注意：覆盖度/优先级问题 case_id="-" 不计入 issue_cases
        assert report.issue_cases == 2
        assert report.total_cases == 3
        assert report.pass_rate == round(1 / 3, 4)  # pass_rate round 到 4 位小数
