# P0 Runner Packet

- run_id: `TP-ORDER__no_skill__r1`
- task_id: `TP-ORDER`
- variant: `no_skill`
- repeat: 1
- benchmark: `pdd-commerce-auth-cart-order@1.0.0`
- requirement_sha256: `436606e439af995af3efb05f694423473939d8daa07d9f86602fb6f382788782`
- skill: none

## 执行要求

不加载任何 skill，仅依据需求文档和任务提示完成任务。

## 任务提示

你是资深测试工程师。请仅基于附件需求文档，为「购买、订单与支付」模块提取测试点。输出 Markdown 表格，列固定为：TP_ID｜模块｜关联需求ID｜维度｜优先级(P0-P3)｜测试点描述｜预期结果。要求：1）覆盖功能、边界、异常、状态、权限、并发、安全、兼容性；2）每个测试点只验证一个独立目标；3）不写执行步骤；4）不重复；5）对第 14 节开放问题只写「待确认」测试点，不虚构规则。

## 输出契约

```json
{
  "format": "markdown_table",
  "columns": [
    "TP_ID",
    "模块",
    "关联需求ID",
    "维度",
    "优先级",
    "测试点描述",
    "预期结果"
  ],
  "forbidden": [
    "执行步骤",
    "同义重复条目",
    "无具体条件与预期的空泛描述"
  ]
}
```

## 输入

- 附件：`requirements-pdd-auth-cart-order.md`
- SHA256：`436606e439af995af3efb05f694423473939d8daa07d9f86602fb6f382788782`
- 运行时应将需求文档全文作为附件提供；不得附加 must-cover、评分卡或历史产物。
