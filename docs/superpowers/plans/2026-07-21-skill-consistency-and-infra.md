# Skill 一致性补全与工程化基础设施实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 偿还 8 个 skill 检查报告中的 21 项 P1-P3 欠债，并补齐开源发布前的工程化基础设施（LICENSE / CHANGELOG / CONTRIBUTING / CI）。

**Architecture:** 按 PR 粒度拆分为 4 个独立 fix 分支，每个分支基于最新 main，遵循 400 行 PR 上限。PR1-P3 聚焦 skill 内容补全，PR4 聚焦仓库级基础设施。所有 PR 共用同一检查报告作为依据。

**Tech Stack:** Markdown / JSON / YAML / GitHub Actions / pre-commit

---

## 背景

8 个 skill 检查报告发现 21 项 P1-P3 问题（P0 已在 PR #18 修复）。本计划按优先级分 4 个 PR 推进：

- **PR1** (fix/skill-structure-p1)：P1 结构补全 — 3 个 skill 的 knowledge/quickstart/assets 补齐
- **PR2** (fix/skill-consistency-p2)：P2 一致性修复 — 负载模型统一、CHECKPOINT 补全、test-prompts 扩充、降级说明完善
- **PR3** (docs/skill-docs-sync-p3)：P3 文档同步 — README 文件结构图修正、v3.0.0 新能力描述、反例数量同步
- **PR4** (chore/project-infra)：工程化基础设施 — LICENSE / CHANGELOG / CONTRIBUTING / .github 模板 / CI

## 文件结构

### PR1 涉及文件

- Create: `plugins/testing/skills/bug-analyzer/knowledge/report-template.md`
- Create: `plugins/testing/skills/bug-analyzer/knowledge/defensive-test-points.md`
- Modify: `plugins/testing/skills/bug-analyzer/SKILL.md`（索引表新增 2 行）
- Modify: `plugins/testing/skills/bug-analyzer/README.md`（knowledge 索引同步）
- Create: `plugins/testing/skills/change-impact-analyzer/knowledge/diff-modes.md`
- Create: `plugins/testing/skills/change-impact-analyzer/knowledge/cross-impact-analysis.md`
- Create: `plugins/testing/skills/change-impact-analyzer/knowledge/report-template.md`
- Create: `plugins/testing/skills/change-impact-analyzer/knowledge/anti-patterns.md`
- Modify: `plugins/testing/skills/change-impact-analyzer/SKILL.md`（下沉内容、索引表更新）
- Create: `plugins/wechat-formatter/skills/wechat-formatter/knowledge/module-design.md`
- Create: `plugins/wechat-formatter/skills/wechat-formatter/knowledge/brand-profile-spec.md`
- Create: `plugins/wechat-formatter/skills/wechat-formatter/integrations/quickstart.md`
- Create: `plugins/wechat-formatter/skills/wechat-formatter/examples/sample-output-apple.md`
- Create: `plugins/wechat-formatter/skills/wechat-formatter/examples/sample-output-cyber.md`
- Modify: `plugins/wechat-formatter/skills/wechat-formatter/README.md`（文件结构图补全）

### PR2 涉及文件

- Modify: `plugins/testing/skills/performance-test-engineer/knowledge/load-models.md`（补第 5 种模型）
- Modify: `plugins/testing/skills/performance-test-engineer/SKILL.md`（统一术语）
- Modify: `plugins/testing/skills/performance-test-engineer/README.md`（同步）
- Modify: `plugins/testing/skills/testing-bundle/test-prompts.json`（id 4 expected 修正）
- Modify: `plugins/testing/skills/test-case-engineer/test-prompts.json`（补 v8.1.0 + 跨 skill 路由 prompt）
- Modify: `plugins/testing/skills/bug-analyzer/SKILL.md`（降级说明完善）
- Modify: `plugins/testing/skills/bug-analyzer/knowledge/bug-patterns-index.md`（降级说明完善）
- Modify: `plugins/testing/skills/bug-analyzer/test-prompts.json`（扩充至 8 条）
- Modify: `plugins/testing/skills/change-impact-analyzer/SKILL.md`（阶段 3 增 CHECKPOINT）
- Modify: `plugins/testing/skills/change-impact-analyzer/test-prompts.json`（补 3 种 diff 模式 prompt）
- Modify: `plugins/testing/skills/test-strategy-engineer/test-prompts.json`（扩充至 8 条）
- Modify: `plugins/wechat-formatter/skills/wechat-formatter/test-prompts.json`（扩充至 8 条）

