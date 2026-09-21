---
name: state-machine-test-engineer
version: 1.2.1
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

状态机驱动的状态型需求测试 skill v1.2.1：基于 MAE（主流程/替代流程/异常流程）+ State Machine 方法论，为状态型业务对象（订单/审批/工单/会员等）构建状态机模型并穷举 10 类测试场景。

> ✅ **MCP Server 状态说明**：配套的 `state-machine-testing-mcp` 已升级至 **v0.3.0**，MCP 协议层（stdio + streamable-http）和真实工具调用已通过端到端测试，**增强模式可用**。`build_state_machine` 为确定性实现（行业模板加载，不内置 LLM）。未安装或调用失败时 skill 仍自动降级为独立模式（输出首行标 `⚠ 独立模式（未校验）`）。

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

始终先读 [state-machine-core.md](state-machine-core.md)，再按阶段延迟加载知识文件：

| 阶段 | 输入 | 必须输出 | 门禁 |
|------|------|----------|------|
| 1. 状态型需求识别 | 用户需求 | 对象、参与者、明确事实、歧义清单 | 缺失规则标「待确认」，不补齐 |
| 2. 状态机建模 | 阶段 1 结果 | 状态、转换、守卫、副作用、不变量、禁止转换 | 状态用名词、事件用动词；每条规则标依据类型 |
| 模型自检 | 候选模型 | 模型摘要和未决事项 | 已授权的只读分析继续；结论性矛盾进入 🔴 CHECKPOINT |
| 3. 完整性检查 | 候选模型 | C0 结构检查 + 9 项业务检查及缺口 | 需求完整性不能由结构校验代替 |
| 4. 场景穷举 | 已检查模型 | 10 类场景清单，不输出用例步骤 | 每类场景标依据类型；未知目标保持待确认 |
| 5. MCP 增强 | 模型与场景 | 校验状态、差异和最终产物 | MCP 仅复核；不可用或失败必须显式降级 |

## 三种运行模式

| 模式 | 触发条件 | 行为 | 输出标记 |
|---|---|---|---|
| **增强模式** | MCP 可用（v0.3.0+，已联调验证） | skill 自身推理 + 调用 MCP 做校验/穷举/可视化复核 | `✓ MCP 增强模式` |
| **独立模式** | MCP 未安装 | skill 纯 LLM 推理执行全流程 | `⚠ 独立模式（未校验）` |
| **降级模式** | MCP 调用失败 | 自动回退到独立模式，记录失败原因 | `⚠ 降级模式（MCP 失败：原因）` |

> **当前状态（v0.3.0）**：MCP 协议层（stdio + streamable-http）已端到端联调验证，安装 MCP Server 后增强模式可用；未安装时自动以独立模式运行。

**关键原则**：
- skill 始终是主，MCP 是复核器（MCP 校验失败不影响 skill 输出，只追加警告）
- 输出格式跨模式一致，下游 test-case-engineer 无需感知上游模式
- 配置可选，零配置也能用 skill

MCP 配置方式见 [integrations/quickstart.md](integrations/quickstart.md)。

## 核心数据契约

完整 Schema 与示例见 [state-machine-core.md](state-machine-core.md)。入口只保留跨阶段和下游必须稳定的字段：

- 状态模型：`meta / states / transitions / forbidden`；transition 与 forbidden 应有稳定 `id`。
- 每条转换与禁止规则必须包含 `evidence_type` 和 `source`；未知业务规则标 `待确认`，不得伪造目标状态。
- 合法场景携带 `transition_id`、`guard_conditions`；非法场景携带 `forbidden_id`、`attempted_target_state`。
- 场景至少包含 `id / title / current_state / trigger_event / expected_target_state / risk_type / evidence_type / source`。
- 引用不能替代目标与守卫匹配；无法唯一匹配的场景进入 `unmatched_scenarios`。
- 下游 test-case-engineer 只消费场景契约，不依赖 MCP 是否启用。

## 知识库

