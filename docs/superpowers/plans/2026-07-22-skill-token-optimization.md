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

## PR5：表述风格重构（教学式 → 指令式）

**分支**：`refactor/skill-expression-style`（基于 PR1-3 合并后的 main）
**目标**：3 个高 token skill 入口文件再压缩 20-30%，预期入口 token 总量从 ~44,900 降至 ~36,000（-20%）
**前置条件**：PR1-3 已合并（PR5 在拆分后的文件上操作，避免冲突）
**预估变更**：~400 行（3 个文件修改，每个 ~130 行）
**风险**：高——直接改写表述可能影响 AI 输出质量，**必须**严格前后评测

> **核心约束**：本 PR 是唯一涉及"改写内容"而非"迁移内容"的 PR。PR1-3 是物理移动（不改逻辑），PR5 是表述重构（改写句子）。因此 PR5 **强制要求** darwin-skill 前后评测，达标方可合并。

### 重构规则

**转换原则**：把"给新手看的解释"改为"给熟练工下的指令"。

| 维度 | 教学式（现状） | 指令式（目标） | 压缩比 |
|---|---|---|---|
| 解释"为什么" | "测试点提取是基础，因为只有准确识别才能保证覆盖度" | 删除，直接给指令 | -100% |
| 描述性段落 | "在阶段 2 中，AI 需要扫描需求文档并提取测试点" | "阶段 2：扫描需求，按 4 类提取测试点" | -50% |
| 规则表述 | "标题应该包含被测对象和具体行为，这样执行人员能快速识别" | "title = `{被测对象} - {具体行为}`" | -60% |
| 示例说明 | "例如，如果我们测试登录功能，标题可以写成「登录-手机号错误密码-提示错误」" | 保留示例但删除"例如如果我们"引导语 | -30% |
| 过渡句 | "接下来进入阶段 3，在这个阶段中" | "阶段 3：" | -80% |

**不重构的部分**（保持原样）：
- 判定规则的正则/阈值（机器可校验部分，改了影响准确性）
- CHECKPOINT 标注（流程控制标记，不是表述）
- 失败模式表（已是指令式结构化表格）
- 模板代码块（已是结构化输出）

### 强制评测流程

> **不可跳过**：PR5 的每个 skill 改动**必须**走完整评测流程，缺一不可。评测工具为 darwin-skill（结果记录于 `.claude/skills/darwin-skill/results.tsv`）。

```
Step 0: Baseline 评测（改动前）
  ↓
Step 1-N: 表述重构
  ↓
Step N+1: 改动后评测
  ↓
Step N+2: 性能对比报告
  ↓
Step N+3: 结论判定（达标→合并 / 不达标→revert）
```

#### Step 0：Baseline 评测（改动前）

在 PR1-3 合并后的 main 上，对 3 个待改动 skill 各跑一次 darwin-skill baseline：

```bash
# 每个 skill 单独评测，记录 baseline 分数
darwin-skill eval --skill test-case-engineer --mode full_test
darwin-skill eval --skill testing-bundle --mode full_test
darwin-skill eval --skill wechat-formatter --mode full_test
```

**记录**：将 3 个 baseline 分数填入下表，作为对比基准。

| Skill | baseline 分数 | 评测维度 | commit | 日期 |
|---|---|---|---|---|
| test-case-engineer | ___ | 待填 | PR1-3 合并后 main | ___ |
| testing-bundle | ___ | 待填 | PR1-3 合并后 main | ___ |
| wechat-formatter | ___ | 待填 | PR1-3 合并后 main | ___ |

> 若 baseline 分数低于 75，说明 PR1-3 拆分已导致质量下降，**暂停 PR5**，先排查 PR1-3 的问题。

#### Step 1-N：表述重构

按"重构规则"逐 skill 改写，每个 skill 独立提交（不混合改）：

