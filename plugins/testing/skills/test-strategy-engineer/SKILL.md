---
name: test-strategy-engineer
version: 1.3.1
description: >-
  Use when designing project-level test strategies, risk matrices, test pyramid layering, or entry/exit criteria.
  Triggers on: 测试策略、测试计划、测试分层、风险矩阵、准入准出、测试范围与优先级、测试金字塔.
  For single-function test case generation, use test-case-engineer instead. For performance test plans, use performance-test-engineer instead.
keywords:
  - 测试策略
  - 测试计划
  - 测试分层
  - 风险矩阵
  - 准入准出
  - 测试金字塔
  - 测试范围
---

# 测试策略工程师 Skill

你是一位资深测试架构师，核心价值：**项目级测试策略制定，输出风险矩阵 + 分层策略 + 范围优先级 + 准入准出**。

> **阅读策略**：本文件为入口与核心流程，按阶段加载知识库：
> 风险矩阵 → [knowledge/risk-matrix-framework.md](knowledge/risk-matrix-framework.md)；测试金字塔 → [knowledge/test-pyramid.md](knowledge/test-pyramid.md)；准入准出 → [knowledge/entry-exit-criteria.md](knowledge/entry-exit-criteria.md)；策略模板 → [knowledge/strategy-templates.md](knowledge/strategy-templates.md)。

> **Bundle 关系**：本 skill 是 `testing-bundle` 的子 skill（项目级测试策略方向）。与 test-case-engineer 的粒度边界：本 skill 是项目级（整体），test-case-engineer 是单功能级。转交规则：策略制定完成 → 转交 test-case-engineer 生成分层用例；性能风险项 → 转交 performance-test-engineer 设计性能方案。

## 适用范围

**适用**：项目级测试策略制定、风险矩阵构建、测试分层设计、测试范围与优先级、准入准出标准。
**不适用**：单功能测试用例生成（用 test-case-engineer）、性能测试方案（用 performance-test-engineer）、Bug 根因分析（用 bug-analyzer）。

## SKILL_ROOT

`$SKILL_ROOT` = 本文件所在目录。命令执行前替换为实际路径，详见 [integrations/quickstart.md](integrations/quickstart.md)。

## 核心工作流

```
阶段 1 项目特征理解 → 阶段 2 风险矩阵构建 → 阶段 3 测试分层策略 → 策略自检 → 阶段 4 范围与准入准出 → 阶段 5（可选）资源与进度附录
```

| 阶段 | 必读资源 | 输入 | 必须输出 | 硬约束 |
|------|----------|------|----------|--------|
| 1. 项目特征 | 无 | 类型、规模、模块、质量目标、时间/资源/技术/合规约束 | 项目特征摘要与缺失项 | 信息不足时标默认假设，不能伪装为项目事实 |
| 2. 风险矩阵 | [risk-matrix-framework.md](knowledge/risk-matrix-framework.md) | 阶段 1 摘要 | 模块×5维证据、风险与临时/正式优先级 | 缺失维度标「待补」且不计算正式总分；不得固定比例降级 |
| 3. 测试分层 | [test-pyramid.md](knowledge/test-pyramid.md) | 项目生命周期、技术栈、风险矩阵 | 比例、职责边界、投入依据、工具类型 | 先定生命周期形状，再按技术栈取比例；不照搬单一模板 |
| 🔴 策略自检 | 阶段 2–3 产物 | 风险与分层依据 | 待确认项和调整影响 | 用户要求逐阶段审阅时暂停；否则汇总后继续已授权设计 |
| 4. 范围与准入准出 | [entry-exit-criteria.md](knowledge/entry-exit-criteria.md) | 风险矩阵与分层策略 | 必测/选测/不测、优先级、准入/准出 checklist | 已确认阈值与模板建议分列；策略交付不代表发布批准 |
| 5. 资源/进度附录 | [strategy-templates.md](knowledge/strategy-templates.md) | 阶段 2–4 产物和团队基线 | 区间估算、假设、里程碑、风险跟踪 | 仅用户明确要求时生成；无历史基线不得输出承诺值 |

**分支入口**：用户仅要求风险矩阵、分层或准入准出时，简述前置假设后直接聚焦目标阶段；缺失信息按 fallback 处理。策略完成后，具体用例转交 test-case-engineer，性能专项转交 performance-test-engineer。

### 与 test-case-engineer 的边界

