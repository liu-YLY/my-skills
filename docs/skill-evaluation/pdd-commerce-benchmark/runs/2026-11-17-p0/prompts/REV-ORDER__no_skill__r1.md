# P0 Runner Packet

- run_id: `REV-ORDER__no_skill__r1`
- task_id: `REV-ORDER`
- variant: `no_skill`
- repeat: 1
- benchmark: `pdd-commerce-auth-cart-order@1.0.0`
- requirement_sha256: `436606e439af995af3efb05f694423473939d8daa07d9f86602fb6f382788782`
- skill: none

## 执行要求

不加载任何 skill，仅依据需求文档和任务提示完成任务。

## 任务提示

你是资深测试工程师。请仅基于附件《拼多多风格电商交易需求文档》v1.0.0，对「购买、订单与支付」模块做需求评审。输出四部分：1）需求理解摘要（不超过 10 条）；2）问题清单（每条含 Q_ID、涉及条款、问题类型[冲突/歧义/缺失/不可测试]、影响、建议决策）；3）风险清单（资金、库存、并发、安全、隐私、异常路径）；4）建议补充的验收标准。必须分析文档第 14 节中与本模块相关的开放问题，并重点检查支付幂等、库存锁定与拼单退款。文档未定义的行为标注「待确认」，不得虚构规则。不要编写测试用例。

## 输出契约

```json
{
  "format": "markdown",
  "required_sections": [
    "需求理解摘要",
    "问题清单",
    "风险清单",
    "建议补充的验收标准"
  ],
  "item_fields": [
    "Q_ID",
    "涉及条款",
    "问题类型",
    "影响",
    "建议决策"
  ],
  "forbidden": [
    "虚构需求中不存在的规则",
    "把开放问题写成确定规则",
    "编写完整测试用例"
  ]
}
```

## 输入

- 附件：`requirements-pdd-auth-cart-order.md`
- SHA256：`436606e439af995af3efb05f694423473939d8daa07d9f86602fb6f382788782`
- 运行时应将需求文档全文作为附件提供；不得附加 must-cover、评分卡或历史产物。
