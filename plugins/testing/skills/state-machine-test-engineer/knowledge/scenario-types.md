# 10 类场景穷举规则

> **何时阅读**：阶段 4（10 类场景穷举）执行时查阅。定义每类场景的生成规则、生成条件、示例。
> **覆盖范围**：10 类 risk_type 的生成规则 / 何时生成 / 何时跳过 / 示例 schema。

## 1. 10 类场景总览

| risk_type | 中文名 | 生成依据 | 默认证据类型 |
|---|---|---|---|
| `legal_transition` | 合法转换 | 每条 transition 生成 1 个 | 与该 transition 相同 |
| `illegal_transition` | 非法转换 | 每条 forbidden 生成 1 个 | 与该 forbidden 相同 |
| `guard_violation` | 条件不满足 | 每条 transition 移除 1 个 guard | 合理推理 |
| `idempotency` | 重复事件与幂等 | 涉及外部回调的 transition | 合理推理 |
| `concurrency` | 并发事件 | 涉及用户操作 + 系统回调的 transition | 合理推理 |
| `message_reorder` | 消息乱序 | 涉及异步消息的 transition | 合理推理 |
| `timeout_retry` | 超时与重试 | 涉及等待/重试的 transition | 合理推理 |
| `data_consistency` | 数据一致性 | 涉及副作用（关联对象更新）的 transition | 合理推理 |
| `access_control` | 权限控制 | 涉及权限的 transition | 待确认（PRD 通常未写权限矩阵） |
| `failure_recovery` | 失败后恢复路径 | 每条 transition 生成 1 个 | 待确认（PRD 通常未写失败后状态） |

## 2. 每类场景的生成规则

### 2.1 legal_transition（合法转换）

**生成规则**：对每条 transition 生成 1 个合法场景，验证 PRD 明确的转换路径。

**生成条件**：所有 transition 都生成。

**示例**：

```yaml
- id: SM-001
  title: 待支付订单收到支付成功回调后转为已支付
  current_state: 待支付
  trigger_event: 支付成功回调
  precondition: 订单处于待支付状态，金额一致，回调可信
  expected_target_state: 已支付
  forbidden_states: [已取消, 退款成功]
  risk_type: legal_transition
  related_objects: [支付记录, 订单日志]
  evidence_type: 需求明确
  source: PRD §3.2 + 状态机 transitions
  notes: 验证转换后副作用已执行（生成支付记录、触发履约）
```

### 2.2 illegal_transition（非法转换）

**生成规则**：对每条 forbidden 生成 1 个非法场景，验证 forbidden 规则被正确拒绝。

**生成条件**：所有 forbidden 都生成。若无显式 forbidden，对终态自动生成终态吸收的非法场景。

**示例**：

```yaml
- id: SM-002
  title: 已取消订单尝试支付应被拒绝
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

### 2.3 guard_violation（条件不满足）

**生成规则**：对每条 transition 的每个 guard 各生成 1 个场景，验证 guard 不满足时转换被拒绝。

**生成条件**：transition 有 guards 字段且非空。

**示例**：

```yaml
- id: SM-003
  title: 待支付订单收到金额不一致的支付回调应被拒绝
  current_state: 待支付
  trigger_event: 支付成功回调
  precondition: 订单处于待支付状态，但回调金额 ≠ 订单金额
  expected_target_state: 待支付（保持不变）
  forbidden_states: [已支付]
  risk_type: guard_violation
  related_objects: [支付记录, 风控日志]
  evidence_type: 合理推理
  source: 状态机 transitions 中 guard "金额一致" 的反向
  notes: 验证拒绝后是否记录风控日志
