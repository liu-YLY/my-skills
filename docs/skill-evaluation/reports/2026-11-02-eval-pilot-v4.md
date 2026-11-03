# pilot v4：两处规则/断言一致性修复的验证（阶段 J）

> 日期：2026-11-02
> 基线：分支 `feat/test-case-eval-pilot`（基于已合并的 `main` @ `4c13cee`），v9.11.0
> 触发：用户批准「继续继续」，执行阶段 I 报告 §4 建议的优先项 ① —— 修两处一致性问题再重跑
> 边界：**pilot v4，不是质量结论、不是整体通过率**；四次 pilot 结果互不可比，理由见 §7
> 配套：[rubric](../eval-pilot-rubric.md)、[v3 报告](2026-11-02-eval-pilot-v3.md)、[v2 报告](2026-11-02-eval-pilot-v2.md)、[v1 报告](2026-11-01-eval-pilot.md)、[评测执行协议](../test-case-quality-eval-protocol.md)

## 1. 目的

阶段 I 的无提示污染基线 11/13 暴露两处「规则与断言不一致」问题：#35 需求未给错误文案时 runner 写「文案待需求补充」导致预期不可判定；#39 断言假设每条用例都设「关键检查点」，但该字段在 skill 里本为可选。本阶段修这两处并重跑，验证是否消除「合规却被判 false」的噪音。

## 2. 本阶段改动（3 处，均为规则/断言对齐，不新增规则文件）

| # | 文件 | 改动 |
|---|---|---|
| J1 | `plugins/testing/skills/test-case-engineer/knowledge/writing-rules.md` L241 | 在 `expected_results 规范` 新增：需求未给出具体文案、数值或错误码时，不写「文案待补充」「待确认」占位；改用可观察的结构化事实作预期，并在需求理解或「原文问题清单」中标注缺失的文案 |
| J2 | `plugins/testing/skills/test-case-engineer/test-prompts.json` #39 第 5 条 | 「关键检查点写在其所依赖的步骤之后，不集中到文末」→「若设有关键检查点，每项标注所依赖的步骤号并就近写；未设检查点时业务结果须完整可判定」 |
| J3 | `docs/skill-evaluation/eval-pilot-rubric.md` #39 第 5 行 + header | 判定口径同步改写；header 指向冻结套件 v3 与本报告 |

冻结套件 **v3**：`docs/skill-evaluation/2026-11-02-test-case-quality-cases-v3.json`，54 cases / 219 task checks / 12 trigger，SHA256 `70cdec7cf7b4d194080380e064ef5af8f7b427fdb349d6c8f33a1f3663831761`，29828 bytes。v1（`a504f741…`，217 checks）、v2（`aaf6fa42…`，219 checks）保留为历史，历史报告引用未改写。checks 条数与 v2 相同，仅 #39 第 5 条文本变化。

## 3. 方法

| 环节 | 实现 |
|---|---|
| 套件 | 冻结套件 **v3**；pilot 用其中 #35(4) / #37(4) / #39(5) 共 13 条 |
| runner | 与 v3 **完全相同的统一、无额外提示**指令（只读 skill 文件 + 三条请求原文，不点出任何句式/预算/标题要求）；三条产物一次性重新生成 |
| 产物 | `pilot/outputs/case-{35,37,39}-v4.txt`（239 / 458 / 325 行；6646 / 11327 / 9915 字符），v1–v3 文件全部保留 |
| judge | 独立子代理 `lite` 配置，不读 skill 指令文件，按 rubric 逐条判定 13 项；判定在上下文压缩前已产出，本次对每条 `false` 与关键 `true` 复核了产物证据 |
| 结果 | `pilot/runs-v4.jsonl`（3 行 / 13 条判定；字符数与 SHA256 由真实文件计算并复验一致） |
| 汇总 | `python scripts/skill-evals.py --results docs/skill-evaluation/pilot/runs-v4.jsonl --expected-runs 1 --variants with_skill` |

