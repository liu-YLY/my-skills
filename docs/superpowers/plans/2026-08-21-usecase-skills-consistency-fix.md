# 用例相关 Skill 一致性修复计划

> **状态**：2026-08-21 制定，依据 [用例相关 Skill 家族全面审查报告](../../skill-evaluation/reports/usecase-skills-family-review-2026-08-21.md)。
> **最高原则**：**逐批次修复，每批次验证达标并经用户确认后才进入下一批次**。单批次不达标不推进，禁止跳批。
> **分支**：`fix/usecase-skills-consistency`（从 main 创建）

**Goal:** 消除审查发现的数值口径漂移、分层映射断点、版本同步滞后与文档术语债，使 4 个用例相关 skill 的跨文件数值与口径完全一致。

**Tech Stack:** Markdown（文档级修复为主，不涉及逻辑代码改动；state-machine MCP 批次除外）

---

## 修复范围与优先级总览

| 批次 | Skill | 主题 | 优先级 | 规模 |
|---|---|---|---|---|
| 1 | test-strategy-engineer | 数值口径统一 + 分档维度错位修复 | P0 | ~60 行 |
| 2 | test-case-engineer | 分层映射约定 + 版本同步 + 残留清理 | P0+P1 | ~30 行 |
| 3 | testing-bundle | 术语与架构图更新 + 裁定/消解规则补全 | P3 | ~40 行 |
| 4（待定） | state-machine-test-engineer | MCP v0.2.0 端到端联调 | P1 | 代码工程，量大，开工前单独确认 |

暂缓项（本次不做，列入观察）：P2 模糊词清单统一、ID 生成规则去重、产品知识库真实数据沉淀。理由：P0 修完前不扩面。

---

## 批次 1：test-strategy-engineer 数值口径统一（P0）

### 问题清单（行级定位）

| # | 冲突 | 位置 A | 位置 B（权威源） |
|---|---|---|---|
| 1-1 | 用例执行率：准出 100% vs ≥95% | strategy-templates.md L131 | entry-exit-criteria.md L37（≥95%）+ L69-72 分档（金融≥98%/内部≥90%） |
| 1-2 | 单元覆盖率：准出 ≥80% vs 权威源为**准入项**且分档 | strategy-templates.md L134 | entry-exit-criteria.md L13（准入 ≥70%，核心≥80%）+ L67-72 分档 |
| 1-3 | 分层比例："7:2:1" 点值 vs 区间 | SKILL.md L102 | test-pyramid.md L12-14（单元 60-70/接口 20-30/UI 5-10） |
| 1-4 | **分档维度错位**（审查新发现） | SKILL.md L101-104 按**项目生命周期**（新/迭代/重构/迁移）选形状（金字塔/橄榄/倒金字塔/沙漏） | test-pyramid.md §3 按**技术栈**（后端/前端/全栈/微服务/遗留）给比例——两套正交维度并存，未声明关系 |
| 1-5 | 复制副本（数值暂未漂移但有漂移风险） | strategy-templates.md §2（L58-86 复制 risk-matrix 评分表+等级映射）、§3（L92-106 复制 test-pyramid 分档表+职责边界） | 源文件各自章节 |

### 改动方案

**A. strategy-templates.md（主战场）**：
1. L131：`测试用例执行率 100%` → `测试用例执行率 ≥ 95%（按项目类型分档，见 entry-exit-criteria.md §3）`
2. L134：删除 `单元测试覆盖率 ≥ 80%（或项目约定阈值）` 一行（权威源中单元覆盖率是准入项，非准出项），checklist 其余行与 entry-exit-criteria.md §2 对齐
3. §2、§3 的复制表替换为"精确引用 + 链接"（如"5 维评分表见 [risk-matrix-framework.md](risk-matrix-framework.md) §1，数值以源文件为准"），消除第二副本
4. §3 选择规则"比例为区间中值"表述与 test-pyramid.md §3 档位规则（"偏差不得超过 ±5%"）对齐

