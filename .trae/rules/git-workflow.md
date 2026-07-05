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

### 分支命名

- Feature 分支：`feat/[skill-name]-[version 或 description]`
  - 示例：`feat/test-case-engineer-v3`
- 修复分支：`fix/[bug 描述]`
- 重构分支：`refactor/[模块 描述]`
- 备份分支：`backup/[pre-xxx]`（大范围拆分/重构前必须创建）
  - 示例：`backup/pre-split-test-engineer`

### Pull Request 流程

1. Feature 分支完成后**必须**推送到远程
2. **必须**在远程发起 PR，等待 review
3. Review 通过后方可合并到 `main`
4. 合并方式**必须**使用 `--no-ff` 保留分支历史：
   ```bash
   git merge --no-ff feat/test-case-engineer-v3
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
