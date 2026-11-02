#!/usr/bin/env python3
"""judge 批处理脚本骨架（阶段 P 完整铺开）。

用途：把 84 份 task 产物 + 219 checks 批量喂给独立 judge（zcode），产出 judge-results.jsonl。

现状：judge 调用入口待接入（zcode 的 API/CLI 尚未确认）。本脚本已完成：
- 读 task-manifest.json 得到 42 条 task 的 checks（从冻结套件 v5 读）
- 读 outputs/ 下 84 份产物
- 生成每份产物的判定 prompt（含 check 组 + 产物内容）
- 预留 judge 调用函数 stub，接入 zcode 后填 `call_judge()`

接入方式（二选一，等用户 23:00 确认 zcode 调用方式后填）：
  方式 A：zcode 提供 HTTP API → 在 call_judge() 里用 urllib 调
  方式 B：zcode 提供 CLI → 在 call_judge() 里用 subprocess 调

用法：
  python docs/skill-evaluation/tier23/full/judge_batch.py --dry-run   # 只生成 prompt 不调 judge
  python docs/skill-evaluation/tier23/full/judge_batch.py             # 实际调用 judge
"""

import argparse
import json
import pathlib
import subprocess
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "outputs"
ROOT = HERE.parent.parent.parent.parent  # 仓库根
FROZEN = ROOT / "docs/skill-evaluation/2026-11-02-test-case-quality-cases-v5.json"

# 通用判定原则（judge 指令头）
JUDGE_HEADER = """你是独立测试用例评测 judge。只做机械判定，不要深度推理、不要脑补规则、不要依据「应该怎么写」推断。

判定原则：
1. 每条 check 单独判 true / false，并附产物里的证据位置（行号或原文片段）。
2. 只在产物文本里找证据；证据不足、含糊、需要猜测 → 判 false 并注明「证据不足」，不给同情分。
3. 一条 check 含多个条件时，全部满足才判 true。
4. 不要猜测、不要标注「这份像是用了什么 skill 或模板」。

输出格式（只输出 JSON，不要解释）：
{"check_results": [true, false, ...], "evidence": ["...", "..."]}

其中 check_results 长度必须等于下面 check 条数。
"""


def load_checks() -> dict:
    """从冻结套件 v5 读 42 条 task 的 checks。"""
    data = json.loads(FROZEN.read_text(encoding="utf-8"))
    checks = {}
    for c in data:
        if c.get("kind") == "task":
            checks[str(c["id"])] = c["checks"]
    return checks


def call_judge_stub(prompt: str) -> str:
    """TODO: 接入 zcode 后替换为真实调用。

    方式 A（HTTP API，示例）：
      req = urllib.request.Request(url, data=json.dumps({"prompt": prompt}).encode(),
                                  headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
      return urllib.request.urlopen(req).read().decode()

    方式 B（CLI，示例）：
      return subprocess.run(["zcode", "run", prompt], capture_output=True, text=True).stdout
    """
    raise NotImplementedError("judge 调用入口待接入 zcode API/CLI")


def build_prompt(case_id: str, checks: list, artifact: str) -> str:
    body = f"{JUDGE_HEADER}\n\n【check 组】（共 {len(checks)} 条）\n"
    for i, chk in enumerate(checks, 1):
        body += f"{i}. {chk}\n"
    body += f"\n【待判产物】\n{artifact}\n"
    return body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="只生成 prompt 数量统计，不调 judge")
    args = parser.parse_args()

    checks = load_checks()
    print(f"已加载 {len(checks)} 条 task 的 checks（来自冻结套件 v5）")

    # 遍历 84 份产物
    results = []
    for case_id, chks in sorted(checks.items(), key=lambda kv: kv[0]):
        for variant in ["with_skill", "no_skill"]:
            p = OUT / f"task-{case_id}-{variant}.txt"
            if not p.exists():
                print(f"[缺] {p}", file=sys.stderr)
                continue
            artifact = p.read_text(encoding="utf-8")
            prompt = build_prompt(case_id, chks, artifact)
            if args.dry_run:
                results.append(None)
                continue
            try:
                resp = call_judge_stub(prompt)
                parsed = json.loads(resp)
                parsed["case_id"] = case_id
                parsed["variant"] = variant
                results.append(parsed)
            except NotImplementedError:
                print("judge 调用入口未接入（zcode API/CLI 待确认）", file=sys.stderr)
                sys.exit(1)

    if args.dry_run:
        print(f"dry-run：将生成 {len(results)} 次 judge 调用（84 份产物）")
        total_checks = sum(len(checks[cid]) for cid in checks for _ in range(2))
        print(f"总判定条数（含两个 variant）≈ {total_checks}")
        return

    out = HERE / "judge-results.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n", encoding="utf-8")
    print(f"judge-results.jsonl 已写入 {len(results)} 行")


if __name__ == "__main__":
    main()
