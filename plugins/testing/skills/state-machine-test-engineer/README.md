# State Machine Test Engineer Skill

> 状态机驱动的状态型需求测试 skill v1.0.0：基于 MAE + State Machine 方法论，为状态型业务对象构建状态机模型并穷举 10 类测试场景。

## 简介

State Machine Test Engineer 是 testing-bundle v3.0.0 新增的子 skill，专注状态型需求的测试设计。它用状态机作为业务建模语言，让测试设计从"功能点罗列"升级为"状态网络穷举"。

### 为什么需要这个 skill

普通 AI 根据 PRD 生成测试用例时，常出现以下漏洞：
- 已取消订单还能不能支付？
- 退款中能否再次申请退款？
- 支付回调重复到达时状态会不会被重复更新？
- 取消请求和支付回调并发时最终状态应是什么？

**根因**：PRD 通常只描述"用户做什么"，没有显性表达"对象处于什么状态、允许什么变化、哪些操作必须被拒绝"。AI 因此把需求理解为几个孤立功能模块，而非同一对象的连续生命周期。

本 skill 用状态机弥补这个缺口——给 AI 一套理解业务行为的结构。

## 核心能力

| 能力 | 说明 |
|---|---|
| 状态机建模 | 识别状态/事件/转换/守卫/不变量/禁止转换，输出 YAML/JSON 结构 |
| MAE 流程建模 | 主流程/替代流程/异常流程三层建模 |
| 10 类场景穷举 | 合法/非法转换、条件不满足、幂等、并发、消息乱序、超时重试、数据一致性、权限控制、失败恢复 |
| 完整性检查 | 9 项检查（含死锁/悬挂/终态吸收/依据类型标注） |
| 防幻觉机制 | 依据类型强制标注、歧义暴露而非补齐 |
| MCP 可选增强 | 调用配套 MCP Server 做 Schema 校验与 Mermaid 可视化 |

## 工作流（五阶段）

```
阶段 1: 状态型需求识别 → 识别业务对象与参与者，标记歧义为"待确认"
阶段 2: 状态机建模 → 抽取状态/转换/不变量/禁止转换
🔴 CHECKPOINT · 状态机模型展示给用户确认
阶段 3: 完整性检查 → 9 项检查，标记缺口
阶段 4: 10 类场景穷举 → 每场景标注依据类型
阶段 5: MCP 增强（可选）→ 校验/复核/导出
```

详细流程见 [SKILL.md](SKILL.md) 与 [state-machine-core.md](state-machine-core.md)。

## 与 test-case-engineer 的边界

| 维度 | state-machine-test-engineer | test-case-engineer |
|---|---|---|
| 触发条件 | 有明确状态/生命周期信号 | 通用功能测试 |
| 方法论 | MAE + State Machine 状态网络穷举 | 四阶段功能点覆盖 |
| 输入 | 状态型需求（订单/审批/工单/会员等） | 任意功能需求 |
| 输出 | 状态机模型 + 10 类场景清单 | 完整测试用例 |
| 输出粒度 | 场景级（含依据类型标注） | 用例步骤级 |
| 关系 | 上游（出场景清单） | 下游（基于清单落用例） |

通过 testing-bundle 链 5 协同：state-machine 输出场景清单 → CHECKPOINT → test-case-engineer 基于清单生成完整用例。

## 三种运行模式

| 模式 | 触发条件 | 行为 |
|---|---|---|
| 增强模式 | MCP 可用 | skill 自身推理 + MCP 做校验/穷举/可视化复核 |
| 独立模式 | MCP 未安装 | skill 纯 LLM 推理执行全流程 |
| 降级模式 | MCP 调用失败 | 自动回退到独立模式 |

skill 始终是主，MCP 是复核器。零配置可用，安装 MCP 后获得额外能力。

## 行业模板

知识库内置 4 个行业状态机模板：
- `order-refund.md` — 订单退款（文章案例，6 状态完整建模）
- `approval-flow.md` — 审批流（待审批/审批中/已通过/已驳回/已撤回）
- `membership.md` — 会员状态（普通/银卡/金卡/钻石/已冻结/已注销）
- `ticket.md` — 工单状态（新建/处理中/待回复/已解决/已关闭/已重开）

