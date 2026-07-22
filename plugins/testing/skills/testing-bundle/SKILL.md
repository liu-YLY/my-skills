---
name: testing-bundle
version: 3.1.0
description: >-
  Use when user needs any testing capability — generating test cases, reviewing test cases,
  designing test strategies, performance test plans, analyzing bug root causes, OR state-machine-driven
  testing for stateful business objects (orders/approvals/tickets/membership etc.).
  Triggers on: 测试、测试用例、测试点、用例评审、测试策略、测试计划、测试分层、风险矩阵、准入准出、需求分析、Bug分析、根因、缺陷定位、复现、5 Whys、性能测试、负载测试、压力测试、TPS、响应时间、瓶颈、容量评估、状态机、状态流转、状态转换、生命周期、非法跳转、幂等、并发冲突、消息乱序、状态回退、幽灵状态、终态吸收.
  This is a bundle entry that routes to test-strategy-engineer, test-case-engineer, performance-test-engineer, bug-analyzer, or state-machine-test-engineer.
keywords:
  - 测试
  - 测试用例
  - 测试策略
  - 性能测试
  - Bug分析
  - 状态机测试
  - 测试bundle
---

# Testing Bundle

测试能力 bundle 入口 v3.1.0：统一路由到 5 个子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer / state-machine-test-engineer），另可协同外部 skill change-impact-analyzer（链 6）。

## 适用范围

**适用**：任何测试相关请求（测试策略 / 测试用例生成 / 用例评审 / 性能测试方案 / 性能瓶颈定位 / Bug 根因分析 / 缺陷定位 / 防御性用例反推 / 状态机驱动的状态型需求测试）

**不适用**：非测试领域（文档撰写、代码风格、其他 skill 范畴）

## 路由规则

收到用户请求后，按以下判定顺序路由（**先匹配混合意图链，再查单意图路由表**）：

1. **第一步**：扫描请求是否命中任一混合意图链关键词（见"混合意图链"章节）→ 命中则按对应链路执行
2. **第二步**：未命中混合意图链 → 查单意图路由决策表 → 路由到对应子 skill
3. **第三步**：单意图也未命中 → 追问用户（🔴 CHECKPOINT）

按以下 5-skill 架构图路由到子 skill：

```
                    用户测试请求
                         │
                         ▼
              ┌─────────────────────────┐
              │   testing-bundle v3.0.0 │  路由层（只路由，不实现能力）
              └───────────┬─────────────┘
                          │ 5-way 意图判断
        ┌─────────┬───────┼───────┬───────────┬──────────────┐
        ▼         ▼       ▼       ▼           ▼
  ┌──────────┐┌─────────┐┌──────┐┌───────────┐┌──────────────┐
  │strategy- ││case-    ││bug-  ││performance││state-machine │
  │engineer  ││engineer ││anlyz ││-engineer  ││-test-engineer│
  │ v1.0.0   ││ v8.1.0  ││v1.0.0││ v1.0.0    ││ v1.0.0(新增) │
  ├──────────┤├─────────┤├──────┤├───────────┤├──────────────┤
  │项目级     ││功能用例  ││功能缺陷││性能测试    ││状态机建模     │
  │策略/分层  ││设计      ││根因   ││场景+瓶颈   ││+场景穷举      │
  └──────────┘└─────────┘└──────┘└───────────┘└──────────────┘
   peer          peer       peer      peer         peer
```

### 路由决策表（单意图）

> 仅列单意图路由。混合意图已在上文"判定顺序第一步"优先处理，不在此表。

| 用户意图关键词 | 路由到 | 说明 |
|---------------|--------|------|
| 测试策略、测试计划、测试分层、风险矩阵、准入准出、测试范围与优先级 **等项目级策略信号** | **test-strategy-engineer** | 项目级策略 |
| 测试用例、编写用例、生成用例、测试点、需求分析、用例评审、单功能测试策略 **等功能级用例信号** | **test-case-engineer** | 功能用例生成 |
| Bug分析、根因、缺陷定位、复现、5 Whys、鱼骨图、防御性用例反推 **等功能缺陷信号** | **bug-analyzer** | 功能缺陷根因 |
| 性能测试、负载测试、压力测试、并发测试、TPS、响应时间、瓶颈、性能瓶颈、容量评估 **等性能/资源层信号** | **performance-test-engineer** | 性能场景+瓶颈分析 |
| 状态机、状态流转、状态转换、生命周期、非法跳转、幂等、并发冲突、消息乱序、状态回退、幽灵状态、终态吸收 **等状态型需求信号** | **state-machine-test-engineer** | 状态机建模+场景穷举 |
| 意图不明确 | **追问用户**（🔴 CHECKPOINT） | 列出 5 个子 skill 的能力让用户选择 |

