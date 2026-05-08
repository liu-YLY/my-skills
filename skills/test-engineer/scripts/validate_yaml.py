"""YAML 测试用例校验工具：校验生成的 YAML 是否符合 TEST test-case-schema 规范。

用法：
    python scripts/validate_yaml.py <yaml文件路径>       # 校验单个文件
    python scripts/validate_yaml.py <目录路径> --recursive  # 递归校验目录下所有 .yaml/.yml

依赖：jsonschema, pyyaml（已在 requirements.txt 中）
"""

import argparse
import json
import sys
from pathlib import Path


def _find_schema_path() -> Path:
    script_dir = Path(__file__).resolve().parent
    candidate = (
        script_dir.parent.parent
        / "test-test-case-skill"
        / "schema"
        / "test-case-schema.json"
    )
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"找不到 TEST schema 文件。预期路径：{candidate}\n"
        "请确保 test-test-case-skill 与 test-engineer 在同一 skills 目录下。"
    )


def validate_yaml(yaml_path: Path, schema_path: Path) -> tuple[bool, list[str]]:
    import yaml
    from jsonschema import Draft7Validator

    with open(schema_path) as f:
        schema = json.load(f)

    raw = yaml_path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        return False, [f"YAML 语法错误: {e}"]

    if data is None:
        return False, ["YAML 文件为空"]

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if not errors:
        return True, []

    messages = []
    for err in errors:
        path = " → ".join(str(p) for p in err.path) if err.path else "<根>"
        msg = f"[{path}] {err.message}"
        if err.validator == "additionalProperties":
            extra = list(err.extra) if isinstance(err.extra, dict) else []
            if extra:
                msg += f"（不允许的字段: {', '.join(extra)}）"
        elif err.validator == "enum":
            allowed = err.validator_value
            msg += f"（允许值: {allowed}）"
        elif err.validator == "type":
            msg += f"（期望类型: {err.validator_value}）"
        elif err.validator == "pattern":
            msg += f"（期望格式: {err.validator_value}）"
        elif err.validator == "required":
            missing = err.validator_value
            if isinstance(missing, list):
                msg += f"（缺少字段: {', '.join(missing)}）"
        messages.append(msg)

    return False, messages


def collect_yaml_files(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in (".yaml", ".yml") else []

    pattern = "**/*" if recursive else "*"
    return sorted(
        f for f in path.glob(pattern) if f.suffix.lower() in (".yaml", ".yml")
    )


def main():
    parser = argparse.ArgumentParser(
        description="校验 YAML 测试用例是否符合 TEST schema"
    )
    parser.add_argument("path", help="YAML 文件或目录路径")
    parser.add_argument("--recursive", "-r", action="store_true", help="递归校验子目录")
    parser.add_argument(
        "--schema",
        help=f"自定义 schema 路径（默认自动查找 test-test-case-skill）",
    )
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"错误：路径不存在 {target}", file=sys.stderr)
        sys.exit(1)

    try:
        schema_path = Path(args.schema) if args.schema else _find_schema_path()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    files = collect_yaml_files(target, args.recursive)
    if not files:
        print("未找到 .yaml/.yml 文件")
        sys.exit(0)

    passed, failed = 0, 0
    for f in files:
        ok, errors = validate_yaml(f, schema_path)
        if ok:
            print(f"  ✓ {f.name}")
            passed += 1
        else:
            print(f"  ✗ {f.name}")
            for err in errors:
                print(f"      {err}")
            failed += 1

    print(f"\n完成：{passed} 通过, {failed} 未通过")

    if failed > 0:
        print("\n常见修复提示：")
        print("  - 顶层必须包含 metadata 和 test_cases（不能是裸列表）")
        print("  - priority 只能取 P0/P1/P2")
        print("  - type 只能取 functional/ui/security/performance/accessibility")
        print("  - 不允许 req_ref、trace 等额外字段（可改写到 description 中）")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
