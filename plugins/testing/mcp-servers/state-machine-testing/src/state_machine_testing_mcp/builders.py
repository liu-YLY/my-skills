"""build_state_machine 实现：从需求文本构建状态机模型。

注意：本工具内部使用 LLM 解析需求，与其他 4 个工具的确定性计算不同。
当前 v0.1.0 仅提供基础占位实现，完整 LLM 集成待 v0.2.0。
"""

from __future__ import annotations

import json
from pathlib import Path

from .schemas import (
    Ambiguity,
    EvidenceType,
    StateMachine,
    StateMachineBuildResult,
)

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    """加载 LLM 提示词模板。"""
    prompt_path = PROMPTS_DIR / f"{name}.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"提示词模板不存在: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def _build_industry_template(template_name: str) -> StateMachine | None:
    """加载行业模板（如果存在）。"""
    templates_dir = (
        Path(__file__).parent.parent.parent.parent.parent
        / "plugins"
        / "testing"
        / "skills"
        / "state-machine-test-engineer"
        / "knowledge"
        / "industry-templates"
    )
    template_path = templates_dir / f"{template_name}.md"
    if not template_path.exists():
        return None
    # 行业模板的解析留待完整版实现，当前返回 None
    return None


def build_state_machine(
    requirement: str,
    object_hint: str | None = None,
    industry_template: str | None = None,
) -> StateMachineBuildResult:
    """从需求文本构建状态机模型。

    Args:
        requirement: 需求文本（PRD/用户描述）
        object_hint: 可选业务对象提示（如 "Order"）
        industry_template: 可选行业模板名（order-refund/approval-flow/membership/ticket）

    Returns:
        StateMachineBuildResult: 状态机构建结果

    Note:
        v0.1.0 仅提供骨架实现，LLM 集成在 v0.2.0 完成。
        当前调用者应通过 state-machine-test-engineer skill 自身的 LLM 推理完成建模，
        再将结果传给 validate_state_machine / generate_scenarios 等确定性工具。
    """
    # 加载行业模板（如有）
    template_sm: StateMachine | None = None
    if industry_template:
        template_sm = _build_industry_template(industry_template)

    # v0.1.0 占位实现：返回空状态机，提示使用 skill 自身建模
    empty_sm = StateMachine(
        meta={
            "object": object_hint or "Unknown",
            "version": "1.0",
            "source": requirement[:200],
            "confidence": "low",
        },
        states=[],
        transitions=[],
        forbidden=[],
    )

    return StateMachineBuildResult(
        state_machine=template_sm or empty_sm,
        extracted_objects=[object_hint] if object_hint else [],
        ambiguities=[
            Ambiguity(
                id="AMB-001",
                question="v0.1.0 build_state_machine 仅提供骨架，请通过 state-machine-test-engineer skill 完成建模",
                evidence_type=EvidenceType.PENDING,
                source="MCP Server v0.1.0 限制",
            )
        ],
        mermaid_diagram="",
        build_notes=(
            "v0.1.0 占位实现。推荐流程：skill 阶段 2 自行建模 → "
            "调用 validate_state_machine 校验 → 调用 generate_scenarios 穷举。"
        ),
    )
