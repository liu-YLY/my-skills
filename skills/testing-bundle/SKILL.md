---
name: testing-bundle
version: 1.0.0
description: >-
  Use when user needs any testing capability — generating test cases, reviewing test cases,
  designing test strategies, OR analyzing bug root causes, reproducing defects.
  Triggers on: 测试、测试用例、测试点、用例评审、测试策略、需求分析、Bug分析、根因、缺陷定位、复现、5 Whys.
  This is a bundle entry that routes to test-case-engineer (case generation) or bug-analyzer (root cause analysis).
keywords:
  - 测试
  - 测试用例
  - Bug分析
  - 根因分析
  - 测试bundle
---

# Testing Bundle

测试能力 bundle 入口：统一路由到 `test-case-engineer`（正向用例生成）或 `bug-analyzer`（逆向根因分析）。

## 适用范围

**适用**：任何测试相关请求（用例生成 / 用例评审 / 测试策略 / Bug 根因分析 / 缺陷定位 / 防御性用例反推）

**不适用**：非测试领域（文档撰写、代码风格、其他 skill 范畴）

## 路由规则

收到用户请求后，按以下规则路由到子 skill：

```
┌─────────────────────────────────────┐
│ 用户请求                             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 意图判断                             │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────┐
│ 正向生成    │  │ 逆向分析    │
└──────┬──────┘  └──────┬──────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│ test-case-  │  │ bug-        │
│ engineer    │  │ analyzer    │
└─────────────┘  └─────────────┘
```

### 路由决策表

| 用户意图关键词 | 路由到 | 说明 |
|---------------|--------|------|
| 测试用例、编写用例、生成用例、测试点、需求分析、测试策略、用例评审、测试分层 | **test-case-engineer** | 正向用例生成 |
| Bug分析、根因、缺陷定位、复现、5 Whys、鱼骨图、防御性用例反推 | **bug-analyzer** | 逆向根因分析 |
| 混合意图（如"分析这个 Bug 并补充防御性用例"） | **bug-analyzer 优先** | bug-analyzer 完成后转交 test-case-engineer 生成完整用例 |
| 意图不明确 | **追问用户** | 列出两个子 skill 的能力，让用户选择 |

### 混合意图的处理流程

当用户请求同时涉及"分析"和"生成"时（如"分析这个重复扣款 Bug 并补充测试用例"）：

```
步骤 1: 路由到 bug-analyzer 执行根因分析
        ↓
步骤 2: bug-analyzer 输出防御性测试点清单
        ↓
步骤 3: 转交 test-case-engineer 基于防御性测试点清单生成完整用例
        ↓
步骤 4: 输出最终报告（根因分析 + 完整测试用例）
```

## 子 skill 协同

本 bundle 包含两个子 skill，各自独立可用，也可通过 bundle 统一调用：

| 子 skill | 职责 | 核心工作流 | 独立可用 |
|---------|------|----------|---------|
| [test-case-engineer](../test-case-engineer/SKILL.md) | 正向用例生成（需求 → 测试用例） | 四阶段：理解需求 → 提取测试点 → 编写用例 → 自检补全 | ✅ 是 |
| [bug-analyzer](../bug-analyzer/SKILL.md) | 逆向根因分析（Bug → 修复建议） | 五步定位法：复现 → 隔离 → 定位 → 验证 → 报告 | ⚠️ 依赖 test-case-engineer 的 bug-patterns.md |

### 知识库共享

`bug-patterns.md` 主归属 test-case-engineer，bug-analyzer 通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用。

**依赖说明**：bug-analyzer 单独安装时，步骤 2/3 的"对照缺陷模式库"能力会降级（仍有通用模式兜底，但无法查阅完整缺陷模式库）。建议通过本 bundle 整体安装。

## 安装方式

### 方式 1：整体安装（推荐）

安装 `testing-bundle` + `test-case-engineer` + `bug-analyzer` 三个 skill，获得完整测试能力。

### 方式 2：按需安装

- 只需用例生成 → 安装 `test-case-engineer`
- 只需 Bug 分析 → 安装 `bug-analyzer`（注意：缺陷模式库引用会降级）
- 两者都需要 → 安装 `testing-bundle` + 两个子 skill

## 使用示例

### 示例 1：正向用例生成（自动路由）

```
用户：我有一个用户登录功能需要测试，需求是手机号+验证码登录...

testing-bundle:
  → 意图判断：测试用例生成
  → 路由到 test-case-engineer
  → 执行四阶段流程
  → 输出测试用例
```

### 示例 2：Bug 根因分析（自动路由）

```
用户：线上出现重复扣款 Bug，用户反馈偶发，帮我分析根因

testing-bundle:
  → 意图判断：Bug 根因分析
  → 路由到 bug-analyzer
  → 执行五步定位法
  → 输出根因分析报告 + 防御性测试点清单
```