> "等X信号"判定边界：含上述任一关键词，或语义等价表达（如"测试计划"等价"测试策略"、"QPS"等价"吞吐量/TPS"）。边界模糊时按"判定顺序第三步"追问用户。

### 混合意图链

当用户请求同时涉及多个子 skill 时，按以下 7 条链路执行，每条链的转交点都必须设 🔴 CHECKPOINT：

**链 1：分析 Bug 并补充用例**
```
步骤 1: 路由到 bug-analyzer 执行根因分析
        ↓
步骤 2: bug-analyzer 输出防御性测试点清单
        ↓
🔴 CHECKPOINT · bug-analyzer 完成：防御性测试点清单必须展示给用户确认，用户可修改清单或终止流程，确认后才转交 case-engineer。
        ↓
步骤 3: 转交 test-case-engineer 基于防御性测试点清单生成完整用例
        ↓
步骤 4: 输出最终报告（根因分析 + 完整测试用例）
```

**链 2：制定测试策略并生成分层用例**
```
步骤 1: 路由到 test-strategy-engineer 执行项目级策略设计
        ↓
步骤 2: strategy 输出分层策略 + 优先级 + 准入准出
        ↓
🔴 CHECKPOINT · strategy 完成：分层策略与优先级必须展示给用户确认，用户可修改或终止流程，确认后才转交 case-engineer。
        ↓
步骤 3: 转交 test-case-engineer 按分层策略生成对应层用例
        ↓
步骤 4: 输出最终报告（测试策略 + 分层测试用例）
```

**链 3：做性能测试并分析瓶颈**
```
步骤 1: 路由到 performance-test-engineer
        ↓
步骤 2: performance 内部完成正向方案（阶段 1-2）+ 逆向瓶颈定位（阶段 3）
        ↓
🔴 CHECKPOINT · performance 阶段 2 后：性能测试方案必须展示给用户确认，用户可修改负载模型/场景/阈值，确认后才进入阶段 3 瓶颈定位。
        ↓
步骤 3: performance 阶段 3 输出瓶颈定位报告（无需转交其他 skill，本链内部完成）
        ↓
步骤 4: 输出最终报告（性能测试方案 + 瓶颈定位报告）
```

**链 4：性能问题定位到代码缺陷**
```
步骤 1: 路由到 performance-test-engineer 执行瓶颈定位（资源/架构层）
        ↓
步骤 2: performance 阶段 3 输出瓶颈定位报告，阶段 4 判断瓶颈指向代码逻辑层
        ↓
🔴 CHECKPOINT · performance 瓶颈定位后：瓶颈归属判断与转交依据必须展示给用户确认，用户可修改归属判断或终止转交，确认后才转交 bug-analyzer。
        ↓
步骤 3: 转交 bug-analyzer 分析代码逻辑层缺陷（死锁/内存泄漏/N+1 查询/锁竞争等）
        ↓
步骤 4: 输出最终报告（瓶颈定位报告 + 代码缺陷根因 + 修复建议）
```

**链 3 vs 链 4 二级判定规则**（区分两条性能链路）：
- 含关键词"代码层/逻辑层/代码缺陷/死锁/N+1 查询/内存泄漏/连接泄漏/空指针/业务规则错误 **等代码逻辑层信号**" → 链 4（转交 bug-analyzer）
- 含关键词"资源/CPU/IO/网络/架构/扩容/连接池不足/缓存未命中 **等资源/架构层信号**" → 链 3（performance 内部完成）
- 同时含两类关键词 → 默认走链 3，performance 阶段 4 判断后决定是否转交（🔴 CHECKPOINT 让用户确认）

**链 5：状态机建模 + 用例生成**
```
步骤 1: 路由到 state-machine-test-engineer 执行状态机建模
        ↓
步骤 2: state-machine 输出状态机模型 + 场景清单（含依据类型标注：需求明确/合理推理/待确认）
        ↓
🔴 CHECKPOINT · state-machine 完成：状态机模型与场景清单必须展示给用户确认，用户可修改模型/补充场景/终止流程，确认后才转交 case-engineer。
        ↓
步骤 3: 转交 test-case-engineer 基于场景清单生成完整用例（每场景落实为可执行步骤）
        ↓
步骤 4: 输出最终报告（状态机模型 + 场景清单 + 完整测试用例）
```

