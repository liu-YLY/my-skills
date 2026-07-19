# State Machine Testing 设计：state-machine-test-engineer + MCP Server

- **日期**：2026-07-18
- **状态**：已通过 brainstorming 五节确认，待 spec 自检 + 用户审阅
- **路线**：Skill + MCP 双形态，Skill 为独立 peer，MCP 为可选增强
- **目标**：将 testing-bundle 从 4-skill（v2.0.0）扩展到 5-skill（v3.0.0），新增 state-machine-test-engineer 作为独立 peer，并配套 Python MCP Server 作为可选执行引擎
- **灵感来源**：Treeify「状态机提升 AI 测试质量」方法论（订单生命周期案例）

---

## 1. 整体架构与 bundle 路由

### 1.1 双形态架构

```
                    用户测试请求
                         │
                         ▼
              ┌─────────────────────────┐
              │   testing-bundle v3.0.0 │  路由层（5-way）
              └───────────┬─────────────┘
                          │
        ┌─────────┬───────┼───────┬───────────┬──────────────┐
        ▼         ▼       ▼       ▼           ▼
   ┌─────────┐┌─────┐┌─────┐┌──────────┐┌──────────────────┐
   │strategy ││case ││bug  ││performance││state-machine     │
   │-engineer││-eng ││-anlz││-engineer  ││-test-engineer    │
   │ v1.0.0  ││v8.1 ││v1.0 ││ v1.0.0    ││ v1.0.0 (新增)    │
   └─────────┘└─────┘└─────┘└──────────┘└──────────────────┘
                                                  │
                                          ┌───────┴───────┐
                                          ▼               ▼
                                   ┌────────────┐  ┌──────────────┐
                                   │ Skill 主体  │  │ MCP Server   │
                                   │ (markdown)  │←→│ (Python)     │
                                   │ 方法论+知识库│  │ 可选增强      │
                                   └────────────┘  └──────────────┘
                                   独立可用         未安装时降级
```

### 1.2 bundle v2.0.0 → v3.0.0 演进

| 维度 | v2.0.0（现状） | v3.0.0（目标） |
|---|---|---|
| 子 skill 数 | 4 | 5（+ state-machine-test-engineer） |
| 路由 | 4-way | 5-way（+ 状态机信号） |
| 混合意图链 | 4 条 | +1 条（state-machine → case-engineer） |
| MCP 集成 | 无 | state-machine 内置可选 MCP |
| version | 2.0.0 | 3.0.0（breaking：路由表扩展） |

### 1.3 5-way 路由决策表（新增行）

| 用户意图关键词 | 路由到 | 说明 |
|---|---|---|
| 状态机、状态流转、状态转换、生命周期、非法跳转、幂等、并发冲突、消息乱序、状态回退、幽灵状态、终态吸收 | **state-machine-test-engineer** | 状态型需求 |
| （原有 4 行保留） | ... | test-strategy / test-case / bug-analyzer / performance |

### 1.4 新增混合意图链（链 5）

```
链 5：状态机建模 + 用例生成
步骤 1: 路由到 state-machine-test-engineer 执行状态机建模
步骤 2: state-machine 输出状态机模型 + 场景清单（含依据类型标注）
        ↓
🔴 CHECKPOINT · 状态机模型展示给用户确认（可修改/补充/终止）
        ↓
步骤 3: 转交 test-case-engineer 基于场景清单生成完整用例
步骤 4: 输出最终报告（状态机模型 + 完整测试用例）
```

### 1.5 与现有 skill 的边界

| 维度 | state-machine-test-engineer | test-case-engineer |
|---|---|---|
| 触发条件 | 有明确状态/生命周期信号 | 通用功能测试 |
| 方法论 | MAE + State Machine 状态网络穷举 | 四阶段功能点覆盖 |
| 输入 | 状态型需求（订单/审批/工单/会员等） | 任意功能需求 |
| 输出 | 状态机模型 + 10 类场景清单 | 完整测试用例 |
| 输出粒度 | 场景级（含依据类型标注） | 用例步骤级 |
| 关系 | 上游（出场景清单） | 下游（基于清单落用例） |

**关键决策**：state-machine-test-engineer **不直接输出用例步骤**，只输出"场景清单"（每场景含：当前状态/触发事件/前置条件/预期目标/禁止状态/风险类型/依据类型）。用例步骤由 test-case-engineer 基于清单生成，避免职责重叠。

---

## 2. state-machine-test-engineer skill 设计

### 2.1 Scope 边界

