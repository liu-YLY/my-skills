"""9 维度确定性校验逻辑。

将 review-mode.md R2 表的判定规则实现为机器可校验的正则/阈值检查，
不依赖 LLM 推理。每个维度返回 Issue 列表， severity 严格对齐 R2 表。
"""

from __future__ import annotations

import re

from .schemas import (
    InputFact,
    Issue,
    PreconditionFact,
    Priority,
    ScenarioType,
    SemanticFacts,
    Severity,
    TestCase,
    TestCaseSet,
)

# --- 正则模式（对齐 review-mode.md R2 表） ---

# 可执行性维度：占位符（P0）
PLACEHOLDER_PATTERN = re.compile(
    r"(xxx|某[个条]?|一些|对应|相应|相关|按.{0,4}要求)"
)

# 可执行性维度：模糊预期（P1）
VAGUE_EXPECTED_PATTERN = re.compile(
    r"(正确|正常|符合预期|功能正常|应生效|与测试目标一致|结果正确|配置正确|对应|相应)"
)

# 字段规范维度：模糊词（P1）
VAGUE_WORD_PATTERN = re.compile(r"(等|之类|正确|正常|类似)")

# 字段规范维度：标题长度软指导阈值（对齐 test-standards.md）
TITLE_LENGTH_GUIDELINE = 40
# 超长标题例外判定关键词（notes 含任一即视为已记录例外）
TITLE_EXCEPTION_KEYWORDS = ("保留", "例外", "超长", "场景可区分", "环境标识", "前置条件", "快速识别")

# 可维护性维度：步骤引用其他用例（P2）
STEP_CROSS_REF_PATTERN = re.compile(r"执行\s*TC[_-]\w+|参考\s*TC[_-]\w+|延续\s*TC[_-]\w+")

# 可维护性维度：UI 绝对坐标/动态 selector（P2）
UI_ABSOLUTE_PATTERN = re.compile(
    r"坐标\s*\(?\d+|xpath\s*=|css_selector\s*=|\.click\(\)|动态\s*selector"
)

# 可自动化维度：模糊断言（P2）
VAGUE_ASSERT_PATTERN = re.compile(r"(页面显示正确|布局正常|界面正常|显示正确|展示正确)")

# 优先级比例指导（对齐 test-standards.md）
PRIORITY_RANGES = {
    Priority.P0: (0.10, 0.15),
    Priority.P1: (0.30, 0.40),
    Priority.P2: (0.30, 0.40),
    Priority.P3: (0.10, 0.15),
}


def check_coverage(case_set: TestCaseSet) -> list[Issue]:
    """覆盖度维度：4 类场景任一为 0 → P0。"""
    issues: list[Issue] = []
    counts = {s: 0 for s in ScenarioType}
    for case in case_set.cases:
        if case.scenario is not None:
            counts[case.scenario] += 1
        else:
            # 无 scenario 字段，按 title 关键词推断
            title = case.title
            if any(k in title for k in ("异常", "错误", "失败", "超时")):
                counts[ScenarioType.NEGATIVE] += 1
            elif any(k in title for k in ("边界", "极限", "空")):
                counts[ScenarioType.BOUNDARY] += 1
            else:
                counts[ScenarioType.POSITIVE] += 1

    for scenario_type, count in counts.items():
        if count == 0:
            issues.append(
                Issue(
                    case_id="-",
                    dimension="覆盖度",
                    severity=Severity.P0,
                    rule="缺失类型判定：4 类场景任一为 0 → P0",
                    evidence=f"{scenario_type.value} 类型用例为 0 条",
                    suggestion=f"补充 {scenario_type.value} 类型用例",
                )
            )
    return issues


