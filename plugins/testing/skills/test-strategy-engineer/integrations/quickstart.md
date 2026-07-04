# 快速上手

> **何时阅读**：首次使用本 skill 或需快速了解触发方式与协同调用时查阅。
> **覆盖范围**：SKILL_ROOT 路径 / 触发示例 / testing-bundle 协同 / 单独安装边界 / 与其他 skill 边界。
> **可跳过条件**：已熟悉本 skill 触发与层间转交规则。

## SKILL_ROOT

在本仓库中：`SKILL_ROOT` = `skills/test-strategy-engineer`

> 下文命令中的 `$SKILL_ROOT` 是占位符，**Agent 执行命令时必须替换为上述实际路径**。
> 人在终端使用时，先执行 `export SKILL_ROOT=skills/test-strategy-engineer`，或手动将 `$SKILL_ROOT` 替换为实际路径。

> 路径禁止误写为 `.cursor/skills/test-strategy-engineer` 或 `~/.claude/skills/test-strategy-engineer`。本 skill 随仓库分发，路径以仓库内 `skills/test-strategy-engineer` 为准。

## 快速触发示例

### 示例 1：电商项目测试策略制定（五阶段完整流程）

**用户输入**：我们有一个电商项目即将启动测试，包含用户中心、商品、订单、支付、营销等模块，团队 20 人，3 个月迭代周期，请帮我制定测试策略

**skill 执行阶段**：
- 阶段 1 项目特征理解：新项目 + 5 模块 + 团队 20 人 + 3 个月迭代；质量目标权重（支付正确性 > 订单一致性 > 营销活动）
- 阶段 2 风险矩阵构建：5 模块 × 5 维评分（业务复杂度/变更频率/历史缺陷/外部依赖/数据敏感性），支付模块因资金+合规+外部依赖拉满，风险等级=高 → P0
- 阶段 3 测试分层策略：新项目 → 经典金字塔（单元:接口:UI = 7:2:1），高风险模块三层全覆盖，中风险模块单元+接口，低风险模块仅接口
- 🔴 CHECKPOINT：展示风险矩阵 + 分层策略，等用户确认
- 阶段 4 范围与准入准出：必测=P0+P1 全量，准出=P0 用例 100% 通过 + 无 P0/P1 缺陷遗留 + 性能达标
- 阶段 5：用户未要求资源估算，跳过并标注「未生成（用户未要求）」

**输出摘要**：
- 项目特征：新项目 / 5 模块 / 3 个月迭代 / 支付为核心风险
- 风险矩阵：支付=P0、订单=P0、营销=P1、商品=P1、用户中心=P2
- 分层策略：经典金字塔 7:2:1，支付与订单三层全覆盖
- 准入：需求评审通过 + 单元覆盖率 ≥ 70% + 构建产物可部署 + 测试环境就绪
- 准出：P0 用例 100% 通过 + P1 用例 ≥ 95% 通过 + 无 P0/P1 缺陷遗留 + 性能达标

### 示例 2：微服务项目分层比例争议（聚焦阶段 3）

**用户输入**：我们的微服务项目有 8 个服务，团队对单元测试和接口测试的比例有分歧，有人认为 UI 测试应该占 30%，请帮我制定分层策略

**skill 执行阶段**：
- 阶段 3 测试分层策略（直接聚焦，阶段 1-2 由用户已提供的项目特征简要带过）：
  - 微服务项目 → 接口契约层加厚，引用 [knowledge/test-pyramid.md](../knowledge/test-pyramid.md) 微服务档位：单元 60% / 接口 30% / UI 10%
  - 纠正 UI 30% 反例：UI 占比过高违反微服务以接口契约为边界的原则，UI 变更频繁会导致维护成本失控
  - 触发「分层比例争议」失败模式 Fallback：UI 占比争议按 UI 稳定性折算，UI 变更频繁 → 降 UI 占比
- 🔴 CHECKPOINT：展示分层策略 + 各层职责边界，等用户确认

**输出摘要**：
- 分层比例：单元 60% / 接口 30% / UI 10%（微服务档位）
- UI 30% 反例纠正：UI 占比过高违反微服务接口契约原则，维护成本失控
- 各层职责边界：单元层（函数逻辑）/ 接口层（8 个服务间契约）/ UI 层（用户旅程），禁止越界
- 工具类型推荐：单元层框架类型 × 1、接口层框架类型 × 1、UI 层框架类型 × 1

### 示例 3：金融系统准入准出 + 资源估算附录（阶段 4 + 阶段 5）

**用户输入**：金融系统上线测试，要求严格合规，请帮我制定准入准出标准，并估算测试团队需要多少人

