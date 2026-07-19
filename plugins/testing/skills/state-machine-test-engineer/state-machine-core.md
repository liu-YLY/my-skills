# State Machine Test Engineer 核心流程详述

> 本文件从 SKILL.md 拆分，详述五阶段流程的具体执行步骤、判断依据、输出格式。SKILL.md 是入口索引，本文件是执行手册。

## 阶段 1: 状态型需求识别

### 1.1 目标

确认输入是否为状态型需求，识别业务对象与参与者，把"用户做什么"的描述重整为"对象处于什么状态、允许什么变化"的结构化摘要。

### 1.2 输入

- PRD 片段 / 用户口述 / 既有用例描述
- 可选：产品知识库中的状态流转规则（见 `knowledge/products/`）

### 1.3 执行步骤

1. **业务对象识别**：从需求中找出承载状态的核心实体（订单/审批/工单/会员/账户等），一个需求可能有多个对象（如订单 + 支付记录），分别建模
2. **参与者识别**：标记每条操作的发起方
   - 人（用户/管理员/审批人）
   - 系统（支付网关/调度器/消息队列）
   - 外部（第三方回调）
   - 定时器（超时任务/cron）
3. **状态信号扫描**：检查需求是否包含以下信号
   - 显式状态名词（待支付/已支付/已取消）
   - 状态转换动词（支付成功后/取消后/审核通过后）
   - 终态描述（完成后不可修改/已退款订单不可再退）
   - 禁止描述（已取消订单不能支付）
4. **歧义标记**：需求未说明的权限/异常/恢复路径，**必须标"待确认"**，禁止 LLM 自行脑补

### 1.4 输出格式

```yaml
requirement_summary:
  business_objects:
    - name: Order
      description: 用户下单后产生的订单实体
  actors:
    - name: 用户
      type: 人
    - name: 支付渠道
      type: 外部
    - name: 超时定时器
      type: 定时器
  state_signals:
    - 显式状态: 待支付/已支付/已取消/退款中/退款成功/退款失败
    - 转换描述: 支付成功回调后订单转为已支付
    - 终态描述: 退款成功后不可再修改
    - 禁止描述: 已取消订单不能支付
  ambiguities:
    - id: AMB-001
      question: 退款失败后是否允许重新发起退款？
      evidence_type: 待确认
      source: PRD 未说明
```

### 1.5 退出条件

- 至少识别到 1 个业务对象
- 至少识别到 2 个状态信号（否则判定为非状态型需求，提示用户转 test-case-engineer）
- 所有歧义已记录到 `ambiguities` 列表

---

## 阶段 2: 状态机建模

### 2.1 目标

基于阶段 1 的摘要，构建符合 Schema 的状态机模型（YAML/JSON），含状态/转换/守卫/副作用/不变量/禁止转换/依据类型。

### 2.2 执行步骤

1. **抽取状态**
   - 只保留名词（待支付/已支付/退款成功），禁用动词状态（支付中/退款中应改为"退款处理中"等名词短语）
   - 每个状态必须填写 `meaning`（含义）
   - 标记 `is_initial`（初始态）和 `is_terminal`（终态）
2. **定义转换**
   - 每条转换：`from → to`，事件（动词）、守卫（前置条件）、副作用（后置动作）
   - 每条转换必须标 `evidence_type`：`需求明确` / `合理推理` / `待确认`
   - 每条转换必须标 `source`（PRD 章节或推理依据）
3. **定义不变量**
   - 每个状态列出不可破坏的约束（如"待支付状态订单金额不可修改"）
4. **定义终态与终态吸收**
   - 终态：业务最终态（退款成功/退款失败），不是受理态（退款申请成功）
   - 终态吸收：终态到任意状态都禁止（`forbidden: { from: 终态, to: "*" }`）
5. **定义禁止转换**
   - 列出业务上不允许的跳转（如"已取消 → 已支付"）
   - 每条禁止转换必须标 `reason` 和 `evidence_type`

### 2.3 输出格式

见 SKILL.md "核心数据结构" 章节。状态机模型必须符合 `knowledge/state-modeling.md` 中定义的 6 要素 + MAE + 不变量结构。

### 2.4 🔴 CHECKPOINT

阶段 2 输出后**必须**展示给用户确认：

- 显示完整状态机模型（状态/转换/禁止/不变量）
- 列出所有"待确认"项
- 询问：是否修改/补充/终止？

