# 贡献指南

感谢你对 my-skill 项目的关注！本文档说明如何参与本项目贡献。

## 开发环境

### 必备工具

- Git（2.30+）
- Python（3.10+，用于运行 MCP Server 与脚本）
- Node.js（18+，用于 markdown lint 等工具）
- pre-commit（用于本地提交前检查）

### 初始化

```bash
git clone https://github.com/liu-YLY/my-skills.git
cd my-skills

# 安装 pre-commit hooks
pip install pre-commit
pre-commit install
```

## Git 工作流

本项目遵循 TBD/GitHub Flow，详细规范见：

- [.trae/rules/git-commit-message.md](.trae/rules/git-commit-message.md) — Conventional Commits 提交信息规范
- [.trae/rules/git-workflow.md](.trae/rules/git-workflow.md) — 分支保护 / 命名 / PR 流程 / 版本历史保护

### 核心约束

- **禁止**直接修改 `main` 分支
- 所有功能开发必须在 feature 分支进行
- 分支命名：`feat/<skill-name>-<version>` / `fix/<bug>` / `refactor/<module>` / `chore/<infra>`
- Feature 分支存活时间**不得超过 2 天**
- 单个 PR 变更**不得超过 400 行**；超过必须拆分

### 开发流程

```bash
# 1. 拉取远程最新
git fetch origin
git checkout main
git pull origin main

# 2. 创建 feature 分支
git checkout -b feat/<skill-name>-<version>

# 3. 开发并提交（保持原子性）
git add <specific-files>
git commit -m "feat(<scope>): <subject>"

# 4. 定期与 main 同步
git fetch origin
git rebase origin/main

# 5. 推送并发起 PR
git push -u origin feat/<skill-name>-<version>
```

### 提交信息规范

采用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type**：feat / fix / docs / style / refactor / perf / test / chore / ci / build / revert
- **scope**：影响的 skill 或模块（如 `bug-analyzer` / `testing-bundle` / `project-infra`）
- **subject**：中文祈使句，不超过 72 字符，结尾不加句号
- **body**：中文详细描述动机与对比，每行不超过 72 字符
- **footer**：`BREAKING CHANGE:` 或 `Closes #<issue>`

## Skill 交付物标准

每个 skill 必须包含以下 8 项标准交付物：

| # | 文件 | 说明 |
|---|---|---|
| 1 | `SKILL.md` | 入口文件，含 frontmatter（name / version / description / keywords） |
| 2 | `README.md` | 说明文档，版本号需与 SKILL.md frontmatter 一致 |
| 3 | `knowledge/` (4 个) | 4 个 knowledge 子文件，按职责拆分 |
| 4 | `integrations/quickstart.md` | 集成快速开始 |
| 5 | `test-prompts.json` | 测试用 prompts |

### 例外

- **元 skill**（如 testing-bundle）：不需要 knowledge/ 与 quickstart.md，但需要 CHANGELOG.md 记录路由演进
- **独立 skill**（如 change-impact-analyzer）：可豁免 quickstart.md，但需在 README 中说明

### Skill 文件结构

```
skills/<skill-name>/
├── SKILL.md                          # 入口
├── README.md                         # 说明
├── test-prompts.json                 # 测试 prompts
├── knowledge/                        # 知识库（4 个文件）
│   ├── <knowledge-1>.md
│   ├── <knowledge-2>.md
│   ├── <knowledge-3>.md
│   └── <knowledge-4>.md
└── integrations/
    └── quickstart.md                 # 快速开始
```

## 代码变更规范

### 格式化

**严格禁止**对原有代码进行任何格式化操作。

- `old_str` 必须**原样复制**文件中已有的内容（含所有空格、缩进、换行）
- **只修改**功能变更所需的那几行，**绝对不要碰**周围无关代码
- 新增代码应遵循已有代码的风格，不要"纠正"现有风格

### 文件编辑原则

- 优先编辑已有文件，不主动创建新文件
- 不主动创建文档（*.md / README.md），除非用户明确要求
- 只做被要求的事，不做额外的"改进"或重构
- 不添加不必要的注释、文档字符串或类型注解

## pre-commit 检查

本项目配置了 pre-commit hooks，提交前自动检查：

- `check-merge-conflict`：合并冲突标记
- `check-added-large-files`：大文件（>500KB）
- `detect-private-key`：私钥泄漏
- `check-json` / `check-yaml`：JSON / YAML 语法
- `conventional-commits`：提交信息规范

**注意**：pre-commit 不启用 auto-fix，符合「禁止对原有代码格式化」硬约束。

## PR 流程

1. Feature 分支完成后推送到远程
2. 在 GitHub 发起 PR，base 为 `main`
3. PR 描述需包含：
   - 背景：为什么做这个变更
   - 变更内容：具体改了什么
   - 自检清单：参考 `.trae/rules/git-workflow.md` 提交前检查清单
4. Review 通过后方可合并
5. 合并策略：默认 squash merge，历史性功能允许 --no-ff

## 版本标记

每次合并到 main 后，根据变更类型决定是否打 tag：

- **major**：不兼容的 API 变更（v2.0.0 → v3.0.0）
- **minor**：向后兼容的新功能（v1.0.0 → v1.1.0）
- **patch**：向后兼容的 bug 修复（v1.0.0 → v1.0.1）

```bash
git tag -a v1.2.0 -m "feat: 新增用例拆分与合并策略"
git push origin v1.2.0
```

## 反馈渠道

- Bug 报告：[GitHub Issues](https://github.com/liu-YLY/my-skills/issues/new?template=bug-report.md)
- 功能建议：[GitHub Issues](https://github.com/liu-YLY/my-skills/issues/new?template=feature-request.md)
- Skill 提案：[GitHub Issues](https://github.com/liu-YLY/my-skills/issues/new?template=skill-proposal.md)
