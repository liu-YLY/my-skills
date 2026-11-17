# P0 Runner Packet

- run_id: `TC-ORDER__with_skill__r2`
- task_id: `TC-ORDER`
- variant: `with_skill`
- repeat: 2
- benchmark: `pdd-commerce-auth-cart-order@1.0.0`
- requirement_sha256: `436606e439af995af3efb05f694423473939d8daa07d9f86602fb6f382788782`
- skill: `test-case-engineer`

## 执行要求

加载 `test-case-engineer` skill，按该 skill 的流程完成任务；不要读取评分卡、must-cover 或 open_findings。

## 任务提示

你是资深测试工程师。请仅基于附件需求文档，为「购买、订单与支付」模块编写可执行测试用例。输出格式：每条用例以 `### TC_ORDER_<功能>_<序号>: 标题` 开始，包含前置条件、测试数据、步骤、预期结果、优先级、关联需求ID。要求：1）步骤可执行，使用第 13 节固定数据；2）预期结果可观察、可判定；3）一条用例只验证一个独立目标；4）覆盖主流程、边界、异常、状态、权限、并发与安全；5）对开放问题写「待确认」用例，不虚构规则。

## 输出契约

```json
{
  "format": "markdown_blocks",
  "block_header": "### TC_模块_功能_序号: 标题",
  "required_fields": [
    "前置条件",
    "测试数据",
    "步骤",
    "预期结果",
    "优先级",
    "关联需求ID"
  ],
  "forbidden": [
    "一张表罗列全部用例",
    "准备相关数据",
    "执行对应操作",
    "功能正常",
    "符合预期"
  ]
}
```

## 输入

- 附件：`requirements-pdd-auth-cart-order.md`
- SHA256：`436606e439af995af3efb05f694423473939d8daa07d9f86602fb6f382788782`
- 运行时应将需求文档全文作为附件提供；不得附加 must-cover、评分卡或历史产物。