```

### 2.4 idempotency（重复事件与幂等）

**生成规则**：对涉及外部回调的 transition（支付/退款/通知类事件）生成重复触发场景。

**生成条件**：transition 的 event 包含"回调"/"通知"/"消息"等外部触发词。

**示例**：

```yaml
- id: SM-004
  title: 支付成功回调重复到达不应重复更新订单状态
  current_state: 已支付
  trigger_event: 支付成功回调（重复）
  precondition: 订单已是已支付状态，收到第二次支付成功回调
  expected_target_state: 已支付（保持不变）
  forbidden_states: [重复生成支付记录]
  risk_type: idempotency
  related_objects: [支付记录, 订单日志, 消息队列]
  evidence_type: 合理推理
  source: 业务常识（支付回调可能因网络重试重复到达）
  notes: 验证幂等键/状态校验/支付记录不重复生成
```

### 2.5 concurrency（并发事件）

**生成规则**：对涉及用户操作 + 系统回调的 transition 生成并发场景，验证并发时的最终状态。

**生成条件**：transition 的 event 同时涉及用户和系统（如"用户取消"与"支付回调"并发）。

**示例**：

```yaml
- id: SM-005
  title: 用户取消与支付回调并发时最终状态正确
  current_state: 待支付
  trigger_event: 用户取消 + 支付成功回调（同时到达）
  precondition: 订单处于待支付状态，用户点取消的同时收到支付成功回调
  expected_target_state: 待确认（取决于业务规则：先到先得/取消优先/支付优先）
  forbidden_states: []
  risk_type: concurrency
  related_objects: [订单日志, 支付记录, 锁机制]
  evidence_type: 待确认
  source: PRD 未说明并发处理规则
  notes: 需澄清并发时的优先级与锁策略
```

### 2.6 message_reorder（消息乱序）

**生成规则**：对涉及异步消息的 transition 生成乱序场景。

**生成条件**：transition 的 event 涉及消息队列/异步通知。

**示例**：

```yaml
- id: SM-006
  title: 退款失败回调先于退款成功回调到达时状态正确
  current_state: 退款中
  trigger_event: 退款失败回调 + 退款成功回调（乱序到达）
  precondition: 退款处理中，两条回调消息乱序到达
  expected_target_state: 待确认（取决于业务规则：最后一条为准/失败优先）
  forbidden_states: []
  risk_type: message_reorder
  related_objects: [消息队列, 退款记录, 订单日志]
  evidence_type: 待确认
  source: PRD 未说明消息乱序处理规则
  notes: 需澄清乱序时以哪条消息为准
```

### 2.7 timeout_retry（超时与重试）

**生成规则**：对涉及等待/重试的 transition 生成超时场景。

**生成条件**：transition 的 event 或 guard 涉及"超时"/"重试"/"等待"。

**示例**：

```yaml
- id: SM-007
  title: 待支付订单 30 分钟未支付应自动取消
  current_state: 待支付
  trigger_event: 超时定时器触发（30 分钟）
  precondition: 订单创建后 30 分钟未收到支付回调
  expected_target_state: 已取消
  forbidden_states: [已支付]
  risk_type: timeout_retry
  related_objects: [定时任务, 订单日志]
  evidence_type: 合理推理
  source: 业务常识（PRD 可能未提超时时长）
  notes: 需澄清超时时长是 15 分钟/30 分钟/60 分钟
```

### 2.8 data_consistency（数据一致性）

**生成规则**：对涉及副作用（关联对象更新）的 transition 生成一致性场景。

**生成条件**：transition 的 side_effects 非空。

**示例**：

```yaml
- id: SM-008
  title: 待支付转已支付后支付记录与订单状态一致
  current_state: 待支付
  trigger_event: 支付成功回调
  precondition: 订单处于待支付状态，收到合法支付回调
  expected_target_state: 已支付
  forbidden_states: [支付记录与订单状态不一致]
  risk_type: data_consistency
  related_objects: [订单, 支付记录, 履约单]
  evidence_type: 合理推理
  source: 状态机 transitions 中 side_effects 的验证
  notes: 验证支付记录/订单状态/履约单在同一事务内更新，部分失败时回滚
