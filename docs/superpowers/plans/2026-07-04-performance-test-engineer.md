# Testing Skills 扩展实现计划（Phase 2: performance-test-engineer）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 performance-test-engineer skill v1.0.0（性能测试方案设计 + 瓶颈定位），并用 darwin-skill 自动优化到 85+ 分。

**Architecture:** 按 spec Section 2 创建独立 skill 目录（4 个知识库文件 + SKILL.md + README.md + quickstart.md + test-prompts.json），完成后跑 darwin-skill 基线评估 → 优化循环 → 双 judge 确认。不与 bug-analyzer 共享知识库（层边界隔离）。

**Tech Stack:** Markdown（skill 内容）、JSON（test-prompts）、darwin-skill（评估优化）、git（ratchet）。

**Spec 来源:** [docs/superpowers/specs/2026-07-04-testing-skills-expansion-design.md](../specs/2026-07-04-testing-skills-expansion-design.md) Section 2

**项目约束（来自 project_memory）:**
- 关键决策需 darwin-skill 双 judge 验证
- README.md 必须与 SKILL.md 同步（避免触发 dim7 惩罚）
- Quickstart.md 必须用正确的 SKILL_ROOT 路径（skills/[skill-name] 不是 .cursor/skills/[skill-name]）
- 每个 skill 维护独立 test-prompts.json

---

## File Structure

```
plugins/testing/skills/performance-test-engineer/
├── SKILL.md                      # 主入口 + 工作流 + 路由规则
├── README.md                     # 与 SKILL.md 同步的概览
├── knowledge/
│   ├── load-models.md            # 负载模型（阶梯/峰值/疲劳/容量）选择决策
│   ├── metrics-framework.md      # 指标体系 + 阈值参考表
│   ├── bottleneck-patterns.md    # 瓶颈模式库（CPU/IO/网络/锁/连接池/GC）
│   └── use-method.md             # USE 方法 + 资源三角
├── integrations/
│   └── quickstart.md             # 快速上手 + SKILL_ROOT 说明
└── test-prompts.json             # darwin-skill dim8 实测用
```

**职责边界:**
- `SKILL.md` — 入口、scope、4 阶段工作流、与 bug-analyzer 的层边界、CHECKPOINT、失败模式、反例黑名单（dim9 必需）
- `knowledge/*.md` — 方法论细节，被 SKILL.md 引用，独立可读
- `test-prompts.json` — 3 个典型场景（happy path + 复杂场景 + 瓶颈定位）
- `README.md` — SKILL.md 的精简镜像，供 marketplace 展示

---

## Task 1: 预检与分支准备

**Files:**
- 无文件改动，仅 git 操作

- [ ] **Step 1: 确认当前分支与工作树状态**

Run:
```bash
git status
git branch --show-current
```
Expected: 当前分支 `refactor/split-test-engineer`，工作树干净（spec 文档已提交为 a36bac2）。

- [ ] **Step 2: 创建性能测试专用分支**

Run:
```bash
git checkout -b feat/performance-test-engineer
```
Expected: 切换到新分支 `feat/performance-test-engineer`。

- [ ] **Step 3: 创建目录骨架**

Run:
```bash
mkdir -p plugins/testing/skills/performance-test-engineer/knowledge
mkdir -p plugins/testing/skills/performance-test-engineer/integrations
```
Expected: 目录创建成功。

- [ ] **Step 4: 提交空骨架**

Run:
```bash
git add plugins/testing/skills/performance-test-engineer/
git commit -m "chore(performance-test-engineer): 创建 skill 目录骨架"
```
Expected: commit 成功。

---

## Task 2: 知识库 — load-models.md

**Files:**
- Create: `plugins/testing/skills/performance-test-engineer/knowledge/load-models.md`

**内容大纲（实现时按此结构填充）:**
- 4 种负载模型定义：阶梯递增（ramp-up）、峰值（spike）、疲劳（soak/endurance）、容量（capacity）
- 每种模型包含：适用场景、负载曲线示意、典型时长、风险点
- 决策表：业务场景 → 推荐负载模型（如"秒杀活动" → 峰值；"日常稳定性验证" → 疲劳）
- 反例：误用场景（如用峰值模型测容量上限）

- [ ] **Step 1: 写 load-models.md**

按上述大纲编写，每个负载模型必须有：定义、适用场景、不适用场景、参数示例、1 个反例。

- [ ] **Step 2: 验证文件可独立阅读**

Read 文件全文，确认不依赖 SKILL.md 上下文也能理解。

