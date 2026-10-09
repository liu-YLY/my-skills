"""pydantic Schema 定义。

与 skill 输出的 YAML/JSON 严格对齐，Transition 和 Scenario 的 evidence_type 必填，
pydantic 会在校验时报错，保证依据标签存在；标签不能证明业务事实已核实。
"""

from __future__ import annotations

from enum import Enum
import hashlib
import json
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class EvidenceType(str, Enum):
    """依据类型枚举。"""

    EXPLICIT = "需求明确"
    INFERRED = "合理推理"
    PENDING = "待确认"


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


class ScenarioApplicability(BaseModel):
    status: Literal["applicable", "not_applicable", "unknown"]
    reason: str = Field(min_length=1)
    source: str = Field(min_length=1)
    evidence_type: EvidenceType = EvidenceType.PENDING
    missing_information: list[str] = Field(default_factory=list)


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


class FailureSemantics(BaseModel):
    phase: Literal["pre_execution_rejected", "pre_commit_failed", "committed_response_lost", "partial_success", "unknown"]
    allowed_states: list[str] = Field(default_factory=list)
    forbidden_side_effects: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    recovery_conditions: list[str] = Field(default_factory=list)
    source: str = ""
    evidence_type: EvidenceType = EvidenceType.PENDING

    @model_validator(mode="after")
    def require_source_for_known_phase(self):
        if self.phase != "unknown" and not self.source.strip():
            raise ValueError("已确定失败阶段需要来源；提交边界未知使用 unknown")
        return self


class Transition(BaseModel):
    """转换定义。evidence_type 必填，保证依据标签存在；标签不能证明业务事实已核实。"""

    from_state: str = Field(alias="from")
    to_state: str = Field(alias="to")
    event: str
    guards: list[str] = Field(default_factory=list)
    side_effects: list[str] = Field(default_factory=list)
    failure_outcomes: list[FailureSemantics] = Field(default_factory=list)
    evidence_type: EvidenceType
    source: str = ""
    id: str | None = None

    @model_validator(mode="after")
    def assign_id(self):
        if not self.id:
            key = [self.from_state, self.event, self.to_state, sorted(set(self.guards))]
            self.id = "T-" + hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16]
        return self

    model_config = {"populate_by_name": True}


class ForbiddenTransition(BaseModel):
    """禁止转换定义。"""

    from_state: str = Field(alias="from")
    to_state: str | Literal["*"] = Field(alias="to")
    reason: str
    evidence_type: EvidenceType
    source: str = ""
    id: str | None = None

    @model_validator(mode="after")
    def assign_id(self):
        if not self.id:
            key = [self.from_state, self.to_state, self.reason]
            self.id = "F-" + hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16]
        return self

    model_config = {"populate_by_name": True}


class ProgressRequirement(BaseModel):
    required: bool
    allowed_terminal_states: list[str] = Field(default_factory=list)
    applies_from_states: list[str] = Field(default_factory=list)
    source: str = Field(min_length=1)
    evidence_type: EvidenceType = EvidenceType.PENDING


class SafetyProperty(BaseModel):
    id: str
    statement: str
    applies_to: list[str] = Field(default_factory=list)
    source: str = Field(min_length=1)
    verification_method: str = Field(min_length=1)
    evidence_type: EvidenceType = EvidenceType.PENDING


class TraceSource(BaseModel):
    id: str
    location: str
    version: str | None = None
    availability: Literal["available", "unreachable", "missing", "unknown"] = "unknown"


class TraceArtifact(BaseModel):
    id: str
    kind: Literal["requirement", "risk", "model", "transition", "scenario", "case", "execution"]
    version: str | None = None


class TraceLink(BaseModel):
    upstream: str
    downstream: str
    confirmation: Literal["confirmed", "candidate"] = "candidate"
    source: str = ""
    source_refs: list[str] = Field(default_factory=list)


class TraceabilityContext(BaseModel):
    sources: list[TraceSource] = Field(default_factory=list)
    artifacts: list[TraceArtifact] = Field(default_factory=list)
    links: list[TraceLink] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_duplicate_identity(self):
        ids = [item.id for item in self.sources + self.artifacts]
        if len(set(ids)) != len(ids) or any(not item.strip() for item in ids):
            raise ValueError("追溯实体 ID 必须唯一且非空；使用对象命名空间")
        return self


class InvalidationReport(BaseModel):
    affected: list[str] = Field(default_factory=list)
    candidate_impacts: list[str] = Field(default_factory=list)
    unmatched_refs: list[str] = Field(default_factory=list)
    uncorroborated_links: list[str] = Field(default_factory=list)


