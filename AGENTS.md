# AGENTS.md

> 通用 AI 编程助手配置模板，适用于 TRAE、Cursor、Codex、Claude 等工具。
> 使用时直接复制到项目根目录，按需调整。

## Git 提交信息规范（Conventional Commits）

### 提交信息结构

```
<type>(<scope>): <subject>
// 空一行
<body>
// 空一行
<footer>
```

### Type（类型，必填）

- **feat**: 新功能
- **fix**: 修复 bug
- **docs**: 仅文档变更
- **style**: 代码格式调整（不影响代码逻辑）
- **refactor**: 重构（既不是新功能也不是修复 bug）
- **perf**: 性能优化
- **test**: 添加或修改测试
- **chore**: 构建过程或辅助工具的变动
- **ci**: CI/CD 配置变更
- **build**: 影响构建系统或外部依赖的变更
- **revert**: 回滚之前的提交

### Scope（范围，可选）

用括号包裹，表示本次提交影响的范围/模块，如：`feat(auth): add login api`

### Subject（主题，必填）

- **默认使用中文**描述本次变更内容
- 使用祈使句，现在时态（如 "新增" 而非 "新增了"）
- 结尾不加句号，不超过 72 个字符

### Body（正文，可选）

- **默认使用中文**详细描述变更的动机、与之前行为的对比等
- 使用祈使句，现在时态，每行不超过 72 个字符

### Footer（页脚，可选）

- **BREAKING CHANGE**: 不兼容的 API 变更，必须以 `BREAKING CHANGE:` 开头
- **关闭 Issue**: 如 `Closes #123`、`Refs #456`

### 示例

```
feat: 新增用户登录 API

基于 JWT 的用户认证接口，登录成功返回 access token 和 refresh token。

Closes #42
```

```
fix(auth): 修复 token 过期时间计算错误

之前 token 过期时间使用了秒而非毫秒计算，导致 token 提前过期。

BREAKING CHANGE: token 过期时间戳从秒改为毫秒
```

### 硬约束

- 每次提交必须只做一件事，保持原子性
- **禁止**提交未完成的功能（WIP）
- 提交前必须确保代码能正常运行并通过测试
- **禁止**在一次提交中混合多个不相关的变更

## Git 工作流规范

### 分支保护

- **禁止**直接修改 `main` / `master` 分支
- 所有功能开发必须在 feature 分支进行
- **禁止**使用 `git push --force` 到 `main` / `master`
- **禁止**使用 `git push --force-with-lease` 到 `main` / `master`

### 分支命名

- Feature 分支：`feat/[模块或功能描述]`
  - 示例：`feat/user-login`、`feat/payment-v2`
- 修复分支：`fix/[bug 描述]`
  - 示例：`fix/token-expiry`
- 重构分支：`refactor/[模块 描述]`
  - 示例：`refactor/auth-module`
- 备份分支：`backup/[pre-xxx]`（大范围重构前必须创建）
  - 示例：`backup/pre-refactor-auth`

### Pull Request 流程

1. Feature 分支完成后**必须**推送到远程
2. **必须**在远程发起 PR，等待 review
3. Review 通过后方可合并到 `main`
4. 合并方式**必须**使用 `--no-ff` 保留分支历史

### 版本历史保护

- 重要操作前**必须**确认备份分支已创建
- 不得使用破坏性命令（`reset --hard`、`clean -f`、`branch -D`）除非用户明确要求

### 提交前检查清单

- [ ] 当前不在 `main` / `master` 分支
- [ ] 提交信息符合 Conventional Commits 规范
- [ ] 提交保持原子性，只做一件事
- [ ] 代码能正常运行并通过测试
- [ ] 不包含未完成的功能（WIP）
- [ ] 不包含敏感文件（.env、credentials 等）

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
