---
name: state-machine-test-engineer
version: 1.0.0
description: >-
  Use when user needs state-machine-driven testing for stateful business objects
  (orders, approvals, tickets, membership, etc.). Triggers on: 状态机、状态流转、状态转换、
  生命周期、非法跳转、幂等、并发冲突、消息乱序、状态回退、幽灵状态、终态吸收.
  Builds a state machine model from requirements, enumerates 10 types of test scenarios
  (legal/illegal transitions, idempotency, concurrency, message reorder, timeout retry,
  data consistency, access control, failure recovery), and outputs a scenario list with
  evidence-type annotations (explicit/inferred/pending). Optionally enhances with
  state-machine-testing-mcp Server for schema validation and Mermaid visualization.
keywords:
  - 状态机测试
  - 状态流转
  - 生命周期测试
  - 状态转换
  - 非法跳转
  - 幂等测试
  - 并发冲突测试
  - MAE
  - 状态网络穷举
integrations:
  mcp_servers:
    - state-machine-testing
---

# State Machine Test Engineer

状态机驱动的状态型需求测试 skill v1.0.0：基于 MAE（主流程/替代流程/异常流程）+ State Machine 方法论，为状态型业务对象（订单/审批/工单/会员等）构建状态机模型并穷举 10 类测试场景。

## 适用范围

**适用**：状态型需求测试
- 业务对象有明确的状态流转（订单生命周期、审批流、工单状态、会员等级等）
- 涉及状态转换、终态吸收、非法跳转、幂等、并发冲突、消息乱序等场景
- PRD 描述了"对象处于什么状态、允许什么变化、哪些操作必须被拒绝"

**不适用**：
- 通用功能用例生成（无状态信号）→ 转交 `test-case-engineer`
- 性能测试 → 转交 `performance-test-engineer`
- Bug 根因分析 → 转交 `bug-analyzer`
- 项目级测试策略 → 转交 `test-strategy-engineer`

## 核心理念

> 状态机不是给 AI "多补几个测试点"，而是给 AI 一套**理解业务行为的结构**。

PRD 通常只描述"用户做什么"，没有显性表达"对象处于什么状态、允许什么变化、哪些操作必须被拒绝"。本 skill 用状态机作为业务建模语言，让测试设计从"功能点罗列"升级为"状态网络穷举"。

**与 test-case-engineer 的边界**：
- 本 skill **只输出场景清单**（场景级，含依据类型标注），**不输出用例步骤**
- 用例步骤由 test-case-engineer 基于场景清单生成（通过 testing-bundle 链 5 协同）

## 工作流（五阶段）

```
阶段 1: 状态型需求识别
  → 识别业务对象（订单/审批/工单/会员等）
  → 识别参与者（人/系统/外部/定时器/管理员）
  → 标记歧义为"待确认"（不补齐）
  → 输出：状态型需求摘要 + 业务对象清单
  ↓
阶段 2: 状态机建模
  → 抽取状态（只保留名词，避免动词状态）
  → 定义转换：FROM --(事件 [守卫])--> TO {副作用}
  → 定义不变量与终态（终态吸收规则）
  → 定义禁止转换
  → 输出：状态机模型（YAML/JSON 结构）
  ↓
🔴 CHECKPOINT · 状态机模型展示给用户确认（可修改/补充/终止）
  ↓
阶段 3: 完整性检查（9 项，与 MCP validate_state_machine 对齐）
  → 每个状态有明确含义？
  → 每个状态有进入条件（除初始态）？
  → 每个非终态有退出路径？
  → 终态是否真的不可变化（无出边）？
  → 禁止转换是否明确无遗漏？
  → 状态变化有副作用定义？
  → 依据类型已标注（无遗漏）？
  → 无悬挂状态（unreachable）？
  → 无死锁状态（非终态但无出边）？
  → 输出：完整性检查报告（标记缺口）
  ↓
阶段 4: 10 类场景穷举
  → 对每条 transition 生成：
    1. 合法转换（legal_transition）
    2. 非法转换（illegal_transition）
    3. 条件不满足（guard_violation）
    4. 重复事件与幂等（idempotency）
    5. 并发事件（concurrency）
    6. 消息乱序（message_reorder）
    7. 超时与重试（timeout_retry）
    8. 转换后数据一致性（data_consistency）
    9. 权限控制（access_control）
    10. 失败后恢复路径（failure_recovery）
  → 每场景标注依据类型（需求明确/合理推理/待确认）
  → 输出：场景清单（场景级，不出用例步骤）
  ↓
阶段 5: MCP 增强（可选）
  → 检测 MCP Server 可用性
  → 可用：调用 validate_state_machine 校验 + generate_scenarios 复核 + export_artifacts 导出
  → 不可用：降级为纯 LLM 推理（在输出首行标注「⚠ 独立模式（未校验）」）
  → 输出：最终状态机模型 + 场景清单（含校验状态标记）
```

