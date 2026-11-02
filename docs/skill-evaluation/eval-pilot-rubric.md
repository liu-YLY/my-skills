# 评测判定口径与 Tier 2/3 执行清单

> 建立日期：2026-11-01（阶段 G）；2026-11-02 修订（阶段 H 拆分复合断言、阶段 J 对齐规则与断言、阶段 K 对齐软预算口径）
> 适用：`test-case-engineer` v9.11.0，冻结套件 v4 = 54 cases / 219 checks
> 边界：本文件是**判定口径与执行清单，不是评测结果**；v5 pilot 结果见 `reports/2026-11-02-eval-pilot-v5.md`，v4 见 `reports/2026-11-02-eval-pilot-v4.md`，v3/v2/v1 为历史
> 配套：[评测执行协议](test-case-quality-eval-protocol.md)、[冻结套件 v4](2026-11-02-test-case-quality-cases-v4.json)（v1 / v2 / v3 保留为历史）

## 1. judge 通用判定原则

1. 每条 check 单独判 `true` / `false`，并附产物中的证据位置（行号或原文片段）。
2. 只在产物文本里找证据；不得依据 skill 规则「应该怎么写」推断产物「写了什么」。
3. 证据不足、表述含糊、需要猜测的判 `false` 并注明「证据不足」，不给同情分。
4. 一条 check 含多个条件时（如「不超过 8 条，且开头写明编排策略」），全部条件满足才判 `true`。
5. judge 不读 skill 指令文件，只读产物、本 rubric 与 checks 文本，避免「知道期望答案」造成偏差。
6. judge 模型应与 runner 模型配置不同；做不到时必须在报告标注「未满足严格独立性」。

## 2. pilot 三条 case 的逐条口径

### #35 修改昵称（4 条）

| # | check | `true` 的判据 | 常见 `false` |
|---|---|---|---|
| 1 | 用例总数 ≤8，或超出 8 条时在开头写明超出的具体理由；并写明编排策略 | ≤8 条且有编排策略声明；或 >8 条但开头写明具体超出理由且有编排策略声明 | >8 条且未写明理由；无编排策略声明；理由空泛（如「需要更多用例」） |
| 2 | 不存在两条用例验证同一业务目标与同一条件 | 逐对比较标题、前置条件与关键输入，无等价重复 | 同一空值校验写两条、仅换 ID |
| 3 | 步骤不复述前置条件或无信息量导航 | 步骤中无「确认已登录」「打开浏览器进入系统」等 | 出现上述填充步骤 |
| 4 | 有效值/空值/格式错误/边界值各自可独立判定 | 四类各有对应用例或参数化行，且每条预期有具体值或文案 | 只写「提示错误」无文案、缺某一类 |

### #37 五条需求条目（4 条）

| # | check | `true` 的判据 | 常见 `false` |
|---|---|---|---|
| 1 | 阶段 1 列出 5 条可测需求条目作分母 | 明确列出 5 条并编号，且称为分母或基线 | 只写「覆盖手机号登录等」未列全 |
| 2 | 输出需求到测试点到用例对应关系，5 条均有对应用例 | 有对应关系表或清单，5 条都能指到用例 ID | 只给用例列表无映射 |
| 3 | 无对应用例的条目单独列出并写明原因 | 有未覆盖项则单独成段逐条写原因；全覆盖则明确写「无未覆盖项」 | 把未覆盖项混进统计，或什么都不写 |
| 4 | 覆盖结论不只用用例条数表达 | 按需求条目逐条给状态，或比例写明分母 | 只写「共 12 条用例，覆盖充分」 |

### #39 Webhook 创建（5 条）