### PR3 涉及文件

- Modify: `plugins/testing/skills/bug-analyzer/README.md`（移除 scripts/ 错误描述）
- Modify: `plugins/testing/skills/test-case-engineer/README.md`（文件结构图补全 + 知识库索引补全）
- Modify: `plugins/wechat-formatter/skills/wechat-formatter/README.md`（文件结构图补 brand/layout + v3.0.0 新能力章节）
- Modify: `plugins/testing/skills/change-impact-analyzer/README.md`（反例数量与 SKILL.md 同步 + prompt 数量修正）

### PR4 涉及文件

- Create: `LICENSE`
- Create: `CHANGELOG.md`
- Create: `CONTRIBUTING.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `.github/ISSUE_TEMPLATE/bug-report.md`
- Create: `.github/ISSUE_TEMPLATE/feature-request.md`
- Create: `.github/ISSUE_TEMPLATE/skill-proposal.md`
- Create: `.github/workflows/ci.yml`

---

## PR1：P1 结构补全

**分支**：`fix/skill-structure-p1`（基于最新 main）
**目标**：让 bug-analyzer / change-impact-analyzer / wechat-formatter 三个 skill 达到 8 项标准交付物

### Task 1: bug-analyzer 补 knowledge 文件

**Files:**
- Create: `plugins/testing/skills/bug-analyzer/knowledge/report-template.md`
- Create: `plugins/testing/skills/bug-analyzer/knowledge/defensive-test-points.md`
- Modify: `plugins/testing/skills/bug-analyzer/SKILL.md`
- Modify: `plugins/testing/skills/bug-analyzer/README.md`

- [ ] **Step 1: 创建 report-template.md**

从 SKILL.md 步骤 5 报告模板下沉内容，包含：
- 报告字段定义（标题/复现步骤/隔离结论/根因/修复方案/防御性测试点）
- 各字段填写规范
- 报告示例（偶发复现 Bug / 环境差异 Bug 两类）

- [ ] **Step 2: 创建 defensive-test-points.md**

防御性测试点反推方法详解，包含：
- 反推流程（根因 → 风险点 → 防御性测试点）
- 5 类防御性测试点（边界值/异常输入/并发/资源/状态）
- 与 test-case-engineer 的转交规则

- [ ] **Step 3: 更新 SKILL.md 知识库索引表**

在索引表中新增 2 行：
- `knowledge/report-template.md` — 何时查阅：步骤 5 生成报告时
- `knowledge/defensive-test-points.md` — 何时查阅：步骤 5 反推防御性测试点时

- [ ] **Step 4: 更新 README.md knowledge 索引**

同步 README 的 knowledge 文件列表（2 → 4）

- [ ] **Step 5: 自检**

验证：
- knowledge/ 目录下文件数 = 4
- SKILL.md 索引表行数 = 4
- README.md knowledge 列表 = 4
- 4 个 knowledge 文件路径在 SKILL.md 中均被引用

- [ ] **Step 6: Commit**

```bash
git add plugins/testing/skills/bug-analyzer/knowledge/report-template.md \
        plugins/testing/skills/bug-analyzer/knowledge/defensive-test-points.md \
        plugins/testing/skills/bug-analyzer/SKILL.md \
        plugins/testing/skills/bug-analyzer/README.md
git commit -m "fix(bug-analyzer): 补全 knowledge 文件至 4 个标准数量

新增 report-template.md（报告模板下沉）与 defensive-test-points.md
（防御性测试点反推方法详解），修复 knowledge 文件数不足的 P1 结构
缺陷。

