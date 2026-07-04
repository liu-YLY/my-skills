# Testing Skills 扩展设计：performance-test-engineer + test-strategy-engineer

- **日期**：2026-07-04
- **状态**：已通过 brainstorming 四节确认，待 spec 自检 + 用户审阅
- **路线**：方案 C —— 并行设计两份 spec，实现阶段先 performance 后 strategy
- **目标**：将 testing-bundle 从 2-skill（test-case-engineer + bug-analyzer）扩展到 4-skill（+ test-strategy-engineer + performance-test-engineer），bundle 从 v1.0.0 升级到 v2.0.0

---

## 1. 整体架构与 bundle 路由

### 1.1 4-skill 架构

```
                    用户测试请求
                         │
                         ▼
              ┌─────────────────────────┐
              │   testing-bundle v2.0.0 │  路由层（只路由，不实现能力）
              └───────────┬─────────────┘
                          │ 4-way 意图判断
        ┌─────────┬───────┼───────┬───────────┐
        ▼         ▼       ▼       ▼
  ┌──────────┐┌─────────┐┌──────┐┌───────────┐
  │strategy- ││case-    ││bug-  ││performance│
  │engineer  ││engineer ││anlyz ││-engineer  │
  │ v1.0.0   ││ v8.0.0  ││v1.0.0││ v1.0.0    │
  ├──────────┤├─────────┤├──────┤├───────────┤
  │项目级     ││功能用例  ││功能缺陷││性能测试    │
  │策略/分层  ││设计      ││根因   ││场景+瓶颈   │
  └──────────┘└─────────┘└──────┘└───────────┘
   peer          peer       peer      peer
```

四个子 skill 互为并列 peer，testing-bundle 仅做路由，不实现具体能力。

### 1.2 4-way 路由决策表

| 用户意图关键词 | 路由到 | 说明 |
|---------------|--------|------|
| 测试策略、测试计划、测试分层、风险矩阵、准入准出、测试范围与优先级 | **test-strategy-engineer** | 项目级策略 |
| 测试用例、编写用例、生成用例、测试点、需求分析、用例评审、单功能测试策略 | **test-case-engineer** | 功能用例生成 |
| Bug分析、根因、缺陷定位、复现、5 Whys、鱼骨图、防御性用例反推 | **bug-analyzer** | 功能缺陷根因 |
| 性能测试、负载测试、压力测试、并发测试、TPS、响应时间、瓶颈、性能瓶颈、容量评估 | **performance-test-engineer** | 性能场景+瓶颈分析 |

### 1.3 混合意图链

| 混合意图 | 执行链 | 状态 |
|---------|--------|------|
| "分析 Bug 并补充用例" | bug-analyzer → case-engineer | 已有 |
| "制定测试策略并生成分层用例" | strategy → case-engineer | 新增 |
| "做性能测试并分析瓶颈" | performance 内部完成正向方案设计 + 逆向瓶颈定位（资源/架构层），无需转交 | 新增 |
| "性能问题定位到代码缺陷" | performance（资源/架构层）→ bug-analyzer（代码逻辑层），转交条件：瓶颈指向代码逻辑缺陷 | 新增，跨 skill 转交 |

### 1.4 关键路由规则

1. **性能类问题默认路由到 performance，不路由到 bug-analyzer** —— bundle 需区分"功能 Bug"与"性能问题"
2. **strategy 是并列 peer，不是必经入口** —— 大多数具体请求直接路由到对应 skill
3. **混合意图遵循"先上游后下游"顺序** —— strategy → case-engineer；performance → bug-analyzer（当性能瓶颈定位到代码缺陷时）
4. **每个转交点设 🔴 CHECKPOINT** —— 与现有 bundle 模式一致，用户可终止/修改

---

## 2. performance-test-engineer 详设

### 2.1 Scope 边界

**包含**：
- 正向：性能需求 → 测试方案（负载模型、场景设计、指标阈值）
- 逆向：性能数据/现象 → 瓶颈定位（资源/架构层）+ 优化建议

