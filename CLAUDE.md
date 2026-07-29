# CLAUDE.md

> 本文件为 Claude Code 提供项目专用上下文，与 [AGENTS.md](AGENTS.md) 互补：
> - `AGENTS.md` 是跨工具通用 AI 助手规范（Git 提交、工作流、代码变更）
> - `CLAUDE.md` 在此基础上补充 Claude Code 在本仓库工作时的特定约定

## 项目概览

my-skill 是一个 AI 技能集合仓库，采用「单 repo + marketplace 多 plugin」结构（参考 [obra/superpowers](https://github.com/obra/superpowers) 与 [anthropics/claude-code](https://github.com/anthropics/claude-code)）。

- 顶层 marketplace 注册：[.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- Plugin 集合索引：[plugins/README.md](plugins/README.md)
- 两个独立 plugin：
  - [plugins/testing/](plugins/testing/) — 测试能力 bundle（v3.0.0，5-way 路由 + 5 子 skill + 1 独立 skill + 1 可选 MCP Server）
  - [plugins/wechat-formatter/](plugins/wechat-formatter/) — 微信公众号排版（v2.0.0，6 种风格）

## Claude Code 工作约定

### Skill 加载机制

- Claude Code runtime 扫描 `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` 加载 skill
- 每个 skill 的 `SKILL.md` 是入口（含 frontmatter + 主流程），细节下沉到 `knowledge/` 子文件
- 修改 skill 时**必须**同步更新 `SKILL.md` 与对应 `README.md`，避免触发 darwin-skill dim7（整体架构）扣分

### Plugin 修改检查清单

修改 plugin 内任何文件前，确认以下同步关系：

| 修改对象 | 必须同步更新 |
|---|---|
| `SKILL.md` frontmatter version | 该 skill 的 `README.md` 版本号 + plugin 的 `.claude-plugin/plugin.json` version（如有） |
| `SKILL.md` 路由规则 / 能力清单 | `README.md` 路由表 + 根 `README.md` 对应章节 |
| `SKILL.md` 引用的 knowledge 文件路径 | knowledge 文件实际存在 |
| 新增 / 删除 skill | `.claude-plugin/marketplace.json` + `plugins/<plugin>/README.md` 能力矩阵 + 根 `README.md` |
| testing-bundle 路由扩展 | `skills/testing-bundle/CHANGELOG.md` |

### 关键相对路径引用

`bug-analyzer` 的 SKILL.md 通过 `../test-case-engineer/knowledge/bug-patterns.md` 引用缺陷模式库。**单独安装 bug-analyzer 时该路径失效**，会触发能力降级。修改 bug-patterns.md 时需同时验证：
- test-case-engineer 的引用：`knowledge/bug-patterns.md`
- bug-analyzer 的引用：`../test-case-engineer/knowledge/bug-patterns.md`

### 文档目录约定

```
docs/superpowers/
├── plans/    # 实施计划文档（命名：YYYY-MM-DD-<feature>.md）
└── specs/    # 设计规格文档（命名：YYYY-MM-DD-<feature>-design.md）
```

新增设计文档需放入对应子目录，并按日期前缀命名。

### darwin-skill 评估

修改 skill 后如需运行 darwin-skill 质量评估：
- 工作区：[.claude/skills/darwin-skill/](.claude/skills/darwin-skill/)
- 历史结果：[.darwin-results/](.darwin-results/)
- 评分波动 ±5 分属正常，需多轮评估取均值

## 强约束入口

以下硬约束**自动注入**，违反将导致提交被拒：

- [.trae/rules/git-commit-message.md](.trae/rules/git-commit-message.md) — Conventional Commits 提交信息
- [.trae/rules/git-workflow.md](.trae/rules/git-workflow.md) — 分支保护 / 命名 / PR 流程 / 版本历史保护

通用版（非自动注入，跨工具一致）：[rules/](rules/)

## 参考实现

- 多 runtime 适配模式参考 [obra/superpowers](https://github.com/obra/superpowers)
- 多 plugin 聚合结构参考 [anthropics/claude-code](https://github.com/anthropics/claude-code)