**skill 执行阶段**：
- 阶段 4 范围与准入准出（金融档位，阈值严于通用 Web）：
  - 准入：需求评审通过 + 单元测试覆盖率 ≥ 85% + 代码静态扫描无高危 + 测试环境与生产配置对齐
  - 准出：P0 用例 100% 通过 + P1 用例 ≥ 95% 通过 + 无 P0/P1 缺陷遗留 + P99 RT ≤ 200ms + 安全扫描无高危 + 回归通过
- 阶段 5 资源与进度附录（用户明确要求估算人力，触发可选附录）：
  - 资源粗估：按各层测试用例数 × 单用例工时估算人天，引用 [knowledge/strategy-templates.md](../knowledge/strategy-templates.md) 附录模板
  - 里程碑式进度：按阶段 1-4 产物拆分里程碑，标注关键节点与依赖
  - 风险跟踪清单：列出策略执行风险项 + 跟踪人 + 跟踪频率

**输出摘要**：
- 准入 checklist：单元覆盖率 ≥ 85% + 静态扫描无高危 + 环境对齐
- 准出 checklist：P0 用例 100% 通过 + P99 RT ≤ 200ms + 安全扫描无高危 + 回归通过
- 资源估算：各层用例数 × 单用例工时 → 人天总数 → 团队人数建议
- 附录生成标注：用户明确要求，已生成资源与进度附录

## 与 testing-bundle 协同调用

本 skill 是 `testing-bundle` 的子 skill（项目级测试策略方向）。bundle 负责意图判断与路由，本 skill 负责项目级策略制定。

**协同流程**：

```
用户：帮我制定测试策略
testing-bundle → 意图判断：测试策略 → 路由到 test-strategy-engineer
test-strategy-engineer → 执行阶段 1~5
```

**路由规则**（由 testing-bundle 执行，本 skill 不感知）：

| 用户意图 | 路由目标 |
|----------|----------|
| 测试策略 / 测试计划 / 测试分层 / 风险矩阵 / 准入准出 / 测试金字塔 | test-strategy-engineer |
| 单功能测试用例生成 | test-case-engineer |
| 性能测试方案 / 瓶颈定位 | performance-test-engineer |
| 功能 Bug 根因分析 | bug-analyzer |

**层间转交**（本 skill 与 test-case-engineer / performance-test-engineer，由 bundle 衔接）：

| 转交方向 | 触发条件 | 携带内容 |
|----------|----------|----------|
| 本 skill → test-case-engineer | 阶段 4 完成，策略文档已确认 | 风险矩阵 + 分层策略 + 范围优先级 + 准入准出 |
| 本 skill → performance-test-engineer | 风险矩阵中标注性能风险项（如支付高并发、营销秒杀） | 性能风险模块清单 + 性能目标阈值（TPS/RT/错误率） |

## 单独安装时的能力边界

本 skill 单独安装（无 testing-bundle）时，行为边界如下：

| 能力 | testing-bundle 下 | 单独安装 |
|------|-------------------|----------|
| 入口路由 | bundle 自动判断意图并路由 | 用户直接调用本 skill |
| 与 test-case-engineer 转交 | bundle 自动衔接两 skill | 用户手动衔接：复制本 skill 输出的策略文档，作为 test-case-engineer 输入 |
| 与 performance-test-engineer 转交 | bundle 可调度 | 用户手动衔接：复制性能风险模块清单，作为 performance-test-engineer 输入 |

**单独使用触发方式**：用户直接给出测试策略 / 测试分层 / 风险矩阵 / 准入准出相关输入即可触发，无需 bundle 介入。

**转交需手动衔接的场景**：
- 本 skill 阶段 4 完成后输出策略文档转交提示（含风险矩阵 + 分层策略 + 范围优先级）。用户需手动将上述内容作为 test-case-engineer 的输入，本 skill 不会自行调用 test-case-engineer。
- 本 skill 阶段 2 风险矩阵中标注性能风险项时输出转交提示（含性能风险模块清单 + 性能目标阈值）。用户需手动将上述内容作为 performance-test-engineer 的输入。

## 与其他 skill 的边界

| 边界方向 | 说明 |
|----------|------|
| 本 skill → test-case-engineer | 本 skill 输出项目级策略（风险矩阵 + 分层策略 + 范围优先级），转交 test-case-engineer 按分层策略生成分层用例。本 skill 不生成单功能用例。 |
| 本 skill → performance-test-engineer | 本 skill 识别风险矩阵中的性能风险项（高并发、低延迟、大流量模块），转交 performance-test-engineer 设计性能方案。本 skill 不设计性能测试场景。 |
| 本 skill ✗ bug-analyzer | 本 skill 不做 Bug 根因分析。Bug 根因分析由 bug-analyzer 负责。 |

**粒度边界**：本 skill 是项目级（整体），test-case-engineer 是单功能级。本 skill 回答「测什么、怎么分层、资源怎么分」，test-case-engineer 回答「怎么测这个功能」。
