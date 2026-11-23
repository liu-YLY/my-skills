# `test-case-engineer` 去说教化、跨模型防漂移与结构性深瘦身实施计划

> **生成日期**：2026-11-23
> **工作分支**：`feat/test-case-depreach-v9.16`（基于 `origin/main` 最新提交创建）
> **关联参考**：本地会话沉淀《测试用例去说教化、真实可测与跨模型质量规范》（2026-11-23）、[2026-11-17-skill-slimming-quality-handoff.md](2026-11-17-skill-slimming-quality-handoff.md)
> **涉及范围**：`plugins/testing/skills/test-case-engineer`（v9.15.0 → v9.16.0）、`plugins/testing/mcp-servers/review-checker`（v0.4.0 → v0.4.1）、`scripts/context-budget.json` 及顶层版本同步文件
> **当前状态**：计划已沉淀；阶段 1（校验器与 MCP 引擎改造）与阶段 2（初版规则合入）已在工作区就绪，**待确认本计划后执行阶段 3（结构性深瘦身）与阶段 4（干净上下文真实场景生成验证）**

---

## 一、 背景与根因诊断

### 1.1 实战产物暴露的三大质量痛点
在对存量 AI 生成用例（173 条登录业务 YAML + 83 条计费通知 YAML）的人类可读性走查与对抗性复盘中，暴露出三类跨模型共性通病：
1. **人类可读性退化为「防作弊免责合同」**：充斥默认无干扰废话（`无其他阻断`、`服务可用`）、过程守规矩叮嘱（`期间不重发`、`不手工改库`）、取证动作下沉前置（`已记录原值`、`保存快照`、`技术协作者配合`）、反面免责与自辩备注（`不用…代替`、`另验`、`不计入通过率`）、业务结果机械冠以 `步骤 1～2：` 前缀，以及业务前置裸写底表列名（`pay_status=0, balance=200`）。
2. **完备性焦虑引发「不可测伪场景」**：无专属容错设计时脑补基础设施宕机/断网；为绕过限制凭空捏造环境未交付夹具（`隔离 stub 返回 503`、`推进可控服务端时钟`）；同一失败兜底分支按底层 HTTP `400/429/503` 机械裂变凑数；把「查配置、向负责人确认口径」写成测试用例。
3. **外置集中数据表破坏单条自包含**：将测试数据抽离为几百行的独立 `test-data.md`，在用例内用暗号（`使用夹具 M4`、`见数据表 S1`）跨文件拼图，或隐式依赖前序用例状态。

### 1.2 本仓库代码层面的两个深层根源
1. **自身规则左右互搏（反向诱导实锤）**：
   - `review-checker` MCP 的 `validators.py` 原逻辑规定：只要 `preconditions` 出现 `"数据库"`/`"特定用户"`/`"特定权限"`/`"第三方"` 且不含 `mock/stub/fixture`，即报 P2 问题并建议 `"提供 mock/stub 替代方案"`——直接逼迫 AI 在多轮评审后编造虚拟夹具。
   - `review-reference.md` 模板示例直接建议 `"新增异常场景用例：网络断开/超时/依赖服务不可用"`，与 `scope-discipline.md` 的「服务故障默认 0 条」正面冲突。
   - `validate_cases.py` 原本漏检了 `前置条件` 段落，且存在解析器缺陷（段落内含冒号的列表项如 `- 步骤 1～2：…` 会被误判为顶部 `meta` 吞掉）。
2. **上下文体积与指令过载（Instruction Overload）**：
   - 上一轮 `v3.7.0` 瘦身后，`test-case-engineer` 默认路径仍常驻 **9 个文件、`36,990` 字符（约 `23.9k` Tokens、179 条规范语句）**。
   - 上一轮阶段 4 Probe 实测（`phase4-probe-report.md`）已发出明确警示：在 `36.9k` 字基础上继续往 `core.md` 追加阻断叮嘱（`INV1`），导致用例生成通过率从 `79.17%` 跌至 `68.75%`（**-10.42pp**），且长 Prompt 在部分模型上高频超时；同时 `v3.7.0` 发布时模型侧实测停留在 `partial`。
   - **结论**：绝不能在 `37k` 字全家桶上继续“叠补丁”；必须坚持**「长尾词表与确定性检查下沉给 Python 脚本，非普适领域按需延迟加载，主路径砍掉 40% 冗余脂肪」**。

