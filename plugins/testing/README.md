# Testing Bundle Plugin

> 测试能力 plugin，提供项目级测试策略、功能用例生成、性能测试、Bug 根因分析、状态机驱动的状态型需求测试与变更影响分析能力。
>
> 通过 testing-bundle 元 skill 统一路由，按用户意图自动分发到对应子 skill。

## 版本

**版本历史**：详见 [skills/testing-bundle/CHANGELOG.md](skills/testing-bundle/CHANGELOG.md)（当前版本以 skill frontmatter 与 plugin manifest 为准）

## 能力矩阵

| Skill | 版本 | 类型 | 职责 |
|---|---|---|---|
| [testing-bundle](skills/testing-bundle/) | v3.3.0 | 元 skill / 路由入口 | 6-way 意图路由（5 核心 + 1 协同）+ 7 条混合意图链 |
| [test-strategy-engineer](skills/test-strategy-engineer/) | v1.3.0 | 子 skill | 项目级测试策略：风险矩阵 / 分层 / 范围优先级 / 准入准出 |
| [test-case-engineer](skills/test-case-engineer/) | v9.4.1 | 子 skill | 功能用例生成：需求分析 / 测试点提取 / 用例编写 / 自检补全 |
| [performance-test-engineer](skills/performance-test-engineer/) | v1.2.3 | 子 skill | 性能测试方案 + 瓶颈定位（资源/架构层）|
| [bug-analyzer](skills/bug-analyzer/) | v1.2.3 | 子 skill | Bug 根因分析（代码逻辑层）：五步定位法 / 鱼骨图 / 5 Whys |
| [state-machine-test-engineer](skills/state-machine-test-engineer/) | v1.7.5 | 子 skill | 状态机驱动的状态型需求测试：10 类场景穷举 |
| [change-impact-analyzer](skills/change-impact-analyzer/) | v1.4.0 | 协同 skill | 代码改动 → 影响范围与测试内容，需求和用例可选（链 6 协同，亦可独立使用） |
| [test-data-generator](skills/test-data-generator/) | v1.0.0 | 独立 skill | 项目规则配置 → 可重复数据、关联和异常输入 → 独立校验与文件交付 |

test-data-generator 可独立调用，使用 Python 3.11 和其 scripts/requirements.txt；不依赖 MCP，不修改现有六路路由和七条混合链。使用方式见 [运行指南](skills/test-data-generator/integrations/quickstart.md)（v1.0.0）。

**可选配套**：[state-machine-testing MCP Server](mcp-servers/state-machine-testing/) v0.3.0 — 为 state-machine-test-engineer 提供 5 个工具（build / validate / generate / export / coverage，协议层 stdio + HTTP 已端到端联调验证），未安装时降级为纯 LLM 推理。

## 路由架构

```
                    用户测试请求
                         │
                         ▼
              ┌─────────────────────────┐
              │   testing-bundle        │  路由层（只路由，不实现能力）
              └───────────┬─────────────┘
                          │ 6-way 意图判断（5 核心 + 1 协同）
      ┌─────────┬─────────┼───────┬───────────┬──────────────┬─────────────┐
      ▼         ▼         ▼       ▼           ▼              ▼
┌──────────┐┌─────────┐┌──────┐┌───────────┐┌──────────────┐┌─────────────┐
│ strategy ││   case  ││ perf ││    bug    ││state-machine ││change-impact│
│ engineer ││engineer ││engine││ analyzer  ││   engineer   ││   analyzer  │
└──────────┘└─────────┘└──────┘└───────────┘└──────────────┘└─────────────┘
```

详细的 6-way 路由表与 7 条混合意图链见 [skills/testing-bundle/SKILL.md](skills/testing-bundle/SKILL.md)。

评审 MCP：[review-checker](mcp-servers/review-checker/) 支持业务结果数组、可选关键检查点和候选问题分离统计；只提供 stdio 传输。

## 多 runtime 适配

| Runtime | manifest 位置 | 安装命令 |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` | `/plugin install testing-bundle@my-skill-marketplace` |
| Cursor | `.cursor-plugin/plugin.json` | 通过 npx skills add 或手动复制 |
| Codex | `.codex-plugin/plugin.json` | 通过 npx skills add 或手动复制 |

## 目录结构

```
testing/
├── .claude-plugin/plugin.json        # Claude Code plugin manifest
├── .cursor-plugin/plugin.json        # Cursor plugin manifest
├── .codex-plugin/plugin.json         # Codex plugin manifest
├── README.md                         # 本文件
├── mcp-servers/
│   ├── review-checker/               # 用例评审 MCP（stdio）
│   └── state-machine-testing/        # 可选 MCP Server（Python 3.11+）
│       ├── src/state_machine_testing_mcp/
│       ├── tests/{unit,integration,fixtures}
│       ├── pyproject.toml
│       └── README.md
└── skills/
    ├── testing-bundle/               # 路由入口 + CHANGELOG
    ├── test-strategy-engineer/       # 项目级策略
    ├── test-case-engineer/           # 功能用例生成（含 bug-patterns.md，被 bug-analyzer 引用）
    │   └── scripts/{convert_docs.py,requirements.txt}
    ├── performance-test-engineer/    # 性能测试
    ├── bug-analyzer/                 # Bug 根因（bug-patterns-index 指向 test-case-engineer）
    ├── state-machine-test-engineer/  # 状态机测试
    └── change-impact-analyzer/       # 协同 skill（链 6，随 plugin 整体安装）
```

## 关键依赖说明

**bug-analyzer 依赖 test-case-engineer**：bug-analyzer 的 SKILL.md 通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用缺陷模式库。单独安装 bug-analyzer 时该路径会失效，根因分析步骤 2/3 的"对照缺陷模式库"能力会降级（仍有通用模式兜底）。**建议与 test-case-engineer 一起安装**。

## 相关文档

- 根目录 [README.md](../../README.md) — 项目总览与安装方式
- [skills/testing-bundle/CHANGELOG.md](skills/testing-bundle/CHANGELOG.md) — 版本历史
- [../../docs/superpowers/specs/2026-07-04-testing-skills-expansion-design.md](../../docs/superpowers/specs/2026-07-04-testing-skills-expansion-design.md) — 测试能力扩展设计
- [../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md](../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md) — 状态机测试设计