详细流程见 [state-machine-core.md](state-machine-core.md)。

## 三种运行模式

| 模式 | 触发条件 | 行为 | 输出标记 |
|---|---|---|---|
| **增强模式** | MCP 可用 | skill 自身推理 + 调用 MCP 做校验/穷举/可视化复核 | `✓ MCP 增强模式` |
| **独立模式** | MCP 未安装 | skill 纯 LLM 推理执行全流程 | `⚠ 独立模式（未校验）` |
| **降级模式** | MCP 调用失败 | 自动回退到独立模式，记录失败原因 | `⚠ 降级模式（MCP 失败：原因）` |

**关键原则**：
- skill 始终是主，MCP 是复核器（MCP 校验失败不影响 skill 输出，只追加警告）
- 输出格式跨模式一致，下游 test-case-engineer 无需感知上游模式
- 配置可选，零配置也能用 skill

MCP 配置方式见 [integrations/quickstart.md](integrations/quickstart.md)。

## 核心数据结构

### 状态机模型 Schema

```yaml
state_machine:
  meta:
    object: Order                      # 业务对象
    version: 1.0
    source: 需求文档/PRD/口头描述
    confidence: high/medium/low
  states:
    - name: 待支付
      meaning: 订单已创建未支付
      is_terminal: false
      entry_events: [订单创建]
      invariants: [订单金额不可修改]
    - name: 退款成功
      is_terminal: true
      invariants: [退款金额不可再修改]
  transitions:
    - from: 待支付
      to: 已支付
      event: 支付成功回调
      guards: [订单有效, 金额一致, 回调可信]
      side_effects: [生成支付记录, 触发履约]
      evidence_type: 需求明确           # 需求明确/合理推理/待确认
      source: PRD §3.2
  forbidden:
    - from: 退款成功
      to: 任何状态
      reason: 终态吸收
```

### 场景清单 Schema（转交 test-case-engineer 的契约）

```yaml
scenarios:
  - id: SM-001
    title: 已取消订单尝试支付
    current_state: 已取消
    trigger_event: 支付成功回调
    precondition: 订单已取消
    expected_target_state: 已取消（保持不变）
    forbidden_states: [已支付]
    risk_type: illegal_transition
    related_objects: [支付记录, 订单日志]
    evidence_type: 需求明确
    source: PRD §3.1 + 状态机 forbidden 规则
    notes: 需验证后端拒绝 + 前端按钮置灰
```

## 知识库

```
knowledge/
├── state-modeling.md             # 状态机建模方法论（6 要素 + MAE + 不变量 + 终态）
├── scenario-types.md             # 10 类场景穷举规则与示例
├── completeness-check.md         # 完整性检查清单（9 项，与 MCP 对齐）
├── anti-patterns.md              # 反模式黑名单
├── industry-templates/           # 行业状态机模板
│   ├── order-refund.md           # 订单退款（文章案例）
│   ├── approval-flow.md          # 审批流
│   ├── membership.md             # 会员状态
│   └── ticket.md                 # 工单状态
└── products/                     # 产品专项知识
    ├── README.md
    └── products-template.md
```

