# Skill Token 优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 通过结构化拆分降低 3 个高 token skill 的入口文件体积，预期入口 token 总量从 ~54,200 降至 ~44,900（-17%），并修正文档中遗留的维度数不一致问题。

**Architecture:** 按 skill 粒度拆分为 4 个独立 PR，每个 PR 基于最新 main，遵循 400 行 PR 上限。PR1-PR3 聚焦入口文件瘦身（纯内容迁移，不改逻辑），PR4 聚焦文档同步修正。所有 PR 互不依赖，可并行 review。

**Tech Stack:** Markdown

---

## 背景

基于 [Token 消耗分析报告](../../../README.md#token-消耗分析)（见 README.md），当前 skill 生态存在 3 个结构性问题：

### 问题 1：入口文件过重

| 文件 | token | 问题 |
|---|---|---|
| test-case-engineer-core.md | 9,699 | 单文件冠军，每次生成用例必加载，含大量可延迟加载的规则集与模板 |
| testing-bundle/SKILL.md | 8,377 | 路由入口，8 个使用示例占 ~2,000 token，与各子 skill README 重复 |
| wechat-formatter/SKILL.md | 5,833 | 模块语法示例占 ~700 token，本属参考材料 |

### 问题 2：示例与正文混载

testing-bundle 的 8 个使用示例（291-408 行）在每次路由决策时都会占用 context，但用户大多数情况下只需要路由判断，不需要看示例。

### 问题 3：文档维度数不一致

test-case-engineer-core.md 第 697、715 行仍写「6 维度评审」，实际评审模式已升级为 9 维度（PR #21）。这是历史遗留的同步问题。

### 优化原则

1. **纯内容迁移**：拆分是物理移动，不改写逻辑，降低风险
2. **保留速查摘要**：拆出大块后，原文件保留 10-15 行速查表 + 链接，避免引用断裂
3. **按需加载**：拆出的 knowledge 文件仅在对应阶段/模式触发时加载
4. **不拆线性流程**：bug-analyzer（五步定位法）、test-strategy-engineer（五阶段）是线性流程，拆分会破坏连贯性，不动

---

## 深度分析

### 1. test-case-engineer-core.md（719 行，9,699 token）

**结构剖析**：

| 区块 | 行范围 | 行数 | ~token | 加载时机 | 可拆分 |
|---|---|---|---|---|---|
| 目录 + 工作流概览 | 1-36 | 36 | 500 | 每次必加载 | 否（导航） |
| 阶段 1：理解需求 | 37-160 | 124 | 1,700 | 阶段 1 | 否（核心流程） |
| 阶段 2：提取测试点 | 161-328 | 168 | 2,300 | 阶段 2 | 否（核心流程） |
| 阶段 3：编写用例（流程部分） | 329-475 | 147 | 2,000 | 阶段 3 | 否（核心流程） |
| **编写与审核铁律** | **476-583** | **108** | **2,000** | 阶段 3 | **是** |
| 输出格式说明 | 584-594 | 11 | 150 | 阶段 3 | 否 |
| 阶段 4：自检（流程部分） | 595-610 | 16 | 200 | 阶段 4 | 否（核心流程） |
| **阶段 4 失败模式 + 自检清单** | **602-661** | **60** | **800** | 阶段 4 | **是** |
| 效率度量输出 | 662-691 | 30 | 400 | 阶段 4 | 否 |
| **模式切换 + 探索章程** | **692-709** | **18** | **300** | 探索式模式 | **是** |
| 评审模式引用 + 反例引用 | 710-719 | 10 | 150 | 引用块 | 否 |

**拆分决策**：

拆出 3 个 knowledge 文件，core 保留速查摘要：

| 拆出文件 | 原位置 | ~token | 拆出后 core 保留 |
|---|---|---|---|
| `knowledge/writing-iron-rules.md` | 476-583 行 | 2,000 | 铁律速查表（~15 行，title/steps/expected_results 各 3 条核心规则 + 链接） |
| `knowledge/self-check-checklist.md` | 602-661 行 | 800 | 「见 [self-check-checklist.md]」一行引用 |
| `knowledge/exploration-mode.md` | 692-709 行 | 300 | 「见 [exploration-mode.md]」一行引用 |

**预期效果**：core 从 9,699 → ~6,600 token（-32%），四阶段流程主线更清晰

**风险与缓解**：
- 风险：铁律拆出后阶段 3 可能引用不及时，导致用例质量下降
- 缓解：core 保留铁律速查表（title/steps/expected_results 各 3 条最核心规则），完整规则按需加载

### 2. testing-bundle/SKILL.md（427 行，8,377 token）

**结构剖析**：

| 区块 | 行范围 | 行数 | ~token | 可拆分 |
|---|---|---|---|---|
| 路由规则 + 决策表 + 混合意图链 | 1-192 | 192 | 3,800 | 否（核心） |
| 子 skill 协同 + 安装方式 | 193-290 | 98 | 1,900 | 否（核心） |
| **使用示例 1-8** | **291-408** | **118** | **2,300** | **是** |
| 快速上手 + 约束 | 409-427 | 19 | 400 | 否 |

**拆分决策**：

迁移 8 个示例到 `knowledge/usage-examples.md`，SKILL.md 保留：
- 示例索引表（~10 行：8 个示例的「场景 → 链路 → 转交点」映射）
- 1 个核心示例（示例 2：混合意图链 1，最能体现 bundle 价值）

**预期效果**：SKILL.md 从 8,377 → ~6,100 token（-27%）

**风险与缓解**：
- 风险：示例外迁后用户不知道在哪看示例
- 缓解：SKILL.md 保留「示例索引」小节，明确指向 knowledge/usage-examples.md

### 3. wechat-formatter/SKILL.md（296 行，5,833 token）

**结构剖析**：

| 区块 | 行范围 | 行数 | ~token | 可拆分 |
|---|---|---|---|---|
| 核心工作流 + 模式切换 + 风格匹配 | 1-116 | 116 | 2,300 | 否（核心） |
| 4 件事原则表 + 9 大类模块速览表 | 117-147 | 31 | 600 | 否（核心参考） |
| **模块语法示例** | **148-171** | **24** | **500** | **是** |
| Brand Profile + 约束 + 失败模式 + 反例 | 172-296 | 125 | 2,400 | 否 |

**拆分决策**：

迁移模块语法示例（148-171 行）到 `knowledge/module-syntax-examples.md`，SKILL.md 保留：
- 4 件事原则表 + 9 大类模块速览表（核心参考，保留）
- 1 个精简示例（hero 模块，~5 行）+ 链接指向完整示例

**预期效果**：SKILL.md 从 5,833 → ~5,300 token（-9%）

**风险与缓解**：
- 风险：低——模块语法本就是按需查阅的参考材料
- 缓解：SKILL.md 保留 1 个最简示例 + 指向 layout/layout-modules.md 的现有链接

### 4. 文档维度数不一致

**全局扫描结果**：

| 文件 | 行 | 现状 | 应改为 |
|---|---|---|---|
| test-case-engineer-core.md | 697 | 「对他人/已有用例做 6 维度评审」 | 「9 维度评审」 |
| test-case-engineer-core.md | 715 | 「对他人/已有用例做 6 维度评审」 | 「9 维度评审」 |

**预期效果**：消除文档与实际实现（review-mode.md 已是 9 维度）的不一致

---

## 文件结构

### PR1 涉及文件（test-case-engineer-core 拆分）

- Create: `plugins/testing/skills/test-case-engineer/knowledge/writing-iron-rules.md`
- Create: `plugins/testing/skills/test-case-engineer/knowledge/self-check-checklist.md`
- Create: `plugins/testing/skills/test-case-engineer/knowledge/exploration-mode.md`
- Modify: `plugins/testing/skills/test-case-engineer/test-case-engineer-core.md`（移出 3 块 + 补速查摘要 + 链接）
- Modify: `plugins/testing/skills/test-case-engineer/SKILL.md`（knowledge 索引表新增 3 行）
- Modify: `plugins/testing/skills/test-case-engineer/README.md`（knowledge 索引同步）

### PR2 涉及文件（testing-bundle 示例外迁）

- Create: `plugins/testing/skills/testing-bundle/knowledge/usage-examples.md`
- Modify: `plugins/testing/skills/testing-bundle/SKILL.md`（移出 7 个示例 + 保留示例 2 + 补索引表）
- Modify: `plugins/testing/skills/testing-bundle/README.md`（若引用了示例，同步链接）

### PR3 涉及文件（wechat-formatter 模块语法精简）

- Create: `plugins/wechat-formatter/skills/wechat-formatter/knowledge/module-syntax-examples.md`
- Modify: `plugins/wechat-formatter/skills/wechat-formatter/SKILL.md`（移出语法示例 + 保留 1 个精简示例）

### PR4 涉及文件（文档同步）

- Modify: `plugins/testing/skills/test-case-engineer/test-case-engineer-core.md`（2 处「6 维度」→「9 维度」）

---

## PR1：test-case-engineer-core 拆分

**分支**：`refactor/test-case-engineer-core-split`（基于最新 main）
**目标**：core 从 9,699 → ~6,600 token（-32%），拆出 3 个 knowledge 文件
**预估变更**：~350 行（3 个新文件 ~250 行 + core 修改 ~100 行）

### 步骤

- [ ] **1.1 创建 knowledge/writing-iron-rules.md**
  - 从 test-case-engineer-core.md 第 476-583 行原样迁移「编写与审核铁律」全部内容
  - 文件开头加标题 `# 编写与审核铁律` 和说明 `> 从 test-case-engineer-core.md 拆分，阶段 3 编写用例时按需加载。`
  - 保留所有子小节：title 规范 / steps 规范 / expected_results 规范 / steps↔expected_results 对应 / 测试点→用例映射 / 用例拆分与合并策略 / 软断言说明

- [ ] **1.2 创建 knowledge/self-check-checklist.md**
  - 从 test-case-engineer-core.md 第 602-661 行原样迁移「阶段 4 失败模式与 Fallback」+「用例自检清单」
  - 文件开头加标题 `# 阶段 4 自检清单` 和说明 `> 从 test-case-engineer-core.md 拆分，阶段 4 自检时加载。`

- [ ] **1.3 创建 knowledge/exploration-mode.md**
  - 从 test-case-engineer-core.md 第 692-709 行原样迁移「模式切换」+「探索章程模板」
  - 文件开头加标题 `# 探索式模式` 和说明 `> 从 test-case-engineer-core.md 拆分，探索式模式触发时加载。`

- [ ] **1.4 修改 test-case-engineer-core.md**
  - 删除第 476-583 行（编写与审核铁律），替换为铁律速查表（~15 行）：
    ```
    ### 编写与审核铁律（速查）

    > 完整规则见 [knowledge/writing-iron-rules.md](knowledge/writing-iron-rules.md)

    | 字段 | 核心规则 |
    |------|---------|
    | title | `{被测对象} - {具体行为}`，动宾结构，含验证对象+行为+预期 |
    | steps | 主动语态，一步一动作，具体值，禁占位话术，≤7 步 |
    | expected_results | 可观察可判定，与 steps 一一对应，禁模糊词 |
    | 映射 | 同流程不同数据→合并参数化；不同前置/预期→拆分 |
    ```
  - 删除第 602-661 行（自检清单），替换为一行引用：
    ```
    ### 用例自检清单

    > 详见 [knowledge/self-check-checklist.md](knowledge/self-check-checklist.md)
    ```
  - 删除第 692-709 行（模式切换+探索章程），替换为：
    ```
    ## 模式切换

    - **默认**：不允许跳过阶段 1/2 直接写完整用例
    - **快速**：压缩阶段 1/4，但必须输出测试点清单，文首声明未做完整理解与自检
    - **探索式**：额外输出探索章程，详见 [knowledge/exploration-mode.md](knowledge/exploration-mode.md)
    - **评审**：独立于四阶段生成流程，对他人/已有用例做 9 维度评审（详见 [knowledge/review-mode.md](knowledge/review-mode.md)）
    ```
  - 注意：第 697 行的「6 维度」同步改为「9 维度」（PR4 的内容合并到此 PR 避免冲突）

- [ ] **1.5 修改 SKILL.md 知识库索引表**
  - 在 knowledge 索引表中新增 3 行：
    - `writing-iron-rules.md | 编写与审核铁律 | 阶段 3 按需加载`
    - `self-check-checklist.md | 阶段 4 自检清单 | 阶段 4 加载`
    - `exploration-mode.md | 探索式模式模板 | 探索式模式加载`

- [ ] **1.6 修改 README.md 知识库索引**
  - 同步 SKILL.md 的 knowledge 索引表更新

- [ ] **1.7 验证**
  - 运行 `wc -l test-case-engineer-core.md` 确认行数从 719 降至 ~580
  - 运行 `wc -m test-case-engineer-core.md` 确认字符数下降约 32%
  - 全文搜索「writing-iron-rules」「self-check-checklist」「exploration-mode」确认链接路径正确
  - 全文搜索「6 维度」确认已全部改为「9 维度」

### 验收标准

- [ ] test-case-engineer-core.md token 下降 ≥30%
- [ ] 3 个新 knowledge 文件内容与原文一致（无遗漏、无改写）
- [ ] core 中保留的铁律速查表覆盖 title/steps/expected_results/映射 4 个核心维度
- [ ] 所有链接路径正确（相对路径 `knowledge/xxx.md`）
- [ ] 无「6 维度」遗留

### 回滚方案

若拆分后用例质量下降（如铁律未被引用导致步骤不规范）：
1. `git revert` 回滚本 PR
2. 或在 core 中扩充铁律速查表（从 15 行扩到 30 行，覆盖更多规则）

---

## PR2：testing-bundle 示例外迁

**分支**：`refactor/testing-bundle-examples-split`（基于最新 main）
**目标**：SKILL.md 从 8,377 → ~6,100 token（-27%）
**预估变更**：~250 行（新文件 ~130 行 + SKILL.md 修改 ~120 行）

### 步骤

- [ ] **2.1 创建 knowledge/usage-examples.md**
  - 从 testing-bundle/SKILL.md 第 291-408 行原样迁移示例 1-8 全部内容
  - 文件开头加标题 `# 使用示例` 和说明 `> 从 SKILL.md 拆分，8 个典型场景的路由与协同示例。`
  - 保留所有示例的代码块和 CHECKPOINT 标注

- [ ] **2.2 修改 SKILL.md**
  - 删除第 291-408 行（示例 1-8），替换为：
    ```
    ## 使用示例

    > 完整示例见 [knowledge/usage-examples.md](knowledge/usage-examples.md)

    **示例索引**：

    | # | 场景 | 路由/链路 | 关键 CHECKPOINT |
    |---|------|----------|----------------|
    | 1 | Bug 根因分析 | → bug-analyzer | 无（单 skill） |
    | 2 | Bug + 用例协同 | 链 1 | bug-analyzer 完成后转交 |
    | 3 | 意图不明确 | 追问用户 | 强制追问 |
    | 4 | 测试策略 | → strategy | 无（单 skill） |
    | 5 | 性能测试方案 | → performance | 阶段 2 后 |
    | 6 | 策略 + 用例协同 | 链 2 | strategy 完成后转交 |
    | 7 | 状态机建模 | → state-machine | 无（单 skill） |
    | 8 | 状态机 + 用例协同 | 链 5 | state-machine 完成后转交 |

    **核心示例（链 1 协同）**：

    ```
    用户：分析这个重复扣款 Bug 的根因，并补充测试用例防止再次出现

    testing-bundle:
      → 意图判断：混合（分析 + 生成）
      → 路由到 bug-analyzer 执行根因分析
      → bug-analyzer 输出防御性测试点清单

    🔴 CHECKPOINT · bug-analyzer 完成：防御性测试点清单必须展示给用户确认，用户可修改清单或终止流程，确认后才转交 test-case-engineer。

      → 转交 test-case-engineer 基于清单生成完整用例
      → 输出根因分析报告 + 完整测试用例
    ```
    ```

- [ ] **2.3 检查 README.md 引用**
  - 若 testing-bundle/README.md 引用了 SKILL.md 的示例，更新链接指向 knowledge/usage-examples.md

- [ ] **2.4 验证**
  - 运行 `wc -l SKILL.md` 确认行数从 427 降至 ~330
  - 确认示例索引表 8 行覆盖全部原示例
  - 确认保留的核心示例（链 1）含 CHECKPOINT 标注

### 验收标准

- [ ] SKILL.md token 下降 ≥25%
- [ ] 示例索引表覆盖全部 8 个原示例
- [ ] 保留 1 个核心示例（链 1）含完整 CHECKPOINT
- [ ] knowledge/usage-examples.md 内容与原文一致

### 回滚方案

若用户反馈找不到示例：
1. 扩充 SKILL.md 示例索引表，为每个示例增加一行触发关键词
2. 或恢复 2-3 个高频示例到 SKILL.md

---

## PR3：wechat-formatter 模块语法精简

**分支**：`refactor/wechat-formatter-syntax-split`（基于最新 main）
**目标**：SKILL.md 从 5,833 → ~5,300 token（-9%）
**预估变更**：~60 行（新文件 ~30 行 + SKILL.md 修改 ~30 行）

### 步骤

- [ ] **3.1 创建 knowledge/module-syntax-examples.md**
  - 从 SKILL.md 第 148-171 行原样迁移模块语法示例（hero/steps/verdict 3 个示例）
  - 文件开头加标题 `# 模块语法示例` 和说明 `> 从 SKILL.md 拆分，:::module 语法的完整示例参考。`
  - 补充 2-3 个额外示例（从 layout/layout-modules.md 摘取 cards/cta/quote 模块），使参考更完整

- [ ] **3.2 修改 SKILL.md**
  - 删除第 148-171 行（模块语法示例），替换为：
    ```
    ### 模块语法速查

    ```markdown
    :::hero
    eyebrow: 深度观察
    title: 高级排版服务阅读决策
    subtitle: 主题决定气质，模块决定读者能不能看懂
    :::
    ```

    > 更多模块示例（steps/verdict/cards/cta/quote 等）见 [knowledge/module-syntax-examples.md](knowledge/module-syntax-examples.md)
    > 完整模块规范：[layout/layout-modules.md](layout/layout-modules.md)
    > 模块 CSS 样式：[layout/modules-base.css](layout/modules-base.css)
    ```

- [ ] **3.3 验证**
  - 运行 `wc -l SKILL.md` 确认行数从 296 降至 ~285
  - 确认保留的 hero 示例可独立说明 :::module 语法基本结构
  - 确认链接路径正确

### 验收标准

- [ ] SKILL.md token 下降 ≥8%
- [ ] 保留 1 个最简示例（hero）说明 :::module 语法
- [ ] knowledge/module-syntax-examples.md 含 ≥5 个模块示例
- [ ] 4 件事原则表 + 9 大类模块速览表保留在 SKILL.md

### 回滚方案

风险极低，无需回滚预案。若需要可恢复原文。

---

## PR4：文档维度数同步

**分支**：`fix/review-dimension-sync`（基于最新 main）
**目标**：消除「6 维度」遗留，统一为「9 维度」
**预估变更**：~5 行

> **注意**：若 PR1 先合并且已包含第 697 行的修正，则 PR4 仅需处理第 715 行。建议 PR1 先合并。

### 步骤

- [ ] **4.1 全局搜索「6 维度」**
  - 在 `plugins/testing/skills/test-case-engineer/` 目录下搜索「6 维度」
  - 记录所有命中位置

- [ ] **4.2 修正**
  - 将所有「6 维度评审」改为「9 维度评审」
  - 若有「6 维度」指代其他含义（非评审维度），不动

- [ ] **4.3 验证**
  - 再次搜索「6 维度」确认无遗留（评审语境下）
  - 搜索「9 维度」确认与 review-mode.md 一致

### 验收标准

- [ ] test-case-engineer 目录下无「6 维度评审」遗留
- [ ] 与 review-mode.md 的 9 维度表述一致

---

## 风险评估

### 整体风险矩阵

| PR | 风险等级 | 风险描述 | 缓解措施 |
|---|---|---|---|
| PR1 | 中 | 铁律拆出后阶段 3 引用不及时，用例质量下降 | core 保留速查表（4 维度核心规则）+ 完整规则链接 |
| PR2 | 低 | 用户找不到示例 | 保留示例索引表 + 1 个核心示例 |
| PR3 | 极低 | 模块语法参考不便 | 保留 hero 示例 + 指向 layout-modules.md 的现有链接 |
| PR4 | 极低 | 无 | - |

### PR 顺序建议

1. **PR4 先行**（或与 PR1 合并）：修正维度数，避免 PR1 修改同一行时冲突
2. **PR1**：收益最大（-32%），但风险中等，需重点验证
3. **PR2**：收益次之（-27%），风险低
4. **PR3**：收益最小（-9%），风险极低，可最后或与 PR2 并行

### 不改动的 skill（已评估，无需优化）

| Skill | token | 不改理由 |
|---|---|---|
| performance-test-engineer | 4,028 | 最轻，已足够精简 |
| test-strategy-engineer | 4,547 | 五阶段线性流程，拆分破坏连贯性 |
| bug-analyzer | 4,969 | 五步定位法线性流程，不宜拆分 |
| state-machine-test-engineer | 4,970 + 3,834 | 双文件结构合理，行业模板已按需加载 |
| change-impact-analyzer | 5,969 | 四阶段线性流程，不宜拆分 |

---

## 预期总体效果

| 指标 | 现状 | 执行 PR1-3 后 | 变化 |
|---|---|---|---|
| test-case-engineer-core | 9,699 token | ~6,600 token | -32% |
| testing-bundle SKILL.md | 8,377 token | ~6,100 token | -27% |
| wechat-formatter SKILL.md | 5,833 token | ~5,300 token | -9% |
| **入口 token 总量** | **~54,200** | **~44,900** | **-17%** |

**附加收益**：
- 拆出的 knowledge 文件可被其他 skill 复用（如 writing-iron-rules.md 可被评审模式引用）
- 文档结构更清晰：核心流程 vs 规则集 vs 模板 vs 示例分离
- 维度数一致性消除用户困惑

---

## 验证清单（所有 PR 合并后）

- [ ] 运行 `wc -m` 对比拆分前后 3 个入口文件的字符数
- [ ] 全局搜索「6 维度」确认无遗留
- [ ] 全局搜索拆出的 knowledge 文件名，确认链接路径正确
- [ ] 更新 README.md 的 Token 消耗分析表（行数与 token 估值）
- [ ] 更新 docs/project-structure.md（若 knowledge 文件数变化）

---

## 附录：Token 估算方法论

- 中文混合 token 估算：字符数 × 0.55
- 入口文件：SKILL.md / core 文件，每次调用必加载
- 全量文件：skill 目录下所有 .md/.txt 文件，knowledge 按需加载
- 估算值非精确测量，用于横向对比与趋势判断
