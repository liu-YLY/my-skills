# State Machine Testing MCP Server

> 配套 state-machine-test-engineer skill 的 Python MCP Server v0.1.0：提供状态机建模/校验/穷举/导出/覆盖度 5 个工具，作为 skill 的可选增强引擎。

> **实现状态**：v0.1.0 已完成 pydantic Schema + 4 个确定性工具（validate/generate/export/coverage）+ 单元测试（34 通过）+ 集成测试（2 通过）。`build_state_machine` 为占位实现（推荐通过 skill 自身 LLM 推理建模，再传给确定性工具校验）。MCP 协议层注册待 v0.2.0。

## 简介

本 MCP Server 是 testing-bundle v3.0.0 的配套组件，位于 `plugins/testing/mcp-servers/state-machine-testing/`。

**本质**：自己写给自己用的 MCP Server，让纯 markdown 的 skill 能调用 Python 写的确定性计算逻辑（Schema 校验/穷举/覆盖度），不依赖 LLM 推理这些本该确定的事。

**与 skill 的关系**：
- skill 是主，Server 是复核器（Server 校验失败不影响 skill 输出）
- skill 独立可用，未安装 Server 时降级为纯 LLM 推理
- 安装 Server 后 skill 进入"增强模式"，获得 Schema 校验、Mermaid 可视化、覆盖度报告

## 技术栈

| 项 | 选择 | 理由 |
|---|---|---|
| 语言 | Python 3.11+ | 与项目现有 scripts/convert_docs.py 一致 |
| MCP SDK | `mcp` 官方 Python SDK | 协议标准、跨 Host 复用 |
| Schema 校验 | pydantic v2 | 类型安全、错误信息详细 |
| 传输 | stdio（默认）+ HTTP/SSE（可选） | 本地用 stdio，远端用 HTTP |
| LLM 调用 | 仅 `build_state_machine` 内部使用 | 其他 4 个工具为确定性计算 |

## 工具集（5 个）

| 工具名 | 用途 | 输入 | 输出 | 是否调 LLM |
|---|---|---|---|---|
| `build_state_machine` | 从需求文本构建状态机模型 | 需求文本/PRD 片段 | StateMachineBuildResult | 是（内部解析需求） |
| `validate_state_machine` | 校验状态机完整性与一致性 | StateMachine | ValidationReport | 否 |
| `generate_scenarios` | 基于状态机穷举 10 类场景 | StateMachine | ScenarioList | 否 |
| `export_artifacts` | 导出为 Markdown / JSON / Mermaid | StateMachine + Scenarios | ExportResult | 否 |
| `check_coverage` | 覆盖度检查 | StateMachine + Scenarios | CoverageReport | 否 |

### 工具签名

```python
@mcp.tool()
def build_state_machine(
    requirement: str,
    object_hint: str | None = None,
    industry_template: str | None = None
) -> StateMachineBuildResult: ...

@mcp.tool()
def validate_state_machine(
    state_machine: StateMachine,
    strict: bool = True
) -> ValidationReport: ...

@mcp.tool()
def generate_scenarios(
    state_machine: StateMachine,
    scenario_types: list[str] | None = None,
    evidence_filter: str | None = None
) -> ScenarioList: ...

@mcp.tool()
def export_artifacts(
    state_machine: StateMachine,
    scenarios: ScenarioList | None = None,
    formats: list[Literal["markdown", "json", "mermaid"]],
    output_dir: str = "./state-machine-outputs"
) -> ExportResult: ...

@mcp.tool()
def check_coverage(
    state_machine: StateMachine,
    scenarios: ScenarioList
) -> CoverageReport: ...
```

详细签名与返回结构见 [设计文档 §3.3](../../../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md#33-工具详设)。

## 核心 Schema（pydantic）

```python
class EvidenceType(str, Enum):
    EXPLICIT = "需求明确"
    INFERRED = "合理推理"
    PENDING = "待确认"

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
    guards: list[str] = []
    side_effects: list[str] = []
    evidence_type: EvidenceType
    source: str = ""

class ForbiddenTransition(BaseModel):
    from_state: str
    to_state: str | Literal["*"]
    reason: str
    evidence_type: EvidenceType

class StateMachine(BaseModel):
    meta: StateMachineMeta
    states: list[State]
    transitions: list[Transition]
    forbidden: list[ForbiddenTransition] = []

class Scenario(BaseModel):
    id: str
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

**关键约束**：`Transition` 和 `Scenario` 的 `evidence_type` 是必填字段，pydantic 会在校验时报错，从机制上防幻觉。

完整 Schema 见 [设计文档 §3.4](../../../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md#34-核心数据结构-schemapydantic)。

## 安装

### 前置条件

- Python 3.11+
- pip 或 uv

### 安装步骤

```bash
cd plugins/testing/mcp-servers/state-machine-testing/
pip install -e .
# 或使用 uv
uv pip install -e .
```

依赖清单（pyproject.toml）：

```toml
[project]
name = "state-machine-testing-mcp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp>=0.9.0",
    "pydantic>=2.0",
]
```

### 验证安装

```bash
python -m state_machine_testing_mcp.server --help
```

应输出 5 个工具的帮助信息。

## 配置 Trae MCP 客户端

详见 [state-machine-test-engineer/integrations/quickstart.md](../../skills/state-machine-test-engineer/integrations/quickstart.md)。

## 目录结构

```
plugins/testing/mcp-servers/state-machine-testing/
├── pyproject.toml                      # 依赖声明
├── README.md                           # 本文档
├── src/
│   └── state_machine_testing_mcp/
│       ├── __init__.py
│       ├── server.py                   # MCP Server 入口（注册 5 个工具）
│       ├── schemas.py                  # pydantic 模型
│       ├── builders.py                 # build_state_machine 实现
│       ├── validators.py               # validate_state_machine 实现（9 项检查）
│       ├── generators.py               # generate_scenarios 实现（10 类穷举）
│       ├── exporters.py                # export_artifacts 实现（Markdown/JSON/Mermaid）
│       ├── coverage.py                 # check_coverage 实现
│       └── prompts/                    # LLM 提示词模板（build_state_machine 内部用）
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