---

## 二、 已确认的架构与边界决策

| 编号 | 决策项 | 已确认方案 | 冲突化解说明 |
|---|---|---|---|
| **D1** | 改造范围 | **同步改造 `test-case-engineer` + `review-checker` MCP** | 根除评审闭环逼写虚拟 `mock/stub` 的反向诱导源头 |
| **D2** | 单条物理字数红线 | **除 `数据组：` 外，单条严格 `≤60 个汉字`、`最多含 1 个分号`（`error` 级）** | 脚本 `_measure_hanzi` 自动剔除反引号代码、URL、引号文案、英文标识符、数字与标点，只计纯汉字骨架，兼顾接口用例且精准拦截长句堆砌 |
| **D3** | 输出与校验格式 | **Skill 默认输出 Markdown 块；`validate_cases.py` 同步支持 `.yaml/.yml`** | 保持本 Skill 既有 Markdown 契约不分裂（保留 `关键检查点` 的 `步骤 N 后：`），同时支持直接扫描 `testing-tm-cases` 等外部 YAML 用例库 |
| **D4** | 数据自包含边界 | **禁建人工阅读的外置暗号表（`夹具 M4`/`见表 S1`）；与 `test-data-generator` 解耦** | 单条用例正文必须内联具体输入与可重建状态；需批量离线 JSON/CSV 文件时走链 8 `test-data-generator`，用例正文仍须可读自包含 |
| **D5** | 瘦身与验证策略 | **结构性深瘦身（默认路径压至 `≤22,000` 字）+ 3 个真实业务场景盲测验证** | 移出全领域大百科与重复反例表，收紧 `context-budget.json` 门禁，并用独立上下文 Subagent 做端到端生成实测 |

---

## 三、 量化目标与验收门槛

### 3.1 上下文体积瘦身目标（对比 `main` 基线）

| 路径 / 模式 | `main` 基线 | 本计划目标上限 | 预期降幅 | 结构调整说明 |
|---|---:|---:|---:|---|
| `test-case-engineer / entry` (`SKILL.md`) | `5,400` 字 | **`≤ 3,600` 字** | **≥ -33%** | 合并重复的知识库大表与模式读取矩阵 |
| `test-case-engineer / default`（默认生成） | `36,990` 字（9 文件） | **`≤ 22,000` 字（7 文件）** | **≥ -40%** | `bug-patterns` 与 `anti-patterns` 改为按需；主路径 5 文件深度去套话 |
| `test-case-engineer / review`（评审路径） | `20,063` 字 | **`≤ 18,500` 字** | **≥ -8%** | 受益于 `SKILL.md` 与 `test-standards.md` 压缩 |
| `test-case-engineer / requirement-review` | `9,560` 字 | **`≤ 7,800` 字** | **≥ -18%** | 解决原路径距 `9,600` 门禁仅余 40 字的紧绷风险 |

### 3.2 确定性工程门禁（100% 必过）
1. **仓库 6 大静态检查全绿**：`check-version-sync.py`、`check-skill-consistency.py`（含全部 `.md` 可达性与 6 模式一致性）、`check-md-links.py`、`check-knowledge-count.py`、`check-project-inventory.py`、`check-context-budget.py --target`（按收紧后的新目标值校验）。
2. **脚本与 MCP 单测全绿**：
   - `test_validate_cases.py`（覆盖说教词、虚构夹具、底表列名、行号前缀、60 汉字+单分号、`数据组：` 豁免、`关键检查点` 与 `审计日志已记录` 防误报、YAML 重构前后对照）；
   - `test_validate_points.py` & `test_validate_requirement_review.py`；
   - `review-checker` MCP 单元测试与 `scripts/tests/test_repository_tools.py`。

### 3.3 真实场景模型生成验证（解决上轮 `partial` 未实测问题）
使用**全新的独立上下文 Subagent**（仅读取瘦身后的 `test-case-engineer` 主路径文件与测试需求，隔离本对话历史），运行 **3 个典型高风险场景**并检验产物：

