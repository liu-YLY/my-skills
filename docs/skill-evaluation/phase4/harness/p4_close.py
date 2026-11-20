#!/usr/bin/env python3
"""Phase-4 matched-subset closure harness.

Runs on the existing outputs under docs/skill-evaluation/phase4/runs.
It does not regenerate skill outputs; it only judges the matched subset and
runs trigger classification, then prints the stage-4 summary.

Requires opencode CLI (see README.md in this directory).
"""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path("/workspace")
CASES = ROOT / "docs/skill-evaluation/2026-11-17-quality-suite-v7.2.json"
RUNS = ROOT / "docs/skill-evaluation/phase4/runs"
OPENCODE = os.environ.get("OPENCODE_BIN", "/tmp/opencode-runner/node_modules/.bin/opencode")
JUDGE = "opencode/mimo-v2.6-flash-free"
RUNNER = "opencode/longcat-2.5-free"
JUDGE_DIR = RUNS / "judge-mimo"
CWD = os.environ.get("OPENCODE_CWD", "/tmp/empty-run")
VMAP = {"base": "baseline", "inv1": "new", "dom1": "old"}


def call(prompt: str, model: str, timeout: int = 240) -> tuple[str, str]:
    try:
        proc = subprocess.run([OPENCODE, "run", prompt, "-m", model, "--format", "json"],
                              cwd=CWD, capture_output=True, text=True, timeout=timeout,
                              env={**os.environ, "NO_COLOR": "1"})
    except subprocess.TimeoutExpired:
        return "", "timeout"
    texts = []
    for line in proc.stdout.splitlines():
        line = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "text":
            value = (event.get("part") or {}).get("text", "")
            if value:
                texts.append(value)
    out = "\n".join(texts).strip()
    err = re.sub(r"\x1b\[[0-9;]*m", "", proc.stderr).strip()
    return out, err


def extract_json(text: str) -> dict | None:
    text = re.sub(r"```(?:json)?", "", text)
    a, b = text.find("{"), text.rfind("}")
    if a < 0 or b <= a:
        return None
    try:
        return json.loads(text[a:b + 1])
    except json.JSONDecodeError:
        return None


def matched_ids() -> list[str]:
    out = []
    for p in sorted((RUNS / "dom1").glob("*-r1.md")):
        if p.stat().st_size >= 100:
            out.append(p.name.split("-r1")[0])
    return out


def judge_prompt(output: str, checks: list[str]) -> str:
    lines = ["You are an independent evaluator. Do not use tools. Read the artifact and evaluate each check strictly.",
             'Return ONLY JSON: {"results":[{"index":1,"pass":true,"evidence":"quote or position"}]}',
             "A check passes only when the artifact explicitly contains the required content. Missing evidence => false.",
             "Checks:"]
    lines += [f"{i}. {c}" for i, c in enumerate(checks, 1)]
    lines += ["Artifact:", output]
    return "\n".join(lines)


def judge(variant: str, limit: int, workers: int) -> None:
    cases = {str(c["id"]): c for c in json.loads(CASES.read_text(encoding="utf-8"))["task_cases"]}
    todo = []
    for cid in matched_ids():
        side = JUDGE_DIR / VMAP[variant] / f"{cid}.json"
        p = RUNS / variant / f"{cid}-r1.md"
        if not side.exists() and p.exists() and p.stat().st_size > 100:
            todo.append((cid, cases[cid], p, side))
    print(f"{variant} matched={len(matched_ids())} judge_missing={len(todo)}", flush=True)
    todo = todo[:limit]

    def one(cid: str, c: dict, p: Path, side: Path) -> str:
        text, err = call(judge_prompt(p.read_text(encoding="utf-8"), c["checks"]), JUDGE)
        data = extract_json(text)
        if not data:
            text, err = call("Return only valid JSON with the same schema, no markdown.\n" + text,
                             JUDGE, timeout=180)
            data = extract_json(text)
        by = {}
        for item in (data or {}).get("results", []):
            if isinstance(item, dict) and isinstance(item.get("index"), int):
                by[item["index"]] = item
        if not data or len(by) < len(c["checks"]):
            raise RuntimeError(f"judge invalid ({err or 'missing checks'})")
        results, evidence = [], []
        for i in range(1, len(c["checks"]) + 1):
            item = by[i]
            results.append(bool(item.get("pass") in (True, "true", "True", 1)))
            evidence.append(str(item.get("evidence", ""))[:300])
        side.parent.mkdir(parents=True, exist_ok=True)
        side.write_text(json.dumps({"valid": True, "check_results": results, "evidence": evidence},
                                   ensure_ascii=False), encoding="utf-8")
        return f"{cid} {sum(results)}/{len(results)}"

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        fs = [pool.submit(one, *j) for j in todo]
        for i, f in enumerate(concurrent.futures.as_completed(fs), 1):
            try:
                print(f"[{i}/{len(todo)}] {f.result()}", flush=True)
            except Exception as e:
                print("FAIL", e, flush=True)


