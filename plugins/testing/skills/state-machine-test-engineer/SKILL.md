---
name: state-machine-test-engineer
version: 1.7.6
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

状态机驱动的状态型需求测试 skill：基于 MAE（主流程/替代流程/异常流程）+ State Machine 方法论，为状态型业务对象（订单/审批/工单/会员等）构建状态机模型并穷举 10 类测试场景。

> **MCP 状态**：协议层已有真实调用回归；宿主须暴露兼容工具才可用增强模式。`build_state_machine` 为确定性实现（模板加载，不内置 LLM）。未安装/失败时自动降级为独立模式（首行标 `⚠ 独立模式（未校验）`）。

## 适用范围

**适用**：对象有明确状态流转（订单/审批/工单/会员等），涉及状态转换、终态吸收、非法跳转、幂等、并发、消息乱序；PRD 描述「对象处于什么状态、允许什么变化、哪些操作必须被拒绝」。

**不适用**：通用用例生成 → test-case-engineer；性能 → performance-test-engineer；Bug 根因 → bug-analyzer；项目级策略 → test-strategy-engineer。

## 核心理念

状态机不是「多补几个测试点」，而是把 PRD 的「用户做什么」重构成「对象处于什么状态、允许什么变化」。本 skill **只输出场景清单**，不输出用例步骤；步骤由 test-case-engineer 基于清单生成（testing-bundle 链 5）。

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
| **增强模式** | MCP 工具已暴露且参数 Schema 兼容 | skill 自身推理 + 调用 MCP 做校验/穷举/可视化复核 | `✓ MCP 增强模式` |
| **独立模式** | MCP 未安装 | skill 纯 LLM 推理执行全流程 | `⚠ 独立模式（未校验）` |
| **降级模式** | MCP 调用失败 | 自动回退到独立模式，记录失败原因 | `⚠ 降级模式（MCP 失败：原因）` |

> **可用性**：以宿主工具和参数 Schema 为准；源码回归不等于当前宿主已连接。

**关键原则**：
- skill 是主，MCP 是复核器；MCP 失败只追加警告，不影响输出
- 输出格式跨模式一致，下游无需感知上游模式
- 配置可选，零配置也能用

MCP 配置方式见 [integrations/quickstart.md](integrations/quickstart.md)。

## 核心数据契约

模型 Schema 见 [state-modeling.md](knowledge/state-modeling.md)，场景完整 Schema 见 [scenario-types.md](knowledge/scenario-types.md)。入口只保留跨阶段稳定字段：

- 状态模型：`meta / states / transitions / forbidden`；transition/forbidden 有稳定 `id`，每条带 `evidence_type` 与 `source`。
- 合法场景带 `transition_id`、`guard_conditions`；非法场景带 `forbidden_id`、`attempted_target_state`。
- 场景至少含 `id / title / current_state / trigger_event / expected_target_state / risk_type / evidence_type / source`；无法唯一匹配的进 `unmatched_scenarios`。
- 下游只消费场景契约，不依赖 MCP 是否启用。

## 知识库

| 文件 | 何时查阅 |
|------|---------|
| [state-machine-core.md](state-machine-core.md) | **始终必读**（五阶段核心流程） |
| [knowledge/state-modeling.md](knowledge/state-modeling.md) | **阶段 2 建模** |
| [knowledge/completeness-check.md](knowledge/completeness-check.md) | **阶段 3 完整性检查**；不在阶段 2 预读 |
| [knowledge/scenario-types.md](knowledge/scenario-types.md) | **阶段 4 场景穷举**；不在阶段 2/3 预读 |
| [knowledge/anti-patterns.md](knowledge/anti-patterns.md) | **输出前自检** |
| [knowledge/industry-templates/](knowledge/industry-templates/) | **仅用户指定行业对象时读**（订单退款/审批流/会员/工单，按需加载对应模板） |
| [knowledge/products/](knowledge/products/) | **仅产品可识别且知识文件存在时读**（产品专项知识） |
| [knowledge/usage-examples.md](knowledge/usage-examples.md) | **仅用户想看演示对话或首次使用时读**（3 个使用示例 + 快速上手） |
| [knowledge/mcp-enhancement.md](knowledge/mcp-enhancement.md) | **宿主暴露 MCP 工具或用户要求增强时读**（探测、增强/独立/降级模式细则） |
| [integrations/quickstart.md](integrations/quickstart.md) | **仅用户要求安装/配置 MCP 时读**（MCP 配置、工具注册与兼容性核对） |

### 阶段读取矩阵

| 阶段 | 首轮可读取 | 延迟读取（进入对应阶段后） |
|------|-----------|--------------------------|
| 阶段 1 需求识别 | 入口（本文件）+ core.md 阶段 1 | — |
| 阶段 2 状态机建模 | state-modeling.md（建模方法论 + 最小 Schema + 命名规则 + 依据类型规则） | — |
| 🔴 CHECKPOINT 模型确认后 | — | completeness-check.md（完整性检查规则） |
| 阶段 4 场景穷举 | — | scenario-types.md（10 类场景细则） |
| 输出前自检 | — | anti-patterns.md（反模式黑名单） |
| 用户指定行业 | — | industry-templates/{对应行业}.md |
| 宿主已暴露 MCP | — | mcp-enhancement.md（增强/独立/降级模式细则） |
| 用户要求 MCP | — | integrations/quickstart.md |

> **阶段隔离**：阶段 2 不预读完整性检查与场景穷举细则；CHECKPOINT 前不加载后续资料；MCP 配置仅在用户要求时读。

## 反模式黑名单

完整清单见 [knowledge/anti-patterns.md](knowledge/anti-patterns.md)。入口只保留 3 条硬禁令：

1. 不把「页面提示/请求受理」等同于「业务状态/处理完成」。
2. PRD 缺权限、异常、恢复路径时标「待确认」，不脑补。
3. 只输出场景清单，不输出用例步骤；状态用名词，事件用动词。

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 需求文本无状态信号 | 询问是否继续/转 test-case-engineer | 标注「非状态型需求」并转交 |
| 建模矛盾 | 标「待确认」，不强行消解 | 列矛盾点要求用户裁定（CHECKPOINT） |
| 完整性检查 fail | 修正有依据的结构问题 | 暂停依赖未决规则的场景，先交付缺口 |
| MCP 探测失败/超时/冲突 | 降级或标「待确认」 | 输出首行标 `⚠ 独立模式` / `⚠ 降级模式（原因）` |
| 转交 test-case-engineer 失败 | 保留场景清单独立输出 | 标注「协同中断」 |

## 约束规则

1. **场景清单是契约**：只输出场景级，不输出用例步骤。
2. **依据类型强制标注**：每条 transition 和场景标 `需求明确/合理推理/待确认`。
3. **歧义暴露而非补齐**：缺权限/异常/恢复路径时输出「待确认」节点。
4. **完整性检查独立成阶段**：不混在建模里；skill 是主，MCP 仅复核。
5. **状态用名词，事件用动词**；输出格式跨模式一致。

## 使用示例

见 [knowledge/usage-examples.md](knowledge/usage-examples.md)（按需）。

---

版本和人类使用说明见 [README.md](README.md)；MCP 实现边界见 [state-machine-testing-mcp](https://github.com/liu-YLY/my-skills/blob/main/plugins/testing/mcp-servers/state-machine-testing/README.md)。