**包含**：
- 状态型需求的状态机建模（识别状态/事件/转换/守卫/不变量/禁止转换）
- 基于 MAE（主流程/替代流程/异常流程）+ State Machine 的 10 类场景穷举
- 场景清单输出（含依据类型标注：需求明确/合理推理/待确认）
- 歧义暴露（PRD 缺权限/异常路径时标"待确认"，禁止自行补齐）
- 可选调用 MCP Server 做 Schema 校验与可视化

**不包含**：
- 用例步骤级输出（转交 test-case-engineer）
- 性能测试方案（转交 performance-test-engineer）
- Bug 根因分析（转交 bug-analyzer）
- 项目级测试策略（转交 test-strategy-engineer）

### 2.2 工作流（五阶段）

```
阶段 1: 状态型需求识别
  → 识别业务对象（订单/审批/工单/会员等）
  → 识别参与者（人/系统/外部/定时器/管理员）
  → 标记歧义为"待确认"（不补齐）
  → 输出：状态型需求摘要 + 业务对象清单
  ↓
阶段 2: 状态机建模
  → 抽取状态（只保留名词，避免动词状态）
  → 定义转换：FROM --(事件 [守卫])--> TO {副作用}
  → 定义不变量与终态（终态吸收规则）
  → 定义禁止转换
  → 输出：状态机模型（YAML/JSON 结构）
  ↓
🔴 CHECKPOINT · 状态机模型展示给用户确认（可修改/补充/终止）
  ↓
阶段 3: 完整性检查（9 项，与 MCP validate_state_machine 对齐）
  → 每个状态有明确含义？
  → 每个状态有进入条件（除初始态）？
  → 每个非终态有退出路径？
  → 终态是否真的不可变化（无出边）？
  → 禁止转换是否明确无遗漏？
  → 状态变化有副作用定义？
  → 依据类型已标注（无遗漏）？
  → 无悬挂状态（unreachable）？
  → 无死锁状态（非终态但无出边）？
  → 输出：完整性检查报告（标记缺口）
  ↓
阶段 4: 10 类场景穷举
  → 对每条 transition 生成：
    1. 合法转换  2. 非法转换  3. 条件不满足
    4. 重复事件与幂等  5. 并发事件  6. 消息乱序
    7. 超时与重试  8. 转换后数据一致性
    9. 权限控制  10. 失败后恢复路径
  → 每场景标注依据类型（需求明确/合理推理/待确认）
  → 输出：场景清单（场景级，不出用例步骤）
  ↓
阶段 5: MCP 增强（可选）
  → 检测 MCP Server 可用性
  → 可用：调用 validate_state_machine 校验 + generate_scenarios 复核
  → 不可用：降级为纯 LLM 推理（在输出首行标注「MCP 未启用，结果未校验」）
  → 输出：最终状态机模型 + 场景清单（含校验状态标记）
```

### 2.3 知识库结构

```
state-machine-test-engineer/
├── SKILL.md                          # 主入口（v1.0.0）
├── README.md                         # 与 SKILL.md 同步
├── state-machine-core.md             # 核心流程详述
├── knowledge/
│   ├── state-modeling.md             # 状态机建模方法论（6 要素 + MAE + 不变量 + 终态）
│   ├── scenario-types.md             # 10 类场景穷举规则与示例
│   ├── completeness-check.md         # 完整性检查清单（9 项，与 MCP 对齐）
│   ├── anti-patterns.md              # 反模式黑名单
│   ├── industry-templates/           # 行业状态机模板
│   │   ├── order-refund.md           # 订单退款（文章案例）
│   │   ├── approval-flow.md          # 审批流
│   │   ├── membership.md             # 会员状态
│   │   └── ticket.md                 # 工单状态
│   └── products/                     # 产品专项知识
│       ├── README.md
│       └── products-template.md
├── integrations/
│   └── quickstart.md                 # MCP 配置说明
└── test-prompts.json                 # darwin-skill 验证用
```

### 2.4 核心数据结构：状态机模型 Schema

skill 输出的状态机模型遵循固定结构（与 MCP Server Schema 一致）：

