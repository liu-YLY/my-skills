# 测试用例 Skill 四目标优化交付报告（v9.11.0）

> 日期：2026-11-01
> 版本：`test-case-engineer` **v9.11.0**（由 v9.10.0 升级，minor，向后兼容）
> 分支：`feat/test-case-quality-eval`，基于 `main` @ `1557de5`；**只本地提交，未推送、未创建 PR**
> 目标：生成准确、精简、覆盖面全、人类可读性强的测试用例
> 边界：**本轮未执行模型行为评测，未产出质量分数；三份阶段报告均为 `dry_run`**
> 配套：[执行计划](../../superpowers/plans/2026-11-01-test-case-quality-plan.md)、[评测执行协议](../test-case-quality-eval-protocol.md)、[阶段 A 基线](2026-11-01-test-case-quality-baseline.md)

## 1. 交付清单

| 阶段 | commit | 内容 |
|---|---|---|
| A | 6 个（`352575d` … `6158c34`） | 修正 CHECKPOINT 漂移；新增 8 条四目标可判定用例；评测执行协议；冻结套件；阶段 A 快照 |
| B | 4 个（`b1b038e` … `8504129`） | `core.md` 瘦身 500→470；阶段 4 机器校验三模式约定；离线对照验证；阶段 B 快照 |
| C | 5 个（`d542038` … `938e96b`） | 7 维度按风险裁剪；Prompt 预算/去重/覆盖核对；三档软预算 8/15/25；阶段 C 对照报告与快照 |
| F | `044dbe3` + 本报告 | 版本同步 8 处；交付报告；基线状态更新 |

**规则改动摘要**：

- 评测集：`test-prompts.json` 40 task / 12 trigger，加 `business-regressions.json` 2 条 = 42 task；新增 #33–#40 覆盖四目标
- `core.md`：阶段 2 取消机械乘法、新增「裁剪说明」列；阶段 4 新增增强/独立/降级三模式机器校验约定
- `prompt-strategy.md`：基础模板加预算/去重/全覆盖核对 3 条；删「每批 20–30 条」；覆盖率合格线 80% → 100% 或显式原因
- `case-arrangement.md`：三档软预算 + 合并优先 + 输出前去重
- `writing-rules.md`：紧凑表格与预算计数对齐

冻结套件：[2026-11-01-test-case-quality-cases.json](../2026-11-01-test-case-quality-cases.json)，54 cases / 217 checks，SHA256 `a504f74130f19cf0ff655692beb11c61a6451d52907d69d6a3c35ed9adb9fd56`（LF blob）。版本升级后重新导出比对，SHA256 完全一致。

## 2. 版本同步（8 处，实跑通过）

| # | 文件 | 位置 |
|---|---|---|
| 1 | `plugins/testing/skills/test-case-engineer/SKILL.md` | frontmatter `version` |
| 2 | `plugins/testing/skills/test-case-engineer/test-prompts.json` | 顶层 `version` |
| 3 | `plugins/testing/skills/test-case-engineer/README.md` | 首段 tagline |
| 4 | `plugins/testing/skills/test-case-engineer/README.md` | 「版本历史」首条 |
| 5 | `README.md` | 根技能表 |
| 6 | `docs/skills-overview.md` | test-case-engineer 节 `**版本**` |
| 7 | `plugins/testing/README.md` | 能力矩阵版本列 |
| 8 | `CHANGELOG.md` | `## [Unreleased]` Added 首条 |

`check-version-sync.py` 全绿。另在评测执行协议中补注当前版本。**不升** `testing-bundle`（仍 3.5.2）与 `review-checker`（仍 0.4.0）：路由行为与 MCP 契约均未改变。

## 3. F1 全量校验结果

| 检查 | 本地结果 |
|---|---|
| 6 个仓库校验脚本 | **全绿**（每个 commit 前实跑） |
| `skill-evals.py --skill test-case-engineer` | `42 task / 12 trigger`；明确标注仅输入校验 |
| 冻结套件可复现性 | 改版前后 SHA256 一致（实跑） |
| review-checker 包 pytest | **110 passed**（本地 venv 实跑） |
| `scripts/tests` | **47 passed / 4 failed**；4 条均为 `ModuleNotFoundError: No module named 'docx'`，本地 venv 未装 `python-docx`，CI 的 `repository-tools` 会安装，与本次改动无关 |
| state-machine-testing 包 pytest | 未完成：本地 venv 缺 `yaml`，CI 侧验证 |
| 系统 Python `pytest` | 未安装，仓库脚本改用 venv 执行 |
| markdownlint / pre-commit / YAML 校验 | 本地未安装，CI 侧验证 |
| 新增 Markdown 格式自检 | 无行尾空格、单个一级标题、末尾单换行（实跑） |