**B. SKILL.md**：
1. L102 `7:2:1` → 区间表述 `单元 60-70% / 接口 20-30% / UI 5-10%（以 test-pyramid.md 为准）`
2. 阶段 3 动作 1 补充一句维度关系声明：**形状由项目生命周期决定，具体比例数值由技术栈分档表决定，两者正交组合**（先按生命周期定形状倾向，再按技术栈查表定比例）

**C. test-pyramid.md**：
1. §3 开头补一行说明，声明"本表按技术栈分档；项目生命周期（新/迭代/重构/迁移）决定形状倾向，见 SKILL.md 阶段 3"，闭合双向引用

### 验收标准

- [ ] `grep -n "100%" strategy-templates.md` 无准出执行率 100% 残留
- [ ] `grep -n "7:2:1" SKILL.md` 无结果
- [ ] strategy-templates.md 中不再存在 risk-matrix-framework.md / test-pyramid.md 的整表复制（仅引用+链接）
- [ ] 准出 checklist 每一项都能在 entry-exit-criteria.md §2 中找到口径一致的对应项
- [ ] `python scripts/check-md-links.py` 通过（无断链）
- [ ] `python scripts/check-skill-consistency.py` 通过

---

## 批次 2：test-case-engineer 映射与同步修复（P0-2 + P1）

### 问题清单

| # | 问题 | 位置 |
|---|---|---|
| 2-1 | strategy 三层（单元/接口/UI）→ case 五层（单元/集成/API/契约/E2E）无映射约定，"接口 30%"如何拆给集成/API/契约三层无规则 | test-levels.md（case 侧分层权威文件） |
| 2-2 | case 内部 test-levels.md 五层与 writing-rules.md 四层（L1/L2-A/L2-B/L3 带占比）关系未声明 | 同上 |
| 2-3 | test-prompts.json version 8.5.0 滞后于 SKILL.md 8.6.0 | test-prompts.json L3 |
| 2-4 | bug-patterns.md L123 残留"bug-analyzer 步骤 2 隔离阶段必查此表"，与 v8.0.0 边界声明冲突 | bug-patterns.md L121-170 |

### 改动方案

**A. test-levels.md**：新增一节"与上游/内部分层体系的映射"：
1. strategy 三层 → case 五层映射表：单元→单元；接口→集成+API+契约（三层合计承接 strategy 的"接口"占比）；UI/E2E→E2E/验收
2. case 内部关系声明：writing-rules.md 的 L1/L2-A/L2-B/L3 是本文件五层的**用例编排分组视角**（L1=单元、L2-A=集成/API 业务场景、L2-B=API/契约接口契约、L3=E2E），占比为编排目标非分层硬约束
3. 声明优先级：接收上游 strategy 比例时按映射表换算；无上游输入时按 writing-rules.md 编排策略

**B. test-prompts.json**：L3 `"version": "8.5.0"` → `"8.6.0"`

**C. bug-patterns.md**：L123 一行的"bug-analyzer 步骤 2 隔离阶段"表述改为 case-engineer 自身视角（如"阶段 2 提取测试点时，当被测功能错误现象为 NPE/500/超时类历史缺陷高发区时必查此表"），消除跨 skill 残留引用

### 验收标准

- [ ] `grep -n '"version"' test-prompts.json` 输出 8.6.0
- [ ] `grep -n "bug-analyzer" bug-patterns.md` 无残留
- [ ] test-levels.md 映射表覆盖 strategy 全部三层，且"接口层"拆分去向明确
- [ ] `python scripts/check-version-sync.py` 通过
- [ ] `python scripts/check-md-links.py` + `python scripts/check-knowledge-count.py` 通过

---

## 批次 3：testing-bundle 术语与规则补全（P3）

### 问题清单

