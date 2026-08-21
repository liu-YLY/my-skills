# state-machine-test-engineer 使用示例与快速上手

> 本文件承载完整演示对话与首次使用引导，由 [SKILL.md](../SKILL.md) 按需加载：仅当用户想看演示或首次安装配置时读取，五阶段流程本身不依赖本文件。

## 使用示例

### 示例 1：订单退款状态机建模（文章案例）

```
用户：订单退款流程要做测试，订单状态包括待支付/已支付/已取消/退款中/退款成功/退款失败

state-machine-test-engineer:
  → 阶段 1：识别业务对象 Order，识别参与者（用户/支付渠道/管理员/定时器）
  → 阶段 2：构建 6 状态状态机
    - 状态：待支付/已支付/已取消/退款中/退款成功/退款失败
    - 转换：待支付→已支付（支付成功回调）/待支付→已取消（用户取消/超时关闭）等
    - 禁止：已取消→已支付（已取消订单不可支付）、退款成功→任何状态（终态吸收）
  → 🔴 CHECKPOINT 展示状态机模型给用户确认
  → 阶段 3：完整性检查（标注"退款失败后恢复路径 PRD 未说明"为缺口）
  → 阶段 4：10 类场景穷举，每场景标注依据类型
    - 已取消订单尝试支付 → illegal_transition（依据：需求明确）
    - 支付回调重复到达 → idempotency（依据：合理推理）
    - 取消与支付并发 → concurrency（依据：合理推理）
    - 退款失败后状态恢复 → failure_recovery（依据：待确认，PRD 未说明）
  → 输出：状态机模型 + 场景清单（含依据类型标注）
```

### 示例 2：MCP 增强模式

```
用户：（已配置 state-machine-testing-mcp）审批流状态机测试

state-machine-test-engineer:
  → 阶段 1-2：构建审批流状态机（待审批/审批中/已通过/已驳回/已撤回）
  → 阶段 3：调用 MCP validate_state_machine 校验
    → MCP 返回 ValidationReport（标注"已撤回后是否能再发起"为缺口）
    → skill 把缺口追加到完整性检查报告
  → 阶段 4：skill 穷举场景 + 调用 MCP generate_scenarios 交叉复核
    → 对比两份清单，差异项标"待确认"
  → 阶段 5：调用 MCP export_artifacts 生成 Mermaid 状态图
    → 调用 MCP check_coverage 输出覆盖度报告
  → 输出（首行标 `✓ MCP 增强模式`）：状态机模型 + 场景清单 + Mermaid 图 + 覆盖度报告
```

### 示例 3：转交 test-case-engineer（链 5 协同）

```
用户：为订单退款流程设计状态机测试场景，并生成完整测试用例

testing-bundle → state-machine-test-engineer:
  → 执行五阶段，输出状态机模型 + 场景清单
  → 🔴 CHECKPOINT 用户确认状态机模型与场景清单

用户确认后 → testing-bundle → test-case-engineer:
  → 基于场景清单生成完整用例（每场景落实为可执行步骤）
  → 输出：状态机模型 + 场景清单 + 完整测试用例
```

## 快速上手

1. 确认已安装本 skill（独立可用，无需 MCP）
2. （可选增强）配套 MCP Server v0.2.0 协议层（stdio + HTTP）已端到端联调验证，按 [integrations/quickstart.md](../integrations/quickstart.md) 配置后进入增强模式；未配置时以独立模式运行
3. 通过 testing-bundle 路由，或直接调用本 skill
4. 提供状态型需求（含业务对象、状态名、状态转换描述）
5. 五阶段流程自动执行，CHECKPOINT 处确认状态机模型
6. 输出场景清单，可手动转交 test-case-engineer 或通过链 5 自动协同
