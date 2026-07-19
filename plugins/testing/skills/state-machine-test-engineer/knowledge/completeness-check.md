# 完整性检查清单（9 项）

> **何时阅读**：阶段 3（完整性检查）执行时查阅。定义 9 项检查的判定条件、pass/fail/warn 规则、缺口/矛盾标记方式。
> **覆盖范围**：9 项检查 / 检查顺序 / overall_status 计算规则 / 缺口与矛盾的输出格式。
> **与 MCP 对齐**：本文件与 MCP Server `validate_state_machine` 工具的 9 项检查完全对齐，skill 自检与 MCP 校验使用相同规则。

## 1. 9 项检查总览

| # | 检查项 | 检查对象 | 默认状态 | fail 触发条件 |
|---|---|---|---|---|
| C1 | 每个状态有明确含义 | `states[].meaning` | pass | meaning 字段为空或为占位符 |
| C2 | 每个状态有进入条件（除初始态） | `transitions[].to` | pass | 非初始态无任何 transition 指向它 |
| C3 | 每个非终态有退出路径 | `transitions[].from` | pass | 非终态无任何 transition 从它出发 |
| C4 | 终态真的不可变化 | `transitions[].from` | pass | 终态出现在任何 transition 的 from |
| C5 | 禁止转换无遗漏 | `forbidden[]` + 业务规则 | warn | 无法自动判定，需人工审视 |
| C6 | 状态变化有副作用定义 | `transitions[].side_effects` | warn | transition 无 side_effects |
| C7 | 依据类型已标注 | `transitions[].evidence_type` | pass | 任何 transition/forbidden 缺 evidence_type |
| C8 | 无悬挂状态 | `states[]` 可达性 | warn | 状态无法从初始态到达 |
| C9 | 无死锁状态 | `states[]` 出边 | warn | 非终态无出边 |

## 2. overall_status 计算规则

```
overall_status =
  若任何检查为 fail → "fail"
  否则若任何检查为 warn → "warn"
  否则 → "pass"
```

| overall_status | 阶段 3 退出动作 |
|---|---|
| `pass` | 直接进入阶段 4 |
| `warn` | 列出 warning，询问用户是否继续（默认继续） |
| `fail` | **不进入阶段 4**，触发 CHECKPOINT 要求用户先修正 |

## 3. 各项检查详细规则

### C1: 每个状态有明确含义

**检查对象**：`states[].meaning`

**pass 条件**：
- meaning 字段非空
- meaning 不是占位符（如"TODO"/"待补充"/"未知"）

**fail 处理**：
- 在 `gaps[]` 中追加缺口，要求用户补充

**示例**：

```yaml
checks:
  - check_id: C1
    name: 每个状态有明确含义
    status: pass
    detail: ""
gaps: []
```

### C2: 每个状态有进入条件（除初始态）

**检查对象**：`transitions[].to` 与 `states[].name` 的对应关系

**pass 条件**：
- 初始态（`is_initial: true`）可无进入条件
- 非初始态至少有 1 条 transition 的 `to` 指向它

**fail 处理**：
- 标 `unreachable` warning（不直接 fail，因为可能是建模未完成）

**示例**：

```yaml
checks:
  - check_id: C2
    name: 每个状态有进入条件（除初始态）
    status: warn
    detail: 状态"退款失败"无任何 transition 指向，疑似悬挂
```

### C3: 每个非终态有退出路径

**检查对象**：`transitions[].from` 与 `states[].name` 的对应关系

**pass 条件**：
- 终态（`is_terminal: true`）可无退出路径（终态吸收）
- 非终态至少有 1 条 transition 的 `from` 是它

**fail 处理**：
- 标 `deadlock` warning（不直接 fail）

**示例**：

```yaml
checks:
  - check_id: C3
    name: 每个非终态有退出路径
    status: warn
    detail: 非终态"退款中"无任何 transition 从它出发，疑似死锁
```

### C4: 终态真的不可变化

**检查对象**：`states[].is_terminal` 与 `transitions[].from` 的冲突

**pass 条件**：
- 终态不出现在任何 transition 的 `from`

**fail 处理**：
- 标 `contradiction`，要求用户裁定（是终态定义错了，还是 transition 错了）

**示例**：

```yaml
checks:
  - check_id: C4
    name: 终态真的不可变化
    status: fail
    detail: 终态"退款成功"出现在 transition "退款成功 → 已支付" 的 from 位置，与终态定义冲突
contradictions:
  - id: CONTR-001
    description: 终态"退款成功"被定义为可转换到"已支付"
    suggestion: 检查是终态定义错误（退款成功后可恢复）还是 transition 错误（不应有此转换）
```

### C5: 禁止转换无遗漏

**检查对象**：`forbidden[]` 的完整性

**判定方式**：本项无法自动判定（业务规则可能很多），默认 `warn`，提示用户人工审视：

- 终态是否都加了"终态吸收"的 forbidden（`from: 终态, to: "*"`）
- 已知不可逆操作是否都加了 forbidden（如"已取消 → 已支付"）
- 是否有"看似合法但业务禁止"的转换未在 forbidden 中声明

**warn 处理**：
- 在 `suggestions[]` 中追加提示

