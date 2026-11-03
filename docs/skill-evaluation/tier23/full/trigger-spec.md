# trigger 判定规格（12 条路由触发）

> trigger 测的是「模型能否正确判断该不该触发 test-case-engineer skill」，产出是布尔 `predicted_trigger`，与 task 的 219 checks 完全两套逻辑。

## 判定方式

judge（zcode，独立模型）需要读取 **SKILL.md 的触发/路由规则**（这是唯一需要读 skill 指令的地方，因为 trigger 测的就是「能否按 skill 的路由规则判断」），然后对 12 条 query 逐条判定：这条 query **应该不应该触发 skill**。

输出 `predicted_trigger`（true=应触发 / false=不应触发），再与 `should_trigger` 真值比对。

## 12 条 trigger 清单（真值 `should_trigger`）

| # | category | should_trigger | query |
|---|---|---:|---|
| 1 | positive | true | 帮我为登录功能编写测试用例 |
| 2 | positive | true | 评审这批测试用例的质量 |
| 3 | positive | true | 快速帮我写支付模块的测试用例 |
| 4 | near_miss | true | 增量评审 feat/order 分支的用例改动 |
| 5 | near_miss | true | 用例太多评审不完，帮我们出一个评审方案 |
| 6 | near_miss | true | 给产品UI前后端讲一下我们的测试思路和用例覆盖度 |
| 7 | near_miss | true | 用探索式模式测试登录功能 |
| 8 | skill_conflict | false | 帮我做性能测试方案，需要压测接口吞吐量 |
| 9 | skill_conflict | false | 分析这个bug的根因，线上登录接口返回500 |
| 10 | skill_conflict | false | 制定项目的整体测试策略和测试计划 |
| 11 | negative | false | 帮我写单元测试代码 |
| 12 | negative | false | 帮我部署测试环境 |

## judge prompt（zcode 执行）

```
你是独立评测 judge。请读取文件 plugins/testing/skills/test-case-engineer/SKILL.md 中的「触发条件 / 路由规则」部分，据此判断下面每条用户请求【是否应该触发 test-case-engineer 这个 skill】。

只输出一个 JSON 数组，每项 true（应触发）或 false（不应触发），不要解释：
[true, true, ..., false]

待判定的 12 条请求（顺序固定）：
1. 帮我为登录功能编写测试用例
2. 评审这批测试用例的质量
3. 快速帮我写支付模块的测试用例
4. 增量评审 feat/order 分支的用例改动
5. 用例太多评审不完，帮我们出一个评审方案
6. 给产品UI前后端讲一下我们的测试思路和用例覆盖度
7. 用探索式模式测试登录功能
8. 帮我做性能测试方案，需要压测接口吞吐量
9. 分析这个bug的根因，线上登录接口返回500
10. 制定项目的整体测试策略和测试计划
11. 帮我写单元测试代码
12. 帮我部署测试环境
```

## 汇总指标（混淆矩阵）

```
                实际 should_trigger
                true      false
预测 true    →  TP        FP
预测 false   →  FN        TN

precision = TP/(TP+FP)
recall    = TP/(TP+FN)
```

trigger 的判定结果写入 `trigger-results.jsonl`，字段：`{"skill":"test-case-engineer","id":"1","kind":"trigger","variant":"with_skill","run":1,"predicted_trigger":bool}`。

> 注：trigger 的 no_skill 对照意义有限（no_skill 时模型本就不该有路由概念），完整评测通常只测 with_skill 下的路由准确性。本阶段先只测 with_skill 的 12 条。
