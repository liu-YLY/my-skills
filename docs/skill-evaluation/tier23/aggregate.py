#!/usr/bin/env python3
"""汇总 Tier 2/3 小规模对照：盲评映射 → runs.jsonl → 配对统计。

用法：
  python docs/skill-evaluation/tier23/aggregate.py

前置：
  - outputs/ 下有 6 份产物（case-{35,37,39}-{with_skill,no_skill}.txt）
  - judge-results.jsonl 已由 judge 回填（blind_id → check_results/evidence）
  - blind-map.json 记录 blind_id → 真实 (case_id, variant)

输出：
  - runs.jsonl（符合 scripts/skill-evals.py 的 --results 契约）
  - 配对统计摘要（with_skill vs no_skill 各自通过率）
"""

import hashlib
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "outputs"
ROOT = HERE.parent.parent.parent  # 仓库根

# 本轮 3 条 case 的 checks 条数（与冻结套件 v5 一致）
CASE_CHECKS = {"35": 4, "37": 4, "39": 5}
VARIANTS = ["with_skill", "no_skill"]


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def make_blind_map() -> dict:
    """把 6 份产物随机映射成中性盲评编号 S1..S6（不暴露 case 或 variant）。"""
    pairs = [(cid, v) for cid in CASE_CHECKS for v in VARIANTS]
    random.shuffle(pairs)
    labels = [f"S{i}" for i in range(1, 7)]
    m = {}
    for label, (cid, v) in zip(labels, pairs):
        m[label] = {"case_id": cid, "variant": v}
    return m


def check_outputs() -> list[dict]:
    """校验产物存在并返回字段。"""
    rows = []
    for cid in CASE_CHECKS:
        for v in VARIANTS:
            p = OUT / f"case-{cid}-{v}.txt"
            if not p.exists():
                print(f"[缺产物] {p}", file=sys.stderr)
                continue
            b = p.read_bytes()
            rows.append({
                "case_id": cid,
                "variant": v,
                "output_path": str(p.relative_to(HERE)),
                "output_characters": len(b.decode("utf-8")),
                "output_sha256": sha256(p),
            })
    return rows


def main():
    blind_map = make_blind_map()
    (HERE / "blind-map.json").write_text(
        json.dumps(blind_map, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已生成 blind-map.json（盲评编号 → 真实 case/variant）")
    print(json.dumps(blind_map, ensure_ascii=False, indent=2))

    rows = check_outputs()
    if len(rows) != 6:
        print(f"[警告] 产物应 6 份，实为 {len(rows)} 份", file=sys.stderr)

    # 读 judge 结果（若已回填）
    jr_path = HERE / "judge-results.jsonl"
    judge = {}
    if jr_path.exists():
        for line in jr_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            judge[r["blind_id"]] = r
    else:
        print("[提示] judge-results.jsonl 尚未生成，跳过判定合并")

    # 生成 runs.jsonl
    runs = []
    # blind_id → (case_id, variant)
    for label, meta in blind_map.items():
        cid, v = meta["case_id"], meta["variant"]
        row = next((r for r in rows if r["case_id"] == cid and r["variant"] == v), None)
        if not row:
            continue
        entry = {
            "skill": "test-case-engineer",
            "id": cid,
            "kind": "task",
            "variant": v,
            "run": 1,
            "duration_seconds": 0,
            "output_characters": row["output_characters"],
            "output_path": row["output_path"],
            "output_sha256": row["output_sha256"],
        }
        if label in judge:
            cr = judge[label].get("check_results")
            if cr is not None and len(cr) == CASE_CHECKS[cid]:
                entry["check_results"] = cr
        runs.append(entry)

    (HERE / "runs.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in runs) + "\n",
        encoding="utf-8",
    )
    print(f"\n已生成 runs.jsonl（{len(runs)} 行）")

    # 配对统计
    print("\n=== 配对统计（with_skill vs no_skill）===")
    stat = {v: {"pass": 0, "total": 0} for v in VARIANTS}
    for r in runs:
        if "check_results" not in r:
            continue
        v = r["variant"]
        stat[v]["pass"] += sum(r["check_results"])
        stat[v]["total"] += len(r["check_results"])
    for v in VARIANTS:
        s = stat[v]
        rate = s["pass"] / s["total"] if s["total"] else 0
        print(f"  {v:11s}: {s['pass']}/{s['total']} = {rate:.1%}")
    if all(s["total"] for s in stat.values()):
        ws = stat["with_skill"]["pass"] / stat["with_skill"]["total"]
        ns = stat["no_skill"]["pass"] / stat["no_skill"]["total"]
        diff = ws - ns
        print(f"\n  差异 with_skill - no_skill = {diff:+.1%}")
        if diff > 0:
            print("  → 方向性：这 3 条 case 上，有 skill 略优（不可外推，见 README §6）")
        elif diff < 0:
            print("  → 方向性：这 3 条 case 上，裸模型反而略优（需排查 skill 是否带来负担）")
        else:
            print("  → 方向性：无差异（可能 case 太简单，或口径对 skill 优势不敏感）")

    print("\n下一步：")
    print("  python scripts/skill-evals.py --skill test-case-engineer --results "
          "docs/skill-evaluation/tier23/runs.jsonl --expected-runs 1 --variants with_skill no_skill")


if __name__ == "__main__":
    main()
