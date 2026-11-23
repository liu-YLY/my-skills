# Skill 瘦身与质量提升 · 执行交接

> **当前阶段**：阶段 6（发布准备）
> **当前进度**：阶段 5 完成；阶段 6 的版本/文档/CI/拆分已完成，15 个 stacked 分支已推送，6-5 待 PR 合并
> **计划文件**：[2026-11-17-skill-slimming-and-quality-plan.md](2026-11-17-skill-slimming-and-quality-plan.md)
> **工作分支**：15 个 stacked 分支已推送（`feat/eval-*` … `docs/phase5-6-handoff`）；原 `trae/agent-WZBLh1` 与 `backup/pre-stacked-release` 保留
> **更新方式**：每完成一个任务追加一节，最新状态置顶；恢复上下文时先读本文件

---

## 最新状态

| 任务 | 状态 | 产出 |
|---|---|---|
| 1-1 上下文度量脚本 | 已完成 | `scripts/skill_context.py`、`scripts/skill-context-report.py` |
| 1-2 预算门禁 | 已完成 | `scripts/check-context-budget.py`、`scripts/context-budget.json` |
| 1-3 规范语句清单 | 已完成 | `scripts/extract-rule-inventory.py`、`docs/skill-evaluation/rule-inventory/` |
| 1-4 评测套件 v7.1 | 已完成 | `docs/skill-evaluation/2026-11-17-quality-suite-v7.1.json` |
| 1-5 需求评审种子集 | 已完成 | `docs/skill-evaluation/2026-11-17-requirement-review-cases.json` |
| 1-6 测试点种子集 | 已完成 | `docs/skill-evaluation/2026-11-17-test-point-cases.json` |
| 1-7 干净基线 | 部分完成 | 确定性基线完成；模型行为 `blocked`，见 `reports/2026-11-17-quality-baseline.md` |
| 1-8 断言-规则一致性 | 已完成 | `docs/skill-evaluation/reports/2026-11-17-eval-rule-consistency.md` |
| 2-1 写作契约单一权威源 | 已完成 | `knowledge/writing-rules.md` 等 4 文件 25,584 → 12,920 |
| 2-2 prompt-strategy 移出默认路径 | 已完成 | 4,267 → 997；default 53,514 → 49,139 |
| 2-3 test-levels + case-arrangement 合并 | 已完成 | 5,512 → 2,695；default 49,139 → 46,241 |
| 2-4 bug-patterns 压缩 | 已完成 | 5,412 → 3,229；default 46,241 → 44,058 |
| 2-5 core 压缩 | 已完成 | 13,810 → 9,500；default 44,058 → 39,755 |
| 2-6 SKILL.md 压缩 | 已完成 | 7,307 → 4,903；159 → 109 行 |
| 2-7 review-mode 压缩 | 已完成 | 13,563 → 6,711；review 26,418 → 19,566 |
| 2-8 project-knowledge 压缩 | 已完成 | 2,149 → 1,199；default 36,521 → 36,394 |
| 2-9 testing-bundle 压缩 | 已完成 | 17,190 → 10,529；SKILL 7,486 → 5,039 |
| 3-1 需求评审知识 | 已完成 | `knowledge/requirement-review.md` 2,961 |
| 3-2 需求评审模式接入 | 已完成 | SKILL/core/README/预算新增模式 |
| 3-3 bundle 需求评审路由 + 链 10 | 已完成 | 单意图路由、链 10、触发用例 |
| 3-4 需求评审校验器 | 已完成 | `validate_requirement_review.py` 279 行 |
| 3-5 测试点校验器 | 已完成 | `validate_points.py` 263 行 |
| 3-6 5 个 PRD 干跑 | 已完成 | `reports/2026-11-17-phase3-dry-run.md` |
| 4-1 确定性代理失败聚类 | 已完成 | `reports/2026-11-17-phase4-harness-round1.md` |
| 4-2 INV1 提案 | 已完成（未应用） | `phase4/inv1-proposal.md` |
| 4-3 DOM1 提案 | 已完成（未应用） | `phase4/dom1-proposal.md` |
| 4-4 两路 Probe | 部分完成 | base/inv1 各 70；dom1 28；complete-case 25 |
| 4-5 Compose | 未执行 | 无候选通过采纳门槛 |
| 4-6 采纳决策 + 经验库 | 已完成 | 不采纳 INV1/DOM1；保留 base；`experience-library.md` 5 条 |
| 5-1 state-machine 瘦身 | 已完成 | default 44,340 → 33,143；entry 7,081 → 5,498 |
| 5-2 change-impact 瘦身 | 已完成 | default 38,829 → 26,984；entry 6,151 → 4,920 |
| 5-3 test-strategy 瘦身 | 已完成 | default 17,765 → 14,979；entry 6,200 → 4,613 |
| 5-4 bug-analyzer 瘦身 | 已完成 | default 21,100 → 12,390；entry 6,940 → 5,487 |
| 5-5 performance 瘦身 | 已完成 | default 18,726 → 15,491；entry 4,170 → 3,724 |
| 5-6 frontend / test-data 瘦身 | 已完成 | frontend 6,378 → 5,994；test-data 10,029 → 8,992 |
| 5-7 其余 skill 质量评测 | 已完成 | `reports/2026-11-20-phase5-skill-quality.md`；模型行为未执行 |
| 6-1 版本同步 | 已完成 | bundle 3.7.0、test-case 9.15.0、其余 skill patch |
| 6-2 文档同步 | 已完成 | 根 README、overview、plugin README、CHANGELOG、marketplace |
| 6-3 CI 门禁 | 已完成 | CI 增加 `check-context-budget.py --target` |
| 6-4 PR 拆分与交付报告 | 已完成 | 15 个 stacked 分支与 PR #141–#155；报告 `reports/2026-11-23-phase6-release.md` |

---

## 阶段 6 发布准备（6-1～6-4）

### 版本

| Skill | 新版本 |
|---|---:|
| testing-bundle | 3.7.0 |
| test-case-engineer | 9.15.0 |
| state-machine-test-engineer | 1.7.7 |
| change-impact-analyzer | 1.5.2 |
| test-strategy-engineer | 1.3.1 |
| bug-analyzer | 1.2.4 |
| performance-test-engineer | 1.2.4 |
| frontend-test-preparation | 1.0.1 |
| test-data-generator | 1.1.1 |

- plugin `testing` 三份 manifest 同步 3.7.0；marketplace 描述同步。
- 根 README、`docs/skills-overview.md`、plugin README 版本与链数（10 条）已更新。
- 6 个 skill README 版本历史、3 个 CHANGELOG 已补条目。
- CI 新增上下文预算门禁；模型评测 smoke 保持手动。
- 详细报告：`docs/skill-evaluation/reports/2026-11-23-phase6-release.md`。

### 校验

- 六个仓库脚本全绿；`check-version-sync.py` 通过。
- pytest 47 passed；9 个环境失败（沙箱无 PowerShell）。
- review-checker 110 passed；state-machine 114 passed。

