#!/usr/bin/env python3
"""Import two reviewer CSV sheets and produce a P0 review summary.

Usage:
  python3 scripts/p0_import_review.py \
    --r1 /path/to/score-sheet-R1.csv \
    --r2 /path/to/score-sheet-R2.csv \
    --out scores/2026-11-17-p0/review-import.json

The CSV must follow reviewer/score-sheet-R1.csv. The blind key maps S01..S18
back to run_id; reviewers must not see it.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from p0_kappa import qwk  # noqa: E402

DIMS = ["D1", "D2", "D3", "D4", "D5", "D6"]
RDIMS = ["R1", "R2", "R3", "R4"]
PRIORITY_WEIGHT = {"critical": 3, "high": 2, "medium": 1}


def load_key(batch: Path) -> dict:
    return {x["blind_id"]: x for x in json.loads((batch / "blind-key.json").read_text(encoding="utf-8"))}


def load_checks(batch: Path) -> dict:
    return {x["run_id"]: x for x in json.loads((batch / "checks.json").read_text(encoding="utf-8"))}


def read_sheet(path: Path) -> dict:
    rows = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("blind_id"):
                continue
            rows[row["blind_id"]] = row
    return rows


def as_int(value: str, field: str, blind_id: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise SystemExit(f"{blind_id}: {field} must be an integer, got {value!r}")


def as_float(value: str, field: str, blind_id: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise SystemExit(f"{blind_id}: {field} must be a number, got {value!r}")


def score_row(row: dict, meta: dict, checks: dict, bench: dict) -> dict:
    task_type = meta["task_type"]
    profile = {
        "requirement_review": "review",
        "test_points": "test_points",
        "test_cases": "test_cases",
    }[task_type]
    weights = bench["scoring_profiles"][profile]["weights"]
    dims = {d: as_int(row[d], d, row["blind_id"]) for d in DIMS}
    weighted = sum(weights[d] * dims[d] / 4 for d in weights)

    errors = []
    s1 = as_int(row.get("S1") or 0, "S1", row["blind_id"])
    s2 = as_int(row.get("S2") or 0, "S2", row["blind_id"])
    s3 = as_int(row.get("S3") or 0, "S3", row["blind_id"])
    if s1:
        errors.append({"severity": "S1", "description": "reviewer marked S1"})
    if s2:
        errors.append({"severity": "S2", "description": "reviewer marked S2"})
    if s3:
        errors.append({"severity": "S3", "description": "reviewer marked S3"})
    penalties = min(s2 * 5, 25) + min(s3, 10)

    coverage = as_float(row["coverage_recall"], "coverage_recall", row["blind_id"])
    caps = []
    if s1:
        caps.append(59)
    if coverage < 0.60:
        caps.append(59)
    elif coverage < 0.70:
        caps.append(69)
    elif coverage < 0.85:
        caps.append(79)
    trace = checks.get(meta["run_id"], {}).get("traceability_rate")
    if trace is not None:
        if trace < 0.5:
            caps.append(74)
        elif trace < 0.8:
            caps.append(84)

    readability = None
    if task_type == "test_cases":
        r = {d: as_int(row[d], d, row["blind_id"]) for d in RDIMS}
        r_total = sum(r.values()) / 4
        if r_total < 1:
            dims["D6"] = min(dims["D6"], 1)
        elif r_total < 2:
            dims["D6"] = min(dims["D6"], 2)
        readability = {
            **{f"R{i}": r[f"R{i}"] for i in range(1, 5)},
            "R_total": round(r_total, 2),
            "r4_pass_rate": as_float(row["R4_pass_rate"], "R4_pass_rate", row["blind_id"]),
        }

    final = min([weighted - penalties] + caps)
    return {
        "run_id": meta["run_id"],
        "task_id": meta["task_id"],
        "task_type": task_type,
        "dims": dims,
        "coverage_recall": coverage,
        "readability": readability,
        "errors": errors,
        "final": round(final, 1),
        "notes": row.get("notes", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", default="2026-11-17-p0")
    parser.add_argument("--r1", required=True)
    parser.add_argument("--r2", required=True)
    parser.add_argument("--out", default="scores/2026-11-17-p0/review-import.json")
    parser.add_argument("--human-scores-name", default="scores-human.jsonl")
    args = parser.parse_args()

    batch = BASE / "runs" / args.batch_id
    bench = json.loads((BASE / "benchmark-v1.json").read_text(encoding="utf-8"))
    key = load_key(batch)
    checks = load_checks(batch)
    r1 = read_sheet(Path(args.r1))
    r2 = read_sheet(Path(args.r2))

    if set(r1) != set(key) or set(r2) != set(key):
        raise SystemExit(f"blind ids mismatch: expected {len(key)}, r1={len(r1)}, r2={len(r2)}")

    scored = {}
    for pass_name, sheet in [("R1", r1), ("R2", r2)]:
        scored[pass_name] = {}
        for blind_id, meta in key.items():
            scored[pass_name][blind_id] = score_row(sheet[blind_id], meta, checks, bench)

    dim_kappa = {}
    for dim in DIMS:
        pairs = [(scored["R1"][b]["dims"][dim], scored["R2"][b]["dims"][dim]) for b in key]
        dim_kappa[dim] = round(qwk(pairs), 4)
    r_kappa = {}
    tc_ids = [b for b in key if scored["R1"][b]["task_type"] == "test_cases"]
    for dim in RDIMS:
        pairs = [(scored["R1"][b]["readability"][dim], scored["R2"][b]["readability"][dim]) for b in tc_ids]
        r_kappa[dim] = round(qwk(pairs), 4) if pairs else None

    r4_pairs = [
        (scored["R1"][b]["readability"]["r4_pass_rate"], scored["R2"][b]["readability"]["r4_pass_rate"])
        for b in tc_ids
    ]
    r4_mae = round(sum(abs(a - b) for a, b in r4_pairs) / len(r4_pairs), 4) if r4_pairs else None
    r4_within = round(sum(1 for a, b in r4_pairs if abs(a - b) <= 0.2) / len(r4_pairs), 4) if r4_pairs else None

    disagreements = []
    for b in key:
        a, c = scored["R1"][b], scored["R2"][b]
        for dim in DIMS:
            if abs(a["dims"][dim] - c["dims"][dim]) >= 2:
                disagreements.append({"blind_id": b, "field": dim, "r1": a["dims"][dim], "r2": c["dims"][dim]})
        if abs(a["final"] - c["final"]) > 10:
            disagreements.append({"blind_id": b, "field": "total", "r1": a["final"], "r2": c["final"]})
        if ("S1" in [e["severity"] for e in a["errors"]]) != ("S1" in [e["severity"] for e in c["errors"]]):
            disagreements.append({"blind_id": b, "field": "S1", "r1": "flag", "r2": "diff"})

    mean_kappa = round(sum(dim_kappa.values()) / len(dim_kappa), 4)
    min_kappa = min(dim_kappa.values())
    result = {
        "batch_id": args.batch_id,
        "n": len(key),
        "dimension_kappa": dim_kappa,
        "mean_kappa": mean_kappa,
        "readability_kappa": r_kappa,
        "r4_agreement": {
            "mae": r4_mae,
            "within_0_2": r4_within,
            "target": 0.80,
        },
        "thresholds": {
            "mean_kappa_min": 0.70,
            "min_dimension_kappa_warn": 0.70,
            "r4_agreement_target": 0.80,
        },
        "pass": mean_kappa >= 0.70 and min_kappa >= 0.70,
        "conditional_pass": mean_kappa >= 0.70 and 0.60 <= min_kappa < 0.70,
        "low_dimensions": [d for d, k in dim_kappa.items() if k < 0.70],
        "disagreements": disagreements,
        "adjudication_queue": [x for x in disagreements if x["field"] in {"S1", "total"}],
        "runs": {b: {"R1": scored["R1"][b], "R2": scored["R2"][b]} for b in key},
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = BASE / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    human_scores = BASE / "scores" / args.batch_id / args.human_scores_name
    with human_scores.open("w", encoding="utf-8") as f:
        for b in key:
            s = scored["R1"][b]
            f.write(
                json.dumps(
                    {
                        "run_id": s["run_id"],
                        "dimension_scores": s["dims"],
                        "coverage_recall": s["coverage_recall"],
                        "errors": s["errors"],
                        "notes": s["notes"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(f"n={len(key)} mean_kappa={mean_kappa:.4f} pass={result['pass']} conditional={result['conditional_pass']}")
    print("dimension kappa:", dim_kappa)
    print("readability kappa:", r_kappa)
    print("r4 agreement:", result["r4_agreement"])
    print("low dimensions:", result["low_dimensions"])
    print("adjudication queue:", len(result["adjudication_queue"]))
    print(f"wrote {out} and {human_scores}")


if __name__ == "__main__":
    main()
