# 完整 Tier 2/3 铺开执行手册（阶段 P）

> 目标：42 task × with_skill/no_skill 两 variant × 1 次 + 12 trigger，用独立 judge（zcode，不同厂商模型）做盲评，产出「有 skill 是否更好」的整体方向性结论。
> 状态：runner 生成阶段由 WorkBuddy 完成；judge 判定阶段待 zcode 可用（23:00 后）。

## 一、分工与独立性

| 角色 | 执行者 | 模型 | 说明 |
|---|---|---|---|
| runner | WorkBuddy | DeepSeek（reasoning） | 生成 84 份 task 产物 + 24 次 trigger 判定 |
| judge | zcode | 与 DeepSeek 不同厂商的模型 | 盲评 task 产物（219 checks × 2 variant），判定 trigger 布尔 |

> ⚠️ judge 必须与 runner 不同厂商，否则结论降级为「未满足严格独立性」。zcode 若只能给 DeepSeek 同源模型，需如实标注。

## 二、规模

| 项 | 数量 |
|---|---|
| task 产物生成 | 42 × 2 variant = **84 份** |
| task judge 判定 | 219 checks × 2 variant = **438 条** |
| trigger 判定 | 12 × 2 variant = **24 次**（布尔） |

## 三、目录结构

```
docs/skill-evaluation/tier23/full/
├── outputs/
│   └── task-{id}-{variant}.txt          # 84 份 task 产物
├── trigger-results.jsonl                 # trigger 判定（predicted_trigger）
├── judge-results.jsonl                   # task 盲评结果
├── runs.jsonl                            # 汇总契约
└── report.md                             # 最终报告
```

## 四、执行步骤

1. **runner 生成**（WorkBuddy，本阶段做）：按 `runner-prompt.md` 的两 variant 模板，批量生成 84 份产物。
2. **judge 盲评**（zcode，23:00 后）：按 `judge-batch.py` 脚本，把 84 份产物 + 219 checks 喂给 zcode，产出 `judge-results.jsonl`。
3. **trigger 判定**（zcode）：读 SKILL.md 触发/路由规则，判 12 条 trigger 的 `should_trigger`，产出 `predicted_trigger`。
4. **汇总**：`python scripts/skill-evals.py --skill test-case-engineer --results runs.jsonl --expected-runs 1 --variants with_skill no_skill`。
5. **报告**：with_skill vs no_skill 整体通过率对比 + trigger 混淆矩阵（precision/recall）。

## 五、诚实边界（不可突破）

- 本轮 42 task × 2 variant × 1 次，`status = partial`（缺 3 次重复、缺 old 对照），**仍不能叫「可发布整体结论」**，只能叫「方向性观察」。
- 只有补上 3 次重复 + old(v9.10.0) 对照 + trigger 完整后，才能宣称「可发布」。
- 42 条 task 里 #1–#32 是历史用例（含「输出包含 XX」类存在性断言，区分度低），#33–#40 是新设计的高区分度用例——整体通过率会被前者稀释，报告需分层呈现。
