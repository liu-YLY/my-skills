"""export_artifacts 单元测试。"""

from __future__ import annotations

import json
from pathlib import Path

from state_machine_testing_mcp.exporters import (
    export_artifacts,
    export_to_json,
    export_to_markdown,
    export_to_mermaid,
)
from state_machine_testing_mcp.generators import generate_scenarios
from state_machine_testing_mcp.schemas import StateMachine

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_order_refund() -> StateMachine:
    fixture = FIXTURES_DIR / "order_refund_state_machine.json"
    return StateMachine.model_validate(json.loads(fixture.read_text(encoding="utf-8")))


def test_export_to_markdown_contains_states() -> None:
    """Markdown 导出应包含状态表。"""
    sm = _load_order_refund()
    md = export_to_markdown(sm)
    assert "# 状态机模型" in md
    assert "待支付" in md
    assert "退款成功" in md


def test_export_to_markdown_with_scenarios() -> None:
    """Markdown 导出含场景清单。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    md = export_to_markdown(sm, scenarios)
    assert "## 场景清单" in md
    assert "SM-001" in md


def test_export_to_json_valid() -> None:
    """JSON 导出应为合法 JSON。"""
    sm = _load_order_refund()
    json_str = export_to_json(sm)
    data = json.loads(json_str)
    assert "state_machine" in data
    assert data["state_machine"]["meta"]["object"] == "Order"


def test_export_to_mermaid_syntax() -> None:
    """Mermaid 导出应包含 stateDiagram-v2 标记。"""
    sm = _load_order_refund()
    mermaid = export_to_mermaid(sm)
    assert mermaid.startswith("stateDiagram-v2")
    assert "[*] --> 待支付" in mermaid
    assert "退款成功 --> [*]" in mermaid


def test_export_artifacts_creates_files(tmp_path: Path) -> None:
    """export_artifacts 应在指定目录创建文件。"""
    sm = _load_order_refund()
    scenarios = generate_scenarios(sm)
    result = export_artifacts(
        sm,
        scenarios,
        formats=["markdown", "json", "mermaid"],
        output_dir=str(tmp_path),
    )
    assert len(result.files) == 3
    for f in result.files:
        assert Path(f).exists()
