# Changelog

本文件记录 testing-bundle 所有版本变更。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

---

## [3.1.1] - 2026-07-22

### Added

- **声明 review-checker MCP Server 可选增强**：test-case-engineer 评审模式可选调用 `review-checker-mcp` Server 做 10 维度确定性校验与度量报告（与 state-machine MCP 增强对称），未安装时降级为纯 LLM 推理

### Changed

- **bundle 版本**：v3.1.0 → v3.1.1
- **路由契约修复**：删除"意图不明确时默认路由到 test-case-engineer"的兜底规则，改为"持续追问，仅当用户明确授权'你来决定'时才默认路由"，消除与路由决策表"追问用户"的冲突
- **change-impact-analyzer 归属修正**：从"外部 skill，需单独安装"修正为"testing plugin 内第 6 个协同 skill（`skills: "./skills/"` 已包含）"，同步安装说明、协同表、快速上手
- **版本单一来源**：同步 frontmatter / 正文标题 / 架构图 / 3 个 plugin manifest / CHANGELOG / test-prompts 版本号至 v3.1.1

## [3.1.0] - 2026-07-21

### Added

- **新增混合意图链 6**：评审 → 覆盖缺口验证（test-case-engineer 评审模式 → change-impact-analyzer 做 git diff × 用例交叉验证）
- **新增混合意图链 7**：评审 → 风险用例根因反推（test-case-engineer 评审模式 → bug-analyzer 按五步定位法反推根因）
- 评审模式成为混合意图链起点（链 6/7 均以评审为上游）

### Changed

- **bundle 版本**：v3.0.0 → v3.1.0
- **混合意图链数**：5 条 → 7 条
- **子 skill 数**：5 核心 + 1 协同（change-impact-analyzer 随 plugin 整体安装）
- **失败模式表**：新增"链 6 降级"方向性指导模板

### Breaking Changes

- 新增链 6/7 依赖 change-impact-analyzer 与 bug-analyzer，按需安装时需注意覆盖

---

## [3.0.0] - 2026-07-18

### Added

- **新增子 skill**：`state-machine-test-engineer v1.0.0`
  - 状态机驱动的状态型需求测试能力（订单/审批/工单/会员等生命周期场景）
  - 五阶段工作流：状态型需求识别 → 状态机建模 → CHECKPOINT → 完整性检查 → 10 类场景穷举 →（可选）MCP 增强
  - 知识库含 4 个行业状态机模板：订单退款 / 审批流 / 会员 / 工单
  - 10 类场景穷举：合法转换 / 非法转换 / 条件不满足 / 重复幂等 / 并发冲突 / 消息乱序 / 超时重试 / 数据一致性 / 权限控制 / 失败恢复
  - 防幻觉机制：依据类型强制标注（需求明确 / 合理推理 / 待确认），歧义暴露而非补齐
- **新增配套 MCP Server**：`state-machine-testing-mcp v0.1.0`（位于 `plugins/testing/mcp-servers/state-machine-testing/`）
  - 5 个工具：build_state_machine / validate_state_machine / generate_scenarios / export_artifacts / check_coverage
  - Python 3.11+ / mcp 官方 SDK / pydantic v2
  - skill 可选增强，未安装时降级为纯 LLM 推理
- **新增混合意图链 5**：状态机建模 + 用例生成（state-machine → case-engineer）
- **新增设计文档**：[2026-07-18-state-machine-testing-design.md](../../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md)

### Changed

- **路由扩展**：4-way → 5-way，新增"状态机/状态流转/生命周期/非法跳转/幂等/并发冲突/消息乱序/终态吸收"等状态型信号关键词
- **bundle 版本**：v2.0.0 → v3.0.0
- **混合意图链数**：4 条 → 5 条
- **子 skill 数**：4 → 5
- **追问选项**：4 选项 → 5 选项（新增 E. 状态机测试）
- **失败模式表**：新增"state-machine 不可用"方向性指导模板
- **README/SKILL**：同步更新架构图、路由表、安装方式、知识库依赖说明、使用示例（新增示例 6/7/8）

### Breaking Changes

- 路由表扩展，依赖原 4-way 路由的下游消费方需更新意图判断逻辑
- 整体安装包从 5 个 skill 扩到 6 个（bundle + 5 子 skill）
- 失败模式表"子 skill 不可用"兜底模板新增 state-machine 分支

### Migration Guide

1. 旧版本（v2.0.0）用户升级时，原 4 个子 skill 无需改动，向后兼容
2. 若需启用状态机测试能力，安装 `state-machine-test-engineer` skill
3. 若需启用 MCP 增强模式，额外安装 `state-machine-testing-mcp` Server（见 [state-machine-test-engineer/integrations/quickstart.md](../state-machine-test-engineer/integrations/quickstart.md)）
4. 若仅使用原 4 个 skill 的能力，不受 v3.0.0 影响，路由行为保持一致

### Validation

- 5-way 路由准确率目标：≥90%（30 个混合 prompt 验证）
- 4 个旧 skill 回归测试：评分不下降
- darwin-skill 评分目标：state-machine-test-engineer ≥83 分，无单项 <70
- MCP Server 单测覆盖率：≥90%

---

## [2.0.0] - 2026-07-04

### Added

- **新增子 skill**：`test-strategy-engineer v1.0.0`（项目级测试策略）
- **新增子 skill**：`performance-test-engineer v1.0.0`（性能测试方案+瓶颈定位）
- **新增混合意图链 2**：测试策略 + 分层用例（strategy → case-engineer）
- **新增混合意图链 3**：性能测试 + 瓶颈定位（performance 内部完成）
- **新增混合意图链 4**：性能瓶颈 + 代码缺陷（performance → bug-analyzer）

### Changed

- 路由扩展：2-way → 4-way
- bundle 版本：v1.0.0 → v2.0.0
- 子 skill 数：2 → 4
- 新增"链 3 vs 链 4 二级判定规则"

### Breaking Changes

- 路由表扩展，原 2-way 路由下游需更新意图判断逻辑

---

## [1.0.0] - 初始版本

### Added

- `testing-bundle` 元 skill（路由入口）
- 子 skill `test-case-engineer`（功能用例生成）
- 子 skill `bug-analyzer`（功能缺陷根因）
- 混合意图链 1：Bug 分析 + 用例生成（bug-analyzer → case-engineer）
- 2-way 路由决策表
- 失败模式与 Fallback 表
- 上下文传递 schema
