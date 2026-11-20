# 10 类场景穷举规则

> **何时阅读**：阶段 4 执行时读。覆盖报告与失败阶段契约见 [coverage-contract.md](coverage-contract.md)（按需）。
> **覆盖范围**：场景契约 / 10 类生成规则 / 适用性 / 去重 / 编号。
> **完整示例**：需要可校验的模型与 10 条场景 YAML 时见 [scenario-examples.md](scenario-examples.md)（按需，MCP 集成测试直接解析）。

## 场景完整契约

每条场景必填 `id/title/current_state/trigger_event/precondition/expected_target_state/risk_type/evidence_type`；`source` 记录需求位置或推理依据。可选字段：`expected_target_state_reason/forbidden_states/related_objects/notes/transition_id/forbidden_id/guard_conditions/attempted_target_state/violated_guard`。

- 目标只填已定义状态名；未知目标统一 `待确认` 并给 `expected_target_state_reason`。
- 合法场景带完整 `guard_conditions` 与 `transition_id`；非法场景带 `forbidden_id` 与具体 `attempted_target_state`。
- 引用只缩小匹配范围，不能绕过目标与守卫匹配；守卫场景保留原转换全部条件，`violated_guard` 只标一个违反项。
- 示例中的业务时间、权限、恢复规则未确认，不充当真实产品需求。

## 10 类总览

| risk_type | 生成依据 | 默认证据 |
|---|---|---|
| legal_transition | 每条 transition 1 个 | 同 transition |
| illegal_transition | 每条 forbidden 1 个；无 forbidden 时对终态生成吸收场景 | 同 forbidden |
| guard_violation | 每条 transition 移除 1 个 guard | 合理推理 |
| idempotency | 涉及外部回调的 transition | 合理推理 |
| concurrency | 同对象同前置状态的可竞争事件 | 合理推理 |
| message_reorder | 涉及异步消息的 transition | 合理推理 |
| timeout_retry | 涉及等待/重试的 transition | 合理推理 |
| data_consistency | side_effects 非空的 transition | 合理推理 |
| access_control | 涉及权限且需求有依据的 transition | 待确认 |
| failure_recovery | 有明确失败能力的 transition | 待确认 |

## 生成规则

### legal_transition

对每条 transition 生成 1 个合法场景，验证 PRD 明确路径。示例：`待支付 + 支付成功回调 → 已支付`，带 `transition_id` 与完整 guards。

### illegal_transition

对每条 forbidden 生成 1 个非法场景，验证被拒绝。示例：`已取消 + 支付成功回调 → 已取消`，带 `forbidden_id` 与 `attempted_target_state: 已支付`。无显式 forbidden 时，对终态自动生成终态吸收场景。

### guard_violation

逐个违反一个 guard，其余 guard 保持满足；只证明对应转换不执行。若同源同事件存在其他分支，字符串守卫无法求解目标，目标标 `待确认` 并给原因；其他分支可能进入同一目标，不能直接把原目标列为禁态。条件联合可满足性未知时说明未验证。

### idempotency

对涉及外部回调的 transition（支付/退款/通知）生成重复触发场景。需求确认事件可能重复或明确要求幂等才生成；回调/通知/消息关键词只是候选，不能证明幂等规则。示例：已支付后第二次支付回调仍为已支付，支付记录不重复。

### concurrency

对同对象同前置状态的可竞争事件生成并发场景。触发源与并发成立条件需核实，不要求必须是「用户操作 + 系统回调」。并发优先级未定义时目标 `待确认`。

### message_reorder

对涉及消息队列/异步通知的 transition 生成乱序场景。乱序处理规则未定义时目标 `待确认`；同步且明确无消息通道才可标不适用。

### timeout_retry

需求明确存在等待或重试能力时生成；关键词只是候选。时限与超时后的目标必须有来源，不能代填 30 分钟；缺失时标 `待确认`。

### data_consistency

对 `side_effects` 非空的 transition 生成一致性场景，验证关联对象、支付记录、履约单等同步更新或部分失败回滚。

### access_control

有已确认权限要求时生成越权场景；角色词只是候选。PRD 未明确角色/矩阵/拒绝规则时目标保持 `待确认`，不能声称未授权或必拒绝，另列缺失依据。

### failure_recovery

按明确失败能力生成「执行失败后状态」场景；资料不足只给 unknown 候选并附 reason。不要假设每条转换都有失败路径，也不要把受理态当作终态。

## 适用性与跳过

十类均输出 `status: applicable / not_applicable / unknown`，以及 `reason/source/evidence_type/missing_information`。

- 模型结构可判断是否有转换、禁止、守卫、副作用；来源注明模型层，不能证明业务完整性。
- 幂等、并发、消息、等待、权限、失败能力需要需求明确提供范围；事件关键词仅产生候选。
- 未知 ≠ 不适用；未说明权限时目标保持 `待确认`，不能默认拒绝。
- 同步且明确无消息通道 → 乱序不适用；并发候选必须同对象同前置状态。
- 场景类型条数保留描述统计，不作为完整性门槛。

| 场景类型 | 跳过条件 |
|---|---|
| legal_transition | 不跳过 |
| illegal_transition | 无 forbidden 且无终态 |
| guard_violation | transition 无 guards |
| idempotency | 无外部回调 |
| concurrency | 无同源竞争事件 |
| message_reorder | 同步且明确无消息通道 |
| timeout_retry | 无等待/重试 |
| data_consistency | 无 side_effects |
| access_control | 明确无权限要求 |
| failure_recovery | 无失败能力；未知时只给待确认候选 |

## 去重与编号

**去重**：同 risk_type 同 `(current_state, trigger_event)` 时，只有转换/禁止引用、完整守卫、违反守卫、前置输入、尝试目标与所有断言都等价才合并；不同 guard/目标不得压成一条。不同 risk_type 保留多条，标题区分。

**编号**：`SM-{三位序号}`，从 SM-001 起；按 risk_type 顺序（legal → illegal → guard → idempotency → concurrency → message_reorder → timeout → data_consistency → access_control → failure_recovery），同类型内按 current_state 字母序。

## 相关

- 反模式见 [anti-patterns.md](anti-patterns.md)
- 建模方法见 [state-modeling.md](state-modeling.md)
- 完整性检查见 [completeness-check.md](completeness-check.md)
- 覆盖/失败语义契约见 [coverage-contract.md](coverage-contract.md)
