---
name: testing-bundle
version: 3.1.1
description: >-
  Use when user has mixed, ambiguous, or explicitly routing-required testing requests —
  e.g. "analyze bug AND generate test cases", "design strategy AND generate layered cases",
  "performance test AND diagnose bottleneck", "review AND check coverage gaps",
  or "not sure which testing capability is needed".
  For single-intent requests (test cases only, strategy only, performance only, bug analysis only,
  state-machine only), the corresponding sub-skill handles directly without bundle routing.
  Triggers on: 混合测试意图、模糊测试请求、测试bundle、测试路由、不确定需要哪种测试能力.
  This is a bundle entry that routes to test-strategy-engineer, test-case-engineer,
  performance-test-engineer, bug-analyzer, state-machine-test-engineer, or
  change-impact-analyzer (cooperative skill for chain 6).
keywords:
  - 测试bundle
  - 测试路由
  - 混合测试意图
  - 模糊测试请求
  - 测试能力选择
---

# Testing Bundle

测试能力 bundle 入口 v3.1.1：统一路由到 5 个核心子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer / state-machine-test-engineer），另含第 6 个协同 skill change-impact-analyzer（链 6，随 testing plugin 整体安装获得）。

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
              │   testing-bundle v3.1.1 │  路由层（只路由，不实现能力）
              └───────────┬─────────────┘
                          │ 5-way 意图判断
        ┌─────────┬───────┼───────┬───────────┬──────────────┐
        ▼         ▼       ▼       ▼           ▼
  ┌──────────┐┌─────────┐┌──────┐┌───────────┐┌──────────────┐
  │strategy- ││case-    ││bug-  ││performance││state-machine │
  │engineer  ││engineer ││anlyz ││-engineer  ││-test-engineer│
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
| 变更影响分析、diff 分析、代码改动检查、覆盖缺口、回归风险 **等变更影响信号** | **change-impact-analyzer** | 代码变更影响分析（链 6 协同，亦可单意图路由） |
| 意图不明确 | **追问用户**（🔴 CHECKPOINT） | 列出 6 个子 skill 的能力让用户选择 |

> "等X信号"判定边界：含上述任一关键词，或语义等价表达（如"测试计划"等价"测试策略"、"QPS"等价"吞吐量/TPS"）。边界模糊时按"判定顺序第三步"追问用户。

### 混合意图链

当用户请求同时涉及多个子 skill 时，按以下 7 条链路执行，每条链的转交点都必须设 🔴 CHECKPOINT。

**链路索引**（命中后读取对应链的完整步骤流）：

| 链 | 名称 | 涉及 skill | 触发信号 |
|---|---|---|---|
| 1 | 分析 Bug 并补充用例 | bug-analyzer → test-case-engineer | Bug 分析 + 用例生成 |
| 2 | 制定测试策略并生成分层用例 | test-strategy-engineer → test-case-engineer | 测试策略 + 用例生成 |
| 3 | 做性能测试并分析瓶颈 | performance-test-engineer（内部完成） | 性能测试 + 瓶颈定位 |
| 4 | 性能问题定位到代码缺陷 | performance-test-engineer → bug-analyzer | 性能瓶颈 + 代码缺陷信号 |
| 5 | 状态机建模 + 用例生成 | state-machine-test-engineer → test-case-engineer | 状态机 + 用例生成 |
| 6 | 评审 → 覆盖缺口验证 | test-case-engineer → change-impact-analyzer | 用例评审 + 覆盖缺口/diff 分析 |
| 7 | 评审 → 风险用例根因反推 | test-case-engineer → bug-analyzer | 用例评审 + 根因反推 |

> **按需加载**：每条链的完整步骤流、CHECKPOINT 定义、触发条件与二级判定规则见 [knowledge/mixed-intent-chains.md](knowledge/mixed-intent-chains.md)。仅当判定顺序第一步命中某条链时，才读取该链的详细步骤流。

## 子 skill 协同

本 bundle 包含 5 个核心子 skill + 1 个协同 skill（change-impact-analyzer，链 6 使用），各自独立可用，也可通过 bundle 统一调用：

| 子 skill | 职责 | 核心工作流 | 独立可用 |
|---------|------|----------|---------|
| [test-strategy-engineer](../test-strategy-engineer/SKILL.md) | 项目级测试策略（风险矩阵+分层+准入准出） | 五阶段：项目特征→风险矩阵→分层→CHECKPOINT→范围准入准出→（可选）资源附录 | ✅ 是 |
| [test-case-engineer](../test-case-engineer/SKILL.md) | 功能用例生成（需求→测试用例） | 四阶段：理解需求→提取测试点→编写用例→自检补全 | ✅ 是 |
| [performance-test-engineer](../performance-test-engineer/SKILL.md) | 性能测试方案+瓶颈定位（资源/架构层） | 四阶段：需求理解→场景设计→CHECKPOINT→瓶颈定位→转交判断 | ✅ 是 |
| [bug-analyzer](../bug-analyzer/SKILL.md) | 功能缺陷根因（代码逻辑层） | 五步定位法：复现→隔离→定位→验证→报告 | ⚠️ 依赖 test-case-engineer 的 bug-patterns.md |
| [state-machine-test-engineer](../state-machine-test-engineer/SKILL.md) | 状态机建模+场景穷举（状态型需求） | 五阶段：状态型需求识别→状态机建模→CHECKPOINT→完整性检查→10类场景穷举→（可选）MCP增强 | ✅ 是（MCP 可选增强） |
| [change-impact-analyzer](../change-impact-analyzer/SKILL.md) | 代码变更影响分析（git diff × 用例交叉验证） | 四阶段：收集输入→Diff 解析→交叉分析→生成报告 | ✅ 是 |

