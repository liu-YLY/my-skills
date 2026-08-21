# testing-bundle 使用示例与快速上手

> 本文件承载 testing-bundle 的完整演示对话与首次使用引导，由 [SKILL.md](../SKILL.md) 按需加载：仅当用户想看路由演示或首次安装配置时读取，路由决策本身不依赖本文件。

## 使用示例

### 示例 1：Bug 根因分析（自动路由到 bug-analyzer）

```
用户：线上出现重复扣款 Bug，用户反馈偶发，帮我分析根因

testing-bundle:
  → 意图判断：Bug 根因分析
  → 路由到 bug-analyzer
  → 执行五步定位法
  → 输出根因分析报告 + 防御性测试点清单
```

### 示例 2：混合意图 Bug + 用例（链 1 协同）

```
用户：分析这个重复扣款 Bug 的根因，并补充测试用例防止再次出现

testing-bundle:
  → 意图判断：混合（分析 + 生成）
  → 路由到 bug-analyzer 执行根因分析
  → bug-analyzer 输出防御性测试点清单

🔴 CHECKPOINT · bug-analyzer 完成：防御性测试点清单必须展示给用户确认，用户可修改清单或终止流程，确认后才转交 test-case-engineer。

  → 转交 test-case-engineer 基于清单生成完整用例
  → 输出根因分析报告 + 完整测试用例
```

### 示例 3：意图不明确（追问）

🔴 **CHECKPOINT · 意图不明确时强制追问**：不得"默认路由"，必须列出 6 个子 skill 的能力让用户选择。

```
用户：我有个测试相关的问题

testing-bundle:
  → 意图判断：不明确
  → 追问用户：
    "请告诉我您需要哪类帮助：
     A. 项目级测试策略（test-strategy-engineer）
     B. 生成测试用例（test-case-engineer）
     C. 性能测试方案/瓶颈定位（performance-test-engineer）
     D. 分析 Bug 根因（bug-analyzer）
     E. 状态机驱动的状态型需求测试（state-machine-test-engineer）
     F. 变更影响分析（change-impact-analyzer）"
```

### 示例 4：测试策略（自动路由到 strategy）

```
用户：我们要启动一个新项目的测试，需要制定测试策略，包括风险矩阵和测试分层

testing-bundle:
  → 意图判断：项目级测试策略（关键词：测试策略、风险矩阵、测试分层）
  → 路由到 test-strategy-engineer
  → 执行五阶段流程：项目特征→风险矩阵→分层→CHECKPOINT→范围准入准出
  → 输出测试策略报告
```

### 示例 5：性能测试方案（自动路由到 performance）

```
用户：我们的支付系统要做性能测试，预期峰值 5000 TPS，关注 P99 响应时间

testing-bundle:
  → 意图判断：性能测试方案设计（关键词：性能测试、TPS、响应时间）
  → 路由到 performance-test-engineer
  → 执行阶段 1-2：性能需求理解 + 测试场景设计

🔴 CHECKPOINT · performance 阶段 2 后：性能测试方案必须展示给用户确认，确认后进入阶段 3（若需瓶颈定位）。

  → 输出性能测试方案（负载模型 + 场景 + 指标阈值）
```

### 示例 6：策略 + 用例协同（链 2 协同）

```
用户：制定项目级测试策略，并按策略生成分层用例

testing-bundle:
  → 意图判断：混合（策略 + 用例）
  → 路由到 test-strategy-engineer 执行项目级策略设计
  → strategy 输出分层策略 + 优先级 + 准入准出

🔴 CHECKPOINT · strategy 完成：分层策略与优先级必须展示给用户确认，用户可修改或终止流程，确认后才转交 test-case-engineer。

  → 转交 test-case-engineer 按分层策略生成对应层用例
  → 输出测试策略 + 分层测试用例
```

### 示例 7：状态机建模（自动路由到 state-machine）

```
用户：订单退款流程要做测试，订单状态包括待支付/已支付/已取消/退款中/退款成功/退款失败

testing-bundle:
  → 意图判断：状态型需求测试（关键词：状态、退款流程、状态名罗列）
  → 路由到 state-machine-test-engineer
  → 执行五阶段：状态型需求识别→状态机建模→CHECKPOINT→完整性检查→10类场景穷举
  → 输出状态机模型 + 场景清单（含依据类型标注，未说明的退款失败恢复路径标"待确认"）
```

### 示例 8：状态机 + 用例协同（链 5 协同）

```
用户：为订单退款流程设计状态机测试场景，并生成完整测试用例

testing-bundle:
  → 意图判断：混合（状态机 + 用例）
  → 路由到 state-machine-test-engineer 执行状态机建模
  → state-machine 输出状态机模型 + 场景清单（含依据类型标注）

🔴 CHECKPOINT · state-machine 完成：状态机模型与场景清单必须展示给用户确认，用户可修改模型/补充场景/终止流程，确认后才转交 test-case-engineer。

  → 转交 test-case-engineer 基于场景清单生成完整用例
  → 输出状态机模型 + 场景清单 + 完整测试用例
```

## 快速上手

1. 确认已安装 6 个子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer / state-machine-test-engineer / change-impact-analyzer）
2. 用户提出测试相关请求时，testing-bundle 自动触发
3. bundle 按 6-way 路由决策表（5 核心 + 1 协同）判断意图并路由到对应子 skill
4. 混合意图按对应链路执行（7 条链），转交点 🔴 CHECKPOINT
5. 子 skill 执行具体任务并输出结果
6. state-machine-test-engineer 可选安装配套 MCP Server 进入增强模式（⚠️ v0.1.0 协议层注册代码已实现但尚未端到端联调验证，验证通过前 skill 默认以独立模式运行，待 v0.2.0；详见 [state-machine-test-engineer/integrations/quickstart.md](../../state-machine-test-engineer/integrations/quickstart.md)）
7. test-case-engineer 评审模式可选安装配套 review-checker MCP Server 进入增强模式（详见 [review-checker README](../../../mcp-servers/review-checker/README.md)）