## 反模式黑名单

> 以下反模式会导致状态机测试质量下降，必须避免。详见 [knowledge/anti-patterns.md](knowledge/anti-patterns.md)。

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|---|---|---|
| 1 | 把"页面提示"等同于"业务状态" | 页面提示 ≠ 后台真实状态，混淆会导致漏测真实状态变化 | 状态/事件/结果必须分层描述，区分"接口调用成功""申请已受理""业务最终成功" |
| 2 | 把"请求受理"等同于"处理完成" | 受理只是提交结果，不代表业务完成（如退款申请成功 ≠ 退款成功） | 转换必须明确 FROM → TO，不能跳过中间态 |
| 3 | PRD 缺权限/异常路径时自行脑补 | LLM 脑补管理员逻辑会引入幻觉，与真实需求不符 | 必须输出"待确认"节点，暴露给用户裁定 |
| 4 | 不标注依据类型 | 无法区分哪些是 PRD 明确、哪些是推理，评审无法聚焦 | 每条 transition 和场景必须标 `需求明确/合理推理/待确认` |
| 5 | 把状态用动词描述（如"支付中"） | 动词状态边界模糊，易与事件混淆 | 状态用名词（如"待支付"/"已支付"），事件用动词 |
| 6 | 不定义禁止转换 | 只测合法路径会漏掉非法跳转的高风险场景 | 每个状态必须明确"禁止进入哪些状态"及理由 |
| 7 | 把"申请成功"作为终态 | 申请成功只是提交结果，业务可能仍在中态（如退款中） | 终态必须是业务最终态（退款成功/退款失败），不是受理态 |
| 8 | 直接输出用例步骤 | 与 test-case-engineer 职责重叠，导致用例重复 | 只输出场景清单，用例步骤交给 test-case-engineer（链 5 协同） |

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 需求文本无状态信号 | 提示并询问是否继续/转 test-case-engineer | 标注「非状态型需求」，建议转 test-case-engineer |
| 状态机建模出现矛盾 | 标"待确认"暴露给用户，不强行消解 | 列出矛盾点，要求用户裁定（🔴 CHECKPOINT） |
| 完整性检查失败（缺口/死锁） | 触发 CHECKPOINT，不进入场景穷举 | 展示缺口报告，等用户补充后再继续 |
| MCP 探测失败 | 静默降级到独立模式 | 输出首行标 `⚠ 独立模式` |
| MCP 调用超时（>10s） | 单次重试，仍失败则降级 | 输出首行标 `⚠ 降级模式（超时）` |
| MCP 返回结果与 skill 严重冲突 | 不自动取舍，标"待确认"交给用户 | 列出差异，要求用户裁定 |
| 转交 test-case-engineer 失败 | 保留场景清单独立输出，提示用户手动衔接 | 标注「协同中断」，仅输出状态机模型 + 场景清单 |

## 约束规则

1. **场景清单是契约** — 只输出场景级，不输出用例步骤，避免与 test-case-engineer 职责重叠
2. **依据类型强制标注** — 每条 transition 和场景必须标 `需求明确/合理推理/待确认`，防幻觉
3. **歧义暴露而非补齐** — PRD 缺权限/异常路径时必须输出"待确认"节点，禁止 LLM 自行脑补
4. **完整性检查独立成阶段** — 不混在建模里，强制人工审视缺口（终态吸收/退出路径/副作用）
5. **skill 始终是主，MCP 是辅** — MCP 校验失败不影响 skill 输出，只追加警告
6. **输出格式跨模式一致** — 下游 test-case-engineer 无需感知上游模式
7. **状态用名词，事件用动词** — 避免状态与事件混淆

## 使用示例

### 示例 1：订单退款状态机建模（文章案例）

