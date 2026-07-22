# 项目结构

> 从 README.md 拆分，包含目录树与文件职责说明。

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
│   │   ├── skills/                # runtime 扫描此目录加载 skill
│   │   │   ├── testing-bundle/    # 测试能力 Bundle v3.1.1（4-way 路由入口）
│   │   │   │   ├── SKILL.md       # 入口（路由规则 + 7 条混合意图链）
│   │   │   │   ├── README.md      # Bundle 说明文档
│   │   │   │   └── test-prompts.json
│   │   │   ├── test-strategy-engineer/  # 测试策略工程师 v1.0.0（项目级策略）
│   │   │   │   ├── SKILL.md       # 入口（五阶段流程 + 风险矩阵 + 分层）
│   │   │   │   ├── README.md
│   │   │   │   ├── knowledge/     # risk-matrix / test-pyramid / entry-exit / templates
│   │   │   │   ├── integrations/
│   │   │   │   └── test-prompts.json
│   │   │   ├── test-case-engineer/  # 测试用例工程师 v8.2.0
│   │   │   │   ├── SKILL.md
│   │   │   │   ├── test-case-engineer-core.md
│   │   │   │   ├── README.md
│   │   │   │   ├── knowledge/     # 知识库（bug-patterns.md + review-mode.md：9 维度评审 + 修订闭环 + 增量评审 + 报告文件化，bug-analyzer 共享引用）
│   │   │   │   ├── integrations/
│   │   │   │   ├── scripts/
│   │   │   │   └── docs/
│   │   │   ├── performance-test-engineer/  # 性能测试工程师 v1.0.0（资源/架构层）
│   │   │   │   ├── SKILL.md       # 入口（四阶段流程 + USE 方法）
│   │   │   │   ├── README.md
│   │   │   │   ├── knowledge/     # load-models / metrics / bottleneck-patterns / use-method
│   │   │   │   ├── integrations/
│   │   │   │   └── test-prompts.json
│   │   │   ├── bug-analyzer/      # Bug 分析师 v1.0.0（代码逻辑层）
│   │   │   │   ├── SKILL.md       # 入口 + 核心流程（五步定位法）
│   │   │   │   ├── README.md
│   │   │   │   ├── knowledge/     # 含 bug-patterns-index.md 指向 ../test-case-engineer/knowledge/bug-patterns.md
│   │   │   │   ├── integrations/
│   │   │   │   └── scripts/
│   │   │   └── change-impact-analyzer/  # 变更影响分析师 v1.0.0（独立 skill）
│   │   │       ├── SKILL.md       # 入口 + 四阶段流程
│   │   │       ├── README.md
│   │   │       └── test-prompts.json
│   │   └── mcp-servers/               # 配套 MCP Server（可选增强）
│   │       ├── review-checker/         # review-checker MCP Server v0.2.0（评审 9 维度校验）
│   │       │   ├── src/review_checker_mcp/
│   │       │   │   ├── server.py       # MCP 工具注册（review_test_cases / generate_report）
│   │       │   │   ├── schemas.py      # pydantic 模型
│   │       │   │   └── validators.py   # 9 维度校验逻辑
│   │       │   ├── tests/
│   │       │   ├── README.md
│   │       │   └── pyproject.toml
│   │       └── state-machine-testing/  # state-machine-testing MCP Server v0.1.0（状态机校验）
│   │           ├── src/state_machine_testing_mcp/
│   │           └── tests/
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
├── docs/                         # 项目文档（从 README 拆分）
│   ├── skills-overview.md        # 技能详细介绍
│   ├── installation.md           # 安装指南
│   ├── project-structure.md      # 项目结构（本文件）
│   └── superpowers/              # 设计 spec 与 plan
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
└── knowledge/                     # 全局知识库
    └── products/                  # 产品知识
        ├── README.md              # 产品知识索引
        └── products-template.md   # 知识模板
```
