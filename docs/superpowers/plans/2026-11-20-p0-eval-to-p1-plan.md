# Skill 评测 P0 → P1 后续计划

> 状态：**P0 机器可执行部分完成；等待 2 名人工评审员回收评分表**
> 日期：2026-11-20
> 分支策略：`backup/p0-eval-baseline-2026-11-20` 仅作归档备份，**不作为 PR 分支**
> 配套资产：[需求文档](../skill-evaluation/pdd-commerce-benchmark/requirements-pdd-auth-cart-order.md)｜[Benchmark](../skill-evaluation/pdd-commerce-benchmark/benchmark-v1.json)｜[评分卡 v1.1.1](../skill-evaluation/pdd-commerce-benchmark/scoring-rubric.md)｜[P0 报告](../skill-evaluation/pdd-commerce-benchmark/reports/2026-11-17-p0-pilot.md)

---

## 1. 当前状态（已实测）

| 项 | 结果 | 证据 |
|---|---|---|
| P0 产物 | 3 任务 × 2 变体 × 3 重复 = 18 份 | `runs/2026-11-17-p0/outputs/raw/` |
| G0 结构闸门 | 18/18 通过 | `runs/2026-11-17-p0/checks.json` |
| 总分宏平均 | with_skill **79.2** vs no_skill **30.4** | `scores/2026-11-17-p0/summary.json` |
| 配对 | 9/9 胜，符号检验 p=0.0020 | 同上 |
| A/A | REV-ORDER 三次均 85.2，差 0.0 | 同上 |
| 同源复核 kappa | 均值 **0.8318**；D2 **0.6364**、D6 **0.6923** 低于 0.70 | `scores/2026-11-17-p0/kappa.json` |
| 用例可读性 R1-R4 | with_skill **3.8** vs no_skill **1.9**；3-5 秒通过率 100% vs 20%-40% | `scores/2026-11-17-p0/readability.json` |
| 人工 kappa | **未测**；两名独立评审员尚未评分 | 待回收 |
| 结论档位 | **N（未证实）**；N=9，不能声称提升 | P0 报告 §6 |

已知限制：

- runner、R1 评分、R2 复核同源；kappa 是上限估计，不是人工 inter-rater reliability。
- 18 份产物由同一会话模型生成；正式结论前应补独立 runner。
- `p0_import_review.py` 只用同源 CSV 做过 dry-run，尚未导入真实人工评分。
- D2/D6 锚点已在评分卡 v1.1.1 细化，但尚未用人工评分复验。

---

## 2. 分支与推送策略

| 项 | 决定 |
|---|---|
| 归档分支 | `backup/p0-eval-baseline-2026-11-20` |
| 是否 PR | **否**。backup 分支只用于保存当前快照，不发起 PR |
| 是否合并 main | 暂不合并；P0 人工评审通过后再决定 |
| 后续 PR 分支 | 人工评审完成后，从最新 `main` 创建 `feat/p0-eval-baseline`，用干净提交重新提交最终状态 |
| 历史提交 | 当前分支包含若干自动提交（`feat: update workspace`）；backup 分支保留历史，不在 PR 中复用 |
| 禁止操作 | 不 force push；不直接改 main；不在评分期间改 benchmark |

---

## 3. 阶段计划

### P0-A 人工评审（当前停止点）

| 项 | 内容 |
|---|---|
| 目标 | 2 名独立评审员对 18 份盲产物评分，验证评分卡可用 |
| 输入 | `runs/2026-11-17-p0/reviewer/P0-review-workbook-R1.xlsx` / `R2.xlsx` |
| 输出 | 两份 `score-sheet-R1.csv` / `R2.csv` |
| 通过条件 | mean kappa ≥ 0.70；D2、D6 单项 ≥ 0.70；R4 通过率差异 ≤ 0.20；S1 一致率 ≥ 0.90 |
| 失败处理 | 进入 P0-B，只修评分卡锚点，不改 skill / benchmark |

**恢复步骤**：

```bash
python3 scripts/p0_import_review.py \
  --r1 runs/2026-11-17-p0/reviewer/score-sheet-R1.csv \
  --r2 runs/2026-11-17-p0/reviewer/score-sheet-R2.csv
```

### P0-B 评分卡复验（条件触发）

| 触发 | 动作 | 退出条件 |
|---|---|---|
| D2/D6 仍 < 0.70 | 补锚点示例、拆分边界条目、加 3-5 秒样例 | 两名评审员重新评分后达标 |
| R4 复述一致率 < 0.80 | 统一「测什么/为什么/预期」复述模板 | 复述一致率 ≥ 0.80 |
| S1 判定不一致 | 细化 S1 清单与证据要求 | S1 一致率 ≥ 0.90 |

纪律：P0-B 只改评分卡，不根据评分结果改 must-cover 或开放问题。

### P0-C 独立 runner 复核（建议）

