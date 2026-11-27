# performance-test-engineer

> 性能测试方案设计 + 资源/架构层瓶颈定位 skill，v1.2.6。
> testing-bundle 的性能测试方向子 skill。

## 适用场景

**适用**：性能测试方案设计、负载模型选择、性能瓶颈定位、容量评估、性能指标阈值制定。
**不适用**：功能用例生成（用 test-case-engineer）、功能 Bug 根因分析（用 bug-analyzer）、编写压测脚本（通用编码任务）。

## 核心能力

- **三条路径**：方案（阶段 1–2）、诊断（阶段 3–4）、两者都要（先诊断已有证据，再给复测方案）。
- **方案**：明确业务目标和依据，选择负载形状、到达方式、观测指标与停止条件；缺数据时给可确定部分和最小补采项。
- **诊断**：从同时间窗最强证据定位，按需查 USE 与对应瓶颈模式，结论区分已确认、候选和证据不足。
- 证据指向代码逻辑缺陷时转交 bug-analyzer；实际发压前核对环境、规模/时长、保护/停止条件与授权。

## 与其他 skill 的边界

本 skill 聚焦资源/架构层，bug-analyzer 聚焦代码逻辑层。

| 维度 | performance-test-engineer | bug-analyzer |
|------|---------------------------|--------------|
| 定位层 | 资源/架构层 | 代码逻辑层 |
| 输入 | 性能数据（CPU/IO/RT/TPS）、性能现象 | Bug 现象、错误日志、复现步骤 |
| 方法论 | USE 方法、资源三角、瓶颈传导链 | 5 Whys、鱼骨图、隔离定位 |
| 输出 | 瓶颈点 + 资源/架构优化建议 | 根因 + 代码修复建议 |
| 转交触发 | 证据指向代码逻辑缺陷（死锁、N+1、内存泄漏、连接未释放）→ bug-analyzer | 根因指向资源/架构瓶颈（连接池不足、扩容、缓存未命中、限流缺失）→ performance |

## 安装方式

- **推荐**：通过 [testing-bundle](../testing-bundle/) 整体安装，由 bundle 统一路由到本 skill。
- **单独安装**：本 skill 可独立使用；与 bug-analyzer 的转交需手动衔接（转交时携带瓶颈定位报告 + 性能数据 + 怀疑代码模块）。

## 知识库

| 文件 | 说明 |
|------|------|
| [knowledge/load-models.md](knowledge/load-models.md) | 负载形状、开放/封闭到达方式与容量 |
| [knowledge/metrics-framework.md](knowledge/metrics-framework.md) | 启动与完成口径、指标与阈值 |
| [knowledge/bottleneck-patterns.md](knowledge/bottleneck-patterns.md) | 6 类瓶颈模式库（CPU/IO/网络/锁/连接池/GC，含层边界声明） |
| [knowledge/use-method.md](knowledge/use-method.md) | USE 方法 + 资源三角 |

## 版本历史

- v1.2.6: 缩短方案与诊断流程，按证据与症状加载知识
- v1.2.5: 区分负载形状、到达方式与吞吐统计口径
- v1.2.4: 合并采集命令与阈值表，压缩指标框架/瓶颈模式；默认路径 18,726→15,491，USE 判定链保留
- v1.2.3: 去除快速上手示例补造的性能指标与瓶颈结论
- v1.2.2: 统一协作转交与方案披露规则
- v1.2.1: 区分性能异常容量边界并统一连续采集口径
- v1.1.1: 修正固定排查顺序和数据缺口边界；阶段细则下沉到 knowledge 并保留证据、授权和转交门禁
- v1.1.0: 新增默认值兜底与意图切换（plan/diagnose/plan-and-diagnose）；阈值以 metrics-framework.md 为权威源
- v1.0.0: 初始版本，作为 testing-bundle 的性能测试方向子 skill