**不包含**：
- 编写 JMeter/Locust/k6 脚本（编码任务，由通用编码能力承载）
- 代码逻辑层缺陷定位（转交 bug-analyzer）
- 功能用例设计（转交 test-case-engineer）

### 2.2 与 bug-analyzer 的层边界（关键）

| 维度 | performance-test-engineer | bug-analyzer |
|------|---------------------------|--------------|
| 定位层 | 资源/架构层 | 代码逻辑层 |
| 输入 | 性能数据（CPU/IO/RT/TPS）、性能现象 | Bug 现象、错误日志、复现步骤 |
| 方法论 | USE 方法、资源三角、瓶颈传导链 | 5 Whys、鱼骨图、隔离定位 |
| 输出 | 瓶颈点 + 资源/架构优化建议 | 根因 + 代码修复建议 |
| 转交触发 | 定位到代码逻辑缺陷 → bug-analyzer | 定位到资源/架构瓶颈 → performance |

### 2.3 工作流

```
阶段 1: 性能需求理解
  → 业务场景 / 用户量 / 峰值 / SLA
  → 输出：性能需求摘要 + 关键指标初值
  ↓
阶段 2: 测试场景设计（正向）
  → 负载模型选择（阶梯/峰值/疲劳/容量）
  → 场景设计（基准/负载/压力/稳定性）
  → 指标阈值（TPS/RT/错误率/资源利用率）
  → 输出：性能测试方案
  ↓
🔴 CHECKPOINT · 方案展示给用户确认
  ↓
阶段 3: 瓶颈定位（逆向，当有性能数据/现象时触发）
  → 现象收集（RT 陡增？TPS 上不去？错误率飙升？）
  → 指标分层排查（应用层 → 资源层 → 架构层）
  → 应用 USE 方法（Utilization/Saturation/Errors）
  → 输出：瓶颈定位报告 + 优化建议
  ↓
阶段 4: 转交判断
  → 瓶颈指向代码逻辑缺陷？转交 bug-analyzer
  → 瓶颈指向资源/架构？本 skill 给优化建议
```

### 2.4 知识库结构

```
performance-test-engineer/
├── SKILL.md
├── knowledge/
│   ├── load-models.md          # 负载模型（阶梯/峰值/疲劳/容量）
│   ├── metrics-framework.md    # 指标体系（TPS/RT/错误率/资源利用率 + 阈值参考）
│   ├── bottleneck-patterns.md  # 瓶颈模式库（CPU/IO/网络/锁/连接池/GC）
│   └── use-method.md           # USE 方法 + 资源三角
├── integrations/
│   └── quickstart.md
└── test-prompts.json
```

### 2.5 关键设计决策

1. **瓶颈模式库独立** —— 不与 bug-analyzer 的 bug-patterns.md 共享；聚焦点不同（资源/架构 vs 代码逻辑），共享会引入路由歧义
2. **正逆两阶段在同一 skill 内完成** —— 性能测试的"方案设计"和"瓶颈定位"强耦合（方案决定采集什么数据，数据反推瓶颈），不应拆分
3. **CHECKPOINT 在方案确认处** —— 方案确认后才进入瓶颈定位，避免对错误方案做分析

---

## 3. test-strategy-engineer 详设

### 3.1 Scope 边界

**包含**（轻量主体）：
- 项目级风险矩阵（功能风险 → 测试优先级）
- 测试分层策略（单元/接口/UI 比例 + 各层职责）
- 测试范围与优先级（测什么 / 不测什么 / 重点测什么）
- 准入准出标准（进入测试 / 完成测试的判定条件）

**包含**（可选附录，用户主动要求时才填）：
- 资源估算（人力/环境/工具粗估）
- 进度排期（里程碑式，不做精细排期）
- 风险跟踪清单

**不包含**：
- 单功能测试策略（test-case-engineer 的"需求分析"阶段已覆盖）
- 具体用例编写（转交 test-case-engineer）
- 性能测试方案（转交 performance-test-engineer）
- Bug 根因分析（转交 bug-analyzer）

### 3.2 与 test-case-engineer 的边界（关键）

