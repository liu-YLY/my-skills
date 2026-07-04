---
name: testing-bundle
version: 2.0.0
description: >-
  Use when user needs any testing capability — generating test cases, reviewing test cases,
  designing test strategies, performance test plans, OR analyzing bug root causes.
  Triggers on: 测试、测试用例、测试点、用例评审、测试策略、测试计划、测试分层、风险矩阵、准入准出、需求分析、Bug分析、根因、缺陷定位、复现、5 Whys、性能测试、负载测试、压力测试、TPS、响应时间、瓶颈、容量评估.
  This is a bundle entry that routes to test-strategy-engineer, test-case-engineer, performance-test-engineer, or bug-analyzer.
keywords:
  - 测试
  - 测试用例
  - 测试策略
  - 性能测试
  - Bug分析
  - 测试bundle
---

# Testing Bundle

测试能力 bundle 入口 v2.0.0：统一路由到 4 个子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer）。

## 适用范围

**适用**：任何测试相关请求（测试策略 / 测试用例生成 / 用例评审 / 性能测试方案 / 性能瓶颈定位 / Bug 根因分析 / 缺陷定位 / 防御性用例反推）

**不适用**：非测试领域（文档撰写、代码风格、其他 skill 范畴）

## 路由规则

收到用户请求后，按以下 4-skill 架构图路由到子 skill：

```
                    用户测试请求
                         │
                         ▼
              ┌─────────────────────────┐
              │   testing-bundle v2.0.0 │  路由层（只路由，不实现能力）
              └───────────┬─────────────┘
                          │ 4-way 意图判断
        ┌─────────┬───────┼───────┬───────────┐
        ▼         ▼       ▼       ▼
  ┌──────────┐┌─────────┐┌──────┐┌───────────┐
  │strategy- ││case-    ││bug-  ││performance│
  │engineer  ││engineer ││anlyz ││-engineer  │
  │ v1.0.0   ││ v8.0.0  ││v1.0.0││ v1.0.0    │
  ├──────────┤├─────────┤├──────┤├───────────┤
  │项目级     ││功能用例  ││功能缺陷││性能测试    │
  │策略/分层  ││设计      ││根因   ││场景+瓶颈   │
  └──────────┘└─────────┘└──────┘└───────────┘
   peer          peer       peer      peer
```

### 路由决策表

| 用户意图关键词 | 路由到 | 说明 |
|---------------|--------|------|
| 测试策略、测试计划、测试分层、风险矩阵、准入准出、测试范围与优先级 | **test-strategy-engineer** | 项目级策略 |
| 测试用例、编写用例、生成用例、测试点、需求分析、用例评审、单功能测试策略 | **test-case-engineer** | 功能用例生成 |
| Bug分析、根因、缺陷定位、复现、5 Whys、鱼骨图、防御性用例反推 | **bug-analyzer** | 功能缺陷根因 |
| 性能测试、负载测试、压力测试、并发测试、TPS、响应时间、瓶颈、性能瓶颈、容量评估 | **performance-test-engineer** | 性能场景+瓶颈分析 |
| 混合意图 | 见下方混合意图链 | 按对应链路执行 |
| 意图不明确 | **追问用户** | 列出 4 个子 skill 的能力让用户选择 |

### 混合意图链

当用户请求同时涉及多个子 skill 时，按以下 4 条链路执行，每条链的转交点都必须设 🔴 CHECKPOINT：

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

## 关键路由规则

1. **性能类问题默认路由到 performance，不路由到 bug-analyzer** — bundle 需区分"功能 Bug"与"性能问题"，性能问题（RT/TPS/资源饱和）由 performance 处理资源/架构层，仅当瓶颈指向代码逻辑层时才转交 bug-analyzer
2. **strategy 是并列 peer，不是必经入口** — 大多数具体请求直接路由到对应 skill，仅项目级策略请求路由到 strategy
3. **混合意图遵循"先上游后下游"顺序** — strategy → case-engineer；performance → bug-analyzer（当性能瓶颈定位到代码缺陷时）
4. **每个转交点设 🔴 CHECKPOINT** — 用户可终止/修改转交内容，禁止无确认点直接转交

## 子 skill 协同

本 bundle 包含 4 个子 skill，各自独立可用，也可通过 bundle 统一调用：

| 子 skill | 职责 | 核心工作流 | 独立可用 |
|---------|------|----------|---------|
| [test-strategy-engineer](../test-strategy-engineer/SKILL.md) | 项目级测试策略（风险矩阵+分层+准入准出） | 五阶段：项目特征→风险矩阵→分层→CHECKPOINT→范围准入准出→（可选）资源附录 | ✅ 是 |
| [test-case-engineer](../test-case-engineer/SKILL.md) | 功能用例生成（需求→测试用例） | 四阶段：理解需求→提取测试点→编写用例→自检补全 | ✅ 是 |
| [performance-test-engineer](../performance-test-engineer/SKILL.md) | 性能测试方案+瓶颈定位（资源/架构层） | 四阶段：需求理解→场景设计→CHECKPOINT→瓶颈定位→转交判断 | ✅ 是 |
| [bug-analyzer](../bug-analyzer/SKILL.md) | 功能缺陷根因（代码逻辑层） | 五步定位法：复现→隔离→定位→验证→报告 | ⚠️ 依赖 test-case-engineer 的 bug-patterns.md |