def check_priority_balance(case_set: TestCaseSet) -> list[Issue]:
    """优先级合理性维度：各档比例偏离指导区间 → P1。"""
    issues: list[Issue] = []
    total = len(case_set.cases)
    if total == 0:
        return issues

    counts = {p: 0 for p in Priority}
    for case in case_set.cases:
        counts[case.priority] += 1

    for priority, (low, high) in PRIORITY_RANGES.items():
        if priority == Priority.P3 and not case_set.supports_p3:
            continue
        ratio = counts[priority] / total
        if ratio < low or ratio > high:
            issues.append(
                Issue(
                    case_id="-",
                    dimension="优先级合理性",
                    severity=Severity.P1,
                    rule=f"{priority.value} 占比偏离 {low:.0%}~{high:.0%} 区间 → P1",
                    evidence=f"{priority.value} 占比 {ratio:.1%}（{counts[priority]}/{total}）",
                    suggestion=f"调整 {priority.value} 用例数量至 {low:.0%}~{high:.0%} 区间",
                )
            )

    # P0+P1 总和 < 50%
    p0_p1_ratio = (counts[Priority.P0] + counts[Priority.P1]) / total
    if p0_p1_ratio < 0.50:
        issues.append(
            Issue(
                case_id="-",
                dimension="优先级合理性",
                severity=Severity.P1,
                rule="P0+P1 总和 < 50% → P1",
                evidence=f"P0+P1 占比 {p0_p1_ratio:.1%}",
                suggestion="提升核心路径用例占比",
            )
        )
    return issues


def check_field_completeness(case: TestCase) -> list[Issue]:
    """字段规范维度（单用例）：必填字段缺失 → P0；模糊词 → P1。"""
    issues: list[Issue] = []

    required_fields = {
        "ID": case.id,
        "title": case.title,
        "priority": case.priority.value,
        "type": case.type,
        "steps": case.steps,
        "expected_results": case.expected_results,
    }
    for field_name, value in required_fields.items():
        if not value:
            issues.append(
                Issue(
                    case_id=case.id,
                    dimension="字段规范",
                    severity=Severity.P0,
                    rule="必填字段缺失 → P0",
                    evidence=f"{field_name} 为空",
                    suggestion=f"补充 {field_name} 字段",
                )
            )

    if VAGUE_WORD_PATTERN.search(case.title):
        issues.append(
            Issue(
                case_id=case.id,
                dimension="字段规范",
                severity=Severity.P1,
                rule='模糊词命中（"等"/"之类"/"正确"/"正常"/"类似"）→ P1',
                evidence=f"title 含模糊词：{VAGUE_WORD_PATTERN.search(case.title).group()}",  # type: ignore[union-attr]
                suggestion="将 title 改为具体描述",
            )
        )

    # 标题长度软指导（对齐 test-standards.md 超长标题例外判定）
    # 软指导：> 40 字符且未记录例外 → P2；已记录例外（notes 含关键词）→ 不报
    if len(case.title) > TITLE_LENGTH_GUIDELINE:
        has_exception = any(kw in case.notes for kw in TITLE_EXCEPTION_KEYWORDS)
        if not has_exception:
            issues.append(
                Issue(
                    case_id=case.id,
                    dimension="字段规范",
                    severity=Severity.P2,
                    rule=f"标题长度 > {TITLE_LENGTH_GUIDELINE} 字符且未记录例外 → P2",
                    evidence=f"title 长度 {len(case.title)} 字符，notes 未记录例外",
                    suggestion="精简标题或在 notes 记录保留原因（如「场景可区分」「环境标识」）",
                )
            )
    return issues


def check_executability(case: TestCase) -> list[Issue]:
    """可执行性维度（单用例）：占位符 → P0；模糊预期 → P1；步骤 >7 → P2。"""
    issues: list[Issue] = []

    for step in case.steps:
        if PLACEHOLDER_PATTERN.search(step):
            issues.append(
                Issue(
                    case_id=case.id,
                    dimension="可执行性",
                    severity=Severity.P0,
                    rule="占位符命中 → P0",
                    evidence=f"step 含占位符：{PLACEHOLDER_PATTERN.search(step).group()}",  # type: ignore[union-attr]
                    suggestion="替换占位符为具体值",
                )
            )

    if VAGUE_EXPECTED_PATTERN.search(case.expected_results):
        issues.append(
            Issue(
                case_id=case.id,
                dimension="可执行性",
                severity=Severity.P1,
                rule="模糊预期命中 → P1",
                evidence=f"expected_results 含模糊词：{VAGUE_EXPECTED_PATTERN.search(case.expected_results).group()}",  # type: ignore[union-attr]
                suggestion="改为可验证的具体预期",
            )
        )

    if len(case.steps) > 7:
        issues.append(
            Issue(
                case_id=case.id,
                dimension="可执行性",
                severity=Severity.P2,
                rule="步骤数 > 7 → P2",
                evidence=f"步骤数 {len(case.steps)}",
                suggestion="拆分为多条用例或合并步骤",
            )
        )
    return issues


