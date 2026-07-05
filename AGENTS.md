# AGENTS.md

本文件定义本仓库的 Agent 工作规范，适用于所有 AI 编程助手（TRAE、Cursor、Codex、Cline 等）。

## Git 提交信息规范

遵循 Conventional Commits，详见 [rules/git-commit-message.md](rules/git-commit-message.md)。

要点速览：

- 结构：`<type>(<scope>): <subject>` + 可选 body + 可选 footer
- Type：`feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `chore` / `ci` / `build` / `revert`
- Subject 默认中文，祈使句，结尾不加句号，不超过 72 字符
- 每次提交保持原子性，不提交 WIP
- 提交前确保代码能正常运行并通过测试

## Git 工作流规范

### 分支策略

- **禁止**直接修改 `main` 分支
- 所有功能开发必须在 feature 分支进行
- Feature 分支命名：`feat/[skill-name]-[version 或 description]`
  - 示例：`feat/test-case-engineer-v3`、`feat/bug-analyzer-v1`
- 修复分支命名：`fix/[bug 描述]`
- 重构分支命名：`refactor/[模块 描述]`

### 备份与回滚

- 涉及大范围拆分/重构前，必须创建备份分支：`backup/[pre-xxx]`
  - 示例：`backup/pre-split-test-engineer`
- 备份分支保留完整版本历史，用于回滚兜底

### Pull Request 流程

1. Feature 分支完成后推送到远程
2. 在远程发起 PR，等待 review
3. Review 通过后方可合并到 `main`
4. 合并方式：使用 `--no-ff` 保留分支历史
   ```bash
   git merge --no-ff feat/test-case-engineer-v3
   ```

### 版本历史保护

- Skill 拆分时必须通过分支重命名保留完整版本历史
- 重要操作前确认备份分支已创建
- 不得使用 `push --force` 到 `main`/`master`

## 代码变更规范

### 格式化

**严格禁止**对原有代码进行任何格式化操作，详见 [rules/no-formatting.md](rules/no-formatting.md)。

- SearchReplace 的 `old_str` 必须**原样复制**文件中已有的内容（含所有空格、缩进、换行）
- **只修改**功能变更所需的那几行，**绝对不要碰**周围无关代码
- 新增代码应遵循已有代码的风格，不要"纠正"现有风格

### 文件编辑原则

- 优先编辑已有文件，不主动创建新文件
- 不主动创建文档（*.md / README.md），除非用户明确要求
- 只做被要求的事，不做额外的"改进"或重构

## Skill 开发约束

- Skill 拆分必须保留完整版本历史
- `Bug-patterns.md` 在 `test-case-engineer` 中保留，`bug-analyzer` 通过相对路径引用
- 每个新 Skill 须包含 8 项标准交付物：`SKILL.md`、`README.md`、4 个 knowledge 文件、`integrations/quickstart.md`、`test-prompts.json`
- `README.md` 必须与 `SKILL.md` 保持同步，避免架构信息不一致
- `performance-test-engineer` 和 `test-strategy-engineer` 不得与其他 Skill 共享 knowledge 文件，避免路由歧义
- `testing-bundle v2.0.0` 在新增 4-way 能力的同时，必须保持与已有 2-way 路由的向后兼容
