# 规范语句清单索引

> 由 `scripts/extract-rule-inventory.py` 生成；用于瘦身前确认每条规则的处置方式。
> D1–D5 分类为启发式初筛，删除或移位前必须人工复核。

| Skill | 条数 | D1 重复 | D2 移位 | D3 冲突 | D4 参考 | D5 行为 |
|---|---:|---:|---:|---:|---:|---:|
| [test-case-engineer](test-case-engineer.md) | 223 | 0 | 17 | 0 | 39 | 167 |
| [state-machine-test-engineer](state-machine-test-engineer.md) | 155 | 52 | 0 | 0 | 25 | 78 |
| [change-impact-analyzer](change-impact-analyzer.md) | 58 | 0 | 7 | 0 | 2 | 49 |
| [testing-bundle](testing-bundle.md) | 16 | 0 | 0 | 0 | 1 | 15 |

## 已知冲突观察（来自 2026-11 评测报告，需在 1-8 逐条核对）

- **#13 评级阈值**：eval check 写 A/B/C/D 阈值，skill 另有「已确认 P0 → 整体评级 D」；需在判定口径中明确 P0 优先
- **#7/#19 抽样标注**：eval check 期望 >100 条标注「抽样评审」，skill 的 S2 全量分批不实际抽样；需改为按策略判定
- **check 术语依赖**：部分 check 要求出现「10 维度」「CHECKPOINT R3」等流程术语，偏向流程存在性而非产物质量
- **软预算口径**：8/15/25 条软预算需与 check、writing-rules、prompt-strategy 三处保持一致

## 处置类别

- **D1**：纯重复：保留单一权威源，其余删为指针
- **D2**：按需化：默认路径中的移出，已在按需的保留并标注
- **D3**：过时/冲突：人工核对，按优先级修复，不直接删
- **D4**：参考/示例：评估是否保留为按需材料，无证据不删
- **D5**：行为规则：默认保留；删除需配对评测

## 使用方式

1. 每个瘦身批次先在本清单中勾选对应条目，写明「保留 / 移动 / 合并 / 删除」。
2. D1 条目必须指出保留的单一权威源。
3. D2 条目必须在新位置保留摘要和链接，并通过 `check-knowledge-count.py`。
4. D3 条目必须写明冲突双方和裁决优先级，不直接删。
5. D4/D5 条目删除前必须有配对评测证据；否则只允许压缩措辞。
