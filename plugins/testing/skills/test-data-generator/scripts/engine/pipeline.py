import json
import platform
import time
import uuid
from importlib.metadata import version
from pathlib import Path

from jsonschema import Draft202012Validator

from . import VERSION
from .common import Budget, ProfileError, ResourceError, digest
from .exporters import Writer, export_data, read_bundle
from .negative import build_negative_cases, validate_negative_cases
from .profile import ROOT, inspect_profile
from .relations import generate_dataset
from .validator import validate_data

REPORT_SCHEMA = json.loads((ROOT / "schemas/report.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(REPORT_SCHEMA)
REPORT_CHECKER = Draft202012Validator(REPORT_SCHEMA)


def combined_report(profile, data, cases, scenario_ids, budget, integrity=None):
    report = validate_data(profile, data, budget)
    if not report["error_count"]:
        report["negative_summary"] = validate_negative_cases(profile, data, scenario_ids, cases, budget)
    else:
        report["negative_summary"] = {"validation_status": "not_run", "expected_cases": sum(
            case["count"] for case in profile["negative_scenarios"]), "completed_cases": 0,
            "mismatches": 0, "issues": ["legal baseline validation failed"], "cases": []}
    report["integrity_issues"] = integrity or []
    if report["negative_summary"]["validation_status"] != "passed" or report["integrity_issues"]:
        report["validation_status"] = "failed"
    REPORT_CHECKER.validate(report)
    budget.check()
    return report


def validate_bundle(profile, directory):
    inspect_profile(profile)
    budget = Budget(profile["generation"]["limits"])
    data, cases, scenario_ids, issues = read_bundle(profile, directory, budget)
    return combined_report(profile, data, cases, scenario_ids, budget, issues)


def human_report(report):
    lines = ["# 测试数据校验报告", "", f"数据生成：{report['generation_status']}",
             f"数据校验：{report['validation_status']}", "系统执行：not_run", "",
             f"正常数据违规数：{report['error_count']}",
             f"异常样本完成数：{report['negative_summary']['completed_cases']}",
             f"异常预期不匹配数：{report['negative_summary']['mismatches']}", "",
             f"未执行检查数：{len(report['unexecuted_checks'])}", "",
             "规则统计和错误定位见 validation-report.json。", "",
             "数据校验结果不代表业务接口执行或业务测试通过。", ""]
    if report["issues"]:
        lines.extend(["待确认规则：", *[f"- {item['target']}：{item['confirmation']}" for item in report["issues"]], ""])
    return "\n".join(lines)


def preserve_failed_run(staging, target, error):
    staging, target = Path(staging), Path(target)
    directory = staging if staging.is_dir() else target if target.is_dir() else None
    if directory is None:
        return
    failure = {"schema_version": "1.0", "run_id": target.name, "generation_status": "failed",
               "validation_status": "not_run", "system_execution_status": "not_run",
               "error": str(error)}
    (directory / "manifest.json").write_text(json.dumps(failure, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    failed = target.with_name(target.name + ".failed")
    if not failed.exists():
        directory.rename(failed)


def generate_bundle(profile, output_root, on_start=None):
    plan = inspect_profile(profile)
    root = Path(output_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_id = f"{profile['profile_id']}-{uuid.uuid4().hex}"
    staging, target = root / f".{run_id}.tmp", root / run_id
    if target.exists():
        raise FileExistsError("output directory already exists")
    staging.mkdir()
    if on_start is not None:
        on_start(str(staging), str(target))
    budget = Budget(profile["generation"]["limits"])
    writer = Writer(staging, budget)
    try:
        data, scenario_ids, plan = generate_dataset(profile, budget)
        baseline = validate_data(profile, data, budget)
        cases = build_negative_cases(profile, data, scenario_ids, budget) if not baseline["error_count"] else []
        writer.json("profile.normalized.json", profile)
        writer.json("generation-plan.json", plan)
        entity_files = export_data(writer, profile, data, cases)
        provisional = {"profile_hash": digest(profile), "dataset_id": digest(data),
                       "files": writer.files, "entity_files": entity_files}
        (staging / "manifest.json").write_text(json.dumps(provisional, ensure_ascii=False), encoding="utf-8")
        restored, restored_cases, restored_ids, issues = read_bundle(profile, staging, budget)
        (staging / "manifest.json").unlink()
        report = combined_report(profile, restored, restored_cases, restored_ids, budget, issues)
        report["generation_status"] = "complete"
        REPORT_CHECKER.validate(report)
        writer.json("validation-report.json", report)
        writer.write("report.md", [human_report(report)])
        manifest = {"schema_version": "1.0", "run_id": run_id, "engine_version": VERSION,
                    "python_version": platform.python_version(),
                    "dependencies": {name: version(name) for name in ("PyYAML", "jsonschema")},
                    "seed": profile["generation"]["seed"], "reference_datetime": profile["generation"].get("reference_datetime"),
                    "profile_hash": digest(profile), "dataset_id": digest(data),
                    "entity_files": entity_files, "files": dict(writer.files),
                    "duration_seconds": time.monotonic() - budget.started,
                    "generation_status": "complete", "validation_status": report["validation_status"],
                    "system_execution_status": "not_run"}
        writer.json("manifest.json", manifest)
        if target.exists():
            raise FileExistsError("output directory appeared during generation")
        result = {"output_directory": str(target), "generation_status": "complete",
                "validation_status": report["validation_status"], "system_execution_status": "not_run",
                "normal_rows": sum(len(rows) for rows in data.values()), "negative_cases": len(cases),
                "profile_hash": digest(profile), "dataset_id": digest(data)}
        budget.check()
        staging.rename(target)
        return result
    except BaseException as error:
        preserve_failed_run(staging, target, "interrupted" if isinstance(error, KeyboardInterrupt) else error)
        raise