### 未完成

- 15 个 stacked 分支已推送，PR **#141–#155** 已创建；未合并、未打 tag（6-5 待执行）。
- PR 合并需逐个 review；超过 400 行的 PR 需确认例外。
- 原 `trae/agent-WZBLh1` 与 `backup/pre-stacked-release` 保留。
- PR 列表与例外说明见阶段 6 报告。

---

## 5-7 其余 skill 质量评测

### 产出

`docs/skill-evaluation/reports/2026-11-20-phase5-skill-quality.md`

### 覆盖

| 项 | 结果 |
|---|---|
| 预算 | 全部 skill/mode 达到 target，无超限 |
| 六个仓库脚本 | 全绿；清单已刷新 |
| pytest | 46 passed；10 个环境失败（要求 PowerShell） |
| MCP | review-checker 110 passed；state-machine 114 passed |
| 触发覆盖 | 10 个 skill 的 trigger case 齐全，每个 ≥4 |
| 规则保留 | 对 6 个 skill 抽检核心硬约束，均保留；唯一措辞变化为「禁止拼接」→「不得将用户输入直接拼入」 |
| 种子回归 | test-case-engineer 沿用阶段 3 gold 结果；本轮瘦身未改其内容 |
| 模型行为 | 无可用 runner/judge，未执行，保持 `partial` |

### 结论

- 阶段 5 验收的「预算全部达成、无只删不测」有确定性证据；规则删除行均为重排、合并或示例移出。
- 不能据此宣称模型生成质量未退化；如需模型侧证据，阶段 6 用付费 runner 对 change-impact / bug-analyzer / performance 各跑 3 case 对照。

---

## 5-6 frontend / test-data 瘦身

### 改动

| 文件 | 变化 |
|---|---:|
| `frontend-test-preparation/SKILL.md` | 4,689 → 4,489 |
| `frontend-test-preparation/references/handoff-template.md` | 1,689 → 1,505 |
| `test-data-generator/SKILL.md` | 2,559（未改） |
| `test-data-generator/knowledge/input-contract.md` | 3,314 → 3,285 |
| `test-data-generator/knowledge/generation-validation.md` | 2,522 → 2,505 |
| `test-data-generator/knowledge/extensions.md` | 1,634 → 891（设计参考移出） |
| `test-data-generator/knowledge/design-references.md` | 新建（按需）：第三方方案来源与取舍 |

### 做法

- frontend 删除与「诚实推进基线」重复的交付清单段落，压缩索引字段、运行核实与交接说明；模板去掉重复路径说明。
- test-data 把与运行无关的「设计参考」整体移到按需文件；压缩输入协议、格式说明和扩展边界中的重复句。
- 不改变命令行参数、Schema、安全约束与校验状态语义。

### 校验

- frontend default 5,994 ≤6,000；entry 4,489 ≤5,500。
- test-data default 8,992 ≤9,000；entry 2,559 ≤5,500。

---

## 5-5 performance 瘦身

### 改动

| 文件 | 变化 |
|---|---:|
| `SKILL.md` | 4,170 → 3,724（删除重复资源索引） |
| `knowledge/metrics-framework.md` | 4,485 → 3,342（合并重复口径、反例压缩） |
| `knowledge/load-models.md` | 2,709 → 2,533（反例表改条目） |
| `knowledge/use-method.md` | 2,966 → 2,373（命令与阈值表合并） |
| `knowledge/bottleneck-patterns.md` | 4,396 → 3,242（模式表保留，定位步骤压缩） |

### 做法

- SKILL 删除与阶段契约重复的资源索引表，其余入口契约不动。
- metrics 保留四项指标、阈值表和 Little's Law，删除重复的「仅示例」说明与部分工具细节。
- use-method 把采集命令表和阈值表合并为一张；反例改为条目。
- bottleneck-patterns 六类模式保留现象/指标/根因/优化/转交列，定位步骤压为单段；传导链保留。
- load-models 反例表改为条目并去重。

### 校验

- 预算、知识引用、链接检查通过。
- default 15,491 ≤15,500；entry 3,724 ≤5,500。

---

## 5-4 bug-analyzer 瘦身

### 改动

| 文件 | 变化 |
|---|---:|
| `SKILL.md` | 6,940 → 5,487 |
| `knowledge/root-cause-frameworks.md` | 1,809 → 1,384（删除与 defensive 重复的反推节） |
| `knowledge/bug-patterns-index.md` | 1,041 → 598 |
| `knowledge/report-template.md` | 5,827 → 2,550（示例移出） |
| `knowledge/report-examples.md` | 新建（按需）：两类完整报告示例 |
| `knowledge/defensive-test-points.md` | 5,483 → 2,371（去掉重复示例表，保留 5 类检查清单） |

### 做法

- SKILL 删除重复知识索引与步骤间依赖段；四张失败模式表逐行压缩；步骤 2/3 自检与能力约束合并。
- report-template 只留字段定义、填写规范、骨架和转交规则；两个完整示例移到 `report-examples.md`（不在默认路径）。
- defensive-test-points 保留反推流程、优先级、5 类检查清单和转交规则，删除与清单重复的示例表与完整示例。
- bug-patterns-index 只留共享来源、降级策略和内容速览。

### 校验

- 预算、知识引用、链接检查通过。
- default 12,390 ≤16,000；entry 5,487 ≤5,500。

---

## 5-3 test-strategy 瘦身

### 改动

| 文件 | 变化 |
|---|---:|
| `SKILL.md` | 6,200 → 4,613 |
| `knowledge/risk-matrix-framework.md` | 2,692 → 2,386 |
| `knowledge/test-pyramid.md` | 2,365 → 1,905 |
| `knowledge/entry-exit-criteria.md` | 1,828 → 1,748 |
| `knowledge/strategy-templates.md` | 4,680 → 4,327 |

### 做法

- SKILL 删除与阶段表重复的「知识库与参考索引」和边界表转交段；失败模式逐行压缩，保留全部触发条件与兜底结论。
- risk-matrix 合并重复的执行规则，反例表去掉「问题」列。
- test-pyramid 删除与职责表重复的边界判定清单，工具选择与自检压缩为单行。
- strategy-templates 的准入准出 checklist 改为引用 entry-exit 权威源，覆盖报告规则与反例压缩。

### 校验

- 5 个仓库结构脚本通过；`check-project-inventory` 已刷新。
- `scripts/tests/test_repository_tools.py` 36 passed（含策略反比例硬约束断言）。
- default 14,979 ≤15,000；entry 4,613 ≤5,500。

---

## 5-2 change-impact 瘦身

### 改动

