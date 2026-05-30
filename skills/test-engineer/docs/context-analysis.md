# test-engineer Skill 上下文分析报告

> 分析时间：2026-05-30
> Skill 版本：2.0.0
> 分析人：Claude (Auto-generated)

---

## 一、各文件 Token 估算

> 估算方法：中文混合英文内容，按 `chars / 2.2` 估算 token 数（中文1字≈1.5-2 token，英文1词≈1.3 token，混合取中间值）

| 文件 | 行数 | 字符数 | 估算 Token | 读取时机 |
|------|------|--------|-----------|----------|
| **SKILL.md** | ~130 | ~4,500 | **~2,045** | 始终加载（Skill 入口） |
| references/stage1-understanding.md | 82 | 1,969 | ~894 | 阶段1 |
| references/stage2-testpoints.md | 131 | 4,226 | ~1,920 | 阶段2 |
| references/stage3-writing.md | ~240 | ~6,200 | ~2,818 | 阶段3 |
| references/stage4-review.md | ~80 | ~2,000 | ~909 | 阶段4 |
| knowledge/bug-patterns.md | 165 | 4,295 | ~1,952 | 阶段2 强制 |
| knowledge/test-standards.md | ~290 | ~7,200 | ~3,273 | 阶段3/4 强制 |
| knowledge/test-levels.md | 86 | 2,588 | ~1,176 | 阶段2/3 强制 |
| knowledge/project-knowledge.md | 66 | 2,060 | ~936 | 阶段1 强制 |
| knowledge/prompt-strategy.md | ~120 | ~3,300 | ~1,500 | 阶段3（AI 生成模式） |
| knowledge/efficiency-metrics.md | ~70 | ~1,800 | ~818 | 阶段4（效率报告） |
| adapters/test.md | 99 | 2,378 | ~1,080 | 阶段3（有适配器时） |
| integrations/quickstart.md | 78 | 2,340 | ~1,063 | 执行命令时 |
| knowledge/python/pep8.md | 247 | 4,499 | ~2,044 | 按需 |
| knowledge/python/debugging.md | 334 | 6,172 | ~2,805 | 按需 |
| **总计** | **~2,238** | **~55,602** | **~25,233** | - |

## 二、按工作流场景计算实际上下文消耗

Agent 并非一次性加载全部文件，而是按阶段按需读取。根据 SKILL.md 的强制读取规则：

### 场景 A：完整四阶段流程（默认模式，最常见）

| 加载顺序 | 文件 | Token | 说明 |
|----------|------|-------|------|
| ① | SKILL.md | 2,045 | 始终加载 |
| ② | stage1 + project-knowledge | 894 + 936 | 阶段1：理解需求 |
| ③ | stage2 + bug-patterns + test-levels | 1,920 + 1,952 + 1,176 | 阶段2：提取测试点 |
| ④ | stage3 + test-standards + prompt-strategy + test | 2,818 + 3,273 + 1,500 + 1,080 | 阶段3：AI 生成用例 |
| ⑤ | stage4 + test-standards(已缓存) + efficiency-metrics | 909 + 0 + 818 | 阶段4：自检 + 效率报告 |
| **累计（不重复计）** | | **~17,321** | |

> 注：test-standards 在阶段3和4都会用到，但第二次读取时已在上下文中，不重复计算。

### 场景 B：快速模式（压缩阶段1/4）

| 加载顺序 | 文件 | Token |
|----------|------|-------|
| ① | SKILL.md | 2,045 |
| ② | stage1（仅1.3模板）≈ 50% | ~447 |
| ③ | stage2 + bug-patterns + test-levels | 1,920 + 1,952 + 1,176 |
| ④ | stage3 + test-standards + prompt-strategy + test | 2,818 + 3,273 + 1,500 + 1,080 |
| ⑤ | stage4（仅质量检查+遗漏扫描）≈ 60% | ~545 |
| **累计** | | **~15,756** |

### 场景 C：仅写用例（跳过阶段1/2，用户直接给测试点）