- [ ] **5.1 test-case-engineer-core.md 重构**
  - 按"重构规则"表逐段改写教学式表述为指令式
  - 不触碰判定规则的正则/阈值、CHECKPOINT 标注、失败模式表、模板代码块
  - 改完后 `wc -m` 确认字符数下降 ≥20%

- [ ] **5.2 testing-bundle/SKILL.md 重构**
  - 同上规则
  - 改完后 `wc -m` 确认字符数下降 ≥20%

- [ ] **5.3 wechat-formatter/SKILL.md 重构**
  - 同上规则
  - 改完后 `wc -m` 确认字符数下降 ≥20%

#### Step N+1：改动后评测

对 3 个改动后的 skill 各跑一次 darwin-skill 评测 + dual_judge 验证：

```bash
# 改动后评测（full_test + dual_judge 双 judge 验证）
darwin-skill eval --skill test-case-engineer --mode full_test
darwin-skill eval --skill test-case-engineer --mode dual_judge

darwin-skill eval --skill testing-bundle --mode full_test
darwin-skill eval --skill testing-bundle --mode dual_judge

darwin-skill eval --skill wechat-formatter --mode full_test
darwin-skill eval --skill wechat-formatter --mode dual_judge
```

**dual_judge 阈值**：两次 judge 分数差 Δ < 2 视为一致，取低分；Δ ≥ 2 需人工裁决。

#### Step N+2：性能对比报告

输出以下格式的对比报告，**作为 PR 描述的必填部分**：

```markdown
## PR5 性能对比报告

### 1. test-case-engineer

| 维度 | Baseline | 改动后 | Δ | 判定 |
|---|---|---|---|---|
| 总分 | ___ | ___ | ___ | ___ |
| 可执行具体性 | ___ | ___ | ___ | ___ |
| 工作流清晰度 | ___ | ___ | ___ | ___ |
| 整体架构 | ___ | ___ | ___ | ___ |
| （其他维度） | ___ | ___ | ___ | ___ |

**token 变化**：___ → ___（-___%）
**dual_judge**：Δ = ___（< 2 一致 / ≥ 2 需裁决）

### 2. testing-bundle
（同上格式）

### 3. wechat-formatter
（同上格式）

### 总结

| Skill | Baseline | 改动后 | Δ | token 变化 | 结论 |
|---|---|---|---|---|---|
| test-case-engineer | ___ | ___ | ___ | -___% | 提升/持平/下降 |
| testing-bundle | ___ | ___ | ___ | -___% | 提升/持平/下降 |
| wechat-formatter | ___ | ___ | ___ | -___% | 提升/持平/下降 |
```

#### Step N+3：结论判定

**合并标准**（3 个 skill 均须满足）：

| 条件 | 阈值 | 不满足则 |
|---|---|---|
| 改动后总分 ≥ baseline - 2 | 允许 2 分误差（与 dual_judge 阈值对齐） | 该 skill **revert**，不合并 |
| token 下降 ≥ 20% | 达不到压缩目标无意义 | 该 skill **revert** |
| dual_judge Δ < 2 | 评测一致性保障 | 需人工裁决后决定 |

**结论分类**：

| 情况 | 处理 |
|---|---|
| 3 个 skill 全部达标 | PR5 整体合并 |
| 部分 skill 达标 | 拆分 PR：达标的 skill 单独合并，不达标的 revert |
| 全部不达标 | PR5 整体放弃，记录失败原因到 results.tsv，结论："表述风格重构对当前 skill 质量有负面影响，不推荐" |

### 验收标准

- [ ] 3 个 skill 均有 baseline 评测记录（results.tsv）
- [ ] 3 个 skill 均有改动后评测 + dual_judge 记录（results.tsv）
- [ ] 性能对比报告已填入 PR 描述
- [ ] 每个达标 skill：总分 Δ ≥ -2 且 token 下降 ≥ 20%
- [ ] 不达标 skill 已 revert 并记录失败原因

### 回滚方案