### 知识库共享

- `bug-patterns.md` 主归属 test-case-engineer，bug-analyzer 通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用
- strategy/performance/state-machine 不共享知识库（聚焦点不同，共享会引入路由歧义）
- state-machine-test-engineer 可选调用 `state-machine-testing-mcp` Server 做 Schema 校验与可视化（未安装时降级为纯 LLM 推理）。⚠️ 该 MCP 当前为 v0.1.0，协议层注册待 v0.2.0 完成，**增强模式实际不可达**，skill 以独立模式运行（详见 state-machine-test-engineer/SKILL.md 状态说明）
- test-case-engineer 评审模式可选调用 `review-checker-mcp` Server 做 10 维度确定性校验与度量报告（9 维度用例级校验 + 1 维度语义一致性冲突检测，未安装时降级为纯 LLM 推理）

**依赖说明**：
- bug-analyzer 单独安装时，步骤 2/3 的"对照缺陷模式库"能力会降级（仍有通用模式兜底，但无法查阅完整缺陷模式库）。通过本 bundle 整体安装获得完整能力。
- state-machine-test-engineer 单独安装时完全可用；安装配套 MCP Server 后进入"增强模式"，获得 Schema 校验、Mermaid 可视化、覆盖度报告等额外能力。⚠️ 增强模式需等 MCP v0.2.0 协议层注册完成后才可用，当前配置后也无法调用。
- test-case-engineer 评审模式单独可用；安装配套 review-checker MCP Server 后进入"增强模式"，获得 10 维度确定性校验与度量报告（通过率/问题密度/评级 A-D）。

## 安装方式

### 方式 1：整体安装（推荐）

安装 testing plugin，获得 `testing-bundle` + `test-strategy-engineer` + `test-case-engineer` + `performance-test-engineer` + `bug-analyzer` + `state-machine-test-engineer` + `change-impact-analyzer` 共 7 个 skill，获得完整测试能力（含链 6 覆盖缺口验证）。

### 方式 2：按需安装

- 只需项目级策略 → 安装 `test-strategy-engineer`
- 只需用例生成 → 安装 `test-case-engineer`（评审模式可选再装 review-checker MCP Server 进入增强模式）
- 只需性能测试 → 安装 `performance-test-engineer`
- 只需 Bug 分析 → 安装 `bug-analyzer`（缺陷模式库引用会降级）
- 只需状态机测试 → 安装 `state-machine-test-engineer`（可选再装 MCP Server 进入增强模式）
- 只需变更影响分析 → 安装 `change-impact-analyzer`
- 多项需求 → 安装 `testing-bundle` + 对应子 skill

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| 意图判断不明确（用户请求含"测试"但未指明策略/用例/性能/Bug/状态机/变更影响） | 追问用户：列出 6 个子 skill 的能力让用户选择（🔴 CHECKPOINT） | 持续追问，不默认路由。仅当用户明确授权"你来决定"时，可路由到 test-case-engineer，并在输出首行标注「已默认路由到用例生成，如需其他能力请说明」 |
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
| 1 | 只装 bundle 不装子 skill | bundle 无法独立完成任何任务，所有请求都会失败 | 整体安装 testing plugin（含 bundle + 6 个子 skill） |
| 2 | bug-analyzer 单独安装不告知降级 | 用户不知缺陷模式库引用失效，根因分析能力打折 | 安装时显式提示「缺陷模式库会降级，同时安装 test-case-engineer 获得完整能力」 |

## 约束规则

1. **本 bundle 只做路由，不实现具体能力** — 所有测试能力由子 skill 承载
2. **路由必须基于显式意图判断** — 不得"默认路由"或"随机路由"
3. **性能类问题默认路由到 performance，不路由到 bug-analyzer** — 性能问题属资源/架构层，仅当瓶颈指向代码逻辑层时才转交 bug-analyzer
4. **strategy 是并列 peer，不是必经入口** — 大多数具体请求直接路由到对应 skill，仅项目级策略请求路由到 strategy
5. **混合意图遵循"先上游后下游"顺序，转交点必须 🔴 CHECKPOINT** — strategy → case-engineer；performance → bug-analyzer
6. **上下文必须完整传递** — 路由时需携带用户原始请求和已收集的上下文
7. **子 skill 独立可用** — bundle 不是子 skill 的前置依赖，用户可绕过 bundle 直接调用子 skill

## 使用示例与快速上手

8 个典型路由演示对话与首次使用引导见 [knowledge/usage-examples.md](knowledge/usage-examples.md)（按需加载：仅当用户想看演示或首次安装配置时读取）。示例索引：

1. Bug 根因分析 → bug-analyzer；2. Bug+用例（链 1）；3. 意图不明确 → 追问（🔴 CHECKPOINT，规则见路由决策表与失败模式表）；4. 测试策略 → strategy
5. 性能测试方案 → performance；6. 策略+用例（链 2）；7. 状态机建模 → state-machine；8. 状态机+用例（链 5）

---

**版本历史**：
- v1.0.0: 初始版本，2-skill 路由（case-engineer + bug-analyzer）
- v2.0.0: 扩展为 4-skill 路由（+ strategy + performance），breaking change
- v3.0.0: 扩展为 5-skill 路由（+ state-machine-test-engineer），新增链 5（状态机+用例协同），breaking change
- v3.1.0: 新增链 6（评审→覆盖缺口验证，协同外部 change-impact-analyzer）+ 链 7（评审→风险用例根因反推，协同 bug-analyzer），评审模式成为混合意图链起点
- v3.1.1: 声明 test-case-engineer 评审模式可选调用 review-checker MCP Server（与 state-machine MCP 增强对称），未安装时降级为纯 LLM 推理
