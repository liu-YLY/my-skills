"""export_artifacts 实现：导出 Markdown / JSON / Mermaid。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from .schemas import ExportResult, ScenarioList, StateMachine


def export_to_markdown(sm: StateMachine, scenarios: ScenarioList | None = None) -> str:
    """导出为 Markdown。"""
    lines: list[str] = []
    lines.append(f"# 状态机模型: {sm.meta.object}")
    lines.append("")
    lines.append(f"- 版本: {sm.meta.version}")
    lines.append(f"- 来源: {sm.meta.source}")
    lines.append(f"- 置信度: {sm.meta.confidence}")
    lines.append("")

    lines.append("## 状态")
    lines.append("")
    lines.append("| 名称 | 含义 | 初始态 | 终态 | 不变量 |")
    lines.append("|---|---|---|---|---|")
    for s in sm.states:
        invariants = ", ".join(s.invariants) if s.invariants else "-"
        lines.append(
            f"| {s.name} | {s.meaning} | {'✓' if s.is_initial else ''} | "
            f"{'✓' if s.is_terminal else ''} | {invariants} |"
        )
    lines.append("")

    lines.append("## 转换")
    lines.append("")
    for t in sm.transitions:
        guards = ", ".join(t.guards) if t.guards else "-"
        side_effects = ", ".join(t.side_effects) if t.side_effects else "-"
        lines.append(f"- **{t.from_state} → {t.to_state}**")
        lines.append(f"  - 事件: {t.event}")
        lines.append(f"  - 守卫: {guards}")
        lines.append(f"  - 副作用: {side_effects}")
        lines.append(f"  - 依据: {t.evidence_type.value}")
        if t.source:
            lines.append(f"  - 来源: {t.source}")
        lines.append("")

    if sm.forbidden:
        lines.append("## 禁止转换")
        lines.append("")
        for f in sm.forbidden:
            target = "任意状态" if f.to_state == "*" else f.to_state
            lines.append(f"- {f.from_state} → {target}: {f.reason}（{f.evidence_type.value}）")
        lines.append("")

    if scenarios and scenarios.scenarios:
        lines.append("## 场景清单")
        lines.append("")
        lines.append("| ID | 标题 | 当前状态 | 触发事件 | 期望目标 | 风险类型 | 依据 |")
        lines.append("|---|---|---|---|---|---|---|")
        for s in scenarios.scenarios:
            lines.append(
                f"| {s.id} | {s.title} | {s.current_state} | {s.trigger_event} | "
                f"{s.expected_target_state} | {s.risk_type} | {s.evidence_type.value} |"
            )

    return "\n".join(lines)


def export_to_json(sm: StateMachine, scenarios: ScenarioList | None = None) -> str:
    """导出为 JSON。"""
    data = {
        "state_machine": sm.model_dump(by_alias=True, mode="json"),
        "scenarios": scenarios.model_dump(mode="json") if scenarios else None,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_to_mermaid(sm: StateMachine) -> str:
    """导出为 Mermaid 状态图。"""
    lines: list[str] = ["stateDiagram-v2"]

    # 初始态入口
    initials = [s.name for s in sm.states if s.is_initial]
    for init in initials:
        lines.append(f"    [*] --> {init}")

    # 转换
    for t in sm.transitions:
        lines.append(f"    {t.from_state} --> {t.to_state}: {t.event}")

    # 终态出口
    terminals = [s.name for s in sm.states if s.is_terminal]
    for term in terminals:
        lines.append(f"    {term} --> [*]")

    return "\n".join(lines)


def export_artifacts(
    state_machine: StateMachine,
    scenarios: ScenarioList | None = None,
    formats: list[Literal["markdown", "json", "mermaid"]] | None = None,
    output_dir: str = "./state-machine-outputs",
) -> ExportResult:
    """导出状态机模型与场景清单为多种格式。

    Args:
        state_machine: 状态机模型
        scenarios: 场景清单（可选）
        formats: 导出格式列表，默认全部三种
        output_dir: 输出目录

    Returns:
        ExportResult: 导出结果（含文件路径列表）
    """
    if formats is None:
        formats = ["markdown", "json", "mermaid"]

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    files: list[str] = []
    obj_name = state_machine.meta.object.lower().replace(" ", "-")

    if "markdown" in formats:
        md_path = out_path / f"{obj_name}.md"
        md_path.write_text(export_to_markdown(state_machine, scenarios), encoding="utf-8")
        files.append(str(md_path))

    if "json" in formats:
        json_path = out_path / f"{obj_name}.json"
        json_path.write_text(export_to_json(state_machine, scenarios), encoding="utf-8")
        files.append(str(json_path))

    if "mermaid" in formats:
        mermaid_path = out_path / f"{obj_name}.mmd"
        mermaid_path.write_text(export_to_mermaid(state_machine), encoding="utf-8")
        files.append(str(mermaid_path))

    return ExportResult(
        output_dir=str(out_path),
        files=files,
        formats=formats,
        notes=f"已导出 {len(files)} 个文件",
    )
