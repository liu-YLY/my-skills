---
name: testing-bundle
version: 3.5.0
description: >-
  Use when user has mixed, ambiguous, or explicitly routing-required testing requests —
  e.g. "analyze bug AND generate test cases", "design strategy AND generate layered cases",
  "performance test AND diagnose bottleneck", "review AND check coverage gaps",
  "write test cases AND prepare offline test data",
  or "not sure which testing capability is needed".
  For single-intent requests (test cases only, strategy only, performance only, bug analysis only,
  state-machine only, change-impact only, frontend navigation preparation only,
  offline test-data generation/validation only),
  the corresponding sub-skill handles directly without bundle routing.
  Triggers on: 混合测试意图、模糊测试请求、测试bundle、测试路由、不确定需要哪种测试能力.
  This is a bundle entry that routes to test-strategy-engineer, test-case-engineer,
  performance-test-engineer, bug-analyzer, state-machine-test-engineer,
  change-impact-analyzer, frontend-test-preparation, or test-data-generator.
keywords:
  - 测试bundle
  - 测试路由
  - 混合测试意图
  - 模糊测试请求
  - 测试能力选择
---

# Testing Bundle

测试能力 bundle 入口：统一路由到 8 个专业子 skill，覆盖项目级策略、用例、性能、缺陷根因、状态机、变更影响、前端测试准备与离线测试数据。子 skill 均可独立调用，随 testing plugin 整体安装获得。

## 适用范围

**适用**：混合测试意图、目标模糊或用户明确要求路由；单一意图直接使用对应专业 Skill。

**不适用**：非测试领域（文档撰写、代码风格、其他 skill 范畴）

## 路由规则

收到用户请求后，按以下判定顺序路由（**先解析意图三要素，再匹配混合链路，最后查单意图表**）：

1. **第一步**：提取对象、动作、交付物三要素（见下方「意图解析」），三要素不全或相互矛盾时先追问
2. **第二步**：扫描请求是否命中任一混合意图链关键词（见"混合意图链"章节）→ 命中则按对应链路执行
3. **第三步**：未命中混合意图链 → 查单意图路由决策表 → 路由到对应子 skill
4. **第四步**：单意图也未命中 → 追问用户（🔴 CHECKPOINT）

路由目标共 8 个。bundle 只判断和传递上下文，不在入口重复实现专业流程。

### 意图解析（先提取三要素，再匹配路由）

禁止只凭单个关键词直接调用子 skill。先提取以下三要素，再对照路由表：

| 要素 | 问法 | 常见取值 |
|------|------|---------|
| **对象** | 用户要对什么做功？ | 需求文档 / 已有用例 / 代码 diff / 线上故障 / 状态流转 / 前端页面与入口 / 数据文件 / 项目整体 |
| **动作** | 要做什么？ | 生成 / 评审 / 分析 / 定位 / 准备 / 校验 / 汇报 |
| **交付物** | 期望拿到什么？ | 用例集 / 测试策略 / 根因报告 / 影响范围 / 数据文件 / 导航索引 / 评审方案 |

解析规则：

1. **对象决定候选集**：需求 → 用例或策略；已有用例 → 评审；代码 diff → 影响分析；故障 → 根因；状态流转 → 状态机；前端页面与入口 → 前端准备；数据文件 → 数据生成或校验
2. **动作决定执行方式**：同一对象出现「生成 + 评审」等多个动作时按混合链处理，不压成一次调用
3. **交付物决定终点**：用户要「方案/汇报/评审会材料」而不是「用例明细」时，走评审方案子模式，不输出完整用例
4. **三要素缺失**：对象缺失 → 追问；动作缺失 → 按对象默认动作（需求默认生成、已有用例默认评审、diff 默认影响分析）；交付物缺失 → 按动作默认交付
5. **要素矛盾**：动作与交付物矛盾（如「生成测试策略」但交付物是「用例」）→ 🔴 CHECKPOINT 请用户确认

### 路由决策表（单意图）

> 仅列单意图路由。混合意图已在上文"判定顺序第二步"优先处理，不在此表。

