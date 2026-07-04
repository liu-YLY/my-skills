# USE 方法

> **何时阅读**：资源层瓶颈定位阶段，需要系统性检查 CPU/内存/IO/网络信号时查阅。
> **覆盖范围**：USE 三维定义 / 四类资源检查项 / 三层排查顺序 / 与瓶颈模式的对应关系。

## 1. 方法定义

USE 方法（Utilization / Saturation / Errors）由 Brendan Gregg 提出，用于系统性资源瓶颈定位。对每个资源检查三个维度：

- **Utilization（利用率）**：资源忙于工作的平均时间比例（如 CPU 利用率 80%）
- **Saturation（饱和度）**：资源排队/等待程度（如 runqueue 长度、IO 队列深度）
- **Errors（错误）**：错误计数（如网络重传、磁盘错误、OOM）

**核心原则**：三者都要查，不能只看利用率。利用率高不一定饱和，饱和不一定有错误，但有错误一定有问题。

## 2. 资源三角：四类资源的 USE 检查项

| 资源 | Utilization | Saturation | Errors |
|------|-------------|------------|--------|
| **CPU** | CPU 利用率（总体+单核） | runqueue 长度、上下文切换 | 无（CPU 无错误概念，可看软中断速率） |
| **内存** | 已用/总内存 | swap 使用、页换入换出、OOM 触发 | OOM kill 次数、malloc 失败 |
| **磁盘 IO** | 磁盘利用率%、IOPS | 队列深度、iowait、await | 磁盘错误、I/O error |
| **网络** | 带宽利用率% | 重传率、TCP 重传、丢包 | rx/tx errors、dropped |

### 采集命令参考

| 资源 | 命令/工具 |
|------|-----------|
| CPU | `top`、`mpstat -P ALL 1`、`pidstat 1`、`perf top` |
| 内存 | `free -m`、`vmstat 1`、`sar -B 1`、`jstat -gcutil <pid> 1s`（GC） |
| 磁盘 | `iostat -x 1`、`sar -d 1`、`iotop` |
| 网络 | `sar -n DEV 1`、`netstat -s`、`ifconfig`、`ethtool -S <iface>` |

**关键指标阈值参考**：

| 指标 | 命令 | 告警阈值 |
|------|------|----------|
| CPU 利用率 | `mpstat` %usr+%sys | 单核持续 >90% |
| runqueue 长度 | `vmstat` r 列 | > CPU 核数 × 1 |
| iowait | `mpstat` %iowait | >20% |
| 磁盘 await | `iostat -x` await | >20ms（HDD）/ >10ms（SSD） |
| 队列深度 | `iostat -x` avgqu-sz | >2 持续 |
| swap 使用 | `free` Swap used | >0（任何 swap 都需排查） |
| TCP 重传率 | `netstat -s` retransmits | >1% |
| 内存使用率 | `free` used/total | >85% 触发排查 |

## 3. 排查顺序

自上而下三层，禁止跳层：

| 层级 | 检查内容 | 典型指标 |
|------|----------|----------|
| 1. 应用层 | 应用自身指标 | RT、TPS、错误率、GC、线程状态、连接池 |
| 2. 资源层 | CPU/内存/IO/网络 USE 信号 | 见第 2 节四类资源检查项 |
| 3. 架构层 | 依赖链 | DB、缓存、下游服务、网络拓扑 |

**原则**：不跳层。跳过资源层直接猜架构问题等于猜测——没有资源层数据支撑的架构判断没有依据。

**执行步骤**：
1. 应用层确认现象（RT 是否真的高？哪类接口慢？错误率多少？）
2. 资源层按 USE 三维逐项采集（CPU→内存→IO→网络顺序）
3. 资源层定位到瓶颈信号后，再下沉到架构层查依赖
4. 若资源层全正常，回到应用层做代码级 profiling（如 perf、async-profiler）

## 4. 与 bottleneck-patterns.md 的对应关系

USE 信号定位后，按以下表对应到具体瓶颈模式：

| USE 信号 | 对应瓶颈模式 | 说明 |
|---------|-------------|------|
| CPU 利用率高 + runqueue 长 | CPU 飙升 | 见 bottleneck-patterns.md 模式 1 |
| iowait 高 + IO 队列深 | IO 等待 | 见模式 2 |
| 网络重传率高 | 网络延迟 | 见模式 3 |
| 线程阻塞多（饱和） | 锁竞争 | 见模式 4 |
| 连接池使用率高（饱和） | 连接池耗尽 | 见模式 5 |
| GC 频繁 + 堆满（饱和） | GC 停顿 | 见模式 6 |

**对应逻辑**：USE 方法提供「资源层信号」，瓶颈模式提供「成因假设与验证路径」。先有 USE 信号，再查对应模式，不能反向套用。

## 5. 反例（不要这样做）

| 反例 | 问题 | 正确做法 |
|------|------|----------|
| 跳过资源层直接猜架构问题 | 没有资源层数据支撑的架构判断是猜测 | 先完成资源层 USE 三维采集 |
| 只看 Utilization 不看 Saturation | CPU 60% 但 runqueue 已很长，仍是瓶颈 | 三维必须全查 |
| 只看单类资源 | 性能瓶颈常是多资源耦合（如 IO 慢导致 CPU 等待） | 四类资源全查，关注耦合 |
| 用 USE 方法分析代码逻辑缺陷 | USE 只适用于资源/架构层 | 代码逻辑层用 bug-analyzer skill |

## 6. 与其他知识库的关系

- **bottleneck-patterns.md**：USE 信号 → 瓶颈模式的映射（见第 4 节）
- **bug-analyzer / root-cause-frameworks.md**：资源层排除后，代码逻辑缺陷用根因分析框架
- **test-case-engineer**：基于 USE 信号设计压测用例时，转交生成完整用例