```yaml
state_machine:
  meta:
    object: Order                      # 业务对象
    version: 1.0
    source: 需求文档/PRD/口头描述
    confidence: high/medium/low
  states:
    - name: 待支付
      meaning: 订单已创建未支付
      is_terminal: false
      entry_events: [订单创建]
      invariants: [订单金额不可修改]
    - name: 退款成功
      is_terminal: true
      invariants: [退款金额不可再修改]
  transitions:
    - from: 待支付
      to: 已支付
      event: 支付成功回调
      guards: [订单有效, 金额一致, 回调可信]
      side_effects: [生成支付记录, 触发履约]
      evidence_type: 需求明确           # 需求明确/合理推理/待确认
      source: PRD §3.2
  forbidden:
    - from: 退款成功
      to: 任何状态
      reason: 终态吸收
    - from: 已取消
      to: 已支付
      reason: 已取消订单不可支付
  completeness_checks:
    - check: 每个非终态有退出路径
      status: pass/fail
      detail: 退款中缺少超时转人工路径
```

### 2.5 场景清单输出格式

每条场景遵循固定 schema（这是转交 test-case-engineer 的契约）：

```yaml
scenarios:
  - id: SM-001
    title: 已取消订单尝试支付
    current_state: 已取消
    trigger_event: 支付成功回调
    precondition: 订单已取消
    expected_target_state: 已取消（保持不变）
    forbidden_states: [已支付]
    risk_type: illegal_transition
    related_objects: [支付记录, 订单日志]
    evidence_type: 需求明确
    source: PRD §3.1 + 状态机 forbidden 规则
    notes: 需验证后端拒绝 + 前端按钮置灰
```

### 2.6 关键设计决策

1. **场景清单是契约**——state-machine 输出场景级，test-case-engineer 基于场景落步骤，避免两者都写用例导致重叠
2. **依据类型强制标注**——每条 transition 和场景必须标 `需求明确/合理推理/待确认`，Schema 约束非 prompt 建议，防幻觉
3. **歧义暴露而非补齐**——PRD 缺权限/异常路径时必须输出"待确认"节点，禁止 LLM 自行脑补管理员逻辑
4. **完整性检查独立成阶段**——不混在建模里，强制人工审视缺口（终态吸收/退出路径/副作用）
5. **行业模板独立**——不与 test-case-engineer 共享产品知识，聚焦点不同（状态网络 vs 功能点）
6. **MCP 可选增强**——skill 自身完整可用，MCP 仅做 Schema 校验和可视化增强

---

## 3. MCP Server 工具集与 Schema 设计

### 3.1 Server 定位

**名称**：`state-machine-testing-mcp`
**版本**：v0.1.0（首版）
**技术栈**：Python 3.11+ / `mcp` 官方 SDK / pydantic v2 做 Schema 校验
**传输**：stdio（本地默认）+ HTTP/SSE（远端可选）
**部署**：与 testing-bundle 同仓，位于 `plugins/testing/mcp-servers/state-machine-testing/`
**本质**：自己写给自己用的 MCP Server，让纯 markdown 的 skill 能调用 Python 写的确定性计算逻辑（Schema 校验/穷举/覆盖度），不依赖 LLM 推理这些本该确定的事

### 3.2 工具集（5 个工具，对应中等版范围）

| 工具名 | 用途 | 输入 | 输出 |
|---|---|---|---|
| `build_state_machine` | 从需求文本构建状态机模型 | 需求文本/PRD 片段 | StateMachine Schema（YAML/JSON） |
| `validate_state_machine` | 校验状态机完整性与一致性 | StateMachine Schema | ValidationReport（含缺口/矛盾/警告） |
| `generate_scenarios` | 基于状态机穷举 10 类场景 | StateMachine Schema | ScenarioList（场景清单） |
| `export_artifacts` | 导出为 Markdown / JSON / Mermaid | StateMachine + Scenarios | 文件路径 |
| `check_coverage` | 覆盖度检查（转换覆盖率/场景类型覆盖率） | StateMachine + Scenarios | CoverageReport |

**未实现**（留给完整版）：节点树存储、Note 增量重算、多 Agent 分工

### 3.3 工具详设

#### Tool 1: `build_state_machine`

```python
@mcp.tool()
def build_state_machine(
    requirement: str,                    # 需求文本（PRD/用户描述）
    object_hint: str | None = None,      # 可选业务对象提示（如 "Order"）
    industry_template: str | None = None # 可选行业模板（order-refund/approval/...）
) -> StateMachineBuildResult:
    """
    从需求文本构建状态机模型。
    流程：抽取状态 → 识别事件 → 建立转换 → 标注守卫/副作用/依据类型 → 完整性预检
    """
```

**返回结构**：
```python
class StateMachineBuildResult(BaseModel):
    state_machine: StateMachine          # 状态机模型（见 3.4 Schema）
    extracted_objects: list[str]         # 识别到的业务对象
    ambiguities: list[Ambiguity]         # 待确认项（强制暴露，不补齐）
    mermaid_diagram: str                 # Mermaid 状态图（可视化）
    build_notes: str                     # 构建说明
```

