# 阶段 4 报告：harness² 第一轮（blocked）

> **日期**：2026-11-17
> **套件**：`2026-11-17-quality-suite-v7.2.json`（70 task / 16 trigger / 354 checks，SHA `5c6bd2ef`）
> **状态**：`blocked` —— 模型 Probe 无法执行；本报告只包含确定性代理基线与未应用的 INV/DOM 提案。
> **不得**把本报告当作 base/inv1/dom1/agg1 的质量对比，也不得据此宣称任何改动有效。

## 1. 阻塞原因

| 依赖 | 检查结果 |
|---|---|
| runner（opencode / zcode / codebuddy / claude / codex / ollama） | 均未安装 |
| 模型 API key | 未配置 |
| 不同厂商独立 judge | 不可用 |
| A/A 一致率 | 无法计算 |

因此 4-4「两路分别全量 Probe」、4-5「Compose」、4-6「采纳决策」不能执行。

## 2. 4-1 确定性代理基线

对象：`docs/skill-evaluation/tier23/full/outputs/task-*-with_skill.txt`（42 份，旧版本 skill 产物）。
方法：`validate_cases.py --json` 逐份校验；只作为失败聚类与回归集，不代表当前 base。

| 指标 | 数值 |
|---|---:|
| 产物 | 42 |
| 可解析为用例 | 20 |
| 不可解析（评审/分析等） | 22 |
| 用例 | 153 |
| ERROR | 10 |
| WARN | 26 |

### 失败聚类

| 类别 | 规则 | 次数 | 文件数 | 证据（≥3） |
|---|---|---:|---:|---|
| 格式/结构 | `TITLE_SEPARATOR` | 13 | 3 | `task-1:L347`「未登录访问受保护页面跳转登录页」；`task-1:L369`「退出登录后清除会话」；`task-2:L279`「领取券后状态变为已领取未使用」 |
| 格式/结构 | `ARRANGE_DECLARE` | 7 | 7 | `task-14:L1`；`task-34:L1`；`task-36:L1`（均未声明编排策略） |
| 格式/结构 | `NONFUNC_TAIL` | 3 | 3 | `task-1:L225`；`task-6:L145`；`task-39:L183`（非功能用例未置末尾） |
| 可读性/模糊 | `VAGUE_WORD` | 7 | 4 | `task-26:L276`「输入任意值 `xxx`」；`task-32:L242`「输入任意值」；`task-38:L76`「报表页面正常展示报表数据」 |
| 格式/结构 | `FIELD_REQUIRED` | 1 | 1 | `task-2:L228` 缺少「业务结果」 |
| 格式/结构 | `TITLE_PREFIX` | 1 | 1 | `task-40:L48`「验证昵称修改功能」 |
| 格式/结构 | `BIZ_CONTEXT_PREFIX` | 1 | 1 | `task-40:L52`「测试修改昵称的功能」 |
| 格式/结构 | `ID_UNIQUE` | 1 | 1 | `task-40` ID 重复 |
| 格式/结构 | `ID_SEQ` | 1 | 1 | `task-40` 序号不连续 |
| 可读性/结构 | `STEP_GROUP` | 1 | 1 | `task-business-order:L67` 步骤分块不足 |
| 覆盖 | J 类 | — | — | 未评估：历史产物无需求基线，不能计算覆盖 |

**聚类结论**：

- 格式/结构类占绝对多数，集中在标题分隔符、编排声明、非功能置末尾。
- 可读性类集中在「任意」「正常」等模糊表达。
- 没有足够证据支持「规则冲突」类；现有冲突候选仍只有阶段 1 的 3 条 check 口径问题（已在 v7.1 修复）。
- 覆盖类不可用历史产物评估。

## 3. 4-2 / 4-3 提案（未应用）

| 提案 | 文件 | 目标失败类 | 范围校验 |
|---|---|---|---|
| [INV1](../phase4/inv1-proposal.md) | `test-case-engineer-core.md` 阶段 3/4 | `TITLE_SEPARATOR`、`ARRANGE_DECLARE`、`NONFUNC_TAIL` | 只改工作流/输出契约；不触碰 knowledge、脚本、MCP |
| [DOM1](../phase4/dom1-proposal.md) | `knowledge/requirement-review.md` | 需求评审召回与级别判例 | 只改领域知识与判例；不触碰工作流、脚本 |

> 两个提案都**没有应用**到 skill。阶段 4 的采纳规则要求 Probe 证据；无 Probe 即合并属于无证据改动。

## 4. 4-4 / 4-5 / 4-6 指标表

| 列 | base | inv1 | dom1 | agg1 |
|---|---|---|---|---|
| 主指标（v7.2 结果型 check 通过率） | 未执行 | 未执行 | 未执行 | 未执行 |
| 护栏（格式 error / 追溯 / 误报） | 仅确定性代理：10 error / 26 WARN | 未执行 | 未执行 | 未执行 |
| 有效样本数 | 0（模型） | 0 | 0 | 0 |
| A/A 一致率 | 不可计算 | 不可计算 | 不可计算 | 不可计算 |
| 结论 | 保留 base | 不采纳 | 不采纳 | 不采纳 |

## 5. 采纳决策

- **不采纳 INV1、DOM1、agg1**：没有模型 Probe，无法证明主指标 +≥5pp 或护栏不退化。
- **保留 base（当前已提交的 skill 状态）**：阶段 2/3 的瘦身与校验器改动已通过确定性门禁，不属于本轮 harness² 采纳。
- 经验沉淀见 [experience-library.md](../experience-library.md)：E-001～E-005，均为确定性或环境事实证据，不宣称模型质量提升。

## 6. 阶段 4 验收对照

| 验收项 | 结果 |
|---|---|
| base/inv1/dom1/agg1 四列指标 | 未达成：四列均无模型指标 |
| 护栏、有效样本数 | 未达成：有效样本 0 |
| 采纳结论 | 达成：保留 base，不采纳未 Probe 改动 |
| 经验库 ≥3 条有证据、可迁移 | 达成：5 条（确定性/代理/环境事实） |
| 未达门槛的改动已回退 | 达成：INV1/DOM1 未应用 |

**结论**：阶段 4 在 4-4 阻塞，未通过验收。下一步必须先补齐 runner + 独立 judge + API key，或由用户决定是否以「静态提案 + 确定性门禁」继续。

## 7. 复跑入口

```bash
# 输入校验（不需要模型）
python3 scripts/skill-evals.py --cases-file docs/skill-evaluation/2026-11-17-quality-suite-v7.2.json

# 确定性代理聚类
python3 plugins/testing/skills/test-case-engineer/scripts/validate_cases.py \
  docs/skill-evaluation/tier23/full/outputs/task-1-with_skill.txt --json

# 需要 runner/judge 后才能执行
python3 scripts/skill-evals.py --cases-file docs/skill-evaluation/2026-11-17-quality-suite-v7.2.json \
  --results <runs.jsonl>
```
