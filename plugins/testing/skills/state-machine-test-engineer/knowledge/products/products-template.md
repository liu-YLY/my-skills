# 产品专项知识模板

> **何时使用**：为本团队的具体业务对象创建状态机知识时，复制本文件为 `{业务对象名}.md` 并按字段填写。
> **填写原则**：所有字段尽量标 `evidence_type: 需求明确`（团队已澄清），避免标 `待确认`。

## 1. 业务对象基本信息

```yaml
product_meta:
  object: Order                          # 业务对象名（英文）
  object_cn: 订单                        # 业务对象名（中文）
  version: 1.0                           # 本知识库版本
  owner: 张三                            # 负责人
  last_updated: 2026-07-18               # 最后更新日期
  source: PRD v2.3 + 业务澄清会议纪要    # 来源
  confidence: high                       # high/medium/low
```

## 2. 业务对象描述

简要描述业务对象的含义、生命周期、关键参与者。

```
订单是用户下单后产生的实体，从创建到完成经历待支付/已支付/已取消/退款中/退款成功/退款失败 6 个状态。
参与者：用户、支付渠道、管理员、超时定时器。
```

## 3. 状态清单（团队实际）

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
    source: PRD §3.1
  - name: 已支付
    meaning: 订单已支付，等待履约
    is_terminal: false
    invariants:
      - 支付金额不可修改
      - 支付时间不可篡改
    evidence_type: 需求明确
    source: PRD §3.2
  # ... 其他状态
```

## 4. 转换清单（团队实际）

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
    source: PRD §3.2
  # ... 其他转换
```

## 5. 禁止转换（团队实际）

```yaml
forbidden:
  - from: 已取消
    to: 已支付
    reason: 已取消订单不可支付
    evidence_type: 需求明确
    source: PRD §3.3
  - from: 退款成功
    to: "*"
    reason: 终态吸收
    evidence_type: 需求明确
  # ... 其他禁止
```

## 6. 已澄清的歧义（历史待确认项 resolved）

记录团队已澄清的业务规则，避免重复询问。

```yaml
resolved_ambiguities:
  - id: RES-001
    question: 退款失败后是否允许重新发起退款？
    answer: 不允许，退款失败为终态，需用户联系客服处理
    resolved_date: 2026-07-15
    resolved_by: 产品经理李四
    source: 业务澄清会议纪要 2026-07-15
  - id: RES-002
    question: 待支付订单超时时长？
    answer: 30 分钟
    resolved_date: 2026-07-15
    resolved_by: 产品经理李四
    source: 业务澄清会议纪要 2026-07-15
```

## 7. 当前待确认项

记录尚未澄清的业务规则，状态机测试时会标 `evidence_type: 待确认`。

```yaml
pending_ambiguities:
  - id: PEND-001
    question: 用户取消与支付回调并发时优先级？
    expected_clarify_date: 2026-08-01
    owner: 产品经理李四
  - id: PEND-002
    question: 退款操作权限矩阵（仅管理员/客服/用户）？
    expected_clarify_date: 2026-08-01
    owner: 产品经理李四
```

## 8. 历史漏测案例

记录本业务对象历史漏测的案例，作为场景穷举的额外参考。

```yaml
historical_missed_cases:
  - id: MISS-001
    date: 2026-06-15
    description: 已取消订单被重复支付，导致库存超卖
    root_cause: 未测试"已取消订单尝试支付"非法转换场景
    added_scenarios:
      - 已取消订单尝试支付应被拒绝（illegal_transition）
    lesson: forbidden 规则必须覆盖所有终态吸收
  - id: MISS-002
    date: 2026-06-20
    description: 支付回调重复到达，订单状态被重复更新
    root_cause: 未测试"支付回调幂等"场景
    added_scenarios:
      - 支付成功回调重复到达不应重复更新订单状态（idempotency）
    lesson: 涉及外部回调的 transition 必测幂等
```

## 9. 与通用模板的差异

记录本团队实际业务规则与通用行业模板（`../industry-templates/`）的差异。

```yaml
diffs_with_industry_template:
  - field: states
    industry: 6 个状态（待支付/已支付/已取消/退款中/退款成功/退款失败）
    product: 8 个状态（多了"风控审核中"和"财务复核中"）
    reason: 本团队有风控和财务二级审核流程
  - field: transitions
    industry: 退款失败为终态，不可恢复
    product: 退款失败后允许管理员审核后重新发起
    reason: 业务需要支持退款失败重试
```

## 10. 维护日志

```yaml
changelog:
  - version: 1.0
    date: 2026-07-18
    changes: 初始版本
    author: 张三
```

---

**填写检查清单**：
- [ ] 业务对象基本信息完整
- [ ] 状态清单覆盖所有实际状态
- [ ] 转换清单覆盖所有实际转换
- [ ] 禁止转换包含终态吸收
- [ ] 已澄清歧义记录完整
- [ ] 当前待确认项有负责人和预期澄清日期
- [ ] 历史漏测案例有 added_scenarios
- [ ] 与通用模板差异已记录

**相关文档**：
- [README.md](README.md) - 产品知识库说明
- [../industry-templates/](../industry-templates/) - 通用行业模板（fallback）
- [../../state-machine-core.md](../../state-machine-core.md) - 核心流程详述
