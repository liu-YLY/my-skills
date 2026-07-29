"""pydantic Schema 定义。

与 test-case-engineer 评审模式的用例结构严格对齐，TestCase 的必填字段
（ID/title/priority/type/steps/expected_results）由 pydantic 强制校验，
从机制上防止字段缺失。
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """用例优先级。"""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class ScenarioType(str, Enum):
    """场景类型（用于覆盖度维度判定）。"""

    POSITIVE = "正向"
    NEGATIVE = "逆向"
    BOUNDARY = "边界"
    EXCEPTION = "异常"


class Severity(str, Enum):
    """问题严重等级。"""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class TestCase(BaseModel):
    """用例定义。必填字段缺失由 pydantic 校验报错。"""

    id: str
    title: str
    priority: Priority
    type: str = ""
    scenario: ScenarioType | None = None
    steps: list[str] = Field(default_factory=list)
    expected_results: str = ""
    preconditions: list[str] = Field(default_factory=list)
    test_point_id: str = ""
    notes: str = ""  # 用例备注，超长标题等场景记录保留原因


class TestCaseSet(BaseModel):
    """用例集合（评审输入）。"""

    cases: list[TestCase]
    test_point_ids: list[str] = Field(default_factory=list)
    supports_p3: bool = True


class Issue(BaseModel):
    """单条评审问题。"""

    # case_id 支持三种形式：单用例 ID（"TC_001"）、集合级（"-"）、
    # 冲突对/闭环（"TC_A,TC_B" 或 "TC_A,TC_B,TC_C"）
    case_id: str
    dimension: str
    severity: Severity
    rule: str
    evidence: str
    suggestion: str = ""


class PreconditionFact(BaseModel):
    """前置条件语义事实（喂给冲突类型 ①）。"""

    subject: str  # 规范化主体，如 "用户登录状态"
    state: str  # 规范化状态值，如 "已登录"
    polarity: Literal["affirmative", "negation"]  # 肯定/否定断言


class InputFact(BaseModel):
    """输入语义事实（喂给冲突类型 ②）。"""

    input_signature: str  # 含数据值的输入签名，如 "登录(account=testuser,pwd=错误密码)"
    expected_outcome: str  # 规范化预期，如 "返回密码错误提示"


class SemanticFacts(BaseModel):
    """一条用例的语义事实（LLM 抽取，MCP 纯检测）。

    LLM 只负责把自然语言翻译为此结构，不做任何冲突判断。
    冲突检测由 validators.check_semantic_conflicts 执行。
    """

    case_id: str
    test_point_id: str | None = None  # 溯源分组键，无则 None
    preconditions: list[PreconditionFact] = Field(default_factory=list)
    inputs: list[InputFact] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)  # 依赖的其他 case_id


class DimensionStat(BaseModel):
    """维度统计。"""

    dimension: str
    issue_count: int
    main_severity: str


class ReviewReport(BaseModel):
    """评审报告（评审输出）。"""

    total_cases: int
    issue_cases: int
    pass_rate: float
    total_issues: int
    issue_density: float
    grade: Literal["A", "B", "C", "D"]
    issues: list[Issue]
    dimension_stats: list[DimensionStat]
    severity_stats: dict[str, int]
