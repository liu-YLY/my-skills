---
alwaysApply: true
scene: git_message
---

## Git 提交信息硬约束（Conventional Commits）

**这是不可违反的硬约束，每次 git commit 必须严格遵守。**

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
- 结尾不加句号
- 不超过 72 个字符

### Body（正文，可选）

- **默认使用中文**详细描述变更的动机、与之前行为的对比等
- 使用祈使句，现在时态
- 每行不超过 72 个字符

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

### 不可违反的规则

- 每次提交必须只做一件事，保持原子性
- **禁止**提交未完成的功能（WIP）
- 提交前必须确保代码能正常运行并通过测试
- **禁止**在一次提交中混合多个不相关的变更
