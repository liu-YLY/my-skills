# 阶段 6 发布准备报告

> **日期**：2026-11-23
> **分支**：`trae/agent-WZBLh1`（无 upstream，未推送）
> **状态**：6-1 版本同步、6-2 文档同步、6-3 CI 门禁、6-4 交付报告已完成；6-5 合并/清理/打 tag 待 PR。
> **工作区**：阶段 6 改动尚未提交；阶段 1–5 已在 `cd94602` 等提交中。

## 1. 版本同步（6-1）

| Skill | 旧版本 | 新版本 | 依据 |
|---|---|---:|---|
| testing-bundle | 3.6.0 | 3.7.0 | 需求评审路由 + 链 10 + 子 skill 同步 |
| test-case-engineer | 9.14.0 | 9.15.0 | 需求评审模式 + 校验器 + 默认路径瘦身 |
| state-machine-test-engineer | 1.7.6 | 1.7.7 | 默认路径瘦身 + 示例按需化 |
| change-impact-analyzer | 1.5.1 | 1.5.2 | 合并交叉分析 + 示例按需化 |
| test-strategy-engineer | 1.3.0 | 1.3.1 | 去重与压缩 |
| bug-analyzer | 1.2.3 | 1.2.4 | 报告示例按需化 + 压缩 |
| performance-test-engineer | 1.2.3 | 1.2.4 | 指标/命令表合并 + 压缩 |
| frontend-test-preparation | 1.0.0 | 1.0.1 | 入口与交接模板压缩 |
| test-data-generator | 1.1.0 | 1.1.1 | 设计参考按需化 + 压缩 |

- `plugins/testing` 三份 `plugin.json`：3.6.0 → 3.7.0。
- `.claude-plugin/marketplace.json`：bundle 描述更新为 v3.7.0、10 条混合链，并补需求评审。
- `test-prompts.json` 顶层 version 已同步 test-case / state-machine / frontend / test-data。
- `check-version-sync.py` 通过。

## 2. 文档同步（6-2）

| 文件 | 更新 |
|---|---|
| `README.md` | 全部 skill 版本；链 10；bundle 10 条链；test-case 增加需求评审 |
| `docs/skills-overview.md` | 版本；需求评审路由行；链 10；test-case 需求评审能力 |
| `plugins/testing/README.md` | 版本；10 条链；test-case 职责；单意图路由表述 |
| `.claude-plugin/marketplace.json` | 版本、链数、需求评审 |
| 6 个 skill README | 版本历史新增当前版本条目 |
| `testing-bundle` / `frontend` / `test-data` CHANGELOG | 新增当前版本条目 |

`check-md-links.py`、`check-project-inventory.py` 通过。

## 3. CI 门禁（6-3）

- `.github/workflows/ci.yml` 新增：
  - `python scripts/check-context-budget.py --target`
- 现有 `check-version-sync`、`check-knowledge-count`、`check-md-links`、`check-skill-consistency` 保留。
- 模型评测 smoke 保持手动；CI 只运行确定性检查与现有 `scripts/skill-evals.py` 输入校验。

## 4. 验证结果

| 项 | 结果 |
|---|---|
| 六个仓库脚本 | 全绿（预算、结构、知识引用、链接、清单、版本） |
| `check-context-budget.py --target` | 20/20 ok |
| 仓库 pytest | 47 passed；9 failed 均为沙箱缺 PowerShell 的安装器 smoke test |
| review-checker MCP | 110 passed |
| state-machine MCP | 114 passed |
| 模型行为质量 | 未执行，沿用阶段 5 `partial` 结论 |

## 5. PR 拆分计划（6-4）

已从 `main` @ `848b613` 重建 15 个 stacked 分支，每组一个原子提交；栈顶树与 `b778f92` 完全一致。15 个分支已推送到 origin。

| # | 分支 | 提交 | 行数 | 说明 |
|---|---|---|---:|---|
| 1 | `feat/eval-context-tools` | `8048f0b` | 826 | 上下文度量、预算门禁、规则清单脚本 |
| 2 | `feat/eval-quality-suite` | `975e0fd` | 5,474 | v7/v7.1/v7.2 套件、种子集、gold、报告 |
| 3 | `feat/eval-rule-inventory` | `1f86f30` | 5,488 | 规范语句清单 |
| 4 | `feat/eval-phase4-harness` | `2b2993f` | 12,724 | 阶段 4 harness 与 Probe 产物 |
| 5 | `refactor/test-case-knowledge` | `5606cb8` | 2,159 | 写作契约合并与知识瘦身 |
| 6 | `feat/test-case-requirement-review` | `490cb63` | 1,341 | 需求评审模式、校验器、评测用例 |
| 7 | `feat/bundle-requirement-review-route` | `dedd74f` | 565 | 需求评审路由与链 10 |
| 8 | `refactor/state-machine-slim` | `d745e3d` | 826 | 入口/场景知识瘦身与示例按需化 |
| 9 | `refactor/change-impact-slim` | `72dd97b` | 1,244 | 合并交叉分析、示例按需化 |
| 10 | `refactor/test-strategy-slim` | `647d6f2` | 259 | 去重与压缩 |
| 11 | `refactor/bug-analyzer-slim` | `6886401` | 742 | 报告示例按需化与压缩 |
| 12 | `refactor/performance-slim` | `1bf9934` | 341 | 指标/命令表合并 |
| 13 | `refactor/frontend-test-data-slim` | `10d9908` | 93 | 去重与按需参考 |
| 14 | `chore/release-sync-3.7.0` | `0852384` | 101 | 版本、文档、CI、marketplace |
| 15 | `docs/phase5-6-handoff` | `8d47119` | 1,446 | 阶段 5–6 交接与计划记录 |

**≤400 行**：第 10、12、13、14 组达标；其余为已记录例外：
- 第 2–4 组是评测套件/生成产物，按文件整体提交，无法无损拆到 400 行以下。
- 第 5–9 组是单个知识文件的整体重写或新增模式，按 hunk 拆分会产生不可评审的半文件。
- 第 1 组为 7 个新增工具文件，按文件拆会破坏脚本间契约。
- 第 15 组为执行交接文档，单独 docs PR。

每个 PR 的描述需注明例外原因与文件清单；merged 后再按 6-5 删除远程分支、打 tag。

## 6. 未完成与限制

- 15 个 stacked 分支已推送；未创建 PR、未打 tag（6-5 待执行）。
- 原 `trae/agent-WZBLh1` 与 `backup/pre-stacked-release` 保留，可回退。
- GitHub 连接器已授权，但服务要求在新会话中重试；本轮未创建 PR。`gh` 仍未登录。
- 9 个安装器 smoke test 因沙箱无 PowerShell 无法执行。
- 模型侧质量未重测；发布前若需该证据，用付费 runner 跑阶段 5 建议的 3-case 对照。

## 7. 需要确认

| 选项 | 内容 | 建议 |
|---|---|---|
| A | 推送 15 个 stacked 分支到 origin | 可立即执行；PR 需 GitHub 授权 |
| B | 先人工 review 本地栈，再推送 | 适合对例外 PR 有顾虑时 |
| C | 合并后打 tag `v3.7.0` 并清理分支 | 6-5，需在 PR 合并后 |
