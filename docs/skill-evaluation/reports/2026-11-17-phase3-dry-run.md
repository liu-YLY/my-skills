# 阶段 3 干跑报告：需求评审与测试点校验

> **日期**：2026-11-17
> **对象**：`test-case-engineer` 需求评审模式、`validate_requirement_review.py`、`validate_points.py`
> **样例**：`docs/skill-evaluation/gold/`（5 个 PRD + 5 份评审报告 + 5 份测试点清单）
> **边界**：本报告是 **gold 样例干跑**，用于验证模板、字段与校验器；**不是模型输出**，不能作为模型召回率、误报率或质量结论。

## 1. 需求评审 gold 干跑

| 报告 | 种子缺陷 | 报告问题 | 召回 | 误报 | 证据完整率 | 校验器 |
|---|---:|---:|---:|---:|---:|---|
| RR-01 | 5 | 5 | 100% | 0 | 100% | 0 error / 0 warn |
| RR-02 | 5 | 5 | 100% | 0 | 100% | 0 error / 0 warn |
| RR-03 | 5 | 5 | 100% | 0 | 100% | 0 error / 0 warn |
| RR-04 | 5 | 5 | 100% | 0 | 100% | 0 error / 0 warn |
| RR-05 | 5 | 5 | 100% | 0 | 100% | 0 error / 0 warn |
| **合计** | **25** | **25** | **100%** | **0** | **100%** | **5/5 通过** |

- 种子严重级别分布：P0 2、P1 12、P2 11。
- 种子类型分布：缺失 16、权限缺失 4、不可测 1、模糊 1、安全/体验 1、矛盾 1、状态缺失 1。
- 校验器覆盖：结构、9 列必填、ID/类型/级别/状态枚举、原文逐字回查、统计一致、10 维度覆盖、维度合计、未评估原因。
- 「误报 0」是按构造得到的（报告只写种子缺陷），**不代表模型误报率**。

### 可读性抽查

- 5 份报告均使用同一 9 列问题表：位置 / 原文 / 类型 / 级别 / 影响 / 问题 / 待确认 / 状态。
- 每条问题都有可回查原文与待确认问题；没有把建议值写成已确认需求。
- P0/P1 与 P2/P3 在同一表内按级别可辨；未做主观「易读性评分」。

## 2. 测试点 gold 干跑

| 清单 | 测试点 | 用例数（估） | P0 | 校验器 |
|---|---:|---:|---:|---|
| TP-01 | 7 | 12 | 3 | 0 error / 0 warn |
| TP-02 | 7 | 8 | 0 | 0 error / 0 warn |
| TP-03 | 6 | 8 | 2 | 0 error / 0 warn |
| TP-04 | 6 | 6 | 1 | 0 error / 0 warn |
| TP-05 | 8 | 9 | 0 | 0 error / 0 warn |
| **合计** | **34** | **43** | **6** | **5/5 通过** |

校验器覆盖：表头 9 列、ID 格式/唯一、7 维度枚举、P0–P3、单点单目标提示、重复、需求追溯、优先级全 P0、裁剪说明、预算、需求条目覆盖、范围外候选提示。

> TP-02 / TP-05 无 P0，是风险分级结果，不是漏标；校验器不强制每份清单都有 P0。

## 3. 结论与限制

- 两个校验器在 5 份 gold 样例上均 0 error，且能分别检出构造的缺证据、伪造原文、统计不一致、缺维度、重复/无追溯/全 P0/无裁剪等缺陷（见单元测试）。
- 需求评审模板与测试点模板的字段链路已打通：`requirement-review.md` → 报告 → 校验器；`core.md` 阶段 2 → 测试点清单 → 校验器。
- **未执行**：模型侧需求评审、模型侧测试点生成、独立 judge、A/A 一致率。
- 因此本报告只能证明「模板可交付、校验器可用」，不能证明「模型能召回 100% 或误报 0%」。

## 4. 复跑命令

```bash
python3 plugins/testing/skills/test-case-engineer/scripts/validate_requirement_review.py \
  docs/skill-evaluation/gold/requirement-review/RR-01.md \
  --prd docs/skill-evaluation/gold/requirement-review/prd/RR-01.md

python3 plugins/testing/skills/test-case-engineer/scripts/validate_points.py \
  docs/skill-evaluation/gold/test-points/TP-01.md \
  --requirements docs/skill-evaluation/2026-11-17-test-point-cases.json --case-id TP-01

python3 -m pytest plugins/testing/skills/test-case-engineer/scripts/test_validate_requirement_review.py \
  plugins/testing/skills/test-case-engineer/scripts/test_validate_points.py -q
```