def check_redundancy(case_set: TestCaseSet) -> list[Issue]:
    """冗余维度：title 相同或 steps 前 3 步一致 → P1；同测试点 >3 → P2。"""
    issues: list[Issue] = []
    cases = case_set.cases

    # title 相同或 steps 前 3 步一致
    for i, a in enumerate(cases):
        for b in cases[i + 1 :]:
            if a.title == b.title:
                issues.append(
                    Issue(
                        case_id=f"{a.id},{b.id}",
                        dimension="冗余",
                        severity=Severity.P1,
                        rule="title 相同 → P1",
                        evidence=f"用例 {a.id} 与 {b.id} title 相同",
                        suggestion="合并或区分标题",
                    )
                )
            elif a.steps[:3] == b.steps[:3] and len(a.steps) >= 3:
                issues.append(
                    Issue(
                        case_id=f"{a.id},{b.id}",
                        dimension="冗余",
                        severity=Severity.P1,
                        rule="steps 前 3 步一致 → P1",
                        evidence=f"用例 {a.id} 与 {b.id} 前 3 步一致",
                        suggestion="合并为参数化用例",
                    )
                )

    # 同测试点用例数 > 3
    tp_counts: dict[str, int] = {}
    for case in cases:
        if case.test_point_id:
            tp_counts[case.test_point_id] = tp_counts.get(case.test_point_id, 0) + 1
    for tp_id, count in tp_counts.items():
        if count > 3:
            issues.append(
                Issue(
                    case_id="-",
                    dimension="冗余",
                    severity=Severity.P2,
                    rule="同测试点用例数 > 3 → P2",
                    evidence=f"测试点 {tp_id} 有 {count} 条用例",
                    suggestion="精简同测试点用例",
                )
            )
    return issues


def check_traceability(case: TestCase, test_point_ids: list[str]) -> list[Issue]:
    """溯源维度（单用例）：test_point_id 为空或不在清单 → P0。"""
    issues: list[Issue] = []
    if not case.test_point_id:
        issues.append(
            Issue(
                case_id=case.id,
                dimension="溯源",
                severity=Severity.P0,
                rule="test_point_id 为空 → P0",
                evidence="test_point_id 字段为空",
                suggestion="补充对应测试点 ID",
            )
        )
    elif test_point_ids and case.test_point_id not in test_point_ids:
        issues.append(
            Issue(
                case_id=case.id,
                dimension="溯源",
                severity=Severity.P0,
                rule="test_point_id 不在测试点清单中 → P0",
                evidence=f"test_point_id={case.test_point_id} 不在清单中",
                suggestion="核对需求，修正测试点 ID",
            )
        )
    return issues


def check_maintainability(case: TestCase) -> list[Issue]:
    """可维护性维度（单用例）：步骤跨引用未声明依赖 → P2；UI 绝对坐标 → P2。"""
    issues: list[Issue] = []
    precond_str = " ".join(case.preconditions)

    for step in case.steps:
        match = STEP_CROSS_REF_PATTERN.search(step)
        if match:
            # 提取引用的用例 ID（如 TC_001）检查是否在 preconditions 中声明
            ref_id = re.search(r"TC[_-]\w+", match.group())
            if ref_id and ref_id.group() not in precond_str:
                issues.append(
                    Issue(
                        case_id=case.id,
                        dimension="可维护性",
                        severity=Severity.P2,
                        rule="步骤引用其他用例但未在 preconditions 声明依赖 → P2",
                        evidence=f"step 含跨用例引用：{match.group()}，preconditions 未声明",
                        suggestion="在 preconditions 声明依赖或改为自包含步骤",
                    )
                )
        if UI_ABSOLUTE_PATTERN.search(step):
            issues.append(
                Issue(
                    case_id=case.id,
                    dimension="可维护性",
                    severity=Severity.P2,
                    rule="引用绝对坐标/动态 selector → P2",
                    evidence=f"step 含 UI 绝对引用：{UI_ABSOLUTE_PATTERN.search(step).group()}",  # type: ignore[union-attr]
                    suggestion="改用语义化定位（如元素文本/role）",
                )
            )
    return issues


