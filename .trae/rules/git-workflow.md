---
alwaysApply: true
---

## Git 工作流硬约束

**这些是不可违反的硬约束，每次涉及 git 操作必须严格遵守。**

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

- Feature 分支：`feat/[skill-name]-[version 或 description]`
  - 示例：`feat/test-case-engineer-v3`
- 修复分支：`fix/[bug 描述]`
- 紧急修复分支：`hotfix/[紧急问题描述]`（生产环境紧急修复专用）
  - 示例：`hotfix/skill-loading-crash`
- 重构分支：`refactor/[模块 描述]`
- 发布分支：`release/v[版本号]`（需要预发布测试时使用）
  - 示例：`release/v1.2.0`
- 备份分支：`backup/[pre-xxx]`（大范围拆分/重构前必须创建）
  - 示例：`backup/pre-split-test-engineer`

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
   - **默认使用 squash merge**，保持 main 线性历史（对齐 TBD/GitHub Flow）：
     ```bash
     git merge --squash feat/xxx
     git commit -m "feat(xxx): 完整功能描述"
     ```
   - 历史性功能（如 skill 大版本拆分）**允许**使用 `--no-ff` 保留分支历史：
     ```bash
     git merge --no-ff feat/xxx
     ```
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
- 打 tag 方式：
  ```bash
  git tag -a v1.2.0 -m "feat: 新增用例拆分与合并策略"
  git push origin v1.2.0
  ```

### 版本历史保护

- Skill 拆分时**必须**通过分支重命名保留完整版本历史
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
