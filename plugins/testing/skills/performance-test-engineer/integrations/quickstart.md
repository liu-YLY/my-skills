# 快速上手

> **何时阅读**：首次使用本 skill 或需快速了解触发方式与协同调用时查阅。
> **覆盖范围**：SKILL_ROOT 路径 / 触发示例 / testing-bundle 协同 / 单独安装边界。
> **可跳过条件**：已熟悉本 skill 触发与层间转交规则。

## SKILL_ROOT

在本仓库中：`SKILL_ROOT` = `skills/performance-test-engineer`

> 下文命令中的 `$SKILL_ROOT` 是占位符，**Agent 执行命令时必须替换为上述实际路径**。
> 人在终端使用时，先执行 `export SKILL_ROOT=skills/performance-test-engineer`，或手动将 `$SKILL_ROOT` 替换为实际路径。

> 路径禁止误写为 `.cursor/skills/performance-test-engineer` 或 `~/.claude/skills/performance-test-engineer`。本 skill 随仓库分发，路径以仓库内 `skills/performance-test-engineer` 为准。

## 快速触发示例

### 示例 1：电商下单接口性能测试方案（正向方案设计）

**用户输入**：我们有一个电商下单接口，日常 QPS 约 500，大促峰值预计 3000 QPS，SLA 要求 P99 响应时间 ≤ 800ms，请帮我设计性能测试方案

**skill 执行阶段**：
- 阶段 1 性能需求理解：提炼目标 TPS=3000、P99 RT ≤ 800ms、错误率 ≤ 0.1%（支付类阈值）
- 阶段 2 测试场景设计：选峰值模型 + 容量模型，输出场景清单与指标阈值表
- 🔴 CHECKPOINT：展示完整方案，等用户确认
- 阶段 3/4：本例为正向方案设计，无性能数据，跳过

**输出摘要**：
- 负载模型：峰值测试（验证大促瞬时峰值）+ 容量测试（找可持续承载 TPS）
- 场景清单：基准（单用户基线）→ 负载（3000 QPS 验证达标）→ 压力（找崩溃点）→ 稳定性（4h 长跑验证内存泄漏）
- 指标阈值表：TPS ≥ 3000、P99 RT ≤ 800ms、P999 RT ≤ 1600ms、错误率 ≤ 0.1%、CPU ≤ 70%、内存 ≤ 80%

### 示例 2：TPS 上不去 + CPU 低的瓶颈定位（逆向）

**用户输入**：线上接口 TPS 上不去，加压到 800 就开始报超时，CPU 才 40%，请帮我定位瓶颈

**skill 执行阶段**：
- 阶段 3 瓶颈定位（逆向触发）：现象收集（TPS 800 停滞、RT 陡增、CPU 40%）
- 分层排查（按序，禁止跳层）：
  - 应用层：GC 频率、线程状态、连接池占用、慢 SQL
  - 资源层：USE 方法，CPU 40% 未饱和排除 CPU；排查连接池/IO/网络饱和度
  - 架构层：DB 连接池规格、缓存命中、限流配置
- 阶段 4 转交判断

**输出摘要**：
- 瓶颈层：资源层 - 连接池饱和
- 证据链：TPS 800 停滞 + RT 陡增 + CPU 40% 未饱和 + 连接池占用 100%
- 优化建议：连接池扩容；同步排查 DB 是否有慢 SQL 拖累连接释放
- 转交判断：若 DB 慢 SQL 为根因（代码逻辑层）→ 转交 bug-analyzer

### 示例 3：P95 RT 陡增但 CPU/内存正常（复杂场景）

**用户输入**：我们的系统最近加压测试时发现 P95 响应时间在并发 500 时从 200ms 陡增到 2s，但错误率没变，CPU/内存都正常，请分析原因

**skill 执行阶段**：
- 阶段 3 瓶颈定位：现象收集（P95 陡增、CPU/内存正常、错误率不变）
- 分层排查：
  - 应用层：GC 频率、线程阻塞、锁竞争
  - 资源层：CPU/内存未饱和，重点排查磁盘 IO（await/svctm）、网络（带宽/包量）
  - 架构层：缓存命中陡降、DB 锁等待、限流触发
- 对照 [knowledge/bottleneck-patterns.md](../knowledge/bottleneck-patterns.md) 6 类瓶颈模式匹配

**输出摘要**：
- 根因候选清单（按优先级）：
  1. 磁盘 IO 饱和（await 飙升）→ 检查 IO 等待采样
  2. 锁竞争（线程阻塞陡增）→ 抓线程 dump
  3. 缓存命中率下降（DB 查询陡增）→ 检查缓存失效与穿透
  4. GC 停顿（FullGC 频率上升）→ 检查 GC 日志
- 转交判断：若根因为锁竞争或 GC 停顿（代码逻辑层）→ 转交 bug-analyzer

## 与 testing-bundle 协同调用

本 skill 是 `testing-bundle` 的子 skill（性能测试方向）。bundle 负责意图判断与路由，本 skill 负责性能测试执行。

**协同流程**：

```
用户：帮我设计性能测试方案
testing-bundle → 意图判断：性能测试 → 路由到 performance-test-engineer
performance-test-engineer → 执行阶段 1~4
```

**路由规则**（由 testing-bundle 执行，本 skill 不感知）：

| 用户意图 | 路由目标 |
|----------|----------|
| 性能测试 / 负载测试 / 压力测试 / 瓶颈定位 / 容量评估 | performance-test-engineer |
| 功能用例生成 | test-case-engineer |
| 功能 Bug 根因分析 | bug-analyzer |

**层间转交**（本 skill 与 bug-analyzer，由 bundle 衔接）：

| 转交方向 | 触发条件 | 携带内容 |
|----------|----------|----------|
| 本 skill → bug-analyzer | 瓶颈指向代码逻辑缺陷（死锁、N+1 查询、内存泄漏、锁竞争、算法低效） | 瓶颈定位报告 + 已收集性能数据 + 怀疑代码模块 |
| bug-analyzer → 本 skill | 根因指向资源/架构瓶颈（连接池不足、扩容需求、缓存未命中、DB 分库分表、限流缺失） | 根因报告 + 资源/架构层怀疑点 |

## 单独安装时的能力边界

本 skill 单独安装（无 testing-bundle）时，行为边界如下：

| 能力 | testing-bundle 下 | 单独安装 |
|------|-------------------|----------|
| 入口路由 | bundle 自动判断意图并路由 | 用户直接调用本 skill |
| 与 bug-analyzer 转交 | bundle 自动衔接两 skill | 用户手动衔接：复制本 skill 输出的瓶颈定位报告，作为 bug-analyzer 输入 |
| 与 test-case-engineer 协同 | bundle 可调度 | 用户手动衔接 |

**单独使用触发方式**：用户直接给出性能测试 / 瓶颈定位相关输入即可触发，无需 bundle 介入。

**转交需手动衔接的场景**：本 skill 阶段 4 判定瓶颈指向代码逻辑缺陷时，输出转交提示（含瓶颈定位报告 + 怀疑代码模块）。用户需手动将上述内容作为 bug-analyzer 的输入，本 skill 不会自行调用 bug-analyzer。
