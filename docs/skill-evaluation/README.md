# Skill 评测档案索引

> 本目录存放全部 Skill 测评相关的**标准、数据、报告与执行记录**。
> 本文件是唯一入口：新增任何文件必须在此登记，否则视为孤儿文件。
>
> 现行标准：[methodology.md](methodology.md) v1.5

## 快速导航

| 你要做什么 | 从这里开始 |
|---|---|
| 第一次评测一个 skill | [methodology.md](methodology.md) §2 总览 → [scoring-template.md](scoring-template.md) |
| 判断 skill 是积极还是消极 | [methodology.md](methodology.md) §13 归因判定 |
| 给 test-case-engineer 跑评测 | [test-case-quality-eval-protocol.md](test-case-quality-eval-protocol.md) |
| 复现某个历史结论 | 在 §3 报告表中找到日期，按该报告引用的套件与 SHA 复跑 |
| 写一份新报告 | 复制 [scoring-template.md](scoring-template.md)，元信息四项必填（套件 SHA / judge 族系 / A/A 一致率 / 净效应档位） |

---

## 1. 现行标准

| 文件 | 作用 | 状态 |
|---|---|---|
| [methodology.md](methodology.md) | 两层 × 十维评分 + §12 无效改进识别 + §13 归因判定 | **现行 v1.5** |
| [scoring-template.md](scoring-template.md) | 可填写评分表 + 净效应判定段 | **现行 v1.5** |
| [test-case-quality-eval-protocol.md](test-case-quality-eval-protocol.md) | test-case-engineer 专用执行协议（阶段划分、断言口径、产物路径） | 现行 |
| [eval-pilot-rubric.md](eval-pilot-rubric.md) | pilot 判定口径（Tier 2/3 执行清单） | 现行 |
| [business-regressions.json](business-regressions.json) | 业务回归清单 | 现行 |
| [2026-09-15-business-rules.md](2026-09-15-business-rules.md) | 业务规则一致性检查说明 | 现行 |

## 2. 评测数据

### 2.1 现行套件

| 文件 | 规模 | 说明 |
|---|---|---|
| [2026-11-17-quality-suite-v7.1.json](2026-11-17-quality-suite-v7.1.json) | 70 task / 12 trigger / 354 checks | **现行冻结版本**。修复 #13 评级口径、#7/#19 抽样口径；其余同 v7。SHA `dd2f1b49` |
| [2026-11-17-test-point-cases.json](2026-11-17-test-point-cases.json) | 10 cases | 测试点种子集：需求条目、期望测试点、范围外项与结果型 checks。SHA `dc900b79` |
| [2026-11-17-requirement-review-cases.json](2026-11-17-requirement-review-cases.json) | 12 cases / 61 seeded defects | 需求评审种子集：每个 PRD 预埋 5-6 个缺陷，附位置、原文、类型、严重级别与期望问题。SHA `aee2ed36` |

> v7 / v7.1 使用 `task_cases` + `trigger_evals` 结构，`scripts/skill-evals.py --cases-file` 可直接读取；v6 及更早为 list 结构。

### 2.2 历史冻结套件（保留仅为复现历史报告，勿用于新评测）

| 文件 | checks | 差异 | SHA256 前缀 |
|---|---:|---|---|
| [2026-11-01-test-case-quality-cases.json](2026-11-01-test-case-quality-cases.json) | 217 | v1 初版 | `a504f741` |
| [2026-11-02-test-case-quality-cases.json](2026-11-02-test-case-quality-cases.json) | 219 | v2，新增断言 | `aaf6fa42` |
| [2026-11-02-test-case-quality-cases-v3.json](2026-11-02-test-case-quality-cases-v3.json) | 219 | v3，仅 #39 文本 | `70cdec7c` |
| [2026-11-02-test-case-quality-cases-v4.json](2026-11-02-test-case-quality-cases-v4.json) | 219 | v4，与 v3 差 1 处 | `4a81d91f` |
| [2026-11-02-test-case-quality-cases-v5.json](2026-11-02-test-case-quality-cases-v5.json) | 219 | v5，与 v4 差 #32 | `9a0520ed` |
| [2026-11-03-test-case-quality-cases-v6.json](2026-11-03-test-case-quality-cases-v6.json) | 219 | v6，修复 #13/14/16/19/20/21 缺料，仍为 list 结构 | `a8fcdc82` |
| [2026-11-17-quality-suite-v7.json](2026-11-17-quality-suite-v7.json) | 354 | v7，补 category + 结果型断言；#13/#7/#19 口径未修 | `ae880180` |

