---
name: testing-bundle
version: 3.6.0
description: >-
  Use when user has mixed, ambiguous, or explicitly routing-required testing requests —
  e.g. "analyze bug AND generate test cases", "design strategy AND generate layered cases",
  "performance test AND diagnose bottleneck", "review AND check coverage gaps",
  "write test cases AND prepare offline test data",
  or "not sure which testing capability is needed".
  For single-intent requests (test cases only, strategy only, performance only, bug analysis only,
  state-machine only, change-impact only, frontend navigation preparation only,
  offline test-data generation/validation only),
  the corresponding sub-skill handles directly without bundle routing.
  Triggers on: 混合测试意图、模糊测试请求、测试bundle、测试路由、不确定需要哪种测试能力.
  This is a bundle entry that routes to test-strategy-engineer, test-case-engineer,
  performance-test-engineer, bug-analyzer, state-machine-test-engineer,
  change-impact-analyzer, frontend-test-preparation, or test-data-generator.
keywords:
  - 测试bundle
  - 测试路由
  - 混合测试意图
  - 模糊测试请求
  - 测试能力选择
---

# Testing Bundle

测试能力 bundle 入口：统一路由到 8 个专业子 skill（策略、用例、性能、缺陷根因、状态机、变更影响、前端准备、离线数据），只判断与传递上下文，不实现专业流程。子 skill 均可独立调用，随 testing plugin 整体安装。

## 路由顺序

1. 提取对象 / 动作 / 交付物三要素；不全或矛盾先追问
2. 命中混合意图链 → 按链执行
3. 未命中 → 查单意图路由表
4. 仍未命中 → 追问（🔴 CHECKPOINT）

### 意图解析

- **对象**：需求文档 / 已有用例 / 代码 diff / 线上故障 / 状态流转 / 前端页面 / 数据文件 / 项目整体
- **动作**：生成 / 评审 / 分析 / 定位 / 准备 / 校验 / 汇报
- **交付物**：用例集 / 测试策略 / 根因报告 / 影响范围 / 数据文件 / 导航索引 / 评审方案

- **对象定候选**：需求 → 用例或策略；已有用例 → 评审；diff → 影响分析；故障 → 根因；状态流转 → 状态机；前端页面/入口 → 前端准备；数据文件 → 造数或校验
- **动作定方式**：同一对象出现「生成 + 评审」等多个动作时按混合链处理，不压成一次
- **交付物定终点**：要「方案/汇报/评审会材料」而非「用例明细」时走评审方案子模式，不输出完整用例
- **缺失**：对象缺失 → 追问；动作缺失 → 按对象默认（需求生成、已有用例评审、diff 影响分析）；交付物缺失 → 按动作默认
- **矛盾**（如「生成测试策略」但交付物是用例）→ 🔴 CHECKPOINT 请用户确认

### 单意图路由

| 意图信号 | 路由到 |
|----------|--------|
| 项目级策略、测试计划、测试分层、风险矩阵、准入准出、测试范围与优先级 | **test-strategy-engineer** |
| 测试用例、编写/生成用例、测试点、需求分析、用例评审、单功能测试策略；评审方案、覆盖度汇报、评审会材料、用例太多评不完 | **test-case-engineer** |
| 需求评审、PRD 评审、评审需求文档、需求文档检查、需求问题清单 | **test-case-engineer**（需求评审模式） |
| 读前端代码、页面索引、前端导航索引、需求入口定位、测试账号与数据状态、更新页面索引 | **frontend-test-preparation** |
| Bug 分析、根因、缺陷定位、复现、5 Whys、鱼骨图、防御性用例反推 | **bug-analyzer** |
| 性能测试、负载/压力/并发测试、TPS、响应时间、瓶颈、容量评估 | **performance-test-engineer** |
| 状态机、状态流转、生命周期、非法跳转、幂等、并发冲突、消息乱序、状态回退、终态吸收 | **state-machine-test-engineer** |
| 变更影响分析、diff 分析、代码改动点、影响范围与测试内容、覆盖缺口、回归风险 | **change-impact-analyzer** |
| 造测试数据、批量生成、生成关联数据、测试 CSV/JSON、按规则校验测试数据 | **test-data-generator** |
| 意图不明确 | 追问（🔴 CHECKPOINT），列出 8 个能力 |

**边界**：