## 错误处理

| 错误场景 | 处理策略 | 返回码 |
|---|---|---|
| Schema 校验失败 | 返回详细错误清单（字段路径+原因） | 400 + ValidationError |
| 状态机含死锁状态 | 标 warning，不拒绝执行 | 200 + warnings[] |
| 状态机含悬挂状态 | 标 warning，不拒绝执行 | 200 + warnings[] |
| 状态机为空 | 拒绝执行 | 400 + EmptyInputError |
| `generate_scenarios` 输入 `scenario_types` 含未知类型 | 忽略未知类型，标 warning | 200 + warnings[] |
| `export_artifacts` 输出目录无写权限 | 返回错误，建议备选目录 | 400 + PermissionError |
| 内部 LLM 调用失败（`build_state_machine`） | 返回错误 + 原始异常 | 500 + LLMError |
| 未捕获异常 | 返回 500 + 通用错误信息 + trace_id | 500 + InternalError |

**关键设计**：死锁/悬挂是质量问题不是协议错误，返回 200 + warnings 让 skill 决定是否阻塞。

## 9 项完整性检查（validate_state_machine）

1. 每个状态有明确含义
2. 每个状态有进入条件（除初始态）
3. 每个非终态有退出路径
4. 终态真的不可变化（无出边）
5. 禁止转换无遗漏（覆盖所有非法跳转）
6. 状态变化有副作用定义
7. 依据类型已标注（无遗漏）
8. 无悬挂状态（unreachable）
9. 无死锁状态（deadlock，非终态但无出边）

## 10 类场景穷举（generate_scenarios）

| risk_type | 中文 | 说明 |
|---|---|---|
| `legal_transition` | 合法转换 | 验证 PRD 明确的转换路径 |
| `illegal_transition` | 非法转换 | 验证 forbidden 规则被正确拒绝 |
| `guard_violation` | 条件不满足 | 守卫条件不满足时的拒绝行为 |
| `idempotency` | 重复事件与幂等 | 同一事件重复触发的处理 |
| `concurrency` | 并发事件 | 多事件同时触发的最终状态 |
| `message_reorder` | 消息乱序 | 异步消息乱序到达的状态正确性 |
| `timeout_retry` | 超时与重试 | 超时后的状态变化与重试幂等性 |
| `data_consistency` | 数据一致性 | 转换后关联对象的数据一致性 |
| `access_control` | 权限控制 | 不同角色触发转换的权限校验 |
| `failure_recovery` | 失败后恢复路径 | 转换失败后的状态恢复策略 |

## 覆盖度报告（check_coverage）

```python
class CoverageReport(BaseModel):
    transition_coverage: float       # 每条转换至少有 1 个合法场景
    forbidden_coverage: float        # 每条禁止转换至少有 1 个非法场景
    scenario_type_coverage: dict[str, int]  # 10 类场景类型分布
    evidence_distribution: dict[str, int]   # 依据类型分布（需求明确/合理推理/待确认）
```

## 测试

```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 覆盖率（目标 ≥90%）
pytest tests/ --cov=state_machine_testing_mcp --cov-report=term-missing
```

测试用例覆盖目标：
- 4 个行业模板各至少 1 个完整端到端用例
- 9 项完整性检查每项至少 1 个 pass + 1 个 fail 用例
- 10 类场景穷举每类至少 1 个验证用例
- 错误注入测试：死锁/悬挂/缺依据/空输入

## 开发

### 本地开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 类型检查
mypy src/

# 格式化
black src/ tests/
ruff check src/ tests/
```

### 添加新工具

1. 在 `src/state_machine_testing_mcp/` 下新建模块
2. 在 `server.py` 中注册工具
3. 在 `tests/unit/` 下添加单测
4. 更新本 README 与 skill 的 quickstart.md

## 隐私与安全

- Server 本地运行，不外发数据
- `build_state_machine` 内部可能调用 LLM 解析需求，若使用云端 LLM 会发送需求文本
- 其他 4 个工具为确定性计算，不发任何数据出本机
- 如需完全离线，配置 `build_state_machine` 使用本地 LLM 或在 skill 侧禁用该工具

## 版本历史

- v0.1.0: 首版，5 个工具（build/validate/generate/export/coverage）+ pydantic Schema + 9 项检查 + 10 类穷举

## 待后续版本

- 节点树存储（状态机模型与场景的 JSON 持久化）
- Note 驱动增量重算
- 多 Agent 分工
- 外部 MCP 集成（TestCaseLab/Jira/Confluence）

---

**相关文档**：
- [state-machine-test-engineer SKILL.md](../../skills/state-machine-test-engineer/SKILL.md) - 配套 skill
- [quickstart.md](../../skills/state-machine-test-engineer/integrations/quickstart.md) - 配置指南
- [设计文档](../../../../docs/superpowers/specs/2026-07-18-state-machine-testing-design.md) - 完整设计 spec
- [MCP 协议规范](https://modelcontextprotocol.io/) - 协议官方文档
