# Testing Bundle Plugin

> 测试能力 plugin，提供项目级测试策略、功能用例生成、性能测试、Bug 根因分析、状态机驱动的状态型需求测试与变更影响分析能力。
>
> 通过 testing-bundle 元 skill 统一路由，按用户意图自动分发到对应子 skill。

## 版本

**当前版本**：v3.0.0（详见 [skills/testing-bundle/CHANGELOG.md](skills/testing-bundle/CHANGELOG.md)）

## 能力矩阵

| Skill | 版本 | 类型 | 职责 |
|---|---|---|---|
| [testing-bundle](skills/testing-bundle/) | v3.0.0 | 元 skill / 路由入口 | 5-way 意图路由 + 5 条混合意图链 |
| [test-strategy-engineer](skills/test-strategy-engineer/) | v1.0.0 | 子 skill | 项目级测试策略：风险矩阵 / 分层 / 范围优先级 / 准入准出 |
| [test-case-engineer](skills/test-case-engineer/) | v8.0.0 | 子 skill | 功能用例生成：需求分析 / 测试点提取 / 用例编写 / 自检补全 |
| [performance-test-engineer](skills/performance-test-engineer/) | v1.0.0 | 子 skill | 性能测试方案 + 瓶颈定位（资源/架构层）|
| [bug-analyzer](skills/bug-analyzer/) | v1.0.0 | 子 skill | Bug 根因分析（代码逻辑层）：五步定位法 / 鱼骨图 / 5 Whys |
| [state-machine-test-engineer](skills/state-machine-test-engineer/) | v1.0.0 | 子 skill | 状态机驱动的状态型需求测试：10 类场景穷举 |
| [change-impact-analyzer](skills/change-impact-analyzer/) | v1.0.0 | 独立 skill | git 代码变更与测试用例交叉分析，不集成到 bundle |

**可选配套**：[state-machine-testing MCP Server](mcp-servers/state-machine-testing/) v0.1.0 — 为 state-machine-test-engineer 提供 5 个工具（build / validate / generate / export / coverage），未安装时降级为纯 LLM 推理。

## 路由架构

```
                    用户测试请求
                         │
                         ▼
              ┌─────────────────────────┐
              │   testing-bundle v3.0.0 │  路由层（只路由，不实现能力）
              └───────────┬─────────────┘
                          │ 5-way 意图判断
        ┌─────────┬───────┼───────┬───────────┬──────────────┐
        ▼         ▼       ▼       ▼           ▼
  ┌──────────┐┌─────────┐┌──────┐┌───────────┐┌──────────────┐
  │ strategy ││   case  ││ perf ││    bug    ││state-machine │
  │ engineer ││engineer ││engine││ analyzer  ││   engineer   │
  └──────────┘└─────────┘└──────┘└───────────┘└──────────────┘
```

详细的 5-way 路由表与 5 条混合意图链见 [skills/testing-bundle/SKILL.md](skills/testing-bundle/SKILL.md)。

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
│   └── state-machine-testing/        # 可选 MCP Server（Python 3.11+）
│       ├── src/state_machine_testing_mcp/
│       ├── tests/{unit,integration,fixtures}
│       ├── pyproject.toml
│       └── README.md
├── scripts/
│   ├── convert_docs.py               # 文档转换降级方案
│   └── requirements.txt
└── skills/
    ├── testing-bundle/               # 路由入口 + CHANGELOG
    ├── test-strategy-engineer/       # 项目级策略
    ├── test-case-engineer/           # 功能用例生成（含 bug-patterns.md，被 bug-analyzer 引用）
    ├── performance-test-engineer/    # 性能测试
    ├── bug-analyzer/                 # Bug 根因（bug-patterns-index 指向 test-case-engineer）
    ├── state-machine-test-engineer/  # 状态机测试
    └── change-impact-analyzer/       # 独立 skill，不集成到 bundle
```

## 关键依赖说明

**bug-analyzer 依赖 test-case-engineer**：bug-analyzer 的 SKILL.md 通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用缺陷模式库。单独安装 bug-analyzer 时该路径会失效，根因分析步骤 2/3 的"对照缺陷模式库"能力会降级（仍有通用模式兜底）。**建议与 test-case-engineer 一起安装**。

## 相关文档

- 根目录 [README.md](../../README.md) — 项目总览与安装方式
- [skills/testing-bundle/CHANGELOG.md](skills/testing-bundle/CHANGELOG.md) — 版本历史
- [../../docs/superpowers/specs/2026-07-04-testing-skills-expansion-design.md](../../docs/superpowers/specs/2026-07-04-testing-skills-expansion-design.md) — 测试能力扩展设计
- [../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md](../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md) — 状态机测试设计