- [ ] **Step 3: Commit**

```bash
git add plugins/testing/skills/performance-test-engineer/knowledge/load-models.md
git commit -m "feat(performance-test-engineer): 新增负载模型知识库"
```

---

## Task 3: 知识库 — metrics-framework.md

**Files:**
- Create: `plugins/testing/skills/performance-test-engineer/knowledge/metrics-framework.md`

**内容大纲:**
- 核心指标 4 项：TPS/QPS、响应时间（RT，区分 P50/P95/P99）、错误率、资源利用率（CPU/内存/IO/网络）
- 指标阈值参考表（按业务类型分档：互联网应用/金融/物联网）
- 指标间关系：Little's Law（L = λW）、RT 陡增与 TPS 上限的传导
- 采集建议：采样频率、采样窗口、冷启动排除
- 反例：只看平均值不看分位数、忽略冷启动数据

- [ ] **Step 1: 写 metrics-framework.md**

按大纲编写，阈值表必须给具体数值范围（如互联网应用 P99 RT ≤ 500ms），不能写"根据情况而定"。

- [ ] **Step 2: Commit**

```bash
git add plugins/testing/skills/performance-test-engineer/knowledge/metrics-framework.md
git commit -m "feat(performance-test-engineer): 新增指标体系知识库"
```

---

## Task 4: 知识库 — bottleneck-patterns.md

**Files:**
- Create: `plugins/testing/skills/performance-test-engineer/knowledge/bottleneck-patterns.md`

**内容大纲:**
- 6 类瓶颈模式：CPU 飙升、IO 等待、网络延迟、锁竞争、连接池耗尽、GC 停顿
- 每类模式包含：典型现象、定位指标、根因候选清单、优化方向
- **层边界声明**：本库聚焦资源/架构层；代码逻辑层缺陷（如空指针、逻辑错误）转交 bug-analyzer
- 瓶颈传导链：一个瓶颈如何引发另一个（如 GC 停顿 → 请求堆积 → 连接池耗尽）
- 反例：把代码逻辑缺陷当性能瓶颈处理

- [ ] **Step 1: 写 bottleneck-patterns.md**

每类模式用统一模板：`| 现象 | 定位指标 | 根因候选 | 优化方向 | 是否转交 bug-analyzer |`。

- [ ] **Step 2: 校验层边界**

Read 文件，确认每条模式都标注"资源/架构层"或"转交 bug-analyzer"，无越界。

- [ ] **Step 3: Commit**

```bash
git add plugins/testing/skills/performance-test-engineer/knowledge/bottleneck-patterns.md
git commit -m "feat(performance-test-engineer): 新增瓶颈模式知识库"
```

---

## Task 5: 知识库 — use-method.md

**Files:**
- Create: `plugins/testing/skills/performance-test-engineer/knowledge/use-method.md`

**内容大纲:**
- USE 方法定义：对每个资源检查 Utilization（利用率）/ Saturation（饱和度）/ Errors（错误）
- 资源三角：CPU、内存、IO、网络四类资源的 USE 检查项
- 排查顺序：应用层 → 资源层 → 架构层（自上而下）
- 与 bottleneck-patterns.md 的对应关系（哪个 USE 信号对应哪类瓶颈）
- 反例：跳过资源层直接猜架构问题

- [ ] **Step 1: 写 use-method.md**

- [ ] **Step 2: Commit**

```bash
git add plugins/testing/skills/performance-test-engineer/knowledge/use-method.md
git commit -m "feat(performance-test-engineer): 新增 USE 方法知识库"
```

---

## Task 6: SKILL.md 主入口

**Files:**
- Create: `plugins/testing/skills/performance-test-engineer/SKILL.md`

**Frontmatter（完整，照抄）:**
```yaml
---
name: performance-test-engineer
version: 1.0.0
description: >-
  Use when designing performance test plans or analyzing performance bottlenecks.
  Triggers on: 性能测试、负载测试、压力测试、并发测试、TPS、响应时间、瓶颈、性能瓶颈、容量评估、USE方法.
  For functional bug root cause analysis, use bug-analyzer instead. For functional test case generation, use test-case-engineer instead.
keywords:
  - 性能测试
  - 负载测试
  - 压力测试
  - 瓶颈定位
  - USE方法
  - TPS
  - 响应时间
---
```

