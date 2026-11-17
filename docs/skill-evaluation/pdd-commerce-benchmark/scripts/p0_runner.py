#!/usr/bin/env python3
"""P0 pilot runner packet generator.

Reads the frozen benchmark, verifies the requirement SHA, creates the batch
directory, and writes one runner packet per planned run. It does NOT call a
model; the packet is the exact input an external runner (human or agent)
should execute.
"""

import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
BENCHMARK = BASE / "benchmark-v1.json"
SKILL_NAME = "test-case-engineer"
P0_TASKS = ["REV-ORDER", "TP-ORDER", "TC-ORDER"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", default="2026-11-17-p0")
    args = parser.parse_args()

    bench = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    req = BASE / bench["requirement_file"]
    actual = sha256(req)
    if actual != bench["requirement_sha256"]:
        raise SystemExit(f"requirement SHA mismatch: {actual}")

    batch = BASE / "runs" / args.batch_id
    for sub in ["prompts", "outputs/raw", "logs"]:
        (batch / sub).mkdir(parents=True, exist_ok=True)

    tasks = {t["id"]: t for t in bench["tasks"]}
    runs = []
    for task_id in P0_TASKS:
        for variant in ["with_skill", "no_skill"]:
            for repeat in [1, 2, 3]:
                runs.append((task_id, variant, repeat))

    run_plan = []
    for task_id, variant, repeat in runs:
        task = tasks[task_id]
        run_id = f"{task_id}__{variant}__r{repeat}"
        contract = bench["output_contracts"][task["output_contract"]]
        lines = [
            "# P0 Runner Packet",
            "",
            f"- run_id: `{run_id}`",
            f"- task_id: `{task_id}`",
            f"- variant: `{variant}`",
            f"- repeat: {repeat}",
            f"- benchmark: `{bench['benchmark_id']}@{bench['version']}`",
            f"- requirement_sha256: `{bench['requirement_sha256']}`",
            f"- skill: `{SKILL_NAME}`" if variant == "with_skill" else "- skill: none",
            "",
            "## 执行要求",
            "",
        ]
        if variant == "with_skill":
            lines.append(f"加载 `{SKILL_NAME}` skill，按该 skill 的流程完成任务；不要读取评分卡、must-cover 或 open_findings。")
        else:
            lines.append("不加载任何 skill，仅依据需求文档和任务提示完成任务。")
        lines += [
            "",
            "## 任务提示",
            "",
            task["prompt"],
            "",
            "## 输出契约",
            "",
            "```json",
            json.dumps(contract, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 输入",
            "",
            f"- 附件：`{req.relative_to(BASE)}`",
            f"- SHA256：`{bench['requirement_sha256']}`",
            "- 运行时应将需求文档全文作为附件提供；不得附加 must-cover、评分卡或历史产物。",
            "",
        ]
        packet = batch / "prompts" / f"{run_id}.md"
        packet.write_text("\n".join(lines), encoding="utf-8")
        run_plan.append(
            {
                "run_id": run_id,
                "task_id": task_id,
                "task_type": task["category"],
                "variant": variant,
                "repeat": repeat,
                "output_path": f"outputs/raw/{run_id}.md",
                "prompt_path": f"prompts/{run_id}.md",
            }
        )

    manifest = {
        "batch_id": args.batch_id,
        "benchmark_id": bench["benchmark_id"],
        "benchmark_version": bench["version"],
        "requirement_file": bench["requirement_file"],
        "requirement_sha256": actual,
        "benchmark_sha256": sha256(BENCHMARK),
        "rubric_sha256": sha256(BASE / bench["scoring_rubric"]),
        "skill_name": SKILL_NAME,
        "skill_version": "9.14.0",
        "model": "pending / external runner",
        "status": "p0-lite: repeat=1, single rater, not blind",
        "known_deviation": [
            "P0 plan calls for 3 repeats and 2 independent reviewers; this batch uses repeat=1 and one rater.",
            "Conclusions are pilot-only and must not be published as quality or improvement evidence."
        ],
    }
    (batch / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (batch / "run-plan.json").write_text(
        json.dumps(run_plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(run_plan)} runner packets to {batch}")


if __name__ == "__main__":
    main()
