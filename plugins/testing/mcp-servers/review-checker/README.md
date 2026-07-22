# Review Checker MCP Server

> 配套 test-case-engineer 评审模式的 Python MCP Server v0.1.0：提供 9 维度确定性校验，作为 skill 的可选增强引擎。

> **实现状态**：v0.1.0 已完成 pydantic Schema + 9 维度确定性校验逻辑 + 单元测试（29 通过，覆盖率 97.3%）。MCP 协议层注册待 v0.2.0。

## 简介

本 MCP Server 是 testing-bundle v3.1.0 的配套组件，位于 `plugins/testing/mcp-servers/review-checker/`。

**本质**：将 review-mode.md R2 表的 9 维度判定规则实现为机器可校验的正则/阈值检查，不依赖 LLM 推理这些本该确定的事。

**与 skill 的关系**：
- skill 是主，Server 是复核器（Server 校验失败不影响 skill 输出）
- skill 独立可用，未安装 Server 时降级为纯 LLM 推理
- 安装 Server 后 skill 进入"增强模式"，获得确定性 9 维度校验

## 9 维度校验

| 维度 | 检查点 | 严重等级 | 校验方式 |
|---|---|---|---|
| 覆盖度 | 4 类场景齐全 | P0 | scenario 字段统计 / title 关键词推断 |
| 优先级合理性 | P0/P1/P2/P3 比例 | P1 | 比例区间阈值（对齐 test-standards.md） |
| 字段规范 | 必填字段 + 模糊词 | P0/P1 | 字段非空 + 正则匹配 |
| 可执行性 | 占位符 + 模糊预期 + 步骤数 | P0/P1/P2 | 正则匹配 + 步骤计数 |
| 冗余 | 重复用例 + 同测试点 | P1/P2 | title/steps 比对 + 测试点计数 |
| 溯源 | 孤儿用例 | P0 | test_point_id 存在性校验 |
| 可维护性 | 步骤耦合 + UI 引用 | P2 | 跨引用正则 + 坐标正则 |
| 可自动化 | 断言模糊 + 数据依赖 | P2 | 模糊断言正则 + 造数关键词 |
| 测试数据依赖 | 高成本造数 | P2 | 生产环境关键词 + mock 检测 |

## 使用方式

### v0.1.0（直接 Python 调用）

```python
from review_checker_mcp.schemas import TestCase, TestCaseSet, Priority, ScenarioType
from review_checker_mcp.validators import validate_all

case_set = TestCaseSet(cases=[...], test_point_ids=[...])
issues = validate_all(case_set)
for issue in issues:
    print(f"{issue.case_id} {issue.dimension} {issue.severity.value}: {issue.evidence}")
```

### v0.2.0（MCP 协议，待实现）

```python
# 通过 MCP 协议调用，待 v0.2.0 实现
@mcp.tool()
def review_test_cases(case_set: TestCaseSet) -> ReviewReport: ...
```

## 技术栈

| 项 | 选择 | 理由 |
|---|---|---|
| 语言 | Python 3.11+ | 与 state-machine-testing MCP Server 一致 |
| Schema 校验 | pydantic v2 | 类型安全、错误信息详细 |
| 测试 | pytest + pytest-cov | 覆盖率门槛 90%（实测 97.3%） |
| MCP SDK | mcp>=0.9.0 | v0.2.0 协议层注册使用 |