#### Tool 2: `validate_state_machine`

```python
@mcp.tool()
def validate_state_machine(
    state_machine: StateMachine,
    strict: bool = True                  # 严格模式：终态吸收/禁止转换必检
) -> ValidationReport:
    """
    校验状态机完整性与一致性。检查项：
    1. 每个状态有明确含义
    2. 每个状态有进入条件（除初始态）
    3. 每个非终态有退出路径
    4. 终态真的不可变化（无出边）
    5. 禁止转换无遗漏（覆盖所有非法跳转）
    6. 状态变化有副作用定义
    7. 依据类型已标注（无遗漏）
    8. 无悬挂状态（unreachable）
    9. 无死锁状态（deadlock，非终态但无出边）
    """
```

**返回结构**：
```python
class ValidationReport(BaseModel):
    overall_status: Literal["pass", "fail", "warn"]
    checks: list[CheckItem]
    gaps: list[Gap]                      # 缺口清单
    contradictions: list[Contradiction]  # 矛盾清单
    suggestions: list[str]
```

#### Tool 3: `generate_scenarios`

```python
@mcp.tool()
def generate_scenarios(
    state_machine: StateMachine,
    scenario_types: list[str] | None = None,  # 默认全部 10 类
    evidence_filter: str | None = None        # 按依据类型过滤
) -> ScenarioList:
    """
    基于状态机穷举测试场景。
    10 类：legal_transition / illegal_transition / guard_violation /
           idempotency / concurrency / message_reorder / timeout_retry /
           data_consistency / access_control / failure_recovery
    """
```

**返回结构**（与 skill 场景清单 schema 一致）：
```python
class ScenarioList(BaseModel):
    scenarios: list[Scenario]
    coverage_summary: CoverageSummary      # 类型覆盖率统计
    pending_confirmation: list[Scenario]  # 待确认场景子集
```

#### Tool 4: `export_artifacts`

```python
@mcp.tool()
def export_artifacts(
    state_machine: StateMachine,
    scenarios: ScenarioList | None = None,
    formats: list[Literal["markdown", "json", "mermaid"]],
    output_dir: str = "./state-machine-outputs"
) -> ExportResult:
    """导出状态机模型与场景清单为多种格式。"""
```

#### Tool 5: `check_coverage`

```python
@mcp.tool()
def check_coverage(
    state_machine: StateMachine,
    scenarios: ScenarioList
) -> CoverageReport:
    """
    覆盖度检查：
    - transition_coverage: 每条转换至少有 1 个合法场景
    - forbidden_coverage: 每条禁止转换至少有 1 个非法场景
    - scenario_type_coverage: 10 类场景类型分布
    - evidence_distribution: 依据类型分布（需求明确/合理推理/待确认）
    """
```

### 3.4 核心数据结构 Schema（pydantic）

```python
from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum

class EvidenceType(str, Enum):
    EXPLICIT = "需求明确"        # PRD 明确说明
    INFERRED = "合理推理"        # 业务常识推理
    PENDING = "待确认"           # PRD 未说明，需澄清

class State(BaseModel):
    name: str
    meaning: str
    is_terminal: bool = False
    is_initial: bool = False
    entry_events: list[str] = []
    invariants: list[str] = []

class Transition(BaseModel):
    from_state: str
    to_state: str
    event: str
    guards: list[str] = []               # 守卫条件
    side_effects: list[str] = []         # 副作用
    evidence_type: EvidenceType
    source: str = ""                     # PRD 章节引用

class ForbiddenTransition(BaseModel):
    from_state: str
    to_state: str | Literal["*"]         # * 表示任意状态
    reason: str
    evidence_type: EvidenceType

class StateMachine(BaseModel):
    meta: "StateMachineMeta"
    states: list[State]
    transitions: list[Transition]
    forbidden: list[ForbiddenTransition] = []

class Scenario(BaseModel):
    id: str                              # SM-001
    title: str
    current_state: str
    trigger_event: str
    precondition: str
    expected_target_state: str
    forbidden_states: list[str]
    risk_type: Literal[
        "legal_transition", "illegal_transition",
        "guard_violation", "idempotency",
        "concurrency", "message_reorder",
        "timeout_retry", "data_consistency",
        "access_control", "failure_recovery"
    ]
    related_objects: list[str]
    evidence_type: EvidenceType
    source: str
    notes: str = ""
```

### 3.5 目录结构