| 文件 | 变化 |
|---|---:|
| `SKILL.md` | 6,151 → 4,920 |
| `knowledge/diff-modes.md` | 6,168 → 4,425 |
| `knowledge/anti-patterns.md` | 6,005 → 3,311 |
| `knowledge/cross-impact-analysis.md` | 9,538 → 8,774（合并 cross-analysis-guide 两轮分析） |
| `knowledge/cross-analysis-guide.md` | 1,343 → 删除（并入 cross-impact-analysis 第 5 节） |
| `knowledge/report-template.md` | 9,624 → 5,554 |
| `knowledge/report-example.md` | 新建（按需）：完整 Mode B 报告示例 |

### 做法

- SKILL 只留定位、四阶段门禁、知识索引、证据边界与 4 条硬禁令；反模式表与失败模式全部指向 anti-patterns。
- diff-modes 删除与表格重复的决策树，7 种模式示例压缩为一张表；保留 `git show --root` 与 6 条 diff 命令原文供安装文档测试校验。
- cross-analysis-guide 的匹配优先级、影响程度表、覆盖/执行状态与缺口风险表并入 cross-impact 第 5 节。
- report-template 只留工作表、P0-P2、场景模板与输出；完整 Mode B 示例移到 `report-example.md`（不在默认路径）。
- anti-patterns 删除与速查表重复的「详解」章节，保留核心/扩展表、触发时机、自检与失败模式。

### 校验

- 6 个仓库脚本通过；`check-project-inventory` 已刷新。
- `scripts/tests/test_installation_docs.py` 9 passed（diff 模式命令契约未破坏）。
- default 26,984 ≤31,000；entry 4,920 ≤5,500。

---

## 5-1 state-machine 瘦身

### 改动

| 文件 | 变化 |
|---|---:|
| `SKILL.md` | 7,081 → 5,498 |
| `state-machine-core.md` | 7,071 → 5,495 |
| `knowledge/scenario-types.md` | 11,657 → 3,719 |
| `knowledge/coverage-contract.md` | 新建（按需）：覆盖报告/失败阶段/分层覆盖契约 |
| `knowledge/scenario-examples.md` | 新建（按需）：可校验状态机模型 + 10 条场景完整 YAML（MCP 集成测试解析） |
| `knowledge/completeness-check.md` / `anti-patterns.md` / `state-modeling.md` | 未改（默认预算已达成） |

### 做法

- SKILL 只留定位、五阶段、模式、读取矩阵、数据契约、3 条硬禁令；反模式表移入 anti-patterns。
- core 删除 9 项检查表、10 类场景表、重复失败模式表，改为判定要点 + 指针；转交段压缩。
- scenario-types 压缩 10 类示例为规则 + 单行示例；完整可校验 YAML 移到 `scenario-examples.md`（不在默认路径），并同步 MCP 集成测试读取路径。
- 覆盖/失败语义移到 `coverage-contract.md`（不在默认路径）。

### 校验

- 6 个仓库脚本通过；`check-project-inventory` 已刷新。
- default 33,242 ≤33,300；entry 5,498 ≤5,500。
- state-machine MCP 114 passed（含迁移后的示例校验）。

---

## 停止点 4：阶段 4 匹配子集闭环（partial）

### 实测

| 项 | 数值 |
|---|---:|
| base 输出 | 70/70 |
| inv1 输出 | 70/70 |
| dom1 有效输出 | 28/70 |
| 三变体 complete-case | 25 |
| judge | Mimo，盲评，单次 |
| base 检查通过率 | 88/128 = 68.75% |
| inv1 检查通过率 | 86/128 = 67.19% |
| dom1 检查通过率 | 86/128 = 67.19% |

### 4-6 采纳结论

| 项 | 决策 | 依据 |
|---|---|---|
| INV1 | **不采纳** | 总通过率 -1.56pp；生成类 -10.42pp；未达 +5pp |
| DOM1 | **不采纳（未评估）** | 匹配子集无 requirement-review case |
| AGG1 | 不构建 | 两个单路都未通过/未评估 |
| base | **保留** | 不低于两个候选 |

### 限制

- 单次运行，无 3 次重复与 A/A；`status=partial`。
- 免费模型（LongCat/Mimo），稳定性低于生产模型；dom1 缺失 42/70，缺失非随机。
- 匹配子集只覆盖 generation/review；DOM1 目标类别未覆盖。
- trigger 评测未完成（48 次调用排队超时）。
- 详细报告：`docs/skill-evaluation/phase4/phase4-probe-report.md`。

### 需要用户选择

| 选项 | 内容 | 推荐 |
|---|---|---|
| A | 用付费 runner 补全 dom1 与 requirement-review 子集，重跑 4-4 | 需要 API key 与更长窗口 |
| B | 接受 `partial` 闭环，进入阶段 5 瘦身第二批 | **推荐**：阶段 4 结论已足以阻止无证据采纳 |
| C | 停止优化，先做发布前的人工 review | 可选：若模型质量是硬门槛 |

---

## 4-1 确定性代理失败聚类

对象：42 份历史 `with_skill` 产物（旧版本 skill）。方法：`validate_cases.py --json` 逐份校验。

| 指标 | 数值 |
|---|---:|
| 可解析为用例 | 20 / 42 |
| 用例 | 153 |
| ERROR | 10 |
| WARN | 26 |

聚类：格式/结构占绝对多数（标题分隔符 13、编排声明 7、非功能置末尾 3、必填/前缀/ID 各 1）；可读性集中在「任意」「正常」（7）；覆盖类因无需求基线不可评估；未发现新的规则冲突类证据。

## 4-2 INV1 提案（未应用）

- 目标：`TITLE_SEPARATOR`、`ARRANGE_DECLARE`、`NONFUNC_TAIL`。
- 改动范围：仅 `core.md` 阶段 3 自检与阶段 4 闸门；不触碰 knowledge、脚本、MCP。
- 核心内容：标题强制 ` - ` 分隔；用例集开头声明编排策略；两类 warning 按阻断项处理。
- 未应用原因：无 Probe 证据，不能证明模型收益或护栏不退化。

## 4-3 DOM1 提案（未应用）

- 目标：需求评审召回与级别判例。
- 改动范围：仅 `knowledge/requirement-review.md` 领域知识；不触碰工作流。
- 核心内容：6 类高频缺陷模式（模糊/数值矛盾/状态/权限/异常/验收口径）+ P0–P3 判例。
- 未应用原因：同上；且模式表可能增加误报，需要原文回查与 Probe 验证。

## 4-4 / 4-5 Probe 与 Compose

- **4-4**：在 dom1 有效输出形成的匹配子集上完成。base/inv1 各 70 个输出，dom1 28 个有效输出；三变体 complete-case 25 个（128 checks）。
- **4-5 Compose**：未执行。INV1 与 DOM1 都未达到采纳门槛，没有可合并的候选。
- 未完成：dom1 其余 42 个、requirement-review 子集、trigger 评测、3 次重复与 A/A。

## 4-6 采纳与经验

- 采纳：不采纳 INV1/DOM1/agg1；保留 base。
- 经验库：`docs/skill-evaluation/experience-library.md`，E-001～E-005，均标注证据强度与边界。