| 加载顺序 | 文件 | Token |
|----------|------|-------|
| ① | SKILL.md | 2,045 |
| ② | stage3 + test-standards + prompt-strategy + test | 2,818 + 3,273 + 1,500 + 1,080 |
| ③ | stage4 | 909 |
| **累计** | | **~11,625** |

### 场景 D：Bug 分析/Python调试（非用例编写场景）

| 加载顺序 | 文件 | Token |
|----------|------|-------|
| ① | SKILL.md | 2,045 |
| ② | bug-patterns | 1,952 |
| ③ | python/debugging（按需） | 2,805 |
| **累计** | | **~6,802** |

## 三、上下文消耗分布可视化

```
场景A（完整四阶段）≈ 17,321 tokens
├─ SKILL.md               ████░░░░░░░░░░░░░░░░  12%
├─ stage1+proj-know       ███░░░░░░░░░░░░░░░░░  11%
├─ stage2+bug+levels      █████░░░░░░░░░░░░░░░  29%  ← 核心环节
├─ stage3+std+prompt+test ████████░░░░░░░░░░░  50%  ← 最大消耗环节（含 AI 生成）
└─ stage4+efficiency       █░░░░░░░░░░░░░░░░░░  10%
```

## 四、关键发现

| 发现 | 数据支撑 | 建议 |
|------|----------|------|
| **阶段2+3 占上下文 79%** | stage2+bug+levels+stage3+std+prompt+test = 13,822 / 17,321 | 这两个阶段是上下文消耗的核心，也是产出质量的关键，压缩空间有限 |
| **新增 prompt-strategy.md 增加 1,500 tokens** | 仅在阶段 3 AI 生成模式加载 | 必要投入，是 AI 赋能的核心文件 |
| **test-standards.md 是最大的单文件** | 3,273 tokens，占场景A的 19% | 已压缩过一次，进一步压缩会损失规则完整性，不建议继续 |
| **Python 知识文件几乎不参与主流程** | pep8(2,044) + debugging(2,805) = 4,849 tokens，仅在非核心场景按需读取 | 当前已标记为"按需"，不影响主流程上下文 |
| **SKILL.md 略有增长** | 2,045 tokens，增加了 AI 赋能模式章节 | 增长合理，仍保持精简 |
| **test.md 仅在有适配器时加载** | 1,080 tokens | 无适配器项目可省略 |

## 五、与主流模型上下文窗口的对比

| 模型 | 上下文窗口 | 场景A占比 |
|------|-----------|----------|
| GPT-4 / Claude 3.5 | 128K tokens | **0.01%** |
| GPT-4o-mini | 128K tokens | **0.01%** |
| Claude 3 Haiku | 200K tokens | **0.009%** |

**结论**：即使是最重的完整四阶段流程（~17,321 tokens），也仅占 128K 上下文窗口的 **13.5%**，加上用户需求文档、代码搜索结果、Agent 推理过程等，总消耗通常在 25K-45K tokens 范围内，远未触及窗口上限。

## 六、真正的上下文瓶颈不在 Skill 文件本身

Skill 文件占用 ~17K tokens 是可控的。实际上下文压力来自：

| 真实瓶颈 | 典型消耗 | 占比 |
|----------|----------|------|
| **需求文档内容**（PRD/设计稿/代码搜索结果） | 5K-20K tokens | 20%-40% |
| **Agent 推理链**（思考过程、中间输出） | 3K-10K tokens | 10%-20% |
| **已有用例文件**（继承风格时需读取） | 2K-8K tokens | 8%-16% |
| **Skill 文件**（本评估） | ~17K tokens | 15%-35% |
| **AI 生成的中间输出**（用例草稿） | 2K-8K tokens | 8%-16% |

如果需要进一步降低上下文，更有效的方向是优化**需求文档的预处理**（只传入相关章节而非全文）和**已有用例的摘要化**（只读结构不读全文），而非继续压缩 Skill 规则文件。