| # | 问题 | 位置 |
|---|---|---|
| 3-1 | "5-way" 术语过时（v3.1.0 后实际 6 路） | usage-examples.md L130、SKILL.md 架构图 L51-61、README.md |
| 3-2 | change-impact-analyzer 定位三处措辞不一（"第 6 个协同 skill" vs "6 个独立 skill" vs "随 plugin 整体安装"） | SKILL.md L25/L99、README.md L17、CHANGELOG.md |
| 3-3 | CHECKPOINT 与"直接交付模式"冲突无裁定规则 | SKILL.md（转交约束处） |
| 3-4 | "测试计划"路由歧义未消解 | SKILL.md 失败模式表 |

### 改动方案

1. 全部"5-way"表述统一为"6-way 路由（5 核心 + 1 协同）"；SKILL.md 架构图补 change-impact-analyzer 节点
2. change-impact-analyzer 定位统一为一句规范表述（建议："第 6 个协同 skill：随 plugin 整体安装，链 6 使用，也可单独使用"），三处对齐
3. 转交约束新增裁定规则：用户明确要求"直接交付/一次完成"时，链路转交 CHECKPOINT 降级为文末汇总确认（列出全部转交点与假设），冲突以用户明确指令优先
4. 失败模式表新增"测试计划"消解规则：含"项目级/分层/风险矩阵/准入准出"→ strategy；含"某功能/单功能"→ case-engineer；无法判定 → 追问

### 验收标准

- [ ] `grep -rn "5-way" skills/testing-bundle/` 无结果（历史 CHANGELOG 记录除外）
- [ ] `grep -rn "6 个" skills/testing-bundle/*.md skills/testing-bundle/knowledge/*.md` 定位表述全部一致
- [ ] SKILL.md 含"直接交付"裁定规则与"测试计划"消解规则
- [ ] `python scripts/check-md-links.py` + `python scripts/check-skill-consistency.py` 通过

---

## 批次 4（待定）：state-machine MCP v0.2.0 联调（P1）

**开工前需用户单独确认**（代码工程，非文档修复）：
- MCP 协议层端到端联调（FastMCP stdio 通道实跑）
- `build_state_machine` 去占位（builders.py L73-101）
- 解除 tests/integration/test_skill_integration.py 的 `pytest.mark.skip`
- SKILL.md/README.md 三处 MCP 状态声明措辞统一

验收标准（预案）：`pytest tests/` 全绿（含集成测试）；skill 输出可切增强模式标记 `✓ MCP 增强模式`。

---

## 流程约束（每批次必须遵守）

1. **验证达标 + 用户确认后才进入下一批次**；不达标先修复本批次
2. 每批次一个原子 commit，Conventional Commits 规范（`fix(strategy): ...` / `fix(case-engineer): ...` / `docs(bundle): ...`）
3. 单 PR ≤ 400 行，超限拆分
4. 只改功能变更所需行，禁止顺手格式化无关代码
5. 提交前跑通：`python scripts/check-md-links.py`、`check-version-sync.py`、`check-knowledge-count.py`、`check-skill-consistency.py`
6. 全部批次完成后统一推送并发起 PR（squash merge）

## 进度记录

| 批次 | 状态 | 完成日期 | 验证结果 |
|---|---|---|---|
| 1 | 已完成 | 2026-08-21 | grep 无 7:2:1/执行率 100% 残留（含 quickstart.md 两处追加发现）；复制表全部去重；4 个一致性脚本全过 |
| 2 | 已完成 | 2026-08-21 | test-prompts.json 8.6.0；bug-patterns.md 无 bug-analyzer 残留；test-levels.md 映射表覆盖 strategy 三层且接口层拆分去向明确（SKILL.md 索引行补映射可发现性）；JSON 合法性验证过；4 个一致性脚本全过 |
| 3 | 已完成 | 2026-08-21 | "5-way"清零（CHANGELOG 历史记录保留）；架构图补 change-impact-analyzer 第 6 路节点（图文一致）；定位表述三处统一"链 6 协同使用，亦可单独使用"；MCP 状态声明三处口径统一为"协议层注册代码已实现但尚未端到端联调验证"；新增"直接交付 vs CHECKPOINT"裁定规则（失败模式表 + 约束规则 5 双覆盖）与"测试计划"消解规则；4 个一致性脚本全过 |
| 4 | 待确认 | — | — |
