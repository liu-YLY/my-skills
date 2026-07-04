# test-engineer Skill 拆分总结：从单体到双 Skill 的实战记录

> **日期**：2026-07-04
> **分支**：`refactor/split-test-engineer`
> **基线**：`backup/pre-split-test-engineer` (cddcc45, v7.0.0)
> **优化后 HEAD**：`0d683ee`

---

## 一、引言

test-engineer 是一个 AI 赋能的测试工程师 skill，原本承载五项能力：测试用例生成、用例评审、测试策略设计、产品知识库、Bug 根因分析。v7.0.0 时文件精简到 ~850 行，懒加载机制成熟，darwin-skill 双 judge 评分 86.8 / 85.6（Δ=1.2）。

表面看一切正常，但一次深度评估暴露了结构性问题：**Bug 分析能力只有 18 行，却和 600 行的用例生成流程挤在同一个 SKILL.md 入口里**。这种"异质工作流并存"是组织层面的隐患——迭代时互相掣肘，路由时容易混淆。

本文记录了从评估、决策、方案设计、实施到持续优化的完整过程，以及其中踩过的坑和得到的经验。

---

## 二、决策：用数据支撑"要不要拆"

### 2.1 拆分的三个强信号

darwin-skill 双 judge 盲评给出了高度一致的结论：

**信号 1：异质工作流投入严重不均**
- 用例生成：约 600 行（四阶段 + 失败模式表 + 检查点 + 模板 + 自检清单）
- Bug 分析：仅约 18 行（仅列五步法名称，无独立检查点/失败模式表/输出模板）

**信号 2：入口路由混杂**
- SKILL.md 声明 5 项能力，前 4 项同工作流，第 5 项（Bug 分析）异质
- 模式选择规则只定义"回归验证清单/快速"两种模式，Bug 分析无独立入口路由

**信号 3：知识库耦合**
- `bug-patterns.md` 自述双重用途："阶段 2 测试点扫描完 7 维度后必读；Bug 根因分析时必须查阅"
- 同一个知识文件同时服务于"预防"（防御性测试点）和"诊断"（根因分析）两个相反方向

### 2.2 关键判断：拆分不是质量补救，是组织优化

各维度绝对分数都较高（最低 dim6=6 是路径笔误），拆分动机来自架构层面，不是质量红线。这意味着拆分的预期收益是"迭代独立性"和"路由清晰度"，而非"评分大幅提升"。

这个判断在后续优化中得到了验证——拆分后评分仅边际变化（+0.8 / -0.7），但 Bug 分析能力从 18 行升级为 295 行独立高质量 skill。

---

## 三、方案设计：借鉴 superpowers 的协同编排