def triggers(workers: int) -> None:
    cases = json.loads(CASES.read_text(encoding="utf-8"))["trigger_evals"]
    jobs = [(v, c) for v in ("base", "inv1", "dom1") for c in cases]
    print(f"trigger_jobs={len(jobs)}", flush=True)

    def one(v: str, c: dict) -> dict:
        prompt = ("You are routing a user request to a skill. Answer whether the test-case-engineer skill should handle it.\n"
                  "The skill handles test cases, test points, test-case review, requirement review, and single-feature test strategy.\n"
                  "User request:\n" + c["prompt"] +
                  '\n\nReturn ONLY JSON: {"trigger": true, "reason": "..."}. Use false for other capabilities (PRD writing, bug root cause, performance, state machine, change impact, frontend prep, test data).')
        text, err = call(prompt, RUNNER, timeout=120)
        data = extract_json(text) or {}
        return {"id": str(c["id"]), "variant": VMAP[v], "kind": "trigger",
                "predicted_trigger": bool(data.get("trigger")),
                "should_trigger": bool(c["should_trigger"]),
                "reason": str(data.get("reason", err))[:300]}

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        fs = [pool.submit(one, v, c) for v, c in jobs]
        for i, f in enumerate(concurrent.futures.as_completed(fs), 1):
            try:
                rows.append(f.result())
                print(f"[{i}/{len(jobs)}]", flush=True)
            except Exception as e:
                print("FAIL", e, flush=True)
    rows.sort(key=lambda x: (x["variant"], int(x["id"])))
    (RUNS / "trigger-results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def summary() -> None:
    cases = {str(c["id"]): c for c in json.loads(CASES.read_text(encoding="utf-8"))["task_cases"]}
    matched = matched_ids()
    out = {"matched_ids": len(matched), "variants": {}}
    for variant in ("base", "inv1", "dom1"):
        passed = total = full = judged = 0
        by_cat = collections.defaultdict(lambda: [0, 0])
        for cid in matched:
            side = JUDGE_DIR / VMAP[variant] / f"{cid}.json"
            if not side.exists():
                continue
            payload = json.loads(side.read_text(encoding="utf-8"))
            if not payload.get("valid"):
                continue
            judged += 1
            r = payload["check_results"]
            passed += sum(bool(x) for x in r)
            total += len(r)
            full += int(all(r))
            cat = cases[cid]["category"]
            by_cat[cat][0] += len(r)
            by_cat[cat][1] += sum(bool(x) for x in r)
            by_cat["ALL"][0] += len(r)
            by_cat["ALL"][1] += sum(bool(x) for x in r)
        out["variants"][variant] = {
            "judged": judged, "checks_passed": passed, "checks_total": total,
            "check_rate": round(passed / total, 4) if total else None,
            "full_pass_tasks": full,
            "full_pass_rate": round(full / judged, 4) if judged else None,
            "by_category": {k: {"passed": v[1], "total": v[0],
                               "rate": round(v[1] / v[0], 4) if v[0] else None}
                            for k, v in by_cat.items()},
        }
    trig = RUNS / "trigger-results.jsonl"
    if trig.exists():
        rows = [json.loads(line) for line in trig.read_text(encoding="utf-8").splitlines() if line.strip()]
        acc = collections.defaultdict(lambda: [0, 0])
        for r in rows:
            acc[r["variant"]][0] += 1
            acc[r["variant"]][1] += int(bool(r["predicted_trigger"]) == bool(r["should_trigger"]))
        out["trigger_accuracy"] = {k: {"correct": v[1], "total": v[0],
                                      "rate": round(v[1] / v[0], 4)} for k, v in acc.items()}
    out["dom1_coverage"] = {"valid": len(matched), "total": len(cases),
                            "missing": len(cases) - len(matched)}
    (RUNS / "summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["judge", "triggers", "summary", "ids"])
    ap.add_argument("--variant", choices=list(VMAP), default="base")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if args.action == "ids":
        print(json.dumps(matched_ids(), ensure_ascii=False))
    elif args.action == "judge":
        judge(args.variant, args.limit, args.workers)
    elif args.action == "triggers":
        triggers(args.workers)
    else:
        summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
