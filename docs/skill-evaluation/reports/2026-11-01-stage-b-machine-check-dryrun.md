# 阶段 B：机器校验接入的离线对照验证（`dry_run`）

> 日期：2026-11-01
> 范围：`test-case-engineer` 阶段 4 机器校验约定（B1）与 review-checker v0.4.0 确定性规则的匹配性
> 边界：**离线确定性验证，不是模型行为评测，未在宿主内实际调用 MCP，未产出质量分数**
> 配套：[评测执行协议](../test-case-quality-eval-protocol.md)、[阶段 A 基线](2026-11-01-test-case-quality-baseline.md)、[执行计划](../../superpowers/plans/2026-11-01-test-case-quality-plan.md)

## 1. 目的

B1 在生成流程里加入「阶段 4 自检后调用 review-checker 复核字段规范、可执行性、冗余、溯源四类规则」的约定。接入前必须确认两件事：

1. 校验器对**合法用例**不产生 `confirmed` 误报（否则会制造噪音、反向损害可读性与精简）
2. B1 承诺的四类规则**确实能检出**对应问题（否则接入是空话）

## 2. 方法与环境

| 项 | 值 |
|---|---|
| Python | 本地 `.venv-tools/review-checker/Scripts/python.exe` |
| pydantic | 2.14.2 |
| 被测代码 | `plugins/testing/mcp-servers/review-checker/src/review_checker_mcp/validators.py` 的 `validate_all` |
| 调用方式 | 直接构造 `TestCaseSet`，不经过 MCP stdio/HTTP 传输层 |
| 样例来源 | [writing-examples.md](../../../plugins/testing/skills/test-case-engineer/knowledge/writing-examples.md) 的「完整用例示例（好）」「易读版」，另加 1 条订单支付用例 |
| 判定口径 | `confirmed` 与 `candidate` 分开统计；只有 `confirmed` P0/P1 计入误判 |

三组样例：

- **合法组**：3 条结构完整、可判定的用例（Webhook 好例、昵称易读版、订单支付），`test_point_ids` 三条齐全
- **问题组**：1 条明显不合格用例（`验证登录功能正常` / `执行对应操作` / `功能正常`）
- **边界组**：3 条用于触发冗余、必填字段缺失、溯源越界的用例

## 3. 结果

| 组 | 用例数 | 问题总数 | confirmed | candidate | confirmed P0/P1 |
|---|---:|---:|---:|---:|---:|
| 合法组 | 3 | 0 | 0 | 0 | **0** |
| 问题组 | 1 | 3 | 2 | 1 | 2 |
| 边界组 | 3 | 3 | 2 | 1 | 2 |

**误判清单（合法组）**：**空**。3 条来自 skill 自身示例的合法用例均未触发任何 `confirmed` 问题，也未触发 P2 可读性 candidate。

**问题组检出明细**：

| 等级 | 维度 | 规则 |
|---|---|---|
| P0 confirmed | 可执行性 | 占位符命中 |
| P1 confirmed | 可执行性 | 预期仅含模糊结论 |
| P2 candidate | 字段规范 | 可读性：标题以「验证」「测试」开头 |

**边界组检出明细**：

| 等级 | 维度 | 规则 |
|---|---|---|
| P1 candidate | 冗余 | title 相同 |
| P0 confirmed | 字段规范 | 必填字段缺失 |
| P0 confirmed | 溯源 | test_point_id 不在测试点清单中 |

**四类规则覆盖**：字段规范、可执行性、冗余、溯源均有检出记录，B1 的承诺与 `validate_all` 实际能力一致。`candidate` 项按 B1 约定分列、不直接改用例、不计入问题数。

## 4. 结论

1. 把 review-checker 的确定性校验接入生成流程，**在本次样例范围内不会误判合法用例**；合法组零问题、零候选噪音。
2. 四类规则均可工作，且 `candidate` / `confirmed` 分离机制有效（冗余为 candidate，字段缺失与溯源越界为 confirmed）。
3. B1 文档中「未安装 MCP 时如实标注独立模式」的降级约定是必要的：本次使用的是本地 venv 直连 Python 模块，**不等于宿主内 MCP 可用**。

## 5. 限制与未验证项

- 本验证标注 `dry_run`：judge 与执行者同源、样例规模小（合法组 3 条）、合法用例为人工构造且刻意避开已知触发词，**不能推广为「所有合法用例均零误报」**。
- 未验证 MCP stdio/HTTP 传输层、宿主内工具注册、`review_test_cases` 的实际调用与返回解析。
- 未验证生成阶段 1–4 端到端流程中机器校验的插入位置与输出标记是否按 B1 落地（需要模型行为评测）。
- 未执行模型行为评测、无质量分数、token 未重测；本结果不可作 keep/revert 依据，不写入「质量提升」类结论。
- 阶段 B 之前的历史评测数据仍不可比（见阶段 A 基线 §6）。

## 6. 阶段 B 停止点

阶段 B 已交付：B0 腾出 core 行数、B1 写入机器校验约定、B2 完成离线对照验证。**生成规则仍未改变用例内容**（B0 是等价压缩、B1 是校验与披露约定），因此四目标的实际表现与改前一致。

进入阶段 C 前需确认：D3 阈值（单字段 8 / 常规 15 / 复杂 25 条）按推荐写入；C1 的 7 维度机械乘法改为「按风险裁剪 + 裁剪理由」；C2 删除「每批 20–30 条」并把覆盖合格线从 ≥80% 改为 100% 或显式未覆盖原因；C3 的总量预算落在 `case-arrangement.md`。