```
plugins/testing/mcp-servers/state-machine-testing/
├── pyproject.toml                      # 依赖：mcp, pydantic>=2
├── README.md                           # 安装与配置
├── src/
│   └── state_machine_testing_mcp/
│       ├── __init__.py
│       ├── server.py                   # MCP Server 入口（注册 5 个工具）
│       ├── schemas.py                  # pydantic 模型（3.4）
│       ├── builders.py                 # build_state_machine 实现
│       ├── validators.py               # validate_state_machine 实现
│       ├── generators.py               # generate_scenarios 实现
│       ├── exporters.py                # export_artifacts 实现
│       ├── coverage.py                 # check_coverage 实现
│       └── prompts/                    # LLM 提示词模板（构建器内部用）
│           ├── extract_states.txt
│           ├── identify_transitions.txt
│           └── generate_scenarios.txt
└── tests/
    ├── unit/
    │   ├── test_schemas.py
    │   ├── test_validators.py
    │   ├── test_generators.py
    │   ├── test_exporters.py
    │   └── test_coverage.py
    ├── integration/
    │   ├── test_mcp_protocol.py
    │   ├── test_end_to_end.py
    │   └── test_skill_integration.py
    └── fixtures/
        ├── order_refund_state_machine.json
        ├── approval_flow_state_machine.json
        ├── membership_state_machine.json
        ├── ticket_state_machine.json
        └── buggy_state_machines/
            ├── deadlock.json
            ├── unreachable.json
            └── missing_evidence.json
```

### 3.6 关键设计决策

1. **不依赖外部 LLM**——Server 自身只做 Schema 校验、转换穷举、覆盖度统计等**确定性计算**，LLM 推理留给 skill。这让 Server 可离线运行、可单测、可复现。`build_state_machine` 例外，它内部会调用 LLM 做需求解析。
2. **Schema 双向兼容**——pydantic Schema 与 skill 输出的 YAML/JSON 严格对齐，skill 可直接把模型喂给 MCP 工具，反之亦然。
3. **Mermaid 内置**——状态图导出是高频需求，Server 直接生成 Mermaid 代码，避免用户手画。
4. **依据类型强制**——Transition 和 Scenario 的 `evidence_type` 是必填字段，pydantic 会在校验时报错，从机制上防幻觉。
5. **5 个工具单一职责**——构建/校验/穷举/导出/覆盖度各司其职，便于独立测试和组合使用。

---

## 4. Skill/MCP 协作与降级策略

### 4.1 三种运行模式

skill 在每次执行时先探测 MCP 可用性，根据结果选择运行模式：

| 模式 | 触发条件 | 行为 | 输出标记 |
|---|---|---|---|
| **增强模式** | MCP 可用 | skill 自身推理 + 调用 MCP 做校验/穷举/可视化复核 | 输出首行标 `✓ MCP 增强模式` |
| **独立模式** | MCP 未安装 | skill 纯 LLM 推理执行全流程 | 输出首行标 `⚠ 独立模式（未校验）` |
| **降级模式** | MCP 调用失败 | 自动回退到独立模式，记录失败原因 | 输出首行标 `⚠ 降级模式（MCP 失败：原因）` |

### 4.2 MCP 可用性探测

skill 在阶段 5（MCP 增强）执行前做一次轻量探测，**不阻塞主流程**：

```
探测方式：
1. 检查环境变量 STATE_MACHINE_MCP_ENABLED=true（用户显式启用）
2. 检查配置文件 ~/.trae/state-machine-mcp.json 存在
3. 任一为真 → 尝试调用 validate_state_machine 做空载测试
4. 探测失败 → 自动进入独立模式，不报错

探测结果缓存在 skill 上下文，单次会话内不重复探测
```

### 4.3 增强模式下的协作流程

skill 五阶段中，阶段 1-2 由 skill 独立完成，阶段 3-5 与 MCP 协作：

```
阶段 1-2: skill 构建 StateMachine Schema（LLM 推理）
         ↓
阶段 3: skill 调用 MCP validate_state_machine 做完整性校验
         → MCP 返回 ValidationReport
         → skill 把缺口/矛盾追加到自己的完整性检查报告
         → 若 validation_status=fail，触发 CHECKPOINT 让用户先修正
         ↓
阶段 4: skill 自身生成场景清单（10 类穷举）
         → 同时调用 MCP generate_scenarios 做交叉复核
         → 对比两份清单，标记差异（多/少/矛盾）
         → 差异项标 evidence_type=待确认，交给用户裁定
         ↓
阶段 5: 调用 MCP export_artifacts 生成 Mermaid 状态图 + Markdown 报告
         → 调用 MCP check_coverage 输出覆盖度报告
         → skill 把覆盖度报告追加到最终输出
```