**示例**：

```yaml
checks:
  - check_id: C5
    name: 禁止转换无遗漏
    status: warn
    detail: 需人工审视终态吸收规则与已知不可逆操作是否完整
suggestions:
  - 检查所有终态是否都加了"终态吸收"forbidden
  - 检查"已取消 → 已支付"等已知不可逆操作是否在 forbidden 中
```

### C6: 状态变化有副作用定义

**检查对象**：`transitions[].side_effects`

**pass 条件**：
- transition 有 side_effects 字段且非空

**warn 处理**：
- 无 side_effects 的 transition 标 warning（可能漏写副作用）

**示例**：

```yaml
checks:
  - check_id: C6
    name: 状态变化有副作用定义
    status: warn
    detail: transition "待支付 → 已取消（用户取消）" 无 side_effects，可能漏写"释放库存"等副作用
```

### C7: 依据类型已标注

**检查对象**：`transitions[].evidence_type` 和 `forbidden[].evidence_type`

**pass 条件**：
- 所有 transition 都有 evidence_type 且为合法枚举（需求明确/合理推理/待确认）
- 所有 forbidden 都有 evidence_type 且为合法枚举

**fail 处理**：
- 缺 evidence_type 是 Schema 违反（pydantic 校验会直接报错），标 `contradiction`

**说明**：本项是防幻觉机制的核心，pydantic Schema 已强制 evidence_type 必填，所以本项 fail 极少发生（除非手动绕过 Schema）。

### C8: 无悬挂状态

**检查对象**：从初始态出发的可达性图

**pass 条件**：
- 所有状态都可从初始态通过若干 transition 到达

**warn 处理**：
- 不可达状态标 `unreachable` warning

**示例**：

```yaml
checks:
  - check_id: C8
    name: 无悬挂状态
    status: warn
    detail: 状态"退款失败"从初始态"待支付"不可达，可能是建模遗漏了某条 transition
```

### C9: 无死锁状态

**检查对象**：非终态的出边

**pass 条件**：
- 所有非终态至少有 1 条 transition 从它出发

**warn 处理**：
- 非终态无出边标 `deadlock` warning（注意：终态无出边是正常的，不报 warning）

**与 C3 的关系**：C3 和 C9 检查的是同一件事（非终态有无出边），只是表述角度不同。skill 实际执行时只做一次检查，同时填 C3 和 C9 的状态。

## 4. 缺口（gap）输出格式

```yaml
gaps:
  - id: GAP-001
    description: 退款失败后的恢复路径未定义
    evidence_type: 待确认
    suggestion: 需澄清退款失败后是否允许重新发起退款
    related_state: 退款失败
    related_check: C3
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✅ | GAP-{三位序号} |
| `description` | ✅ | 缺口描述 |
| `evidence_type` | ✅ | 通常为"待确认" |
| `suggestion` | 可选 | 建议的澄清方向 |
| `related_state` | 可选 | 相关状态名 |
| `related_check` | 可选 | 相关检查项 ID（C1-C9） |

## 5. 矛盾（contradiction）输出格式

```yaml
contradictions:
  - id: CONTR-001
    description: 终态"退款成功"被定义为可转换到"已支付"
    severity: high
    suggestion: 检查是终态定义错误还是 transition 错误
    related_states: [退款成功, 已支付]
    related_check: C4
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✅ | CONTR-{三位序号} |
| `description` | ✅ | 矛盾描述 |
| `severity` | ✅ | high/medium/low |
| `suggestion` | ✅ | 建议的解决方向 |
| `related_states` | 可选 | 相关状态名列表 |
| `related_check` | 可选 | 相关检查项 ID |

## 6. 与 MCP validate_state_machine 的对齐

本文件的 9 项检查与 MCP Server `validate_state_machine` 工具的 9 项检查**完全对齐**：

| 检查项 | skill 自检 | MCP 校验 | 差异处理 |
|---|---|---|---|
| C1-C9 | skill 阶段 3 执行 | MCP validate_state_machine 执行 | 增强模式下两者都执行，差异项标"待确认" |

**对齐原则**：
- skill 自检先执行（独立模式也能跑）
- 增强模式下 MCP 校验作为交叉复核，差异不自动取舍
- 若 MCP 返回 fail 但 skill 自检 pass，触发 CHECKPOINT 让用户裁定

## 7. 反模式（详见 anti-patterns.md）

| 反模式 | 说明 |
|---|---|
| 跳过 C5（禁止转换无遗漏） | C5 无法自动判定，但跳过会导致大量非法转换漏测 |
| 把 C8 unreachable 直接当 fail | unreachable 可能是建模未完成，warn 即可，不要阻塞 |
| 把 C9 deadlock 当 fail | 同上，deadlock 也可能是建模未完成 |
| 不输出 contradictions | contradictions 是 fail 项，必须列出供用户裁定 |

---

**相关文档**：
- [state-modeling.md](state-modeling.md) - 状态机建模方法论
- [scenario-types.md](scenario-types.md) - 10 类场景穷举规则
- [anti-patterns.md](anti-patterns.md) - 反模式黑名单
- [../state-machine-core.md](../state-machine-core.md) - 核心流程详述
