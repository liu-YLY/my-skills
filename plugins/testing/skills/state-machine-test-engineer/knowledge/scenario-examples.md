# 场景完整示例（可校验）

> **何时阅读**：需要对照完整状态机模型与 10 条场景的字段写法，或修改 MCP 示例契约时加载；日常生成只需 [scenario-types.md](scenario-types.md)。
> 本文件中的 YAML 块由 state-machine-testing MCP 集成测试直接解析，修改时须保持可校验。

```yaml
state_machine:
  meta: {object: Order, source: 示例基线}
  states:
    - {name: 待支付, meaning: 等待支付, is_initial: true}
    - {name: 已支付, meaning: 已收到支付结果}
    - {name: 已取消, meaning: 订单已取消, is_terminal: true}
    - {name: 退款中, meaning: 退款处理中}
    - {name: 退款成功, meaning: 退款完成, is_terminal: true}
  transitions:
    - id: T-PAY
      from: 待支付
      to: 已支付
      event: 支付成功回调
      guards: [订单有效, 金额一致, 回调可信]
      side_effects: [生成支付记录, 触发履约]
      evidence_type: 需求明确
      source: 示例 PRD §3.2
  forbidden:
    - id: F-CANCEL
      from: 已取消
      to: 已支付
      reason: 已取消订单不可支付
      evidence_type: 需求明确
      source: 示例 PRD §3.1
```

```yaml
- id: SM-001
  title: 待支付订单收到支付成功回调后转为已支付
  current_state: 待支付
  trigger_event: 支付成功回调
  precondition: 订单处于待支付状态，金额一致，回调可信
  expected_target_state: 已支付
  forbidden_states: [已取消, 退款成功]
  risk_type: legal_transition
  transition_id: T-PAY
  guard_conditions: [订单有效, 金额一致, 回调可信]
  related_objects: [支付记录, 订单日志]
  evidence_type: 需求明确
  source: PRD §3.2 + 状态机 transitions
  notes: 验证转换后副作用已执行（生成支付记录、触发履约）
```

```yaml
- id: SM-002
  title: 已取消订单尝试支付应被拒绝
  current_state: 已取消
  trigger_event: 支付成功回调
  precondition: 订单已取消
  expected_target_state: 已取消
  forbidden_states: [已支付]
  risk_type: illegal_transition
  forbidden_id: F-CANCEL
  attempted_target_state: 已支付
  related_objects: [支付记录, 订单日志]
  evidence_type: 需求明确
  source: PRD §3.1 + 状态机 forbidden 规则
  notes: 需验证后端拒绝 + 前端按钮置灰
```

```yaml
- id: SM-003
  title: 待支付订单收到金额不一致的支付回调应被拒绝
  current_state: 待支付
  trigger_event: 支付成功回调
  precondition: 订单处于待支付状态，但回调金额 ≠ 订单金额
  expected_target_state: 待支付
  forbidden_states: [已支付]
  risk_type: guard_violation
  transition_id: T-PAY
  guard_conditions: [订单有效, 金额一致, 回调可信]
  violated_guard: 金额一致
  related_objects: [支付记录, 风控日志]
  evidence_type: 合理推理
  source: 状态机 transitions 中 guard "金额一致" 的反向
  notes: 验证拒绝后是否记录风控日志
```

```yaml
- id: SM-004
  title: 支付成功回调重复到达不应重复更新订单状态
  current_state: 已支付
  trigger_event: 支付成功回调（重复）
  precondition: 订单已是已支付状态，收到第二次支付成功回调
  expected_target_state: 已支付
  forbidden_states: [重复生成支付记录]
  risk_type: idempotency
  related_objects: [支付记录, 订单日志, 消息队列]
  evidence_type: 合理推理
  source: 业务常识（支付回调可能因网络重试重复到达）
  notes: 验证幂等键/状态校验/支付记录不重复生成
```

```yaml
- id: SM-005
  title: 用户取消与支付回调并发时最终状态正确
  current_state: 待支付
  trigger_event: 用户取消 + 支付成功回调（同时到达）
  precondition: 订单处于待支付状态，用户点取消的同时收到支付成功回调
  expected_target_state: 待确认
  expected_target_state_reason: 并发处理优先级未定义
  forbidden_states: []
  risk_type: concurrency
  related_objects: [订单日志, 支付记录, 锁机制]
  evidence_type: 待确认
  source: PRD 未说明并发处理规则
  notes: 需澄清并发时的优先级与锁策略
```

```yaml
- id: SM-006
  title: 退款失败回调先于退款成功回调到达时状态正确
  current_state: 退款中
  trigger_event: 退款失败回调 + 退款成功回调（乱序到达）
  precondition: 退款处理中，两条回调消息乱序到达
  expected_target_state: 待确认
  expected_target_state_reason: 乱序处理规则未定义
  forbidden_states: []
  risk_type: message_reorder
  related_objects: [消息队列, 退款记录, 订单日志]
  evidence_type: 待确认
  source: PRD 未说明消息乱序处理规则
  notes: 需澄清乱序时以哪条消息为准
```

```yaml
- id: SM-007
  title: 待支付超时后目标与处理策略待确认
  current_state: 待支付
  trigger_event: 超时定时器（时限待确认）
  precondition: 达到等待阈值，实际时限待确认
  expected_target_state: 待确认
  expected_target_state_reason: 需求未提供超时阈值与目标状态
  forbidden_states: []
  risk_type: timeout_retry
  related_objects: [定时任务, 订单日志]
  evidence_type: 待确认
  source: 超时阈值及处理策略缺少需求依据
  notes: 需澄清超时时长是 15 分钟/30 分钟/60 分钟
```

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

```yaml
- id: SM-009
  title: 已支付 下 管理员发起退款（普通用户冒充） 的权限边界待确认
  current_state: 已支付
  trigger_event: 管理员发起退款（普通用户冒充）
  precondition: 用户为普通用户，无管理员权限
  expected_target_state: 待确认
  expected_target_state_reason: 权限矩阵及拒绝行为缺少依据
  forbidden_states: []
  risk_type: access_control
  related_objects: [权限系统, 操作日志]
  evidence_type: 待确认
  source: PRD 未说明退款操作权限矩阵
  notes: 需澄清退款操作是仅管理员/客服/还是用户也可发起
```

```yaml
- id: SM-010
  title: 退款中执行退款失败回调后状态恢复路径
  current_state: 退款中
  trigger_event: 退款失败回调
  precondition: 订单处于退款中状态，收到退款失败回调
  expected_target_state: 待确认
  expected_target_state_reason: 失败后的恢复状态未定义
  forbidden_states: []
  risk_type: failure_recovery
  related_objects: [退款记录, 订单日志, 通知系统]
  evidence_type: 待确认
  source: PRD 未说明退款失败后的状态恢复规则
  notes: 需澄清失败后是允许重试/回退到原状态/进入退款失败终态
```
