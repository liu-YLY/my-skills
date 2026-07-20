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

### 开发前准备（每次开始新功能前必须执行）

```bash
# 1. 拉取远程最新内容（不自动合并，仅更新远程跟踪分支）
git fetch origin

# 2. 切换到 main 并同步到远程最新
git checkout main
git pull origin main

# 3. 基于最新 main 创建 feature 分支
git checkout -b feat/xxx
```

- **禁止**在本地 main 落后于远程的情况下创建 feature 分支
- 如果当前在旧的 feature 分支上，**必须**先切回 main 并 pull 最新再创建新分支
- `git fetch` 必须在每次开发会话开始时执行，确保本地感知远程最新状态

### 分支命名

- Feature 分支：`feat/[模块或功能描述]`
  - 示例：`feat/user-login`、`feat/payment-v2`
- 修复分支：`fix/[bug 描述]`
  - 示例：`fix/token-expiry`
- 紧急修复分支：`hotfix/[紧急问题描述]`（生产环境紧急修复专用）
  - 示例：`hotfix/skill-loading-crash`
- 重构分支：`refactor/[模块 描述]`
  - 示例：`refactor/auth-module`
- 发布分支：`release/v[版本号]`（需要预发布测试时使用）
  - 示例：`release/v1.2.0`
- 备份分支：`backup/[pre-xxx]`（大范围重构前必须创建）
  - 示例：`backup/pre-refactor-auth`

### 分支生命周期

- Feature 分支存活时间**不得超过 2 天**；超过则必须拆分为更小的增量
- 分支存活期间**必须**定期与 main 同步，避免合并冲突：
  ```bash
  git fetch origin
  git rebase origin/main
  ```
- PR 合并后**必须立即删除**远程分支：
  ```bash
  git push origin --delete feat/xxx
  git branch -d feat/xxx
  ```
- **禁止**长期保留已合并的 feature 分支

### Pull Request 流程

1. Feature 分支完成后**必须**推送到远程
2. **必须**在远程发起 PR，等待 review
3. Review 通过后方可合并到 `main`
4. 合并策略：
   - **默认使用 squash merge**，保持 main 线性历史
   - 历史性功能（如 skill 大版本拆分）**允许**使用 `--no-ff` 保留分支历史
5. PR 规模约束：单个 PR 变更**不得超过 400 行**；超过必须拆分为多个小 PR

### 紧急修复流程（Hotfix）

当生产环境出现紧急问题时，走快速通道：

```bash
# 1. 从 main 创建 hotfix 分支
git checkout main
git pull origin main
git checkout -b hotfix/xxx

# 2. 修复并提交
git add .
git commit -m "fix: 紧急修复描述"

# 3. 推送并发起 PR（标记为紧急）
git push -u origin hotfix/xxx

# 4. 合并后删除分支
git checkout main
git merge --squash hotfix/xxx
git push origin main
git push origin --delete hotfix/xxx
```

- Hotfix 分支**必须**直接从 main 创建，不从 feature 分支创建
- Hotfix PR 可以跳过常规 review 排队，但**至少需要 1 人 review**
- 修复完成后**必须**同步到当前进行中的 feature 分支（rebase）

### 版本标记

- 每次合并到 main 后，根据变更类型决定是否打 tag
- 使用语义化版本（SemVer）：`v[major].[minor].[patch]`
  - **major**: 不兼容的 API 变更
  - **minor**: 向后兼容的新功能
  - **patch**: 向后兼容的 bug 修复

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
- [ ] 分支存活时间未超过 2 天
- [ ] 分支已与 main 同步（rebase 过）
- [ ] PR 变更行数未超过 400 行

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