| 产物 | SHA256 |
|---|---|
| `case-35-v4.txt` | `715581cdc3d0d35c480a725f082fa43f0c5738a2d236d137192e4ea4ed802a66` |
| `case-37-v4.txt` | `6cca531805f29e76cb81917793d35c8f247e5120b973da686287573e8155c230` |
| `case-39-v4.txt` | `5767233042386dd464c985f460aabdfc3a49ace22cc5eec114a070f44468287a` |

## 4. 结果

| case | 判定项 | v3 | **v4** | v4 判定数组 |
|---|---:|---:|---:|---|
| #35 精简 | 4 | 3/4 | **3/4** | `[false, true, true, true]` |
| #37 覆盖全 | 4 | 4/4 | **4/4** | `[true, true, true, true]` |
| #39 可读性 | 5 | 4/5 | **5/5** | `[true, true, true, true, true]` |
| 合计 | 13 | 11/13 | **12/13** | 12 true |

`--results`：`status = partial`、`checks_passed 12 / 13`、`invalid_runs = []`、`unpaired_runs = []`、`unexpected_runs = []`、`mean_output_characters 9296.0`、`completed_runs 3 / expected_runs 277`、`completion_rate 1.08%`。

> 口径说明：v1–v3 报告写的「3/54」指**冻结套件规模**；`--results` 默认按 `--skill` 加载的是全仓库评测集，故实际 `expected_runs = 277`。本报告按工具真实输出记录，不沿用旧表述。

**分数只涨 1，但内部换了位置**：#35 第 4 条 false→true、第 1 条 true→false；#39 第 5 条 false→true。净增 1。见 §5 / §6。

## 5. 两处目标修复的验证（本阶段主要产出）

### 5.1 J1 生效：#35 第 4 条 false → true

v3 把空值 / 格式错误写成「长度提示（文案待需求补充）」，预期不可独立判定。v4 中：

- `case-35-v4.txt` L143 / L166 / L189 三条非法输入的业务结果均为「『昵称』行仍显示 `旧昵称`」「『昵称』输入框下方出现错误提示」；
- 有效值 L96、L115–119 给出具体显示值，边界值 L93 / L96 给出具体值；
- 「原文问题清单」L29 标注「未给出空值/超长/非法字符的错误提示文案 → 用例改用可观察结构化事实，不写文案占位」。
- 3 处「待补充」均落在需求追溯表与待确认项，**没有一处落在用例预期里**（正是 J1 允许的位置）。

四类输入各有独立可判定预期，**验证了「不编造」与「可判定」可以同时满足**。归因边界：仅 1 个样本、1 次重复、runner 输入因新增规则而变化；可观察为「规则改动后该类占位消失」，不构成统计意义上的质量提升。

### 5.2 J2 / J3 生效：#39 第 5 条 false → true

`case-39-v4.txt` 全文 **0 处「关键检查点」**，但有 8 处「业务结果」段（L102 / 127 / 152 / 176 / 200 / 226 / 250 / 278），每条给出具体值，可逐条判定。按新口径「未设检查点时业务结果须完整可判定」判 true。

这里消除的是**断言假设了 skill 本为可选的字段**造成的「合规却被判 false」噪音；`true` 主要归因于断言口径改写，不是产物写法变好。

## 6. 新暴露：#35 第 1 条暴露第三处软硬口径不一致

`case-35-v4.txt` L71 明确写：「用例总数 10 条（含紧凑表格组 5 行），超出单字段纯校验 ≤8 条软预算；超出理由：…按 `case-arrangement.md` 在开头写明理由，预算不作硬性门槛」。产物按 `case-arrangement.md` L77「**软预算**；超出时在用例集开头写明理由，**不把预算当硬性扣分或质量门槛**」合规地超了预算，且写了理由与编排策略。

但 #35 check #1 是「**用例总数不超过 8 条**，且开头写明所采用的编排策略」。按 rubric §1 第 4 条「一条 check 含多个条件时全部满足才判 true」，10 > 8 即判 `false`。

这与 §5.2 是同类问题：**断言把规则里的软约束写成了硬门槛**。三种处理方向（本阶段未擅自改动）：

