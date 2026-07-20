"""pydantic Schema 定义。

与 skill 输出的 YAML/JSON 严格对齐，Transition 和 Scenario 的 evidence_type 必填，
pydantic 会在校验时报错，从机制上防幻觉。
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """依据类型枚举。"""

    EXPLICIT = "需求明确"
    INFERRED = "合理推理"
    PENDING = "待确认"


class StateMachineMeta(BaseModel):
    """状态机元信息。"""

    object: str
    version: str = "1.0"
    source: str = ""
    confidence: Literal["high", "medium", "low"] = "medium"


class State(BaseModel):
    """状态定义。"""

    name: str
    meaning: str
    is_terminal: bool = False
    is_initial: bool = False
    entry_events: list[str] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)


class Transition(BaseModel):
    """转换定义。evidence_type 必填，从机制上防幻觉。"""

    from_state: str = Field(alias="from")
    to_state: str = Field(alias="to")
    event: str
    guards: list[str] = Field(default_factory=list)
    side_effects: list[str] = Field(default_factory=list)
    evidence_type: EvidenceType
    source: str = ""

    model_config = {"populate_by_name": True}


class ForbiddenTransition(BaseModel):
    """禁止转换定义。"""

    from_state: str = Field(alias="from")
    to_state: str | Literal["*"] = Field(alias="to")
    reason: str
    evidence_type: EvidenceType

    model_config = {"populate_by_name": True}


class StateMachine(BaseModel):
    """状态机模型。"""

    meta: StateMachineMeta
    states: list[State]
    transitions: list[Transition]
    forbidden: list[ForbiddenTransition] = Field(default_factory=list)


RiskType = Literal[
    "legal_transition",
    "illegal_transition",
    "guard_violation",
    "idempotency",
    "concurrency",
    "message_reorder",
    "timeout_retry",
    "data_consistency",
    "access_control",
    "failure_recovery",
]


class Scenario(BaseModel):
    """测试场景定义。evidence_type 必填。"""

    id: str
    title: str
    current_state: str
    trigger_event: str
    precondition: str
    expected_target_state: str
    forbidden_states: list[str] = Field(default_factory=list)
    risk_type: RiskType
    related_objects: list[str] = Field(default_factory=list)
    evidence_type: EvidenceType
    source: str = ""
    notes: str = ""


class ScenarioList(BaseModel):
    """场景清单。"""

    scenarios: list[Scenario]
    coverage_summary: dict[str, int] = Field(default_factory=dict)
    pending_confirmation: list[Scenario] = Field(default_factory=list)


class Ambiguity(BaseModel):
    """歧义项（强制暴露，不补齐）。"""

    id: str
    question: str
    evidence_type: EvidenceType = EvidenceType.PENDING
    source: str = ""


class StateMachineBuildResult(BaseModel):
    """build_state_machine 返回结构。"""

    state_machine: StateMachine
    extracted_objects: list[str] = Field(default_factory=list)
    ambiguities: list[Ambiguity] = Field(default_factory=list)
    mermaid_diagram: str = ""
    build_notes: str = ""


class CheckItem(BaseModel):
    """完整性检查项。"""

    check_id: str
    name: str
    status: Literal["pass", "fail", "warn"]
    detail: str = ""


class Gap(BaseModel):
    """缺口。"""

    id: str
    description: str
    evidence_type: EvidenceType = EvidenceType.PENDING
    suggestion: str = ""
    related_state: str = ""
    related_check: str = ""


class Contradiction(BaseModel):
    """矛盾。"""

    id: str
    description: str
    severity: Literal["high", "medium", "low"] = "medium"
    suggestion: str = ""
    related_states: list[str] = Field(default_factory=list)
    related_check: str = ""


class ValidationReport(BaseModel):
    """validate_state_machine 返回结构。"""

    overall_status: Literal["pass", "fail", "warn"]
    checks: list[CheckItem]
    gaps: list[Gap] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class CoverageReport(BaseModel):
    """check_coverage 返回结构。"""

    transition_coverage: float
    forbidden_coverage: float
    scenario_type_coverage: dict[str, int]
    evidence_distribution: dict[str, int]
    uncovered_transitions: list[str] = Field(default_factory=list)
    missing_scenario_types: list[str] = Field(default_factory=list)


class ExportResult(BaseModel):
    """export_artifacts 返回结构。"""

    output_dir: str
    files: list[str]
    formats: list[Literal["markdown", "json", "mermaid"]]
    notes: str = ""