**CHECKPOINT 规则**：
- 用户修改 → 重新执行阶段 2
- 用户补充 → 更新模型后重新展示
- 用户确认 → 进入阶段 3
- 用户终止 → 输出当前状态机模型，不进入后续阶段

---

## 阶段 3: 完整性检查（9 项）

### 3.1 目标

对状态机模型做 9 项结构化检查，标记缺口/矛盾/警告，**不修复**（修复由用户决定）。

### 3.2 9 项检查清单

详见 `knowledge/completeness-check.md`。简要列表：

| # | 检查项 | pass 条件 | fail 处理 |
|---|---|---|---|
| 1 | 每个状态有明确含义 | `meaning` 字段非空 | 标 gap，要求补充 |
| 2 | 每个状态有进入条件（除初始态） | 至少 1 条 transition 的 `to` 指向它 | 标 unreachable warning |
| 3 | 每个非终态有退出路径 | 至少 1 条 transition 的 `from` 是它 | 标 deadlock warning |
| 4 | 终态真的不可变化 | 终态不出现在任何 transition 的 `from` | 标 contradiction |
| 5 | 禁止转换无遗漏 | 每个状态都明确"禁止进入哪些" | 标 gap，要求补充 |
| 6 | 状态变化有副作用定义 | `side_effects` 字段非空 | 标 warning |
| 7 | 依据类型已标注 | 所有 transition/forbidden 都有 `evidence_type` | 标 contradiction（Schema 违反） |
| 8 | 无悬挂状态 | 所有状态都可从初始态到达 | 标 warning |
| 9 | 无死锁状态 | 非终态都有出边 | 标 warning |

### 3.3 输出格式

```yaml
completeness_report:
  overall_status: pass | warn | fail
  checks:
    - check_id: C1
      name: 每个状态有明确含义
      status: pass
      detail: ""
    - check_id: C9
      name: 无死锁状态
      status: warn
      detail: 退款中状态无超时退出路径，疑似死锁
  gaps:
    - id: GAP-001
      description: 退款失败后的恢复路径未定义
      evidence_type: 待确认
      suggestion: 需澄清退款失败后是否允许重新发起
  contradictions: []
  suggestions:
    - 为退款中状态补充超时转人工的退出路径
```

### 3.4 退出条件

- `overall_status = pass` → 直接进入阶段 4
- `overall_status = warn` → 列出 warning，询问用户是否继续（默认继续）
- `overall_status = fail` → **不进入阶段 4**，触发 CHECKPOINT 要求用户先修正

---

## 阶段 4: 10 类场景穷举

### 4.1 目标

基于状态机模型，对每条 transition 生成 10 类场景，每场景标注依据类型。**只输出场景级**，不出用例步骤（用例步骤由 test-case-engineer 落地）。

### 4.2 10 类场景生成规则

详见 `knowledge/scenario-types.md`。简要列表：

| risk_type | 生成规则 |
|---|---|
| legal_transition | 对每条 transition 生成 1 个合法场景 |
| illegal_transition | 对每条 forbidden 生成 1 个非法场景 |
| guard_violation | 对每条 transition 移除 1 个 guard 生成场景 |
| idempotency | 对涉及外部回调的 transition 生成重复触发场景 |
| concurrency | 对涉及用户操作 + 系统回调的 transition 生成并发场景 |
| message_reorder | 对涉及异步消息的 transition 生成乱序场景 |
| timeout_retry | 对涉及等待/重试的 transition 生成超时场景 |
| data_consistency | 对涉及副作用（关联对象更新）的 transition 生成一致性场景 |
| access_control | 对涉及权限的 transition 生成越权场景 |
| failure_recovery | 对每条 transition 生成"执行失败后状态"场景 |

### 4.3 输出格式

见 SKILL.md "场景清单 Schema"。每条场景必须包含：
- `id`（SM-001 起编）
- `risk_type`（10 类枚举之一）
- `evidence_type`（需求明确/合理推理/待确认）
- `source`（PRD 章节 + 推理依据）

### 4.4 退出条件

- 至少生成 10 条场景（每类至少 1 条）
- 所有场景都有 `evidence_type` 标注
- 所有"PRD 未说明"的场景都标 `evidence_type: 待确认`

---

## 阶段 5: MCP 增强（可选）

### 5.1 探测 MCP 可用性

按以下顺序探测，任一失败则降级：

