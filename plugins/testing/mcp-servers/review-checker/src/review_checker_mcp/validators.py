"""确定性校验逻辑（9 用例级维度 + 1 语义一致性维度 = 10 维度）。

将 review-mode.md R2 表的判定规则实现为机器可校验的正则/阈值检查，
不依赖 LLM 推理。每个维度返回 Issue 列表， severity 严格对齐 R2 表。
"""

from __future__ import annotations

import re

from .schemas import (
    Issue,
    ScenarioType,
    SemanticFacts,
    Severity,
    TestCase,
    TestCaseSet,
)

# --- 正则模式（对齐 review-mode.md R2 表） ---

# 可执行性维度：占位符（P0）
PLACEHOLDER_PATTERN = re.compile(
    r"(\bxxx\b|某[个条]|按.{0,4}要求执行|执行对应操作|验证相关功能)"
)

# 可执行性维度：模糊预期（P1）
VAGUE_EXPECTED_PATTERN = re.compile(
    r"(?:结果|功能|配置|页面显示|布局|界面|显示|展示|提示信息|返回)?(?:正确|正常|符合预期|应生效|与测试目标一致)[。.!！\s]*"
)

# 字段规范维度：模糊词（P1）
VAGUE_WORD_PATTERN = re.compile(r"(?:^|[-，、\s])(?:等|之类|正确|正常|类似)(?=$|[-，、\s])")

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

def check_coverage(case_set: TestCaseSet) -> list[Issue]:
    """仅校验需求明确要求的适用场景，不从标题猜测覆盖率。"""
    if case_set.required_scenarios is None:
        return []
    present = {case.scenario for case in case_set.cases if case.scenario is not None}
    missing = set(case_set.required_scenarios) - present
    return [Issue(
        case_id="-", dimension="覆盖度", severity=Severity.P0,
        rule="明确要求的场景类型缺失 → P0", evidence=f"{kind.value} 类型用例为 0 条",
        suggestion=f"补充需求要求的 {kind.value} 场景",
        confirmation="candidate" if any(c.scenario is None for c in case_set.cases) else "confirmed",
    ) for kind in ScenarioType if kind in missing]

def check_priority_balance(case_set: TestCaseSet) -> list[Issue]:
    """比例不代表业务风险，优先级需结合需求人工评估。"""
    return []


def _results(value: str | list[str]) -> list[str]:
    return value.splitlines() if isinstance(value, str) else value


def _expectations(case: TestCase) -> list[str]:
    return _results(case.expected_results) + [
        result for checkpoint in case.checkpoints for result in checkpoint.expected_results
    ]


def _has_content(value: str | list[str]) -> bool:
    items = _results(value)
    return bool(items) and all(item.strip() for item in items)

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
        if not _has_content(value):
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

    for index, checkpoint in enumerate(case.checkpoints, 1):
        if not 1 <= checkpoint.after_step <= len(case.steps):
            issues.append(Issue(
                case_id=case.id, dimension="字段规范", severity=Severity.P0,
                rule="检查点必须引用实际步骤", evidence=f"checkpoints[{index}].after_step={checkpoint.after_step}",
                suggestion="使用从 1 开始且不超过步骤数的编号",
            ))
        if not _has_content(checkpoint.expected_results):
            issues.append(Issue(
                case_id=case.id, dimension="字段规范", severity=Severity.P0,
                rule="检查点结果缺失", evidence=f"checkpoints[{index}].expected_results 为空",
                suggestion="补充可判定的关键检查点结果",
            ))

    if VAGUE_WORD_PATTERN.search(case.title):
        issues.append(
            Issue(
                case_id=case.id,
                dimension="字段规范",
                severity=Severity.P1,
                confirmation="candidate",
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
                    confirmation="candidate",
                    rule=f"标题长度 > {TITLE_LENGTH_GUIDELINE} 字符且未记录例外 → P2",
                    evidence=f"title 长度 {len(case.title)} 字符，notes 未记录例外",
                    suggestion="精简标题或在 notes 记录保留原因（如「场景可区分」「环境标识」）",
                )
            )
    return issues


def check_executability(case: TestCase) -> list[Issue]:
    """可执行性维度（单用例）：占位符 → P0；缺少可判定结果 → P1；步骤数不扣分。"""
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

    for expected in _expectations(case):
        if VAGUE_EXPECTED_PATTERN.fullmatch(expected.strip()):
            issues.append(Issue(
                case_id=case.id, dimension="可执行性", severity=Severity.P1,
                rule="预期仅含模糊结论 → P1", evidence=f"预期缺少可观察结果：{expected}",
                suggestion="描述业务对象、结果及判定证据",
            ))

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
                        confirmation="candidate",
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
                        confirmation="candidate",
                        severity=Severity.P1,
                        rule="steps 前 3 步一致 → P1",
                        evidence=f"用例 {a.id} 与 {b.id} 前 3 步一致",
                        suggestion="核对业务目标、条件与结果，仅等价场景考虑参数化",
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
                    confirmation="candidate",
                    severity=Severity.P2,
                    rule="同测试点用例数 > 3 → P2",
                    evidence=f"测试点 {tp_id} 有 {count} 条用例",
                    suggestion="核对是否覆盖不同业务分支，不按数量删减",
                )
            )
    return issues