| 用户意图关键词 | 路由到 | 说明 |
|---------------|--------|------|
| 测试策略、测试计划、测试分层、风险矩阵、准入准出、测试范围与优先级 **等项目级策略信号** | **test-strategy-engineer** | 项目级策略 |
| 测试用例、编写用例、生成用例、测试点、需求分析、用例评审、单功能测试策略 **等功能级用例信号**；评审方案、覆盖度汇报、评审会材料、用例太多评不完 **等评审组织信号** | **test-case-engineer** | 功能用例生成；评审模式含规模化评审与干系人评审方案子模式 |
| 前端代码准备测试、页面索引、前端导航索引、需求入口定位、测试账号与数据状态、更新页面索引 **等前端准备信号** | **frontend-test-preparation** | 建/更新前端导航索引，把需求映射到入口、角色、数据与检查点；不替代用例生成 |
| Bug分析、根因、缺陷定位、复现、5 Whys、鱼骨图、防御性用例反推 **等功能缺陷信号** | **bug-analyzer** | 功能缺陷根因 |
| 性能测试、负载测试、压力测试、并发测试、TPS、响应时间、瓶颈、性能瓶颈、容量评估 **等性能/资源层信号** | **performance-test-engineer** | 性能场景+瓶颈分析 |
| 状态机、状态流转、状态转换、生命周期、非法跳转、幂等、并发冲突、消息乱序、状态回退、幽灵状态、终态吸收 **等状态型需求信号** | **state-machine-test-engineer** | 状态机建模+场景穷举 |
| 变更影响分析、diff 分析、代码改动点、影响范围与测试内容、覆盖缺口、回归风险 **等变更影响信号** | **change-impact-analyzer** | 从改动生成范围与测试内容；旧用例可选，完整用例集另行协作 |
| 造测试数据、批量生成数据、生成关联数据、测试 CSV/JSON、按规则校验测试数据 **等离线数据交付信号** | **test-data-generator** | 从字段、规则或已有用例生成数据，或独立校验已有 JSON/JSONL/CSV；不执行系统测试 |
| 意图不明确 | **追问用户**（🔴 CHECKPOINT） | 列出 8 个子 skill 的能力让用户选择 |

给定代码改动并要求范围、优先级或测试内容时，按变更分析单意图路由；不因出现「测试内容」转为完整用例生成或项目级策略。用户另外明确要求正式用例集时，再基于变更分析产物协作。

仅说「测试前端功能」「测这个页面」属于用例生成信号，路由到 test-case-engineer；只有明确要求读前端代码、定位入口或维护页面索引时才路由到 frontend-test-preparation。

已有用例、场景或组合矩阵，只要求准备数据或检查文件时，直接路由到 test-data-generator；出现「用例」「订单状态」「并发」不自动触发用例生成、状态机建模或性能测试。只有明确要求新编/修订用例并准备数据时才触发链 8。写数据库、调用业务 API、执行压测由对应执行流程处理，离线造数授权不覆盖这些操作。

> "等X信号"判定边界：含上述任一关键词，或语义等价表达（如"测试计划"等价"测试策略"、"QPS"等价"吞吐量/TPS"）。边界模糊时按"判定顺序第四步"追问用户。

### 混合意图链

当用户请求同时涉及多个子 skill 时，按以下 9 条链路执行，转交时记录依据与未决事项；既有授权内的分析与离线文件生成连续执行。

**链路索引**（命中后读取对应链的完整步骤流）：