def check_automation(case: TestCase) -> list[Issue]:
    """可自动化维度（单用例）：模糊断言 → P2；强数据依赖未提供造数 → P2。"""
    issues: list[Issue] = []

    if VAGUE_ASSERT_PATTERN.search(case.expected_results):
        issues.append(
            Issue(
                case_id=case.id,
                dimension="可自动化",
                severity=Severity.P2,
                rule="模糊断言 → P2",
                evidence=f"expected_results 含模糊断言：{VAGUE_ASSERT_PATTERN.search(case.expected_results).group()}",  # type: ignore[union-attr]
                suggestion="改为可自动化断验的具体描述",
            )
        )

    for precond in case.preconditions:
        if any(k in precond for k in ("数据库", "生产环境", "特定用户", "第三方")):
            if not any(k in precond for k in ("mock", "Mock", "替代", "fixture")):
                issues.append(
                    Issue(
                        case_id=case.id,
                        dimension="可自动化",
                        severity=Severity.P2,
                        rule="强数据依赖未提供造数方式 → P2",
                        evidence=f"precondition 要求特定数据但无 mock：{precond}",
                        suggestion="提供 mock 或 fixture 造数方式",
                    )
                )
    return issues


def check_test_data_dependency(case: TestCase) -> list[Issue]:
    """测试数据依赖维度（单用例）：高成本造数无替代 → P2。"""
    issues: list[Issue] = []
    for precond in case.preconditions:
        if any(k in precond for k in ("生产环境", "特定权限", "第三方系统")):
            if not any(k in precond for k in ("mock", "Mock", "替代", "stub")):
                issues.append(
                    Issue(
                        case_id=case.id,
                        dimension="测试数据依赖",
                        severity=Severity.P2,
                        rule="高成本造数无替代方案 → P2",
                        evidence=f"precondition 要求高成本数据：{precond}",
                        suggestion="提供 mock/stub 替代方案",
                    )
                )
    return issues


def _extract_module_function_segment(case_id: str) -> str:
    """从 case_id 提取模块+功能段。

    如 TC_WEBHOOK_ADD_001 → WEBHOOK_ADD
    若无法提取（格式不符 TC_{模块}_{功能}_{序号}），返回 "unknown"。
    """
    parts = case_id.split("_")
    if len(parts) >= 4 and parts[0] == "TC":
        # TC_{模块}_{功能}_{序号} → 模块+功能段（去掉 TC 前缀和序号）
        return "_".join(parts[1:-1])
    return "unknown"


def check_precondition_state_conflicts(facts: list[SemanticFacts]) -> list[Issue]:
    """冲突类型 ①：前置条件状态矛盾。

    同 test_point_id 分组内（无 test_point_id 时按 case_id 模块+功能段分组），
    存在两条用例的 PreconditionFact.subject 相同，但 state 不同且 polarity
    互为肯定/否定 → P0。
    """
    issues: list[Issue] = []

    # 分组：优先用 test_point_id，无则用模块+功能段
    groups: dict[str, list[SemanticFacts]] = {}
    for fact in facts:
        if fact.test_point_id:
            group_key = fact.test_point_id
        else:
            group_key = _extract_module_function_segment(fact.case_id)
        groups.setdefault(group_key, []).append(fact)

    for group_key, group_facts in groups.items():
        if len(group_facts) < 2:
            continue
        # 收集组内所有 (case_id, PreconditionFact)
        entries: list[tuple[str, PreconditionFact]] = []
        for f in group_facts:
            for pc in f.preconditions:
                entries.append((f.case_id, pc))

        # 两两比对
        for i, (case_a, pc_a) in enumerate(entries):
            for case_b, pc_b in entries[i + 1 :]:
                if case_a == case_b:
                    continue
                if (
                    pc_a.subject == pc_b.subject
                    and pc_a.state != pc_b.state
                    and pc_a.polarity != pc_b.polarity
                ):
                    issues.append(
                        Issue(
                            case_id=f"{case_a},{case_b}",
                            dimension="语义一致性",
                            severity=Severity.P0,
                            rule="同分组内 subject 相同且 polarity 互斥 → P0",
                            evidence=(
                                f"{case_a}.preconditions[{pc_a.subject}={pc_a.state}] "
                                f"vs {case_b}.preconditions[{pc_b.subject}={pc_b.state}]"
                            ),
                            suggestion="核对场景归属：若属不同测试场景则拆分 test_point_id；若属同场景则修正其中一条的前置条件",
                        )
                    )
    return issues