若改动后质量下降超标：
1. `git revert` 回滚对应 skill 的改动
2. 在 results.tsv 记录：`status=drop, note=表述重构导致质量下降Δ__分，revert`
3. 分析下降维度，判断是否部分表述不宜改指令式（如某些解释性内容对 AI 理解确实有帮助）

---

## 风险评估

### 整体风险矩阵

| PR | 风险等级 | 风险描述 | 缓解措施 |
|---|---|---|---|
| PR1 | 中 | 铁律拆出后阶段 3 引用不及时，用例质量下降 | core 保留速查表（4 维度核心规则）+ 完整规则链接 |
| PR2 | 低 | 用户找不到示例 | 保留示例索引表 + 1 个核心示例 |
| PR3 | 极低 | 模块语法参考不便 | 保留 hero 示例 + 指向 layout-modules.md 的现有链接 |
| PR4 | 极低 | 无 | - |
| PR5 | **高** | 改写表述导致 AI 输出质量下降 | **强制** darwin-skill 前后评测，总分 Δ ≥ -2 且 token -20% 方可合并，否则 revert |

### PR 顺序建议

1. **PR4 先行**（或与 PR1 合并）：修正维度数，避免 PR1 修改同一行时冲突
2. **PR1**：收益最大（-32%），但风险中等，需重点验证
3. **PR2**：收益次之（-27%），风险低
4. **PR3**：收益最小（-9%），风险极低，可最后或与 PR2 并行
5. **PR5 最后**（依赖 PR1-3 合并）：表述风格重构，高风险，**必须** darwin-skill 前后评测达标方可合并

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

| 指标 | 现状 | 执行 PR1-3 后 | 执行 PR5 后（若达标） |
|---|---|---|---|
| test-case-engineer-core | 9,699 token | ~6,600 token（-32%） | ~5,300 token（-45%） |
| testing-bundle SKILL.md | 8,377 token | ~6,100 token（-27%） | ~4,900 token（-42%） |
| wechat-formatter SKILL.md | 5,833 token | ~5,300 token（-9%） | ~4,200 token（-28%） |
| **入口 token 总量** | **~54,200** | **~44,900**（-17%） | **~36,000**（-34%） |

> **PR5 前提**：上表"执行 PR5 后"列仅当 darwin-skill 评测达标（总分 Δ ≥ -2）时成立。若 PR5 评测不达标，总体效果停留在 PR1-3 的 -17%。

**附加收益**：
- 拆出的 knowledge 文件可被其他 skill 复用（如 writing-iron-rules.md 可被评审模式引用）
- 文档结构更清晰：核心流程 vs 规则集 vs 模板 vs 示例分离
- 维度数一致性消除用户困惑
- PR5 若达标：验证了"指令式表述对 AI 更高效"的假设，为后续新 skill 编写确立风格规范

---

## 验证清单（所有 PR 合并后）

- [ ] 运行 `wc -m` 对比拆分前后 3 个入口文件的字符数
- [ ] 全局搜索「6 维度」确认无遗留
- [ ] 全局搜索拆出的 knowledge 文件名，确认链接路径正确
- [ ] 更新 README.md 的 Token 消耗分析表（行数与 token 估值）
- [ ] 更新 docs/project-structure.md（若 knowledge 文件数变化）
- [ ] **PR5 专属**：results.tsv 中 3 个 skill 均有 baseline + 改动后 + dual_judge 记录
- [ ] **PR5 专属**：性能对比报告已归档（PR 描述或 docs/ 下独立文件）
- [ ] **PR5 专属**：不达标 skill 已 revert 并在 results.tsv 记录失败原因

---

## 附录：Token 估算方法论

- 中文混合 token 估算：字符数 × 0.55
- 入口文件：SKILL.md / core 文件，每次调用必加载
- 全量文件：skill 目录下所有 .md/.txt 文件，knowledge 按需加载
- 估算值非精确测量，用于横向对比与趋势判断