**链 5 触发条件**：用户请求同时含"状态机/状态流转/生命周期/状态转换"等状态型信号 **且** 含"测试用例/测试场景/测试点"等用例生成信号。
- 仅含状态型信号 → 单意图路由到 state-machine-test-engineer（输出场景清单为止）
- 仅含用例信号 → 单意图路由到 test-case-engineer（按四阶段流程）
- 含两者 → 链 5 协同

**链 6：评审 → 覆盖缺口验证**
```
步骤 1: 路由到 test-case-engineer 评审模式执行用例评审
        ↓
步骤 2: 评审 R2 覆盖度维度发现 P0/P1 问题（4 类场景缺失 / 异常类型用例为 0）
        ↓
🔴 CHECKPOINT · 评审覆盖度问题确认：覆盖度问题清单（缺失场景类型 + 受影响模块 + 度量报告覆盖度行）必须展示给用户确认，用户可修改范围或终止流程，确认后才转交 change-impact-analyzer。
        ↓
步骤 3: 转交 change-impact-analyzer 做 git diff × 用例交叉验证，用代码层证据确认覆盖缺口是否真实存在
        ↓
步骤 4: 输出最终报告（评审意见表 + 评审度量报告 + 覆盖度问题清单 + 代码层覆盖缺口验证 + 补充用例建议）
```

**链 6 触发条件**：用户请求同时含"评审/review/检查用例质量"等评审信号 **且** 含"覆盖缺口/覆盖度验证/代码变更影响/diff 分析/回归风险"等覆盖验证信号。
- 仅含评审信号 → 单意图路由到 test-case-engineer 评审模式
- 仅含覆盖验证信号 → 单意图路由到 change-impact-analyzer
- 含两者 → 链 6 协同

> **注意**：change-impact-analyzer 不是 testing-bundle 的核心 peer（5-skill 架构未含），需单独安装。未安装时链 6 步骤 3 降级为 bundle 层方向性指导（"按四阶段：收集输入→Diff 解析→交叉分析→生成报告"）。

**链 7：评审 → 风险用例根因反推**
```
步骤 1: 路由到 test-case-engineer 评审模式执行用例评审
        ↓
步骤 2: 评审发现高风险用例（P0 优先级集中 / 可执行性 P0 占位符 / 字段规范 P0 缺失）
        ↓
🔴 CHECKPOINT · 风险用例清单确认：风险用例清单（用例 ID + 问题维度 + 严重等级 + 具体问题 + 度量报告严重等级分布）必须展示给用户确认，用户可修改范围或终止流程，确认后才转交 bug-analyzer。
        ↓
步骤 3: 转交 bug-analyzer 基于风险用例反推根因（将风险用例视为"潜在缺陷场景"，按五步定位法分析根因）
        ↓
步骤 4: 输出最终报告（评审意见表 + 评审度量报告 + 风险用例清单 + 根因反推 + 防御性测试点清单）
```

**链 7 触发条件**：用户请求同时含"评审/review/检查用例质量"等评审信号 **且** 含"根因/缺陷定位/风险分析/为什么会出问题"等根因反推信号。
- 仅含评审信号 → 单意图路由到 test-case-engineer 评审模式
- 仅含根因信号 → 单意图路由到 bug-analyzer
- 含两者 → 链 7 协同

## 子 skill 协同

本 bundle 包含 5 个子 skill，各自独立可用，也可通过 bundle 统一调用：

| 子 skill | 职责 | 核心工作流 | 独立可用 |
|---------|------|----------|---------|
| [test-strategy-engineer](../test-strategy-engineer/SKILL.md) | 项目级测试策略（风险矩阵+分层+准入准出） | 五阶段：项目特征→风险矩阵→分层→CHECKPOINT→范围准入准出→（可选）资源附录 | ✅ 是 |
| [test-case-engineer](../test-case-engineer/SKILL.md) | 功能用例生成（需求→测试用例） | 四阶段：理解需求→提取测试点→编写用例→自检补全 | ✅ 是 |
| [performance-test-engineer](../performance-test-engineer/SKILL.md) | 性能测试方案+瓶颈定位（资源/架构层） | 四阶段：需求理解→场景设计→CHECKPOINT→瓶颈定位→转交判断 | ✅ 是 |
| [bug-analyzer](../bug-analyzer/SKILL.md) | 功能缺陷根因（代码逻辑层） | 五步定位法：复现→隔离→定位→验证→报告 | ⚠️ 依赖 test-case-engineer 的 bug-patterns.md |
| [state-machine-test-engineer](../state-machine-test-engineer/SKILL.md) | 状态机建模+场景穷举（状态型需求） | 五阶段：状态型需求识别→状态机建模→CHECKPOINT→完整性检查→10类场景穷举→（可选）MCP增强 | ✅ 是（MCP 可选增强） |

