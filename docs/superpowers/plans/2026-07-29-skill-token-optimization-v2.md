# Skill Token 优化实施计划 v2

> **状态**：2026-07-29 制定，基于当前仓库实测数据，取代 [2026-07-22 历史计划](2026-07-22-skill-token-optimization.md)。
> **最高原则**：**能力保护优先于 token 削减**——只外迁"事后参考材料"（教学示例、演示对话、快速上手），所有行为约束（铁律条文、CHECKPOINT、失败模式、路由规则）一律留守首轮加载，宁可少省 token 也不动摇 skill 执行质量。

**Goal:** 在不损伤 skill 能力的前提下，把可延迟加载的参考材料移出首轮路径，预期削减首轮负担合计 ~5,800 token（bundle -1,915、state-machine -1,258、test-case-engineer 默认模式 -1,400、change-impact -1,068、wechat -170）。

**Tech Stack:** Markdown（纯内容迁移，不改任何逻辑）

---

## 与旧计划（2026-07-22）的差异

| 旧计划前提 | 实测结果 | 结论 |
|---|---|---|
| review-mode.md ~14k token，评审首轮 ~21k | 实测 ~7,263 tok，评审首轮 ~11,980 | **误报**，review-mode 不再拆分 |
| core.md 第 697/715 行「6 维度」需修正（PR4） | 已是「10 维度」（PR #21 后已同步） | PR4 **作废** |
| 铁律区块 L476-583 整体外迁 writing-iron-rules.md | 铁律含大量**行为硬约束**（steps ≤7 步、一步一验、禁模糊词） | **改为只迁教学示例表**，条文全留（见下"能力保护红线"） |
| 未覆盖 change-impact-analyzer / state-machine | 实测 ~6,119 / ~5,534 tok，均属前 5 大入口 | **新增**处置项 |

## 实测基线（2026-07-29，chars × 0.55 估算）

**首轮加载负担**（skill 触发时必读的组合）：

| 组合 | token |
|---|---|
| test-case-engineer 默认模式 = SKILL.md + core.md | 12,056 |
| test-case-engineer 评审模式 = SKILL.md + review-mode + test-standards | 11,980 |
| testing-bundle 路由入口 | 7,395 |
| wechat-formatter 入口 | 6,257 |
| change-impact-analyzer 入口 | 6,119 |
| state-machine 入口（另有 core.md 伴生） | 5,534 |
| bug-analyzer / strategy / performance 入口 | 5,070 / 4,607 / 4,394 |
| test-case-engineer/SKILL.md（**全仓范本**：纯索引 + 模式读取矩阵） | 2,356 |

**候选外迁区块实测**：

| 区块 | 位置 | token | 性质判定 |
|---|---|---|---|
| bundle 8 个使用示例 | testing-bundle/SKILL.md L197-316 | ~1,313 | 演示对话，纯参考 → **可迁** |
| bundle 快速上手 | 同上 L317-335 | ~602 | 安装/首次体验引导 → **可迁** |
| state-machine 使用示例 | SKILL.md L244-297 | ~755 | 演示对话 → **可迁** |
| state-machine 快速上手 | 同上 L298-319 | ~503 | 同上 → **可迁** |
| core.md 铁律 3 个「行业优秀实践示例」表 | core.md L483-491 / L507-513 / L524-531 | ~1,400 | 教学对照示例（规则条文本身另算）→ **只迁示例表** |
| change-impact 阶段 3 交叉分析细则 | SKILL.md L222-293 | ~1,068 | 进入阶段 3 才需要 → **可迁** |
| wechat 模块语法示例代码块 | SKILL.md L152-178 | ~310 | layout-modules.md §二 已有权威版 → **删重复，留链接** |

## 能力保护红线（不可外迁清单）

以下内容直接决定输出质量，**必须留在首轮加载文件中**：

1. **铁律条文本体**：title/steps/expected_results 的所有"必须/禁止"规则、≤7 步约束、一步一验、模糊词黑名单、拆分/合并 5 步判断法
2. **所有 🛑 STOP / 🔴 CHECKPOINT**：位置和文字一字不动
3. **失败模式与 Fallback 表**：这是运行时兜底逻辑，不是参考材料
4. **bundle 路由规则 + 7 条混合意图链 + 消歧规则**：路由入口的本职
5. **wechat 排版输出约束（L233，~683 tok）与参考索引（L251，~771 tok）**：硬约束与导航
6. **review-mode.md 不动**：实测仅 7.3k，且已是按需加载文件，二次拆分只会增加评审时的文件跳转成本
7. **bug-analyzer / test-strategy / performance 三个线性流程 skill 不动**：4.4k-5.1k 属合理区间，拆线性流程破坏连贯性
8. 外迁后原位置**必须保留 1-3 行摘要 + 精确链接**，且新文件登记进 SKILL.md 的知识库索引/阅读矩阵

---

## PR1: testing-bundle 示例与快速上手外迁（-1,915 tok，风险最低）

**分支**：`refactor/bundle-examples-extract`，约 250 行变更

- [ ] 新建 `plugins/testing/skills/testing-bundle/knowledge/usage-examples.md`：整体迁入 L197-316「使用示例」（8 个）+ L317-335「快速上手」，内容原样不改
- [ ] SKILL.md 原位置替换为 ~4 行：每类示例 1 行"意图 → 路由结果"极简索引 + 链接 usage-examples.md
- [ ] 「失败模式与 Fallback」「反例与黑名单」「约束规则」全部保留（路由兜底逻辑）
- [ ] 更新 testing-bundle/CHANGELOG.md
- [ ] 验证：全仓链接扫描无断链；`python scripts/check-version-sync.py` 通过；test-prompts.json 全部触发场景与示例无关，无需改动

