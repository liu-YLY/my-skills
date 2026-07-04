# test-strategy-engineer

> 项目级测试策略制定 skill，输出风险矩阵 + 分层策略 + 范围优先级 + 准入准出，v1.0.0。
> testing-bundle 的项目级测试策略方向子 skill。

## 适用场景

**适用**：项目级测试策略制定、风险矩阵构建、测试分层设计、测试范围与优先级、准入准出标准。
**不适用**：单功能测试用例生成（用 test-case-engineer）、性能测试方案（用 performance-test-engineer）、Bug 根因分析（用 bug-analyzer）。

## 核心能力

5 阶段工作流（含 🔴 CHECKPOINT 强制确认点）：

```
阶段 1 项目特征理解 → 阶段 2 风险矩阵构建 → 阶段 3 测试分层策略 → 🔴 CHECKPOINT → 阶段 4 范围与准入准出 → 阶段 5（可选）资源与进度附录
```

- **阶段 1 项目特征理解**：提炼项目类型、规模、质量目标与约束，输出项目特征摘要作为后续输入。
- **阶段 2 风险矩阵构建**：按 5 维（业务复杂度/变更频率/历史缺陷/外部依赖/数据敏感性）量化评分，映射风险等级与测试优先级。
- **阶段 3 测试分层策略**：按项目类型选择分层比例，明确各层职责边界，按风险矩阵分配各层测试投入，推荐工具类型。
- **🔴 CHECKPOINT**：阶段 3 完成后展示风险矩阵 + 分层策略给用户确认，未确认前禁止进入阶段 4。
- **阶段 4 范围与准入准出**：定义必测/选测/不测三档范围，制定准入准出 checklist（全部给具体阈值）。
- **阶段 5（可选）资源与进度附录**：仅当用户明确要求资源估算/进度排期/风险跟踪时执行，否则跳过。

## 与其他 skill 的边界

本 skill 聚焦项目级策略，test-case-engineer 聚焦单功能用例。

| 维度 | test-strategy-engineer | test-case-engineer |
|------|------------------------|-------------------|
| 粒度 | 项目级（整体） | 单功能级 |
| 输入 | 项目需求/特征/约束 | 单功能需求 |
| 输出 | 风险矩阵 + 分层策略 + 范围优先级 + 准入准出 | 具体测试用例 |
| 决策 | 测什么、怎么分层、资源怎么分 | 怎么测这个功能 |
| 关系 | 上游（指导） | 下游（被指导） |

**转交规则**：
- 本 skill 阶段 4 完成 → 转交 test-case-engineer 按分层策略与优先级生成各层用例
- 风险矩阵中标注性能风险项 → 转交 performance-test-engineer 设计性能方案

## 安装方式

- **推荐**：通过 [testing-bundle](../testing-bundle/) 整体安装，由 bundle 统一路由到本 skill。
- **单独安装**：本 skill 可独立使用；与 test-case-engineer/performance-test-engineer 的转交需手动衔接（转交时携带风险矩阵 + 分层策略 + 范围优先级）。

## 知识库

| 文件 | 说明 |
|------|------|
| [knowledge/risk-matrix-framework.md](knowledge/risk-matrix-framework.md) | 风险识别 5 维 + 评级 |
| [knowledge/test-pyramid.md](knowledge/test-pyramid.md) | 测试金字塔分层 + 比例 |
| [knowledge/entry-exit-criteria.md](knowledge/entry-exit-criteria.md) | 准入准出 checklist |
| [knowledge/strategy-templates.md](knowledge/strategy-templates.md) | 策略文档模板 |

## 版本历史

- v1.0.0: 初始版本，作为 testing-bundle 的项目级测试策略方向子 skill