| 文件 | 何时查阅 |
|------|---------|
| [state-machine-core.md](state-machine-core.md) | **始终必读**（五阶段核心流程） |
| [knowledge/state-modeling.md](knowledge/state-modeling.md) | **阶段 2 建模时读**（6 要素 + MAE + 不变量 + 终态方法论） |
| [knowledge/completeness-check.md](knowledge/completeness-check.md) | **阶段 3 完整性检查时读**（9 项检查清单，与 MCP validate 对齐）。不在阶段 2 预读 |
| [knowledge/scenario-types.md](knowledge/scenario-types.md) | **阶段 4 场景穷举时读**（10 类场景细则与示例）。不在阶段 2/3 预读 |
| [knowledge/anti-patterns.md](knowledge/anti-patterns.md) | **输出前自检时读**（反模式黑名单） |
| [knowledge/industry-templates/](knowledge/industry-templates/) | **仅用户指定行业对象时读**（订单退款/审批流/会员/工单，按需加载对应模板） |
| [knowledge/products/](knowledge/products/) | **仅产品可识别且知识文件存在时读**（产品专项知识） |
| [knowledge/usage-examples.md](knowledge/usage-examples.md) | **仅用户想看演示对话或首次使用时读**（3 个使用示例 + 快速上手） |
| [integrations/quickstart.md](integrations/quickstart.md) | **仅用户要求安装/配置 MCP 时读**（MCP 配置说明，v0.3.0 已联调验证，配置后增强模式可用） |

### 阶段读取矩阵

| 阶段 | 首轮可读取 | 延迟读取（进入对应阶段后） |
|------|-----------|--------------------------|
| 阶段 1 需求识别 | 入口（本文件）+ core.md 阶段 1 | — |
| 阶段 2 状态机建模 | state-modeling.md（建模方法论 + 最小 Schema + 命名规则 + 依据类型规则） | — |
| 🔴 CHECKPOINT 模型确认后 | — | completeness-check.md（完整性检查规则） |
| 阶段 4 场景穷举 | — | scenario-types.md（10 类场景细则） |
| 输出前自检 | — | anti-patterns.md（反模式黑名单） |
| 用户指定行业 | — | industry-templates/{对应行业}.md |
| 用户要求 MCP | — | integrations/quickstart.md |

> **阶段隔离原则**：建模阶段（阶段 2）不预读完整性检查规则和场景穷举细则。CHECKPOINT 前的知识资料不得在 CHECKPOINT 前加载。MCP 配置资料仅在用户明确要求时读取。

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
| 完整性检查失败（缺口/死锁） | 修正有依据的结构问题 | 暂停依赖未决规则的场景，先交付缺口和已有结论 |
| MCP 探测失败 | 静默降级到独立模式 | 输出首行标 `⚠ 独立模式` |
| MCP 调用超时（>10s） | 单次重试，仍失败则降级 | 输出首行标 `⚠ 降级模式（超时）` |
| MCP 返回结果与 skill 严重冲突 | 不自动取舍，标"待确认"交给用户 | 列出差异，要求用户裁定 |
| 转交 test-case-engineer 失败 | 保留场景清单独立输出，提示用户手动衔接 | 标注「协同中断」，仅输出状态机模型 + 场景清单 |

## 约束规则

1. **场景清单是契约** — 只输出场景级，不输出用例步骤，避免与 test-case-engineer 职责重叠
2. **依据类型强制标注** — 每条 transition 和场景必须标 `需求明确/合理推理/待确认`；标签不代表依据已核实
3. **歧义暴露而非补齐** — PRD 缺权限/异常路径时必须输出"待确认"节点，禁止 LLM 自行脑补
4. **完整性检查独立成阶段** — 不混在建模里，强制人工审视缺口（终态吸收/退出路径/副作用）
5. **skill 始终是主，MCP 是辅** — MCP 校验失败不影响 skill 输出，只追加警告
6. **输出格式跨模式一致** — 下游 test-case-engineer 无需感知上游模式
7. **状态用名词，事件用动词** — 避免状态与事件混淆

## 使用示例与快速上手

3 个完整演示对话（订单退款建模 / MCP 增强模式 / 链 5 转交 test-case-engineer）与首次使用引导见 [knowledge/usage-examples.md](knowledge/usage-examples.md)（按需加载：仅当用户想看演示或首次安装配置时读取）。

---

版本和人类使用说明见 [README.md](README.md)；MCP 实现边界见 [state-machine-testing-mcp](../../mcp-servers/state-machine-testing/README.md)。