## 安装方式

### 方式 1：通过 testing-bundle 整体安装（推荐）

```
skills/
├── testing-bundle/
├── test-strategy-engineer/
├── test-case-engineer/
├── performance-test-engineer/
├── bug-analyzer/
└── state-machine-test-engineer/   ← 本 skill
```

### 方式 2：独立安装

只装本 skill 也可独立使用，但失去 testing-bundle 的链 5 协同能力（无法自动转交 test-case-engineer 生成用例步骤）。

### 方式 3：配套安装 MCP Server（可选增强）

进入增强模式，获得 Schema 校验、Mermaid 可视化、覆盖度报告。配置见 [integrations/quickstart.md](integrations/quickstart.md)。

## 使用示例

### 示例 1：订单退款状态机测试

```
用户：订单退款流程要做测试，订单状态包括待支付/已支付/已取消/退款中/退款成功/退款失败

→ 识别 6 个状态 + 转换 + 禁止（已取消→已支付、退款成功→任意）
→ 完整性检查（标注"退款失败后恢复路径"为缺口）
→ 10 类场景穷举（依据类型标注：需求明确/合理推理/待确认）
→ 输出：状态机模型 + 场景清单
```

### 示例 2：MCP 增强模式

```
用户：（已配置 MCP）审批流状态机测试

→ 构建 5 状态审批流状态机
→ MCP validate_state_machine 校验，缺口追加到报告
→ skill 穷举 + MCP generate_scenarios 交叉复核，差异标"待确认"
→ MCP export_artifacts 生成 Mermaid 状态图
→ 输出（✓ MCP 增强模式）：状态机模型 + 场景清单 + Mermaid 图 + 覆盖度报告
```

详细示例见 [SKILL.md](SKILL.md#使用示例)。

## 文件结构

```
state-machine-test-engineer/
├── SKILL.md                  # 主入口（工作流 + 反模式 + 示例）
├── README.md                 # 本说明文档
├── state-machine-core.md     # 核心流程详述
├── knowledge/
│   ├── state-modeling.md             # 状态机建模方法论
│   ├── scenario-types.md             # 10 类场景穷举规则
│   ├── completeness-check.md         # 完整性检查清单（9 项）
│   ├── anti-patterns.md              # 反模式黑名单
│   ├── industry-templates/           # 行业状态机模板
│   │   ├── order-refund.md
│   │   ├── approval-flow.md
│   │   ├── membership.md
│   │   └── ticket.md
│   └── products/                     # 产品专项知识
│       ├── README.md
│       └── products-template.md
├── integrations/
│   └── quickstart.md                 # MCP 配置说明
└── test-prompts.json                 # darwin-skill 验证用
```

## 反例与黑名单

- ❌ 把"页面提示"等同于"业务状态"
- ❌ 把"请求受理"等同于"处理完成"
- ❌ PRD 缺权限/异常路径时自行脑补（应标"待确认"）
- ❌ 不标注依据类型
- ❌ 把状态用动词描述（应用名词）
- ❌ 不定义禁止转换
- ❌ 把"申请成功"作为终态
- ❌ 直接输出用例步骤（应转交 test-case-engineer）

详见 [SKILL.md](SKILL.md#反模式黑名单)。

## 版本历史

- v1.0.0: 初始版本，五阶段流程 + 10 类场景穷举 + MCP 可选增强

---

**相关文档**：
- [SKILL.md](SKILL.md) - 完整方法论与工作流
- [state-machine-core.md](state-machine-core.md) - 核心流程详述
- [integrations/quickstart.md](integrations/quickstart.md) - MCP 配置说明
- [设计文档](../../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md) - 完整设计 spec
- [testing-bundle](../testing-bundle/SKILL.md) - bundle 入口（5-way 路由）
- [test-case-engineer](../test-case-engineer/SKILL.md) - 下游协同（链 5）
- [state-machine-testing-mcp](../../mcp-servers/state-machine-testing/README.md) - 配套 MCP Server
