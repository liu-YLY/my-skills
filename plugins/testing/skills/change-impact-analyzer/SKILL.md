---
name: change-impact-analyzer
version: 1.2.1
description: >-
  Analyzes git changes against test cases to find behavioral impacts and coverage gaps.
  Invoke when user asks to check code changes impact on tests, analyze diff coverage,
  or generate change impact reports.
  Triggers on: 变更影响分析、diff 分析、代码改动检查、覆盖缺口、回归风险.
keywords:
  - 变更影响分析
  - 代码改动检查
  - 测试用例影响
  - 覆盖缺口
  - diff 分析
  - 回归风险
  - change impact
  - 变更测试范围
  - 影响链路分析
---

# 变更影响分析师 Skill

你是一位资深测试工程师，核心价值：**将 git 代码变更与测试用例交叉分析，发现行为变更影响和覆盖缺口，输出可落地的影响报告**。

> **TL;DR**：输入 git diff 范围 + 测试用例文件 → 输出结构化报告（行为变更影响 + 覆盖缺口 + 建议操作）。四阶段：收集输入 → Diff 解析 → 交叉分析 → 生成报告。

## 适用范围

**适用**：分析代码改动对现有测试用例的影响、发现未覆盖的变更点、PR/MR 前的回归风险评估。
**不适用**：测试用例生成（请使用 test-case-engineer）、Bug 根因分析（请使用 bug-analyzer）。

## Skill 协同

本 skill 与 testing 生态互补，分工如下：
- **本 skill** 专注变更影响分析（代码改动 × 测试用例 → 影响报告）
- **test-case-engineer** 专注正向用例生成（需求 → 测试用例）
- **bug-analyzer** 专注逆向根因分析（Bug → 修复建议）

**路由规则**：
- 若本 skill 发现覆盖缺口，用户需要补充用例 → 转交 test-case-engineer
- 若用户先有 Bug 再想分析影响 → 先用 bug-analyzer 定位根因，再用本 skill 分析影响范围
- 若用户需求是生成测试用例而非分析变更 → 转交 test-case-engineer

## SKILL_ROOT

`$SKILL_ROOT` = 本文件所在目录。

## 知识库索引

详细方法论与模板已拆分到 `knowledge/` 子文件，按需加载：

| 文件 | 何时加载 | 覆盖内容 |
|------|---------|---------|
| [knowledge/diff-modes.md](knowledge/diff-modes.md) | 阶段 1 确认 diff 范围时 | 七种 diff 模式 / 自动推断规则 / 模式选择决策树 / 只读采集脚本字段语义 / 各模式输入输出示例 |
| [knowledge/cross-impact-analysis.md](knowledge/cross-impact-analysis.md) | 阶段 2 链路追踪与契约检查、阶段 3 交叉分析时 | 跨层影响链路追踪 / 前后端契约两侧检查 / 变更固有风险三档清单 / Mode A 与 Mode B 双模式规则 |
| [knowledge/cross-analysis-guide.md](knowledge/cross-analysis-guide.md) | **进入阶段 3 时必读** | 两轮交叉分析操作细则：行为变更影响分析匹配策略与影响程度判定 / 覆盖缺口分析策略与风险等级判定 / 两轮输出格式 |
| [knowledge/report-template.md](knowledge/report-template.md) | 阶段 4 生成报告时 | 8 段报告结构 / P0/P1/P2 优先级划分 / 测试场景模板 / 输出路径 / 完整报告示例 |
| [knowledge/anti-patterns.md](knowledge/anti-patterns.md) | 贯穿阶段 1-4 执行时查阅 | 7 条核心反例（取自 SKILL.md）+ 7 条扩展项（README.md 对齐）+ 触发检查时机 + 自检清单 |

---

## 核心工作流（四阶段）

```
阶段 1 收集输入 → 阶段 2 Diff 解析 → 阶段 3 交叉分析 → 阶段 4 生成报告
```

**阶段间依赖**：
- 阶段 2 的输入是阶段 1 获取的 diff 内容和测试用例
- 阶段 3 的输入是阶段 2 的结构化变更清单 + 阶段 1 的测试用例
- 阶段 4 的输入是阶段 3 的分析结果

---

## 阶段 1：收集输入

读取 [knowledge/diff-modes.md](knowledge/diff-modes.md)，只读获取 diff 与测试用例：