### 知识库共享

- `bug-patterns.md` 主归属 test-case-engineer，bug-analyzer 通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用
- strategy/performance 不共享知识库（聚焦点不同，共享会引入路由歧义）

**依赖说明**：bug-analyzer 单独安装时，步骤 2/3 的"对照缺陷模式库"能力会降级（仍有通用模式兜底，但无法查阅完整缺陷模式库）。通过本 bundle 整体安装获得完整能力。

## 安装方式

### 方式 1：整体安装（推荐）

安装 `testing-bundle` + `test-strategy-engineer` + `test-case-engineer` + `performance-test-engineer` + `bug-analyzer` 五个 skill，获得完整测试能力。

### 方式 2：按需安装

- 只需项目级策略 → 安装 `test-strategy-engineer`
- 只需用例生成 → 安装 `test-case-engineer`
- 只需性能测试 → 安装 `performance-test-engineer`
- 只需 Bug 分析 → 安装 `bug-analyzer`（缺陷模式库引用会降级）
- 多项需求 → 安装 `testing-bundle` + 对应子 skill

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| 意图判断不明确（用户请求含"测试"但未指明策略/用例/性能/Bug） | 追问用户：列出 4 个子 skill 的能力让用户选择（🔴 CHECKPOINT） | 默认路由到 test-case-engineer（覆盖面更广），并在输出首行标注「已默认路由到用例生成，如需其他能力请说明」 |
| 混合意图判定争议（如"防御性用例反推"既属 bug-analyzer 又与 test-case-engineer 边界模糊） | 优先路由到 bug-analyzer（根因分析是前置），完成后 🔴 CHECKPOINT 转交 test-case-engineer 生成完整用例 | 若用户明确只需用例不需根因分析，直接路由到 test-case-engineer |
| 子 skill 未安装（路由目标 skill 不存在） | 检测到子 skill 不可用，提示用户安装对应 skill，并给出安装命令 | 标注「子 skill 不可用」，输出 bundle 层能提供的方向性指导（如"按五步定位法分析根因"） |
| 混合意图协同失败（上游 skill 完成但下游 skill 不可用） | 输出上游 skill 的中间产物（如防御性测试点清单 / 分层策略），提示用户手动转交下游 skill 或自行处理 | 标注「协同中断」，仅输出上游 skill 报告，中间产物作为附录 |
| 子 skill 执行失败（路由后子 skill 内部错误） | 捕获子 skill 错误信息，回退到 bundle 层向用户报告失败原因 | 提示用户直接调用子 skill 重试，或降级为 bundle 层方向性指导 |
| 上下文传递丢失（路由后子 skill 未收到原始请求） | 在路由调用时显式传递：用户原始请求 + 已收集上下文 + 已完成步骤摘要 | 标注「上下文不完整」，要求子 skill 主动向用户确认缺失信息 |
| "性能 Bug"路由歧义（既属 bug-analyzer 又属 performance） | 默认路由到 performance（资源/架构层优先排查），performance 内部判断是否转交 bug-analyzer | 若用户明确指明为代码逻辑缺陷（如死锁/N+1），直接路由到 bug-analyzer |
| "测试策略"一词双义（项目级 strategy vs 单功能 case-engineer） | 关键词限定：含"项目级/测试计划/分层/风险矩阵/准入准出"→ strategy；含"单功能/某功能测试策略"→ case-engineer | 追问用户：明确是项目级策略还是单功能用例策略（🔴 CHECKPOINT） |
| strategy 与 case-engineer 协同失败（strategy 完成但 case-engineer 不可用） | 输出 strategy 的分层策略与优先级，提示用户手动转交 case-engineer 生成对应层用例 | 标注「协同中断」，仅输出测试策略报告，分层策略作为用例生成依据附录 |

## 反例与黑名单

> **设计依据**：基于 SkillLens 论文（arXiv 2605.23899）实证——只写"应该做 X"没有"不要做 Y"会导致 LLM judge 准确率下降。