---

## 停止点 3：阶段 3 完成，待确认

### 交付物

| 项 | 文件/结果 |
|---|---|
| 需求评审知识 | `knowledge/requirement-review.md`（10 维度、P0–P3、问题 schema、报告模板、输出规则） |
| 模式接入 | `SKILL.md` 模式选择/索引/读取矩阵；`core.md` 阶段 1 消费问题清单、阶段 2 校验闸门；`README.md` 同步 |
| bundle 路由 | 单意图「需求评审/PRD 评审」→ test-case-engineer；新增链 10（需求评审 → 用例生成） |
| 需求评审校验器 | `scripts/validate_requirement_review.py`：结构、9 列必填、枚举、原文回查、统计一致、10 维度覆盖 |
| 测试点校验器 | `scripts/validate_points.py`：结构、ID/维度/优先级、单点单目标、重复、追溯、优先级分布、裁剪、预算、需求覆盖 |
| gold 样例 | `docs/skill-evaluation/gold/`：5 PRD + 5 评审报告 + 5 测试点清单 |
| 干跑报告 | `reports/2026-11-17-phase3-dry-run.md` |
| 评测套件 | v7.2：70 task / 16 trigger / 354 checks，SHA `5c6bd2ef` |

### 预算影响

| 路径 | 阶段 2 后 | 阶段 3 后 | 目标 |
|---|---:|---:|---:|
| test-case-engineer / entry | 4,903 | 5,400 | ≤5,500 |
| test-case-engineer / default | 36,394 | 36,990 | ≤44,800 |
| test-case-engineer / review | 19,566 | 20,063 | ≤25,200 |
| test-case-engineer / requirement-review | — | 9,560 | ≤9,600 |
| testing-bundle / entry | 5,039 | 5,253 | ≤5,500 |
| testing-bundle / route | 10,529 | 11,119 | ≤13,750 |

### 校验结果

| 项 | 结果 |
|---|---|
| 六个仓库脚本 | 全绿 |
| 仓库 pytest + 新校验器测试 | 46 passed |
| review-checker MCP | 110 passed |
| state-machine MCP | 114 passed |
| v7.2 套件输入校验 | 70 task / 16 trigger 通过 |
| gold 需求评审 | 5/5 通过；25/25 种子缺陷；0 误报；证据完整率 100% |
| gold 测试点 | 5/5 通过；34 测试点 / 43 用例 |

### 未评估 / 限制

- gold 干跑是「按种子缺陷构造的报告」，召回 100% 与误报 0 是构造结果，**不是模型召回率/误报率**。
- 模型侧需求评审、测试点生成、独立 judge、A/A 一致率仍未执行；`status` 仍为 `blocked`。
- 阶段 3 验收中的「误报 ≤25%」目前只有 gold 样例证据，不能替代模型评测。

### 需要用户选择

| 选项 | 内容 | 推荐 |
|---|---|---|
| A | 进入阶段 4：harness² 第一轮（INV / DOM / Compose） | **推荐**：阶段 3 工具与样例已就绪 |
| B | 先补模型行为基线，再进阶段 4 | 稳妥但需外部 runner/judge |
| C | 先调整需求评审模板/校验器，再进阶段 4 | 适合对字段或阈值有额外要求时 |

---

## 3-1 需求评审知识

新增 `knowledge/requirement-review.md`（2,961 字符，≤5k）：

- 10 维度检查表，每维带判定问句。
- P0–P3 严重级别与处置。
- 9 字段问题 schema：ID / 位置 / 原文 / 类型 / 级别 / 影响 / 问题 / 待确认 / 状态。
- 报告模板：问题清单、维度覆盖、未评估项、原文回查。
- 硬约束：原文逐字回查、一条一个问题、不虚构值、confirmed/candidate 分开、统计与表一致。

## 3-2 需求评审模式接入

- `SKILL.md`：模式选择新增「需求评审」；知识索引新增 requirement-review；读取矩阵新增一行；模式数改为 6 种。
- `core.md`：阶段 1 新增「需求评审衔接」；阶段 2 新增 `validate_points.py` 机器校验闸门；模式切换新增需求评审；评审模式段落补需求评审指针。
- `README.md`：模式表、快速开始、知识树、快速参考同步。
- `context-budget.json`：新增 `requirement-review` 模式（SKILL + requirement-review + project-knowledge），预算 9,700 / 目标 9,600。

## 3-3 bundle 路由与链 10

- 单意图表新增：需求评审、PRD 评审、评审需求文档、需求文档检查、需求问题清单 → test-case-engineer（需求评审模式）。
- 边界：撰写/润色 PRD 不进入需求评审。
- 新增链 10：需求评审 → 用例生成；链冲突优先级把 6/7/10 归为「评审先于生成」。
- `test-prompts.json` 新增 3 条（需求评审、非需求评审、链 10）。

## 3-4 需求评审校验器

`validate_requirement_review.py`（279 行）：

- 解析 `## 问题清单` 与 `## 维度覆盖` 两张 Markdown 表。
- 9 列必填、ID/类型/级别/状态枚举、位置格式提示。
- `--prd` 原文逐字回查，矛盾引用按 ` / ` 分段回查。
- 统计与表一致、维度合计 = confirmed、未评估维度必须有原因。
- 输出 JSON/文本；error 退出 1，`--strict` 时 warning 也失败。

## 3-5 测试点校验器

`validate_points.py`（263 行）：

- 解析 `## 测试点清单` 9 列表。
- ID 格式/唯一、7 维度、P0–P3、单点单目标提示、重复、需求追溯。
- 全 P0 / P0 占比 >80% 提示；用例数 0 必须有裁剪说明；预算超限提示。
- `--requirements` 支持种子 case 或种子集 + `--case-id`，检查需求条目覆盖与范围外候选。

## 3-6 5 个 PRD 干跑

- gold 报告 5 份、PRD 5 份、测试点清单 5 份。
- 需求评审：25 个种子缺陷全部覆盖（构造），0 误报（构造），证据完整率 100%，校验器 5/5 通过。
- 测试点：34 个测试点、43 条估算用例，校验器 5/5 通过。
- 结论仅证明模板与校验器可用；模型侧指标未执行。

---

## 停止点 2：阶段 2 完成，待确认

### 预算对比（字符）

| 路径 | 阶段 1 基线 | 阶段 2 后 | 目标 | 结果 |
|---|---:|---:|---:|---|
| test-case-engineer / entry | 7,391 | 4,903 | ≤5,500 | 通过 |
| test-case-engineer / default | 64,028 | 36,394 | ≤44,800 | 通过（-43.2%） |
| test-case-engineer / review | 33,545 | 19,566 | ≤25,200 | 通过（-41.7%） |
| testing-bundle / entry | 7,486 | 5,039 | ≤5,500 | 通过 |
| testing-bundle / route | 17,190 | 10,529 | ≤13,750 | 通过（-38.7%） |