| 验证编号 | 测试场景特征 | 重点检验的旧通病 | 通过标准 |
|---|---|---|---|
| **V-01** | **邮箱激活流程 30 分钟过期 + 5 分钟重发码边界**（多时间阈值 + 前后端绕过校验） | 取证动作下沉（`已记录原值/快照`）、过程叮嘱（`期间不再重发`）、结果 `步骤 N：` 前缀、超 60 字长句 | `validate_points.py` & `validate_cases.py` **0 error**；说教黑名单 **0 命中**；30m/5m/错误码断言 100% 保留 |
| **V-02** | **待支付订单重复提交支付 + 第三方支付渠道调用**（幂等 + 外部依赖，PRD 未定义降级） | 脑补「支付服务宕机/断网/DB 失败」、捏造「隔离 stub 返回 503」、按 400/429/503 裂变、裸写 `pay_status=0` | 服务宕机/虚构 stub 用例 **0 条**（写入裁剪说明）；底表列名裸写 **0 处**；`validate_cases.py` **0 error** |
| **V-03** | **Webhook 创建与 URL/事件校验**（单功能多校验规则 + 非焦点旧列表展示） | 边界值膨胀（拆成十几个同构块）、非焦点展开多步、遗漏编排声明或预算失控 | 焦点三点边界 + 同构校验参数化/紧凑合表；非焦点仅 1 条冒烟；`validate_cases.py` **0 error** |

实测原始产物摘要与量化对比沉淀至 `docs/skill-evaluation/reports/2026-11-23-depreach-slim-verification.md`。

---

## 四、 分阶段执行步骤与文件落点

### 阶段 1：反向诱导清扫与确定性校验器升级（工作区已完成，待联调）
- [x] **1-1 `review-checker` MCP（v0.4.1）**：修改 `validators.py` 与 `test_validators.py`，废除强迫写 `mock/stub/fixture` 的旧规则，改为拦截生产不可重置数据与虚构夹具/外置暗号表，并在 `check_readability` 中增加说教噪音与行首 `步骤 N：` 检测。
- [x] **1-2 `validate_cases.py` 静态门禁升级**：新增 `PREACH_NOISE`、`FICTIONAL_FIXTURE`、`RAW_DB_COL`、`RESULT_STEP_PREFIX` 四条 `error` 规则；将 `前置条件` 纳入模糊词与句长检查；实施单条 `≤60` 汉字与 `<2` 个分号红线（`数据组：` 豁免）；修复 Markdown 列表项冒号误判 `meta` 的解析 bug；新增 `parse_yaml_cases` 支持 `.yaml/.yml` 用例校验；补充 21 项单测。

### 阶段 2：跨模型防漂移规则合入与入口整合（工作区已完成）
- [x] **2-1 植入核心规则与语感锚点**：在 `scope-discipline.md`、`writing-rules.md`、`writing-examples.md`、`review-mode.md`、`review-reference.md`、`review-rubric.md` 中合入淘汰门、句法槽位公式、单条自包含、删词脱水测试及 `TC_ORDER_PAY_002` 正反对照锚点（同时删除 `writing-examples.md` 中重叠的 2 组旧长例）。
- [x] **2-2 入口与低频契约解耦**：合并 `SKILL.md` 双表（`5,400 → ~3,200` 字）；将协同链专属 `traceability` 图对象与四层基线说明从 `writing-rules.md` 下沉至按需文件 `failure-semantics.md`。

### 阶段 3：主路径结构性深瘦身与门禁收紧（待执行）
- [ ] **3-1 按需化剥离 2 个非常驻文件**：
  - 将 `knowledge/bug-patterns.md`（`3,229` 字）移出默认必读，在 `test-case-engineer-core.md` 阶段 2 内联 4 行「功能特征 → 必查缺陷点」速查规则，仅在命中复杂领域（支付封顶/搜索通配/通知渲染/文件上传/公网安全 10 项）时按需读取完整文件（保持 `bug-patterns.md` 文件内容完整，确保 `bug-analyzer` 相对路径共享不受影响）。
  - 将 `knowledge/anti-patterns.md`（`2,553` 字）移出默认必读（D 类反例已由 `validate_cases.py` 100% 接管，改为阶段 4 排障按需读取）。