```
用户：订单退款流程要做测试，订单状态包括待支付/已支付/已取消/退款中/退款成功/退款失败

state-machine-test-engineer:
  → 阶段 1：识别业务对象 Order，识别参与者（用户/支付渠道/管理员/定时器）
  → 阶段 2：构建 6 状态状态机
    - 状态：待支付/已支付/已取消/退款中/退款成功/退款失败
    - 转换：待支付→已支付（支付成功回调）/待支付→已取消（用户取消/超时关闭）等
    - 禁止：已取消→已支付（已取消订单不可支付）、退款成功→任何状态（终态吸收）
  → 🔴 CHECKPOINT 展示状态机模型给用户确认
  → 阶段 3：完整性检查（标注"退款失败后恢复路径 PRD 未说明"为缺口）
  → 阶段 4：10 类场景穷举，每场景标注依据类型
    - 已取消订单尝试支付 → illegal_transition（依据：需求明确）
    - 支付回调重复到达 → idempotency（依据：合理推理）
    - 取消与支付并发 → concurrency（依据：合理推理）
    - 退款失败后状态恢复 → failure_recovery（依据：待确认，PRD 未说明）
  → 输出：状态机模型 + 场景清单（含依据类型标注）
```

### 示例 2：MCP 增强模式

```
用户：（已配置 state-machine-testing-mcp）审批流状态机测试

state-machine-test-engineer:
  → 阶段 1-2：构建审批流状态机（待审批/审批中/已通过/已驳回/已撤回）
  → 阶段 3：调用 MCP validate_state_machine 校验
    → MCP 返回 ValidationReport（标注"已撤回后是否能再发起"为缺口）
    → skill 把缺口追加到完整性检查报告
  → 阶段 4：skill 穷举场景 + 调用 MCP generate_scenarios 交叉复核
    → 对比两份清单，差异项标"待确认"
  → 阶段 5：调用 MCP export_artifacts 生成 Mermaid 状态图
    → 调用 MCP check_coverage 输出覆盖度报告
  → 输出（首行标 `✓ MCP 增强模式`）：状态机模型 + 场景清单 + Mermaid 图 + 覆盖度报告
```

### 示例 3：转交 test-case-engineer（链 5 协同）

```
用户：为订单退款流程设计状态机测试场景，并生成完整测试用例

testing-bundle → state-machine-test-engineer:
  → 执行五阶段，输出状态机模型 + 场景清单
  → 🔴 CHECKPOINT 用户确认状态机模型与场景清单

用户确认后 → testing-bundle → test-case-engineer:
  → 基于场景清单生成完整用例（每场景落实为可执行步骤）
  → 输出：状态机模型 + 场景清单 + 完整测试用例
```

## 快速上手

1. 确认已安装本 skill（独立可用）
2. （可选）安装配套 MCP Server 进入增强模式，配置见 [integrations/quickstart.md](integrations/quickstart.md)
3. 通过 testing-bundle 路由，或直接调用本 skill
4. 提供状态型需求（含业务对象、状态名、状态转换描述）
5. 五阶段流程自动执行，CHECKPOINT 处确认状态机模型
6. 输出场景清单，可手动转交 test-case-engineer 或通过链 5 自动协同

---

**相关文档**：
- [README.md](README.md) - 简介与使用指南
- [state-machine-core.md](state-machine-core.md) - 核心流程详述
- [integrations/quickstart.md](integrations/quickstart.md) - MCP 配置说明
- [设计文档](../../../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md) - 完整设计 spec
- [testing-bundle](../testing-bundle/SKILL.md) - bundle 入口（5-way 路由）
- [test-case-engineer](../test-case-engineer/SKILL.md) - 下游协同（链 5）
- [state-machine-testing-mcp](../../mcp-servers/state-machine-testing/README.md) - 配套 MCP Server

**版本历史**：
- v1.0.0: 初始版本，五阶段流程 + 10 类场景穷举 + MCP 可选增强
