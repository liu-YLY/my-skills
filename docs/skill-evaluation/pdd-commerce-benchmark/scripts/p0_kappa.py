#!/usr/bin/env python3
"""Quadratic weighted kappa for two P0 score passes.

This is a mechanics check. If both passes come from the same model, the
result is an upper bound / consistency check, not human inter-rater reliability.
"""

import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DIMS = ["D1", "D2", "D3", "D4", "D5", "D6"]
MAX_SCORE = 4


def qwk(pairs: list[tuple[int, int]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    size = MAX_SCORE + 1
    observed = [[0] * size for _ in range(size)]
    for a, b in pairs:
        observed[a][b] += 1
    row = [sum(observed[i]) for i in range(size)]
    col = [sum(observed[i][j] for i in range(size)) for j in range(size)]
    num = den = 0.0
    for i in range(size):
        for j in range(size):
            weight = (i - j) ** 2
            num += weight * observed[i][j]
            den += weight * row[i] * col[j] / n
    if den == 0:
        return 1.0 if num == 0 else 0.0
    return 1 - num / den


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", default="2026-11-17-p0")
    parser.add_argument("--r1", default="scores.jsonl")
    parser.add_argument("--r2", default="scores-r2.jsonl")
    args = parser.parse_args()

    base = BASE / "scores" / args.batch_id
    r1 = {json.loads(line)["run_id"]: json.loads(line) for line in (base / args.r1).read_text(encoding="utf-8").splitlines() if line.strip()}
    r2 = {json.loads(line)["run_id"]: json.loads(line) for line in (base / args.r2).read_text(encoding="utf-8").splitlines() if line.strip()}
    common = sorted(set(r1) & set(r2))
    if not common:
        raise SystemExit("no common run_id between the two score files")

    result = {"batch_id": args.batch_id, "n": len(common), "dimensions": {}, "mean_kappa": 0.0}
    kappas = []
    for dim in DIMS:
        pairs = [(int(r1[rid]["dimension_scores"][dim]), int(r2[rid]["dimension_scores"][dim])) for rid in common]
        k = qwk(pairs)
        exact = sum(1 for a, b in pairs if a == b) / len(pairs)
        adjacent = sum(1 for a, b in pairs if abs(a - b) <= 1) / len(pairs)
        mae = sum(abs(a - b) for a, b in pairs) / len(pairs)
        result["dimensions"][dim] = {
            "kappa": round(k, 4),
            "exact_agreement": round(exact, 4),
            "adjacent_agreement": round(adjacent, 4),
            "mae": round(mae, 4),
        }
        kappas.append(k)
    result["mean_kappa"] = round(sum(kappas) / len(kappas), 4)
    out = base / "kappa.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"n={len(common)} mean_kappa={result['mean_kappa']:.4f}")
    for dim in DIMS:
        d = result["dimensions"][dim]
        print(f"{dim}: kappa={d['kappa']:.4f} exact={d['exact_agreement']:.2f} adjacent={d['adjacent_agreement']:.2f} mae={d['mae']:.2f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