```

### 2.9 access_control（权限控制）

**生成规则**：对涉及权限的 transition 生成越权场景。

**生成条件**：transition 涉及管理员/审批人/特定角色操作。若 PRD 未明确权限矩阵，全部标"待确认"。

**示例**：

```yaml
- id: SM-009
  title: 普通用户尝试管理员退款操作应被拒绝
  current_state: 已支付
  trigger_event: 管理员发起退款（普通用户冒充）
  precondition: 用户为普通用户，无管理员权限
  expected_target_state: 已支付（保持不变）
  forbidden_states: [退款中]
  risk_type: access_control
  related_objects: [权限系统, 操作日志]
  evidence_type: 待确认
  source: PRD 未说明退款操作权限矩阵
  notes: 需澄清退款操作是仅管理员/客服/还是用户也可发起
```

### 2.10 failure_recovery（失败后恢复路径）

**生成规则**：对每条 transition 生成"执行失败后状态"场景。

**生成条件**：所有 transition 都生成。PRD 通常未写失败后状态，多数标"待确认"。

**示例**：

```yaml
- id: SM-010
  title: 退款中执行退款失败回调后状态恢复路径
  current_state: 退款中
  trigger_event: 退款失败回调
  precondition: 订单处于退款中状态，收到退款失败回调
  expected_target_state: 待确认（PRD 未说明失败后是回退到已支付还是进入退款失败）
  forbidden_states: []
  risk_type: failure_recovery
  related_objects: [退款记录, 订单日志, 通知系统]
  evidence_type: 待确认
  source: PRD 未说明退款失败后的状态恢复规则
  notes: 需澄清失败后是允许重试/回退到原状态/进入退款失败终态
```

## 3. 何时跳过某类场景

| 场景类型 | 跳过条件 |
|---|---|
| `legal_transition` | 不跳过，每条 transition 必生成 |
| `illegal_transition` | 若无 forbidden 且无终态，可跳过 |
| `guard_violation` | transition 无 guards 可跳过 |
| `idempotency` | 无外部回调触发可跳过 |
| `concurrency` | 无用户操作 + 系统回调并发可跳过 |
| `message_reorder` | 无异步消息可跳过 |
| `timeout_retry` | 无等待/重试可跳过 |
| `data_consistency` | transition 无 side_effects 可跳过 |
| `access_control` | 无权限要求可跳过（但多数业务都有权限，默认生成） |
| `failure_recovery` | 不跳过，每条 transition 必生成 |

## 4. 场景去重规则

若同一对 (current_state, trigger_event) 在多类场景中出现，按以下规则去重：

1. **同 risk_type 同 (state, event)**：合并为 1 个场景，precondition 描述差异
2. **不同 risk_type 同 (state, event)**：保留为多个场景，title 区分（如"已取消订单尝试支付"vs"已取消订单支付回调重复到达"）

## 5. 场景编号规则

- 格式：`SM-{三位序号}`，从 SM-001 起编
- 编号顺序：按 risk_type 顺序（legal → illegal → guard → idempotency → concurrency → message_reorder → timeout → data_consistency → access_control → failure_recovery）
- 同 risk_type 内按 current_state 字母序

## 6. 反模式（详见 anti-patterns.md）

| 反模式 | 说明 |
|---|---|
| 把"重复触发"和"并发触发"混为 idempotency | 并发是 concurrency，重复是 idempotency，两者机制不同 |
| 不生成 failure_recovery 场景 | 漏测失败后状态，是最常见的高危漏测点 |
| 把 access_control 全部脑补为"管理员才能" | PRD 未说明权限矩阵时必须标"待确认"，不能脑补 |
| 把 message_reorder 跳过 | 即使无显式异步消息，支付/退款回调本质是异步，必须生成 |

---

**相关文档**：
- [state-modeling.md](state-modeling.md) - 状态机建模方法论
- [completeness-check.md](completeness-check.md) - 9 项检查清单
- [anti-patterns.md](anti-patterns.md) - 反模式黑名单
- [../state-machine-core.md](../state-machine-core.md) - 核心流程详述