| # | check | `true` 的判据 | 常见 `false` |
|---|---|---|---|
| 1 | 仅看标题可说出对象、条件、预期，且不以「验证」「测试」开头 | 每条标题都含被测对象、触发条件与预期行为，且首词不是这两个词 | 出现「验证表单」「测试创建」类标题 |
| 2 | 按中文逗号切分后每个构件不超过 40 字，URL 与字段名等行内代码不计入字数 | 逐段计数（剔除行内代码）后均 ≤40 字 | 出现 >40 字构件 |
| 3 | 每一步只含一个决策点，不出现「输入 A 并点击 B」式多动作 | 每步只有一个动作或一次状态改变 | 出现一步两动作 |
| 4 | 同一动作全文用同一动词，同一控件全文用界面原文 | 动词一致（输入/选择/点击），控件名保留 `Version`、`Endpoint URL` 等原文 | 混用「填写/输入」「选中/选择」，或翻译控件名 |
| 5 | 若设有关键检查点，每项标注所依赖的步骤号并就近写；未设检查点时业务结果须完整可判定 | 有检查点则带步骤号且就近；无检查点则业务结果逐条可判定 | 检查点堆在文末且无步骤号，或无检查点且业务结果不可判定 |

> #32 第 4 条同类复合断言也已同步拆分（长句 / 单决策点），完整评测时按同一口径判定。其余 task 的 checks 本身已写成可判定句，按 §1 通用原则判定；如需逐条 rubric 可按上表格式扩展。

## 3. `--results` 字段契约（来自 `scripts/skill-evals.py` 的 `read_results`）

| 字段 | 约束 |
|---|---|
| `skill` / `id` / `kind` | 必须与冻结套件的键一致；`kind` 为 `task` 或 `trigger` |
| `variant` | `with_skill` / `baseline` / `old` / `new` / `no_skill` |
| `run` | 正整数，同一 `(skill,id,kind,variant,run)` 不得重复 |
| `duration_seconds` | ≥0 且有限；完整评测应由 runner 记录真实耗时 |
| `output_characters` | 必须等于产物文件 UTF-8 字符数 |
| `output_path` | 绝对路径，或相对 `runs.jsonl` 所在目录 |
| `output_sha256` | 必须等于产物文件 SHA256（省略则由脚本代算） |
| `check_results` | 仅 task；布尔数组，长度必须等于该 case 的 checks 条数 |
| `predicted_trigger` | 仅 trigger；布尔值 |

产物文件不存在、字符数或哈希不匹配时该行标 `artifact_verified = false`，不进入统计。

## 4. 完整 Tier 2 / Tier 3 执行清单

**规模估算**：

| 组合 | 生成次数 |
|---|---|
| 42 task × 3 次重复（单 variant） | 126 |
| 12 trigger × 3 次重复（单 variant） | 36 |
| 三 variant 对照（with_skill / old / no_skill） | task 378 + trigger 108 |
| judge 判定量（单 variant，219 checks × 3 次） | 657 |

**步骤**：

1. 冻结用例：`python scripts/skill-evals.py --skill test-case-engineer --json > eval-cases.json`，记录 SHA256
2. runner 按 variant 分组执行：`with_skill` 组加载 skill 指令，`no_skill` 组只读任务材料；记录真实 `duration_seconds`
3. 每个 case 落盘一份产物，记录 `output_characters` 与 `output_sha256`
4. judge 按 §1/§2 逐条判定，产出 `check_results` 布尔数组
5. 汇总：`python scripts/skill-evals.py --skill test-case-engineer --results runs.jsonl --expected-runs 3 --expected-trigger-runs 3 --variants with_skill old no_skill`
6. 只有 `status = evaluated` 且无 `invalid_runs` / `unpaired_runs` 才能发布结论；`partial` 时不得下结论

**外部依赖**：

- 能批量调用模型的 runner 执行器（**当前仓库无**，本阶段只验证工具链）
- 与 runner 不同模型的独立 judge，或人工盲评并标注「未盲评」
- 产物存储、运行日志与计费/配额确认（三 variant 约 486 次调用）
- 若沿用 2026-09-15 的 9 任务 × 3 次口径，注意其 81/81 零区分度问题，须用 #33–#40 这类能区分好坏的任务

## 5. 已知边界

- pilot 仅覆盖 3/42 task、1 次重复、单 variant，**不能代表整体**
- 无 baseline / no_skill 对照时，不能判断「有 skill 是否更好」
- judge 与 runner 若同源或同模型家族，须标注「未满足严格独立性」，结果不可作 keep/revert 依据
- 历史 `runs.jsonl` 与当前套件不兼容，跨版本分数不可比