| 链 | 名称 | 涉及 skill | 触发信号 |
|---|---|---|---|
| 1 | 分析 Bug 并补充用例 | bug-analyzer → test-case-engineer | Bug 分析 + 用例生成 |
| 2 | 制定测试策略并生成分层用例 | test-strategy-engineer → test-case-engineer | 测试策略 + 用例生成 |
| 3 | 做性能测试并分析瓶颈 | performance-test-engineer（内部完成） | 性能测试 + 瓶颈定位 |
| 4 | 性能问题定位到代码缺陷 | performance-test-engineer → bug-analyzer | 性能瓶颈 + 代码缺陷信号 |
| 5 | 状态机建模 + 用例生成 | state-machine-test-engineer → test-case-engineer | 状态机 + 明确要求完整用例或步骤级落地；仅场景/测试点不触发 |
| 6 | 评审 → 覆盖缺口验证 | test-case-engineer → change-impact-analyzer | 用例评审 + 覆盖缺口/diff 分析 |
| 7 | 评审 → 风险用例根因反推 | test-case-engineer → bug-analyzer | 用例评审 + 根因反推 |
| 8 | 用例编写/修订 → 离线数据准备 | test-case-engineer → test-data-generator | 明确要求新编/修订用例 + 生成或校验对应数据；已有用例仅造数不触发 |
| 9 | 前端测试准备 → 用例编写 | frontend-test-preparation → test-case-engineer | 明确要求读前端代码、定位入口或维护页面索引 + 生成/修订用例 |

> **按需加载**：每条链的完整步骤流、CHECKPOINT 定义、触发条件与二级判定规则见 [knowledge/mixed-intent-chains.md](knowledge/mixed-intent-chains.md)。仅当判定顺序第二步命中某条链时，才读取该链的详细步骤流。

## 子 skill 加载规则

路由确定后才读取目标文件；混合链按顺序加载，禁止预先加载全部子 skill：

- [test-strategy-engineer](../test-strategy-engineer/SKILL.md)：项目级策略、分层、风险矩阵、准入准出。
- [test-case-engineer](../test-case-engineer/SKILL.md)：功能用例、测试点、用例评审（含规模化评审与干系人评审方案）；review-checker MCP 为可选增强。
- [frontend-test-preparation](../frontend-test-preparation/SKILL.md)：前端导航索引与单需求上下文映射；运行页面核实需浏览器工具、测试环境与当次授权，未具备时只交付代码分析与待确认项。
- [performance-test-engineer](../performance-test-engineer/SKILL.md)：性能方案与资源/架构层瓶颈。
- [bug-analyzer](../bug-analyzer/SKILL.md)：功能缺陷根因；缺少共享 bug-patterns 时按其自身规则降级。
- [state-machine-test-engineer](../state-machine-test-engineer/SKILL.md)：状态建模与场景穷举；state-machine-testing MCP v0.8.5 为可选增强。
- [change-impact-analyzer](../change-impact-analyzer/SKILL.md)：从代码变更生成影响范围与测试内容，用例和需求对照为可选增强。
- [test-data-generator](../test-data-generator/SKILL.md)：可重复离线造数与已有文件校验；规则来自项目资料，无需 MCP，不写数据库或调用业务 API。

