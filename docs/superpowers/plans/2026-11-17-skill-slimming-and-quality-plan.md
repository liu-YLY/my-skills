# Skill 瘦身与生成质量提升计划

> **状态**：计划稿，待确认 §0 决策后执行
> **基线**：`main` @ `848b613`（2026-11-17）
> **范围**：`plugins/testing` 下 9 个 skill（含 testing-bundle）为第一优先级；wechat-formatter 暂不纳入
> **目标**：在不损伤既有能力的前提下，降低默认路径上下文成本，并提升测试用例、测试点、需求评审三类产物的生成质量
> **方法参考**：[维护3.3万字符的长 Prompt？让优化 Agent 迭代执行 Agent](https://mp.weixin.qq.com/s/pMQFjkllDxcqSJhh_aZjZQ)（harness²：INV/DOM 分路提案 → Probe → Compose → 经验沉淀）

---

## 0. 需要先拍板的决策

| 编号 | 决策 | 选项 | 推荐 |
|---|---|---|---|
| D1 | 首批范围 | ① test-case-engineer + testing-bundle ② ① + state-machine + change-impact ③ 全部 9 个 skill | **②**：先做高频、上下文最重的 4 个；其余 skill 在阶段 5 按同一协议跟进 |
| D2 | 需求评审形态 | ① test-case-engineer 新增「需求评审模式」② 新建独立 requirement-reviewer skill ③ 仅做独立 agent | **① + 可选 agent**：模式负责产出，独立 agent 负责复核；不新增 skill，避免扩大路由面 |
| D3 | 瘦身幅度 | ① 保守 -15% ② 标准 -25% ③ 激进 -35% | **②**：优先做重复规则合并与按需加载，不靠删规则凑数；单 skill 允许在 -20%～-30% 区间浮动 |
| D4 | 评测执行方式 | ① 仅确定性校验 ② 独立 judge + 3 次重复 ③ 先小规模方向性验证，再铺开 | **③ → ②**：先 3 case × 2 variant 验证口径，再跑全量；无独立 judge 时结论只标 `partial`，不得用于采纳决策 |
| D5 | 发布方式 | ① 单 PR ② 堆叠 PR（每个 ≤400 行） | **②**：评测/工具、瘦身、需求评审、质量迭代分 PR，便于逐段 review 与回滚 |
| D6 | 是否新增 bundle 链 10（需求评审 → 用例生成） | ① 新增 ② 不新增，仅单意图路由 | **①**：与现有链 6/7 的「评审后消费」模式一致；若路由评测无收益则回退 |

> 以上决策在执行前确认；未确认项按推荐值执行，并在阶段 0 记录。

---

## 1. 现状与基线（已实测）

### 1.1 上下文体积

统计口径：当前工作区 Markdown 字符数（UTF-8 字符，非字节）；默认路径 = SKILL.md + 该模式下「必读」的 core/knowledge 文件。token 需在阶段 1 用 tiktoken 重测，本计划暂以字符数作为预算单位。

| Skill / 模式 | 默认路径字符 | 文件数 | 目录内全部 Markdown 字符 | 入口 SKILL.md 字符 |
|---|---:|---:|---:|---:|
| test-case-engineer / 默认生成 | 64,028 | 11 | 124,199（24 个） | 7,391 |
| test-case-engineer / 评审（含 J rubric） | 33,545 | 5 | 同上 | 7,391 |
| state-machine-test-engineer / 默认 | 44,340 | 6 | 104,084（17 个） | 7,081 |
| change-impact-analyzer / 默认 | 38,829 | 6 | 49,175（8 个） | 6,151 |
| testing-bundle / 路由 | 17,190 | 3 | 32,144（6 个） | 7,486 |
| test-strategy-engineer / 默认 | 17,765 | 5 | 24,129（7 个） | 6,200 |
| bug-analyzer / 默认 | 20,074 | 5 | 24,536（7 个） | 6,955 |
| performance-test-engineer / 默认 | 15,760 | 4 | 23,700（7 个） | 4,170 |
| frontend-test-preparation / 默认 | 6,903 | 3 | 6,903（3 个） | 4,689 |
| test-data-generator / 默认 | 12,339 | 6 | 12,339（6 个） | 2,559 |

### 1.2 评测与校验能力

| 项 | 现状 | 缺口 |
|---|---|---|
| 冻结质量套件 | `docs/skill-evaluation/2026-11-03-test-case-quality-cases-v6.json`：54 case / 219 checks（42 task + 12 trigger） | 仅覆盖 test-case-engineer；task 缺 category；部分 check 仍是「输出包含 XX」存在性断言 |
| 对照评测 | Tier 2/3 N=40 配对盲评；v6 修复缺料后 with_skill 82.6% vs no_skill 47.5% | 1 次重复、缺 old 对照、judge 未换族，`status=partial`，只能作方向性观察 |
| 触发评测 | 12 条 trigger，四类齐全 | 仅 test-case-engineer；其余 skill 的 trigger 未纳入统一口径 |
| 确定性校验 | 6 个仓库脚本 + 2 个 MCP（101 / 68 项测试） | 没有上下文预算门禁；没有测试点、需求评审的独立校验器 |
| 已知口径冲突 | `#13` 评级阈值、`#7/#19` 抽样标注与 skill 规则不一致 | 需在阶段 1 建立「断言-规则一致性」检查 |
| 历史教训 | 2026-09-15 对照 81/81 零区分度；多次「结构分上涨但效果未提升」 | 新用例必须能区分好坏，且不得用结构分替代效果结论 |

### 1.3 结论

1. **上下文成本集中在 test-case-engineer / state-machine / change-impact 三个 skill**，合计默认路径约 147k 字符；只做「删示例」已不足以继续下降，必须处理规则重复与按需加载。
2. **质量评测目前只对 test-case-engineer 形成闭环**，测试点、需求评审没有可判定的 ground truth，无法回答「是否变好」。
3. **瘦身与提质必须同时做**：没有评测保护的瘦身会删掉历史上修复缺陷的规则；没有瘦身的提质会继续推高默认路径成本。

---

## 2. 目标与验收

### 2.1 瘦身目标

| 对象 | 当前 | 目标 | 降幅 |
|---|---:|---:|---:|
| test-case-engineer 默认生成路径 | 64,028 | ≤44,800 | ≥30% |
| test-case-engineer 评审路径 | 33,545 | ≤25,200 | ≥25% |
| state-machine-test-engineer 默认路径 | 44,340 | ≤33,300 | ≥25% |
| change-impact-analyzer 默认路径 | 38,829 | ≤31,000 | ≥20% |
| testing-bundle 路由路径 | 17,190 | ≤13,750 | ≥20% |
| strategy / bug / performance 默认路径 | 17,765 / 20,074 / 15,760 | 各 ≤15,000 | 15%～25% |
| 单个 SKILL.md 入口 | 4,170～7,486 | ≤5,500 且 ≤120 行 | — |
| testing 目录 Markdown 总量 | 约 401k | ≤320k | ≥20% |
| 新增需求评审知识文件 | 0 | ≤5,000 | 由 prompt-strategy 移出默认路径抵消 |

> 预算按「默认路径」而非「目录总量」优先；行业模板、示例、报告模板属于按需资源，不计入首轮负担，但需去重与标注读取时机。

### 2.2 质量目标

| 产物 | 主指标 | 护栏指标 | 判定方式 |
|---|---|---|---|
| 测试用例 | 结果型 check 通过率 ≥90%，或较干净基线 +8pp | 格式/契约 error = 0；需求追溯 100%；等价重复 ≤2%；标题可独立定位 ≥95% | 冻结套件 + 独立 judge + 确定性校验 |
| 测试点 | 种子需求覆盖召回 ≥90% | 单点单目标 ≥95%；追溯 100%；预算内；裁剪理由完整 | 种子需求 + judge + `validate_points.py` |
| 需求评审 | P0/P1 种子缺陷召回 ≥85% | 误报率 ≤25%；证据完整率 100%（位置+原文+影响+问题）；severity 准确 ≥85% | 种子缺陷 PRD + 确定性校验 + judge |
| 触发路由 | precision ≥90%，recall ≥90% | near_miss 不误触发；skill_conflict 正确分流 | 12+ 条 trigger 套件 |
| 效率 | 默认路径字符 -25%～30% | 单任务总 input token 不增加 >10%；产物长度不膨胀 >20% | 上下文报告 + runner usage |

> 质量结论的发布门槛沿用 [methodology.md](../../skill-evaluation/methodology.md) v1.5：3 次重复、独立 judge、A/A 一致率 ≥70%、`status=evaluated`、无 `invalid_runs`；否则只能写「方向性观察」。

### 2.3 非目标

- 不重写 skill 结构，不引入新框架，不改变 MCP 协议契约。
- 不为「整洁」删除历史上修复过缺陷的规则。
- 不把「结构分/字数下降」当作质量提升。
- 不把评测集样本原文写进 skill 知识库。
- 不在 `main` 上直接提交；不跳过仓库校验脚本。
- 不在本轮处理 wechat-formatter。

---

## 3. 方法论：把文章映射到本仓库

### 3.1 harness 组件映射

| 文章概念 | 本仓库对应物 |
|---|---|
| 3.3 万字符长 Prompt | test-case-engineer 默认路径 64k 字符（core + 9 个默认读取知识文件） |
| 执行 agent | 加载 SKILL.md / core / knowledge / scripts / MCP 的测试 skill runtime |
| 优化 agent | 维护 agent + 冻结评测套件 + 确定性校验器 |
| harness 8 个可编辑组件 | SKILL.md 入口、core 流程、knowledge 知识、scripts、MCP、路由规则、输出契约、示例 |
| INV（怎么工作） | 模式路由、阶段流转、输出格式、字段契约、检查点、规则优先级、措辞与位置 |
| DOM（需要知道什么） | 缺陷模式、业务规则与例外、判例、行业模板、需求评审检查项 |
| base / inv1 / dom1 / agg1 | 同一套件的基线 / 工作流候选 / 领域知识候选 / 合成候选 |
| 人工标注 | 冻结套件的 checks + 种子缺陷 ground truth |
| 分歧样本 | 逐 case、逐 check 的失败产物 + 模型判断依据 + 失败聚类 |
| 经验库 | `docs/skill-evaluation/experience-library.md`（只沉淀有执行证据、可迁移的经验） |
| 采纳阈值 | 主指标提升 ≥5pp 且护栏不退化 >2pp，否则保留基线 |

### 3.2 单轮优化协议（k=1）

```text
base 执行
  → 失败聚类（按 check / 产物类型 / 根因）
  → INV 提案（只改工作流与输出契约）
  → DOM 提案（只改领域知识与判例）
  → 两路分别全量 Probe（同模型、同参数、同套件）
  → Compose（按证据合并，冲突按优先级裁决）
  → 全量执行 agg
  → 按主指标 + 护栏决定采纳/保留
  → 写入经验库
```

**改动边界（硬约束）**：

- INV 只允许改：`SKILL.md` 路由与模式段、`test-case-engineer-core.md` 阶段流转、`review-mode.md` 工作流段、输出模板、字段契约、检查点。
- DOM 只允许改：`knowledge/bug-patterns.md`、`knowledge/requirement-review.md`、`knowledge/test-standards.md` 的业务判定部分、行业模板、判例与例外。
- 两路共同禁止改：`scripts/`、MCP 契约、安全与授权约束、评测集、版本元数据、README/CHANGELOG。
- 两路互相不可见；Compose 才允许同时看两份 diff。
- 冲突裁决顺序：安全/授权 > 输出契约 > 业务规则 > 风格与措辞。

### 3.3 ground truth 与防过拟合

- 需求评审使用**种子缺陷 PRD**：每个 PRD 预埋 5～8 个已知问题（模糊/矛盾/缺失/不可测/权限/状态/非功能），召回与误报可计算，这是比 judge 更硬的信号。
- 测试用例沿用冻结 checks，但把「输出包含阶段 X」改为「产物中可观察的结果」；judge 只读产物与 checks，不读 skill。
- 测试点使用「需求条目 → 应覆盖测试点」的种子映射，判覆盖率而非文本相似度。
- 保留 20% case 作为 holdout，优化 agent 不可见，只用于最终验证。
- 机械扫描新知识内容与评测样本的 n-gram 重合；新增示例不得与评测样本相同。
- 保留起始版本中的既有示例，不允许优化 agent 删改。

---

## 4. 阶段与停止点

```text
阶段 0  决策确认 + 分支准备
   ↓ 🔴 停止点 0
阶段 1  度量工具 + 规则清单 + 评测套件扩容 + 干净基线
   ↓ 🔴 停止点 1：确认基线、套件 SHA、失败聚类
阶段 2  瘦身第一批（test-case-engineer + testing-bundle）
   ↓ 🔴 停止点 2：确认预算达成且质量无回退
阶段 3  需求评审模式 + 测试点校验器 + 对应评测套件
   ↓ 🔴 停止点 3：确认样例、误报率与体积预算
阶段 4  harness² 第一轮（INV / DOM / Compose）
   ↓ 🔴 停止点 4：确认采纳/保留决策
阶段 5  瘦身第二批（state-machine / change-impact / 其余）
   ↓ 🔴 停止点 5：确认第二批质量与预算
阶段 6  版本同步、CI 门禁、文档、PR 发布
   ↓ 🔴 停止点 6：发布确认
```

> 每阶段结束输出「改动清单 + 校验结果 + 预算对比 + 质量对比 + 下一阶段建议」；不自动跨阶段。

---

## 5. 任务清单

### 阶段 0：决策与准备

| ID | 动作 | 验收 |
|---|---|---|
| 0-1 | 确认 D1–D6；未确认项记录为默认值 | 本文 §0 填写结果 |
| 0-2 | 按 [git-workflow.md](../../../.trae/rules/git-workflow.md) 从最新 `main` 建 `feat/skill-slimming-quality-v1` | `git status` 干净，分支基于最新 main |
| 0-3 | 冻结当前版本号、套件 SHA、6 个脚本结果 | 基线快照写入阶段 1 报告 |

### 阶段 1：度量、规则清单与评测扩容

| ID | 动作 | 主要文件 | 验收 | 预算 |
|---|---|---|---|---:|
| 1-1 | 新建上下文报告脚本：按 skill / 模式输出默认路径、按需文件、字符与 token | `scripts/skill-context-report.py` | 对 9 个 skill 输出稳定 JSON/Markdown | +150 行 |
| 1-2 | 新建预算门禁：每 skill / 模式配置预算，超限失败 | `scripts/check-context-budget.py` + `scripts/context-budget.json` | `python scripts/check-context-budget.py` 在当前基线通过 | +120 行 |
| 1-3 | 抽取规范语句清单：`必须/禁止/不得/应` 逐条编号，标注 D1–D5 处置类别 | 生成 `docs/skill-evaluation/rule-inventory/` 报告 | 4 个首批 skill 全覆盖；每条有处置类别 | 报告 |
| 1-4 | 评测套件 v7：补 category；把存在性断言改为结果断言；新增测试点 10 case、需求评审 12 case、高区分度用例评审 6 case | `docs/skill-evaluation/2026-11-17-quality-suite-v7.json` | 套件 SHA 冻结；`skill-evals.py` 输入校验通过 | 300～400 checks |
| 1-5 | 需求评审种子缺陷集：12 个 PRD，每个 5～8 个已知问题，附位置与严重级别 | `docs/skill-evaluation/2026-11-17-requirement-review-cases.json` | 每个缺陷可定位；召回/误报可计算 | 12 PRD |
| 1-6 | 测试点种子集：10 条需求，标注应覆盖测试点与裁剪项 | `docs/skill-evaluation/2026-11-17-test-point-cases.json` | 覆盖分母明确；预算与裁剪可判定 | 10 case |
| 1-7 | 干净基线：with_skill / no_skill × 3 次 + 独立 judge + A/A | `docs/skill-evaluation/reports/2026-11-17-quality-baseline.md` | `status=evaluated`；无 `invalid_runs`；记录有效样本数 | — |
| 1-8 | 断言-规则一致性扫描：逐条核对 checks 与 skill 规则 | 报告 | 列出全部冲突及建议；不擅自改断言 | — |

**阶段 1 验收**：6 个仓库脚本全绿；MCP 测试全绿；v7 套件 SHA 冻结；基线报告含主指标、护栏、有效样本数、失败聚类；预算门禁在当前版本通过。

### 阶段 2：瘦身第一批

**总原则**：先合并重复规则，再按需加载，最后压缩措辞；删改必须能映射到规则清单编号。

| ID | 对象 | 动作 | 预期字符变化 |
|---|---|---|---:|
| 2-1 | `knowledge/writing-rules.md`、`readability.md`、`test-standards.md`、`anti-patterns.md` | 建立「写作契约」单一权威源：字段/句式/术语/模糊词/反例各只保留一处；`readability.md` 降为按需细则；`anti-patterns.md` 压成黑名单表 | 25.6k → ≤13k |
| 2-2 | `knowledge/prompt-strategy.md` | 移出默认路径；SKILL.md 保留 5 行指针；仅保留「语义事实抽取」按需段 | 4.3k → ≤1k |
| 2-3 | `knowledge/test-levels.md`、`case-arrangement.md` | 合并为「用例组织」单一文件；删除重复的层级/占比表述 | 5.5k → ≤3.5k |
| 2-4 | `knowledge/bug-patterns.md` | 保留映射表与高频模式；领域长清单改为按需 | 5.4k → ≤3.5k |
| 2-5 | `test-case-engineer-core.md` | 删除与 knowledge 重复的清单/表格；保留四阶段流转、闸门、失败模式；阶段 2/3/4 只留判定问句 | 13.9k → ≤9.5k |
| 2-6 | `SKILL.md` | 入口只留定位、模式选择、读取矩阵、硬门禁；重复的协同/产品知识说明压缩 | 7.4k → ≤5.5k |
| 2-7 | `knowledge/review-mode.md` | 拆为「评审工作流（R1–R3）」+「模板与规模化/增量按需」；模板移出首轮 | 13.6k → ≤9k（评审路径） |
| 2-8 | `knowledge/project-knowledge.md` | 压缩加载步骤，保留证据与授权边界 | 2.1k → ≤1.2k |
| 2-9 | `testing-bundle` | 压缩 `mixed-intent-chains.md` 的重复示例；`routing-fallbacks.md` 去重；SKILL 只留判定顺序与转交契约 | 17.2k → ≤13.5k |

**阶段 2 验收**：

- 默认路径 ≤44.8k；评审路径 ≤25.2k；bundle ≤13.75k。
- `python scripts/check-context-budget.py` 通过。
- 6 个仓库脚本 + MCP 测试全绿。
- `validate_cases.py` 在固定 10 份历史产物上 0 error。
- v7 质量套件主指标较基线回退 ≤2pp；格式 error = 0。
- 每个任务一个 commit；单 PR ≤400 行。

### 阶段 3：需求评审模式与测试点校验

| ID | 动作 | 主要文件 | 验收 | 预算 |
|---|---|---|---|---:|
| 3-1 | 新增需求评审知识：10 维度检查项、P0–P3 严重级别、问题 schema、报告模板 | `test-case-engineer/knowledge/requirement-review.md` | 每个维度有判定问句；每个问题含位置/原文/类型/影响/问题 | ≤5k 字符 |
| 3-2 | SKILL.md 新增「需求评审模式」；core 阶段 1 改为消费评审问题清单，避免重复产出 | `SKILL.md`、`test-case-engineer-core.md` | 模式读取矩阵新增一行；不读四阶段生成流程 | +15 行，靠 2-5/2-6 抵消 |
| 3-3 | bundle 单意图路由「评审 PRD / 需求文档」→ test-case-engineer 需求评审模式；按 D6 决定是否加链 10 | `testing-bundle/SKILL.md`、`mixed-intent-chains.md` | 路由评测 near_miss 不误触发；链 10 有依赖顺序 | +10 行 |
| 3-4 | 新建需求评审校验器：schema、证据完整、摘要一致、原文引用可回查 | `test-case-engineer/scripts/validate_requirement_review.py` | 对 gold 样例 0 error；缺证据必报 | +200 行 |
| 3-5 | 新建测试点校验器：单点单目标、重复、追溯、优先级、裁剪说明 | `test-case-engineer/scripts/validate_points.py` | 对 gold 样例 0 error；能检出 5 类种子缺陷 | +180 行 |
| 3-6 | 用 5 个 PRD 干跑：检查报告可读性、误报、字段完整性 | 报告 | 误报 ≤25%；证据完整率 100%；无「猜测式问题」 | — |

**阶段 3 验收**：需求评审样例可交付；两个新校验器接入阶段闸门；默认路径仍在预算内；v7 套件新增 case 的基线已记录。

### 阶段 4：harness² 第一轮

| ID | 动作 | 产出 | 验收 |
|---|---|---|---|
| 4-1 | base 全量执行；按 check 与产物聚类失败 | 失败聚类报告 | 每类有 3 条以上证据；区分格式/规则冲突/覆盖/可读性 |
| 4-2 | INV 提案：只改工作流与输出契约 | `inv1` diff | 改动范围校验通过；不触碰 DOM 与脚本 |
| 4-3 | DOM 提案：只改领域知识与判例 | `dom1` diff | 不触碰 INV 与脚本 |
| 4-4 | 两路分别全量 Probe | inv1 / dom1 产物与指标 | 同模型、同参数、同套件；记录有效样本数 |
| 4-5 | Compose：按证据合并，冲突按优先级裁决 | `agg1` | 每项合并有对应证据；冲突有裁决记录 |
| 4-6 | 采纳决策 + 经验沉淀 | 报告 + `experience-library.md` | 主指标 +≥5pp 且护栏不退化 >2pp 才采纳；否则保留 base |

**阶段 4 验收**：报告含 base/inv1/dom1/agg1 四列指标、护栏、有效样本数、采纳结论；经验库至少 3 条有证据、可迁移的条目；未达门槛的改动已回退。

### 阶段 5：瘦身第二批与其余 skill

| ID | 对象 | 动作 | 预算 |
|---|---|---|---:|
| 5-1 | state-machine-test-engineer | 压缩 `scenario-types.md`、`completeness-check.md`、`anti-patterns.md`、core、SKILL；行业模板保留但标注按需 | 44.3k → ≤33.3k |
| 5-2 | change-impact-analyzer | 合并 `cross-impact-analysis.md` 与 `cross-analysis-guide.md`；报告模板按需；反模式压缩 | 38.8k → ≤31k |
| 5-3 | test-strategy-engineer | 压缩 SKILL 与 `strategy-templates.md`；风险矩阵保留判定问句 | ≤15k |
| 5-4 | bug-analyzer | 压缩报告模板与防御性测试点；`bug-patterns` 跨 skill 引用改为可选降级说明 | ≤15k |
| 5-5 | performance-test-engineer | 压缩指标框架与瓶颈模式；保留 USE 判定链 | ≤15k |
| 5-6 | frontend / test-data-generator | 仅去重与入口压缩；不改变脚本与安全约束 | ≤10k |
| 5-7 | 其余 skill 的质量评测 | 有种子集的加种子回归；无种子集的用确定性校验 + 小规模方向性对照 | 报告 |

**阶段 5 验收**：预算全部达成；每个 skill 的验证脚本全绿；无「只删不测」的改动；阶段 4 经验库按需复用而非自动继承。

### 阶段 6：发布

| ID | 动作 | 验收 |
|---|---|---|
| 6-1 | 版本同步：按语义化版本升 skill / bundle / plugin / marketplace | `python scripts/check-version-sync.py` 通过 |
| 6-2 | 文档同步：SKILL、README、根 README、`docs/skills-overview.md`、CHANGELOG | `check-md-links.py`、`check-project-inventory.py --write` 通过 |
| 6-3 | CI 门禁：上下文预算脚本接入；评测 smoke 保持手动（需模型调用） | CI 全绿；预算门禁可失败 |
| 6-4 | PR 拆分与交付报告 | 每个 PR ≤400 行；报告含预算、质量、有效样本数、未评估项 |
| 6-5 | 合并后清理分支与发布标签 | 远程分支删除；tag 按 SemVer |

---

## 6. 评测执行协议

### 6.1 角色与独立性

| 角色 | 谁 | 读什么 | 禁止 |
|---|---|---|---|
| runner | 当前 runtime | skill 指令 + 需求原文 | 不读 checks、rubric、历史产物 |
| judge | 不同厂商模型或人工盲评 | 产物 + checks + 判定口径 | 不读 skill 指令；不知道 variant |
| 汇总 | `scripts/skill-evals.py --results` | `runs.jsonl` | 不使用 `dry_run` 支撑提升结论 |

### 6.2 执行步骤

1. 冻结套件：记录 SHA256、case 数、checks 数。
2. 跑 A/A：同 variant 重复两次，一致率 <70% 时停止判定，先修口径。
3. 跑 with_skill / no_skill（必要时加 old）：每条 3 次；产物落盘并记录 `output_sha256`。
4. judge 逐条判定：每条 check 给 `true/false` + 证据位置；复合条件全满足才 true。
5. 汇总：要求 `status=evaluated`、无 `invalid_runs/unpaired_runs`；报告有效样本数。
6. 分层报告：按 deliverable / category / 难度分层；整体通过率不得掩盖局部回退。

### 6.3 采纳规则

| 条件 | 结论 |
|---|---|
| 主指标 +≥5pp，护栏无 >2pp 回退，`status=evaluated` | 采纳 |
| 主指标提升但护栏回退 >2pp | 不采纳，先修护栏 |
| 主指标持平但上下文显著下降 | 可采纳瘦身，但不得宣称质量提升 |
| `status=partial` / judge 同族 / 单次重复 | 仅记录方向性观察，不采纳 |
| 有效样本数不足或格式丢弃率上升 | 不采纳，先修格式与执行链路 |

### 6.4 防过拟合检查

- holdout 20% case 不进入优化会话。
- 新旧知识内容与评测样本做 8-gram 重合扫描，命中即拒绝。
- 起始示例保护：不允许删改既有示例；新增示例不得与评测样本完全一致。
- 评测集变更必须冻结新 SHA，并声明跨版本分数不可比。

---

## 7. 风险与对策

| 风险 | 信号 | 对策 |
|---|---|---|
| 瘦身删掉历史修复规则 | 某类 check 回退、失败聚类集中在已删条款 | 规则清单映射；D5 规则不删只移位；每批小步 + 配对评测 |
| 评测过拟合 | 套件分数上升，holdout 不升 | holdout + 泄漏扫描 + 新 case 不进入优化会话 |
| judge 偏差 | A/A 一致率低、判定理由空泛 | 换族 judge、盲评、逐条证据、A/A 前置 |
| 需求评审误报高 | 报告出现无原文依据的问题 | `validate_requirement_review.py` 强制位置+原文；误报率纳入护栏 |
| 体积反弹 | 新增模式后超预算 | 先删后加；预算门禁；新文件必须抵消 |
| 版本/文档不同步 | `check-version-sync.py` 失败 | 阶段 6 统一同步；PR 检查清单 |
| 范围蔓延到 9 个 skill | 阶段 5 过长、验证不足 | 首批 4 个；其余按同一协议分批，未验证不发布 |
| 评测成本高 | 调用次数多、无法完成 | 先用 3 case 方向性验证；全量前确认 judge 与配额；结果标 `partial` |

---

## 8. 不可违反的约束

1. 安全、授权、证据边界、失败语义条文不得删改；只允许移动并保留链接。
2. 不改变 MCP 工具契约与脚本输出格式；确需变更时单独立项。
3. 不把评测集、checks、rubric、种子缺陷写入 skill 知识文件。
4. 不为了「整洁」重写文件；所有删改必须映射到规则清单编号。
5. 没有独立评测证据，不得在 CHANGELOG、README 或交付报告中写「质量提升」。
6. 每批改动一个 commit，单 PR ≤400 行；不直接提交 `main`。
7. 每次阶段结束必须回到 6 个仓库脚本全绿 + MCP 测试全绿。

---

## 9. 完成定义（Definition of Done）

- [ ] 4 个首批 skill 的默认路径达到预算；总体 Markdown 体积下降 ≥20%。
- [ ] v7 套件冻结，覆盖测试用例、测试点、需求评审三类产物，checks 均为结果型或证据型。
- [ ] 干净基线报告完成：3 次重复、独立 judge、A/A 一致率 ≥70%、`status=evaluated`。
- [ ] 需求评审模式可独立交付，种子缺陷 P0/P1 召回 ≥85%、误报 ≤25%。
- [ ] 测试点校验器与需求评审校验器接入阶段闸门，gold 样例 0 error。
- [ ] 第一轮 INV/DOM 完成，采纳决策有证据，经验库有可迁移条目。
- [ ] 6 个仓库脚本 + 2 个 MCP 测试全绿；上下文预算门禁生效。
- [ ] 版本、README、CHANGELOG、plugin manifest、marketplace 同步。
- [ ] PR 拆分合并完成，交付报告如实列出未评估项与 `partial` 结论。

---

## 附录 A：首批瘦身候选清单（按收益排序）

| 优先级 | 文件 | 现状 | 处置 |
|---|---|---|---|
| P0 | `test-case-engineer-core.md` | 13.9k 字符，含与 knowledge 重复的清单 | 保留四阶段与闸门；清单改为判定问句 |
| P0 | `writing-rules.md` + `readability.md` + `test-standards.md` + `anti-patterns.md` | 合计 20.6k，规则多源 | 合并为单一写作契约；细则按需 |
| P0 | `prompt-strategy.md` | 4.3k，属提示词工程元内容 | 移出默认路径，仅留语义抽取 |
| P1 | `review-mode.md` | 13.6k，工作流与模板混载 | 工作流首轮；模板/规模化按需 |
| P1 | `test-levels.md` + `case-arrangement.md` | 5.5k，层级与编排分散 | 合并为用例组织 |
| P1 | `bug-patterns.md` | 5.4k，领域清单较长 | 保留映射表与高频模式 |
| P2 | `project-knowledge.md` | 2.1k | 压缩加载步骤 |
| P2 | `testing-bundle/SKILL.md` + `mixed-intent-chains.md` + `routing-fallbacks.md` | 17.2k | 去重示例；保留路由判定与转交契约 |

## 附录 B：需求评审问题 schema（建议）

```json
{
  "issue_id": "REQ-001",
  "location": "PRD §3.2 / req.md:L42",
  "quote": "原文片段，必须可在原文中回查",
  "type": "模糊|矛盾|缺失|不可测|权限|状态|数据|非功能|依赖|可行性",
  "severity": "P0|P1|P2|P3",
  "impact": "影响的测试点/用例/发布决策",
  "question": "向产品/需求方提出的具体问题",
  "suggestion": "建议的修订方向",
  "status": "已确认|待确认"
}
```

## 附录 C：harness² 单轮记录模板

```text
轮次：R1
基线版本：vX.Y.Z
套件 SHA：...
base：主指标 X%，护栏 A/B/C，有效样本 N
inv1：主指标 X%，护栏 A/B/C，diff 摘要
dom1：主指标 X%，护栏 A/B/C，diff 摘要
agg1：主指标 X%，护栏 A/B/C，合成决策
采纳：是/否
经验：问题 → 证据 → 改动 → 适用条件 → 结果
未评估项：...
```
