#!/usr/bin/env python3
"""P0 score aggregator.

Reads scores.jsonl and checks.json, computes weighted dimension scores, gate
caps, penalties, macro averages, paired deltas and an exact sign test. It does
not pretend that N=3 is enough for an effectiveness conclusion.
"""

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
BENCH = BASE / "benchmark-v1.json"
PRIORITY_WEIGHT = {"critical": 3, "high": 2, "medium": 1}


def weight(category: str) -> dict:
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    profile = {
        "requirement_review": "review",
        "test_points": "test_points",
        "test_cases": "test_cases",
    }[category]
    return bench["scoring_profiles"][profile]["weights"]


def sign_p(wins: int, n: int) -> float:
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(wins, n + 1)) / (2 ** n)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", default="2026-11-17-p0")
    parser.add_argument("--scores-file", default="scores.jsonl")
    args = parser.parse_args()

    batch = BASE / "runs" / args.batch_id
    plan = {r["run_id"]: r for r in json.loads((batch / "run-plan.json").read_text(encoding="utf-8"))}
    checks = {r["run_id"]: r for r in json.loads((batch / "checks.json").read_text(encoding="utf-8"))}
    scores_path = BASE / "scores" / args.batch_id / args.scores_file
    scores = [json.loads(line) for line in scores_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    priority = {m["id"]: PRIORITY_WEIGHT[m["priority"]] for m in bench["must_cover"]}

    rows = []
    for score in scores:
        run_id = score["run_id"]
        meta = plan[run_id]
        w = weight(meta["task_type"])
        weighted = sum(w[d] * score["dimension_scores"][d] / 4 for d in w)
        penalties = 0
        s1 = s2 = s3 = 0
        for err in score.get("errors", []):
            if err["severity"] == "S1":
                s1 += 1
            elif err["severity"] == "S2":
                s2 += 1
                penalties += 5
            elif err["severity"] == "S3":
                s3 += 1
                penalties += 1
        penalties = min(penalties, 25 + 10)

        recall = score.get("coverage_recall")
        if recall is None and score.get("must_cover"):
            num = den = 0
            for mid, hit in score["must_cover"].items():
                p = priority.get(mid, 1)
                num += hit["hit"] * p
                den += p
            recall = num / den if den else 0.0

        caps = []
        if s1:
            caps.append(59)
        if recall is not None:
            if recall < 0.60:
                caps.append(59)
            elif recall < 0.70:
                caps.append(69)
            elif recall < 0.85:
                caps.append(79)
        trace = checks.get(run_id, {}).get("traceability_rate")
        if trace is not None:
            if trace < 0.5:
                caps.append(74)
            elif trace < 0.8:
                caps.append(84)
        final = min([weighted - penalties] + caps)
        rows.append(
            {
                "run_id": run_id,
                "task_id": meta["task_id"],
                "variant": meta["variant"],
                "repeat": meta["repeat"],
                "weighted": round(weighted, 1),
                "coverage_recall": round(recall, 3) if recall is not None else None,
                "s1": s1,
                "s2": s2,
                "s3": s3,
                "penalties": penalties,
                "caps": caps,
                "final": round(final, 1),
                "g0_pass": checks.get(run_id, {}).get("g0_pass", False),
            }
        )

    by_variant = defaultdict(list)
    for row in rows:
        by_variant[row["variant"]].append(row["final"])
    macro = {k: round(sum(v) / len(v), 1) for k, v in by_variant.items()}

    pairs = []
    wins = losses = ties = 0
    for task_id in ["REV-ORDER", "TP-ORDER", "TC-ORDER"]:
        for repeat in [1, 2, 3]:
            with_row = next((r for r in rows if r["task_id"] == task_id and r["variant"] == "with_skill" and r["repeat"] == repeat), None)
            no_row = next((r for r in rows if r["task_id"] == task_id and r["variant"] == "no_skill" and r["repeat"] == repeat), None)
            if not with_row or not no_row:
                continue
            diff = round(with_row["final"] - no_row["final"], 1)
            result = "win" if diff > 5 else "lose" if diff < -5 else "tie"
            if result == "win":
                wins += 1
            elif result == "lose":
                losses += 1
            else:
                ties += 1
            pairs.append({"task_id": task_id, "repeat": repeat, "with": with_row["final"], "no": no_row["final"], "diff": diff, "result": result})

    n = wins + losses
    p = sign_p(wins, n) if n else 1.0
    if n < 6:
        verdict = "?"
    elif wins >= 21 and n >= 30:
        verdict = "P"
    elif wins <= 1:
        verdict = "X"
    else:
        verdict = "N"

    aa = [r for r in rows if r["task_id"] == "REV-ORDER" and r["variant"] == "with_skill"]
    aa_diff = round(max(r["final"] for r in aa) - min(r["final"] for r in aa), 1) if len(aa) >= 2 else None

    summary = {
        "batch_id": args.batch_id,
        "n_pairs": n,
        "macro_by_variant": macro,
        "pairs": pairs,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "sign_test_p_one_sided": round(p, 4),
        "aa_rev_order_score_diff": aa_diff,
        "verdict": verdict,
        "verdict_note": "P0-lite: N<6 and single rater; pilot only, not an effectiveness conclusion.",
        "rows": rows,
    }
    out = BASE / "scores" / args.batch_id / "summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{'run':<32}{'final':>7}{'recall':>9}{'S1':>4}{'S2':>4}{'S3':>4}{'G0':>5}")
    for r in rows:
        print(
            f"{r['run_id']:<32}{r['final']:>7}{str(r['coverage_recall']):>9}"
            f"{r['s1']:>4}{r['s2']:>4}{r['s3']:>4}{str(r['g0_pass']):>5}"
        )
    print(f"\nmacro: {macro}")
    print(f"pairs: {pairs}")
    print(f"wins/losses/ties: {wins}/{losses}/{ties}; sign p={p:.4f}; A/A diff={aa_diff}")
    print(f"verdict: {verdict} (P0-lite, pilot only)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