**预期**：bundle 入口 7,395 → ~5,480 tok

## PR2: state-machine 示例与快速上手外迁（-1,258 tok）

**分支**：`refactor/state-machine-examples-extract`，约 160 行变更

- [ ] 新建 `plugins/testing/skills/state-machine-test-engineer/knowledge/usage-examples.md`：迁入 L244-297「使用示例」+ L298-319「快速上手」
- [ ] SKILL.md 原位置留 2 行摘要 + 链接；「知识库」索引表登记新文件（"首次使用或想看演示对话时查阅"）
- [ ] 「反模式黑名单」「失败模式与 Fallback」「约束规则」「核心数据结构」全部保留
- [ ] 验证：同 PR1

**预期**：state-machine 入口 5,534 → ~4,280 tok

## PR3: core.md 教学示例表外迁（-1,400 tok，规则条文全留）

**分支**：`refactor/core-examples-extract`，约 200 行变更

- [ ] 新建 `plugins/testing/skills/test-case-engineer/knowledge/writing-examples.md`：只迁 3 个「行业优秀实践示例」表（title 好坏对照 L483-491、steps 好坏对照 L507-513、expected_results 好坏对照 L524-531）
- [ ] **铁律条文一条不动**：title/steps/expected 的全部"必须/禁止"规则、一一对应强制、拆分合并策略、5 步判断法、软断言说明留在 core.md 原位
- [ ] 每个示例表原位置留 1 行：`> 好/坏写法对照示例见 knowledge/writing-examples.md`（正文中为实际 markdown 链接）
- [ ] SKILL.md 知识库索引表 + 模式读取矩阵登记 writing-examples.md（"阶段 3 写用例拿不准格式时查阅"）
- [ ] 验证：同 PR1，另跑 frontmatter/description 长度检查

**预期**：core.md 9,700 → ~8,300；默认模式首轮 12,056 → ~10,650 tok

## PR4: change-impact-analyzer 阶段 3 细则外迁 + wechat 去重（-1,238 tok）

**分支**：`refactor/cia-wechat-slim`，约 220 行变更

- [ ] 新建 `plugins/testing/skills/change-impact-analyzer/knowledge/cross-analysis-guide.md`：迁入 L222-293「阶段 3：交叉分析」的操作细则；SKILL.md 保留阶段 3 的 8-10 行概览（输入/输出/步骤名）+ 链接，保证四阶段流程在入口仍完整可读
- [ ] 阶段 3 内若含 CHECKPOINT/失败模式行，保留在 SKILL.md 概览中不外迁
- [ ] 「知识库索引」登记新文件（"进入阶段 3 时必读"）
- [ ] wechat-formatter/SKILL.md L152-178 的 27 行语法示例代码块删除（layout/layout-modules.md §二 已有权威完整版），保留 L150 的格式说明与 L180-181 的两个链接
- [ ] 验证：同 PR1，另跑 wechat test-prompts 场景核对（语法示例不参与触发）

**预期**：change-impact 入口 6,119 → ~5,050；wechat 入口 6,257 → ~6,090 tok

---

## 不做清单（明确排除，防止过度优化）

| 候选项 | 排除原因 |
|---|---|
| 铁律条文整体外迁（旧计划 PR1 方案） | steps ≤7 步、一步一验、禁模糊词是**每次生成都生效的硬约束**，外迁后阶段 3 若漏读将直接产出劣质用例 |
| 阶段 4 自检清单外迁（~748 tok） | 自检是强制流程步骤，外迁增加漏检风险，且本身不大 |
| review-mode.md 拆分 | 实测 7.3k 非 14k，且已按需加载；拆分收益低、跳转成本高 |
| core.md 阶段 1/2 拆分 | 四阶段是线性主流程，拆开破坏连贯性 |
| bundle 失败模式表外迁（~1,030 tok） | 路由 fallback 是运行时逻辑 |
| bug-analyzer / strategy / performance 任何拆分 | 线性方法论 skill，体积合理 |
| wechat 排版输出约束/参考索引外迁 | 硬约束与导航本职 |

## 收益汇总与验证

| 指标 | 优化前 | 优化后（预期） |
|---|---|---|
| test-case-engineer 默认模式首轮 | 12,056 | ~10,650（-12%） |
| testing-bundle 入口 | 7,395 | ~5,480（-26%） |
| change-impact 入口 | 6,119 | ~5,050（-17%） |
| state-machine 入口 | 5,534 | ~4,280（-23%） |
| wechat 入口 | 6,257 | ~6,090（-3%） |

**每个 PR 的统一验证门槛**：

1. 全仓 Markdown 相对链接扫描 0 断链
2. `python scripts/check-version-sync.py` 通过
3. 迁移前后新旧文件内容 diff 逐段核对 = 纯移动、零改写
4. 对应 skill 的 test-prompts.json 触发场景逐条核对不受影响
5. 外迁材料在 SKILL.md 知识库索引/阅读矩阵中有明确的"何时查阅"条目

**执行顺序**：PR1 → PR2 → PR3 → PR4（按风险从低到高；PR1/PR2 是纯示例迁移可先行验证模式，PR3/PR4 涉及主流程文件放后）。每个 PR 独立分支基于最新 main，< 400 行，Conventional Commits（中文）。