### 示例 3：混合意图（协同执行）

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

🔴 **CHECKPOINT · 意图不明确时强制追问**：不得"默认路由"，必须列出两个子 skill 的能力让用户选择。

```
用户：我有个测试相关的问题

testing-bundle:
  → 意图判断：不明确
  → 追问用户：
    "请告诉我您需要哪类帮助：
     A. 生成测试用例（test-case-engineer）
     B. 分析 Bug 根因（bug-analyzer）"
```

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| 意图判断不明确（用户请求含"测试"但未指明生成/分析） | 追问用户：列出两个子 skill 的能力让用户选择（🔴 CHECKPOINT） | 默认路由到 test-case-engineer（覆盖面更广），并在输出首行标注「已默认路由到用例生成，如需 Bug 分析请说明」 |
| 混合意图判定争议（如"防御性用例反推"既属 bug-analyzer 又与 test-case-engineer 边界模糊） | 优先路由到 bug-analyzer（根因分析是前置），完成后转交 test-case-engineer 生成完整用例 | 若用户明确只需用例不需根因分析，直接路由到 test-case-engineer |
| 子 skill 未安装（路由目标 skill 不存在） | 检测到子 skill 不可用，提示用户安装对应 skill，并给出安装命令 | 标注「子 skill 不可用」，输出 bundle 层能提供的方向性建议（如"建议按五步定位法分析根因"） |
| 混合意图协同失败（bug-analyzer 完成但 test-case-engineer 不可用） | 输出 bug-analyzer 的防御性测试点清单，提示用户手动转交 test-case-engineer 或自行编写用例 | 标注「协同中断」，仅输出根因分析报告，防御性测试点清单作为附录 |
| 子 skill 执行失败（路由后子 skill 内部错误） | 捕获子 skill 错误信息，回退到 bundle 层向用户报告失败原因 | 建议用户直接调用子 skill 重试，或降级为 bundle 层方向性指导 |
| 上下文传递丢失（路由后子 skill 未收到原始请求） | 在路由调用时显式传递：用户原始请求 + 已收集上下文 + 已完成步骤摘要 | 标注「上下文不完整」，要求子 skill 主动向用户确认缺失信息 |

## 反例与黑名单

### 路由反模式

| 反模式 | 为什么不要做 | 替代做法 |
|--------|------------|---------|
| 不判断意图直接调用某个子 skill | 跳过路由会导致用户请求被错误 skill 处理，违反 bundle 职责 | 必须按路由决策表判断意图，意图不明确时追问用户（🔴 CHECKPOINT） |
| 在 bundle 层重复实现子 skill 的能力 | 破坏职责边界，导致内容冗余和维护成本翻倍 | bundle 只做路由，具体能力由子 skill 承载 |
| 路由后不传递上下文 | 用户需重新描述需求，体验差且信息丢失 | 路由时显式传递：原始请求 + 已收集上下文 + 已完成步骤摘要 |
| 混合意图不按"先分析后生成"顺序 | 跳过根因分析直接生成用例，用例缺乏针对性 | 先 bug-analyzer 输出防御性测试点，🔴 CHECKPOINT 确认后转交 test-case-engineer |
| 混合意图协同无用户确认点 | 用户无法终止流程或修改防御性测试点清单 | bug-analyzer 完成后必须 🔴 CHECKPOINT，用户确认后才转交 test-case-engineer |

### 安装反模式

| 反模式 | 为什么不要做 | 替代做法 |
|--------|------------|---------|
| 只装 bundle 不装子 skill | bundle 无法独立完成任何任务，所有请求都会失败 | 整体安装 testing-bundle + test-case-engineer + bug-analyzer 三个 skill |
| bug-analyzer 单独安装不告知降级 | 用户不知缺陷模式库引用失效，根因分析能力打折 | 安装时显式提示「缺陷模式库会降级，建议同时安装 test-case-engineer」 |

## 约束规则

1. **本 bundle 只做路由，不实现具体能力** — 所有测试能力由子 skill 承载
2. **路由必须基于显式意图判断** — 不得"默认路由"或"随机路由"
3. **混合意图遵循"先分析后生成"顺序** — bug-analyzer 先输出防御性测试点，再由 test-case-engineer 生成用例
4. **上下文必须完整传递** — 路由时需携带用户原始请求和已收集的上下文
5. **子 skill 独立可用** — bundle 不是子 skill 的前置依赖，用户可绕过 bundle 直接调用子 skill

## 快速上手

1. 确认已安装 `test-case-engineer` 和 `bug-analyzer` 子 skill
2. 用户提出测试相关请求时，testing-bundle 自动触发
3. bundle 判断意图并路由到对应子 skill
4. 子 skill 执行具体任务并输出结果

---

**版本历史**：
- v1.0.0: 初始版本，作为 test-case-engineer + bug-analyzer 的 bundle 入口