> 其余 5 个 skill 的 `--target` 仍超限，属阶段 5 范围，不在本轮验收。
>
> 按需文件不计入首轮路径：`review-reference.md`（4,614，R3/增量时读）、`runtime-error-patterns.md`（2,367，出现 NPE/500/超时历史时读）、`writing-examples.md`、`readability.md` 等仍按读取矩阵延迟加载。

### 文件级变化

| 文件 | 变化 |
|---|---:|
| writing-rules.md | 13,081 → 7,281 |
| readability.md | 3,832 → 1,704 |
| test-standards.md | 4,435 → 1,924 |
| anti-patterns.md | 4,236 → 2,011 |
| prompt-strategy.md | 4,267 → 997（移出默认路径） |
| test-levels.md | 2,907 → 删除（并入 case-arrangement） |
| case-arrangement.md | 2,605 → 2,695（吸收分层） |
| bug-patterns.md | 5,412 → 3,229 |
| runtime-error-patterns.md | 新建 2,367（按需） |
| test-case-engineer-core.md | 13,810 → 9,500 |
| SKILL.md | 7,391 → 4,903 |
| review-mode.md | 13,563 → 6,711 |
| review-reference.md | 新建 4,614（按需模板） |
| project-knowledge.md | 2,149 → 1,199 |
| testing-bundle/SKILL.md | 7,486 → 5,039（120 行） |
| mixed-intent-chains.md | 5,869 → 3,015 |
| routing-fallbacks.md | 3,835 → 2,475 |

### 校验结果

| 项 | 结果 |
|---|---|
| 六个仓库脚本 | 全绿（预算、结构一致性、知识引用、链接、清单、版本同步） |
| 仓库 pytest | 36 passed |
| review-checker MCP | 110 passed（已安装 editable 依赖） |
| state-machine MCP | 114 passed |
| v7.1 套件输入校验 | 70 task / 12 trigger 通过 |
| 固定 10 份历史产物 | 85 条用例，0 error，7 WARN |
| testing 目录 Markdown 总量 | 401,209 → 387,927（阶段 5/6 继续降至 ≤320k） |

### 未评估 / 阻塞

- 模型行为质量：无 runner、无不同厂商独立 judge、无 API key，`status` 仍为 `blocked`。
- 阶段 2 验收中的「v7 主指标回退 ≤2pp」无法执行；当前只有确定性校验与历史产物回归，**不得**据此声称质量未回退或已提升。
- v7.1 套件与种子集未运行模型侧评测。

### 需要用户选择

| 选项 | 内容 | 推荐 |
|---|---|---|
| A | 进入阶段 3：需求评审模式 + 测试点校验器 + 对应评测套件 | **推荐**：阶段 2 预算已达成，确定性门禁全绿 |
| B | 先补模型行为基线，再进阶段 3 | 稳妥但需外部 runner/judge |
| C | 继续压缩其余 skill（提前做阶段 5） | 可选，但会跳过阶段 3 的质量闭环 |

---

## 2-9 testing-bundle 压缩

### 改动

| 文件 | 变化 |
|---|---|
| `testing-bundle/SKILL.md` | 7,486 → 5,039；158 → 120 行 |
| `knowledge/mixed-intent-chains.md` | 5,869 → 3,015 |
| `knowledge/routing-fallbacks.md` | 3,835 → 2,475 |

### 保留与压缩

- SKILL 只留路由顺序、三要素解析、单意图表、9 条链索引、子 skill 加载与入口约束；删除示例列表，保留按需指针。
- 9 条链由 ASCII 步骤图改为「一行路径 + 触发/边界」；链冲突裁定、链 3/4 判定、数据语义、前端边界全部保留。
- 失败模式表与反例删除「为什么不要做」列；上下文 schema 与安装反例保留。
- `mixed-intent-chains.md` 新增安全提示，满足 shell 执行点的安全约束检查。

### 校验结果

- 六个仓库脚本通过；pytest 36 passed；两个 MCP 测试 110 + 114 passed。
- bundle entry 5,039（≤5,500，120 行）；route 10,529（≤13,750）。

---

## 2-8 project-knowledge 压缩

### 改动

| 文件 | 变化 |
|---|---|
| `knowledge/project-knowledge.md` | 2,149 → 1,199 |

### 保留与压缩

- 保留：来源优先级四档、冲突/过期资料标注、模板不覆盖项目事实、七类扫描目录、Office/PDF 自动转换、MarkItDown 主方案与 `convert_docs.py` 降级、无 venv/终端时的局限说明、用户只给文档路径时的处理。
- 压缩：blockquote 说明合并为两行；目录表与转换步骤改为紧凑列表；安全约束与首次自举保留为指针。

### 校验结果

- 六个仓库脚本通过；`test-case-engineer / default` 36,521 → 36,394。

---

## 2-7 review-mode 拆分与压缩

### 改动

| 文件 | 动作 |
|---|---|
| `knowledge/review-mode.md` | 13,563 → 6,711；保留触发条件、R1–R3、10 维度、可读性子项、评审主体、MCP 三模式/工具/阈值/调用约定、修订闭环、失败模式、反例、子模式边界、文件化规则 |
| `knowledge/review-reference.md` | 新建，4,614；承载意见表/建议清单/度量报告模板、修订上下文 schema、修订报告模板、报告文件结构、增量评审子模式 |
| `README.md` | 文件树新增 review-reference.md |

### 说明

- 模板与增量评审移出首轮读取，R3 或增量评审时再读；R2 判定规则仍全部在 review-mode.md。
- 评审反例删除「为什么不要做」列，规则与替代做法保留。
- pytest 中有一条依赖 `review-mode.md` 原文短语的断言（`不重跑与当前问题无关的完整四阶段`），已按原文保留该短语，36 passed。

### 校验结果

- 六个仓库脚本通过；pytest 36 passed。
- review-mode 6,711（≤9,000）；评审路径 26,418 → 19,566（≤25,200）。

---

## 2-6 SKILL.md 压缩

### 改动

| 项 | 变化 |
|---|---|
| `SKILL.md` | 7,307 → 4,903 字符；159 → 109 行 |

### 保留与压缩

- 保留：定位与阅读策略、bundle 关系、bug-analyzer / state-machine 协同边界、五种模式选择与复杂度判定、四阶段入口、输出块约束、知识库索引全部 20 个资源、模式读取矩阵、评审隔离、产品知识加载、连续交付、能力约束。
- 压缩：协同与边界改为两条；模式选择改为短句列表；知识索引描述改为一句话用途；模式读取矩阵改为阶段级引用；产品知识库与快速上手合并压缩。

### 校验结果

- 六个仓库脚本通过；pytest 36 passed；模式一致性检查通过。
- 入口 7,307 → 4,903（≤5,500）；default 39,755 → 37,344；review 28,822 → 26,418。

---

## 2-5 core 压缩