| 维度 | test-strategy-engineer | test-case-engineer |
|------|------------------------|-------------------|
| 粒度 | 项目级（整体） | 单功能级 |
| 输入 | 项目需求/特征/约束 | 单功能需求 |
| 输出 | 风险矩阵 + 分层策略 + 范围优先级 + 准入准出 | 具体测试用例 |
| 决策 | 测什么、怎么分层、资源怎么分 | 怎么测这个功能 |
| 关系 | 上游（指导） | 下游（被指导） |

### 3.3 工作流

```
阶段 1: 项目特征理解
  → 项目类型 / 规模 / 关键质量目标 / 约束（时间/资源/技术栈）
  → 输出：项目特征摘要
  ↓
阶段 2: 风险矩阵构建
  → 功能风险识别（业务复杂度/变更频率/历史缺陷/外部依赖）
  → 风险评级（高/中/低）→ 测试优先级
  → 输出：风险矩阵
  ↓
阶段 3: 测试分层策略
  → 测试金字塔比例（单元/接口/UI）
  → 各层职责与边界
  → 分层工具选择建议（方法论层，不写脚本）
  → 输出：分层策略
  ↓
🔴 CHECKPOINT · 策略展示给用户确认
  ↓
阶段 4: 范围与准入准出
  → 测试范围（必测/选测/不测）+ 优先级
  → 准入标准（开发完成 / 冒烟通过 / 环境就绪）
  → 准出标准（用例覆盖率 / 缺陷收敛 / 性能达标）
  → 输出：范围与准入准出
  ↓
阶段 5（可选）: 资源与进度附录
  → 仅当用户明确要求时生成
  → 资源粗估 + 里程碑式进度 + 风险跟踪清单
```

### 3.4 知识库结构

```
test-strategy-engineer/
├── SKILL.md
├── knowledge/
│   ├── risk-matrix-framework.md   # 风险识别维度 + 评级方法
│   ├── test-pyramid.md            # 测试金字塔分层模型 + 比例参考
│   ├── entry-exit-criteria.md     # 准入准出标准参考库
│   └── strategy-templates.md      # 策略文档模板（含可选附录）
├── integrations/
│   └── quickstart.md
└── test-prompts.json
```

### 3.5 关键设计决策

1. **不共享 bug-patterns.md** —— strategy 聚焦项目级风险识别，与 bug 模式无关；若需历史缺陷数据，由用户提供或转交 bug-analyzer
2. **不与 case-engineer 共享知识库** —— 两者粒度不同（项目级 vs 功能级），共享会模糊边界；strategy 的"分层策略"是输出，case-engineer 的"测试分层"是输入参考
3. **CHECKPOINT 在策略确认处** —— 策略确认后才进入范围/准出，避免对错误策略做细化
4. **可选附录用条件触发** —— SKILL.md 中明确"阶段 5 仅在用户明确要求资源/进度时执行"，避免默认生成冗余内容

### 3.6 Bundle 协同

- **strategy → case-engineer**：strategy 输出分层策略与优先级，case-engineer 基于策略生成各层用例
- **strategy → performance**：strategy 输出性能风险项，performance 基于风险设计性能测试方案
- **strategy 不直接协同 bug-analyzer**：bug-analyzer 是事后分析，与策略无直接链路

---

## 4. bundle 演进与实现顺序

### 4.1 testing-bundle v1.0.0 → v2.0.0 演进

| 维度 | v1.0.0（现状） | v2.0.0（目标） |
|------|---------------|---------------|
| 子 skill 数 | 2（case-engineer + bug-analyzer） | 4（+ strategy + performance） |
| 路由 | 2-way（正向生成 / 逆向分析） | 4-way（策略 / 用例 / 根因 / 性能） |
| 混合意图链 | 1 条（bug → case） | 4 条（详见 1.3） |
| description 触发词 | 测试、用例、Bug、根因 | + 测试策略、性能测试、负载、瓶颈、TPS |
| version | 1.0.0 | 2.0.0（breaking：路由表扩展） |

### 4.2 bundle 文件改动

```
testing-bundle/
├── SKILL.md           # 改：路由表 2-way→4-way + 新增混合意图链 + 失败模式扩展
├── README.md          # 改：同步更新 4-skill 架构说明
└── test-prompts.json  # 改：新增 strategy/performance 路由测试用例
```

