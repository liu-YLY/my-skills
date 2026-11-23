# 阶段 5 其余 skill 质量评测报告

> **日期**：2026-11-20
> **范围**：change-impact-analyzer、test-strategy-engineer、bug-analyzer、performance-test-engineer、frontend-test-preparation、test-data-generator（state-machine 的瘦身在 5-1，另见交接文档）
> **方法**：确定性校验（预算/结构/链接/清单/版本/pytest）+ 规则保留抽检 + test-prompts 触发覆盖；无可用模型 runner，未做模型行为评测。
> **结论**：预算全部达成；未发现硬规则丢失证据；模型行为维度保持 `partial`。

## 1. 确定性校验

### 1.1 上下文预算（`check-context-budget.py --target`）

| Skill / Mode | 字符 | 目标 | 结果 |
|---|---:|---:|---|
| state-machine / default | 33,143 | 33,300 | ok |
| state-machine / entry | 5,498 | 5,500 | ok |
| change-impact / default | 26,984 | 31,000 | ok |
| change-impact / entry | 4,920 | 5,500 | ok |
| test-strategy / default | 14,979 | 15,000 | ok |
| test-strategy / entry | 4,613 | 5,500 | ok |
| bug-analyzer / default | 12,390 | 16,000 | ok |
| bug-analyzer / entry | 5,487 | 5,500 | ok |
| performance / default | 15,491 | 15,500 | ok |
| performance / entry | 3,724 | 5,500 | ok |
| frontend / default | 5,994 | 6,000 | ok |
| frontend / entry | 4,489 | 5,500 | ok |
| test-data / default | 8,992 | 9,000 | ok |
| test-data / entry | 2,559 | 5,500 | ok |
| test-case / default | 36,990 | 44,800 | ok |
| test-case / review | 20,063 | 25,200 | ok |
| test-case / requirement-review | 9,560 | 9,600 | ok |
| testing-bundle / route | 11,119 | 13,750 | ok |

### 1.2 仓库脚本

| 检查 | 结果 |
|---|---|
| `check-skill-consistency.py` | 通过 |
| `check-knowledge-count.py` | 通过（无死链、无孤立知识文件） |
| `check-md-links.py` | 通过 |
| `check-project-inventory.py` | 通过（已 `--write` 刷新） |
| `check-version-sync.py` | 通过 |
| `check-context-budget.py --target` | 全部 ok |

### 1.3 pytest、MCP 与触发覆盖

- `scripts/tests`：46 passed，10 failed。
- 10 个失败均为环境缺失，与本次改动无关：要求 PowerShell（CI installer smoke test）；本沙箱无 PowerShell。
- review-checker MCP：110 passed。
- state-machine MCP：114 passed；其中场景示例校验已改为读取按需文件 `knowledge/scenario-examples.md`，与瘦身后的知识结构一致。
- `test_every_skill_has_complete_trigger_coverage` 通过：10 个 skill 的 trigger case 齐全，每个 ≥4 条。
- `scripts/tests/test_installation_docs.py` 9 passed：diff-modes 的 6 条只读命令与 `git show --root` 契约未被破坏。

## 2. 规则保留抽检

### 2.1 变更规模（行数，含重排）

| Skill | 新增行 | 删除行 | 删除行中含硬规则词（禁止/不得/必须/只能/不允许） |
|---|---:|---:|---:|
| state-machine | 123 | 471 | 24 |
| change-impact | 294 | 809 | 31 |
| test-strategy | 88 | 166 | 23 |
| bug-analyzer | 138 | 495 | 12 |
| performance | 117 | 219 | 9 |
| frontend | 21 | 26 | 0 |
| test-data | 4 | 10 | 1 |

删除行数高主要来自：表格改条目、重复解释合并、示例移到按需文件；不是整条规则删除。

### 2.2 关键不变量复核

对每个 skill 检索其核心硬约束，当前文本均存在：

| Skill | 抽检规则 | 结果 |
|---|---|---|
| change-impact | 不得误报无变更；不得忽略 feature 分支已提交改动；`<default>...HEAD`；Excel 需转换；降低风险需证据；只读命令注入防护；不能用部分基线断言全库未覆盖 | 全部保留 |
| test-strategy | 缺失维度标「待补」且不计算正式总分；不得为固定比例下调风险等级；±5% 档位约束；高风险必测异常/探索；微服务契约测试 | 全部保留；`P0 占比 ≤ 30%`、`前 30% → P0` 等反比例措辞保持不存在 |
| bug-analyzer | 无法稳定复现的处理；5 Whys 证据中断即停；未验证假设只能标候选；防御性测试点五列；因果验证不充分；生产无法撤销修复的替代验证 | 全部保留 |
| performance | 缺 TPS 不得推断吞吐拐点/资源饱和；不得输出已确认瓶颈；USE 三维；Little's Law；瓶颈传导链；P99/冷启动/多机/NTP | 全部保留 |
| frontend | 代码推断/运行已验证/待确认三态；运行未验证；索引路径；授权边界 | 全部保留 |
| test-data | generation complete / validation passed / incomplete / failed / not_run；negative_scenarios；profile Schema | 全部保留 |

唯一措辞变化：change-impact 的「禁止拼接」改为「不得将用户输入直接拼入 `git diff` 命令」，语义未变。

## 3. 种子回归

- **已有种子集**：test-case-engineer 的需求评审与测试点种子集在阶段 3 已完成 gold 干跑（评审 5/5、测试点 5/5、25/25 种子缺陷、0 误报），阶段 5 未修改其内容，故未重跑。
- **state-machine / change-impact / test-strategy / bug-analyzer / performance / frontend / test-data**：无对应种子集，按计划采用确定性校验 + 规则保留抽检，不做模型召回/误报声明。

## 4. 小规模方向性对照

- 计划中的方向性对照需要可用的模型 runner 与盲评 judge；当前沙箱无可靠 runner，阶段 4 的免费模型也多次超时，故本轮未生成模型输出。
- 替代证据：test-prompts 触发覆盖通过；各 skill 的 test-prompts 期望行为仍能在保留规则中找到依据；安装文档测试验证了 diff 模式命令契约。
- 这些证据只能排除「规则被删导致行为依据消失」，不能证明模型输出质量未下降。

## 5. 结论与限制

| 项 | 结论 |
|---|---|
| 预算 | 全部达成，无超限 |
| 结构/链接/版本/清单 | 全部通过 |
| 硬规则保留 | 抽检未发现丢失；删除行均为重排或合并 |
| 种子回归 | seed 覆盖的 test-case-engineer 沿用阶段 3 结果；其余无种子集 |
| 模型行为 | 未执行，状态 `partial` |
| 只删不测 | 未发现：每个 skill 均有预算、结构与关键规则证据 |

限制：没有 3 次重复、A/A 对照和独立 judge；不能据此宣布生成质量提升或未退化。若发布前需要模型侧证据，建议在阶段 6 用付费 runner 对 change-impact、bug-analyzer、performance 各跑 3 个代表 case 的小规模对照。