### 改动

| 文件 | 变化 |
|---|---|
| `test-case-engineer-core.md` | 13,810 → 9,500 字符；490 → 309 行 |

### 保留与压缩

- 保留：四阶段流转、范围闸门三问、7 维度扫描、测试点设计四原则、失败模式与 Fallback、脚本校验闸门、J 类评审、五种模式切换。
- 压缩：需求理解模板改为紧凑字段清单；业务系统识别表与失败模式表缩短；阶段 3 自检改为判定要点；阶段 4 J 类自检按类别合并。
- 删除与 knowledge 重复的细表（字段、句式、模糊词、编排），改为指针。

### 校验结果

- 六个仓库脚本通过；pytest 36 passed；`check-skill-consistency` 的模式一致性检查通过。
- `test-case-engineer / default` 44,058 → 39,755，低于 44,800 目标；`review` 28,822 不变。

---

## 2-4 bug-patterns 压缩与运行时清单按需化

### 改动

| 文件 | 动作 |
|---|---|
| `knowledge/bug-patterns.md` | 5,412 → 3,229；保留通用缺陷模式、映射表、领域模式、安全清单 |
| `knowledge/runtime-error-patterns.md` | 新建，2,367；原 NPE / 500 / 超时的 P1–P5 根因、排查路径、验证方法、防御性测试点原样保留 |
| `bug-analyzer/SKILL.md` | NPE / 500 / 超时排查改指新文件 |
| `bug-analyzer/knowledge/bug-patterns-index.md` | 同步引用新文件 |
| `README.md` | 文件树新增 runtime-error-patterns.md |

### 说明

- 运行时清单服务于 bug-analyzer 的排查路径，不是默认生成必经内容；按需化而非删除。
- `bug-patterns.md` 的映射表、高频模式、领域模式、安全清单仍留在默认路径。

### 校验结果

- 六个仓库脚本通过；pytest 36 passed。
- `test-case-engineer / default` 46,241 → 44,058，已低于 44,800 目标。

---

## 2-3 用例组织单一文件

### 改动

| 文件 | 动作 |
|---|---|
| `knowledge/case-arrangement.md` | 重写为「用例组织：分层、输出类型与编排」，吸收 test-levels 的五层定义、默认重心、禁止混层、L1/L2-A/L2-B/L3 占比、默认输出类型与 strategy 映射 |
| `knowledge/test-levels.md` | 删除（内容已并入） |
| `SKILL.md` | 知识索引与读取矩阵合并为单一 case-arrangement 入口；删除重复索引行 |
| `README.md` | 文件树删除 test-levels，更新 case-arrangement 说明 |
| `scripts/context-budget.json` | default 文件清单删除 test-levels |

### 去重口径

- 分层表、默认重心、禁止混层、分层选择、编排组占比、动态调整、strategy 三层映射全部保留。
- 「默认输出功能测试用例」的触发条件与 `test-standards.md`「用例类型」重复，改为指针。
- 编排策略一/二、模块划分依据、通用排序、用例集预算、输出前去重、与阶段 2 裁剪的关系全部保留。

### 校验结果

- 六个仓库脚本通过；pytest 36 passed；`README.md` 项目清单已用 `--write` 刷新。
- `test-case-engineer / default` 49,139 → 46,241；`review` 28,903 → 28,822。

---

## 2-2 prompt-strategy 移出默认路径

### 改动

| 文件 | 动作 |
|---|---|
| `knowledge/prompt-strategy.md` | 4,267 → 997；只保留「语义事实抽取」按需段与生成策略一行 |
| `test-case-engineer-core.md` | 阶段 3 删除「读取 prompt-strategy 模板」，改为三轮生成流程 |
| `SKILL.md` | prompt-strategy 标为按需；默认读取矩阵移除该文件 |
| `scripts/context-budget.json` | default 文件清单移除 prompt-strategy |

### 说明

- 原「结构化提示词模板」的 11 条要求分别落在 writing-rules、scope-discipline、case-arrangement，属于 D1 语义重复；模板本体删除，不删规则。
- 三轮生成策略保留在 core.md 阶段 3，仍处于默认路径。
- 语义事实抽取的 JSON 结构、归一化规则、硬约束完整保留。

### 校验结果

- 六个仓库脚本通过；pytest 36 passed；`test-case-engineer / default` 53,514 → 49,139。

---

## 2-1 写作契约单一权威源

### 改动

| 文件 | 角色 | 字符变化 |
|---|---|---:|
| `knowledge/writing-rules.md` | 写作规则唯一权威源：格式 / 字段 / 标题·步骤·预期 / 句式阈值 / 模糊词 / 术语 / Tag / 拆分合并 / 证据边界 | 13,081 → 7,281 |
| `knowledge/readability.md` | 降为按需细则：句式改写对照、动词首选表、术语/环境写法、说人话、认知负荷 | 3,832 → 1,704 |
| `knowledge/test-standards.md` | 只保留优先级、类型、测试策略、生命周期；字段与模糊词改为指针 | 4,435 → 1,924 |
| `knowledge/anti-patterns.md` | 压成黑名单表（工作流/输出、可读性、范围/测试点/拆分合并） | 4,236 → 2,011 |
| `test-case-engineer-core.md` | 阶段 3 自检的模糊词引用改指 writing-rules | 13,893 → 13,898 |
| `SKILL.md` | test-standards 索引去掉「模糊词权威源」，改为 writing-rules | 7,391 → 7,414 |

### 去重口径

- 字段、标题/步骤/预期铁律、模糊词词表、术语与 Tag 规则只在 `writing-rules.md` 维护；`test-standards.md` 不再保留副本。
- 可读性阈值（20/40/100 字、7 步、300 字、字段 ≤5）由 `writing-rules.md` 持有，`readability.md` 只保留对照表与示例。
- 反例黑名单删除「为什么不要做」列；合并语义重复项（多验证目标、泛化预期、测试点三连、阈值正反各写一条），规则本身保留。
- 未删除行为规则；所有合并项都能映射回 writing-rules 或 core 的对应条款。

### 校验结果

```bash
python3 scripts/check-context-budget.py          # 全部 ok
python3 scripts/check-skill-consistency.py       # 通过
python3 scripts/check-knowledge-count.py         # 通过
python3 scripts/check-md-links.py                # 通过
python3 scripts/check-project-inventory.py       # 通过
python3 scripts/check-version-sync.py            # 通过
python3 -m pytest scripts/tests/test_repository_tools.py -q  # 36 passed
python3 scripts/skill-evals.py                   # 输入校验通过
```

固定 10 份历史产物（`task-1/6/14/23/25/27/28/33/34/35-with_skill.txt`）`validate_cases.py` 全部 0 error，共 85 条用例、7 WARN。

### 预算影响