**关键点**：MCP 是**复核器**而非生成器。skill 的输出不被 MCP 覆盖，MCP 只提供校验报告和交叉复核差异，最终结果以 skill 为准（除非用户明确采纳 MCP 修正建议）。

### 4.4 降级策略矩阵

| MCP 状态 | 阶段 3（完整性检查） | 阶段 4（场景穷举） | 阶段 5（导出/覆盖度） |
|---|---|---|---|
| 增强模式 | MCP 校验 + skill 自检双重 | skill 穷举 + MCP 复核 | MCP 导出 + 覆盖度报告 |
| 独立模式 | skill 内置 9 项自检 | skill 穷举（无复核） | skill 手写 Mermaid + 简单统计 |
| 降级模式 | 同独立模式 + 记录失败原因 | 同独立模式 | 同独立模式 |

### 4.5 Skill 调用 MCP 的方式

skill 是纯 markdown，自身不能直接发 JSON-RPC。实际执行时通过 Trae 的 MCP 客户端能力间接调用：

```
skill 在文档中写入指令：
  "调用 MCP 工具 validate_state_machine，传入 state_machine={...}"
  ↓
Trae 宿主识别该指令（通过 SKILL.md 中的 integration 声明）
  ↓
Trae 调用已注册的 state-machine-testing MCP Server
  ↓
返回结果给 skill 上下文，skill 继续推理
```

**实现要点**：
- SKILL.md 中声明 `integrations.mcp_servers: [state-machine-testing]`
- 调用指令用结构化代码块包裹，便于宿主解析
- 失败时 skill 内置 fallback 逻辑（不依赖宿主错误处理）

### 4.6 配置接口

用户在 `~/.trae/state-machine-mcp.json` 中配置（可选）：

```json
{
  "enabled": true,
  "transport": "stdio",
  "command": "python",
  "args": ["/path/to/state-machine-testing-mcp/src/server.py"],
  "fallback_on_error": true,
  "log_level": "warn"
}
```

未配置时 skill 默认进入独立模式，不报错。

### 4.7 一致性保证

无论哪种模式，输出格式**完全一致**：

| 输出项 | 增强模式 | 独立模式 | 差异 |
|---|---|---|---|
| 状态机模型 Schema | ✓ | ✓ | 无 |
| 场景清单 | ✓ | ✓ | 独立模式无 MCP 复核差异标记 |
| 完整性检查报告 | ✓ | ✓ | 独立模式只含 skill 自检项 |
| Mermaid 状态图 | MCP 生成 | skill 手写 | 可能样式略差 |
| 覆盖度报告 | MCP 详细 | skill 简单统计 | 独立模式粒度较粗 |
| 依据类型标注 | ✓ | ✓ | 无（强制必填） |

下游 test-case-engineer **无需关心上游是哪种模式**，只消费场景清单 schema。

### 4.8 关键设计决策

1. **skill 始终是主，MCP 是辅**——MCP 校验失败不影响 skill 输出，只追加警告。这保证 skill 永远可用，符合"Skill 为主、MCP 可选增强"的决策。
2. **MCP 是复核器不是生成器**——避免 skill 和 MCP 各出一份结果让用户困惑。skill 出结果，MCP 出校验报告，差异标"待确认"。
3. **探测不阻塞**——MCP 不可用时直接降级，不让用户等超时。
4. **输出格式跨模式一致**——下游 test-case-engineer 无需感知上游模式，简化混合意图链实现。
5. **配置可选**——不强制用户安装 MCP，零配置也能用 skill。

---

## 5. 错误处理、测试、darwin-skill 验证

### 5.1 错误处理矩阵

#### Skill 侧错误处理

| 错误场景 | 处理策略 | 用户可见输出 |
|---|---|---|
| 需求文本无状态信号 | 提示并询问是否继续/转 test-case-engineer | "未检测到状态型需求特征，建议转通用用例生成。是否继续？" |
| 状态机建模出现矛盾 | 标"待确认"暴露给用户，不强行消解 | 列出矛盾点，要求用户裁定 |
| 完整性检查失败（缺口/死锁） | 触发 CHECKPOINT，不进入场景穷举 | 展示缺口报告，等用户补充 |
| MCP 探测失败 | 静默降级到独立模式 | 输出首行标 `⚠ 独立模式` |
| MCP 调用超时（>10s） | 单次重试，仍失败则降级 | 输出首行标 `⚠ 降级模式（超时）` |
| MCP 返回结果与 skill 严重冲突 | 不自动取舍，标"待确认"交给用户 | 列出差异，要求用户裁定 |
| 转交 test-case-engineer 失败 | 保留场景清单独立输出，提示用户手动衔接 | "已生成场景清单，转交失败，请手动调用 test-case-engineer" |

