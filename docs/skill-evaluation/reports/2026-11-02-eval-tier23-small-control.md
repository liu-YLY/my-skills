# Tier 2/3 小规模真实对照（with_skill vs no_skill）—— 方向性结论

> 日期：2026-11-02
> 基线：分支 `feat/test-case-eval-pilot`，HEAD `280dbfb`；冻结套件 v5（SHA `9a0520ed…`）
> 触发：用户选择「外部 runner + 独立 judge 跑完整 Tier 2/3」，经澄清改为**先做小规模真实对照**验证方向
> 范围：3 条 case（#35/#37/#39）× 2 variant（with_skill / no_skill）× 1 次重复 = 6 份产物、78 条判定
> 边界：**方向性观察，不是整体通过率、不是质量分数、不可外推到 42 条 task**

## 1. 独立性（本报告能成立的前提）

| 角色 | 执行者 | 模型 |
|---|---|---|
| runner（生成产物） | WorkBuddy | DeepSeek 系（reasoning 配置） |
| judge（盲评判定） | 用户在 opencode 客户端 | **GLM 5.3 Flash（智谱，与 runner 不同厂商，思考强度最低）** |

judge 与 runner 分属不同厂商（GLM vs DeepSeek），**满足方法论「judge 与被测模型不同」的独立性要求**；且采用 S1–S6 盲评编号（judge 判定期间不知哪份用了 skill）。这是前 5 次 pilot 一直缺失、而本轮补齐的关键。

## 2. 方法

- 6 份产物由同一 runner 配置生成：`with_skill` 加载 skill 指令、`no_skill` 只读需求原文（禁用 skill）。
- judge（GLM 5.3 Flash）只读判定口径 + 产物，逐条判 true/false 并附证据位置，盲评不暴露 variant。
- 映射见 `tier23/blind-map.json`（本地保留，未提交），汇总见 `tier23/runs.jsonl`、`judge-results.jsonl`。

## 3. 结果

| case | 判定项 | with_skill | no_skill |
|---|---:|---:|---:|
| #35 精简 | 4 | **3/4** | 2/4 |
| #37 覆盖全 | 4 | **3/4** | 2/4 |
| #39 可读性 | 5 | **5/5** | 1/5 |
| **合计** | 13 | **11/13 = 84.6%** | 5/13 = 38.5% |

`--results`：`status = partial`、`with_skill 11/13`、`no_skill 5/13`、`invalid_runs = []`、`unpaired_runs = []`、`unexpected_runs = []`。

**方向性结论：这 3 条 case 上，有 skill 的产物通过率（84.6%）显著高于裸模型（38.5%），差 +46.2 个百分点。**

## 4. 逐条证据（blind 编号 → 真实）

| 产物 | 真实身份 | 判定 | 关键 false 原因 |
|---|---|---|---|
| S1 | #35 no_skill | `[F,F,T,T]` | 16 条超预算且无理由；20 字符用例重复、空值/非法字符重叠 |
| S2 | #39 no_skill | `[F,T,F,F,F]` | 多标题含「（若支持）」「处理正确」模糊措辞；多动作步骤；动词/控件名不统一；业务结果或/按需分支不可判定 |
| S3 | #37 with_skill | `[T,T,F,T]` | 唯一 false：未覆盖条目口径自相矛盾（TP-LOGIN-05 既标「未落为用例」又计入已覆盖） |
| S4 | #37 no_skill | `[T,F,F,T]` | 无需求→用例映射；无未覆盖清单 |
| S5 | #35 with_skill | `[F,T,T,T]` | 唯一 false：11 条超预算且理由证据不足 |
| S6 | #39 with_skill | `[T,T,T,T,T]` | 全通过：标题可定位、单决策点、动词/控件统一、业务结果可判定 |

**最具区分度的是 #39（Webhook 创建，可读性）**：with_skill 5/5 vs no_skill 1/5。裸模型在「标题可定位」「单决策点」「动词/控件原文」「业务结果可判定」上系统性失分，而有 skill 时这四条稳定通过——说明 skill 的可读性规则确实在起作用。

## 5. 诚实边界（重要，避免过度解读）

1. **只有 3 条 case、1 次重复、单 judge**，`status = partial`，**不能外推到 42 条 task 的整体**，不是「通过率 84.6%」的质量结论。
2. **+46.2% 可能被高估**：本轮 3 条 case 恰好是阶段 A 特意设计来「区分好坏输出」的（#33–#40 系列），本身就是 skill 强项场景；对简单 CRUD 类需求，skill 优势可能没那么明显（正是 2026-09-15 历史 81/81 零区分度的教训）。
3. **runner 与 judge 独立性已满足，但仍有残留**：runner 是 `reasoning` 深度思考配置，judge 是 GLM Flash 非思考——二者不仅厂商不同、思考强度也不同，这本身是好事；但「runner 用了深度思考」意味着本对照测的是「深度思考 + skill」vs「深度思考裸模型」，**未单独测「skill 本身」的边际增益**。严格说，要归因到「skill 有用」还需一个「同配置裸模型」基线，本轮 no_skill 已尽量贴近但无法完全等同。
4. `duration_seconds = 0` 占位，未记录真实耗时与 token。
5. 结论仅限「方向性观察」，**不可作 keep/revert 依据**，不构成「质量提升」声明。

## 6. 与历史 pilot 的关系

前 5 次 pilot（v1–v5）都因「runner 与 judge 同源/同模型家族」标「未满足严格独立性」，只能算工具链验证与断言可判定性验证。**本轮是第一次满足独立性的真实对照**，因此第一次能给出「有 skill 是否更好」的方向性判断——尽管仍只是小规模。

## 7. 下一步

1. **（推荐）铺开到完整 Tier 2/3**：42 task + 12 trigger × 3 variant × 3 次重复（约 486 次调用），同样用「WorkBuddy 当 runner + GLM Flash 当 judge」的独立性方案；只有铺开且加 `old`/`baseline` 对照后，才能出可发布的整体结论。
2. **补一个「同配置裸模型」基线**：若要严格归因「skill 本身的增益」，需让 no_skill 也用与 with_skill 相同的模型配置（去掉「深度思考」这个变量）。
3. 停在当前方向性结论，先回阶段 D/E 或处理版本发布。

## 8. 交付物

- `docs/skill-evaluation/tier23/`（README、runner-prompt、judge-prompt、blind-guide、aggregate.py、outputs/ 6 份、blind/ S1–S6）
- `judge-results.jsonl`、`runs.jsonl`、`blind-map.json`（本地保留，已 .gitignore）
- 本报告

> 未升版本（仍 v9.11.0）、未推送、未建 PR；本次产物与判定结果已提交，盲评映射与结果 JSONL 按 .gitignore 本地保留。
