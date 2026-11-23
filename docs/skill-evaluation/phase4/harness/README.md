# Phase 4 closure harness

只做阶段 4 的收尾：对已生成的 Probe 输出做盲评、触发评测和汇总，不重新生成 skill 输出。

## 环境

```bash
mkdir -p /tmp/opencode-runner /tmp/empty-run
npm install --prefix /tmp/opencode-runner opencode-ai@1.19.6 --no-audit --no-fund
export OPENCODE_BIN=/tmp/opencode-runner/node_modules/.bin/opencode
export OPENCODE_CWD=/tmp/empty-run
```

Runner：`opencode/longcat-2.5-free`（已生成的 base/inv1/dom1 输出）。
Judge：`opencode/mimo-v2.6-flash-free`（与 runner 不同厂商）；GLM 在实测中返回 server error，未使用。

## 匹配子集

`dom1` 有效输出不足 70，为保持三变体可比，只用 `dom1` 有效的 ID 作为匹配子集；缺失用例在报告中单列，不当作能力差异。

## 命令

```bash
# 查看匹配子集
python3 docs/skill-evaluation/phase4/harness/p4_close.py ids

# 盲评，按变体分批
python3 docs/skill-evaluation/phase4/harness/p4_close.py judge --variant base --limit 20 --workers 4
python3 docs/skill-evaluation/phase4/harness/p4_close.py judge --variant inv1 --limit 20 --workers 4
python3 docs/skill-evaluation/phase4/harness/p4_close.py judge --variant dom1 --limit 20 --workers 4

# 触发评测（本轮未完成，免费模型排队超时）
python3 docs/skill-evaluation/phase4/harness/p4_close.py triggers --workers 4

# 汇总
python3 docs/skill-evaluation/phase4/harness/p4_close.py summary-complete
```

输出：

- `docs/skill-evaluation/phase4/runs/judge/<baseline|new|old>/<id>.json`
- `docs/skill-evaluation/phase4/runs/trigger-results.jsonl`
- `docs/skill-evaluation/phase4/runs/summary.json`
