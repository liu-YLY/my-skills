# 语义事实抽取

> **何时阅读**：评审模式 R2 第 10 维度语义一致性检测前读取；默认生成不读。生成流程见 [../test-case-engineer-core.md](../test-case-engineer-core.md) 阶段 3，写作约束见 [writing-rules.md](writing-rules.md)。

## 语义事实抽取

> 将用例字段抽取为 SemanticFacts，供 MCP `check_semantic_conflicts` 做确定性检测；只归一化，不做冲突判断。

**输出（JSON）**：

```json
{"facts":[{"case_id":"TC_X_001","test_point_id":"TP_X_001","preconditions":[{"subject":"登录状态","state":"已登录","polarity":"affirmative"}],"inputs":[{"input_signature":"登录(account=a,pwd=错)","expected_outcome":"返回401"}],"context":{},"dependencies":[]}]}
```

**归一化规则**：

1. `subject`/`context`：同一概念用同一字符串；主体为名词短语，状态为具体取值；context 保留原文明示的角色、登录状态、权限、配置、时间与对象归属，缺失留空。
2. `polarity`：`affirmative` 成立；`negation` 否定同一状态（“未登录”→state="已登录", polarity="negation"）；`unknown` 不补造；不同状态值不自动互斥。
3. `input_signature` 必须含数据值；同一动作的不同数据必须体现（不能只写 `登录`）。
4. `dependencies` 从 steps 与 preconditions 的 `TC_xxx` 引用提取；自包含用例输出 `[]`。

**硬约束**：每条用例产出一个 SemanticFacts；`test_point_id` 缺失输出 `null`，`preconditions` 为空输出 `[]`；**禁止**输出「冲突/矛盾/不一致」等判断词。
