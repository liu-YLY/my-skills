---
name: test-strategy-engineer
version: 1.3.3
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

# 测试策略工程师

按请求选择下表对应部分。完整策略按项目特征、风险、分层、范围与准入准出组织。先从材料提取业务目标、核心模块和资源约束。只有会改变决策的信息需要追问，其余注明假设与影响。

| 任务 | 按需读取 | 交付 |
|------|----------|------|
| 风险矩阵 | [risk-matrix-framework.md](knowledge/risk-matrix-framework.md) | 逐模块标 5 维证据、风险与优先级。缺失维度标「待补」且不计算正式总分。按已证实影响给临时优先级，并写复评条件。 |
| 分层与契约 | [test-pyramid.md](knowledge/test-pyramid.md) | 按风险、可观察结果、现有覆盖和成本选层。比例可省略。契约验证写明双方可控程度与实际证据。 |
| 范围与准入准出 | [entry-exit-criteria.md](knowledge/entry-exit-criteria.md) | 明确必测、选测、延期及影响。区分已确认门槛、建议值和待确认项。门槛调整记录理由、责任人与复评时间。 |
| 指定模板、覆盖口径或资源附录 | [strategy-templates.md](knowledge/strategy-templates.md) 相应部分 | 用户要求覆盖分析时按各层基线报告。仅明确要求时提供资源、进度或风险跟踪附录。估算给区间、依据和预算缺口。 |

缺资料时给可判断部分，代理指标单列。不得为满足固定比例下调风险等级，资源不足就在同等级排序或分批。已确认发布阻断项独立记录，历史已修复的 P0 仍可作为风险依据。准入准出可映射到实际迭代节点，保留需求评审、核心用例与阻断缺陷门槛。

输出时汇总分层取舍与待确认事项。仅用户要求逐段评审时暂停。用户需要完整功能用例或专项性能方案时，带上相关优先级和风险转交 `test-case-engineer` 或 `performance-test-engineer`。

[使用说明](README.md) · [示例](integrations/quickstart.md)