### 4.3 实现顺序（方案 C 确定）

```
Phase 1: 设计阶段（当前，并行产出两份 spec）
  → 本文档覆盖两个 skill 的设计
  → 一次性敲定边界，避免先后实现返工
  ↓
Phase 2: 实现 performance-test-engineer（先做）
  → 边界清晰、方法论独立、见效快
  → 验证 bundle 从 2→3 skill 的扩展模式
  → 跑 darwin-skill 评分验证质量
  ↓
Phase 3: 实现 test-strategy-engineer（后做）
  → 上游 skill，需更多打磨
  → 基于 Phase 2 经验调整
  → bundle 升级到 v2.0.0（4-skill 完整形态）
  → 跑 darwin-skill 评分验证质量
  ↓
Phase 4: bundle v2.0.0 整体验证
  → 4-way 路由测试
  → 混合意图链端到端验证
  → darwin-skill 整体评分
```

### 4.4 每个 skill 的标准交付物

参照现有 test-case-engineer / bug-analyzer 的结构：

```
[skill-name]/
├── SKILL.md                    # 主入口
├── README.md                   # 与 SKILL.md 同步
├── knowledge/                  # 知识库
├── integrations/
│   └── quickstart.md          # 快速上手
├── test-prompts.json          # darwin-skill 验证用
└── scripts/                   # 仅当有真实脚本需求时
    ├── convert_docs.py        # 复用现有脚本
    └── requirements.txt
```

### 4.5 风险与对策

| 风险 | 对策 |
|------|------|
| 4-way 路由歧义（如"性能 Bug"既属 bug-analyzer 又属 performance） | 在路由表用"功能 Bug vs 性能问题"显式区分；性能类默认路由到 performance，performance 内部判断是否转交 bug-analyzer |
| strategy 与 case-engineer 边界模糊（"测试策略"一词双义） | strategy 关键词限定"项目级/测试计划/分层"；case-engineer 的"测试策略"改为"单功能测试策略"；在路由表备注层区分 |
| performance 瓶颈定位与 bug-analyzer 重叠 | 用 2.2 的层边界表明确：资源/架构层 vs 代码逻辑层；不共享知识库 |
| bundle 升级影响现有用户 | v2.0.0 是 breaking change，但路由表是超集（原有路由全部保留）；在 README 标注升级说明 |

### 4.6 darwin-skill 验证计划

每个 skill 完成后：
1. 跑 darwin-skill 双 judge 评分
2. 对比 test-case-engineer（v8.0.0, ~86-91 分）和 bug-analyzer（v1.0.0）的基线
3. 目标：两个新 skill 都达到 85+ 分

bundle v2.0.0 完成后：
1. 整体跑 4-way 路由测试（覆盖 4 个 peer + 4 条混合意图链）
2. 整体 darwin-skill 评分

---

## 5. 关键决策记录

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 路线方案 | 方案 C（并行设计 + 先 performance 后 strategy） | 一次性敲定边界避免返工；performance 边界清晰先做验证模式 |
| performance scope | 正逆都含 | 方案设计与瓶颈定位强耦合，拆分会丢失上下文 |
| strategy scope | 轻量 + 可选附录 | 主体聚焦方法论，资源/进度偏项目管理用条件触发避免冗余 |
| strategy 在 bundle 中定位 | 并列 peer | 大多数请求是具体的，不需要每次先做策略；与现有 peer 路由模式一致 |
| 知识库共享 | 不共享 | 各 skill 聚焦点不同，共享会引入路由歧义（参考 test-case-engineer/bug-analyzer 的 bug-patterns 共享教训） |

---

## 6. 待办（交给 writing-plans）

- [ ] Phase 2: performance-test-engineer 实现计划（文件清单 + 知识库内容大纲 + SKILL.md 结构）
- [ ] Phase 3: test-strategy-engineer 实现计划
- [ ] Phase 4: testing-bundle v2.0.0 升级计划（SKILL.md/README.md/test-prompts.json 改动）
- [ ] darwin-skill 验证脚本与基线对比