- [ ] **3-2 深度压缩默认路径 5 个核心文件（不删行为硬规则，只压模板边框、重复解释与管理废话）**：
  - `test-case-engineer-core.md`（`7,869 → ~5,200` 字）：压缩阶段 1/2 Markdown 占位框说明、产品知识重复叙述与 J 类清单重复项，保留全部阶段闸门与 6 模式定义。
  - `knowledge/writing-rules.md`（`6,900 → ~4,800` 字）：精简紧凑表格、Tag、拆分合并中的重复修饰句，突出槽位公式与物理红线。
  - `knowledge/scope-discipline.md`（`2,959 → ~1,900` 字）：合并重复的「描述深度分级表」（已在焦点三档表定义）与过渡段落。
  - `knowledge/case-arrangement.md`（`2,695 → ~1,750` 字）：合并五层定义表与 L1–L3 占比表为单张决策表，精简策略叙述，保留 `8/15/25` 软预算与非功能置尾硬规则。
  - `knowledge/test-standards.md`（`1,924 → ~1,150` 字）：移除对生成无作用的「用例生命周期（Draft→Obsolete）」章节，保留超长标题例外、P0–P3 三步法、8 类枚举与新功能覆盖基线。
- [ ] **3-3 锁死新预算与刷新仓库索引**：
  - 更新 `scripts/context-budget.json`：同步 `test-case-engineer.modes.default.files`（7 文件），将 `target` 从 `44,800` 下调锁死至 `23,000`、`entry.target` 下调至 `4,000`、`review.target` 下调至 `19,000`、`requirement-review.target` 下调至 `8,200`；
  - 运行 `python3 scripts/check-project-inventory.py --write` 同步根 `README.md` 行数统计，跑通全部 6 个仓库检查脚本与全部 pytest/unittest。

### 阶段 4：干净上下文真实生成盲测与报告沉淀（待执行）
- [ ] **4-1 执行 V-01 / V-02 / V-03 独立子代理生成测试**：分别派发 3 个无历史记忆的 Subagent 按新 Skill 走完需求理解 → 测试点提取 → 用例编写，并对生成结果实际运行 `validate_points.py` 与 `validate_cases.py`。
- [ ] **4-2 检查与微调闭环**：逐项核验说教词命中率、单条字数、是否出现虚构 Stub/无依据宕机、核心业务规则召回率；若有漏网项则定向修正规则或校验正则并复测，输出实测报告 `docs/skill-evaluation/reports/2026-11-23-depreach-slim-verification.md`。

### 阶段 5：合规拆分提交与 PR 交付（待执行）
遵循 `.trae/rules/git-workflow.md`（Conventional Commits 中文祈使句、不在 `main` 直接提交、控制单 PR 规模与职责原子性），建议按职责拆分为 **2～3 个清晰的原子提交 / Stacked PR**：
1. **`fix(review-checker)` + `feat(test-case-engineer)`（静态引擎层）**：`review-checker` v0.4.1 移除反向诱导 + `validate_cases.py` 去说教规则、解析修复与 YAML 支持及单测；
2. **`refactor(test-case-engineer)`（Skill 规范与深瘦身层）**：`test-case-engineer` v9.16.0 去说教规范合入、默认路径结构性深瘦身（`36,990 → ≤22,000` 字）、`context-budget.json` 收紧与版本文档同步；
3. **`docs(eval)`（计划与实测证据层）**：实施计划文档与 3 场景干净上下文实测验证报告。

---

## 五、 风险与回退预案

1. **瘦身误删关键规则风险**：只移出重复表与领域百科（改为特征触发按需读），保留 `extract-rule-inventory.py` 识别的核心行为约束；`bug-patterns.md` 原文件保留不动，确保 `bug-analyzer` 跨目录引用零影响。
2. **60 汉字红线误伤复杂接口用例风险**：`_measure_hanzi()` 已排除反引号代码、URL、引号内文案、英文参数名、数字与标点（60 个纯汉字约合混合原文 90～120 字符），并对 `数据组：` 行豁免；阶段 4 将通过 V-01～V-03 实测检验是否过严。
3. **版本与门禁漂移风险**：任何改动均以仓库 6 个检查脚本 + 120 项 pytest 全绿作为硬性准入条件。