### 路由反模式

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|--------|------------|---------|
| 1 | 不判断意图直接调用某个子 skill | 跳过路由会导致用户请求被错误 skill 处理，违反 bundle 职责 | 必须按路由决策表判断意图，意图不明确时追问用户（🔴 CHECKPOINT） |
| 2 | 在 bundle 层重复实现子 skill 的能力 | 破坏职责边界，导致内容冗余和维护成本翻倍 | bundle 只做路由，具体能力由子 skill 承载 |
| 3 | 路由后不传递上下文 | 用户需重新描述需求，体验差且信息丢失 | 路由时显式传递：原始请求 + 已收集上下文 + 已完成步骤摘要 |
| 4 | 混合意图不按"先上游后下游"顺序 | 跳过上游直接下游，下游缺乏上游输入，输出缺乏针对性 | strategy → case-engineer；performance → bug-analyzer（当瓶颈定位到代码缺陷时） |
| 5 | 混合意图协同无用户确认点 | 用户无法终止流程或修改中间产物 | 每个转交点必须 🔴 CHECKPOINT，用户确认后才转交 |
| 6 | 把"性能 Bug"路由到 bug-analyzer | 性能问题（RT/TPS/资源饱和）属资源/架构层，bug-analyzer 聚焦代码逻辑层，错路由会导致定位方向错误 | 性能类问题默认路由到 performance，performance 内部判断是否转交 bug-analyzer |
| 7 | 把"项目级测试策略"路由到 case-engineer | case-engineer 处理单功能用例，项目级策略（风险矩阵/分层/准入准出）超出其职责 | 含"项目级/测试计划/分层/风险矩阵/准入准出"关键词路由到 strategy |
| 8 | strategy/performance 与 case-engineer/bug-analyzer 混合意图不按"先上游后下游"顺序 | 跳过 strategy 直接 case-engineer 会丢失分层依据；跳过 performance 直接 bug-analyzer 会丢失瓶颈定位报告 | strategy → case-engineer；performance → bug-analyzer，转交点 🔴 CHECKPOINT |

### 安装反模式

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|--------|------------|---------|
| 1 | 只装 bundle 不装子 skill | bundle 无法独立完成任何任务，所有请求都会失败 | 整体安装 testing-bundle + 4 个子 skill |
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

### 示例 1：正向用例生成（自动路由到 case-engineer）

```
用户：我有一个用户登录功能需要测试，需求是手机号+验证码登录...

testing-bundle:
  → 意图判断：测试用例生成
  → 路由到 test-case-engineer
  → 执行四阶段流程
  → 输出测试用例
```

### 示例 2：Bug 根因分析（自动路由到 bug-analyzer）

```
用户：线上出现重复扣款 Bug，用户反馈偶发，帮我分析根因

testing-bundle:
  → 意图判断：Bug 根因分析
  → 路由到 bug-analyzer
  → 执行五步定位法
  → 输出根因分析报告 + 防御性测试点清单
```

### 示例 3：混合意图 Bug + 用例（链 1 协同）

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

### 示例 4：意图不明确（追问）

🔴 **CHECKPOINT · 意图不明确时强制追问**：不得"默认路由"，必须列出 4 个子 skill 的能力让用户选择。

```
用户：我有个测试相关的问题

testing-bundle:
  → 意图判断：不明确
  → 追问用户：
    "请告诉我您需要哪类帮助：
     A. 项目级测试策略（test-strategy-engineer）
     B. 生成测试用例（test-case-engineer）
     C. 性能测试方案/瓶颈定位（performance-test-engineer）
     D. 分析 Bug 根因（bug-analyzer）"
```

### 示例 5：测试策略（自动路由到 strategy）

```
用户：我们要启动一个新项目的测试，需要制定测试策略，包括风险矩阵和测试分层

testing-bundle:
  → 意图判断：项目级测试策略（关键词：测试策略、风险矩阵、测试分层）
  → 路由到 test-strategy-engineer
  → 执行五阶段流程：项目特征→风险矩阵→分层→CHECKPOINT→范围准入准出
  → 输出测试策略报告
```

### 示例 6：性能测试方案（自动路由到 performance）

```
用户：我们的支付系统要做性能测试，预期峰值 5000 TPS，关注 P99 响应时间

testing-bundle:
  → 意图判断：性能测试方案设计（关键词：性能测试、TPS、响应时间）
  → 路由到 performance-test-engineer
  → 执行阶段 1-2：性能需求理解 + 测试场景设计

🔴 CHECKPOINT · performance 阶段 2 后：性能测试方案必须展示给用户确认，确认后进入阶段 3（若需瓶颈定位）。

  → 输出性能测试方案（负载模型 + 场景 + 指标阈值）
```

### 示例 7：策略 + 用例协同（链 2 协同）

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

## 快速上手

1. 确认已安装 4 个子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer）
2. 用户提出测试相关请求时，testing-bundle 自动触发
3. bundle 按 4-way 路由决策表判断意图并路由到对应子 skill
4. 混合意图按对应链路执行，转交点 🔴 CHECKPOINT
5. 子 skill 执行具体任务并输出结果

---

**版本历史**：
- v1.0.0: 初始版本，2-skill 路由（case-engineer + bug-analyzer）
- v2.0.0: 扩展为 4-skill 路由（+ strategy + performance），breaking change
