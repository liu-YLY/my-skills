# 阶段 4 Probe 报告（匹配子集闭环）

> **状态**：`partial` —— 在匹配子集上完成闭环；全量 70 case × 3 变体未完成。
> **日期**：2026-11-17
> **套件**：`2026-11-17-quality-suite-v7.2.json`（70 task / 16 trigger / 354 checks，SHA `5c6bd2ef`）
> **结论**：**不采纳 INV1 / DOM1 / AGG1，保留 base**。理由见 §5。

## 1. 方法

| 项 | 设置 |
|---|---|
| Runner | `opencode/longcat-2.5-free` |
| Judge | `opencode/mimo-v2.6-flash-free`（与 runner 不同厂商） |
| 变体 | base / inv1 / dom1 |
| 生成 | 每 case 1 次；同一 harness、同一 runner、同一 prompt 预算（≤2500 字） |
| 盲评 | judge 只看产物 + checks，不知道变体 |
| 匹配子集 | 只取 `dom1` 有有效输出的 case ID；三变体取交集做 complete-case 比较 |

### 样本

| 项 | 数值 |
|---|---:|
| 套件 task | 70 |
| dom1 有效输出 | 28 |
| base 已判 | 27 |
| inv1 已判 | 26 |
| dom1 已判 | 28 |
| **三变体 complete-case** | **25** |
| 未判 | base `32`；inv1 `31`、`7` |

> dom1 缺失 42 个，主要是长 prompt 在免费模型上 300s 超时；缺失不是随机，可能存在难度/长度选择偏差。

## 2. 主结果（complete-case n=25，128 checks）

| 变体 | 检查通过 | 通过率 | 整任务全通过 | 生成类 | 评审类 |
|---|---:|---:|---:|---:|---:|
| base | 88/128 | 68.75% | 5/25 (20.0%) | 79.17% | 62.50% |
| inv1 | 86/128 | 67.19% | 7/25 (28.0%) | 68.75% | 66.25% |
| dom1 | 86/128 | 67.19% | 4/25 (16.0%) | 62.50% | 70.00% |

### 变化

| 对比 | 总通过率 | 生成类 | 评审类 | 整任务全通过 |
|---|---:|---:|---:|---:|
| inv1 − base | **-1.56pp** | **-10.42pp** | +3.75pp | +8.0pp |
| dom1 − base | **-1.56pp** | -16.67pp | +7.50pp | -4.0pp |

## 3. 关键发现

1. **INV1 未达到采纳门槛**：总通过率 -1.56pp，生成类 -10.42pp；只有评审类 +3.75pp、整任务全通过 +8pp，但 n=25，且方向不一致。未达到「主指标 +≥5pp 且护栏不退化」。
2. **DOM1 的目标类别没有被覆盖**：DOM1 只改需求评审知识，但匹配子集全部是 generation/review，没有 requirement-review case。因此本轮**不能评估 DOM1**，只能保留提案。
3. **dom1 是非目标类别的「噪声参照」**：DOM1 不改变 generation/review 的 skill 内容，但观测到 -1.56pp 总差异；说明 judge/单次运行噪声至少在这个量级。±1.6pp 内的差异不应解释为能力变化。
4. **base 的生成类仍高于 inv1**：INV1 增加的是标题分隔符/编排声明的阻断提示，但本轮生成类反而下降；可能是提示变长后挤压了内容生成，也可能是单次运行噪声。无论原因，没有证据支持采纳。

## 4. 触发评测

**未完成**。48 次分类调用（16 trigger × 3 变体）在免费模型上排队/超时，未形成结果文件。
INV1/DOM1 未修改 `SKILL.md` 的路由描述，因此触发差异理论上只来自模型噪声；但本轮不能给出 trigger accuracy，列为限制，不作为采纳依据。

## 5. 4-6 采纳结论

| 项 | 决策 | 依据 |
|---|---|---|
| INV1（标题分隔符/编排声明闸门） | **不采纳** | 总通过率 -1.56pp；生成类 -10.42pp；无 +5pp 主指标收益 |
| DOM1（需求缺陷高频模式） | **不采纳（未评估）** | 匹配子集无 requirement-review case，无法验证召回/误报 |
| AGG1（INV1+DOM1） | **不构建、不 Probe** | 两个单路都未通过/未评估 |
| base | **保留** | 当前版本在匹配子集上不低于两个候选 |

> 这是一次**无采纳**的 harness² 轮次。无采纳也是有效结论：它阻止了无证据的 rule 增量。

## 6. 限制

- 单次运行，无 3 次重复，无 A/A 一致率；不能给出 `status=evaluated`。
- 免费模型（LongCat / Mimo / HY4）能力与稳定性低于生产模型；超时和 judge 失败已排除，但仍可能引入偏差。
- 匹配子集 n=25，且只覆盖 generation/review；不能外推到 requirement-review、test-points。
- dom1 缺失 42/70，缺失非随机；不能把 dom1 的通过率当作旧版全量能力。
- judge 为单模型，未做第二 judge 交叉；`judge missing` 的 3 个 case 已从 complete-case 中排除。

## 7. 复跑

```bash
# 环境
mkdir -p /tmp/opencode-runner /tmp/empty-run
npm install --prefix /tmp/opencode-runner opencode-ai@1.19.6 --no-audit --no-fund
export OPENCODE_BIN=/tmp/opencode-runner/node_modules/.bin/opencode
export OPENCODE_CWD=/tmp/empty-run

# 汇总（已有输出）
python3 docs/skill-evaluation/phase4/harness/p4_close.py summary-complete
```

下一轮若要评估 DOM1，必须补 `RR-01..RR-12` 的 base/inv1/dom1 三变体输出；当前 dom1 缺失，不能得出 DOM1 有效或无效的结论。