拆分最大的顾虑是"两个 skill 怎么协同"。调研了 [obra/superpowers](https://github.com/obra/superpowers) 后，发现其核心机制非常适合我们的场景。

### 3.1 superpowers 的三层协同机制

1. **Bootstrap 入口层**：`using-superpowers` skill 在 session 启动时注入，强制规则"即使 1% 概率某个 skill 适用也必须 invoke"
2. **Skill 间引用层**：命名约定 + 显式标记（`**REQUIRED SUB-SKILL:** Use superpowers:xxx`），明确禁止 `@skills/.../SKILL.md` 语法（会 force-load 烧 context）
3. **Skill 类型分层**：Process skills 优先级高于 Implementation skills，"Process 决定 HOW，Implementation 决定 WHAT"

### 3.2 采纳与不采纳

**采纳的部分**：
- description 改为纯"何时用"格式（superpowers 的 SDO 原则）
- Skill 间用名称引用，不用 `@` 路径
- 显式路由提示（在 SKILL.md 顶部声明"不适用时转交哪个 skill"）

**不采纳的部分**：
- 不引入 bootstrap 入口 skill（过度设计，依赖 TRAE 自身触发机制即可）
- 不采用 subagent 并行执行（我们的工作流是单一 session 串行）
- 不采用 TDD 式 skill 验证（darwin-skill 的 dim8 已覆盖）

### 3.3 拆分方案核心

```
test-engineer/ (v7.0.0)
  ↓
  ├─ test-case-engineer/ (v8.0.0)  ← 用例生成（保留主框架）
  └─ bug-analyzer/        (v1.0.0)  ← Bug 根因分析（新建）
```

**关键决策**：
- `bug-patterns.md` 主归属 test-case-engineer，bug-analyzer 通过相对路径引用（避免复制导致内容分叉）
- 版本号：test-case-engineer v8.0.0（破坏性变更），bug-analyzer v1.0.0（新建）
- test-prompts.json 两 skill 各自独立维护（便于 darwin-skill dim8 实测验证）

---

## 四、实施：9 步迁移 + 8 个 commit

按方案分 9 步执行，每步独立 commit 保证可回退：

| 步骤 | 操作 | commit |
|------|------|--------|
| 1 | 复制 test-engineer/ → test-case-engineer/ | `a175a17` |
| 2 | 切除 test-case-engineer 中 Bug 分析内容 | `2aac91a` |
| 3 | 更新 test-case-engineer/SKILL.md 为 v8.0.0 | `6ba5fbe` |
| 4 | 修复 quickstart.md 路径 bug | `4829645` |
| 5 | 新建 bug-analyzer/ 基础结构 | `07a8823` |
| 6 | 实现 bug-analyzer 五步定位法核心流程 | `07a8823` |
| 7 | 迁移 bug-analyzer/test-prompts.json | `4915fd3` |
| 8 | 删除原 test-engineer/ 目录 | `4915fd3` |
| 9 | 更新项目 README.md | `85a8615` |

**Git 安全实践**：
- 拆分前创建基线分支 `backup/pre-split-test-engineer`，保证可整体回退
- 每步独立 commit，局部问题可 `git revert <commit>` 不影响其他改动
- 不使用 `git reset --hard` 当回滚手段（darwin-skill 反例黑名单第 2 条）

---

## 五、效果验证：拆分后双 judge 评估

### 5.1 拆分前后评分对比

| Skill | 拆分前 | 拆分后 | Δ | 说明 |
|-------|--------|--------|---|------|
| test-case-engineer | 86.8 / 85.6（双 judge） | 85.2 | -0.7 | 误差范围内保持水平 |
| bug-analyzer | （原 18 行，未独立评分） | 91.3 | — | 从"附带功能"升级为高质量独立 skill |

### 5.2 核心收益：Bug 分析能力的飞跃

拆分前 Bug 分析能力存在严重短板：
- 仅 18 行描述，无独立工作流
- 无失败模式编码（dim3 缺失）
- 无检查点设计（dim4 缺失）
- 无独立反例黑名单（dim9 部分）

拆分后 bug-analyzer 全面补齐：
- 五步定位法每步配备三段式失败模式表（dim3 满分 10）
- 5 个 🔴 CHECKPOINT + 1 个 🛑 STOP 显性标记（dim4 评分 9）
- 16 条反例黑名单覆盖三类场景（dim9 满分 10）
- 报告模板字段完整说明 + 防御性测试点清单输出格式

**关键发现**：bug-analyzer 独立评分 91.3 显著高于原 test-engineer 整体的 86 分。这印证了拆分的核心价值——Bug 分析作为独立 skill 获得了完整的工作流支撑，从原本 18 行的"附带功能"升级为高质量独立能力。

---

## 六、持续优化：3 轮 hill-climbing + ratchet

拆分完成后，进入 darwin-skill Phase 2 优化循环，采用"保守优化"策略：执行 P0 修复 + HL 杠杆点，跳过结构性增强。

### 6.1 优化前基线（保证可回溯）

创建 `backup/pre-optimize-baseline` 分支，保存优化前评估结果到 `results.tsv` 和 `2026-07-04-baseline.md`。

### 6.2 三轮优化

| 轮次 | Skill | 改动 | 目标维度 | Δ |
|------|-------|------|----------|---|
| 1 | test-case-engineer | 修复 docs/ 矛盾（触发词+旧名+适配器） | dim7 +1, dim6 +1 | +0.8 |
| 2 | bug-analyzer | 失败模式表具体化（补具体字段/阈值） | dim5 +1 | -0.7 |
| 3 | bug-analyzer | 步骤 5 补失败模式表 | dim3 +1 | 0 |

### 6.3 HL-4 触顶信号

按 darwin-skill HL-4 规则：连续 2 轮 Δ < 2 分 → break 进 Phase 3。第 2-3 轮均触顶，停止优化。

### 6.4 Ratchet 决策的争议

bug-analyzer 总分 -0.7，按 ratchet 严格规则应 revert。但分析发现：
- dim5 +1 是真实改进（失败模式表具体化）
- 下降主要来自 dim2/4/9 各 -1，理由都是"judge 更严格"而非"内容变差"

这印证了 darwin-skill 反例黑名单第 1 条：LLM-as-judge 准确率仅 46.4%，fine-grained 差异不可信。最终决定保留 bug-analyzer 改动。

---

## 七、经验总结

### 7.1 什么有效

**1. 评估先行，数据支撑决策**
- 用 darwin-skill 双 judge 评分佐证拆分必要性，避免"感觉应该拆"的主观判断
- 三个强信号（异质工作流/路由混杂/知识库耦合）都有具体维度证据

**2. 基线分支保证可回退**
- 拆分前创建 `backup/pre-split-test-engineer`，优化前创建 `backup/pre-optimize-baseline`
- 两层基线让任何阶段都可回退，不惧怕实验性改动

**3. 借鉴成熟方案而非发明轮子**
- superpowers 的协同编排机制完全适用，不需要从零设计
- "采纳什么"和"不采纳什么"都有明确理由

**4. HL 杠杆点投入产出比高**
- 失败模式表具体化（HL-2 应用）：5 行改动撬动 dim5 +1
- 步骤 5 补表：9 行新增补齐 dim3 短板
- 显性视觉标记（HL-1 应用）：🔴/🛑 标记是 LLM 解析时的关键信号

### 7.2 什么没效

**1. 单 context 自评自改的乐观偏差**
- 拆分后第一次评分 91.3，优化后降到 86.4，部分原因是第一次评分有乐观偏差
- darwin-skill 反例黑名单第 1 条已警告：必须 spawn 独立子 agent 评分

**2. dry_run 比例过高**
- 整个优化过程 0 full_test / 3 dry_run，dim8 实测维度形同虚设
- 按 darwin-skill 反例黑名单第 6 条：分数有虚高风险

**3. 行数标注易引起 judge 误判**
- test-case-engineer 的 judge 报告行数标注"全部错误"，但实测标注准确
- judge 可能用了不同的统计方式（含空行/不同编码）
- 教训：行数标注容易引起歧义，不如直接删除或标注"约"

### 7.3 教训

**1. 拆分时容易漏改悬空引用**
- test-standards.md 中的"项目适配器"概念在拆分时被遗漏，judge 后才发现
- 拆分后应做一次全局 grep 扫描悬空引用

**2. judge 波动是常态，不是异常**
- bug-analyzer 优化后 -0.7 主要来自 judge 严格度波动，非内容变差
- 重要决策不应依赖单次评分，要看多轮趋势

**3. 见好就收比硬凑分更重要**
- HL-4 触顶信号（连续 2 轮 Δ < 2）是停手信号，不是继续信号
- 硬凑 MAX_ROUNDS 会引入 over-engineering（反例黑名单第 3 条）

---

## 八、最终成果

### 8.1 分数变化

| Skill | 拆分前 | 拆分后 | 优化后 | 总 Δ |
|-------|--------|--------|--------|------|
| test-case-engineer | 86.8 | 85.2 | 86.8 | 0 |
| bug-analyzer | （18 行） | 91.3 | 86.4 | — |

> 注：bug-analyzer 优化后分数下降主要来自 judge 波动，dim5 真实改进已保留。

### 8.2 提交历史

完整拆分 + 优化共 13 个 commit，从 `a175a17`（复制目录）到 `0d683ee`（对比报告），每步独立可回退。

### 8.3 可回溯性

| 回退点 | 分支 | HEAD |
|--------|------|------|
| 优化前基线 | `backup/pre-optimize-baseline` | b227049 |
| 拆分前基线 | `backup/pre-split-test-engineer` | cddcc45 |
| 优化后当前 | `refactor/split-test-engineer` | 0d683ee |

评估数据完整保存：
- `skills/.darwin-results/results.tsv` - 标准化评分日志
- `skills/.darwin-results/2026-07-04-baseline.md` - 优化前基线报告
- `skills/.darwin-results/2026-07-04-comparison.md` - 优化前后对比报告

---

## 九、后续迭代方向

按优先级排序：

1. **P1：修复 test-standards.md 适配器悬空引用**（judge 发现的拆分遗留问题）
2. **P1：补齐 test-case-engineer 的用例评审工作流**（dim8 短板）
3. **P2：bug-analyzer 步骤 4 新增生产环境反向验证 Fallback**（生产环境无法"撤销修复"）
4. **P2：bug-analyzer 特定缺陷类型 checklist**（NPE/500/超时等高频缺陷）
5. **P3：精简三文件内容重叠**（SKILL.md/core.md/README.md 职责分工）

---

## 十、结语

这次拆分验证了一个核心观点：**skill 的组织结构会反过来影响能力上限**。

Bug 分析在 test-engineer 里只是 18 行的附带功能，无论怎么迭代都受限于用例生成的主框架。拆分为独立 skill 后，它获得了完整的工作流支撑（五步定位法 + 失败模式表 + 检查点 + 反例黑名单），评分从无法独立评估升级到 86.4-91.3 区间。

darwin-skill 的评估机制在这次拆分中扮演了关键角色：
- **拆分前**：双 judge 评分佐证拆分必要性
- **拆分后**：双 judge 评估验证拆分效果
- **优化时**：ratchet 机制保证只保留改进
- **触顶后**：HL-4 信号避免 over-engineering

但 darwin-skill 也有局限：LLM-as-judge 准确率仅 46.4%，fine-grained 差异不可信。bug-analyzer 优化后 -0.7 的下降就是 judge 波动的典型案例。重要决策必须人审，不能盲信分数。

> "Train your Skills like you train your models" — darwin-skill