| 路径 | 阶段 1 基线 | 2-1 后 | 目标 |
|---|---:|---:|---:|
| test-case-engineer / default | 64,028 | 53,514 | 44,800 |
| test-case-engineer / review | 33,545 | 28,929 | 25,200 |
| 四文件合计 | 25,584 | 12,920 | ≤13,000 |

### 下一步（2-2）

`knowledge/prompt-strategy.md` 移出默认路径：SKILL.md 保留 5 行指针，仅保留「语义事实抽取」按需段；同步 `context-budget.json` 的 default 文件清单。

---

## 1-1 / 1-2 上下文度量与预算门禁

### 改动

| 文件 | 作用 |
|---|---|
| `scripts/skill_context.py` | 共享度量库：加载配置、按 skill/mode 统计字符/行数/字节、可选 tiktoken 计数、全目录 Markdown 统计 |
| `scripts/skill-context-report.py` | 输出按 skill/模式的人读表格或 `--json` |
| `scripts/context-budget.json` | 9 个 skill 的 entry + mode 文件清单、当前门槛（budget）、瘦身目标（target） |
| `scripts/check-context-budget.py` | 预算门禁；默认查 budget，`--target` 查瘦身目标 |
| `scripts/tests/test_repository_tools.py` | 新增 2 个测试，覆盖度量与超限失败 |

### 实测基线（2026-11-17）

| Skill / 模式 | 字符 | 行数 | Token(估) |
|---|---:|---:|---:|
| test-case-engineer / default | 64,028 | 2,091 | 41,308 |
| test-case-engineer / review | 33,545 | 1,138 | 21,642 |
| state-machine-test-engineer / default | 44,340 | 1,716 | 28,606 |
| change-impact-analyzer / default | 38,829 | 1,266 | 25,051 |
| testing-bundle / route | 17,190 | 440 | 11,090 |
| test-strategy-engineer / default | 17,765 | 562 | 11,461 |
| bug-analyzer / default | 21,053 | 854 | 13,583 |
| performance-test-engineer / default | 18,726 | 604 | 12,081 |
| frontend-test-preparation / default | 6,378 | 151 | 4,115 |
| test-data-generator / default | 10,029 | 193 | 6,470 |

- 默认路径合计（含 test-case 生成 + 评审）：271,883 字符
- 目录内全部 Markdown：401,209 字符
- Token 口径：tiktoken 未安装，当前为 `characters / 1.55` 回退估算；报告会标注实际口径
- 计划文件 §1.1 已按本次精确测量修正 bug / performance / frontend / data 四个基线

### 验证命令与结果

```bash
python3 scripts/skill-context-report.py          # 输出表格，正常
python3 scripts/check-context-budget.py          # 全部 ok，exit 0
python3 -m pytest scripts/tests/test_repository_tools.py -q  # 33 passed
python3 scripts/check-skill-consistency.py       # 通过
python3 scripts/check-knowledge-count.py         # 通过
python3 scripts/check-md-links.py                # 通过
python3 scripts/check-project-inventory.py       # 通过
python3 scripts/check-version-sync.py            # 通过
python3 scripts/skill-evals.py                   # 输入校验通过
```

### 已知边界

- `tiktoken` 未安装；如后续需要精确 token，安装后脚本自动切换为 `o200k_base`，无需改代码。
- `context-budget.json` 的 `budget` 是「当前基线 + 约 2%」，只用于阶段 1 不阻断；瘦身完成后应改为 `target` 或更紧的值。
- `frontend-test-preparation` 与 `test-data-generator` 当前已低于 5,500 入口目标，entry 行的 `--target` 不会失败。

### 下一步（1-3）

按计划从 4 个首批 skill 抽取 `必须/禁止/不得/应/严禁/强制` 规范语句，生成规则清单并标注 D1–D5 处置类别：
- D1 纯重复：可删并留指针
- D2 移位：可移出默认路径，需链接
- D3 过时/冲突：按优先级修复，不直接删
- D4 低价值：需评测证据才删
- D5 行为规则：无配对评测不得删

---

## 1-3 规范语句清单

### 改动

| 文件 | 作用 |
|---|---|
| `scripts/extract-rule-inventory.py` | 从 4 个首批 skill 抽取规范语句，按 D1–D5 启发式分类，生成 Markdown + JSON |
| `docs/skill-evaluation/rule-inventory/README.md` | 汇总索引、D1–D5 处置规则、已知冲突观察 |
| `docs/skill-evaluation/rule-inventory/<skill>.md` | 每个 skill 的逐条清单（ID / 位置 / 语句 / 类别 / 依据 / 处置 / 复核） |
| `docs/skill-evaluation/rule-inventory/rule-inventory.json` | 机器可读清单，供瘦身批次勾选与后续脚本使用 |
| `scripts/tests/test_repository_tools.py` | 新增 1 个测试，验证只抽取实质规范句、跳过纯标题 |

### 实测结果

| Skill | 条数 | D1 重复 | D2 按需化 | D3 冲突 | D4 参考/按需 | D5 行为 |
|---|---:|---:|---:|---:|---:|---:|
| test-case-engineer | 223 | 0 | 17 | 0 | 39 | 167 |
| state-machine-test-engineer | 155 | 52 | 0 | 0 | 25 | 78 |
| change-impact-analyzer | 58 | 0 | 7 | 0 | 2 | 49 |
| testing-bundle | 16 | 0 | 0 | 0 | 1 | 15 |

- D1 = 0 不代表无重复，只代表没有逐字重复的规范句；`writing-rules` / `readability` / `test-standards` / `anti-patterns` 的语义重复需在阶段 2 按主题合并。
- state-machine 的 D1 主要来自 `products/order-refund.md` 与 `industry-templates/order-refund.md` 的重复规范句，阶段 5 处理。
- D3 = 0 是因为已知冲突主要在 eval checks 与 skill 规则之间，不在 skill 内部；README 已列出 4 项已知冲突观察，供 1-8 核对。

### 验证

```bash
python3 scripts/extract-rule-inventory.py     # 生成 4 份报告 + JSON + README
python3 -m pytest scripts/tests/test_repository_tools.py -q  # 34 passed
python3 scripts/check-md-links.py             # 通过
```

### 下一步（1-4）

评测套件 v7：
1. 读取 `test-prompts.json` + v6 套件，统一 schema（`task_cases` + `trigger_evals`，兼容 `skill-evals.py`）。
2. 给所有 task 补 `category`（generation / review / requirement-review / test-points / coverage / strategy）。
3. 把存在性断言改为结果型断言；新增测试点 10 case、需求评审 12 case、高区分度用例评审 6 case。
4. 冻结 v7 SHA，记录 case/check 数。

---

## 1-4 评测套件 v7

### 产出

| 文件 | 内容 |
|---|---|
| `docs/skill-evaluation/2026-11-17-quality-suite-v7.1.json` | 现行：70 task / 12 trigger / 354 checks；SHA `dd2f1b49` |
| `docs/skill-evaluation/2026-11-17-quality-suite-v7.json` | 历史：SHA `ae880180`，保留复现 1-8 审计 |
| `docs/skill-evaluation/README.md` | v7.1 登记为现行套件；v7/v6 移入历史冻结套件 |