SKILL.md 与 README.md 知识库索引同步更新。"
```

### Task 2: change-impact-analyzer 拆分 SKILL.md

**Files:**
- Create: `plugins/testing/skills/change-impact-analyzer/knowledge/diff-modes.md`
- Create: `plugins/testing/skills/change-impact-analyzer/knowledge/cross-impact-analysis.md`
- Create: `plugins/testing/skills/change-impact-analyzer/knowledge/report-template.md`
- Create: `plugins/testing/skills/change-impact-analyzer/knowledge/anti-patterns.md`
- Modify: `plugins/testing/skills/change-impact-analyzer/SKILL.md`

- [ ] **Step 1: 创建 diff-modes.md**

下沉 SKILL.md 中「七种 diff 模式」章节，包含：
- 7 种 diff 模式的 git 命令、适用场景、输出格式
- 模式选择决策树

- [ ] **Step 2: 创建 cross-impact-analysis.md**

下沉 SKILL.md 中「阶段 3 交叉分析」章节，包含：
- Mode A / Mode B 双模式规则
- 变更固有风险三档清单
- 跨层影响链路追踪方法
- 前后端契约两侧检查

- [ ] **Step 3: 创建 report-template.md**

下沉 SKILL.md 中「阶段 4 报告模板」章节，包含：
- 8 段报告结构
- P0/P1/P2 优先级标注规则
- 报告示例

- [ ] **Step 4: 创建 anti-patterns.md**

下沉 SKILL.md 中「反例与黑名单」章节（7 条），与 README 反例对齐

- [ ] **Step 5: 精简 SKILL.md**

将 SKILL.md 中已下沉的章节替换为索引引用，目标行数从 815 行降至 300 行以内。保留：
- frontmatter
- 适用范围 / 不适用范围
- 四阶段流程概览（含 CHECKPOINT）
- 知识库索引表
- 与其他 skill 的协同路由规则

- [ ] **Step 6: 自检**

验证：
- knowledge/ 目录下文件数 = 4
- SKILL.md 行数 ≤ 300
- 4 个 knowledge 文件路径在 SKILL.md 中均被引用
- SKILL.md 仍包含 frontmatter / 适用范围 / 四阶段流程 / 索引表 / 路由规则

- [ ] **Step 7: Commit**

```bash
git add plugins/testing/skills/change-impact-analyzer/knowledge/ \
        plugins/testing/skills/change-impact-analyzer/SKILL.md
git commit -m "refactor(change-impact-analyzer): 拆分 815 行 SKILL.md 为 knowledge 子文件

将七种 diff 模式、交叉分析、报告模板、反例黑名单下沉到 knowledge/
目录，SKILL.md 收敛为索引+决策树（815 行 → <300 行），修复 SKILL.md
全内联与自身反例原则矛盾的 P1 结构缺陷。

新增 4 个 knowledge 文件：
- diff-modes.md：7 种 diff 模式与选择决策树
- cross-impact-analysis.md：Mode A/B + 跨层链路追踪
- report-template.md：8 段报告结构
- anti-patterns.md：7 条反例黑名单"
```

### Task 3: wechat-formatter 补 knowledge + quickstart + examples

**Files:**
- Create: `plugins/wechat-formatter/skills/wechat-formatter/knowledge/module-design.md`
- Create: `plugins/wechat-formatter/skills/wechat-formatter/knowledge/brand-profile-spec.md`
- Create: `plugins/wechat-formatter/skills/wechat-formatter/integrations/quickstart.md`
- Create: `plugins/wechat-formatter/skills/wechat-formatter/examples/sample-output-apple.md`
- Create: `plugins/wechat-formatter/skills/wechat-formatter/examples/sample-output-cyber.md`
- Modify: `plugins/wechat-formatter/skills/wechat-formatter/README.md`

- [ ] **Step 1: 创建 module-design.md**

v3.0.0 高级排版模块设计原则，包含：
- 9 大类模块清单（callout/cards/timeline/tabs/quote/stat/grid/animated/extra）
- `:::module` 语法规范
- 模块组合规则与限制

- [ ] **Step 2: 创建 brand-profile-spec.md**

Brand Profile 配置规范，包含：
- brand-profile.md 字段定义
- 配置加载机制
- 与文章风格的优先级规则

- [ ] **Step 3: 创建 integrations/quickstart.md**

包含：
- 依赖安装（pip install markdown beautifulsoup4）
- 3 种典型用法（默认/快速/仅排版）
- 输出文件说明
- 故障排查 3 项

- [ ] **Step 4: 创建 sample-output-apple.md**

苹果风格输出示例（参考 sample-output-tech-blog.md 格式），输入用 article-input-sample.md

- [ ] **Step 5: 创建 sample-output-cyber.md**

赛博风格输出示例

- [ ] **Step 6: 更新 README.md 文件结构图**

补全 knowledge/（1 → 3 文件）、integrations/、examples/（4 → 6 文件）描述

- [ ] **Step 7: 自检**

验证：
- knowledge/ 目录下文件数 = 3
- integrations/quickstart.md 存在
- examples/ 下 sample-output 数 = 6
- README.md 文件结构图与实际一致

- [ ] **Step 8: Commit**

```bash
git add plugins/wechat-formatter/skills/wechat-formatter/knowledge/module-design.md \
        plugins/wechat-formatter/skills/wechat-formatter/knowledge/brand-profile-spec.md \
        plugins/wechat-formatter/skills/wechat-formatter/integrations/quickstart.md \
        plugins/wechat-formatter/skills/wechat-formatter/examples/sample-output-apple.md \
        plugins/wechat-formatter/skills/wechat-formatter/examples/sample-output-cyber.md \
        plugins/wechat-formatter/skills/wechat-formatter/README.md
