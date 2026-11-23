# INV1 提案：输出契约闸门（未应用）

> **状态**：提案，未应用。阶段 4 模型 Probe 被阻塞（无 runner / judge / API key），不能按采纳规则验证，故不合并。
> **依据**：`docs/skill-evaluation/reports/2026-11-17-phase4-harness-round1.md` 的确定性失败聚类。
> **范围**：仅 `test-case-engineer-core.md` 的工作流/输出契约；不触碰 knowledge 领域知识、脚本、MCP 契约。

## 目标失败类

| 失败类 | 证据 | 目标 |
|---|---|---|
| `TITLE_SEPARATOR` | 13 次 / 3 文件；如 `task-1:L347`「未登录访问受保护页面跳转登录页」 | 标题统一 `对象 - 行为/条件/结果` |
| `ARRANGE_DECLARE` | 7 次 / 7 文件；如 `task-14:L1`、`task-34:L1`、`task-36:L1` | 用例集开头显式声明编排策略 |
| `NONFUNC_TAIL` | 3 次 / 3 文件；如 `task-1:L225`、`task-6:L145`、`task-39:L183` | 非功能用例统一置末尾独立成组 |

## 拟改动（pseudo-diff）

```diff
--- a/plugins/testing/skills/test-case-engineer/test-case-engineer-core.md
+++ b/plugins/testing/skills/test-case-engineer/test-case-engineer-core.md
@@ 阶段 3 输出前自检
+- 标题必须使用 `被测对象 - 行为/条件/结果`，以 ` - ` 分隔；禁止用逗号、分号或空格替代分隔符
+- 用例集开头必须声明编排策略：`用户旅程编排` 或 `模块分组 + 组内用户旅程编排`
@@ 阶段 4 机器校验
+- `validate_cases.py` 命中 TITLE_SEPARATOR 或 ARRANGE_DECLARE 时，按阻断项处理：修复后重跑，0 warning 方可交付
```

## 范围校验

- 只改 `test-case-engineer-core.md` 的阶段 3 自检与阶段 4 闸门。
- 不新增/删除知识条款，不改 `writing-rules.md` 的字段定义，不改 `validate_cases.py` 规则级别。
- 依赖现有 `validate_cases.py` 的 `TITLE_SEPARATOR` / `ARRANGE_DECLARE` 检测，不新增脚本规则。

## 未验证风险

- 把 warning 当阻断项可能增加交付摩擦，尤其在历史用例迁移场景。
- 旧产物失败不代表当前 skill 仍失败；必须用当前 base/inv1 配对 Probe 验证后才能采纳。