### 结构

- v7 使用 `{skill, version, frozen_at, notes, task_cases, trigger_evals}`；`scripts/skill-evals.py` 已支持 `task_cases` + `checks` 字段。
- 70 task 的 category：
  - `generation` 21
  - `review` 21
  - `requirement-review` 12
  - `test-points` 10
  - `review-high-discrimination` 6
- 12 trigger 仍为 positive 3 / near_miss 4 / skill_conflict 3 / negative 2；trigger coverage 校验通过。

### 断言改造

- 37 处流程术语型断言（「输出包含 / 触发模式 / CHECKPOINT / R1-R3 / 10 维度」）已改写为结果型，覆盖 case `4,5,6,7,8,9,10,11,13,14,15,16,17,19,20,21,22,23,24,25,26,28,30,37`。
- 仅保留 1 处「引用 R2 判定规则」作为证据要求，不是存在性断言。
- 改写示例：`触发评审模式` → `输出以用例结构解析和问题清单为主，未进入需求生成流程`；`触发失败模式#2（无需求文档）` → `报告明确标注溯源维度未评估，未编造需求基线`。

### 验证

```bash
python3 scripts/skill-evals.py --cases-file docs/skill-evaluation/2026-11-17-quality-suite-v7.1.json
# test-case-engineer: 70 task / 12 trigger
python3 -m pytest scripts/tests/test_repository_tools.py -q
# 36 passed
```

### 已知冲突（未改断言）

3 条 check 与 skill 规则冲突，详见 [一致性报告](../../skill-evaluation/reports/2026-11-17-eval-rule-consistency.md)：
- `#13` 评级阈值未写「已确认 P0 → D」；
- `#7` / `#19` 对 120/100+ 条用例强制抽样，skill S2 在 50<N≤300 且无时间约束时走全量分批。

---

## 1-5 需求评审种子集

### 产出

`docs/skill-evaluation/2026-11-17-requirement-review-cases.json`

| 项 | 数值 |
|---|---:|
| PRD case | 12 |
| 预埋缺陷 | 61（每个 PRD 5-6 个） |
| checks | 60 |
| SHA | `aee2ed36` |

### 缺陷字段

每个 `seeded_defect` 含：`id` / `type` / `severity` / `location` / `quote` / `expected`。
覆盖类型：模糊、矛盾、缺失、不可测、权限、状态、数据、兼容性、非功能、依赖、文案冲突。

### 用途

- 主指标：P0/P1 种子缺陷召回率。
- 护栏：误报率、证据完整率（位置+原文+影响+问题）、severity 准确率。
- 确定性校验：`quote` 必须能在 PRD 原文中回查；这是比 judge 更硬的信号。

---

## 1-6 测试点种子集

### 产出

`docs/skill-evaluation/2026-11-17-test-point-cases.json`

| 项 | 数值 |
|---|---:|
| case | 10 |
| checks | 52 |
| SHA | `dc900b79` |

### 字段

每个 case 含：
- `requirement_items`：需求条目（覆盖分母）
- `expected_points`：期望测试点
- `out_of_scope`：范围外项
- `checks`：结果型断言（原子性、追溯、边界、优先级、裁剪）

### 用途

- 主指标：种子需求覆盖召回。
- 护栏：单点单目标、追溯完整性、预算、裁剪理由。
- 阶段 3 的 `validate_points.py` 将以同一 schema 做确定性校验。

---

## 1-7 干净基线

### 状态：`blocked`（模型行为未执行），确定性基线完成

产出：`docs/skill-evaluation/reports/2026-11-17-quality-baseline.md`

阻塞原因：

- 沙箱无 `opencode` / `zcode` / `codebuddy` / `claude` / `codex` runner；
- 无模型 API key；
- 无不同厂商独立 judge；
- 因此无法执行 3 次重复与 A/A 一致率，`status` 不能为 `evaluated`。

已完成：

- 6 个仓库脚本 + pytest 36 项 + 预算门禁 + v7 输入校验全绿；
- 历史 42 份 with_skill 产物确定性校验：20 份可解析、153 条用例、10 ERROR、26 WARN（旧版本产物，仅作校验器基线）；
- 规则清单与一致性扫描完成。

**不得**把本报告当作质量分数或「有 skill 更好」的结论。

---

## 1-8 断言-规则一致性

产出：`docs/skill-evaluation/reports/2026-11-17-eval-rule-consistency.md`

| 项 | 数值 |
|---|---:|
| v7 task checks | 354 |
| 流程术语断言（改写前） | 37 |
| 流程术语断言（改写后） | 1 |
| 冲突候选 | 3（#13、#7、#19） |
| 抽检一致 | 6 组 |

结论：3 条冲突都是 check 表述不完整，不是 skill 行为错误；本阶段只给建议，未改 skill、未改断言。

---

## 停止点 1：待用户决定

### 已完成

- 度量脚本、预算门禁、规则清单、v7 套件、需求评审种子集、测试点种子集、确定性基线、一致性报告。
- 6 个仓库脚本全绿；pytest 36 passed；v7 输入校验通过。

### 未完成 / 阻塞

- 模型行为基线：需要独立 runner + 不同厂商 judge + API key。
- 3 条冲突 check 的修复：按 1-8 约定未擅自修改。

### 需要用户选择

| 选项 | 内容 | 推荐 |
|---|---|---|
| A | 先修 3 条冲突 check 并冻结 v7.1，再进阶段 2 | **推荐**：成本低，避免后续评测口径漂移 |
| B | 直接进阶段 2，用预算门禁 + 确定性校验 + 历史产物回归保护 | 可选：瘦身可以先做，但质量结论必须等独立评测 |
| C | 等外部 runner/judge 补齐模型基线后再继续 | 稳妥但阻塞进度 |

### 决策结果（2026-11-17）：选 A，已完成

1. `#13`：check 改为「若存在已确认 P0，整体评级为 D；否则按 A/B/C/D 阈值判定」。
2. `#7`：check 改为「报告给出 S2 全量分批或 S3 分层抽样策略及依据；仅 S3 要求抽样清单与「抽样评审」标注」。
3. `#19`：同上，删除「>100 必抽样」的绝对表述。
4. 已冻结 **v7.1**：`docs/skill-evaluation/2026-11-17-quality-suite-v7.1.json`，SHA `dd2f1b49`，70 task / 12 trigger / 354 checks；v7 保留为历史。
5. 已更新 `docs/skill-evaluation/README.md`、基线报告、一致性报告与 v7 测试引用。

### 若选 B 的下一步

阶段 2-1：建立「写作契约」单一权威源，先做 `writing-rules` / `readability` / `test-standards` / `anti-patterns` 的规则合并；每批一个 commit，阶段 2 结束回到默认路径 ≤44.8k 的预算门禁。
