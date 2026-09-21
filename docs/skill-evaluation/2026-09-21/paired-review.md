# 2026-09-21 成对评测记录

## 记录规则

机器可读记录位于 `paired-results.jsonl`。每票必须包含：

- `evaluation_id`、`skill`、`baseline_ref`、`candidate_ref`
- `prompt_ids`、`judge_id`、`verdict`、`margin`、`reason`
- `regression_risk`、`duration_seconds`、`output_path`
- `evidence_status` 与 `evidence_gaps`

`evidence_status=full` 时，`duration_seconds` 必须为非负数，`regression_risk` 必须描述具体退化场景及原因，`output_path` 必须指向保存的原始输出。缺少任一项只能标记 `partial`，不得作为可完全复现的模型评测证据。

## performance-test-engineer

- Baseline：`ad015ff`
- Candidate：`d1bf9b7`
- 提示 1：线上接口 TPS 上不去，加压到 800 就开始报超时，CPU 才 40%，请帮我定位瓶颈。
- 提示 2：某接口偶发超时，无法稳定复现，TPS 数据也取不到，帮我做性能分析。
- 结果：3 票选择 candidate，margin 均为 clear。
- 边界：保存了候选引用、提示与 judge 结论；未记录 judge 耗时，也未要求 judge 给出潜在退化场景，因此证据状态为 partial。

## test-case-engineer

- Baseline：`d1bf9b7`
- Candidate：`6fb0d96`
- 提示 1：评审这些用例，然后直接帮我改好（已有修订授权）。
- 提示 2：仅提供 P0/P1/P2/P3 数量分布，评审优先级合理性。
- 结果：3 票选择 candidate，margin 均为 clear。
- 边界：保存了候选引用、提示与 judge 结论；未记录 judge 耗时，也未要求 judge 给出潜在退化场景，因此证据状态为 partial。

## 尚未回填

其他 Skill 的历史成对评测未保存足够的逐票原始记录。本次不根据会话摘要补造数据；后续评测必须在决策时写入同一 JSONL 契约。