git commit -m "fix(wechat-formatter): 补全 knowledge/quickstart/examples 至标准结构

新增 2 个 knowledge 文件（module-design + brand-profile-spec）、
integrations/quickstart.md、2 个 sample-output（apple + cyber），
修复 knowledge 文件数偏少 + 缺 quickstart + examples 输出示例不全的
P1 结构缺陷。

README.md 文件结构图同步更新。"
```

### Task 4: PR1 推送与创建 PR

- [ ] **Step 1: 推送分支**

```bash
git push -u origin fix/skill-structure-p1
```

- [ ] **Step 2: 创建 PR**

通过 GitHub MCP 创建 PR，base=main，head=fix/skill-structure-p1

---

## PR2：P2 一致性修复

**分支**：`fix/skill-consistency-p2`（基于最新 main，需等 PR1 合并后）
**目标**：修复内容一致性问题，扩充 test-prompts 覆盖度

### Task 1: performance-test-engineer 负载模型统一

**Files:**
- Modify: `plugins/testing/skills/performance-test-engineer/knowledge/load-models.md`
- Modify: `plugins/testing/skills/performance-test-engineer/SKILL.md`
- Modify: `plugins/testing/skills/performance-test-engineer/README.md`

- [ ] **Step 1: 在 load-models.md 补齐第 5 种模型**

新增「基准测试（Baseline Test）」作为第 5 类，与 SKILL.md 术语统一。包含定义/适用场景/执行命令/输出格式

- [ ] **Step 2: 统一 SKILL.md 与 README.md 术语**

确保 SKILL.md 阶段 2 与 README 的负载模型列表均为 5 种，命名与 load-models.md 一致

- [ ] **Step 3: 自检**

验证：load-models.md / SKILL.md / README.md 三处负载模型数量 = 5，命名一致

- [ ] **Step 4: Commit**

```bash
git commit -m "fix(performance-test-engineer): 统一负载模型数量至 5 种

load-models.md 新增基准测试（Baseline Test）作为第 5 类，与
SKILL.md/README.md 的 5 种模型术语对齐，修复 P2 一致性问题。"
```

### Task 2: testing-bundle test-prompts id 4 修正

**Files:**
- Modify: `plugins/testing/skills/testing-bundle/test-prompts.json`

- [ ] **Step 1: 修正 id 4 expected 描述**

在 expected 字段中补列第 5 个选项 "E. 状态机测试（state-machine-test-engineer）"

- [ ] **Step 2: 自检**

验证：id 4 expected 列出 5 个选项，与 SKILL.md 路由规则一致

- [ ] **Step 3: Commit**

```bash
git commit -m "fix(testing-bundle): 修正 test-prompts id 4 expected 漏列状态机选项

补列第 5 个选项 E. 状态机测试，与 SKILL.md 路由规则保持一致。"
```

### Task 3: bug-analyzer 降级说明完善

**Files:**
- Modify: `plugins/testing/skills/bug-analyzer/SKILL.md`
- Modify: `plugins/testing/skills/bug-analyzer/knowledge/bug-patterns-index.md`

- [ ] **Step 1: 在 SKILL.md 完善降级说明**

明确：单独安装时步骤 2 隔离阶段回退到「通用模式（输入校验/状态/权限/数据/UI）兜底」；步骤 5 报告中「对照缺陷模式」字段标注「缺陷模式库不可用，未对照」

- [ ] **Step 2: 在 bug-patterns-index.md 同步降级说明**

- [ ] **Step 3: Commit**

```bash
git commit -m "docs(bug-analyzer): 完善单独安装时的降级行为说明