#### MCP Server 侧错误处理

| 错误场景 | 处理策略 | 返回码 |
|---|---|---|
| Schema 校验失败 | 返回详细错误清单（字段路径+原因） | 400 + ValidationError |
| 状态机含死锁状态 | 标 warning，不拒绝执行 | 200 + warnings[] |
| 状态机含悬挂状态 | 标 warning，不拒绝执行 | 200 + warnings[] |
| 状态机为空 | 拒绝执行 | 400 + EmptyInputError |
| generate_scenarios 输入 scenario_types 含未知类型 | 忽略未知类型，标 warning | 200 + warnings[] |
| export_artifacts 输出目录无写权限 | 返回错误，建议备选目录 | 400 + PermissionError |
| 内部 LLM 调用失败（build_state_machine） | 返回错误 + 原始异常 | 500 + LLMError |
| 未捕获异常 | 返回 500 + 通用错误信息 + trace_id | 500 + InternalError |

### 5.2 测试策略

#### MCP Server 测试（Python）

```
tests/
├── unit/                          # 单元测试（90%+ 覆盖率目标）
│   ├── test_schemas.py            # pydantic 模型校验
│   ├── test_validators.py         # 完整性检查 9 项
│   ├── test_generators.py         # 10 类场景穷举
│   ├── test_exporters.py          # Markdown/JSON/Mermaid 导出
│   └── test_coverage.py           # 覆盖度计算
├── integration/                   # 集成测试
│   ├── test_mcp_protocol.py       # JSON-RPC 协议合规
│   ├── test_end_to_end.py         # 需求→模型→场景→导出 全链路
│   └── test_skill_integration.py  # 与 skill 协作（mock）
└── fixtures/
    ├── order_refund_state_machine.json   # 文章案例
    ├── approval_flow_state_machine.json
    ├── membership_state_machine.json
    ├── ticket_state_machine.json
    └── buggy_state_machines/             # 故意有问题的样本
        ├── deadlock.json
        ├── unreachable.json
        └── missing_evidence.json
```

**测试用例覆盖目标**：
- 4 个行业模板各至少 1 个完整端到端用例
- 9 项完整性检查每项至少 1 个 pass + 1 个 fail 用例
- 10 类场景穷举每类至少 1 个验证用例
- 错误注入测试：死锁/悬挂/缺依据/空输入

#### Skill 测试（darwin-skill 验证）

`test-prompts.json` 包含 6 类验证场景：

| ID | 类别 | 验证要点 | darwin-skill 目标分 |
|---|---|---|---|
| SM-TP-01 | 订单退款（文章案例） | 6 状态识别/禁止转换/10 类场景/依据标注 | 85 |
| SM-TP-02 | 审批流 | 并发冲突/终态吸收 | 80 |
| SM-TP-03 | 歧义暴露 | 标"待确认"而非补齐 | 90 |
| SM-TP-04 | 降级模式 | MCP 未启用仍输出完整 | 75 |
| SM-TP-05 | 转交 case-engineer | 触发混合意图链 5 | 80 |
| SM-TP-06 | 误路由检查 | 非状态型需求不路由到本 skill | 95 |

### 5.3 darwin-skill 验证标准

新增 skill 必须通过 darwin-skill 评分。state-machine-test-engineer 的评分维度：

| 维度 | 权重 | 目标分 | 评分要点 |
|---|---|---|---|
| 方法论完整性 | 25% | 85 | MAE + State Machine + 10 类场景穷举是否完整 |
| 防幻觉能力 | 20% | 90 | 依据类型标注、歧义暴露、禁止补齐 |
| 与 MCP 协作 | 15% | 80 | 增强模式有效、降级模式无降级故障 |
| 与 bundle 集成 | 15% | 85 | 路由准确率、混合意图链 5 转交正确 |
| 行业覆盖 | 10% | 80 | 4 个行业模板各可独立验证 |
| 输出一致性 | 10% | 85 | 跨模式输出格式一致，schema 严格 |
| 文档质量 | 5% | 80 | SKILL.md/README/knowledge 完整 |

