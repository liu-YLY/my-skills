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


class TestCaseSet(BaseModel):
    """用例集合（评审输入）。"""

    cases: list[TestCase]
    test_point_ids: list[str] = Field(default_factory=list)
    supports_p3: bool = True


class Issue(BaseModel):
    """单条评审问题。"""

    case_id: str
    dimension: str
    severity: Severity
    rule: str
    evidence: str
    suggestion: str = ""


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
