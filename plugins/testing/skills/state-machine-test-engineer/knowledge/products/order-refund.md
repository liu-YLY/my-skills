# 产品专项知识：订单退款

> **何时使用**：state-machine-test-engineer 用于本项目订单退款对象时，优先使用本文的团队实际规则，替代 `../industry-templates/order-refund.md` 通用模板。
> **来源**：本文为**示例沉淀**——基于行业模板与 skill 测试集文章案例编写，用于验证 products/ 机制端到端可用；团队落地时须按真实 PRD 核对每项，来源字段已标注。
> **资料优先级**：用户明确要求 > 当前项目已确认资料 > 本文（示例沉淀）> 行业模板。冲突事项标为待确认；未获授权不回写产品资料。

## 1. 业务对象基本信息

```yaml
product_meta:
  object: Order
  object_cn: 订单退款
  version: 1.0
  owner: 待补充（示例沉淀，无实际负责人）
  last_updated: 2026-09-18
  source: 行业模板 order-refund.md + skill 测试集文章案例（示例沉淀，团队落地须核对真实 PRD）
  confidence: medium
```

## 2. 业务对象描述

订单是用户下单后产生的实体，从创建到退款结束经历待支付/已支付/已取消/退款中/退款成功/退款失败 6 个状态。
参与者：用户、支付渠道、管理员、超时定时器。
本文记录订单退款专项规则：支付/取消/退款三类核心流程，含幂等、并发、终态吸收等关键不变量。

## 3. 状态清单（示例沉淀）

```yaml
states:
  - name: 待支付
    meaning: 订单已创建未支付
    is_initial: true
    is_terminal: false
    invariants:
      - 订单金额不可修改
      - 订单项不可删除
    evidence_type: 需求明确
    source: 行业模板 §2 states.待支付
  - name: 已支付
    meaning: 订单已支付，等待履约
    is_terminal: false
    invariants:
      - 支付金额不可修改
      - 支付时间不可篡改
    evidence_type: 需求明确
    source: 行业模板 §2 states.已支付
  - name: 已取消
    meaning: 订单已取消，不可再支付
    is_terminal: true
    invariants:
      - 不可再次支付
      - 库存已释放
    evidence_type: 需求明确
    source: 行业模板 §2 states.已取消
  - name: 退款中
    meaning: 退款申请已受理，等待渠道处理
    is_terminal: false
    invariants:
      - 退款金额不可修改
      - 退款申请记录已生成
    evidence_type: 需求明确
    source: 行业模板 §2 states.退款中
  - name: 退款成功
    meaning: 退款已完成，资金已退回
    is_terminal: true
    invariants:
      - 退款金额不可再修改
      - 不可再次发起退款
    evidence_type: 需求明确
    source: 行业模板 §2 states.退款成功
  - name: 退款失败
    meaning: 退款失败，等待处理
    is_terminal: true
    invariants:
      - 退款失败记录已生成
      - 后续路径待确认
    evidence_type: 待确认
    source: 行业模板 §2 states.退款失败（恢复路径未定义，见待确认项 PEND-001）
```

## 4. 转换清单（示例沉淀）

```yaml
transitions:
  - from: 待支付
    to: 已支付
    event: 支付成功回调
    guards:
      - 订单有效
      - 金额一致
      - 回调可信
    side_effects:
      - 生成支付记录
      - 触发履约
      - 通知用户
    evidence_type: 需求明确
    source: 行业模板 §2 transitions
  - from: 待支付
    to: 已取消
    event: 用户取消
    side_effects: [释放库存, 通知用户]
    evidence_type: 需求明确
    source: 行业模板 §2 transitions
  - from: 待支付
    to: 已取消
    event: 超时取消
    guards: [创建后 30 分钟未支付]
    side_effects: [释放库存, 标记超时]
    evidence_type: 合理推理
    source: 行业模板 §2 transitions（超时时长 30 分钟为合理推理，见待确认项 PEND-002）
  - from: 已支付
    to: 退款中
    event: 管理员发起退款
    guards: [订单已支付, 退款金额有效]
    side_effects: [生成退款申请, 调用退款渠道]
    evidence_type: 需求明确
    source: 行业模板 §2 transitions（权限矩阵见待确认项 PEND-003）
  - from: 退款中
    to: 退款成功
    event: 退款成功回调
    guards: [回调可信, 退款金额一致]
    side_effects: [更新退款记录, 通知用户, 释放履约]
    evidence_type: 需求明确
    source: 行业模板 §2 transitions
  - from: 退款中
    to: 退款失败
    event: 退款失败回调
    guards: [回调可信]
    side_effects: [更新退款记录, 通知用户]
    evidence_type: 需求明确
    source: 行业模板 §2 transitions
```

## 5. 禁止转换（示例沉淀）