class StateMachine(BaseModel):
    """状态机模型。"""

    meta: StateMachineMeta
    states: list[State]
    transitions: list[Transition]
    forbidden: list[ForbiddenTransition] = Field(default_factory=list)
    scenario_applicability: dict[RiskType, ScenarioApplicability] = Field(default_factory=dict)
    progress_requirement: ProgressRequirement | None = None
    safety_properties: list[SafetyProperty] = Field(default_factory=list)
    traceability: TraceabilityContext | None = None





class Scenario(BaseModel):
    """测试场景定义。evidence_type 必填。"""

    id: str
    title: str
    current_state: str
    trigger_event: str
    precondition: str
    expected_target_state: str
    expected_target_state_reason: str | None = None
    forbidden_states: list[str] = Field(default_factory=list)
    risk_type: RiskType
    related_objects: list[str] = Field(default_factory=list)
    evidence_type: EvidenceType
    source: str = ""
    notes: str = ""
    transition_id: str | None = None
    forbidden_id: str | None = None
    guard_conditions: list[str] = Field(default_factory=list)
    attempted_target_state: str | None = None
    violated_guard: str | None = None
    failure_semantics: FailureSemantics | None = None
    stable_ref: str | None = None
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_reason_for_pending_target(self):
        """expected_target_state 为「待确认」时必须给出待确认原因。"""
        if self.expected_target_state == "待确认" and not self.expected_target_state_reason:
            raise ValueError(
                "expected_target_state='待确认' 时必须提供 expected_target_state_reason"
            )
        return self


class ScenarioList(BaseModel):
    """场景清单。"""

    scenarios: list[Scenario]
    coverage_summary: dict[str, int] = Field(default_factory=dict)
    scenario_applicability: dict[RiskType, ScenarioApplicability] = Field(default_factory=dict)
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
    status: Literal["pass", "fail", "warn", "not_checked"]
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


class PropertyCheck(BaseModel):
    evidence_type: EvidenceType = EvidenceType.PENDING
    check_id: str
    name: str
    status: Literal["pass", "fail", "warn", "not_checked", "not_applicable"]
    detail: str = ""
    source: str = ""


class ValidationReport(BaseModel):
    """validate_state_machine 返回结构。"""

    overall_status: Literal["pass", "fail", "warn"]
    checks: list[CheckItem]
    property_checks: list[PropertyCheck] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    manual_review_required: bool = False


class CoverageBaseline(BaseModel):
    source: str = Field(min_length=1)
    version: str = Field(min_length=1)
    items: list[str]


class CoverageLink(BaseModel):
    item_id: str
    scenario_ref: str
    confirmation: Literal["confirmed", "candidate"] = "candidate"


class ExecutionRecord(BaseModel):
    case_id: str
    baseline_version: str
    run_id: str = Field(min_length=1)
    status: Literal["passed", "failed", "blocked", "not_run"]
    evidence_ref: str | None = None
    evidence_status: Literal["verified", "unknown", "unreachable", "missing"] = "unknown"


class CoverageContext(BaseModel):
    requirement_baseline: CoverageBaseline | None = None
    requirement_links: list[CoverageLink] = Field(default_factory=list)
    design_baseline: CoverageBaseline | None = None
    case_baseline: CoverageBaseline | None = None
    execution_records: list[ExecutionRecord] = Field(default_factory=list)


class CoverageLayer(BaseModel):
    status: Literal["assessed", "not_assessed", "not_applicable"]
    numerator: int | None = None
    denominator: int | None = None
    ratio: float | None = None
    baseline_source: str | None = None
    baseline_version: str | None = None
    unassessed_items: list[str] = Field(default_factory=list)


class CoverageReport(BaseModel):
    """check_coverage 返回结构。"""

    transition_coverage: float
    layers: dict[str, CoverageLayer] = Field(default_factory=dict)
    forbidden_coverage: float
    scenario_type_coverage: dict[str, int]
    evidence_distribution: dict[str, int]
    uncovered_transitions: list[str] = Field(default_factory=list)
    missing_scenario_types: list[str] = Field(default_factory=list)
    unmatched_scenarios: list[str] = Field(default_factory=list)
    scenario_applicability: dict[RiskType, ScenarioApplicability] = Field(default_factory=dict)
    applicable_missing_scenario_types: list[str] = Field(default_factory=list)
    not_applicable_scenario_types: list[str] = Field(default_factory=list)
    unknown_scenario_types: list[str] = Field(default_factory=list)


class ExportResult(BaseModel):
    """export_artifacts 返回结构。"""

    output_dir: str
    files: list[str]
    formats: list[Literal["markdown", "json", "mermaid"]]
    notes: str = ""
