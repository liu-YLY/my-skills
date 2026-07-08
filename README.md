# My Skill - AI 技能集合项目

> 基于 AI 的智能技能系统，提供测试策略、测试用例生成、性能测试、Bug 根因分析、变更影响分析、微信公众号排版等专业技能

## 项目简介

My Skill 是一个 AI 驱动的技能集合项目，旨在通过人工智能技术提升工作效率。项目包含多个专业领域的技能模块，每个技能都经过精心设计，能够理解用户需求并提供高质量的专业输出。

### 核心特性

- **AI 赋能**：基于大语言模型，理解自然语言需求
- **专业化输出**：每个技能都有明确的输出规范和质量标准
- **模块化设计**：技能独立运行，可按需组合使用
- **知识库支持**：内置专业知识库，确保输出的专业性和准确性
- **多场景适用**：覆盖测试、排版、文档生成等多个工作场景

## 主要技能

> **技能分组**：项目采用 plugin marketplace 模式（参考 [obra/superpowers](https://github.com/obra/superpowers)），单 repo 内通过 `.claude-plugin/marketplace.json` 注册两个独立 plugin：
> - **testing-bundle plugin**：testing-bundle + test-strategy-engineer + test-case-engineer + performance-test-engineer + bug-analyzer（位于 `plugins/testing/skills/`）
> - **wechat-formatter plugin**：wechat-formatter（位于 `plugins/wechat-formatter/skills/`）
>
> 另有独立 skill **change-impact-analyzer**（变更影响分析）位于 `plugins/testing/skills/`，不集成到 bundle，可单独使用。
>
> 用户可按需安装整个 plugin（一键装上 plugin 内所有 skill），详见下方「安装方式」。

### 1. Testing Bundle (testing-bundle)

**版本**：v2.0.0  
**功能**：测试能力 bundle 入口，统一路由到 4 个子 skill：test-strategy-engineer（项目级策略）/ test-case-engineer（功能用例生成）/ performance-test-engineer（性能测试）/ bug-analyzer（Bug 根因分析）。

> Bundle 是元 skill，本身不实现具体能力，而是根据用户意图自动路由到对应子 skill。

**路由规则**（4-way 路由 + 4 条混合意图链）：

| 用户意图关键词 | 路由到 | 说明 |
|---------------|--------|------|
| 测试策略、测试计划、测试分层、风险矩阵、准入准出、测试范围与优先级 | test-strategy-engineer | 项目级策略 |
| 生成/评审测试用例、需求分析、单功能测试策略 | test-case-engineer | 功能用例生成 |
| 性能测试、负载测试、压力测试、TPS、响应时间、瓶颈、容量评估 | performance-test-engineer | 性能场景 + 瓶颈分析 |
| Bug 根因分析、缺陷定位、5 Whys、鱼骨图、防御性用例反推 | bug-analyzer | 功能缺陷根因 |
| 混合意图（4 条链） | 见 SKILL.md 混合意图链 | 转交点 🔴 CHECKPOINT |
| 意图不明确 | 追问用户 | 列出 4 个子 skill 让用户选择 |

**4 条混合意图链**：
- 链 1：Bug 分析 + 补充用例 → bug-analyzer → case-engineer
- 链 2：测试策略 + 分层用例 → strategy → case-engineer
- 链 3：性能测试 + 瓶颈定位 → performance（内部完成）
- 链 4：性能瓶颈 + 代码缺陷 → performance → bug-analyzer

**安装方式**：
- **整体安装（推荐）**：安装 testing-bundle + 4 个子 skill 共 5 个 skill
- **按需安装**：仅安装需要的子 skill（bug-analyzer 单独安装时缺陷模式库引用会降级）

### 1a. 测试策略工程师 (test-strategy-engineer)

**版本**：v1.0.0  
**功能**：扮演资深测试架构师角色，专注项目级测试策略制定，输出风险矩阵 + 分层策略 + 范围优先级 + 准入准出。

> testing-bundle v2.0.0 新增子 skill，与 test-case-engineer 的粒度边界：本 skill 是项目级（整体），test-case-engineer 是单功能级。

**核心能力**：
- **风险矩阵构建**：5 维量化评估（业务复杂度/变更频率/历史缺陷/外部依赖/数据敏感性）
- **测试分层策略**：按项目类型选择分层比例（经典金字塔/橄榄型/倒金字塔/沙漏型）
- **范围与优先级**：必测 P0 + 选测 P1 + 不测 P2，强制分级规则
- **准入准出标准**：具体阈值（覆盖率/通过率/缺陷遗留），禁止模糊措辞

**适用场景**：
- ✅ 项目级测试策略制定
- ✅ 风险矩阵构建与优先级排序
- ✅ 测试分层设计（单元/接口/UI 比例）
- ✅ 准入准出标准制定

**工作流程**：
```
阶段 1: 项目特征 → 阶段 2: 风险矩阵 → 阶段 3: 测试分层 → 🔴 CHECKPOINT → 阶段 4: 范围准入准出 → 阶段 5（可选）: 资源附录
```

**使用示例**：
```
用户：我们有一个电商项目即将启动测试，包含用户中心、商品、订单、支付等模块，团队 20 人，请帮我制定测试策略

AI（test-strategy-engineer）：
## 阶段 1: 项目特征理解

**项目类型**：新项目
**规模**：4 个核心模块，团队 20 人
**质量目标**：功能正确性 + 性能 + 安全

[展示给用户确认后继续阶段 2 风险矩阵...]
```

### 1b. 测试用例工程师 (test-case-engineer)

**版本**：v8.0.0  
**功能**：扮演资深测试工程师角色，AI 赋能用例生成，深入理解需求与产品现状，精准提取测试点，输出完整全面可落地的测试用例。

> v8.0.0 起由原 test-engineer v7.0.0 拆分而来，专注正向用例生成。Bug 根因分析能力已迁移至 bug-analyzer skill。

**核心能力**：
- **需求分析**：深入理解需求文档，提取业务规则和测试点
- **测试点提取**：系统性扫描 7 个维度，确保测试覆盖无遗漏
- **用例生成**：AI 生成 70%-90% 的基础用例，人工审核补充
- **产品知识库**：按产品维度沉淀业务知识，增强测试针对性

**适用场景**：
- ✅ 编写测试用例：从需求文档自动生成完整测试用例
- ✅ 评审测试用例：检查用例质量和覆盖度
- ✅ 需求分析：提取业务规则和测试点
- ✅ 单功能测试策略设计

**工作流程**：
```
阶段 1: 理解需求 → 阶段 2: 提取测试点 → 阶段 3: 编写用例 → 阶段 4: 自检补全
```

**使用示例**：
```
用户：我有一个用户登录功能需要测试，需求如下：用户通过手机号+验证码登录...

AI（test-case-engineer）：
## 阶段 1: 需求理解

**功能概述**：用户通过手机号+验证码登录系统

[展示给用户确认后继续阶段 2...]
```

### 1c. 性能测试工程师 (performance-test-engineer)

**版本**：v1.0.0  
**功能**：扮演资深性能测试工程师角色，专注性能测试方案设计与瓶颈定位（资源/架构层），通过 USE 方法 + 4 种负载模型 + 6 类瓶颈模式提供完整方案。

> testing-bundle v2.0.0 新增子 skill，聚焦资源/架构层；当代码逻辑层缺陷（死锁/N+1/内存泄漏）时转交 bug-analyzer。

**核心能力**：
- **4 种负载模型**：基准/阶梯/浪涌/峰值，按场景选择
- **指标体系与阈值**：RT/TPS/错误率/资源饱和度，含 SLA 阈值表
- **USE 方法**：资源三角（Utilization/Saturation/Errors）定位瓶颈
- **6 类瓶颈模式**：CPU/内存/IO/网络/连接池/缓存，含层边界声明

**适用场景**：
- ✅ 性能测试方案设计（负载模型 + 场景 + 指标阈值）
- ✅ 性能瓶颈定位（资源/架构层）
- ✅ 容量评估与扩容建议
- ✅ 性能问题转交判断（资源层 vs 代码层）

**工作流程**：
```
阶段 1: 需求理解 → 阶段 2: 场景设计 → 🔴 CHECKPOINT → 阶段 3: 瓶颈定位 → 阶段 4: 转交判断
```

**使用示例**：
```
用户：我们的支付系统要做性能测试，预期峰值 5000 TPS，关注 P99 响应时间

AI（performance-test-engineer）：
## 阶段 1: 性能需求理解

**关键指标**：TPS ≥ 5000，P99 ≤ 800ms
**负载模型推荐**：峰值模型（大促场景）

[展示给用户确认后继续阶段 2 场景设计...]
```

### 1d. Bug 分析师 (bug-analyzer)

**版本**：v1.0.0  
**功能**：扮演资深测试工程师角色，专注于 Bug 根因分析与缺陷定位（代码逻辑层）。使用五步定位法、鱼骨图、5 Whys 等方法，输出结构化根因分析报告与防御性测试用例建议。

**核心能力**：
- **五步定位法**：复现 → 隔离 → 定位 → 验证 → 报告
- **根因分析框架**：鱼骨图（人/机/料/法/环）+ 5 Whys + 因果链追溯
- **防御性用例反推**：基于根因输出防御性测试点清单
- **结构化报告**：标准根因分析报告模板

**适用场景**：
- ✅ Bug 根因分析：系统性定位 Bug 根本原因
- ✅ 缺陷定位：缩小问题范围，定位到具体组件
- ✅ 防御性用例反推：基于根因生成防御性测试点
- ✅ 性能瓶颈转交的代码层缺陷分析（死锁/N+1/内存泄漏）

**工作流程**：
```
步骤 1: 复现 → 步骤 2: 隔离 → 步骤 3: 定位 → 步骤 4: 验证 → 步骤 5: 报告
```

**使用示例**：
```
用户：用户反馈提交订单时偶尔会重复扣款，请帮我分析可能的原因

AI（bug-analyzer）：
## 步骤 1: 复现

**现象**：提交订单时偶尔出现重复扣款
**复现率**：偶发约 5%

[展示给用户确认后继续步骤 2 隔离...]
```

### 1e. 变更影响分析师 (change-impact-analyzer)

**版本**：v1.0.0  
**功能**：扮演资深测试工程师角色，将 git 代码变更与测试用例交叉分析，发现行为变更影响和覆盖缺口，输出可落地的影响报告。

> 独立 skill，不集成到 testing-bundle，可单独使用。

**核心能力**：
- **四阶段工作流**：收集输入 → Diff 解析 → 交叉分析 → 生成报告
- **三种 diff 模式**：本地改动、分支对比、commit 范围，自动推断
- **两类问题检测**：行为变更影响（代码改动导致用例预期不成立）+ 覆盖缺口（改动功能无用例覆盖）
- **灵活用例输入**：支持 Markdown/CSV/JSON 格式

**适用场景**：
- ✅ PR/MR 前检查：分析分支改动对现有用例的影响
- ✅ 回归风险评估：检查 commit 范围的变更是否破坏用例
- ✅ 覆盖缺口分析：找出改动功能中未被用例覆盖的部分
- ✅ 版本发布前验证：对比 release 分支的变更影响

**工作流程**：
```
阶段 1: 收集输入 → 🔴 CHECKPOINT → 阶段 2: Diff 解析 → 🔴 CHECKPOINT → 阶段 3: 交叉分析 → 阶段 4: 生成报告
```

**使用示例**：
```
用户：帮我分析一下当前改动对测试用例的影响，用例在 docs/test-cases.md

AI（change-impact-analyzer）：
## 阶段 1: 收集输入

**分析范围**：本地未提交改动
**用例文件**：docs/test-cases.md（解析出 42 条用例）

[🔴 CHECKPOINT 确认后继续阶段 2 Diff 解析...]
```

### 2. 微信公众号排版 (wechat-formatter)

**版本**：v2.0.0  
**功能**：微信公众号文章排版技能，提供多种适用于互联网/技术领域的排版风格模板。自动分析用户文章内容，按选定风格完成排版，输出为可直接复制到公众号编辑器的格式化 Markdown 文件。

**核心能力**：
- **内容分析**：自动识别文章要素（标题层级、代码块、列表、要点）
- **风格匹配**：提供 6 种专业排版风格，智能推荐最适合的风格
- **排版执行**：严格按模板规则转换，确保格式一致性
- **质量校验**：覆盖度 + 可读性 + 公众号兼容性三项检查
- **HTML 生成**：一键生成带内联样式的 HTML 文件，可直接粘贴到公众号

**六大排版风格**：

| 风格 | 代号 | 适用场景 | 核心视觉特征 |
|------|------|----------|-------------|
| **技术博客** | `tech-blog` | 编程教程、技术分享、工具介绍 | 导读框 + 中文编号章节 + 核心观点框 + 分割线 + 脚注式参考 |
| **教程指南** | `tutorial` | 操作指南、最佳实践、配置说明 | 目标框 + Step 五段式 + 4 种提示框(TIP/WARNING/NOTE/CHECK) + FAQ |
| **深度干货** | `deep-dive` | 原理剖析、架构分析、技术复盘 | 摘要框 + 纯文本目录 + 核心结论框 + 图表编号 + 参考带说明 |
| **轻松聊天** | `casual-chat` | 经验总结、技术随笔、行业思考 | 自然开场 + 短段落 + `—` 分隔 + Emoji 点缀 + 互动引导 |
| **苹果风** | `apple` | 产品设计、架构哲学、技术选型 | 极简留白 + 圆角卡片引用 + 无编号无 Emoji + Apple 品牌色 |
| **赛博朋克** | `cyber` | 安全技术、前沿探索、极客文化 | 暗黑背景 + 霓虹色调 + 发光代码块 + 系统弹窗风格引用 |

**使用示例**：
```
用户：帮我把这篇技术文章排版成 tech-blog 风格

AI（wechat-formatter）：
## 阶段 1: 内容分析

**文章类型**：技术教程
**核心要素**：
- 标题层级：H2-H3
- 代码块：2 处（Python 示例）
- 列表：3 处有序列表
- 要点：5 个核心观点

**推荐风格**：tech-blog（技术博客风格）

[继续阶段 2: 风格选择...]
```

## 项目结构

```
my-skill/
├── .gitignore                     # Git 忽略文件配置
├── README.md                      # 项目说明文档（本文件）
├── AGENTS.md                      # 跨工具通用 Agent 工作规范（TRAE/Cursor/Codex/Cline）
│
├── .claude-plugin/                # Claude Code plugin marketplace 注册
│   └── marketplace.json           # 列出 testing-bundle + wechat-formatter 两个 plugin
│
├── .darwin-results/               # darwin-skill 评估结果（基线/对比/总结）
│   ├── results.tsv                # 优化日志（9 列含 eval_mode）
│   ├── 2026-07-04-baseline.md     # 优化前基线报告
│   ├── 2026-07-04-comparison.md   # 优化前后对比报告
│   └── 2026-07-04-split-summary.md # 拆分总结文章
│
├── scripts/                       # 项目级工具脚本
│   └── install-testing-bundle.ps1 # 测试 bundle 本地安装脚本（plugin 模式兜底）
│
├── plugins/                       # Plugin 目录（每个子目录 = 一个独立 plugin）
│   ├── testing/                   # Plugin: testing-bundle
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json        # Claude Code plugin manifest
│   │   ├── .cursor-plugin/
│   │   │   └── plugin.json        # Cursor plugin manifest
│   │   ├── .codex-plugin/
│   │   │   └── plugin.json        # Codex plugin manifest
│   │   └── skills/                # runtime 扫描此目录加载 skill
│   │       ├── testing-bundle/    # 测试能力 Bundle v2.0.0（4-way 路由入口）
│   │       │   ├── SKILL.md       # 入口（路由规则 + 4 条混合意图链）
│   │       │   ├── README.md      # Bundle 说明文档
│   │       │   └── test-prompts.json
│   │       ├── test-strategy-engineer/  # 测试策略工程师 v1.0.0（项目级策略）
│   │       │   ├── SKILL.md       # 入口（五阶段流程 + 风险矩阵 + 分层）
│   │       │   ├── README.md
│   │       │   ├── knowledge/     # risk-matrix / test-pyramid / entry-exit / templates
│   │       │   ├── integrations/
│   │       │   └── test-prompts.json
│   │       ├── test-case-engineer/  # 测试用例工程师 v8.0.0
│   │       │   ├── SKILL.md
│   │       │   ├── test-case-engineer-core.md
│   │       │   ├── README.md
│   │       │   ├── knowledge/     # 知识库（bug-patterns.md 在此处，bug-analyzer 共享引用）
│   │       │   ├── integrations/
│   │       │   ├── scripts/
│   │       │   └── docs/
│   │       ├── performance-test-engineer/  # 性能测试工程师 v1.0.0（资源/架构层）
│   │       │   ├── SKILL.md       # 入口（四阶段流程 + USE 方法）
│   │       │   ├── README.md
│   │       │   ├── knowledge/     # load-models / metrics / bottleneck-patterns / use-method
│   │       │   ├── integrations/
│   │       │   └── test-prompts.json
│   │       └── bug-analyzer/      # Bug 分析师 v1.0.0（代码逻辑层）
│   │           ├── SKILL.md       # 入口 + 核心流程（五步定位法）
│   │           ├── README.md
│   │           ├── knowledge/     # 含 bug-patterns-index.md 指向 ../test-case-engineer/knowledge/bug-patterns.md
│   │           ├── integrations/
│   │           └── scripts/
│   │       └── change-impact-analyzer/  # 变更影响分析师 v1.0.0（独立 skill）
│   │           ├── SKILL.md       # 入口 + 四阶段流程
│   │           ├── README.md
│   │           └── test-prompts.json
│   │
│   └── wechat-formatter/          # Plugin: wechat-formatter
│       ├── .claude-plugin/
│       │   └── plugin.json        # Claude Code plugin manifest
│       ├── .cursor-plugin/
│       │   └── plugin.json        # Cursor plugin manifest
│       ├── .codex-plugin/
│       │   └── plugin.json        # Codex plugin manifest
│       └── skills/
│           └── wechat-formatter/  # 微信公众号排版技能 v2.0.0
│               ├── SKILL.md
│               ├── README.md
│               ├── templates/     # 6 种风格模板
│               ├── styles/        # CSS 样式
│               ├── references/    # 排版规则
│               ├── examples/      # 示例文件
│               ├── scripts/       # md2wechat.py
│               └── knowledge/     # wechat-traps.md
│
├── .trae/                         # TRAE IDE 专用配置
│   └── rules/                     # TRAE 自动注入的硬约束规则（alwaysApply: true）
│       ├── git-commit-message.md  # Conventional Commits 提交信息硬约束
│       └── git-workflow.md        # 分支保护/命名/PR流程/版本历史保护硬约束
│
├── rules/                         # 规则文档源（跨工具通用，不自动注入）
│   ├── git-commit-message.md      # Git 提交信息规范（完整版）
│   └── no-formatting.md           # 代码格式化规范
│
├── knowledge/                     # 全局知识库
│   └── products/                  # 产品知识
│       ├── README.md              # 产品知识索引
│       └── products-template.md   # 知识模板
│
└── 微信公众号/                     # 微信公众号相关文件
    ├── 已有文章/                   # 已有文章
    │   ├── 印象深刻的几个bug - 记录.md
    │   └── 软件测试学习路线.md
    ├── playwright学习路线.md
    └── playwright学习路线_formatted_tech-blog.md
```

## 快速开始

### 环境要求

- **操作系统**：Windows / macOS / Linux
- **运行环境**：支持 AI 技能的 IDE（Claude Code / Cursor / Codex / OpenCode 等）
- **Node.js**（推荐）：v18+（用于 skills CLI）
- **Python 环境**（可选）：Python 3.8+（用于工具脚本）

### 安装与配置

本项目支持三种安装方式，按推荐程度排序：

| 方式 | 适用场景 | 优势 | 操作复杂度 |
|------|----------|------|------------|
| **npx skills add** | 跨平台、跨 runtime | 自动适配 70+ runtime，按 skill 粒度选择 | ⭐⭐ |
| **Plugin Marketplace** | Claude Code 用户 | 原生支持，一键安装整个 plugin | ⭐ |
| **本地脚本** | 离线安装、无 Node.js | 无需网络，灵活控制安装路径 | ⭐⭐⭐ |

#### ⚠️ 重要提示

**bug-analyzer 依赖说明**：bug-analyzer 的 SKILL.md 引用 `../test-case-engineer/knowledge/bug-patterns.md`（缺陷模式库）。单独安装时该相对路径会失效，根因分析步骤 2/3 的"对照缺陷模式库"能力会降级（仍有通用模式兜底）。**建议与 test-case-engineer 一起安装**。

---

#### 方式 1：npx skills add（推荐）

使用 [skills CLI](https://skills.sh)（Agent 界的 npm）安装，自动适配 Claude Code / Cursor / Codex / OpenCode 等 70+ runtime。

**前置条件**：安装 Node.js v18+

**基础操作**：

```bash
# 列出仓库所有可安装的 skill
npx skills add liu-YLY/my-skills --list
```

**安装方式**：

```bash
# 安装所有 skill（推荐，包含 testing-bundle + 4 个子 skill + wechat-formatter）
npx skills add liu-YLY/my-skills --skill '*' -g -y

# 仅安装测试能力 bundle（5 个 skill）
npx skills add liu-YLY/my-skills --skill 'testing-bundle' --skill 'test-*' -g -y

# 仅安装微信公众号排版 skill
npx skills add liu-YLY/my-skills --skill 'wechat-formatter' -g -y

# 指定安装到特定 runtime
npx skills add liu-YLY/my-skills --skill 'testing-bundle' -a claude-code -a cursor -g -y
```

**参数说明**：

| 参数 | 说明 |
|------|------|
| `-g, --global` | 全局安装（`~/<agent>/skills/`），不加则装到项目级（`./<agent>/skills/`） |
| `-a, --agent <agents...>` | 指定目标 runtime（claude-code / cursor / codex / opencode 等） |
| `-s, --skill <skills...>` | 按 skill 名选择，支持通配符（如 `test-*`），`'*'` 表示全部 |
| `-y, --yes` | 跳过确认提示（CI/CD 友好） |
| `--copy` | 复制文件而非 symlink（默认 symlink，便于更新） |

---

#### 方式 2：Plugin Marketplace（Claude Code 原生）

Claude Code 用户可通过原生 `/plugin` 命令，按 plugin 粒度一键安装。

```
# 注册 marketplace（只需执行一次）
/plugin marketplace add liu-YLY/my-skills

# 安装测试能力 bundle（含 testing-bundle + 4 个子 skill）
/plugin install testing-bundle@my-skill-marketplace

# 安装微信公众号排版 skill
/plugin install wechat-formatter@my-skill-marketplace
```

> 本项目采用「单 repo + marketplace 多 plugin」结构（参考 [obra/superpowers](https://github.com/obra/superpowers)）。Cursor/Codex 用户可指向 plugin source 子目录安装，详见各 runtime 的 plugin 文档。

---

#### 方式 3：本地脚本（兜底方案）

适用于未安装 Node.js 或需要离线安装的场景。

**Windows（PowerShell）**：
```powershell
# 安装测试能力 bundle
.\scripts\install-testing-bundle.ps1
# 默认装到 ~\.claude\skills

# 指定安装目录
.\scripts\install-testing-bundle.ps1 -TargetDir "C:\Users\<用户名>\.cursor\skills"

# 卸载
.\scripts\install-testing-bundle.ps1 -Uninstall
```

**macOS / Linux**：
```bash
# 手动复制技能目录到目标 runtime 的 skills 目录
# Claude Code: ~/.claude/skills/
# Cursor: ~/.cursor/skills/
# Codex: ~/.codex/skills/

# 示例：复制 testing-bundle 到 Claude Code
cp -r plugins/testing/skills/testing-bundle ~/.claude/skills/
cp -r plugins/testing/skills/test-strategy-engineer ~/.claude/skills/
cp -r plugins/testing/skills/test-case-engineer ~/.claude/skills/
cp -r plugins/testing/skills/performance-test-engineer ~/.claude/skills/
cp -r plugins/testing/skills/bug-analyzer ~/.claude/skills/

# 复制 wechat-formatter
cp -r plugins/wechat-formatter/skills/wechat-formatter ~/.claude/skills/
```

---

#### 后续步骤

安装完成后，请执行以下操作：

1. **安装工具脚本依赖**（可选，用于 test-case-engineer 内的 Python 脚本）
   ```bash
   cd plugins/testing/skills/test-case-engineer/scripts
   pip install -r requirements.txt
   ```

2. **重启 runtime** 让其重新扫描 skills 目录，技能会自动识别并注册

3. **验证安装**：在 runtime 中输入技能名称（如 "测试用例工程师"），确认技能已激活

### 使用方式

#### 测试用例工程师技能（test-case-engineer）

1. **基础使用**
   ```
   直接描述你的测试需求，技能会自动触发
   示例：我有一个用户注册功能需要测试...
   ```

2. **快速模式**
   ```
   使用快速模式：测试用户登录功能，需求如下...
   ```

3. **指定模式**
   ```
   使用探索式模式测试支付功能...
   ```

#### 微信公众号排版技能

1. **基础使用**
   ```
   帮我排版这篇技术文章
   [粘贴文章内容]
   ```

2. **指定风格**
   ```
   使用 tech-blog 风格排版这篇文章
   [粘贴文章内容]
   ```

3. **快速排版**
   ```
   快速排版：用 tutorial 风格
   [粘贴文章内容]
   ```

## 使用示例

### 示例 1：测试用例生成

**输入**：
```
我有一个电商购物车功能需要测试，需求如下：
1. 用户可以添加商品到购物车
2. 可以修改商品数量
3. 可以删除商品
4. 显示商品总价
5. 支持批量操作
```

**输出**：
```markdown
### TC_CART_ADD_001: 添加商品到购物车

- **优先级**: P0
- **类型**: functional
- **需求追溯**: Story-101 / TP-01

**前置条件**:
- 用户已登录
- 商品库存充足

**测试步骤与预期结果**:

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 浏览商品详情页 | 页面显示商品信息和"加入购物车"按钮 |
| 2 | 点击"加入购物车"按钮 | 提示"已添加到购物车"，购物车图标数量+1 |
| 3 | 进入购物车页面 | 显示已添加的商品，数量为1 |
```

### 示例 2：文章排版

**输入**：
```markdown
# Python 测试框架对比

pytest 和 unittest 是 Python 中最常用的两个测试框架。本文将对比它们的优缺点。

## pytest 优点

1. 语法简洁，无需继承 TestCase 类
2. 丰富的插件生态
3. 参数化测试支持好

## unittest 优点

1. 标准库自带，无需安装
2. 文档完善
3. 与 IDE 集成好
```

**输出**（tech-blog 风格）：
```markdown
<!--
排版风格：技术博客 (tech-blog)
排版时间：2026-06-28
原始文件：python-testing-frameworks.md
图片占位：0 处
代码块：0 处
-->

# Python 测试框架对比

> **📖 导读**
>
> 本文约 **800 字**，预计阅读 **3 分钟**。文章将对比 Python 中最常用的两个测试框架 pytest 和 unittest，帮助你选择最适合项目的测试方案。适合 **Python 开发者** 和 **测试工程师** 阅读。

---

## 一、前言

在 Python 测试领域，**pytest** 和 **unittest** 是两个最主流的框架。

本文将从多个维度对比这两个框架，帮助你根据项目需求做出最佳选择。

---

## 二、pytest 的优势

**pytest** 是一个成熟的全功能测试框架，具有以下优势：

- **语法简洁**：无需继承 TestCase 类，使用普通的 assert 语句
- **插件生态**：拥有 800+ 插件，覆盖各种测试场景
- **参数化支持**：内置 `@pytest.mark.parametrize` 装饰器

---

## 三、unittest 的优势

**unittest** 是 Python 标准库自带的测试框架：

- **零依赖**：标准库自带，无需额外安装
- **文档完善**：官方文档详细，学习资源丰富
- **IDE 集成**：与主流 IDE 集成良好

---

## 四、如何选择

| 场景 | 推荐框架 |
|------|----------|
| 新项目 | pytest |
| 已有 unittest 项目 | 继续使用 unittest |
| 需要丰富插件 | pytest |
| 追求零依赖 | unittest |

---

**参考资料**

[1] pytest 官方文档: https://docs.pytest.org/
[2] unittest 官方文档: https://docs.python.org/3/library/unittest.html

---

*如果本文对你有帮助，欢迎 **点赞、在看** 支持 👏*
```

## 配置说明

### Git 提交规范

项目遵循 Conventional Commits 规范，提交信息格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 仅文档变更
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动
- `ci`: CI/CD 配置变更
- `build`: 影响构建系统或外部依赖的变更
- `revert`: 回滚之前的提交

完整规范详见 [rules/git-commit-message.md](rules/git-commit-message.md)，TRAE 用户会通过 [.trae/rules/git-commit-message.md](.trae/rules/git-commit-message.md) 自动注入硬约束。

### Git 工作流规范

项目采用 feature 分支工作流，硬约束详见 [.trae/rules/git-workflow.md](.trae/rules/git-workflow.md)：

- **禁止**直接修改 `main` / `master` 分支
- Feature 分支命名：`feat/[skill-name]-[version 或 description]`
- 修复分支命名：`fix/[bug 描述]`
- 重构分支命名：`refactor/[模块 描述]`
- 大范围拆分/重构前必须创建备份分支：`backup/[pre-xxx]`
- PR 合并必须使用 `--no-ff` 保留分支历史

### 代码格式化规范

- **严格禁止**对原有代码进行任何格式化操作
- 只有在用户明确要求时才能进行格式化
- 新增代码应遵循已有代码的风格和格式

完整规范详见 [rules/no-formatting.md](rules/no-formatting.md)。

### Agent 工作规范（跨工具）

[AGENTS.md](AGENTS.md) 是跨工具通用 Agent 规范入口（TRAE / Cursor / Codex / Cline 均可读取），整合了 Git 提交规范、工作流规范、代码变更规范、Skill 开发约束的完整说明。

**分层设计**：

| 层级 | 位置 | 作用 | 读取方 |
|---|---|---|---|
| 跨工具通用 | `AGENTS.md` | 软规范 + 全景导航 | 所有 IDE |
| 文档源 | `rules/*.md` | 完整版文档 | 人工 / 引用 |
| TRAE 硬约束 | `.trae/rules/*.md` | 不可违反的硬约束（自动注入） | TRAE |

## 贡献指南

### 如何贡献

1. Fork 项目
2. 创建特性分支（命名规范见 [Git 工作流规范](#git-工作流规范)）
   ```bash
   git checkout -b feat/your-skill-v1
   ```
3. 提交更改（遵循 [Conventional Commits](#git-提交规范)）
   ```bash
   git commit -m 'feat: 新增某技能的某能力'
   ```
4. 推送到远程分支
   ```bash
   git push -u origin feat/your-skill-v1
   ```
5. 发起 Pull Request，等待 review
6. Review 通过后使用 `--no-ff` 合并到 `main`

### 开发规范

- 遵循项目现有的代码风格
- 确保所有测试通过
- 更新相关文档
- 提交前运行代码检查工具

### 报告问题

使用 GitHub Issues 报告问题，请包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 致谢

- 感谢开源社区提供的优秀工具和库
- 特别感谢 AI 技术的发展，让智能技能成为可能

## 联系方式

- **项目主页**：[GitHub Repository]
- **问题反馈**：[GitHub Issues]
- **邮箱**：[your-email@example.com]

---

**最后更新**：2026 年 7 月 8 日

*如果这个项目对你有帮助，请给我们一个 ⭐️*
