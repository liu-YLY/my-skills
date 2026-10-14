"""build_state_machine 实现：确定性构建状态机模型。

v0.2.0 契约（无内部 LLM）：
- 指定 industry_template 时：确定性加载并解析 skill 知识库中的行业模板，
  返回模板状态机 + 适配提示（skill 需按需求差异适配后再校验）。
- 仅传入自由文本需求时：本工具不做 NLU，返回空骨架 + 建模指引，
  由调用方 LLM（skill 阶段 2）完成建模后传给 validate_state_machine。
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .exporters import export_to_mermaid
from .schemas import (
    Ambiguity,
    EvidenceType,
    StateMachine,
    StateMachineBuildResult,
)

AVAILABLE_TEMPLATES = ("order-refund", "approval-flow", "membership", "ticket")

_YAML_BLOCK_RE = re.compile(r"```yaml\n(.*?)```", re.DOTALL)


def _templates_dir() -> Path:
    """行业模板目录（skill 知识库内，模板 markdown 为唯一事实源）。

    src/state_machine_testing_mcp/ 上溯 5 级到 plugins/testing/，
    再进入 skills/state-machine-test-engineer/knowledge/industry-templates/。
    注意：该路径要求以源码树或 editable 安装方式运行。
    """
    return (
        Path(__file__).resolve().parent.parent.parent.parent.parent
        / "skills"
        / "state-machine-test-engineer"
        / "knowledge"
        / "industry-templates"
    )


def _build_industry_template(template_name: str) -> StateMachine | None:
    """加载并解析行业模板 markdown 中的状态机 YAML 定义。

    模板文件含多个 yaml 块，取解析后含 state_machine 键的那一块。
    """
    template_path = _templates_dir() / f"{template_name}.md"
    if not template_path.exists():
        return None
    md_text = template_path.read_text(encoding="utf-8")
    for block in _YAML_BLOCK_RE.findall(md_text):
        data = yaml.safe_load(block)
        if isinstance(data, dict) and "state_machine" in data:
            sm_data = data["state_machine"]
            # 模板 YAML 中 version: 1.0 会被解析为 float，schema 要求 str
            meta = sm_data.get("meta") if isinstance(sm_data, dict) else None
            if isinstance(meta, dict) and isinstance(meta.get("version"), (int, float)):
                meta["version"] = str(meta["version"])
            return StateMachine.model_validate(sm_data)
    return None


def build_state_machine(
    requirement: str,
    object_hint: str | None = None,
    industry_template: str | None = None,
) -> StateMachineBuildResult:
    """从需求构建状态机模型（确定性实现，无内部 LLM）。

    Args:
        requirement: 需求文本（PRD/用户描述）
        object_hint: 可选业务对象提示（如 "Order"）
        industry_template: 可选行业模板名（order-refund/approval-flow/membership/ticket）

    Returns:
        StateMachineBuildResult: 状态机构建结果
    """
    # 路径 1：行业模板确定性加载
    if industry_template:
        template_sm = _build_industry_template(industry_template)
        if template_sm is not None:
            return StateMachineBuildResult(
                state_machine=template_sm,
                extracted_objects=[template_sm.meta.object],
                ambiguities=[
                    Ambiguity(
                        id="AMB-TEMPLATE-ADAPT",
                        question=(
                            f"已加载行业模板 {industry_template}，请对照需求差异适配："
                            "模板中需求未覆盖的状态/转换应删除或改标「待确认」，"
                            "需求新增的状态/转换应补充并标注依据类型"
                        ),
                        evidence_type=EvidenceType.PENDING,
                        source=f"industry-templates/{industry_template}.md",
                    )
                ],
                mermaid_diagram=export_to_mermaid(template_sm),
                build_notes=(
                    f"模板路径：已确定性加载 {industry_template} 模板"
                    f"（{len(template_sm.states)} 状态 / {len(template_sm.transitions)} 转换 / "
                    f"{len(template_sm.forbidden)} 禁止转换）。"
                    "skill 按需求适配后调用 validate_state_machine 校验。"
                ),
            )
        # 模板名无效：明确报告可用模板，不静默降级
        return _plain_requirement_result(
            requirement,
            object_hint,
            extra_ambiguity=Ambiguity(
                id="AMB-TEMPLATE-NOT-FOUND",
                question=(
                    f"行业模板 {industry_template} 不存在。可用模板："
                    + "、".join(AVAILABLE_TEMPLATES)
                ),
                evidence_type=EvidenceType.PENDING,
                source="MCP Server 输入校验",
            ),
        )

    # 路径 2：纯需求文本——本工具不内置 LLM，不做 NLU
    return _plain_requirement_result(requirement, object_hint)


def _plain_requirement_result(
    requirement: str,
    object_hint: str | None,
    extra_ambiguity: Ambiguity | None = None,
) -> StateMachineBuildResult:
    """自由文本路径：返回空骨架 + 建模指引（建模由调用方 LLM 完成）。"""
    ambiguities = [
        Ambiguity(
            id="AMB-001",
            question=(
                "本工具不内置 LLM，无法从自由文本抽取状态机。"
                "请由调用方 LLM（state-machine-test-engineer skill 阶段 2）完成建模，"
                "或将建模结果传给 validate_state_machine；"
                "也可指定 industry_template 直接加载确定性模板"
            ),
            evidence_type=EvidenceType.PENDING,
            source="MCP Server v0.2.0 契约",
        )
    ]
    if extra_ambiguity is not None:
        ambiguities.append(extra_ambiguity)

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
        state_machine=empty_sm,
        extracted_objects=[object_hint] if object_hint else [],
        ambiguities=ambiguities,
        mermaid_diagram="",
        build_notes=(
            "推荐流程：skill 阶段 2 自行建模 → validate_state_machine 校验 → "
            "generate_scenarios 穷举；或指定 industry_template 加载模板起点。"
        ),
    )
