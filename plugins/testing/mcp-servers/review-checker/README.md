# Review Checker MCP Server

> 配套 test-case-engineer 评审模式的 Python MCP Server v0.3.0：提供 10 维度确定性校验与度量报告（9 用例级 + 1 语义一致性），作为 skill 的可选增强引擎。

> **实现状态**：已实现 3 个工具及 stdio 协议；当前报告区分确定问题、候选线索及未评估范围。

## 简介

本 MCP Server 是 testing-bundle 的配套组件，位于 `plugins/testing/mcp-servers/review-checker/`。

**本质**：将 review-mode.md R2 表的 10 维度判定规则实现为机器可校验的正则/阈值检查，不依赖 LLM 推理这些本该确定的事。

**与 skill 的关系**：
- skill 是主，Server 是复核器（Server 校验失败不影响 skill 输出）
- skill 独立可用，未安装 Server 时降级为纯 LLM 推理
- 安装 Server 后 skill 进入"增强模式"，获得确定性 10 维度校验

## 评审规则与输入契约

业务编写原则以 [writing-rules.md](../../skills/test-case-engineer/knowledge/writing-rules.md) 为准；评审判定以 [review-mode.md](../../skills/test-case-engineer/knowledge/review-mode.md) 为准。

- `expected_results` 接受字符串或字符串数组，新用例用数组；`checkpoints` 为可选列表，每项含从 1 开始的 `after_step` 和结果数组。校验实际步骤引用，不检查步骤／结果数量相等。
- `required_scenarios` 仅填写需求明确适用的场景；缺少覆盖和测试点基线时报告未评估。优先级根据业务风险人工判断，不按占比扣分。
- `Issue.confirmation` 为 `confirmed` 或 `candidate`；重复标题、相同步骤等启发式线索不直接认定问题。
- `SemanticFacts.context` 保留权限、配置等条件，前置条件极性不明时用 `unknown`；不同业务条件不能当作确定冲突。

## 工具集（3 个）

| 工具名 | 用途 | 输入 | 输出 | 是否调 LLM |
|---|---|---|---|---|
| `review_test_cases` | 对用例集执行 9 维度用例级评审 | TestCaseSet | list[Issue] | 否 |
| `check_semantic_conflicts` | 第 10 维度语义一致性冲突检测 | list[SemanticFacts] | list[Issue] | 否（facts 由 skill 侧 LLM 抽取） |
| `generate_report` | 基于评审结果生成度量报告 | TestCaseSet（+可选预计算 issues） | ReviewReport | 否 |

### 工具签名

```python
@mcp.tool()
def review_test_cases(case_set: TestCaseSet) -> list[Issue]: ...

@mcp.tool()
def check_semantic_conflicts(facts: list[SemanticFacts]) -> list[Issue]: ...

@mcp.tool()
def generate_report(case_set: TestCaseSet, issues: list[Issue] | None = None, semantic_reviewed: bool = False) -> ReviewReport: ...
```

`generate_report` 保留原统计，增加 `candidate_issues`、`assessed_dimensions` 和 `not_assessed`；候选问题不计扣分或通过率。空集合评级为“未评估”，通过率为 null。

> **调用顺序**：skill 先调 `review_test_cases` 获取 9 维度 Issue → LLM 抽取 SemanticFacts → 调 `check_semantic_conflicts` 获取第 10 维度 Issue → 合并全部 Issue 传入 `generate_report`。

**评级阈值**（仅适用于已评估范围）：
- 存在任何已确认 P0（包括集合级问题）时直接为 D；无 P0 时再按以下阈值计算
- A: 通过率 ≥ 95% 且 问题密度 < 0.5
- B: 通过率 ≥ 80%
- C: 通过率 ≥ 60%
- D: 通过率 < 60%

## 使用方式

### 直接 Python 调用（库模式）

```python
from review_checker_mcp.schemas import TestCase, TestCaseSet, Priority, ScenarioType, SemanticFacts
from review_checker_mcp.server import review_test_cases, check_semantic_conflicts, generate_report

case_set = TestCaseSet(cases=[...], test_point_ids=[...])

# 1. 9 维度用例级校验
issues = review_test_cases(case_set)

# 2. 第 10 维度语义一致性（facts 由 skill 侧 LLM 抽取后传入）
facts: list[SemanticFacts] = [...]  # LLM 抽取，详见 skill 的 prompt-strategy.md
issues += check_semantic_conflicts(facts)

for issue in issues:
    print(f"{issue.case_id} {issue.dimension} {issue.severity.value}: {issue.evidence}")

# 3. 合并后生成度量报告
report = generate_report(case_set, issues, semantic_reviewed=True)
print(f"评级: {report.grade} 通过率: {report.pass_rate} 问题密度: {report.issue_density}")
```

### MCP 协议（stdio）

```bash
# 启动 stdio 传输
python -m review_checker_mcp.server --transport stdio

# 查看工具帮助
python -m review_checker_mcp.server --help-tools
```

Host 侧配置 MCP 客户端指向本 Server 后，可通过 MCP 协议调用 `review_test_cases` / `check_semantic_conflicts` / `generate_report` 工具。

### 安全降级

- 未安装 `mcp` SDK → `_register_mcp_tools` 静默返回，模块仍可作为普通 Python 库使用
- 已安装 `mcp` SDK 但 Server API 不兼容（无 `.tool()` 装饰器）→ 静默返回，不影响库模式调用
- 当前仅支持 stdio，尚未实现 HTTP 传输

## 技术栈

| 项 | 选择 | 理由 |
|---|---|---|
| 语言 | Python 3.11+ | 与 state-machine-testing MCP Server 一致 |
| Schema 校验 | pydantic v2 | 类型安全、错误信息详细 |
| 测试 | pytest + pytest-cov | 功能测试与 stdio 冒烟进入 CI |
| MCP SDK | mcp>=0.9.0,<2.0.0 | v0.2.0 协议层注册使用 |

## 版本历史

- v0.3.0: 业务结果与关键检查点输入、候选问题分离、P0 评级否决及评审范围披露

- v0.1.0: 首版，9 维度确定性校验逻辑（validators）+ pydantic Schema + 单元测试
- v0.2.0: 新增 MCP 协议层注册（review_test_cases / check_semantic_conflicts / generate_report 3 工具）+ 第 10 维度语义一致性冲突检测 + 度量报告（通过率/问题密度/评级/10 维度分布/严重等级分布）+ main CLI 入口（--transport/--help-tools）

## 待后续版本

- HTTP 传输支持（未排期）
- v0.4.0: 增量评审模式（基于 git diff 仅校验变更用例）
- v0.5.0: 历史报告对比（趋势分析）
