# Changelog

本文件记录 my-skill 项目的所有重要变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 新增实施计划文档：`docs/superpowers/plans/2026-07-21-skill-consistency-and-infra.md`
- 新增工程化基础设施：LICENSE / CONTRIBUTING.md / .github 模板 / CI workflow
- test-case-engineer 升级到 v8.3.0：生成流程新增「原文问题清单」机制——阶段 1 输出模板新增「原文问题清单」字段（序号/原文位置/问题类型/问题描述/影响范围/处置），阶段 1/2/3/4 发现需求/代码/口述原文问题（模糊/矛盾/缺失/错误）时回填该清单，阶段 4 行为约束从"发现遗漏直接补充到用例，不另外说明"调整为"源于原文问题的遗漏同时回填清单"，阶段 4 自检清单新增「原文问题回填」检查项

## [testing-bundle-3.1.1] - 2026-07-22

### Added
- 声明 review-checker MCP Server 为 test-case-engineer 评审模式的可选增强组件（10 维度确定性校验，与 state-machine-testing MCP 增强对称）

### Changed
- bundle 版本 v3.1.0 → v3.1.1
- 路由契约修复：删除"意图不明确时默认路由到 test-case-engineer"的兜底规则，改为"持续追问，仅当用户明确授权'你来决定'时才默认路由"，消除与路由决策表"追问用户"的冲突
- change-impact-analyzer 归属修正：从"外部 skill，需单独安装"修正为"testing plugin 内第 6 个协同 skill（`skills: "./skills/"` 已包含）"，同步安装说明、协同表、快速上手
- bug-analyzer knowledge 文件数从 2 个补齐到 4 个（新增 report-template.md / defensive-test-points.md）
- change-impact-analyzer SKILL.md 从 815 行精简到 398 行，下沉到 4 个 knowledge 子文件（diff-modes / cross-impact-analysis / report-template / anti-patterns）
- 版本单一来源：同步 frontmatter / 正文标题 / 架构图 / 3 个 plugin manifest / CHANGELOG / test-prompts 版本号至 v3.1.1

### Fixed
- wechat-formatter plugin.json 版本号从 2.0.0 统一到 3.0.0（与 SKILL.md frontmatter 同步）
- test-case-engineer README 版本历史补全 v8.1.0 条目
- state-machine-test-engineer SKILL.md / quickstart.md 标注 MCP Server v0.1.0 协议层未完成状态

## [testing-bundle-3.1.0] - 2026-07-21

### Added
- 新增混合意图链 6：评审 → 覆盖缺口验证（test-case-engineer 评审模式 → change-impact-analyzer 做 git diff × 用例交叉验证）
- 新增混合意图链 7：评审 → 风险用例根因反推（test-case-engineer 评审模式 → bug-analyzer 按五步定位法反推根因）
- test-case-engineer 升级到 v8.2.0：评审模式新增第 10 维度「语义一致性冲突检测」（跨用例前后语义冲突：前置条件矛盾 / 同输入异预期 / 依赖闭环）
- change-impact-analyzer 升级到 v1.1.0：阶段 3 末尾新增 🔴 CHECKPOINT（让用户校对两类问题分析结果后再生成最终报告），anti-patterns.md 第 2 条改为"两条通道分类"（测试基础设施 vs 测试用例作为覆盖证据）

### Changed
- bundle 版本 v3.0.0 → v3.1.0
- 混合意图链数 5 条 → 7 条
- 子 skill 数 5 核心 + 1 协同（change-impact-analyzer 随 testing plugin 整体安装获得）
- 评审模式成为混合意图链起点（链 6/7 均以评审为上游）
- 失败模式表新增"链 6 降级"方向性指导模板

### Breaking Changes

- 新增链 6/7 依赖 change-impact-analyzer 与 bug-analyzer，按需安装时需注意覆盖

## [testing-bundle-3.0.0] - 2026-07-18

### Added
- testing-bundle v3.0.0：5-way 路由 + 5 条混合意图链 + 状态机测试集成
- state-machine-test-engineer v1.0.0：状态机驱动的状态型需求测试（10 类场景穷举 + 4 个行业模板 + 可选 MCP Server）
- change-impact-analyzer v1.0.0：独立 skill，四阶段工作流 + 七种 diff 模式

### Changed
- testing-bundle 路由从 4-way 扩展到 5-way（新增状态机测试路由）
- test-case-engineer 升级到 v8.1.0：新增用例拆分与合并平衡策略

## [wechat-formatter-3.0.0] - 2026-07-15

### Added
- wechat-formatter v3.0.0：6 种排版风格 + 高级排版模块（9 大类 + `:::module` 语法）+ Brand Profile
- 新增 apple 与 cyber 两种风格
- 新增 layout/ 目录与 brand/ 目录

### Changed
- 五阶段工作流重构（分析内容 → 匹配风格 → 执行排版 → 输出校验 → 生成 HTML）

## [testing-bundle-2.0.0] - 2026-07-10

### Added
- testing-bundle v2.0.0：4-way 路由（test-strategy / test-case / performance / bug-analyzer）
- performance-test-engineer v1.0.0：资源/架构层瓶颈定位（USE 方法 + 6 类瓶颈模式）
- test-strategy-engineer v1.0.0：项目级测试策略（五阶段 + 风险矩阵 + 准入准出）
- bug-analyzer v1.0.0：Bug 根因分析（五步定位法 + 5 Whys + 鱼骨图）

### Changed
- test-case-engineer 从 test-engineer v7.0.0 拆分而来，专注正向用例生成

[Unreleased]: https://github.com/liu-YLY/my-skills/compare/main...HEAD
[testing-bundle-3.1.1]: https://github.com/liu-YLY/my-skills/releases/tag/v3.1.1-testing
[testing-bundle-3.1.0]: https://github.com/liu-YLY/my-skills/releases/tag/v3.1.0-testing
[testing-bundle-3.0.0]: https://github.com/liu-YLY/my-skills/releases/tag/v3.0.0-testing
[wechat-formatter-3.0.0]: https://github.com/liu-YLY/my-skills/releases/tag/v3.0.0-wechat
[testing-bundle-2.0.0]: https://github.com/liu-YLY/my-skills/releases/tag/v2.0.0-testing