def check_traceability(case: TestCase, test_point_ids: list[str]) -> list[Issue]:
    """溯源维度（单用例）：test_point_id 为空或不在清单 → P0。"""
    issues: list[Issue] = []
    if not test_point_ids:
        return issues
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
                    confirmation="candidate",
                    rule="引用绝对坐标/动态 selector → P2",
                    evidence=f"step 含 UI 绝对引用：{UI_ABSOLUTE_PATTERN.search(step).group()}",  # type: ignore[union-attr]
                    suggestion="改用语义化定位（如元素文本/role）",
                )
            )
    return issues


def check_automation(case: TestCase) -> list[Issue]:
    """可自动化维度（单用例）：模糊断言 → P2；强数据依赖未提供造数 → P2。"""
    issues: list[Issue] = []

    assertion = VAGUE_ASSERT_PATTERN.fullmatch("\n".join(_expectations(case)))
    if assertion:
        issues.append(
            Issue(
                case_id=case.id,
                dimension="可自动化",
                severity=Severity.P2,
                rule="模糊断言 → P2",
                evidence=f"expected_results 含模糊断言：{assertion.group()}",  # type: ignore[union-attr]
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
                        confirmation="candidate",
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
                        confirmation="candidate",
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
    """检测单用例抽取事实的直接矛盾，不把不同场景的前置条件当作冲突。"""
    issues: list[Issue] = []
    for fact in facts:
        states: dict[tuple[str, str], set[str]] = {}
        for condition in fact.preconditions:
            states.setdefault((condition.subject, condition.state), set()).add(condition.polarity)
        for (subject, state), polarities in states.items():
            if {"affirmative", "negation"} <= polarities:
                issues.append(Issue(
                    case_id=fact.case_id, dimension="语义一致性", severity=Severity.P0,
                    rule="同一用例对同一事实同时肯定和否定 → P0",
                    evidence=f"{fact.case_id}.preconditions[{subject}={state}] 同时为 affirmative/negation",
                    suggestion="核对原文及抽取结果，修正互斥前置条件",
                ))
    return issues

def check_input_outcome_conflicts(facts: list[SemanticFacts]) -> list[Issue]:
    """相同输入的不同结果仅作为候选；已知上下文不同则不报冲突。"""
    issues: list[Issue] = []
    entries = [(fact, inp) for fact in facts for inp in fact.inputs]
    for i, (a, inp_a) in enumerate(entries):
        for b, inp_b in entries[i + 1:]:
            if inp_a.input_signature != inp_b.input_signature or inp_a.expected_outcome == inp_b.expected_outcome:
                continue
            if a.test_point_id and b.test_point_id and a.test_point_id != b.test_point_id:
                continue
            context_differs = any(a.context[k] != b.context[k] for k in a.context.keys() & b.context.keys())
            states_a = {(p.subject, p.state, p.polarity) for p in a.preconditions if p.polarity != "unknown"}
            states_b = {(p.subject, p.state, p.polarity) for p in b.preconditions if p.polarity != "unknown"}
            if context_differs or (states_a and states_b and states_a != states_b):
                continue
            issues.append(Issue(
                case_id=a.case_id if a.case_id == b.case_id else f"{a.case_id},{b.case_id}",
                dimension="语义一致性", severity=Severity.P1, confirmation="candidate",
                rule="相同输入的预期不同，需核实完整业务上下文",
                evidence=f"{a.case_id}[{inp_a.input_signature}]→{inp_a.expected_outcome} vs {b.case_id}→{inp_b.expected_outcome}",
                suggestion="核对权限、配置、环境、时间条件及需求依据后再确认问题",
            ))
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
                    # 仅当 nbr 在当前 path 中才构成环；
                    # 若 nbr 是前次 DFS 残留的 GRAY（不在 path 中）则跳过
                    if nbr not in path:
                        continue
                    cycle_start_idx = path.index(nbr)
                    cycle = path[cycle_start_idx:] + [nbr]
                    # 将环上节点标记为 BLACK，避免后续 DFS 误判残留 GRAY
                    for n in path[cycle_start_idx:]:
                        color[n] = BLACK
                    return cycle
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


def check_semantic_conflicts(facts: list[SemanticFacts]) -> list[Issue]:
    """第 10 维度：语义一致性。

    输入：skill 侧 LLM 抽取的 SemanticFacts 列表。
    输出：Issue 列表，case_id 形如 "TC_A,TC_B"（冲突对）或
          "TC_A,TC_B,TC_C"（闭环）。

    内部执行 3 类确定性检测：
      - check_precondition_state_conflicts  # 类型 ①
      - check_input_outcome_conflicts       # 类型 ②
      - check_dependency_cycles             # 类型 ③
    """
    issues: list[Issue] = []
    issues.extend(check_precondition_state_conflicts(facts))
    issues.extend(check_input_outcome_conflicts(facts))
    issues.extend(check_dependency_cycles(facts))
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
