"""端到端集成测试：需求 → 模型 → 校验 → 场景 → 导出 → 覆盖度。"""

from __future__ import annotations

import json
from pathlib import Path

from state_machine_testing_mcp.coverage import check_coverage
from state_machine_testing_mcp.exporters import export_artifacts
from state_machine_testing_mcp.generators import generate_scenarios
from state_machine_testing_mcp.schemas import StateMachine
from state_machine_testing_mcp.validators import validate_state_machine

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_order_refund_end_to_end(tmp_path: Path) -> None:
    """订单退款 fixture 端到端测试。"""
    # 1. 加载 fixture
    sm = StateMachine.model_validate(
        json.loads((FIXTURES_DIR / "order_refund_state_machine.json").read_text("utf-8"))
    )

    # 2. 校验
    report = validate_state_machine(sm, strict=False)
    assert report.overall_status in ("pass", "warn")
    assert len(report.checks) == 9

    # 3. 生成场景
    scenarios = generate_scenarios(sm)
    assert len(scenarios.scenarios) >= 10  # 至少 10 类各 1 条

    # 4. 导出
    export_result = export_artifacts(sm, scenarios, output_dir=str(tmp_path))
    assert len(export_result.files) == 3

    # 5. 覆盖度
    coverage = check_coverage(sm, scenarios)
    assert coverage.transition_coverage == 1.0
    assert len(coverage.missing_scenario_types) < 10


def test_approval_flow_end_to_end() -> None:
    """审批流 fixture 端到端测试。"""
    sm = StateMachine.model_validate(
        json.loads((FIXTURES_DIR / "approval_flow_state_machine.json").read_text("utf-8"))
    )
    report = validate_state_machine(sm, strict=False)
    assert all(c.status != "fail" for c in report.checks)

    scenarios = generate_scenarios(sm)
    assert len(scenarios.scenarios) >= 10