1. 检查环境变量 `STATE_MACHINE_MCP_ENABLED=true`
2. 检查配置文件 `~/.trae/state-machine-mcp.json` 存在且 `enabled=true`
3. 检查 Trae 已注册 `state-machine-testing` MCP Server
4. 尝试调用 `validate_state_machine` 做空载测试

**探测不阻塞主流程**，超时 3s 即降级。

### 5.2 增强模式（MCP 可用）

```
阶段 3 增强：
  skill 调用 MCP validate_state_machine
  → MCP 返回 ValidationReport
  → skill 把 gaps/contradictions 追加到自己的完整性检查报告
  → 若 validation_status=fail，触发 CHECKPOINT 让用户先修正

阶段 4 增强：
  skill 自身穷举 + 调用 MCP generate_scenarios 交叉复核
  → 对比两份清单，标记差异（多/少/矛盾）
  → 差异项标 evidence_type=待确认，交给用户裁定

阶段 5 增强：
  调用 MCP export_artifacts 生成 Mermaid 状态图 + Markdown 报告
  调用 MCP check_coverage 输出覆盖度报告
  skill 把覆盖度报告追加到最终输出
```

### 5.3 独立模式（MCP 未安装）

- 完整执行阶段 1-4，输出首行标 `⚠ 独立模式（未校验）`
- skill 手写 Mermaid 状态图（样式可能略差）
- skill 简单统计覆盖度（10 类是否齐全）

### 5.4 降级模式（MCP 调用失败）

- 自动回退到独立模式
- 输出首行标 `⚠ 降级模式（MCP 失败：原因）`
- 记录失败原因（超时/连接拒绝/Schema 不匹配等）

### 5.5 最终输出

无论哪种模式，最终输出都包含：
1. 模式标记（增强/独立/降级）
2. 状态机模型（YAML/JSON）
3. 完整性检查报告
4. 场景清单（10 类穷举）
5. （可选）Mermaid 状态图
6. （可选）覆盖度报告
7. 待确认项汇总（要求用户裁定）

---

## 转交 test-case-engineer（链 5 协同）

当用户原始请求包含"建模 + 用例"混合意图时，阶段 5 完成后由 testing-bundle 转交：

```
state-machine-test-engineer 输出：
  - 状态机模型
  - 场景清单（场景级）

↓ testing-bundle 链 5 转交 ↓

test-case-engineer 接收：
  - upstream_artifacts: 状态机模型 + 场景清单
  - downstream_task: 基于场景清单生成完整测试用例（每场景落实为可执行步骤）

test-case-engineer 输出：
  - 完整测试用例（用例步骤级）
```

转交时按 testing-bundle 定义的标准上下文 schema 传递，包含 `original_request` / `upstream_artifacts` / `completed_steps` / `downstream_task` 四个字段。

---

## 失败模式与 Fallback 速查

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 需求文本无状态信号 | 提示并询问是否继续/转 test-case-engineer | 标注「非状态型需求」，建议转 test-case-engineer |
| 状态机建模出现矛盾 | 标"待确认"暴露给用户，不强行消解 | 列出矛盾点，要求用户裁定（CHECKPOINT） |
| 完整性检查 fail | 触发 CHECKPOINT，不进入场景穷举 | 展示缺口报告，等用户补充后再继续 |
| MCP 探测失败 | 静默降级到独立模式 | 输出首行标 `⚠ 独立模式` |
| MCP 调用超时（>10s） | 单次重试，仍失败则降级 | 输出首行标 `⚠ 降级模式（超时）` |
| MCP 返回结果与 skill 严重冲突 | 不自动取舍，标"待确认"交给用户 | 列出差异，要求用户裁定 |
| 转交 test-case-engineer 失败 | 保留场景清单独立输出，提示用户手动衔接 | 标注「协同中断」，仅输出状态机模型 + 场景清单 |

---

**相关文档**：
- [SKILL.md](SKILL.md) - 入口索引
- [knowledge/state-modeling.md](knowledge/state-modeling.md) - 状态机建模方法论
- [knowledge/scenario-types.md](knowledge/scenario-types.md) - 10 类场景穷举规则
- [knowledge/completeness-check.md](knowledge/completeness-check.md) - 9 项检查清单
- [knowledge/anti-patterns.md](knowledge/anti-patterns.md) - 反模式黑名单
- [integrations/quickstart.md](integrations/quickstart.md) - MCP 配置说明