明确 fallback 行为（步骤 2 回退通用模式兜底、步骤 5 报告字段标注
「缺陷模式库不可用」），修复 P2 降级说明不具体问题。"
```

### Task 4: change-impact-analyzer 阶段 3 增 CHECKPOINT

**Files:**
- Modify: `plugins/testing/skills/change-impact-analyzer/SKILL.md`

- [ ] **Step 1: 在阶段 3 末尾增 🔴 CHECKPOINT**

让用户校对两类问题分析结果后再生成最终报告

- [ ] **Step 2: Commit**

```bash
git commit -m "fix(change-impact-analyzer): 阶段 3 末尾新增 CHECKPOINT

让用户校对两类问题分析结果后再生成最终报告，修复 P2 CHECKPOINT
覆盖不全问题。"
```

### Task 5: 批量扩充 test-prompts.json

**Files:**
- Modify: `plugins/testing/skills/test-case-engineer/test-prompts.json`（+2 条）
- Modify: `plugins/testing/skills/bug-analyzer/test-prompts.json`（3 → 8 条）
- Modify: `plugins/testing/skills/test-strategy-engineer/test-prompts.json`（3 → 8 条）
- Modify: `plugins/testing/skills/change-impact-analyzer/test-prompts.json`（5 → 8 条）
- Modify: `plugins/wechat-formatter/skills/wechat-formatter/test-prompts.json`（3 → 8 条）

- [ ] **Step 1: test-case-engineer 补 2 条**

- 验证 v8.1.0 拆分合并平衡策略（含 8 检查点强制拆分）
- 验证 bug 根因描述路由到 bug-analyzer

- [ ] **Step 2: bug-analyzer 扩充至 8 条**

补充：无法复现 / 多根因 / 生产无法撤销修复 / 防御性测试点反推 + 转交 test-case-engineer / 反例（跳过复现直接猜根因）

- [ ] **Step 3: test-strategy-engineer 扩充至 8 条**

补充：项目特征模糊追问 / 风险数据不足降级 / 分层比例争议 fallback / 一词双义边界消解 / 阶段 5 不触发负向验证

- [ ] **Step 4: change-impact-analyzer 扩充至 8 条**

补充：暂存区模式 / 单 Commit 模式 / Revision Range 模式

- [ ] **Step 5: wechat-formatter 扩充至 8 条**

补充：tutorial / casual-chat / cyber 三种风格 + 快速模式 + :::module 高级模块 + Brand Profile 触发 + 文件不存在 fallback

- [ ] **Step 6: 自检**

验证：5 个 test-prompts.json 均为合法 JSON，prompts 数量符合预期

- [ ] **Step 7: Commit**

```bash
git commit -m "test(skills): 批量扩充 5 个 skill 的 test-prompts.json 覆盖度

- test-case-engineer: 12 → 14（补 v8.1.0 拆分合并 + 跨 skill 路由）
- bug-analyzer: 3 → 8（补无法复现/多根因/生产无法撤销/防御性反推/反例）
- test-strategy-engineer: 3 → 8（补模糊追问/降级/争议/边界消解/负向）
- change-impact-analyzer: 5 → 8（补暂存区/单 Commit/Revision Range）
- wechat-formatter: 3 → 8（补 tutorial/casual-chat/cyber/快速/模块/Brand/fallback）