| 项 | 内容 |
|---|---|
| 目标 | 排除同源会话污染 |
| 做法 | 用独立 runner 重新生成 18 份产物，保持同一 prompt、同一变体 |
| 对比 | 新旧产物分数差、must-cover 命中差、S1/S2 差 |
| 通过 | 差异不改变 P0 结论方向；否则以独立 runner 结果为准 |

### P1 全量人工基线

| 项 | 内容 |
|---|---|
| 范围 | 10 任务 × 3 变体 × 3 重复 = 90 份产物；人工评分 120 份（含 4 次重复校准） |
| 变体 | `no_skill` / `with_skill` / `reference` |
| 通过条件 | A/A 通过；覆盖率 3 类任务齐全；报告含 P/N/X/?；N ≥ 30 才可判 P |
| 输出 | 首份正式版本对照报告 + 标注数据集 |

### P2 AI 影子评分

| 项 | 内容 |
|---|---|
| 前提 | P1 人工 kappa ≥ 0.70；≥ 120 个标注样本 |
| 做法 | 不同族 AI judge 与人工并行评分，AI 不参与决策 |
| 通过 | AI-人工 kappa ≥ 0.75；S1/S2 一致率 ≥ 0.90；MAE ≤ 0.5；各维度偏差 ≤ 0.5 |
| 不通过 | 继续人工评分，优先修 rubric 与证据要求 |

### P3 AI 初评 + 人工审计

| 项 | 内容 |
|---|---|
| 做法 | AI 给初评；人工审计 20% 随机样本 + 100% S1/S2 + 55-65 边界样本 |
| 通过 | 连续 3 轮审计通过；月度漂移 kappa ≥ 0.70 |
| 回退 | kappa < 0.70 回到 P2；连续两次 S1 漏判回到 P1 |

### P4 扩展与防过拟合

| 项 | 内容 |
|---|---|
| 新变体 | 售后、优惠券叠加、跨境、登录风控等 |
| sealed 集 | 保留不公开的 held-out 任务，禁止写入 skill few-shot |
| 条目分析 | 淘汰饱和 must-cover；拆分低一致条目 |
| 复校 | 每季度固定锚点复校；版本升级双评分 |

---

## 4. 决策门与停止点

| 门 | 条件 | 不通过 |
|---|---|---|
| G0 人工评审 | mean kappa ≥ 0.70；D2/D6 ≥ 0.70 | 停，修评分卡，不进 P1 |
| G1 独立 runner | 差异不改变结论方向 | 以独立 runner 为准，重写 P0 报告 |
| G2 P1 全量 | N ≥ 30 且胜场达门槛 | 只写 N（未证实），不声称提升 |
| G3 AI 影子 | kappa ≥ 0.75；S1/S2 ≥ 0.90 | AI 不进入初评 |
| G4 AI 初评 | 连续 3 轮审计通过 | 回退 P2 |

---

## 5. 后续待办清单

- [ ] 评审员 A 填写 `P0-review-workbook-R1.xlsx`，导出 `score-sheet-R1.csv`
- [ ] 评审员 B 填写 `P0-review-workbook-R2.xlsx`，导出 `score-sheet-R2.csv`
- [ ] 运行 `p0_import_review.py`，检查 mean kappa / D2 / D6 / R4
- [ ] 若 kappa 不达标，进入 P0-B 修锚点并复评
- [ ] P0 通过后，创建 `feat/p0-eval-baseline` 干净分支，准备 PR
- [ ] 独立 runner 复核 18 份产物
- [ ] 进入 P1 全量 10 任务
- [ ] P1 报告通过后，进入 H1 AI 影子
- [ ] 每季度复校 sealed 集与评分卡

---

## 6. 不要做的事

- 不要从 `backup/p0-eval-baseline-2026-11-20` 直接发 PR。
- 不要用同源 AI 评分替代人工基线。
- 不要在人工 kappa 未达标时对外声称「skill 提升」。
- 不要在评分期间修改需求、must-cover 或评分卡。
- 不要把 benchmark 原题/答案逐字写进 skill few-shot。

---

## 7. 证据入口

| 证据 | 路径 |
|---|---|
| P0 报告 | `docs/skill-evaluation/pdd-commerce-benchmark/reports/2026-11-17-p0-pilot.md` |
| 评审员包 | `docs/skill-evaluation/pdd-commerce-benchmark/runs/2026-11-17-p0/reviewer/` |
| 评分汇总 | `docs/skill-evaluation/pdd-commerce-benchmark/scores/2026-11-17-p0/summary.json` |
| kappa | `docs/skill-evaluation/pdd-commerce-benchmark/scores/2026-11-17-p0/kappa.json` |
| 可读性 | `docs/skill-evaluation/pdd-commerce-benchmark/scores/2026-11-17-p0/readability.json` |
| 工具 | `docs/skill-evaluation/pdd-commerce-benchmark/scripts/` |
