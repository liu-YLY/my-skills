# 测试用例 Skill 四目标评测执行协议

> 适用版本：`test-case-engineer` v9.10.0 起（当前 v9.11.0），评测集 42 task / 12 trigger
> 建立日期：2026-11-01（阶段 A）
> 配套：[测评方法论](methodology.md)、[2026-10-31 基线](reports/2026-10-31-baseline.md)
> 状态：**协议已就绪，尚未执行真实模型评测**

## 1. 目的与边界

本协议定义如何把「准确、精简、覆盖面全、人类可读性强」四个目标转成可复跑、可判定的评测动作，并明确哪些结论**不能**由仓库内工具给出。

| 层级 | 内容 | 仓库内能否完成 |
|---|---|---|
| Tier 1 | 输入校验、结构/链接/版本一致性、确定性规则检查 | **能**，见 §2 |
| Tier 2 | 模型按评测集实际生成用例并落盘产物 | **不能**，需外部 runner |
| Tier 3 | 独立 judge 按 expectations 逐条判定 | **不能**，需独立模型或人工盲评 |

`scripts/skill-evals.py` 默认模式明确打印 `Input validation only; model behavior has not been evaluated by this command.`，`--results` 只校验并汇总外部产出的 JSONL。因此 **Tier 1 通过不等于质量达标**。

## 2. Tier 1：本地确定性检查

```bash
python scripts/skill-evals.py --skill test-case-engineer
python scripts/check-skill-consistency.py
python scripts/check-version-sync.py
python scripts/check-knowledge-count.py
python scripts/check-project-inventory.py
python scripts/check-md-links.py
```

期望：`42 task / 12 trigger`，且 6 项全部无错误输出。`skill-evals.py` 的 `validate_trigger_coverage` 要求 trigger 用例四类齐全（positive / negative / near_miss / skill_conflict）且至少各有一条 `should_trigger` 为 true 与 false。

评测集由两部分组成，修改时不可只改其一：

- `plugins/testing/skills/test-case-engineer/test-prompts.json`：40 条 task + 12 条 trigger
- `docs/skill-evaluation/business-regressions.json`：其中 2 条归属 `test-case-engineer`

## 3. Tier 2：外部 runner 执行契约

```bash
# 导出冻结用例（记录输出文件的 SHA256）
python scripts/skill-evals.py --skill test-case-engineer --json > eval-cases.json
```

runner 对每条 case 生成一份真实产物文件，并在 `runs.jsonl` 中写一行。字段契约来自 `scripts/skill-evals.py` 的 `read_results`：

| 字段 | 类型 | 约束 |
|---|---|---|
| `skill` / `id` / `kind` | string | 必须与导出用例键一致；`kind` 为 `task` 或 `trigger` |
| `variant` | string | 只能是 `with_skill` / `baseline` / `old` / `new` / `no_skill` |
| `run` | int | ≥ 1，同一 `(skill,id,kind,variant,run)` 不得重复 |
| `duration_seconds` | number | ≥ 0 且有限 |
| `output_characters` | int | 必须等于产物文件 UTF-8 字符数 |
| `output_path` | string | 绝对路径，或相对 `runs.jsonl` 所在目录 |
| `output_sha256` | string | 必须等于产物文件 SHA256，可省略由脚本代算 |
| `check_results` | bool[] | 仅 task 类；长度必须等于该 case 的 `expectations` 条数 |
| `predicted_trigger` | bool | 仅 trigger 类 |

产物文件必须真实存在，否则该行标记 `artifact_verified = false`，不进入统计。

```bash
# 正式评测建议 3 次重复
python scripts/skill-evals.py --skill test-case-engineer \
  --results runs.jsonl --expected-runs 3
```

返回的 `status` 为 `partial` 时（缺运行、无效产物、未配对运行），**不得**发布评测结论。

## 4. Tier 3：判定口径

1. **judge 独立性**：判定模型不得与被测模型相同；无法盲评时必须在报告标注「未盲评」及可能的方向性偏差。
2. **逐条判定**：每条 expectation 单独给 true/false，并附产物中的证据位置；禁止用整体印象替代。
3. **paired 比较**：有 Skill / 无 Skill（或 old / new）使用同一组 case、同一 run 编号，只比较配对成功的运行。
4. **无效改进识别**：按方法论 §12，若改后版只在措辞或文件组织上变化、任务判定无增益，标注「疑似无效改进」，不得计为质量提升。
5. **断言强度**：expectations 应为可判定句，避免「输出包含 XX」这类存在性断言，避免 `正常` / `正确` / `合理` / `符合预期` 作为判定词（作为被禁止词的引用除外）。

## 5. dry_run 标注规则

本会话内由执行者自行加载 skill、自行核对的冒烟验证一律标注 `dry_run`：

- 可信度低，judge 与执行者同源，不构成独立评测
- 只用于验证「断言是否可判定」「流程是否跑得通」
- 不填入通过率、不参与 keep/revert 决策、不写入「质量提升」类结论
- 报告中与 Tier 1 结论分栏展示

## 6. 已知边界与不可比性

- 2026-11-01 阶段 A 改写了 #1/#2/#24/#32 的 expectations 并新增 #33–#40，`check_results` 数组长度随之变化，**历史 `runs.jsonl` 与当前评测集不兼容**，跨版本分数不可比。
- 2026-09-15 的历史对照为 9 任务 × 3 次、有/无 Skill 均 81/81，零区分度；新用例 #33–#40 专为区分好/坏输出设计，但区分度仍需实测验证。
- 2026-10-31 基线记录的分数与 token 数据仍是 2026-10-10 的旧值，不代表 v9.10.0。
- 全量 expectations 平均长度受历史短断言影响为 19.5 字符，低于方法论 §12 规则 6 的 20 字符提示线；本次改写的 12 条用例平均 25.5 字符、新增 8 条平均 24.3 字符。存量短断言的处理属于后续专项。

## 7. 结论发布前置条件

同时满足才可写「效果结论」：

1. Tier 1 六项全绿
2. Tier 2 `status = evaluated` 且所有 variant 配对完整
3. Tier 3 判定者与被测模型独立，或明确标注未盲评及置信度
4. 报告中列出未评估维度、未覆盖 case 与 dry_run 项
5. 未使用 `dry_run` 结果支撑任何提升类表述