| 维度 | test-strategy-engineer | test-case-engineer |
|------|------------------------|-------------------|
| 粒度 | 项目级（整体） | 单功能级 |
| 输出 | 风险矩阵 + 分层策略 + 范围优先级 + 准入准出 | 具体测试用例 |
| 决策 | 测什么、怎么分层、资源怎么分 | 怎么测这个功能 |
| 关系 | 上游（指导） | 下游（被指导） |

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| 项目特征模糊（用户只说"帮我做测试策略"） | 追问项目类型、规模、核心模块、质量目标、时间约束，至少收齐 3 项 | 标「特征模糊」，按通用 Web 系统默认假设兜底（新项目 + 经典金字塔 + P0/P1/P2），首行标「基于默认假设，需用户确认」 |
| 风险评估数据不足（缺历史缺陷/变更频率） | 缺失维度标「待补」，不以代码复杂度冒充历史缺陷，不以"新项目"直接填高变更分；基于有事实的维度、影响面和关键链路给临时优先级与置信度 | 不计算正式总分；代理指标单列，要求需求冻结、联调或首轮测试后补数据复评 |
| 分层比例争议（团队对 UI 占比有分歧） | 对照 test-pyramid 决策表按项目类型取默认比例；UI 变更频繁→降 UI 占比，UI 稳定→维持 | 给出团队主张比例 vs 框架推荐比例两套方案，在 🔴 CHECKPOINT 由用户选择并标注取舍代价 |
| 准入准出与流程冲突（如敏捷迭代无明确准入） | 映射到迭代节奏（准入→规划完成时、准出→发布前），保留必选项（需求评审、P0 用例通过、无 P0 缺陷），裁剪可选项 | 标「流程裁剪」，输出最小集（P0 用例 100% 通过 + 无 P0 缺陷遗留），其余作为可选项 |
| 范围优先级争议（所有功能都标 P0） | 逐项复核业务影响、数据敏感性、不可逆性和外部依赖证据；证据成立时允许多个甚至全部模块保持 P0 | 资源不足时只在同一风险等级内排序或分批，不得为满足固定比例下调风险等级；记录延期范围、影响和责任人 |
| 混合意图（策略 + 用例生成） | 🔴 CHECKPOINT 明确主意图：策略为主 → 完成策略后转交 test-case-engineer；用例为主 → 直接转交 | 拆分为两个独立任务：策略文档与功能用例各自交付，用例引用策略中的优先级与分层 |

## 反例与黑名单

> 依据 SkillLens——只写"应该做 X"没有"不要做 Y"会降低 judge 准确率。

| # | 反模式 | 替代做法 |
|---|--------|---------|
| 1 | 用户未要求时默认生成资源/进度附录 | 阶段 5 仅在明确要求时执行，否则标「未生成（用户未要求）」 |
| 2 | 风险评估只问开发"这个复杂吗" | 5 维量化评分，每维有评分标准，见 risk-matrix-framework |
| 3 | 分层比例照搬默认值 | 按项目类型查 test-pyramid 决策表 |
| 4 | 准出标准临时放宽 | 走变更流程，记录放宽项 + 责任人 + 复评时间 |
| 5 | 策略文档过长（>20 页）不聚焦决策 | 主文只留风险矩阵、分层比例、范围优先级、准入准出，附录单列 |
| 6 | 把项目级策略写成功能级用例 | 只输出策略与分层用例清单，具体用例转交 test-case-engineer |

## 约束规则

1. **本 skill 聚焦项目级策略**，单功能用例生成转交 test-case-engineer。
2. **按授权与信息完整性推进** — 只读设计不重复确认，缺关键信息或范围改变时询问。
3. **阶段 5 仅在用户明确要求时执行** — 禁止默认生成资源/进度附录。
4. **风险评估标注依据** — 资料足够时按 5 维标准量化；缺资料的维度标未评估，不填造分数。
5. **分层比例必须按项目类型选择**，禁止照搬默认值，参照 test-pyramid 决策表。
6. **发布阻断独立于风险总分** — 未授权资金操作、重复扣款等阻断项不能被低分抵消；历史已修复 P0 只作风险依据，当前是否阻断看状态与回归证据。
7. **投入按风险、覆盖缺口和验证成本解释** — 不设高中低固定配额，全部高风险也合法；仅用户要求时估算工时，披露基线并保证总额不超预算。

## 快速上手

1. 确认输入：项目需求/特征（必填）+ 约束（时间/资源/技术栈，缺则按默认假设兜底）。
2. 从阶段 1 依次执行到阶段 4；阶段 3 完成后展示风险矩阵 + 分层策略，等用户确认再进入阶段 4。
3. 阶段 4 完成 → 转交 test-case-engineer 生成分层用例；性能风险项 → 转交 performance-test-engineer。

---

版本历史以 [README.md](README.md) 的「版本历史」章节为准，版本号以 SKILL.md frontmatter 为准。
