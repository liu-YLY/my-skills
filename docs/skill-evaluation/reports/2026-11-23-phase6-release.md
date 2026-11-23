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

已从 `main` @ `848b613` 重建 11 个自洽 stacked 分支，每组一个原子提交；栈顶树与修复后的源提交一致。分支已推送，PR **#156–#166** 已创建。

| # | 分支 | PR | 行数 | 说明 |
|---|---|---|---:|---|
| 1 | `feat/eval-foundation` | #156 | 24.5k | 评测工具、套件、种子集、gold、规则清单、阶段 4 产物 |
| 2 | `feat/test-case-v9.15` | #157 | 3,495 | 需求评审模式、校验器、知识瘦身 |
| 3 | `feat/bundle-requirement-review` | #158 | 565 | 需求评审路由与链 10 |
| 4 | `refactor/state-machine-slim` | #159 | 823 | 入口/场景知识瘦身与示例按需化 |
| 5 | `refactor/change-impact-slim` | #160 | 1,241 | 合并交叉分析、示例按需化 |
| 6 | `refactor/test-strategy-slim` | #161 | 256 | 去重与压缩 |
| 7 | `refactor/bug-analyzer-slim` | #162 | 739 | 报告示例按需化与压缩 |
| 8 | `refactor/performance-slim` | #163 | 338 | 指标/命令表合并 |
| 9 | `refactor/frontend-test-data-slim` | #164 | 89 | 去重与按需参考 |
| 10 | `chore/release-sync-3.7.0` | #165 | 125 | 版本、文档、CI、marketplace |
| 11 | `docs/phase5-6-handoff` | #166 | 1,446 | 阶段 5–6 交接与计划记录 |

**≤400 行**：第 6、8、9、10 组达标；其余为已记录例外：
- 第 1 组是评测套件/生成产物，整体提交，无法无损拆到 400 行以下。
- 第 2、4、5、7 组是单个知识文件的整体重写或新增模式，按 hunk 拆分会产生不可评审的半文件。
- 第 3 组路由与链 10 需整体评审。
- 第 11 组为执行交接文档，单独 docs PR。

PR #156 已通过完整 CI（repository-tools、Lint、功能测试与造数测试全绿）。CI 仅在 PR 目标为 `main` 时触发，因此 #157–#166 当前无检查记录；需按顺序合并前一个 PR、把下一个 PR 的 base 改为 `main` 后触发 CI。每个 PR 的 base 为上一组分支，第 1 组 base 为 `main`；merged 后再按 6-5 删除远程分支、打 tag。

## 6. 未完成与限制

- 11 个 stacked 分支已推送，PR **#156–#166** 已创建；未合并、未打 tag（6-5 待执行）。
- 原 `trae/agent-WZBLh1` 与 `backup/pre-stacked-release` 保留，可回退。
- PR 合并需逐个 review；超过 400 行的 PR 需确认例外。
- 9 个安装器 smoke test 因沙箱无 PowerShell 无法本地执行；CI runner 已通过。
- 模型侧质量未重测；发布前若需该证据，用付费 runner 跑阶段 5 建议的 3-case 对照。

## 7. 需要确认

| 选项 | 内容 | 建议 |
|---|---|---|
| A | 按 #156→#166 顺序 review 并合并 | 推荐；每合并一个即可把下一个 PR 的 base 改为 `main` |
| B | 合并完成后打 tag `v3.7.0` 并删除 11 个远程分支 | 6-5 |
| C | 暂不合并，先处理例外 PR 的 review | 适合对评测数据体积有顾虑时 |
