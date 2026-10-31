# MCP 增强、独立与降级模式

> **何时阅读**：宿主已暴露 state-machine-testing MCP 工具，或用户明确要求 MCP 增强/校验时。
> **覆盖范围**：MCP 可用性探测、增强模式交叉复核、独立模式与降级模式规则。
> **可跳过条件**：未安装 MCP 且用户未要求增强时，按独立模式直接执行 core 阶段 1-4。

## 5.1 探测 MCP 可用性

先遵守用户显式禁用，再检查当前宿主已暴露的 `validate_state_machine/generate_scenarios/check_coverage` 工具；使用宿主工具清单，不将 Trae 配置或环境变量作为跨宿主前置。无工具时独立模式；已有工具可直接增强。

工具清单能证明可用时不额外探测；需要健康调用时使用下面的最小合法模型，不能空载调用。返回业务 pass/warn/fail 都证明服务响应；参数错误记为参数错误，先修正输入，不能冒充离线。连接失败、超时和工具不存在分别记录。健康检查只读，不调用写文件的 export。

```yaml
state_machine:
  meta: {object: HealthProbe, source: 健康检查示例}
  states:
    - {name: A, meaning: 初始态, is_initial: true}
    - {name: B, meaning: 完成态, is_terminal: true}
  transitions:
    - {from: A, to: B, event: 完成, side_effects: [记录结果], evidence_type: 合理推理}
```

工具清单探测超时 3s；只读业务调用超时 10s 可重试一次，仍失败降级并保留具体原因。正常业务校验不通过不触发连接降级。

## 5.2 增强模式（MCP 可用）

```
阶段 3 增强：
  skill 调用 MCP validate_state_machine
  → MCP 返回 ValidationReport
  → skill 把 gaps/contradictions 追加到自己的完整性检查报告
  → 若 validation_status=fail，先核对结构与来源，未决部分单列待确认

阶段 4 增强：
  skill 自身穷举 + 调用 MCP generate_scenarios 交叉复核
  → 对比两份清单，标记差异（多/少/矛盾）
  → 差异项标 evidence_type=待确认，交给用户裁定

阶段 5 增强：
  调用 MCP export_artifacts 生成 Mermaid 状态图 + Markdown 报告
  调用 MCP check_coverage 输出覆盖度报告
  skill 把覆盖度报告追加到最终输出
```

## 5.3 独立模式（MCP 未安装）

- 完整执行阶段 1-4，输出首行标 `⚠ 独立模式（未校验）`
- skill 手写 Mermaid 状态图（样式可能略差）
- skill 统计适用类型已处理情况，单列不适用和未知项；零计数不自动等于业务缺口

## 5.4 降级模式（MCP 调用失败）

- 自动回退到独立模式
- 输出首行标 `⚠ 降级模式（MCP 失败：原因）`
- 记录失败原因（超时/连接拒绝/Schema 不匹配等）