**正文结构（按此顺序编写）:**
1. 标题 + 角色定位（资深性能测试工程师）
2. 阅读策略（指向 knowledge/4 个文件）
3. Bundle 关系（说明是 testing-bundle 子 skill，与 bug-analyzer 的层边界）
4. 适用范围（适用/不适用，显式排除项）
5. SKILL_ROOT 声明
6. 核心工作流（4 阶段，照 spec Section 2.3）
   - 阶段间依赖说明
   - 🔴 CHECKPOINT 在阶段 2→3 之间（方案确认）
7. 与 bug-analyzer 的层边界表（照 spec Section 2.2）
8. 失败模式与 Fallback（三段式：触发条件/一线修复/仍失败兜底，至少 5 条）
9. 反例与黑名单（dim9 必需，至少 4 条反模式）
10. 约束规则（5 条）

- [ ] **Step 1: 写 SKILL.md frontmatter + 前 5 节**

- [ ] **Step 2: 写工作流 + CHECKPOINT**

阶段 2 后必须显式标记 `🔴 CHECKPOINT · 性能方案确认`，不能只用"建议"措辞。

- [ ] **Step 3: 写层边界表 + 失败模式 + 反例黑名单 + 约束**

失败模式表用三段式（触发条件 / 一线修复 / 仍失败兜底）。反例黑名单独立章节。

- [ ] **Step 4: 自查 dim1-5/7/9 关键项**

Read 全文检查：
- frontmatter 触发词完整、无空话尾巴（dim1）
- 工作流步骤有序号、有输入输出（dim2）
- 失败模式显式编码"如果 X 失败 → Y"（dim3）
- CHECKPOINT 有 🔴 视觉标记（dim4）
- 无"建议/可以考虑/根据情况"等软化措辞（dim5）
- 无"说白了/换句话说"等花叔禁用词（dim7）
- 反例黑名单独立章节（dim9）

- [ ] **Step 5: Commit**

```bash
git add plugins/testing/skills/performance-test-engineer/SKILL.md
git commit -m "feat(performance-test-engineer): 新增 SKILL.md 主入口 v1.0.0"
```

---

## Task 7: test-prompts.json

**Files:**
- Create: `plugins/testing/skills/performance-test-engineer/test-prompts.json`

**完整内容（照抄）:**
```json
[
  {
    "id": 1,
    "prompt": "我们有一个电商下单接口，日常 QPS 约 500，大促峰值预计 3000 QPS，SLA 要求 P99 响应时间 ≤ 800ms，请帮我设计性能测试方案",
    "expected": "按四阶段工作流：理解需求 → 选择负载模型（峰值+容量）→ 设计场景（基准/负载/压力/稳定性）→ 给出指标阈值表，输出完整性能测试方案"
  },
  {
    "id": 2,
    "prompt": "线上接口 TPS 上不去，加压到 800 就开始报超时，CPU 才 40%，请帮我定位瓶颈",
    "expected": "触发逆向瓶颈定位：应用 USE 方法分层排查，从资源层（连接池/IO）入手，输出瓶颈定位报告 + 优化建议"
  },
  {
    "id": 3,
    "prompt": "我们的系统最近加压测试时发现 P95 响应时间在并发 500 时从 200ms 陡增到 2s，但错误率没变，CPU/内存都正常，请分析原因",
    "expected": "复杂场景：现象收集 → 排除 CPU/内存 → 排查 IO/锁/网络/GC → 给出根因候选清单，必要时转交 bug-analyzer 处理代码逻辑缺陷"
  }
]
```

- [ ] **Step 1: 写 test-prompts.json**

- [ ] **Step 2: 校验 JSON 合法**

Run:
```bash
python -c "import json; json.load(open('plugins/testing/skills/performance-test-engineer/test-prompts.json', encoding='utf-8')); print('OK')"
```
Expected: 输出 `OK`

- [ ] **Step 3: Commit**

```bash
git add plugins/testing/skills/performance-test-engineer/test-prompts.json
git commit -m "feat(performance-test-engineer): 新增 darwin-skill 测试 prompts"
```

---

## Task 8: integrations/quickstart.md

**Files:**
- Create: `plugins/testing/skills/performance-test-engineer/integrations/quickstart.md`

**内容大纲:**
- SKILL_ROOT 路径说明：`skills/performance-test-engineer`（不是 `.cursor/skills/...`）
- 快速触发示例（3 个，对应 test-prompts.json）
- 与 testing-bundle 协同调用示例
- 单独安装时的能力边界（无 bundle 路由，需用户直接调用）

- [ ] **Step 1: 写 quickstart.md**

- [ ] **Step 2: 校验 SKILL_ROOT 路径**