**PR 创建后的 CI 结果（2026-11-01 实测）**：GitHub Actions 6 个检查全部 `completed / success`——`Offline test data generator`、`Functional tests (state-machine-testing)`、`repository-tools`、`Functional tests (wechat-formatter)`、`Functional tests (review-checker)`、`Lint & Validate`。本地缺失的 `python-docx`、`yaml`、markdownlint、pre-commit 相关测试组在 CI 侧全部通过；上表中「CI 侧验证」项至此已补齐。

## 4. 未验证项与 `dry_run` 边界

- **模型行为评测未执行**：无外部 runner / 独立 judge，Tier 2 与 Tier 3 为空；无通过率、无质量分数、无 A/B 对比结论。
- **token 未重测**：10-10 报告的 28,585 代理 token 与「1 条支付用例 input 中位数 136,339」仍是 v9.4.1 旧数据。
- **三份阶段报告均为 `dry_run`**：[阶段 A 基线](2026-11-01-test-case-quality-baseline.md)、[阶段 B 对照](2026-11-01-stage-b-machine-check-dryrun.md)、[阶段 C 对照](2026-11-01-stage-c-conciseness-dryrun.md)。judge 与执行者同源，不作 keep/revert 依据。
- **宿主内 MCP 调用与端到端生成流程未验证**：B2 是本地 venv 直连 `validate_all`，不等于宿主内 MCP 可用。
- **历史 `runs.jsonl` 与新套件不兼容**：A2 改变 expectations 条数，`--results` 要求 `check_results` 长度严格相等，跨版本分数不可比。
- 本报告不含「质量提升」「优化效果」类表述；规则改动的实际效果需 Tier 2/Tier 3 结果支撑。

## 5. 已知未完成（如实记录）

| 项 | 状态 | 归属 |
|---|---|---|
| 交付物由 4 份收敛为 2 份 | 仍为 4 份（需求理解/测试点清单/用例集/效率报告） | 后续阶段 |
| #37「需求条目作分母」与需求→测试点→用例矩阵 | 1 项断言部分、1 项仍缺 | 阶段 E |
| 「覆盖全」的完整可计算覆盖度 | 仅做到测试点→用例不遗漏 | 阶段 E |
| `core.md` 产品特定测试点段的机械表述 | 与裁剪原则并存，未改 | 阶段 D |
| `prompt-strategy.md` 的 ≥90% 人工检查比例 | 与 100% 覆盖口径不完全一致 | 阶段 D |
| 根 `README.md` 技能表仍写 `review-checker v0.3.1（可选）` | 既有漂移（实际 0.4.0），不在本次范围 | 后续专项 |

用例条数、重复用例数**没有实测数字**，三份阶段报告均未编造前后对比值。

## 6. 发布边界与回滚

- 发布状态（2026-11-01）：分支 `feat/test-case-quality-eval` 已推送到 `origin`，**PR [#137](https://github.com/liu-YLY/my-skills/pull/137)** 已创建，CI 6 项全绿；**尚未合并**，合并与删除分支由用户决定。
- PR 规模：1783 insertions / 76 deletions，超过 AGENTS.md 的 400 行/PR 上限；PR 描述中已按文档/生成物类申请豁免（747 行冻结套件 JSON + 422 行执行计划 + 约 430 行评测文档，实际规则改动约 250 行）。如需严格合规，可改为按阶段拆分的堆叠 PR。
- 每个任务一个 Conventional Commits 中文 commit；整体 PR 规模说明见上一条。
- 回滚：按 commit 用 `git revert` 单任务回滚；`backup/pre-sync-20261031` 仍为整仓回滚点。
- 版本回退需同时回退 §2 的 8 处引用，否则 `check-version-sync.py` 会失败。

## 7. 下一步（待用户决定）

1. **已完成**：分支已推送，PR [#137](https://github.com/liu-YLY/my-skills/pull/137) 已创建，CI 6 项全绿；待用户决定是否合并与删除分支
2. 执行可选阶段 D（规则收敛）或 E（覆盖度可计算，补上需求条目分母）
3. 准备独立 runner 与 judge，按 [评测执行协议](../test-case-quality-eval-protocol.md) 跑 Tier 2/Tier 3，形成可比基线
4. 或者直接停在 v9.11.0，不再改动
