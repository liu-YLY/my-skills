# 真实模型评测 pilot（3 条 case，单 variant）

> 日期：2026-11-01（阶段 G）
> 基线：`main` @ `4c13cee`（PR #137 已合并），分支 `feat/test-case-eval-pilot`
> 版本：`test-case-engineer` v9.11.0；冻结套件 54 cases / 217 checks
> 边界：**pilot，不是质量结论**。3/42 task、1 次重复、单 `with_skill` variant、无 baseline 对照；judge 与 runner 为同模型家族的不同配置，**未满足严格独立性**
> 配套：[判定口径与 Tier 2/3 执行清单](../eval-pilot-rubric.md)、[评测执行协议](../test-case-quality-eval-protocol.md)、[冻结套件](../2026-11-01-test-case-quality-cases.json)

## 1. 目的

用户选择「先跑真实模型评测」。完整 Tier 2/3 需要外部 runner（三 variant 约 486 次模型调用）与独立 judge，**当前仓库与会话无法独立完成**。本阶段把工具链真正跑通并产出一次小规模真实 pilot，验证「接上 runner 就能跑」的契约，而不是继续堆规则。

## 2. 方法

| 环节 | 实现 |
|---|---|
| 冻结用例 | `docs/skill-evaluation/2026-11-01-test-case-quality-cases.json`（SHA256 `a504f741…`） |
| runner | 独立子代理，模型配置 `reasoning`；只读 skill 指令文件，按 #35 / #37 / #39 三条请求生成 3 份产物 |
| 产物 | `docs/skill-evaluation/pilot/outputs/case-{35,37,39}.txt`，UTF-8 纯文本 |
| judge | 独立子代理，模型配置 `lite`；**不读 skill 指令文件**，只读 rubric + 产物 + checks，逐条给布尔判定与证据 |
| rubric | `docs/skill-evaluation/eval-pilot-rubric.md` §1 通用原则 + §2 三条 case 的 12 条逐条口径 |
| 结果 | `docs/skill-evaluation/pilot/runs.jsonl`，由真实产物的字符数 / SHA256 构造 |
| 汇总 | `python scripts/skill-evals.py --skill test-case-engineer --results docs/skill-evaluation/pilot/runs.jsonl --expected-runs 1 --expected-trigger-runs 1 --variants with_skill` |

`duration_seconds` 填 `0` 占位（本会话无法计量模型生成耗时，脚本仅校验 ≥0）；完整评测应由 runner 记录真实值。

## 3. pilot 结果

| case | 目标 | 判定项 | 通过 | judge 证据摘要 |
|---|---|---:|---:|---|
| #35 | 精简 | 4 | **4** | 开头写明「按用户旅程编排」，共 7 条用例（≤8）；7 条输入各不相同且附逐对去重说明；步骤无填充动作；四类输入各有含具体文案的可判定预期 |
| #37 | 覆盖全 | 4 | **4** | 阶段 1 列出 R1–R5 五条并明称覆盖分母；需求→测试点→用例映射表五条均指到用例 ID；未覆盖项单独成段；结论写「5/5 已设计用例」并带分母 |
| #39 | 可读性强 | 4 | **3** | 标题均以 `Webhook` 开头且含对象/条件/预期；动词与控件原文一致；检查点均标「步骤 N 后」。**第 2 条判 false**：产物业务结果中存在约 47 字的长构件且含 URL/英文，40 字口径含糊；另有标题含「选择…并点击…」多动作，judge 按「证据不足」判 false |

**合计 11/12 条判定项通过**（仅针对这 3 份产物，不是 skill 整体通过率）。

`--results` 汇总关键指标：

| 指标 | 值 | 说明 |
|---|---:|---|
| `status` | `partial` | 协议规定 partial 不得发布结论，本次符合预期 |
| `runs` / `expected_runs` | 3 / 54 | 完成率 5.56%，如实标记缺失的 51 条 |
| `checks_passed` / `checks_total` | 11 / 12 | 与 judge 判定一致 |
| `invalid_runs` | `[]` | 3 份产物的 `output_characters` 与 `output_sha256` 校验全部通过 |
| `unpaired_runs` / `unexpected_runs` | `[]` / `[]` | 字段契约与 case 键匹配无误 |
| `mean_output_characters` | 7557.3 | 三份产物的平均字符数 |

**工具链结论**：`--json → 产物 → runs.jsonl → --results` 全链路可跑通；确定性校验（字符数、SHA256、check_results 长度、variant/run 合法性）全部生效；`partial` 状态能正确阻止误发布结论。

## 4. 暴露的问题（有真实价值）

1. **#39 第 2 条断言本身口径不够可判定**：judge 对「超过 40 字的逗号分隔构件」是否计入英文/URL 产生疑问，并因标题多动作并存而判 false。这说明该 check 把两个独立条件（长句、单决策点）合并成一条，且未界定字符计数口径。按 [rubric](../eval-pilot-rubric.md) §1 第 4 条，复合 check 任一部分不满足即 false，容易把「规则问题」与「断言歧义」混在一起。**建议后续把 #39 第 2 条拆成两条，并写明 40 字按中文字符计、URL/字段名不计入**。
2. **产物偏长**：三份产物 201 / 337 / 259 行，平均 7557 字符。与「精简」目标相关，但单凭 pilot 不能判断是流程要求（四阶段交付）还是模型堆量，需 baseline 对照才能归因。

## 5. 不得宣称的边界

- 无 `no_skill` / `old` / `baseline` variant，**不能回答「有 skill 是否更好」**
- 3/42 task、1 次重复、completion_rate 5.56%，**不是整体通过率**，11/12 不可外推
- judge 与 runner 属同模型家族的不同配置，方法论 §7 的严格独立性未满足；judge 未做盲评复核
- `duration_seconds = 0` 为占位，`mean_duration_seconds` 无意义
- 本结果**不可作 keep/revert 依据**，不写入「质量提升」类结论；历史 `runs.jsonl` 仍与当前套件不兼容

## 6. 完整 Tier 2/3 的执行清单（待外部 runner）

详见 [rubric §4](../eval-pilot-rubric.md)：42 task × 3 次 = 126 次、12 trigger × 3 次 = 36 次；三 variant 对照为 task 378 + trigger 108 次；judge 需判 651 条（单 variant）。步骤为冻结用例 → runner 分组执行 → 产物落盘 → judge 逐条判定 → `--results --expected-runs 3` 汇总，只有 `status = evaluated` 才能发布结论。

外部依赖：批量模型 runner、与 runner 不同模型的独立 judge（或人工盲评并标注）、产物存储与计费/配额确认。沿用 2026-09-15 的 9 任务 × 3 次口径会有 81/81 零区分度问题，须使用 #33–#40 这类能区分好坏的任务。

## 7. 阶段 G 停止点

本阶段交付：rubric 与完整执行清单、3 份真实产物、judge 判定、`runs.jsonl`、`--results` 链路验证、pilot 报告。**未改动任何 skill 规则，未升版本**（仍 v9.11.0）。

下一步需用户决定：① 提供 runner/judge 环境以跑完整 Tier 2/3；② 先按 §4 修正 #39 第 2 条断言并重跑 pilot；③ 回到可选阶段 D/E；④ 直接停在 v9.11.0。