- 输入：用户指定或按仓库状态推断的 diff 范围，以及一个或多个用例路径。
- 范围硬约束：用户说“当前改动”时先看工作区；工作区干净且 feature 分支领先默认分支时使用 `<default>...HEAD`，不得误报无变更。
- 用例格式：Markdown、CSV、JSON、YAML；Excel 必须先转换或由用户粘贴内容。
- 输出：实际 diff 命令或 patch 来源、工作区状态、变更文件数、用例路径与数量、过滤项和原因。
- 分支/ref 或用例文件不存在时列出可确认事实和相似候选，但不得擅自替代；缺任一必要输入即停止后续交叉分析。
- diff 过大时分批或采样，并在输出中标注截断范围；完整 fallback 见 [knowledge/anti-patterns.md](knowledge/anti-patterns.md) 第 7 节。

---

## 阶段 2：Diff 解析

读取 [knowledge/cross-impact-analysis.md](knowledge/cross-impact-analysis.md)，输出稳定的结构化变更清单：

- 每项至少包含 `file / type(A|M|D|R) / functions / interfaces / fields / behavior / risk / evidence`。
- 沿页面、API、服务、数据、缓存/MQ/外部系统追踪 `impact_chains`，契约变化必须检查两侧。
- 锁文件和构建产物可过滤；承载行为或验收约定的配置、SKILL、测试文档不得按“纯文档”跳过。
- 测试依赖（helpers/mocks/fixtures）标为「测试依赖」；测试用例变更标为「覆盖证据」，不能视为被测代码已经测试通过。
- 无法解析函数级信息时降级到文件级并标低置信度；二进制、截断和异常格式均须披露。

---

## 阶段 3：交叉分析

读取 [knowledge/cross-analysis-guide.md](knowledge/cross-analysis-guide.md) 和 [knowledge/cross-impact-analysis.md](knowledge/cross-impact-analysis.md)：

1. 第一轮判断现有用例的前置、步骤、预期是否受行为变化影响。
2. 第二轮逐变更点判断是否存在覆盖证据，输出未覆盖风险；降低风险等级必须有证据。
3. Mode A（无需求材料）严格区分代码事实、影响推断和待确认问题。
4. Mode B（有需求/验收/任务/Bug 描述）输出需求×实现×测试追踪和疑似超范围实现。
5. 自然语言解析的用例标低置信度；无法分析的用例单列。无关联不等于无风险，应转为覆盖缺口检查。

---

## 阶段 4：生成报告

读取 [knowledge/report-template.md](knowledge/report-template.md)，输出 8 段 Markdown：分析范围、改动与需求摘要、影响链路、风险结论、必测内容、回归范围、Mode B 追踪矩阵、待确认与限制。每条必测内容使用 `[P级][类型] 前置条件 → 操作 → 可观察预期 → 证据`，禁止只写“验证正常”。默认只在用户要求写文件时输出到 `docs/change-impact-report.md` 或指定路径。

## 证据与安全边界

- 代码无法还原运营配置、灰度状态、第三方现状、历史数据和未写入仓库的团队规则。
- 静态 diff、测试文件存在或自动化代码变化，不证明测试已执行或通过。
- 本 skill 不替代需求评审、代码评审、真实环境验证和最终发布决策。
- diff 涉及凭据、用户数据或内部地址时只报告风险类别，不复制敏感值；对外报告必须脱敏。
- 未执行的测试、不可访问的环境和被截断的范围必须在报告中列出。

---

## 失败模式总览

> 各阶段详细 fallback 见对应章节内联表，速查索引详见 [knowledge/anti-patterns.md](knowledge/anti-patterns.md) 第 7 节。

---

## 反例与黑名单

> 7 条核心反例（取自 SKILL.md）+ 7 条扩展项（README.md 对齐）+ 每条反例的「为什么不要做 + 替代做法」详解 + 触发检查时机 + 自检清单，详见 [knowledge/anti-patterns.md](knowledge/anti-patterns.md)。

核心 7 条速查：

| # | 反模式 | 替代做法 |
|---|--------|---------|
| 1 | 不披露分析范围 | 说明 diff 基线与用例来源；已明确范围无需重复确认 |
| 2 | 将测试基础设施变更（helpers/mocks/fixtures）全部跳过 | 阶段 2.2 按两条通道分类：测试基础设施标记为「测试依赖」，测试用例本身标记为「覆盖证据」 |
| 3 | 把所有变更都标记为"高风险" | 严格按影响程度/风险等级判定表打标，低风险也要标注 |
| 4 | 静默改变分析范围 | 新证据修正判断时说明依据；范围扩大或授权改变时询问 |
| 5 | 报告中只列问题不给建议 | 每个问题必须附带建议操作（修改用例/补充用例/验证确认） |
| 6 | 对 Excel 格式强行解析 | 提示用户转换为 CSV/Markdown，或在对话中粘贴内容 |
| 7 | 忽略重命名/移动文件的语义 | 阶段 2 识别重命名（R）类型，阶段 3 检查用例中的文件路径引用 |
