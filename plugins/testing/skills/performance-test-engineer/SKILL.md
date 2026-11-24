---
name: performance-test-engineer
version: 1.2.6
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

# 性能测试工程师

按用户目标交付方案、定位或两者。只读分析可直接继续。实际发压、配置修改和其他环境写入前核对授权与范围。这里负责测试设计及诊断。

## 设计方案

- 记录业务场景、流量、环境、目标与来源。缺数据时给能确定的方案和最小补采项，未确认阈值标待定。
- 按 [load-models.md](knowledge/load-models.md) 选负载形状、到达方式和配比，写清数据、稳态、停止与恢复条件。用 [metrics-framework.md](knowledge/metrics-framework.md) 对齐单位、观测窗口和达标依据。按目标选择指标，区分已测值、估算和待验证项。
- 交付方案时说明适用环境、风险与待确认事项。用户只要方案时到此结束。

## 定位现象

- 对齐同一窗口的实际流量、延迟分位、错误和相关资源。到达率或吞吐异常时，查负载模型和指标框架 §1.1，明确计量对象、发起与完成及发压能力。
- 由最强证据定位。需要核对资源饱和时读 [use-method.md](knowledge/use-method.md)，已缩小到某类现象时查 [bottleneck-patterns.md](knowledge/bottleneck-patterns.md) 对应项。用资源、队列、时序与对照区分发压机、服务、网络和依赖，避免把单个指标当根因。
- 缺 TPS 时不得推断吞吐拐点或资源饱和。仅有零散指标时给候选、最小补采与判定信号，不得输出已确认瓶颈。观测到异常、超过已确认 SLA、测得容量边界分别说明。停止加压不能证明容量上限，无基线也不能按生产规格倍数外推。
- 优化建议对应证据并附复测指标。证据指向代码逻辑缺陷时，将数据、链路和可疑模块转交 `bug-analyzer`。

[使用说明](README.md) · [示例](integrations/quickstart.md)
