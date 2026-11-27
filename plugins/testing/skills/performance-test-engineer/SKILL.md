---
name: performance-test-engineer
version: 1.2.7
description: >-
  Use when designing performance test plans or analyzing performance bottlenecks.
  Triggers on: 性能测试、负载测试、压力测试、并发测试、TPS、响应时间、瓶颈、性能瓶颈、容量评估、USE方法.
  For functional bug root cause analysis, use bug-analyzer instead. For functional test case generation, use test-case-engineer instead.
  Writing or debugging load-test scripts alone is a general coding task, not this skill.
keywords:
  - 性能测试
  - 负载测试
  - 压力测试
  - 并发测试
  - 瓶颈定位
  - 性能瓶颈
  - USE方法
  - TPS
  - 响应时间
  - 容量评估
---

# 性能测试工程师

按用户目标选择路径。已有数据的只读分析可直接进行；实际发压、修改配置或写环境前，先核对目标环境、规模与时长、保护/停止条件、授权范围与责任人。

| 用户目标 | 执行 | 按需读取 | 交付 |
|---|---|---|---|
| 设计方案（plan） | 阶段 1→2 | [metrics-framework.md](knowledge/metrics-framework.md) §1–2、§4；[load-models.md](knowledge/load-models.md) | 目标与假设、负载与场景、指标与采集、停止与恢复、风险与待确认 |
| 定位瓶颈（diagnose） | 阶段 3→4 | [use-method.md](knowledge/use-method.md)；[bottleneck-patterns.md](knowledge/bottleneck-patterns.md) 对应项 | 现象与窗口、证据与排除、结论状态、补采或复测、转交判断 |
| 两者都要（plan+diagnose） | 先阶段 3→4，再阶段 1→2 | 按缺口加载 | 分开陈述诊断结论与复测方案 |

**阶段 1 需求与指标**：记录业务场景、流量来源、环境、目标与依据。缺数据时只给可确定部分和最小补采项，未确认阈值标「待定」。用指标框架对齐单位、统计边界、观测窗口和达标依据，区分已测值、估算与待验证项。

**阶段 2 负载与场景**：按目标选负载形状与开放/封闭到达方式，写明流量配比、数据、预热与稳态、停止与恢复条件。数字仅为设计示例，按业务周期、基线与保护条件确定。

**阶段 3 瓶颈定位**：对齐同一时间窗的实际流量、延迟分位、错误与相关资源。到达率或吞吐异常时，按负载模型和指标框架 §1.1 核对计量对象、计划/实际发起、完成量与发压能力。按最强证据选起点；需要资源饱和证据时查 USE，已缩小到某类现象时查对应瓶颈模式；用资源、队列、时序与对照区分发压机、服务、网络和依赖，避免把单个指标当根因。

**阶段 4 归属与转交**：

- 异常观测、超过已确认 SLA、测得容量边界分别说明；只有零散指标时给候选、最小补采与判定信号，不得输出已确认瓶颈。
- 缺 TPS 时不得推断吞吐拐点或资源饱和；但 USE 三维齐备且时间窗一致时，可报告已观测到的资源饱和，容量与拐点仍待吞吐证据。
- 停止加压不能证明容量上限；无基线不能按生产规格倍数外推。
- 优化建议对应证据并附复测指标；证据指向代码逻辑缺陷时，携带数据、链路与可疑模块转交 `bug-analyzer`。

## 交付与边界

- **方案**：说明适用环境、假设与待确认项、风险；用户只要方案时到此结束。
- **诊断**：结论只能是「已确认瓶颈 / 候选原因 / 证据不足」，未执行项写清原因。
- **不适用**：功能 Bug 根因（bug-analyzer）、功能用例（test-case-engineer）、单独编写压测脚本或 CI 配置（通用编码任务）。

[使用说明](README.md) · [示例](integrations/quickstart.md)
