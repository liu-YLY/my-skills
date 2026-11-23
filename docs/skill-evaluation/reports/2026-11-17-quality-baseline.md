# 2026-11-17 质量基线报告（阶段 1-7）

> 日期：2026-11-17
> 套件：[2026-11-17-quality-suite-v7.1.json](../2026-11-17-quality-suite-v7.1.json)，SHA `dd2f1b49`，70 task / 12 trigger / 354 checks
> 历史版本：[v7](../2026-11-17-quality-suite-v7.json)（SHA `ae880180`，保留用于复现）
> 种子集：[测试点 10 cases](../2026-11-17-test-point-cases.json)（SHA `dc900b79`）、[需求评审 12 cases / 61 defects](../2026-11-17-requirement-review-cases.json)（SHA `aee2ed36`）
> **状态：`blocked`（模型行为基线未执行）；确定性基线已完成**
> 边界：本报告不提供质量分数，不构成「有 skill 是否更好」的结论

---

## 1. 为什么是 blocked

| 前置条件 | 现状 | 影响 |
|---|---|---|
| 模型 runner | 当前沙箱没有 `opencode` / `zcode` / `codebuddy` / `claude` / `codex` 等 runner，也没有模型 API key | 无法生成 with_skill / no_skill 产物 |
| 独立 judge | 无不同厂商模型；子代理与主代理同源 | 不满足 methodology v1.5 §1 的 judge 独立性 |
| 3 次重复 | 无 runner，无法执行 | 不满足 `--expected-runs 3` |
| A/A 噪声基线 | 未执行 | 一致率未知，不能判定口径稳定性 |

按 [methodology.md](../methodology.md) v1.5 与计划 §6.3：无独立 judge / 单次重复 / `status=partial` 时，只能记录方向性观察，不得用于采纳决策。因此本阶段**不伪造基线分数**。

---

## 2. 确定性基线（已完成）

### 2.1 仓库校验

```bash
python3 scripts/check-skill-consistency.py     # 通过
python3 scripts/check-knowledge-count.py       # 通过
python3 scripts/check-md-links.py              # 通过
python3 scripts/check-project-inventory.py     # 通过
python3 scripts/check-version-sync.py          # 通过
python3 scripts/skill-evals.py                 # 输入校验通过
python3 -m pytest scripts/tests/test_repository_tools.py -q  # 36 passed
python3 scripts/check-context-budget.py        # 全部 ok，exit 0
```

### 2.2 上下文预算

当前默认路径（字符）：

| Skill / 模式 | 字符 | 当前门槛 | 阶段 2 目标 |
|---|---:|---:|---:|
| test-case-engineer / default | 64,028 | 65,300 | 44,800 |
| test-case-engineer / review | 33,545 | 34,200 | 25,200 |
| state-machine-test-engineer / default | 44,340 | 45,200 | 33,300 |
| change-impact-analyzer / default | 38,829 | 39,600 | 31,000 |
| testing-bundle / route | 17,190 | 17,500 | 13,750 |
| test-strategy-engineer / default | 17,765 | 18,100 | 15,000 |
| bug-analyzer / default | 21,053 | 21,500 | 16,000 |
| performance-test-engineer / default | 18,726 | 19,100 | 15,500 |
| frontend-test-preparation / default | 6,378 | 6,500 | 6,000 |
| test-data-generator / default | 10,029 | 10,200 | 9,000 |

- 默认路径合计：271,883 字符
- 目录内全部 Markdown：401,209 字符
- Token 口径：tiktoken 未安装，当前为 `characters / 1.55` 回退估算

### 2.3 确定性用例校验（历史产物，仅作校验器基线）

对象：`docs/skill-evaluation/tier23/full/outputs/task-*-with_skill.txt`（42 份，生成时为旧版本 skill）。

| 指标 | 数值 |
|---|---:|
| 可解析为用例文件的产物 | 20 / 42 |
| 不可解析（评审报告/其他格式） | 22 / 42 |
| 用例总数 | 153 |
| ERROR | 10 |
| WARN | 26 |
| 有 ERROR 的文件 | `task-2`、`task-26`、`task-32`、`task-38`、`task-40` |

