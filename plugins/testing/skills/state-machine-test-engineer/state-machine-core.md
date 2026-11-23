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

状态机模型必须符合 `knowledge/state-modeling.md` 中定义的 6 要素 + MAE + 不变量结构。以下示例同时作为 skill 与 MCP 的结构协作契约：

```yaml
state_machine:
  meta:
    object: Order
    version: "1.0"
    source: 示例需求 PRD §3.2
    confidence: medium
  states:
    - name: 待支付
      meaning: 订单已创建未支付
      is_initial: true
      entry_events: [订单创建]
      invariants: [订单金额不可修改]
    - name: 已支付
      meaning: 已收到可信支付结果
      is_terminal: true
      invariants: [支付金额与订单一致]
  transitions:
    - id: T-PAY
      from: 待支付
      to: 已支付
      event: 支付成功回调
      guards: [订单有效, 金额一致, 回调可信]
      side_effects: [生成支付记录, 触发履约]
      evidence_type: 需求明确
      source: 示例需求 PRD §3.2
  forbidden:
    - id: F-PAID
      from: 已支付
      to: "*"
      reason: 示例中已支付为终态
      evidence_type: 需求明确
```

### 2.4 🔴 CHECKPOINT

阶段 2 输出后展示模型与未决事项，已有依据的部分继续结构检查：

- 显示完整状态机模型（状态/转换/禁止/不变量）
- 列出所有"待确认"项
- 仅缺少影响结论的关键信息、范围变化或未授权写操作时询问

**CHECKPOINT 规则**：用户修改/补充 → 更新模型后重新展示；无阻塞信息 → 阶段 3；用户终止 → 输出当前模型，不进入后续阶段。

---

## 阶段 3: 完整性检查（C0 结构检查 + 9 项业务检查）

### 3.1 目标

对状态机模型做 9 项结构化检查，标记缺口/矛盾/警告，**不修复**（修复由用户决定）。

### 3.2 检查清单

完整判定见 [knowledge/completeness-check.md](knowledge/completeness-check.md)。先做 C0 结构检查，再做 9 项业务检查；每项输出 `pass/warn/fail + detail`，结构校验不能代替业务完整性。

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

`not_checked` 不参与机器通过／失败判定；`manual_review_required` 记录仍需对照需求审阅的事项。

### 3.4 退出条件

- `overall_status = pass` → 直接进入阶段 4
- `overall_status = warn` → 列出风险，继续有依据的场景；不把警告当作已确认需求
- `overall_status = fail` → 先按已确认资料修正结构；不能确认的部分暂停依赖场景，交付缺口与已有结论

---

## 阶段 4: 10 类场景穷举

### 4.1 目标

基于状态机模型先判断十类适用性，再对适用转换生成场景；不适用类不凑数，未知项单列依据缺口。每场景标注依据类型。**只输出场景级**，不出用例步骤（用例步骤由 test-case-engineer 落地）。

### 4.2 10 类场景生成规则

完整生成规则与示例见 [knowledge/scenario-types.md](knowledge/scenario-types.md)。先逐类判定 `applicable / not_applicable / unknown`，再对适用转换生成场景：

- 合法/非法：每条 transition / forbidden 各 1 个
- 守卫/幂等/并发/乱序/超时/一致性/越权/失败恢复：按转换特征命中才生成
- 并发、消息、提交边界等未知条件 → `待确认`，不补造

### 4.3 输出格式

完整场景 Schema 和可校验示例见 [knowledge/scenario-types.md](knowledge/scenario-types.md)。每条场景必须包含：
- `id`（SM-001 起编）
- `risk_type`（10 类枚举之一）
- `evidence_type`（需求明确/合理推理/待确认）
- `source`（PRD 章节 + 推理依据）

### 4.4 退出条件

- 十类均记录 `applicable / not_applicable / unknown`、理由、来源及缺失信息；全部适用类型已处理，未知项附待确认说明，不强行每类一条
- 所有场景都有 `evidence_type` 标注
- 所有"PRD 未说明"的场景都标 `evidence_type: 待确认`

---

## 阶段 5: MCP 增强（可选）

MCP 可用性探测、增强模式交叉复核、独立模式与降级模式的细则见 [knowledge/mcp-enhancement.md](knowledge/mcp-enhancement.md)（仅宿主暴露 MCP 工具或用户要求增强时读）。

## 最终输出

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

混合意图「建模 + 用例」由 testing-bundle 链 5 转交：上游交付状态机模型 + 场景清单；下游按场景生成步骤级用例。按标准上下文 schema 传递 `original_request` / `upstream_artifacts` / `completed_steps` / `downstream_task`；转交失败时保留场景清单独立输出并标注「协同中断」。

---

**相关文档**：
- [SKILL.md](SKILL.md) - 入口索引
- [knowledge/state-modeling.md](knowledge/state-modeling.md) - 建模方法论
- [knowledge/scenario-types.md](knowledge/scenario-types.md) - 10 类场景穷举规则
- [knowledge/completeness-check.md](knowledge/completeness-check.md) - 9 项检查清单
- [knowledge/anti-patterns.md](knowledge/anti-patterns.md) - 反模式黑名单
- [integrations/quickstart.md](integrations/quickstart.md) - MCP 配置说明