### 知识库共享

- `bug-patterns.md` 主归属 test-case-engineer，bug-analyzer 通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用
- strategy/performance/state-machine 不共享知识库（聚焦点不同，共享会引入路由歧义）
- state-machine-test-engineer 可选调用 `state-machine-testing-mcp` Server 做 Schema 校验与可视化（未安装时降级为纯 LLM 推理）

**依赖说明**：
- bug-analyzer 单独安装时，步骤 2/3 的"对照缺陷模式库"能力会降级（仍有通用模式兜底，但无法查阅完整缺陷模式库）。通过本 bundle 整体安装获得完整能力。
- state-machine-test-engineer 单独安装时完全可用；安装配套 MCP Server 后进入"增强模式"，获得 Schema 校验、Mermaid 可视化、覆盖度报告等额外能力。

## 安装方式

### 方式 1：整体安装（推荐）

安装 `testing-bundle` + `test-strategy-engineer` + `test-case-engineer` + `performance-test-engineer` + `bug-analyzer` + `state-machine-test-engineer` 六个 skill，获得完整测试能力。

### 方式 2：按需安装

- 只需项目级策略 → 安装 `test-strategy-engineer`
- 只需用例生成 → 安装 `test-case-engineer`
- 只需性能测试 → 安装 `performance-test-engineer`
- 只需 Bug 分析 → 安装 `bug-analyzer`（缺陷模式库引用会降级）
- 只需状态机测试 → 安装 `state-machine-test-engineer`（可选再装 MCP Server 进入增强模式）
- 多项需求 → 安装 `testing-bundle` + 对应子 skill

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| 意图判断不明确（用户请求含"测试"但未指明策略/用例/性能/Bug/状态机） | 追问用户：列出 5 个子 skill 的能力让用户选择（🔴 CHECKPOINT） | 默认路由到 test-case-engineer（覆盖面更广），并在输出首行标注「已默认路由到用例生成，如需其他能力请说明」 |
| 混合意图判定争议（如"防御性用例反推"既属 bug-analyzer 又与 test-case-engineer 边界模糊） | 优先路由到 bug-analyzer（根因分析是前置），完成后 🔴 CHECKPOINT 转交 test-case-engineer 生成完整用例 | 若用户明确只需用例不需根因分析，直接路由到 test-case-engineer |
| 子 skill 未安装（路由目标 skill 不存在） | 检测到子 skill 不可用，提示用户安装对应 skill，并给出安装命令 | 标注「子 skill 不可用」，输出 bundle 层方向性指导模板（按目标 skill 选一）：bug-analyzer→「按五步定位法：复现→隔离→定位→验证→报告」；case-engineer→「按四阶段：理解需求→提取测试点→编写用例→自检补全」；strategy→「按五阶段：项目特征→风险矩阵→分层→范围准入准出→资源附录」；performance→「按四阶段：需求理解→场景设计→瓶颈定位→转交判断」；state-machine→「按五阶段：状态型需求识别→状态机建模→完整性检查→10类场景穷举→MCP增强」 |
| 混合意图协同失败（上游 skill 完成但下游 skill 不可用） | 输出上游 skill 的中间产物（防御性测试点清单 / 分层策略 / 瓶颈定位报告），提示用户手动转交下游 skill 或自行处理 | 标注「协同中断」，仅输出上游 skill 报告，中间产物按上下文 schema 格式作为附录 |
| 子 skill 执行失败（路由后子 skill 内部错误） | 捕获子 skill 错误信息，回退到 bundle 层向用户报告失败原因 | 提示用户直接调用子 skill 重试，或降级为 bundle 层方向性指导模板（同上） |
| 上下文传递丢失（路由后子 skill 未收到原始请求） | 在路由调用时按上下文 schema 显式传递（见下方 schema 定义） | 标注「上下文不完整」，要求子 skill 主动向用户确认缺失信息 |
| "性能 Bug"路由歧义（既属 bug-analyzer 又属 performance） | 默认路由到 performance（资源/架构层优先排查），performance 内部判断是否转交 bug-analyzer | 若用户明确指明为代码逻辑缺陷（如死锁/N+1），直接路由到 bug-analyzer |
| "测试策略"一词双义（项目级 strategy vs 单功能 case-engineer） | 关键词限定：含"项目级/测试计划/分层/风险矩阵/准入准出"→ strategy；含"单功能/某功能测试策略"→ case-engineer | 追问用户：明确是项目级策略还是单功能用例策略（🔴 CHECKPOINT） |
| strategy 与 case-engineer 协同失败（strategy 完成但 case-engineer 不可用） | 输出 strategy 的分层策略与优先级，提示用户手动转交 case-engineer 生成对应层用例 | 标注「协同中断」，仅输出测试策略报告，分层策略作为用例生成依据附录 |