说明：

- 这不是当前 v9.14.0 的质量分数；产物来自旧版本，且无需求基线。
- 22 份不可解析产物是评审/分析类输出，不适用 `validate_cases.py` 的生成格式校验。
- 10 个 ERROR 需要逐个确认是产物问题还是校验器边界；不在本阶段修改 skill。

### 2.4 规则清单

```bash
python3 scripts/extract-rule-inventory.py
```

| Skill | 条数 | D1 重复 | D2 按需化 | D3 冲突 | D4 参考/按需 | D5 行为 |
|---|---:|---:|---:|---:|---:|---:|
| test-case-engineer | 223 | 0 | 17 | 0 | 39 | 167 |
| state-machine-test-engineer | 155 | 52 | 0 | 0 | 25 | 78 |
| change-impact-analyzer | 58 | 0 | 7 | 0 | 2 | 49 |
| testing-bundle | 16 | 0 | 0 | 0 | 1 | 15 |

### 2.5 断言-规则一致性

见 [2026-11-17-eval-rule-consistency.md](2026-11-17-eval-rule-consistency.md)：

- 流程术语型断言：37 → 1
- 冲突候选：3 条（#13 评级、#7/#19 抽样）
- 其余重点规则抽检一致

---

## 3. 恢复模型行为基线的步骤

### 3.1 角色

| 角色 | 要求 |
|---|---|
| runner | 能批量调用模型；with_skill 读 skill 指令，no_skill 只读需求原文；同模型、同参数、同套件 |
| judge | 与 runner 不同厂商/不同模型家族；盲评；只读产物 + checks + 判定口径，不读 skill |
| 汇总 | `scripts/skill-evals.py --results` |

### 3.2 规模

| 组合 | 次数 |
|---|---:|
| 70 task × 2 variant × 3 次 | 420 |
| 12 trigger × 2 variant × 3 次 | 72 |
| A/A（同 variant 重复 2 次） | 建议至少 20 份 |

### 3.3 执行

1. 冻结套件：记录 v7.1 SHA `dd2f1b49`；若再改断言，必须生成 v7.x 并重新冻结。
2. 跑 A/A：同 variant 两次，一致率 <70% 时停止，先修口径。
3. 跑 with_skill / no_skill：每条 3 次；产物落盘，记录 `output_characters` 与 `output_sha256`。
4. judge 逐条判定：每条 check 给 `true/false` + 证据位置；复合条件全满足才 true。
5. 汇总：

```bash
python3 scripts/skill-evals.py \
  --cases-file docs/skill-evaluation/2026-11-17-quality-suite-v7.json \
  --results runs.jsonl \
  --expected-runs 3 \
  --expected-trigger-runs 3 \
  --variants with_skill no_skill
```

6. 只有 `status=evaluated`、无 `invalid_runs` / `unpaired_runs` 时，才写质量结论。

### 3.4 需求评审与测试点

- 需求评审：用 `2026-11-17-requirement-review-cases.json` 的 61 个种子缺陷计算召回/误报；每个缺陷需有原文位置与引用。
- 测试点：用 `2026-11-17-test-point-cases.json` 的 `requirement_items` / `expected_points` / `out_of_scope` 计算覆盖召回、原子性与范围裁剪。
- 两个种子集都需要 runner + judge；没有独立 judge 时只做作者自评，标 `dry_run`，不作为质量结论。

---

## 4. 本阶段结论

1. **确定性基础设施已就绪**：预算门禁、规则清单、v7 套件、种子集、一致性报告。
2. **模型行为基线被外部依赖阻塞**：无 runner / 无独立 judge / 无 API key；不伪造分数。
3. **可以进入阶段 2 的前提**：用户确认「先做结构性瘦身，用确定性门禁 + 预算 + 历史产物回归保护；质量结论等独立评测补齐」。
4. **不能做**：在没有独立评测的情况下宣称瘦身「提升质量」；只能宣称「体积下降 + 确定性检查通过 + 未发现规则冲突」。
