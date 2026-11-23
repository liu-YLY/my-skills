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

当前分支相对 `main` @ `848b613` 的改动约 430 文件 / 28.9k 行，主要体积来自评测数据与生成产物。按 ≤400 行的规则，需要拆分为以下 PR；超过 400 行的组需再拆或标记为生成数据例外。

| PR | 范围 | 估算行数 | 处理建议 |
|---|---|---:|---|
| PR-1 | `scripts/` 工具与测试 | 826 | 拆为 2–3 个：上下文脚本 / 校验器与测试 / 技能评测输入校验 |
| PR-2 | 评测套件 v7.1/v7.2 + 种子集 + gold | 3,593 | 生成数据例外或按套件拆 |
| PR-3 | `rule-inventory/` | 5,488 | 生成数据例外，单独 PR |
| PR-4 | `phase4/` harness 与 Probe 产物 | 12,724 | 生成数据例外，单独 PR |
| PR-5 | 报告与经验库 | 544 | 1 个 PR |
| PR-6 | test-case-engineer | 3,500+ | 拆为知识契约 / 需求评审模式+校验器 / 瘦身 3 个 PR |
| PR-7 | testing-bundle | 500+ | 路由与链 10 / 瘦身 2 个 PR |
| PR-8 | state-machine | 821 | 拆为 2 个 PR |
| PR-9 | change-impact | 1,244 | 拆为 3 个 PR |
| PR-10 | strategy / bug / performance | 1,342 | 每个 skill 1 个 PR |
| PR-11 | frontend / test-data | 93 | 1 个 PR |
| PR-12 | 版本、文档、CI 同步 | ~200 | 1 个 PR |

**阻塞**：现有 `trae/agent-WZBLh1` 历史包含多个大提交且未推送，直接开 PR 无法满足 ≤400 行。建议先在本地按上表重建干净的 stacked 分支（从 `main` 逐组 cherry-pick/checkout 路径），再推送逐个 PR；不重写已推送历史。

## 6. 未完成与限制

- 未提交、未推送、未创建 PR、未打 tag（6-5 待执行）。
- 无 GitHub 凭据确认，远程 PR 需用户授权。
- 9 个安装器 smoke test 因沙箱无 PowerShell 无法执行。
- 模型侧质量未重测；发布前若需该证据，用付费 runner 跑阶段 5 建议的 3-case 对照。

## 7. 需要确认

| 选项 | 内容 | 建议 |
|---|---|---|
| A | 先提交阶段 6 改动到当前分支 | 可立即执行 |
| B | 直接推送当前分支并开一个大 PR | 不满足 ≤400 行，仅适合内部预审 |
| C | 按上表重建 stacked PR 后再推送 | **推荐**，符合仓库规则 |
| D | 合并后打 tag `v3.7.0` 并清理分支 | 6-5，需在 C/B 之后 |
