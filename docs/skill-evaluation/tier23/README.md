# 小规模真实对照（Tier 2/3）执行手册

> 目的：用 **独立 runner + 独立 judge** 做一次「有 skill vs 无 skill」的小规模配对对照，验证方向性结论。这是完整 Tier 2/3 的前置试点，不是完整评测本身。

## 0. 分工（独立性是硬前提）

| 角色 | 谁 | 用什么模型 | 读什么 |
|---|---|---|---|
| **runner** | WorkBuddy（本工具） | 当前模型 | `with_skill` 组读 skill 指令 + 需求原文；`no_skill` 组**只读需求原文** |
| **judge** | 你（opencode 客户端） | **切成与 WorkBuddy 当前模型不同的另一个模型** | 只读 rubric + 产物 + checks，**不读任何 skill 指令文件** |

> ⚠️ 若 judge 用的模型与 runner 相同或同家族，结果只能标「未满足严格独立性」，不能作「有 skill 是否更好」的结论。你已确认能在 opencode 切不同模型，请务必在判定前切好。

## 1. 本轮范围（小规模，3 条 case）

| 项 | 值 |
|---|---|
| case | #35（精简）、#37（覆盖全）、#39（可读性） |
| variant | `with_skill`（加载 skill）、`no_skill`（裸模型） |
| 重复 | 每条 × 1 次（小规模试点；完整评测才做 3 次） |
| 判定项 | #35 4 + #37 4 + #39 5 = 13 条/份产物 |
| 总判定量 | 3 case × 2 variant × 13 checks = **78 条判定** |

## 2. 目录结构

```
docs/skill-evaluation/tier23/
├── README.md              本手册
├── runner-prompt.md       runner 指令（两 variant 各一份模板）
├── judge-prompt.md        judge 指令 + 盲评说明
├── blind-map.json         盲评映射（case_id → 打乱后的 A/B 编号，判定后才揭开）
├── outputs/
│   ├── case-35-with_skill.txt
│   ├── case-35-no_skill.txt
│   ├── case-37-with_skill.txt
│   ├── case-37-no_skill.txt
│   ├── case-39-with_skill.txt
│   └── case-39-no_skill.txt
├── judge-results.jsonl    judge 判定结果（盲评后回填）
└── runs.jsonl             汇总用 JSONL（--results 契约）
```

## 3. 执行步骤

### 步骤 1：runner 生成产物（在 WorkBuddy 完成）

1. `with_skill`：按 `runner-prompt.md` 的「with_skill 模板」生成 #35/#37/#39 三份产物，落盘到 `outputs/case-{id}-with_skill.txt`。
2. `no_skill`：按「no_skill 模板」生成同样三份产物，落盘到 `outputs/case-{id}-no_skill.txt`。**no_skill 模板只给需求原文，不加载、不引用任何 skill 指令。**

### 步骤 2：打乱顺序做盲评（在 WorkBuddy 完成）

1. 生成 `blind-map.json`：把 6 份产物随机映射成中性编号 S1–S6，记录 `{ "S1": "case-35-with_skill", ... }`，**判定期间不向 judge 暴露真实 case_id 与 variant**。
2. 把 6 份产物按 S1–S6 编号重命名成盲评副本，连同 `judge-prompt.md` 交给 judge。

### 步骤 3：独立 judge 判定（你在 opencode 客户端完成）

1. 在 opencode 客户端**切换到与 runner 不同的模型**。
2. 打开 `judge-prompt.md`，按里面 13 条 check 逐条判 6 份盲评产物，每条给 `true`/`false` + 证据位置。
3. 把结果回填到 `judge-results.jsonl`（字段见下），或直接交给我整理。

### 步骤 4：揭开盲评 + 汇总（在 WorkBuddy 完成）

1. 按 `blind-map.json` 把 A/B 映射回真实 case_id + variant。
2. 生成 `runs.jsonl`，跑 `python scripts/skill-evals.py --skill test-case-engineer --results runs.jsonl --expected-runs 1 --variants with_skill no_skill`。
3. 计算 `with_skill` 与 `no_skill` 各自通过率，做配对对比，写报告。

## 4. 判定结果字段契约（judge-results.jsonl 每行）

```json
{"blind_id": "A", "check_results": [true, false, ...], "evidence": ["...", ...]}
```

- `blind_id`：盲评编号（A/B/…），长度等于该产物 checks 条数。
- 判完后由 `blind-map.json` 映射回真实 `(case_id, variant)`，再拼进 `runs.jsonl`。

## 5. 结论门槛（发布前置条件，来自协议 §7）

只有**同时满足**才可写「效果结论」：

1. Tier 1 六项校验全绿；
2. `with_skill` 与 `no_skill` 两组配对完整、无 `invalid_runs`/`unpaired_runs`；
3. judge 与被测模型独立（你已确认能切不同模型），并附盲评说明；
4. 报告列出未评估维度、未覆盖 case、dry_run 项；
5. 未用 dry_run 结果支撑任何提升类表述。

`status = partial` 时**不得**下结论；小规模试点只能给「方向性观察」，不能叫「整体通过率」或「质量分数」。

## 6. 诚实边界

- 本轮是 **3/42 case、单 variant 对照、1 次重复**，只能回答「这 3 条 case 上，有 skill 是否比裸模型好」，**不能**外推到整体。
- 若 `no_skill` 组在 #35/#37/#39 上与 `with_skill` 打平或更差，不必然说明 skill 无用——可能是这 3 条 case 本身简单、或 judge 口径对 skill 优势不敏感（这正是 2026-09-15 历史 81/81 零区分度的问题）。
- 完整结论仍需 42 task + 12 trigger × 3 variant × 3 次重复（约 486 次调用）。