```yaml
forbidden:
  - from: 已取消
    to: 已支付
    reason: 已取消订单不可支付
    evidence_type: 需求明确
    source: 行业模板 §2 forbidden
  - from: 已取消
    to: 退款中
    reason: 已取消订单不可退款
    evidence_type: 合理推理
    source: 行业模板 §2 forbidden
  - from: 退款成功
    to: "*"
    reason: 终态吸收
    evidence_type: 需求明确
    source: 行业模板 §2 forbidden
  - from: 退款失败
    to: "*"
    reason: 终态吸收
    evidence_type: 待确认
    source: 行业模板 §2 forbidden（退款失败后能否重新发起未定义，见待确认项 PEND-001）
```

## 6. 已澄清的歧义（示例沉淀）

```yaml
resolved_ambiguities:
  - id: RES-001
    question: 退款成功回调重复到达是否重复更新状态？
    answer: 不重复更新，幂等处理，第二次回调直接忽略
    resolved_date: 2026-09-18
    resolved_by: 示例沉淀（行业模板幂等场景推导）
    source: 行业模板 §4 SM-004 幂等场景
```

## 7. 当前待确认项

```yaml
pending_ambiguities:
  - id: PEND-001
    question: 退款失败后的恢复路径（重新发起/回退到已支付/保持终态）？
    expected_clarify_date: 待补充
    owner: 待补充
  - id: PEND-002
    question: 待支付订单超时时长是 15/30/60 分钟？
    expected_clarify_date: 待补充
    owner: 待补充
  - id: PEND-003
    question: 退款操作权限矩阵（仅管理员/客服/用户）？
    expected_clarify_date: 待补充
    owner: 待补充
  - id: PEND-004
    question: 用户取消与支付回调并发时优先级？
    expected_clarify_date: 待补充
    owner: 待补充
  - id: PEND-005
    question: 退款失败回调先于退款成功回调乱序到达时以哪条为准？
    expected_clarify_date: 待补充
    owner: 待补充
```

## 8. 历史漏测案例（示例沉淀）

```yaml
historical_missed_cases:
  - id: MISS-001
    date: 2026-09-18
    description: 已取消订单被重复支付，导致库存超卖（示例沉淀，源自行业模板教训）
    root_cause: 未测试"已取消订单尝试支付"非法转换场景
    added_scenarios:
      - 已取消订单尝试支付应被拒绝（illegal_transition）
    lesson: forbidden 规则必须覆盖所有终态吸收
  - id: MISS-002
    date: 2026-09-18
    description: 支付回调重复到达，订单状态被重复更新（示例沉淀，源自行业模板教训）
    root_cause: 未测试"支付回调幂等"场景
    added_scenarios:
      - 支付成功回调重复到达不应重复更新订单状态（idempotency）
    lesson: 涉及外部回调的 transition 必测幂等
```

## 9. 与通用模板的差异

```yaml
diffs_with_industry_template:
  - field: states
    industry: 6 个状态（待支付/已支付/已取消/退款中/退款成功/退款失败）
    product: 与行业模板一致（示例沉淀，团队若有风控/财务级状态在此补充）
    reason: 示例沉淀暂未发现差异
  - field: transitions
    industry: 退款失败为终态，不可恢复
    product: 与行业模板一致，退款失败恢复路径待确认
    reason: 与 PEND-001 联动，澄清后在此更新
```

## 10. 维护日志

```yaml
changelog:
  - version: 1.0
    date: 2026-09-18
    changes: 示例沉淀，基于行业模板 order-refund.md 与测试集文章案例建立，验证 products/ 机制端到端可用
    author: skill 维护者（示例）
```

---

**落地说明（团队使用前必读）**：本文为**示例沉淀**，全体 `evidence_type` 与 `source` 均标注为行业模板/合理推理，未经验证为真实业务规则。团队使用时按 products/README.md「资料优先级」核对真实 PRD，将 `owner`、`expected_clarify_date`、待确认项补全，并把 `confidence` 提升为 high。

**填写检查清单**：
- [x] 业务对象基本信息完整（owner/澄清日期为示例占位，落地时补全）
- [x] 状态清单覆盖所有实际状态
- [x] 转换清单覆盖所有实际转换
- [x] 禁止转换包含终态吸收
- [x] 已澄清歧义记录（示例）
- [x] 当前待确认项有负责人和预期澄清日期（示例占位）
- [x] 历史漏测案例有 added_scenarios
- [x] 与通用模板差异已记录

**相关文档**：
- [README.md](README.md) - 产品知识库说明
- [products-template.md](products-template.md) - 产品模板填写模板
- [../industry-templates/order-refund.md](../industry-templates/order-refund.md) - 本示例沉淀的行业模板来源
- [../../state-machine-core.md](../../state-machine-core.md) - 核心流程详述