修复 P2 test-prompts 覆盖度不足问题。"
```

### Task 6: PR2 推送与创建 PR

- [ ] **Step 1: 推送分支**

- [ ] **Step 2: 创建 PR**

---

## PR3：P3 文档同步

**分支**：`docs/skill-docs-sync-p3`（基于最新 main，需等 PR1/PR2 合并后）
**目标**：修正 README 文件结构图，同步 v3.0.0 新能力描述

### Task 1: bug-analyzer README 移除 scripts/ 错误描述

- [ ] **Step 1: 修正 README 文件结构图**

移除不存在的 `scripts/` 子目录，改为说明「脚本共享于 `$PLUGIN_ROOT/scripts/`」

- [ ] **Step 2: Commit**

### Task 2: test-case-engineer README 文件结构图补全

- [ ] **Step 1: 补全文件结构图**

新增 test-prompts.json / docs/ / knowledge/products/example.md
- [ ] **Step 2: 补全知识库索引表**

新增 review-mode.md 与 anti-patterns.md

- [ ] **Step 3: Commit**

### Task 3: wechat-formatter README 补 v3.0.0 新能力

- [ ] **Step 1: 文件结构图补 brand/ 与 layout/**

- [ ] **Step 2: 新增 v3.0.0 新能力章节**

包含：高级排版模块（9 大类 + `:::module` 语法）、Brand Profile、layout/ 目录说明

- [ ] **Step 3: Commit**

### Task 4: change-impact-analyzer README 反例与 prompt 数同步

- [ ] **Step 1: 反例数量与 SKILL.md 同步**

- [ ] **Step 2: 修正 prompt 数量描述（3 → 5）**

- [ ] **Step 3: Commit**

### Task 5: PR3 推送与创建 PR

---

## PR4：工程化基础设施

**分支**：`chore/project-infra`（基于最新 main，可与 PR1-3 并行）
**目标**：补齐开源发布前的工程化基础设施

### Task 1: 添加 LICENSE

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: 创建 MIT LICENSE 文件**

- [ ] **Step 2: Commit**

```bash
git commit -m "chore: 添加 MIT LICENSE"
```

### Task 2: 添加 CHANGELOG.md

**Files:**
- Create: `CHANGELOG.md`

- [ ] **Step 1: 创建 Keep a Changelog 格式的 CHANGELOG.md**

包含 [Unreleased] + 历史版本（testing-bundle v3.0.0 / wechat-formatter v3.0.0 等）

- [ ] **Step 2: Commit**

### Task 3: 添加 CONTRIBUTING.md

**Files:**
- Create: `CONTRIBUTING.md`

- [ ] **Step 1: 创建 CONTRIBUTING.md**

包含：开发环境 / git workflow（引用 .trae/rules/） / 8 项交付物标准 / pre-commit 安装 / PR 流程

- [ ] **Step 2: Commit**

### Task 4: 添加 .github 模板

**Files:**
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `.github/ISSUE_TEMPLATE/bug-report.md`
- Create: `.github/ISSUE_TEMPLATE/feature-request.md`
- Create: `.github/ISSUE_TEMPLATE/skill-proposal.md`

- [ ] **Step 1: 创建 PR 模板**

含自检清单（与 .trae/rules/git-workflow.md 对齐）

- [ ] **Step 2: 创建 3 个 Issue 模板**

- [ ] **Step 3: Commit**

### Task 5: 添加 CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: 创建 CI workflow**

包含：markdown lint + JSON 校验 + YAML lint + pre-commit 运行

- [ ] **Step 2: Commit**

### Task 6: PR4 推送与创建 PR

---

## 执行顺序

1. **PR1** (fix/skill-structure-p1) — 当前执行
2. **PR4** (chore/project-infra) — 可与 PR1 并行
3. **PR2** (fix/skill-consistency-p2) — 等 PR1 合并后
4. **PR3** (docs/skill-docs-sync-p3) — 等 PR1/PR2 合并后

## Self-Review

### Spec coverage

- ✅ P1 bug-analyzer knowledge 不足 → PR1 Task 1
- ✅ P1 change-impact-analyzer 无 knowledge → PR1 Task 2
- ✅ P1 wechat-formatter knowledge/quickstart/examples 不足 → PR1 Task 3
- ✅ P2 performance 负载模型不一致 → PR2 Task 1
- ✅ P2 testing-bundle id 4 → PR2 Task 2
- ✅ P2 bug-analyzer 降级说明 → PR2 Task 3
- ✅ P2 change-impact CHECKPOINT → PR2 Task 4
- ✅ P2 test-prompts 覆盖度 → PR2 Task 5
- ✅ P3 README 文件结构图 → PR3 Task 1-3
- ✅ P3 wechat v3.0.0 新能力 → PR3 Task 3
- ✅ P3 change-impact 反例/prompt 数 → PR3 Task 4
- ✅ 工程化基础设施 → PR4

### Placeholder scan

- ✅ 无 TBD / TODO / "implement later"
- ✅ 每个步骤均有具体操作或代码
- ⚠️ 部分 knowledge 文件内容描述较粗（如「下沉 SKILL.md 章节」），执行时需读取 SKILL.md 实际内容

### Type consistency

- ✅ 4 个 PR 分支命名与 BASE 一致
- ✅ 文件路径在 PR 间无冲突（PR1 创建 / PR2 修改不同文件 / PR3 修改 README / PR4 创建新文件）