**上下文传递 schema**（路由/转交时必须按此 JSON 结构传递）：
```json
{
  "original_request": "用户原始请求全文",
  "upstream_artifacts": "上游 skill 输出（如防御性测试点清单 / 分层策略 / 瓶颈定位报告）",
  "completed_steps": ["已完成步骤摘要数组"],
  "downstream_task": "下游 skill 需执行的任务描述"
}
```

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
| 5 | 混合意图协同无用户确认点 | 用户无法终止流程或修改中间产物 | 每个转交点必须 🔴 CHECKPOINT，用户确认后才转交 |

> 路由方向性反例（"性能 Bug 路由到 bug-analyzer""项目级策略路由到 case-engineer"等）已编码在失败模式表第 7/8 行，此处不重复。

### 安装反模式

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|--------|------------|---------|
| 1 | 只装 bundle 不装子 skill | bundle 无法独立完成任何任务，所有请求都会失败 | 整体安装 testing-bundle + 5 个子 skill |
| 2 | bug-analyzer 单独安装不告知降级 | 用户不知缺陷模式库引用失效，根因分析能力打折 | 安装时显式提示「缺陷模式库会降级，同时安装 test-case-engineer 获得完整能力」 |

## 约束规则

1. **本 bundle 只做路由，不实现具体能力** — 所有测试能力由子 skill 承载
2. **路由必须基于显式意图判断** — 不得"默认路由"或"随机路由"
3. **性能类问题默认路由到 performance，不路由到 bug-analyzer** — 性能问题属资源/架构层，仅当瓶颈指向代码逻辑层时才转交 bug-analyzer
4. **strategy 是并列 peer，不是必经入口** — 大多数具体请求直接路由到对应 skill，仅项目级策略请求路由到 strategy
5. **混合意图遵循"先上游后下游"顺序，转交点必须 🔴 CHECKPOINT** — strategy → case-engineer；performance → bug-analyzer
6. **上下文必须完整传递** — 路由时需携带用户原始请求和已收集的上下文
7. **子 skill 独立可用** — bundle 不是子 skill 的前置依赖，用户可绕过 bundle 直接调用子 skill

## 使用示例

### 示例 1：Bug 根因分析（自动路由到 bug-analyzer）

```
用户：线上出现重复扣款 Bug，用户反馈偶发，帮我分析根因

testing-bundle:
  → 意图判断：Bug 根因分析
  → 路由到 bug-analyzer
  → 执行五步定位法
  → 输出根因分析报告 + 防御性测试点清单
```

### 示例 2：混合意图 Bug + 用例（链 1 协同）

```
用户：分析这个重复扣款 Bug 的根因，并补充测试用例防止再次出现

testing-bundle:
  → 意图判断：混合（分析 + 生成）
  → 路由到 bug-analyzer 执行根因分析
  → bug-analyzer 输出防御性测试点清单

🔴 CHECKPOINT · bug-analyzer 完成：防御性测试点清单必须展示给用户确认，用户可修改清单或终止流程，确认后才转交 test-case-engineer。

  → 转交 test-case-engineer 基于清单生成完整用例
  → 输出根因分析报告 + 完整测试用例
```

### 示例 3：意图不明确（追问）

🔴 **CHECKPOINT · 意图不明确时强制追问**：不得"默认路由"，必须列出 5 个子 skill 的能力让用户选择。