Read 文件，确认所有路径示例使用 `skills/performance-test-engineer`，无 `.cursor/skills/` 误写。

- [ ] **Step 3: Commit**

```bash
git add plugins/testing/skills/performance-test-engineer/integrations/quickstart.md
git commit -m "feat(performance-test-engineer): 新增快速上手文档"
```

---

## Task 9: README.md（与 SKILL.md 同步）

**Files:**
- Create: `plugins/testing/skills/performance-test-engineer/README.md`

**内容大纲:**
- 标题 + 一句话定位
- 适用场景（与 SKILL.md 适用范围一致）
- 核心能力（4 阶段工作流摘要）
- 与 bug-analyzer/test-case-engineer 的边界
- 安装方式（指向 testing-bundle 整体安装或单独安装）
- 版本历史：v1.0.0 初始版本

- [ ] **Step 1: 写 README.md**

- [ ] **Step 2: 同步校验**

对比 README.md 与 SKILL.md，确认：适用范围、scope 边界、层边界表三处描述一致（避免 dim7 惩罚）。

- [ ] **Step 3: Commit**

```bash
git add plugins/testing/skills/performance-test-engineer/README.md
git commit -m "feat(performance-test-engineer): 新增 README 与 SKILL.md 同步"
```

---

## Task 10: v1.0.0 基线版本完成 + Runtime 红灯扫描

**Files:**
- 无新文件，验证 + 提交 tag

- [ ] **Step 1: 确认所有文件就位**

Run:
```bash
ls plugins/testing/skills/performance-test-engineer/
ls plugins/testing/skills/performance-test-engineer/knowledge/
```
Expected: SKILL.md / README.md / test-prompts.json / integrations/ / knowledge/(4 个 md)

- [ ] **Step 2: Runtime 红灯扫描（darwin Phase 1 gate 项）**

Run:
```bash
grep -nE "(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|~/\.claude/skills/[a-z]|/plugin install\b)" plugins/testing/skills/performance-test-engineer/SKILL.md plugins/testing/skills/performance-test-engineer/README.md plugins/testing/skills/performance-test-engineer/integrations/quickstart.md
```
Expected: 无输出（无红灯命中）。若有命中 → 修正后再提交。

- [ ] **Step 3: 打 tag 标记基线版本**

Run:
```bash
git tag performance-test-engineer-v1.0.0-baseline
```
Expected: tag 创建成功（供 darwin-skill 优化前后对比）。

- [ ] **Step 4: 推送分支与 tag（可选，需用户确认）**

询问用户是否推送。若推送：
```bash
git push -u origin feat/performance-test-engineer
git push origin performance-test-engineer-v1.0.0-baseline
```

---

## Task 11: darwin-skill Phase 0.5 — 测试 prompt 确认

**Files:**
- 无文件改动，展示 test-prompts.json 给用户

- [ ] **Step 1: 展示 3 个测试 prompt 给用户**

读 `test-prompts.json`，列出 3 个 prompt + expected，请用户确认是否覆盖典型场景。

- [ ] **Step 2: 等待用户确认或修改**

若用户要求修改 → 编辑 test-prompts.json 并 commit。若确认 → 进入 Task 12。

---

## Task 12: darwin-skill Phase 1 — 基线评估

**Files:**
- 更新: `.claude/skills/darwin-skill/results.tsv`（追加基线行）

- [ ] **Step 1: 调用 darwin-skill 对 performance-test-engineer 做基线评估**

向 darwin-skill 发起评估请求，目标 skill = `plugins/testing/skills/performance-test-engineer`，eval_mode 优先 `full_test`（spawn 子 agent 跑 test-prompts）。

- [ ] **Step 2: 记录基线分数到 results.tsv**

格式：
```
timestamp	commit	performance-test-engineer	-	<baseline_score>	baseline	-	初始评估	full_test
```

- [ ] **Step 3: 🔴 CHECKPOINT · 展示基线评分卡给用户**

展示 9 维分数 + 总分 + 结构短板 + 效果短板。等待用户确认后进入优化循环。

---

## Task 13: darwin-skill Phase 2 — 优化循环

**Files:**
- 可能修改: `plugins/testing/skills/performance-test-engineer/SKILL.md` 及知识库

**目标:** 优化到 85+ 分（spec Section 4.6 目标）。

- [ ] **Step 1: 按分数最低维度优先优化**

darwin-skill 自动按 round 优化，每轮 1 个维度。每轮后：
- 若新分 > 旧分 → keep，commit（message: `optimize(performance-test-engineer): {改进摘要}`）
- 若新分 ≤ 旧分 → revert，break