安装方式、依赖关系和 MCP 配置属于部署文档，见 [../../README.md](https://github.com/liu-YLY/my-skills/blob/main/plugins/testing/README.md)，不参与运行时路由判断。复制安装只交付 Skill 资源，不安装 MCP 服务；缺 MCP 时由专业 Skill 进入独立模式并如实标记。

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| 意图判断不明确（用户请求含"测试"但未指明策略/用例/性能/Bug/状态机/变更影响/前端准备/测试数据） | 追问用户：列出 8 个子 skill 的能力让用户选择（🔴 CHECKPOINT） | 持续追问，不默认路由。仅当用户明确授权"你来决定"时，可路由到 test-case-engineer，并在输出首行标注「已默认路由到用例生成，如需其他能力请说明」 |
| 混合意图判定争议（如"防御性用例反推"既属 bug-analyzer 又与 test-case-engineer 边界模糊） | 有实际故障证据时先诊断，再转交生成用例；只有用例质量问题时直接进入用例修订 | 若用户明确只需用例不需根因分析，直接路由到 test-case-engineer |
| 子 skill 未安装（路由目标 skill 不存在） | 检测到子 skill 不可用，提示用户安装对应 skill，并给出安装命令 | 标注「子 skill 不可用」，输出 bundle 层方向性指导模板（按目标 skill 选一）：bug-analyzer→「按五步定位法：复现→隔离→定位→验证→报告」；case-engineer→「按四阶段：理解需求→提取测试点→编写用例→自检补全」；strategy→「按五阶段：项目特征→风险矩阵→分层→范围准入准出→资源附录」；performance→「按四阶段：需求理解→场景设计→瓶颈定位→转交判断」；state-machine→「按五阶段：状态型需求识别→状态机建模→完整性检查→10类场景穷举→MCP增强」；frontend→「按五步：读项目说明与已有索引→分层导航索引→单需求映射→运行核实（条件具备时）→交接产物」 |
| 评审类意图歧义（用例评审 / 评审方案 / 覆盖度汇报 / 规模化评审） | 按交付物区分：要问题清单 → R2 评审；要对外材料 → 评审方案子模式；用例数 >100 或要排期 → 规模化评审子模式 | 交付物仍不明确时追问：要评审意见、评审会材料，还是分批抽样方案（🔴 CHECKPOINT） |
| 混合意图协同失败（上游 skill 完成但下游 skill 不可用） | 输出上游 skill 的中间产物（防御性测试点清单 / 分层策略 / 瓶颈定位报告），提示用户手动转交下游 skill 或自行处理 | 标注「协同中断」，仅输出上游 skill 报告，中间产物按上下文 schema 格式作为附录 |
| 子 skill 执行失败（路由后子 skill 内部错误） | 捕获子 skill 错误信息，回退到 bundle 层向用户报告失败原因 | 提示用户直接调用子 skill 重试，或降级为 bundle 层方向性指导模板（同上） |
| 上下文传递丢失（路由后子 skill 未收到原始请求） | 在路由调用时按上下文 schema 显式传递（见下方 schema 定义） | 标注「上下文不完整」，要求子 skill 主动向用户确认缺失信息 |
| "性能 Bug"路由歧义（既属 bug-analyzer 又属 performance） | 默认路由到 performance（资源/架构层优先排查），performance 内部判断是否转交 bug-analyzer | 若用户明确指明为代码逻辑缺陷（如死锁/N+1），直接路由到 bug-analyzer |
| "测试计划"/"测试策略"一词双义（项目级 strategy vs 单功能 case-engineer） | 关键词限定：含"项目级/测试计划/分层/风险矩阵/准入准出"→ strategy；含"单功能/某功能/某模块"→ case-engineer | 追问用户：明确是项目级策略还是单功能用例策略（🔴 CHECKPOINT） |
| 转交可能重复请求确认 | 展示转交依据，继续已授权的分析 | 仅缺关键信息、改变范围或未授权写操作时询问；用户要求逐阶段确认时遵循其要求 |
| 多链同时命中（两条及以上混合意图链的触发信号并存，如"分析订单退款 bug 根因并补用例"同时命中链 1 与链 5） | 按 mixed-intent-chains.md「链冲突裁定」优先级执行最高优先链 | 优先级无法判定时，🔴 CHECKPOINT 列出候选链请用户选择；用户明确"你来决定"时按默认顺序（先根因/建模，后用例生成） |
| strategy 与 case-engineer 协同失败（strategy 完成但 case-engineer 不可用） | 输出 strategy 的分层策略与优先级，提示用户手动转交 case-engineer 生成对应层用例 | 标注「协同中断」，仅输出测试策略报告，分层策略作为用例生成依据附录 |
| test-data-generator 未安装、缺少依赖或数据规则未确认 | 保留上游用例、规则来源与数据需求，报告具体缺口并按目标 Skill 说明处理 | 不用少量手写样例替代批量执行；生成和校验未运行时标 not_run，受影响规则无法检查时保留 incomplete；数据校验通过不代表系统测试通过 |

**上下文传递 schema**（路由/转交时必须按此 JSON 结构传递）：
```json
{
  "original_request": "用户原始请求全文",
  "upstream_artifacts": "上游 skill 输出（如防御性测试点清单 / 分层策略 / 瓶颈定位报告）",
  "completed_steps": ["已完成步骤摘要数组"],
  "downstream_task": "下游 skill 需执行的任务描述"
}
```

转交 test-data-generator 时，upstream_artifacts 需保留用例编号/文件位置、固定组合维度、字段与关联约束及其来源、数量、种子、输出位置和未决规则；仅传递已获得的资料。数据报告中的系统执行状态保持 not_run。

## 反例与黑名单

> **设计依据**：基于 SkillLens 论文（arXiv 2605.23899）实证——只写"应该做 X"没有"不要做 Y"会导致 LLM judge 准确率下降。

### 路由反模式

> 以下反模式聚焦"常见误用场景"。异常触发与恢复路径见上方"失败模式与 Fallback"表，此处不重复。

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|--------|------------|---------|
| 1 | 不判断意图直接调用某个子 skill | 跳过路由会导致用户请求被错误 skill 处理，违反 bundle 职责 | 必须按路由决策表判断意图，意图不明确时追问用户（🔴 CHECKPOINT） |
| 2 | 在 bundle 层重复实现子 skill 的能力 | 破坏职责边界，导致内容冗余和维护成本翻倍 | bundle 只做路由，具体能力由子 skill 承载 |
| 3 | 路由后不传递上下文 | 用户需重新描述需求，体验差且信息丢失 | 路由时显式传递：原始请求 + 已收集上下文 + 已完成步骤摘要 |
| 4 | 混合意图不按"先上游后下游"顺序 | 跳过上游直接下游，下游缺乏上游输入，输出缺乏针对性 | strategy → case-engineer；performance → bug-analyzer（当瓶颈定位到代码缺陷时） |
| 5 | 已授权协同仍默认逐段暂停 | 重复确认阻断完整交付 | 报告转交依据；既有授权覆盖的只读分析连续执行，仅缺关键信息、范围变化或未授权写操作时询问 |

> 路由方向性反例（"性能 Bug 路由到 bug-analyzer""项目级策略路由到 case-engineer"等）已编码在失败模式表第 7/8 行，此处不重复。

### 安装反模式

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|--------|------------|---------|
| 1 | 只装 bundle 不装子 skill | bundle 无法独立完成任何任务，所有请求都会失败 | 整体安装 testing plugin（含 bundle + 7 个子 skill） |
| 2 | bug-analyzer 单独安装不告知降级 | 用户不知缺陷模式库引用失效，根因分析能力打折 | 安装时显式提示「缺陷模式库会降级，同时安装 test-case-engineer 获得完整能力」 |

## 约束规则

1. **本 bundle 只做路由，不实现具体能力** — 所有测试能力由子 skill 承载
2. **路由必须基于显式意图判断** — 不得"默认路由"或"随机路由"
3. **性能类问题默认路由到 performance，不路由到 bug-analyzer** — 性能问题属资源/架构层，仅当瓶颈指向代码逻辑层时才转交 bug-analyzer
4. **strategy 是并列 peer，不是必经入口** — 大多数具体请求直接路由到对应 skill，仅项目级策略请求路由到 strategy
5. **混合意图按业务依赖转交** — strategy → case-engineer；有实际故障证据时 performance → bug-analyzer；用例编写与数据准备按 case-engineer → test-data-generator。既有授权内连续执行，文末列出转交依据和未决事项
6. **上下文必须完整传递** — 路由时需携带用户原始请求和已收集的上下文
7. **子 skill 独立可用** — bundle 不是子 skill 的前置依赖，用户可绕过 bundle 直接调用子 skill
8. **frontend-test-preparation 只在明确前端准备信号时接入** — 普通「测试前端功能」属于用例生成；前端准备产物作为用例生成的上游上下文，不直接产出用例

## 使用示例与快速上手

11 个典型路由演示对话与首次使用引导见 [knowledge/usage-examples.md](knowledge/usage-examples.md)（按需加载：仅当用户想看演示或首次安装配置时读取）。示例索引：

1. Bug 根因分析 → bug-analyzer；2. Bug+用例（链 1）；3. 意图不明确 → 追问（🔴 CHECKPOINT，规则见路由决策表与失败模式表）；4. 测试策略 → strategy
5. 性能测试方案 → performance；6. 策略+用例（链 2）；7. 状态机建模 → state-machine；8. 状态机+用例（链 5）
9. 已有用例准备数据 → test-data-generator；10. 编写用例+准备数据（链 8）；11. 前端准备+用例（链 9）

---

版本历史见 [CHANGELOG.md](CHANGELOG.md)。