```
用户：我有个测试相关的问题

testing-bundle:
  → 意图判断：不明确
  → 追问用户：
    "请告诉我您需要哪类帮助：
     A. 项目级测试策略（test-strategy-engineer）
     B. 生成测试用例（test-case-engineer）
     C. 性能测试方案/瓶颈定位（performance-test-engineer）
     D. 分析 Bug 根因（bug-analyzer）
     E. 状态机驱动的状态型需求测试（state-machine-test-engineer）"
```

### 示例 4：测试策略（自动路由到 strategy）

```
用户：我们要启动一个新项目的测试，需要制定测试策略，包括风险矩阵和测试分层

testing-bundle:
  → 意图判断：项目级测试策略（关键词：测试策略、风险矩阵、测试分层）
  → 路由到 test-strategy-engineer
  → 执行五阶段流程：项目特征→风险矩阵→分层→CHECKPOINT→范围准入准出
  → 输出测试策略报告
```

### 示例 5：性能测试方案（自动路由到 performance）

```
用户：我们的支付系统要做性能测试，预期峰值 5000 TPS，关注 P99 响应时间

testing-bundle:
  → 意图判断：性能测试方案设计（关键词：性能测试、TPS、响应时间）
  → 路由到 performance-test-engineer
  → 执行阶段 1-2：性能需求理解 + 测试场景设计

🔴 CHECKPOINT · performance 阶段 2 后：性能测试方案必须展示给用户确认，确认后进入阶段 3（若需瓶颈定位）。

  → 输出性能测试方案（负载模型 + 场景 + 指标阈值）
```

### 示例 6：策略 + 用例协同（链 2 协同）

```
用户：制定项目级测试策略，并按策略生成分层用例

testing-bundle:
  → 意图判断：混合（策略 + 用例）
  → 路由到 test-strategy-engineer 执行项目级策略设计
  → strategy 输出分层策略 + 优先级 + 准入准出

🔴 CHECKPOINT · strategy 完成：分层策略与优先级必须展示给用户确认，用户可修改或终止流程，确认后才转交 test-case-engineer。

  → 转交 test-case-engineer 按分层策略生成对应层用例
  → 输出测试策略 + 分层测试用例
```

### 示例 7：状态机建模（自动路由到 state-machine）

```
用户：订单退款流程要做测试，订单状态包括待支付/已支付/已取消/退款中/退款成功/退款失败

testing-bundle:
  → 意图判断：状态型需求测试（关键词：状态、退款流程、状态名罗列）
  → 路由到 state-machine-test-engineer
  → 执行五阶段：状态型需求识别→状态机建模→CHECKPOINT→完整性检查→10类场景穷举
  → 输出状态机模型 + 场景清单（含依据类型标注，未说明的退款失败恢复路径标"待确认"）
```

### 示例 8：状态机 + 用例协同（链 5 协同）

```
用户：为订单退款流程设计状态机测试场景，并生成完整测试用例

testing-bundle:
  → 意图判断：混合（状态机 + 用例）
  → 路由到 state-machine-test-engineer 执行状态机建模
  → state-machine 输出状态机模型 + 场景清单（含依据类型标注）

🔴 CHECKPOINT · state-machine 完成：状态机模型与场景清单必须展示给用户确认，用户可修改模型/补充场景/终止流程，确认后才转交 test-case-engineer。

  → 转交 test-case-engineer 基于场景清单生成完整用例
  → 输出状态机模型 + 场景清单 + 完整测试用例
```

## 快速上手

1. 确认已安装 5 个子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer / state-machine-test-engineer）
2. 用户提出测试相关请求时，testing-bundle 自动触发
3. bundle 按 5-way 路由决策表判断意图并路由到对应子 skill
4. 混合意图按对应链路执行（7 条链），转交点 🔴 CHECKPOINT
5. 子 skill 执行具体任务并输出结果
6. state-machine-test-engineer 可选安装配套 MCP Server 进入增强模式（详见 [state-machine-test-engineer/integrations/quickstart.md](../state-machine-test-engineer/integrations/quickstart.md)）

---

**版本历史**：
- v1.0.0: 初始版本，2-skill 路由（case-engineer + bug-analyzer）
- v2.0.0: 扩展为 4-skill 路由（+ strategy + performance），breaking change
- v3.0.0: 扩展为 5-skill 路由（+ state-machine-test-engineer），新增链 5（状态机+用例协同），breaking change
- v3.1.0: 新增链 6（评审→覆盖缺口验证，协同外部 change-impact-analyzer）+ 链 7（评审→风险用例根因反推，协同 bug-analyzer），评审模式成为混合意图链起点