- 代码改动 + 范围/优先级/测试内容 → 变更分析；用户另外明确要求正式用例集时才转用例生成
- 「测试前端功能」「测这个页面」→ 用例生成；只有明确读前端代码、定位入口或维护索引才走前端准备
- 要求撰写/润色 PRD，而非找需求问题 → 不进入需求评审；需求评审只针对已有 PRD/需求文档
- 已有用例/场景/组合矩阵只要准备或检查数据 → test-data-generator；出现「用例/订单状态/并发」不自动触发用例、状态机或性能
- 含关键词或语义等价（测试计划=测试策略、QPS=吞吐量）即命中；模糊时按第 4 步追问
- 计数术语：`7 维度` = 用例阶段 2；`10 类场景` = 状态机阶段 4；`10 维度` = 用例评审 R2

## 混合意图链

命中后读取 [knowledge/mixed-intent-chains.md](knowledge/mixed-intent-chains.md)，按链执行；转交时记录依据与未决事项，既有授权内连续执行。

| 链 | 名称 | 路径 | 触发 |
|---|---|---|---|
| 1 | Bug + 用例 | bug-analyzer → test-case-engineer | Bug 分析 + 用例生成 |
| 2 | 策略 + 分层用例 | test-strategy-engineer → test-case-engineer | 测试策略 + 用例生成 |
| 3 | 性能 + 瓶颈 | performance-test-engineer（内部完成） | 性能测试 + 瓶颈定位 |
| 4 | 性能 → 代码缺陷 | performance-test-engineer → bug-analyzer | 瓶颈 + 代码缺陷信号 |
| 5 | 状态机 + 用例 | state-machine-test-engineer → test-case-engineer | 状态机 + 明确要求完整用例 |
| 6 | 评审 → 覆盖缺口 | test-case-engineer → change-impact-analyzer | 评审 + 覆盖缺口/diff |
| 7 | 评审 → 根因反推 | test-case-engineer → bug-analyzer | 评审 + 根因反推 |
| 8 | 用例 → 离线数据 | test-case-engineer → test-data-generator | 新编/修订用例 + 造数或校验 |
| 9 | 前端准备 → 用例 | frontend-test-preparation → test-case-engineer | 前端准备 + 生成/修订用例 |
| 10 | 需求评审 → 用例 | test-case-engineer（需求评审）→ test-case-engineer（用例生成） | 需求评审 + 明确要求生成/修订用例 |

## 子 skill 加载

路由确定后才读目标文件；混合链按顺序加载，禁止预载全部。

- [test-strategy-engineer](../test-strategy-engineer/SKILL.md)：项目级策略、分层、风险矩阵、准入准出
- [test-case-engineer](../test-case-engineer/SKILL.md)：功能用例、测试点、评审（含规模化与干系人方案）；review-checker MCP 可选
- [frontend-test-preparation](../frontend-test-preparation/SKILL.md)：前端导航索引与需求映射；运行核实需浏览器工具/环境/授权，不具备时只交付代码分析与待确认
- [performance-test-engineer](../performance-test-engineer/SKILL.md)：性能方案与资源/架构瓶颈
- [bug-analyzer](../bug-analyzer/SKILL.md)：功能缺陷根因；缺共享 bug-patterns 时按其规则降级
- [state-machine-test-engineer](../state-machine-test-engineer/SKILL.md)：状态建模与场景穷举；state-machine MCP v0.8.5 可选
- [change-impact-analyzer](../change-impact-analyzer/SKILL.md)：从改动生成影响范围与测试内容；用例/需求对照可选
- [test-data-generator](../test-data-generator/SKILL.md)：可重复离线造数与文件校验；不写数据库、不调业务 API

安装/依赖/MCP 配置见 [../../README.md](https://github.com/liu-YLY/my-skills/blob/main/plugins/testing/README.md)；复制安装只交付 Skill 资源，缺 MCP 时子 skill 进入独立模式并如实标记。

## 失败模式与约束

降级、冲突裁定、上下文 schema、路由/安装反例见 [knowledge/routing-fallbacks.md](knowledge/routing-fallbacks.md)（按需）。

入口三条：

1. 意图不明确 → 追问；仅用户明确「你来决定」才默认 test-case-engineer
2. 子 skill 不可用 → 标注并交付上游产物与方向性指导，不假装完成
3. 转交 → 按 schema 显式传原始请求、上游产物、已完成步骤、下游任务

约束：

- 只路由，不实现能力；不默认或随机路由
- 性能类默认 performance，仅瓶颈指向代码逻辑层才转 bug-analyzer
- strategy 是并列 peer，不是必经入口
- 混合意图按业务依赖转交；已授权内连续执行，文末列依据与未决

11 个路由演示与首次使用引导见 [knowledge/usage-examples.md](knowledge/usage-examples.md)（按需）；版本历史见 [CHANGELOG.md](CHANGELOG.md)。