def check_input_outcome_conflicts(facts: list[SemanticFacts]) -> list[Issue]:
    """冲突类型 ②：同输入不同预期。

    全用例集范围内，用例 A 的任一 InputFact 与用例 B 的任一 InputFact 的
    input_signature 完全相同，但 expected_outcome 不同 → P0。
    支持参数化用例的多 InputFact 笛卡尔比对。
    """
    issues: list[Issue] = []

    # 收集所有 (case_id, InputFact)
    entries: list[tuple[str, InputFact]] = []
    for fact in facts:
        for inp in fact.inputs:
            entries.append((fact.case_id, inp))

    # 两两比对（不同 case_id 之间）
    for i, (case_a, inp_a) in enumerate(entries):
        for case_b, inp_b in entries[i + 1 :]:
            if case_a == case_b:
                continue
            if (
                inp_a.input_signature == inp_b.input_signature
                and inp_a.expected_outcome != inp_b.expected_outcome
            ):
                issues.append(
                    Issue(
                        case_id=f"{case_a},{case_b}",
                        dimension="语义一致性",
                        severity=Severity.P0,
                        rule="input_signature 相同且 expected_outcome 不同 → P0",
                        evidence=(
                            f"{case_a}[{inp_a.input_signature}]→{inp_a.expected_outcome} "
                            f"vs {case_b}[{inp_b.input_signature}]→{inp_b.expected_outcome}"
                        ),
                        suggestion="核对预期：同一输入应有唯一预期，修正其中一条的 expected_outcome",
                    )
                )
    return issues


def check_dependency_cycles(facts: list[SemanticFacts]) -> list[Issue]:
    """冲突类型 ③：数据依赖闭环。

    构建 case_id → dependencies 有向图，DFS 检测环 → P1。
    case_id 形如 "TC_A,TC_B,TC_C"（闭环路径）。
    """
    issues: list[Issue] = []

    # 构建邻接表
    graph: dict[str, list[str]] = {f.case_id: list(f.dependencies) for f in facts}

    # DFS 检测环（迭代实现，避免深递归栈溢出）
    WHITE, GRAY, BLACK = 0, 1, 2  # 未访问 / 访问中 / 已完成
    color: dict[str, int] = {node: WHITE for node in graph}

    detected_cycles: list[list[str]] = []

    def _find_cycle_from(start: str) -> list[str] | None:
        """从 start 出发找环，返回环路径或 None。"""
        stack: list[tuple[str, list[str]]] = [(start, [start])]
        # 标记 start 为 GRAY（在栈中）
        color[start] = GRAY
        while stack:
            node, path = stack[-1]
            neighbors = graph.get(node, [])
            found_next = False
            for nbr in neighbors:
                if nbr not in graph:
                    continue  # 依赖的 case_id 不在用例集中，跳过
                if color.get(nbr, WHITE) == GRAY:
                    # 找到环：从 path 中 nbr 的位置到当前节点
                    cycle_start_idx = path.index(nbr)
                    return path[cycle_start_idx:] + [nbr]
                if color.get(nbr, WHITE) == WHITE:
                    color[nbr] = GRAY
                    stack.append((nbr, path + [nbr]))
                    found_next = True
                    break
            if not found_next:
                color[node] = BLACK
                stack.pop()
        return None

    for node in graph:
        if color[node] == WHITE:
            cycle = _find_cycle_from(node)
            if cycle:
                detected_cycles.append(cycle)

    for cycle in detected_cycles:
        # 去掉末尾重复的起点（path + [nbr] 导致末尾重复）
        if len(cycle) > 1 and cycle[0] == cycle[-1]:
            cycle = cycle[:-1]
        cycle_str = ",".join(cycle)
        arrow_path = "→".join(cycle)
        issues.append(
            Issue(
                case_id=cycle_str,
                dimension="语义一致性",
                severity=Severity.P1,
                rule="dependencies 有向图存在环 → P1",
                evidence=f"依赖闭环：{arrow_path}→{cycle[0]}",
                suggestion="拆解闭环：将其中一条依赖改为自包含步骤，或重新排序执行顺序",
            )
        )
    return issues


def validate_all(case_set: TestCaseSet) -> list[Issue]:
    """执行全部 9 维度校验，返回所有 Issue。"""
    issues: list[Issue] = []

    # 集合级维度
    issues.extend(check_coverage(case_set))
    issues.extend(check_priority_balance(case_set))
    issues.extend(check_redundancy(case_set))

    # 单用例级维度
    for case in case_set.cases:
        issues.extend(check_field_completeness(case))
        issues.extend(check_executability(case))
        issues.extend(check_traceability(case, case_set.test_point_ids))
        issues.extend(check_maintainability(case))
        issues.extend(check_automation(case))
        issues.extend(check_test_data_dependency(case))

    return issues