1. 把 #35 第 1 条改成「用例总数在预算内，或超出时在开头写明理由」，与 `case-arrangement.md` 对齐 —— **推荐**，成本最低且继续消除「合规却被判 false」噪音；
2. 收紧 `case-arrangement.md` 把预算改为硬上限 —— 与既有「软预算」设计冲突，会动摇阶段 C 的精简策略；
3. 保留现状，在 rubric 中显式标注「该 check 测的是硬门槛，与软预算规则不等价，结果仅作观察」。

另需注意：v3 的 #35 第 1 条为 `true`（产物恰好 ≤8 条），v4 为 `false` 属产物重新生成的波动 + 口径冲突共同作用，**不能归因于 J1 规则改动**。

## 7. 四次 pilot 不可比（重要）

| 项 | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| runner 指令 | 标准 | 额外强调句式（给答案） | 统一、无额外提示 | 与 v3 相同 |
| 产物来源 | 三条各生成 1 次 | 仅重生成 #39 | 三条全部重生成 | 三条全部重生成 |
| skill 规则 | v9.11.0 | v9.11.0 | v9.11.0 | **v9.11.0 + J1 新增规则** |
| 判定口径 | 12 条 | 13 条（拆分复合断言） | 13 条 | **13 条（#39 第 5 条改写）** |
| 判定项数 | 12 | 13 | 13 | 13 |
| judge 配置 | `lite` | `lite` | `lite` | `lite` |
| 结果 | 11/12 | 13/13 | 11/13 | **12/13** |

v2 有提示污染；v3 → v4 之间 skill 规则与判定口径**同时**变化。**12/13 不是质量提升证据，四次数字不可作趋势或 keep/revert 依据。**

## 8. 工具链副发现：`--cases-file` 与冻结套件格式语义不同

本阶段额外尝试把冻结套件 v3 作为 `--cases-file` 直接回喂汇总器：

```bash
python scripts/skill-evals.py \
  --cases-file docs/skill-evaluation/2026-11-02-test-case-quality-cases-v3.json \
  --results docs/skill-evaluation/pilot/runs-v4.jsonl --expected-runs 1 --variants with_skill
```

报错 `ValueError: ...: 1 has no expectations`。原因：`read_cases()` 期望**源格式**（`expectations` / `validation_points`），而三代冻结套件都是 `--json` 导出的**归一化格式**（`checks`）。这是既有的接口语义差异（v1 / v2 / v3 一致），**不是 v3 引入的回归**；协议 §3 也只把 `--json` 定义为 runner 输入、把 `--results` 定义为按 `--skill` 加载。

本次**未改脚本**，默认加载口径已跑通（§4）。若后续需要让冻结套件可直接回喂，属工具链专项，需用户单独拍板。

## 9. 不得宣称的边界

- 仍为 **3 条 case**、单 `with_skill` variant、1 次重复、**无 baseline / no_skill 对照**；不能回答「有 skill 是否更好」
- judge 与 runner 属同模型家族的不同配置，未满足协议 §4 的严格独立性；judge 未做盲评复核
- `duration_seconds = 0` 占位；`status = partial`，协议 §7 规定 partial 不得发布结论
- 完整 Tier 2/3 仍未执行，无质量分数、token 未重测；历史 `runs*.jsonl` 与当前套件不兼容
- 本报告不含「质量提升 / 退化」结论；结果不可作 keep/revert 依据
- J1 修改的是 skill 生成规则，但**未升版本**（仍 v9.11.0）、未推送、未建 PR

## 10. 阶段 J 停止点

已交付：3 处规则/断言改动、冻结套件 v3、3 份 v4 产物、`runs-v4.jsonl`、`--results` 验证、本报告、协议 §8 与计划 §9.8 状态写回。

下一步需用户决定：

1. 按 §6 推荐改 #35 第 1 条断言，消除第三处软硬口径不一致后再重跑；
2. 提供外部 runner + 独立 judge 跑完整 Tier 2/3（用冻结套件 v3、219 checks，三 variant 约 486 次调用）；
3. 处理 §8 的 `--cases-file` 工具链语义；
4. 回到可选阶段 D（规则收敛）/ E（覆盖度可计算）；
5. 停在 v9.11.0，把 J1 的规则改动随下次版本发布一并升版本。