- [ ] **Step 2: 触顶检测**

连续 2 轮 Δ < 2 分 → break（HL-4 见好就收）。

- [ ] **Step 3: 达到 85 分或触顶 → 进入双 judge 验证**

若单 judge 已达 85+ → 跑第二个 judge 确认（project_memory 要求关键决策双 judge）。
若双 judge 一致 ≥ 85 → 通过。若不一致 → 取低分，继续优化或人审。

- [ ] **Step 4: 🔴 CHECKPOINT · 每个 skill 优化完后强制人审**

展示：
- git diff（baseline tag vs 当前）
- 分数变化（9 维 + 总分）
- 测试 prompt 输出对比

等用户确认 OK。若用户说"不好" → 回滚到 baseline tag。

---

## Task 14: 优化收尾 + 成果卡片

**Files:**
- 更新: results.tsv（最终行）
- 生成: 成果卡片 PNG（darwin-skill templates/result-card.html）

- [ ] **Step 1: 记录最终分数到 results.tsv**

- [ ] **Step 2: 生成成果卡片**

用 darwin-skill templates/result-card.html，填入：
- skill-name: performance-test-engineer
- score-before/after/delta
- 9 维 dim-bar
- improvement-1/2/3（主要改进摘要）
- date: 2026-07-04

随机选风格（swiss/terminal/newspaper），截图保存为 PNG。

- [ ] **Step 3: 提交最终版本 + 打 tag**

```bash
git add plugins/testing/skills/performance-test-engineer/
git commit -m "optimize(performance-test-engineer): darwin-skill 优化完成 v1.0.0"
git tag performance-test-engineer-v1.0.0-final
```

- [ ] **Step 4: 通知用户 Phase 2 完成**

展示成果卡片，告知 Phase 2 完成。询问是否进入 Phase 3（test-strategy-engineer）。

---

## Phase 3/4 后续大纲（待 Phase 2 学习后细化）

### Phase 3: test-strategy-engineer（后续独立计划）
- 结构同 Phase 2：4 知识库 + SKILL.md + README + quickstart + test-prompts
- 知识库：risk-matrix-framework.md / test-pyramid.md / entry-exit-criteria.md / strategy-templates.md
- 工作流 5 阶段（含可选阶段 5），CHECKPOINT 在阶段 3→4
- 边界关键：与 test-case-engineer 的粒度区分（项目级 vs 功能级）
- darwin-skill 优化目标 85+

### Phase 4: testing-bundle v2.0.0 升级（后续独立计划）
- 改 testing-bundle/SKILL.md：2-way → 4-way 路由表 + 4 条混合意图链 + 失败模式扩展
- 改 testing-bundle/README.md：同步 4-skill 架构说明
- 改 testing-bundle/test-prompts.json：新增 strategy/performance 路由测试用例
- 4-way 路由端到端测试 + darwin-skill 整体评分

---

## Self-Review

### Spec coverage
- spec Section 2.1 scope → Task 6 SKILL.md 适用范围 ✓
- spec Section 2.2 层边界 → Task 6 SKILL.md 层边界表 + Task 4 bottleneck-patterns.md 层边界声明 ✓
- spec Section 2.3 工作流 → Task 6 SKILL.md 核心工作流 ✓
- spec Section 2.4 知识库 → Task 2-5 ✓
- spec Section 2.5 设计决策 → Task 4/6 内化 ✓
- spec Section 4.6 darwin-skill 验证 → Task 11-14 ✓
- project_memory 约束（README 同步 / SKILL_ROOT / 双 judge / 独立 test-prompts）→ Task 8/9/13/7 ✓

### Placeholder scan
- 知识库内容用"大纲"描述而非完整 prose —— 这是 skill 作者任务的特性，执行时按大纲填充具体内容；每个文件已明确章节结构和必填项（如阈值表必须给具体数值）
- 无 "TBD/TODO/根据情况而定" 等占位措辞

### Type consistency
- frontmatter name/description 在 Task 6 与 spec Section 1.2 路由表关键词一致 ✓
- 文件路径在所有 Task 中一致（`plugins/testing/skills/performance-test-engineer/...`）✓
- tag 命名一致（`performance-test-engineer-v1.0.0-baseline` / `-final`）✓

### 风险
- 知识库 prose 质量在执行阶段才能验证 → Task 12 darwin-skill 基线评估会暴露问题，Task 13 优化循环兜底
- 双 judge 不一致 → Task 13 Step 3 有 fallback（取低分继续优化或人审）
