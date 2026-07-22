# My Skill - AI 技能集合项目

> 基于 AI 的智能技能系统，提供测试策略、测试用例生成、性能测试、Bug 根因分析、状态机测试、变更影响分析、微信公众号排版等专业技能

## 项目简介

My Skill 是一个 AI 驱动的技能集合项目，旨在通过人工智能技术提升工作效率。项目包含多个专业领域的技能模块，每个技能都经过精心设计，能够理解用户需求并提供高质量的专业输出。

### 核心特性

- **AI 赋能**：基于大语言模型，理解自然语言需求
- **专业化输出**：每个技能都有明确的输出规范和质量标准
- **模块化设计**：技能独立运行，可按需组合使用
- **知识库支持**：内置专业知识库，确保输出的专业性和准确性
- **MCP 增强**：部分 skill 配套 MCP Server，提供确定性机器校验（未安装时降级为纯 LLM 推理）

## 技能一览

> **技能分组**：项目采用 plugin marketplace 模式（参考 [obra/superpowers](https://github.com/obra/superpowers)），单 repo 内通过 `.claude-plugin/marketplace.json` 注册两个独立 plugin。

### Testing Bundle（测试能力 bundle）

| Skill | 版本 | 功能 | MCP Server |
|---|---|---|---|
| **testing-bundle** | v3.1.1 | bundle 入口，5-way 路由 + 7 条混合意图链 | - |
| test-strategy-engineer | v1.0.0 | 项目级测试策略（风险矩阵/分层/准入准出） | - |
| test-case-engineer | v8.2.0 | 功能用例生成 + 9 维度评审模式 | review-checker v0.2.0（可选） |
| performance-test-engineer | v1.0.0 | 性能测试方案 + 瓶颈定位（USE 方法） | - |
| bug-analyzer | v1.0.0 | Bug 根因分析（五步定位法/鱼骨图/5 Whys） | - |
| state-machine-test-engineer | v1.0.0 | 状态机建模 + 10 类场景穷举 | state-machine-testing v0.1.0（可选） |
| change-impact-analyzer | v1.0.0 | 变更影响分析（独立 skill，不集成到 bundle） | - |

**7 条混合意图链**：
- 链 1：Bug 分析 + 补充用例 → bug-analyzer → case-engineer
- 链 2：测试策略 + 分层用例 → strategy → case-engineer
- 链 3：性能测试 + 瓶颈定位 → performance（内部完成）
- 链 4：性能瓶颈 + 代码缺陷 → performance → bug-analyzer
- 链 5：状态机建模 + 用例生成 → state-machine → case-engineer
- 链 6：评审→覆盖缺口验证 → case-engineer 评审模式 → change-impact-analyzer
- 链 7：评审→风险用例根因反推 → case-engineer 评审模式 → bug-analyzer

### Wechat Formatter（微信公众号排版）

| Skill | 版本 | 功能 |
|---|---|---|
| **wechat-formatter** | v2.0.0 | 6 种排版风格（tech-blog/tutorial/deep-dive/casual-chat/apple/cyber）+ HTML 生成 |

> 各 skill 的详细能力、工作流程、使用示例见 [docs/skills-overview.md](docs/skills-overview.md)。

## Token 消耗分析

> 帮助用户评估各 skill 的 context 占用，合理规划使用。token 为混合中英文估算值（字符数 × 0.55）。

### 入口文件（SKILL.md，每次调用必加载）

| Skill 入口文件 | 行数 | ~token | 备注 |
|---|---|---|---|
| test-case-engineer-core | 719 | 9,699 | 单文件最重 |
| testing-bundle | 427 | 8,377 | 路由表 + 7 链 |
| review-mode | 390 | 6,385 | 评审模式按需加载 |
| change-impact-analyzer | 398 | 5,969 | |
| wechat-formatter | 296 | 5,833 | |
| state-machine-test-engineer | 308 | 4,970 | |
| bug-analyzer | 333 | 4,969 | |
| test-strategy-engineer | 249 | 4,547 | |
| performance-test-engineer | 216 | 4,028 | 最轻 |
| state-machine-core | 304 | 3,834 | 按需加载 |
| test-case-engineer (SKILL.md) | 123 | 1,877 | 薄入口，转发 core |

### 全量文件（含 knowledge，理论最大占用）

| Skill | 文件数 | ~token | 量级 |
|---|---|---|---|
| wechat-formatter | 31 | 72,637 | 最重（6 风格模板 + 示例） |
| state-machine-test-engineer | 14 | 47,748 | 重（4 行业模板） |
| test-case-engineer | 16 | 42,739 | 重（含 review-mode） |
| change-impact-analyzer | 6 | 19,707 | 中 |
| performance-test-engineer | 7 | 14,240 | 轻 |
| bug-analyzer | 7 | 13,999 | 轻 |
| test-strategy-engineer | 7 | 13,688 | 轻 |
| testing-bundle | 3 | 12,731 | 轻（元 skill） |

**关键发现**：
- `test-case-engineer-core`（9.7k token）是单文件 token 冠军，每次调用必加载
- `wechat-formatter` 全量 72k token，但 6 种风格模板按需加载，实际占用远小于全量
- `testing-bundle` 作为路由入口 8.4k token，每次混合意图请求都会占用
- 各 skill 的 knowledge/ 文件仅在需要时加载，不会全部进入 context

## 快速开始

### 安装

三种安装方式任选其一，详细步骤见 [docs/installation.md](docs/installation.md)：

```bash
# 方式 1（推荐）：npx skills add，跨 runtime 自动适配
npx skills add liu-YLY/my-skills --skill '*' -g -y

# 方式 2：Claude Code 原生 plugin marketplace
/plugin marketplace add liu-YLY/my-skills
/plugin install testing-bundle@my-skill-marketplace

# 方式 3：本地脚本（离线兜底）
cp -r plugins/testing/skills/testing-bundle ~/.claude/skills/
```

安装后重启 runtime，技能自动识别注册。

### 验证

```
# 直接输入技能名称或描述需求即可触发
测试用例工程师
我有一个用户登录功能需要测试...
```

### 使用示例

| 场景 | 触发方式 | 输出示例 |
|---|---|---|
| 生成测试用例 | "我有一个用户登录功能需要测试" | 四阶段流程 + 完整用例 |
| 评审已有用例 | "评审 docs/test-cases.md 的用例质量" | 9 维度评审报告 + 度量报告 |
| Bug 根因分析 | "线上重复扣款，帮我分析根因" | 五步定位法 + 根因报告 |
| 性能瓶颈定位 | "支付接口 RT 飙升，帮我定位瓶颈" | USE 方法 + 瓶颈报告 |
| 微信排版 | "用 tech-blog 风格排版这篇文章" | 格式化 Markdown + HTML |

更多示例见 [docs/skills-overview.md](docs/skills-overview.md)。

## 文档索引

| 文档 | 内容 |
|---|---|
| [docs/skills-overview.md](docs/skills-overview.md) | 各 skill 详细介绍 + 使用示例 |
| [docs/installation.md](docs/installation.md) | 环境要求 + 3 种安装方式 + 故障排查 |
| [docs/project-structure.md](docs/project-structure.md) | 目录树 + 文件职责说明 |
| [AGENTS.md](AGENTS.md) | 跨工具通用 Agent 工作规范 |
| [CHANGELOG.md](CHANGELOG.md) | 变更历史 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |

### 配套 MCP Server

| MCP Server | 版本 | 配套 skill | 功能 |
|---|---|---|---|
| [review-checker](plugins/testing/mcp-servers/review-checker/README.md) | v0.2.0 | test-case-engineer 评审模式 | 9 维度确定性校验 + 度量报告（A-D 评级） |
| [state-machine-testing](plugins/testing/mcp-servers/state-machine-testing/README.md) | v0.1.0 | state-machine-test-engineer | Schema 校验 + 场景穷举 + 覆盖度报告 |

> MCP Server 为可选增强组件，未安装时 skill 降级为纯 LLM 推理，不影响核心能力。

## 配置说明

### Git 提交规范

项目遵循 Conventional Commits 规范，提交信息格式 `<type>(<scope>): <subject>`，默认使用中文描述。完整规范详见 [rules/git-commit-message.md](rules/git-commit-message.md)，TRAE 用户会通过 [.trae/rules/git-commit-message.md](.trae/rules/git-commit-message.md) 自动注入硬约束。

### Git 工作流

采用 feature 分支工作流，禁止直接修改 main，PR 默认使用 squash merge，单个 PR 变更不超过 400 行。详见 [.trae/rules/git-workflow.md](.trae/rules/git-workflow.md)。

### Agent 工作规范

[AGENTS.md](AGENTS.md) 是跨工具通用 Agent 规范入口（TRAE / Cursor / Codex / Cline 均可读取），整合了 Git 提交规范、工作流规范、代码变更规范。

**分层设计**：

| 层级 | 位置 | 作用 | 读取方 |
|---|---|---|---|
| 跨工具通用 | `AGENTS.md` | 软规范 + 全景导航 | 所有 IDE |
| 文档源 | `rules/*.md` | 完整版文档 | 人工 / 引用 |
| TRAE 硬约束 | `.trae/rules/*.md` | 不可违反的硬约束（自动注入） | TRAE |

## 贡献

1. Fork 项目
2. 创建特性分支 `feat/your-skill-v1`
3. 提交更改（遵循 Conventional Commits）
4. 推送并发起 PR
5. Review 通过后使用 squash merge 合并到 main

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT License](LICENSE)

---

**最后更新**：2026 年 7 月 22 日
