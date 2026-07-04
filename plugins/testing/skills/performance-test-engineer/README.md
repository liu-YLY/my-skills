# performance-test-engineer

> 性能测试方案设计 + 资源/架构层瓶颈定位 skill，v1.0.0。
> testing-bundle 的性能测试方向子 skill。

## 适用场景

**适用**：性能测试方案设计、负载模型选择、性能瓶颈定位、容量评估、性能指标阈值制定。
**不适用**：功能用例生成（用 test-case-engineer）、功能 Bug 根因分析（用 bug-analyzer）、编写压测脚本（通用编码任务）。

## 核心能力

4 阶段工作流（含 🔴 CHECKPOINT 强制确认点）：

```
阶段 1 性能需求理解 → 阶段 2 测试场景设计 → 🔴 CHECKPOINT → 阶段 3 瓶颈定位 → 阶段 4 转交判断
```

- **阶段 1 性能需求理解**：提炼性能目标（TPS / RT / 并发数 / 错误率），估算关键指标初值。
- **阶段 2 测试场景设计**：选择负载模型（基准/负载/压力/稳定性/容量），设计场景，确定指标阈值。
- **🔴 CHECKPOINT**：阶段 2 完成后展示完整方案给用户确认，未确认前禁止进入阶段 3。
- **阶段 3 瓶颈定位**：按"应用层→资源层→架构层"顺序排查，应用 USE 方法，对照瓶颈模式库，输出瓶颈定位报告。
- **阶段 4 转交判断**：判断瓶颈归属层，资源/架构层由本 skill 给优化建议，代码逻辑缺陷转交 bug-analyzer。

## 与其他 skill 的边界

本 skill 聚焦资源/架构层，bug-analyzer 聚焦代码逻辑层。

| 维度 | performance-test-engineer | bug-analyzer |
|------|---------------------------|--------------|
| 定位层 | 资源/架构层 | 代码逻辑层 |
| 输入 | 性能数据（CPU/IO/RT/TPS）、性能现象 | Bug 现象、错误日志、复现步骤 |
| 方法论 | USE 方法、资源三角、瓶颈传导链 | 5 Whys、鱼骨图、隔离定位 |
| 输出 | 瓶颈点 + 资源/架构优化建议 | 根因 + 代码修复建议 |
| 转交触发 | 定位到代码逻辑缺陷 → bug-analyzer | 定位到资源/架构瓶颈 → performance |

## 安装方式

- **推荐**：通过 [testing-bundle](../testing-bundle/) 整体安装，由 bundle 统一路由到本 skill。
- **单独安装**：本 skill 可独立使用；与 bug-analyzer 的转交需手动衔接（转交时携带瓶颈定位报告 + 性能数据 + 怀疑代码模块）。

## 知识库

| 文件 | 说明 |
|------|------|
| [knowledge/load-models.md](knowledge/load-models.md) | 负载模型决策表（基准/负载/压力/稳定性/容量） |
| [knowledge/metrics-framework.md](knowledge/metrics-framework.md) | 指标体系 + 阈值参考 |
| [knowledge/bottleneck-patterns.md](knowledge/bottleneck-patterns.md) | 6 类瓶颈模式库（含层边界声明） |
| [knowledge/use-method.md](knowledge/use-method.md) | USE 方法 + 资源三角 |

## 版本历史

- v1.0.0: 初始版本，作为 testing-bundle 的性能测试方向子 skill