### 2.3 批次数据

| 批次 | 内容 | 证据强度 |
|---|---|---|
| [2026-09-15/](2026-09-15/) | 早期评测：answers / runs / browser-results / summary | 历史基线，元数据不完整 |
| [2026-09-21/](2026-09-21/) | **唯一成对评测记录**（paired-results.jsonl + paired-review.md） | `partial`：未记录 judge 耗时与退化场景 |
| [2026-10-09/](2026-10-09/) | 触发 / 行为 / 确定性 / 浏览器 / 最终回归五件套 | 触发部分为**元数据分类**，非宿主真触发 |
| [data-generator-2026-10-14/](data-generator-2026-10-14/) | data-generator 完整证据链（38 份原始产物 + 26 项校验输出 + README 说明） | 强：产物落盘 + SHA 可核 |
| [pilot/](pilot/) | 11-01 / 11-02 的 3-case pilot（runs.jsonl + v2–v5） | 单 case 试跑，用于调口径 |
| [tier23/](tier23/) | N=40 配对 + 盲评（blind/ + full/），含原始产物 84 份；判分脚本锁定**套件 v5**（`full/judge_batch.py` 硬编码，属可复现设计，勿改为 v6） | 中等：配对完备，judge 未换族 |

## 3. 报告

> 判定强度标签：**强** = 产物落盘 + 多轮 + 判据可核；**中** = 配对完整但 judge 同族或未换族；**弱** = N=1 / dry_run / 方向性。

### 3.1 方法论建立期（2026-08）

| 报告 | 主题 | 强度 |
|---|---|---|
| [v1.1-vs-v1.2-comparison-2026-08-06.md](reports/v1.1-vs-v1.2-comparison-2026-08-06.md) | 方法论自身版本对比（v1.1 → v1.2 的改动依据） | 弱（方法论演进记录） |
| [test-case-engineer-2026-08-06.md](reports/test-case-engineer-2026-08-06.md) | test-case-engineer 首次十维评分 | 弱（N=1） |
| [bug-analyzer-2026-08-06.md](reports/bug-analyzer-2026-08-06.md) | bug-analyzer 首次十维评分 | 弱（N=1） |
| [test-case-engineer-2026-08-17.md](reports/test-case-engineer-2026-08-17.md) | 语言风格优化版评分 | 弱（N=1） |
| [none-vs-simple-vs-full-comparison-2026-08-18.md](reports/none-vs-simple-vs-full-comparison-2026-08-18.md) | **三条件对照**（无 skill / 简单 / 全量） | 中（成本数据强，质量结论弱） |
| [test-case-engineer-v8.5-verification-2026-08-18.md](reports/test-case-engineer-v8.5-verification-2026-08-18.md) | v8.5.0 优化验证（三条件重跑） | 弱（N=1） |
| [usecase-skills-family-review-2026-08-21.md](reports/usecase-skills-family-review-2026-08-21.md) | 用例 skill 家族审查 | 弱（静态） |
| [usecase-skills-consistency-fix-final-report-2026-08-21.md](reports/usecase-skills-consistency-fix-final-report-2026-08-21.md) | 一致性修复交付 | 弱（静态） |

### 3.2 工程验证期（2026-10）

| 报告 | 主题 | 强度 |
|---|---|---|
| [2026-10-10-skill-workflow-token-usage-report.md](reports/2026-10-10-skill-workflow-token-usage-report.md) | 工作流与 token 消耗测量 | 中（计量可核） |
| [2026-10-14-test-data-generator-verification.md](reports/2026-10-14-test-data-generator-verification.md) | test-data-generator 实现与验证 | 强 |
| [2026-10-31-baseline.md](reports/2026-10-31-baseline.md) | 测试 skill 基线记录 | 中 |

### 3.3 质量评测期（2026-11）

