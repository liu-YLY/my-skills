# Changelog

本文件记录 my-skill 项目的所有重要变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 新增实施计划文档：`docs/superpowers/plans/2026-07-21-skill-consistency-and-infra.md`
- 新增工程化基础设施：LICENSE / CONTRIBUTING.md / .github 模板 / CI workflow

### Changed
- bug-analyzer knowledge 文件数从 2 个补齐到 4 个（新增 report-template.md / defensive-test-points.md）
- change-impact-analyzer SKILL.md 从 815 行精简到 398 行，下沉到 4 个 knowledge 子文件
- wechat-formatter knowledge 文件数从 1 个补齐到 3 个（新增 module-design.md / brand-profile-spec.md）
- wechat-formatter 新增 integrations/quickstart.md 与 2 个 sample-output（apple / cyber）

### Fixed
- wechat-formatter plugin.json 版本号从 2.0.0 统一到 3.0.0（与 SKILL.md frontmatter 同步）
- test-case-engineer README 版本历史补全 v8.1.0 条目
- state-machine-test-engineer SKILL.md / quickstart.md 标注 MCP Server v0.1.0 协议层未完成状态

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
[testing-bundle-3.0.0]: https://github.com/liu-YLY/my-skills/releases/tag/v3.0.0-testing
[wechat-formatter-3.0.0]: https://github.com/liu-YLY/my-skills/releases/tag/v3.0.0-wechat
[testing-bundle-2.0.0]: https://github.com/liu-YLY/my-skills/releases/tag/v2.0.0-testing
