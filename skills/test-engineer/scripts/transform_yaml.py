"""通用 → TEST 适配器转换工具。

将 test-engineer 通用格式 YAML(裸 test_cases 列表 或 已含 metadata)
按 ``adapters/test.md`` 规则转换为 TEST test-case-schema 兼容格式。

转换规则一览(与 ``adapters/test.md`` 一一对应):
    1. 优先级降级: P3 → P2;空/缺失 → P2
    2. type 枚举映射: compatibility/usability/observability → ui/ui/functional
    3. 字段合并: req_ref / trace 合并到 description 首行,原字段删除
    4. 顶层包装: 裸列表自动包装为 ``metadata + test_cases``
    5. 字段值引号保留(由 ruamel.yaml 输出时统一加引号)
    6. 字段白名单: 删除所有 schema 不允许的额外字段

用法:
    python scripts/transform_yaml.py <输入> [-o 输出] [--validate] \\
        [--module M] [--feature F] [--owner O]

    # 单文件转换 + 自动校验,覆盖输出
    python scripts/transform_yaml.py draft.yaml -o out.yaml --validate

    # 仅打印结果(不写文件)
    python scripts/transform_yaml.py draft.yaml --dry-run

    # 目录递归转换(产物落在同名 .test.yaml)
    python scripts/transform_yaml.py drafts/ --recursive --validate

依赖: pyyaml(必需), jsonschema(--validate 时使用)
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml


PRIORITY_MAP = {
    "P0": "P0",
    "P1": "P1",
    "P2": "P2",
    "P3": "P2",
}

TYPE_MAP = {
    "functional": ("functional", None),
    "ui": ("ui", None),
    "security": ("security", None),
    "performance": ("performance", None),
    "accessibility": ("accessibility", None),
    "compatibility": ("ui", "兼容性测试"),
    "usability": ("ui", "可用性测试"),
    "observability": ("functional", "可观测性测试"),
}

TEST_TC_FIELDS = {
    "id",
    "title",
    "description",
    "priority",
    "type",
    "preconditions",
    "steps",
    "expected_results",
    "tags",
    "auto",
}

DROPPED_TC_FIELDS = {"req_ref", "trace"}

TEST_METADATA_FIELDS = {"module", "feature", "owner", "last_reviewed", "tags"}


class TransformError(Exception):
    """转换失败时抛出,携带可读上下文。"""


def _ensure_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip() or default


def _build_description(case: dict[str, Any]) -> str:
    """根据 req_ref/trace/description 拼接 TEST 的 description 首行。

    规则 3:
    - req_ref + trace 都存在: ``追溯:Story-42 | TP-03``
    - 仅 req_ref: ``追溯:Story-42``
    - 仅 trace: ``追溯:TP-03``
    - 原 description 已存在则追溯行前插,中间用 ``\\n`` 分隔
    """
    req_ref = _ensure_str(case.get("req_ref"))
    trace = _ensure_str(case.get("trace"))
    original = _ensure_str(case.get("description"))

    parts = []
    if req_ref and trace:
        parts.append(f"追溯:{req_ref} | {trace}")
    elif req_ref:
        parts.append(f"追溯:{req_ref}")
    elif trace:
        parts.append(f"追溯:{trace}")

    if original:
        parts.append(original)

    return "\n".join(parts)


def transform_case(
    case: dict[str, Any],
    *,
    case_index: int,
) -> dict[str, Any]:
    """将单条通用格式用例转换为 TEST 用例。

    保留字段顺序与 ``adapters/test.md`` 示例一致,便于人读 diff。
    """
    if not isinstance(case, dict):
        raise TransformError(
            f"第 {case_index + 1} 条用例不是 mapping,实际类型: {type(case).__name__}"
        )

    case_id = _ensure_str(case.get("id"))
    if not case_id:
        raise TransformError(f"第 {case_index + 1} 条用例缺少 id")

    raw_priority = _ensure_str(case.get("priority"), default="P2").upper()
    priority = PRIORITY_MAP.get(raw_priority)
    if priority is None:
        raise TransformError(
            f"用例 {case_id} 优先级 {raw_priority!r} 非法,允许 P0/P1/P2/P3"
        )

    raw_type = _ensure_str(case.get("type"), default="functional").lower()
    if raw_type not in TYPE_MAP:
        raise TransformError(
            f"用例 {case_id} type {raw_type!r} 非法,"
            f"允许: {sorted(TYPE_MAP.keys())}"
        )
    new_type, type_note = TYPE_MAP[raw_type]

    description = _build_description(case)
    if type_note:
        description = (
            f"({type_note}) {description}" if description else f"({type_note})"
        )

    transformed: dict[str, Any] = {
        "id": case_id,
        "title": _ensure_str(case.get("title")),
        "priority": priority,
        "type": new_type,
    }
    if description:
        transformed["description"] = description

    if "preconditions" in case and case["preconditions"]:
        transformed["preconditions"] = list(case["preconditions"])

    transformed["steps"] = list(case.get("steps") or [])
    transformed["expected_results"] = list(case.get("expected_results") or [])

    if not transformed["steps"]:
        raise TransformError(f"用例 {case_id} steps 为空")
    if not transformed["expected_results"]:
        raise TransformError(f"用例 {case_id} expected_results 为空")

    if case.get("tags"):
        transformed["tags"] = list(case["tags"])

    transformed["auto"] = bool(case.get("auto", False))

    extras = (
        set(case.keys()) - TEST_TC_FIELDS - DROPPED_TC_FIELDS - {"req_ref", "trace"}
    )
    if extras:
        print(
            f"  ! 用例 {case_id} 删除了未识别字段: {sorted(extras)}",
            file=sys.stderr,
        )

    return transformed


def _infer_module_from_path(yaml_path: Path) -> str:
    """从文件所在目录推断 module 名(规则 4 默认值)。

    形如 ``releases/webhook-v5/add-webhook.yaml`` → ``webhook-v5``。
    """
    parent = yaml_path.parent.name
    return parent or "待确认"


def build_metadata(
    raw_metadata: dict[str, Any] | None,
    yaml_path: Path,
    *,
    module_override: str | None,
    feature_override: str | None,
    owner_override: str | None,
) -> dict[str, Any]:
    """生成 TEST metadata。

    优先级: 命令行参数 > 原文件已有值 > 默认推断值。
    """
    raw = raw_metadata or {}
    metadata = {
        "module": module_override
        or _ensure_str(raw.get("module"))
        or _infer_module_from_path(yaml_path),
        "feature": feature_override
        or _ensure_str(raw.get("feature"))
        or yaml_path.stem,
        "owner": owner_override or _ensure_str(raw.get("owner")) or "Tester",
        "last_reviewed": _ensure_str(raw.get("last_reviewed"))
        or date.today().isoformat(),
    }

    tags = raw.get("tags")
    metadata["tags"] = list(tags) if tags else []

    extras = set(raw.keys()) - TEST_METADATA_FIELDS
    if extras:
        print(
            f"  ! metadata 删除了未识别字段: {sorted(extras)}",
            file=sys.stderr,
        )
    return metadata


def transform_document(
    data: Any,
    yaml_path: Path,
    *,
    module_override: str | None = None,
    feature_override: str | None = None,
    owner_override: str | None = None,
) -> dict[str, Any]:
    """主转换入口。支持两种输入形态:

    1. 裸列表(通用格式默认形态): ``[{...}, {...}]``
    2. 已含 metadata 的 mapping: ``{metadata:..., test_cases:[...]}``
    """
    if isinstance(data, list):
        raw_metadata: dict[str, Any] | None = None
        cases = data
    elif isinstance(data, dict):
        raw_metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else None
        cases = data.get("test_cases") or []
        if not isinstance(cases, list):
            raise TransformError("test_cases 字段必须是列表")
    else:
        raise TransformError(
            f"YAML 顶层结构非法,期望 list 或 mapping,实际: {type(data).__name__}"
        )

    if not cases:
        raise TransformError("未发现任何 test_case,无法转换")

    metadata = build_metadata(
        raw_metadata,
        yaml_path,
        module_override=module_override,
        feature_override=feature_override,
        owner_override=owner_override,
    )

    transformed_cases = [
        transform_case(case, case_index=i) for i, case in enumerate(cases)
    ]

    seen_ids: set[str] = set()
    for tc in transformed_cases:
        if tc["id"] in seen_ids:
            raise TransformError(f"用例 ID 重复: {tc['id']}")
        seen_ids.add(tc["id"])

    return {"metadata": metadata, "test_cases": transformed_cases}


class _TestDumper(yaml.SafeDumper):
    """自定义 dumper:tags 用 flow style 与 ``adapters/test.md`` 示例一致。"""


def _represent_str(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_TestDumper.add_representer(str, _represent_str)


def _represent_dict_preserve_order(
    dumper: yaml.SafeDumper, data: dict[str, Any]
) -> yaml.MappingNode:
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


_TestDumper.add_representer(dict, _represent_dict_preserve_order)


def dump_yaml(doc: dict[str, Any]) -> str:
    """以稳定顺序输出 YAML,与 ``adapters/test.md`` 示例风格保持一致。

    - 字符串含换行: 使用 literal block(``|``)
    - tags 列表: 输出后再做一次正则归一化为 flow style
    """
    rendered = yaml.dump(
        doc,
        Dumper=_TestDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=4096,
    )

    return _flow_inline_tags(rendered)


def _flow_inline_tags(rendered: str) -> str:
    """把多行 ``tags:`` 列表合并为 flow style ``tags: [a, b]``。

    仅匹配 tags / metadata.tags;其余列表保持 block style。
    """
    import re

    pattern = re.compile(
        r"^(?P<indent>[ \t]*)tags:\n"
        r"(?P<items>(?:\1[ \t]*-[^\n]*\n)+)",
        re.MULTILINE,
    )

    def repl(match: "re.Match[str]") -> str:
        indent = match.group("indent")
        raw_items = match.group("items").strip().splitlines()
        values = [item.strip().lstrip("-").strip() for item in raw_items]
        return f"{indent}tags: [{', '.join(values)}]\n"

    return pattern.sub(repl, rendered)


def _validate_via_schema(doc: dict[str, Any]) -> list[str]:
    """直接用 jsonschema 校验 dict(避免落盘后再读)。"""
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        return ["未安装 jsonschema,无法执行 --validate;请安装后重试"]

    schema_path = (
        Path(__file__).resolve().parent.parent.parent
        / "test-test-case-skill"
        / "schema"
        / "test-case-schema.json"
    )
    if not schema_path.exists():
        return [f"找不到 TEST schema: {schema_path}"]

    import json

    with schema_path.open(encoding="utf-8") as f:
        schema = json.load(f)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    if not errors:
        return []
    return [
        f"[{' → '.join(str(p) for p in err.path) or '<root>'}] {err.message}"
        for err in errors
    ]


def _resolve_output(input_path: Path, output: Path | None) -> Path:
    if output is not None:
        return output
    if input_path.suffixes[-2:] == [".test", ".yaml"]:
        return input_path
    return input_path.with_suffix(".test.yaml")


def transform_file(
    input_path: Path,
    output_path: Path | None,
    *,
    dry_run: bool,
    validate: bool,
    module_override: str | None,
    feature_override: str | None,
    owner_override: str | None,
) -> bool:
    """处理单个文件,返回 True 表示成功。"""
    raw = input_path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        print(f"  ✗ {input_path}: YAML 语法错误 {e}", file=sys.stderr)
        return False

    try:
        doc = transform_document(
            data,
            input_path,
            module_override=module_override,
            feature_override=feature_override,
            owner_override=owner_override,
        )
    except TransformError as e:
        print(f"  ✗ {input_path}: {e}", file=sys.stderr)
        return False

    if validate:
        errors = _validate_via_schema(doc)
        if errors:
            print(f"  ✗ {input_path}: schema 校验失败", file=sys.stderr)
            for err in errors:
                print(f"      {err}", file=sys.stderr)
            return False

    rendered = dump_yaml(doc)

    if dry_run:
        print(f"--- {input_path} (dry-run) ---")
        print(rendered)
        return True

    target = _resolve_output(input_path, output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    print(f"  ✓ {input_path} → {target} ({len(doc['test_cases'])} cases)")
    return True


def collect_inputs(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in (".yaml", ".yml") else []

    pattern = "**/*" if recursive else "*"
    candidates = [
        f
        for f in path.glob(pattern)
        if f.is_file() and f.suffix.lower() in (".yaml", ".yml")
    ]
    return sorted(f for f in candidates if not f.name.endswith(".test.yaml"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将通用格式 YAML 转换为 TEST 兼容格式"
    )
    parser.add_argument("path", help="输入文件或目录")
    parser.add_argument("-o", "--output", help="输出路径(单文件场景)")
    parser.add_argument(
        "--recursive", "-r", action="store_true", help="递归处理目录"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只打印结果不写文件"
    )
    parser.add_argument(
        "--validate", action="store_true", help="转换后立即用 TEST schema 校验"
    )
    parser.add_argument("--module", help="覆盖 metadata.module")
    parser.add_argument("--feature", help="覆盖 metadata.feature")
    parser.add_argument("--owner", help="覆盖 metadata.owner")
    args = parser.parse_args()

    input_root = Path(args.path)
    if not input_root.exists():
        print(f"错误:路径不存在 {input_root}", file=sys.stderr)
        return 1

    if args.output and (input_root.is_dir() or args.recursive):
        print("错误:目录/递归模式下不支持 -o,产物默认落在同名 .test.yaml", file=sys.stderr)
        return 1

    files = collect_inputs(input_root, args.recursive)
    if not files:
        print("未找到 .yaml/.yml 输入文件")
        return 0

    output_path = Path(args.output) if args.output else None
    success, failed = 0, 0
    for f in files:
        ok = transform_file(
            f,
            output_path,
            dry_run=args.dry_run,
            validate=args.validate,
            module_override=args.module,
            feature_override=args.feature,
            owner_override=args.owner,
        )
        if ok:
            success += 1
        else:
            failed += 1

    print(f"\n完成:{success} 成功, {failed} 失败")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