| 报告 | 主题 | 强度 |
|---|---|---|
| [2026-11-01-test-case-quality-baseline.md](reports/2026-11-01-test-case-quality-baseline.md) | 四目标评测基线（阶段 A） | 中 |
| [2026-11-01-eval-pilot.md](reports/2026-11-01-eval-pilot.md) | 3-case pilot（单 variant） | 弱 |
| [2026-11-01-stage-b-machine-check-dryrun.md](reports/2026-11-01-stage-b-machine-check-dryrun.md) | 机器校验接入离线对照 | 弱（dry_run） |
| [2026-11-01-stage-c-conciseness-dryrun.md](reports/2026-11-01-stage-c-conciseness-dryrun.md) | 精简约束落地对照 | 弱（dry_run） |
| [2026-11-01-test-case-quality-delivery.md](reports/2026-11-01-test-case-quality-delivery.md) | 四目标优化交付（v9.11.0） | 中 |
| [2026-11-02-assertion-consistency-audit.md](reports/2026-11-02-assertion-consistency-audit.md) | 断言-规则一致性排查（阶段 L） | 中（静态审计） |
| [2026-11-02-eval-pilot-v2.md](reports/2026-11-02-eval-pilot-v2.md) | 断言修正与 pilot v2 | 弱 |
| [2026-11-02-eval-pilot-v3.md](reports/2026-11-02-eval-pilot-v3.md) | 三轮一致干净基线 | 中 |
| [2026-11-02-eval-pilot-v4.md](reports/2026-11-02-eval-pilot-v4.md) | 两处修复验证 | 中 |
| [2026-11-02-eval-pilot-v5.md](reports/2026-11-02-eval-pilot-v5.md) | 软预算口径对齐 + 配对复核 | 中 |
| [2026-11-02-eval-tier23-small-control.md](reports/2026-11-02-eval-tier23-small-control.md) | 小规模真实对照（方向性） | 中 |
| [2026-11-03-eval-fix-suite-gaps.md](reports/2026-11-03-eval-fix-suite-gaps.md) | 修复套件缺料后的完整对照（阶段 Q） | 中 |
| [2026-11-03-eval-tier23-full.md](reports/2026-11-03-eval-tier23-full.md) | **42 task × with/without 完整对照** | 中（当前最强单份） |
| [2026-11-17-quality-baseline.md](reports/2026-11-17-quality-baseline.md) | 阶段 1 确定性基线；模型行为评测 `blocked` | 中（确定性）/ 模型行为未执行 |
| [2026-11-17-eval-rule-consistency.md](reports/2026-11-17-eval-rule-consistency.md) | v7 断言-规则一致性扫描 | 中（静态审计） |

## 4. 执行档案

| 目录 | 内容 | 说明 |
|---|---|---|
| [../superpowers/plans/](../superpowers/plans/) | 12 份实施计划（2026-07 → 2026-11） | 已完成事项的历史档案，不再更新 |
| [../superpowers/specs/](../superpowers/specs/) | 2 份设计文档（testing skills 扩展、状态机设计） | 已完成事项的历史档案 |
| [rule-inventory/](rule-inventory/) | 4 个首批 skill 的规范语句清单与 D1–D5 分类 | 瘦身前置材料，由 `scripts/extract-rule-inventory.py` 生成 |

## 5. 建议阅读顺序

1. [methodology.md](methodology.md) §2 + §13 —— 先建立"评分"与"净效应"是两个维度
2. [2026-11-03-eval-tier23-full.md](reports/2026-11-03-eval-tier23-full.md) —— 看当前最强的一份实际对照怎么做的
3. [none-vs-simple-vs-full-comparison-2026-08-18.md](reports/none-vs-simple-vs-full-comparison-2026-08-18.md) —— 看成本维度如何给出不依赖 judge 的硬结论
4. [2026-10-09/trigger-validation.json](2026-10-09/trigger-validation.json) —— 看一个**效力有上限**的测试长什么样（`no_skill` 同样 tp=21）

## 6. 维护约定

1. **历史不改写**：结论被推翻时新增报告并注明取代关系，不修改旧报告内容与 SHA。
2. **新报告四项必填**：套件版本 + SHA256、judge 族系（是否与被测同族）、A/A 一致率、净效应档位（P / N / X / ?）。
3. **档位表述纪律**：N 档只能写"未证实"，不得写"有效"；X 档必须给出回滚或裁剪动作；? 档不得产出效果结论。依据 [methodology.md](methodology.md) §13.6。
4. **新增文件必须在本索引登记**，否则视为孤儿文件，在下一次清理中被移除。
5. **原始产物优先**：任何进入报告的数字都必须能追溯到落盘产物，追溯不到的数字不写入报告。