**总分目标**：≥83 分（与 test-case-engineer v8.1.0 同档）

### 5.4 验证流程

```
开发完成
   ↓
单元测试通过（覆盖率 ≥90%）
   ↓
集成测试通过（4 行业模板端到端）
   ↓
darwin-skill 评分（6 个 test-prompts）
   ↓
总分 ≥83 且无单项 <70？
   ├─ 是 → 合并到 main，发布 v3.0.0
   └─ 否 → 修复后重测，最多 3 轮
```

### 5.5 bundle v3.0.0 集成测试

| 测试项 | 方法 | 通过标准 |
|---|---|---|
| 5-way 路由准确率 | 30 个混合 prompt 跑 bundle | state-machine 命中率 ≥90%，无误路由到其他 skill |
| 混合意图链 5 | 10 个"建模+用例"prompt | 转交 test-case-engineer 成功率 100% |
| 4-way 旧 skill 回归 | 既有 test-prompts 重跑 | 4 个旧 skill 评分不下降 |
| MCP 独立可用 | 不启动 skill，直接调 MCP | 5 个工具全部 200 响应 |
| MCP 增强模式 | skill + MCP 协作跑文章案例 | 校验报告正确生成，差异标记准确 |
| MCP 降级模式 | 强制 MCP 失效 | skill 仍完整输出，首行标记降级 |

### 5.6 文档与发布

| 文档 | 位置 | 内容 |
|---|---|---|
| SKILL.md | `plugins/testing/skills/state-machine-test-engineer/SKILL.md` | skill 主入口 |
| README.md | 同上目录 | 与 SKILL.md 同步 |
| MCP README | `plugins/testing/mcp-servers/state-machine-testing/README.md` | 安装/配置/调试 |
| 集成指南 | `state-machine-test-engineer/integrations/quickstart.md` | skill+MCP 配置示例 |
| bundle 升级说明 | `plugins/testing/skills/testing-bundle/CHANGELOG.md` | v2.0.0 → v3.0.0 变更 |
| spec 文档 | `docs/superpowers/specs/2026-07-18-state-machine-testing-design.md` | 本设计文档 |

### 5.7 关键设计决策

1. **错误不阻塞主流程**——skill 永远有输出，MCP 失败只追加警告，不让用户卡住
2. **MCP 返回 200 + warnings 而非 400**——死锁/悬挂是质量问题不是协议错误，让 skill 决定是否阻塞
3. **darwin-skill 评分与既有 skill 同档**——保证新 skill 不拉低 bundle 整体质量
4. **误路由检查独立成测试项**——5-way 路由的最大风险是误路由，专门测试
5. **回归测试保护旧 skill**——bundle 升级必须证明 4 个旧 skill 不退化

---

## 6. 实现路线

### 6.1 分阶段交付

| 阶段 | 内容 | 依赖 |
|---|---|---|
| P1 | skill 骨架 + 知识库（state-modeling/scenario-types/completeness-check/anti-patterns） | 无 |
| P2 | 4 个行业模板（order-refund/approval/membership/ticket） | P1 |
| P3 | MCP Server v0.1.0（5 个工具 + pydantic Schema + 单测） | P1 |
| P4 | skill ↔ MCP 协作（增强模式 + 降级策略） | P2, P3 |
| P5 | bundle v3.0.0 升级（5-way 路由 + 混合意图链 5） | P4 |
| P6 | darwin-skill 验证 + 回归测试 | P5 |

### 6.2 验收标准

- P1-P6 全部完成
- darwin-skill 总分 ≥83，无单项 <70
- 4 个旧 skill 回归测试无评分下降
- MCP Server 单测覆盖率 ≥90%
- 文档齐全（SKILL.md/README/MCP README/集成指南/CHANGELOG）

---

## 7. 待后续版本考虑

以下不在 v0.1.0 / v1.0.0 范围内，记录供后续评估：

- **节点树存储**——状态机模型与场景的 JSON 持久化，支持增量更新
- **Note 驱动增量重算**——只重算被用户修改的节点，类似 Treeify 智能再生成
- **多 Agent 分工**——需求分析师/状态建模师/场景生成师/查重评审师分角色协作
- **外部 MCP 集成**——TestCaseLab MCP（写回用例管理系统）、Jira MCP（待确认项自动建 Issue）、Confluence MCP（拉取 PRD）
- **状态机版本管理**——状态机模型的 git 化版本对比与差异可视化
- **测试执行对接**——把场景清单直接转为自动化测试脚本（Playwright/pytest 骨架）
