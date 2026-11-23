---
name: test-case-engineer
version: 9.16.0
description: >-
  Use when generating, reviewing, or designing test cases and single-feature
  test strategies.
  Triggers on: 测试用例、测试点、用例评审、单功能测试策略、需求分析、QA.
  For bug root cause analysis or defect localization, use bug-analyzer instead.
  For project-level test strategy or test layering, use test-strategy-engineer instead.
keywords:
  - QA
  - 测试用例
  - 测试点
  - 用例评审
  - 单功能测试策略
  - AI赋能
  - Prompt策略
  - 需求结构化
---

# 测试用例工程师 Skill

理解需求 → 提取测试点 → 输出精炼可判定的测试用例。本文件为入口索引，属 `testing-bundle` 正向用例生成子 skill。

## 协同与边界

- Bug 根因分析、缺陷定位、复现、5 Whys → 转 `bug-analyzer`（完成后需防御性用例再转回）。
- 要求状态机建模/流转穷举 → 先转 `state-machine-test-engineer` 产出场景清单，本 skill 落步骤级用例；普通状态字段直接在本 skill 扫描。
- 需离线批量造数文件（CSV/JSON/SQL）→ 交 `test-data-generator`，用例正文仍须单条数据自包含。

## 模式选择与切换

工作流：`阶段 1 理解需求 → 阶段 2 提取测试点 → 阶段 3 编写用例 → 阶段 4 自检补全`（见 [test-case-engineer-core.md](test-case-engineer-core.md)）。模式切换：默认/快速/回归验证清单/探索式/评审/需求评审 6 种模式。

- **默认**：多规则约束、状态机、涉资金/权限/并发/第三方，或跨模块联动 >2 处时走完整四阶段。
- **快速**：单字段纯校验（无联动/状态机/资金）或用户要求快速；压缩阶段 1/4，必出测试点清单并跑脚本校验。
- **回归验证清单**：纯重构无行为变更，跳过阶段 1/2 直接列验证项。
- **探索式**：四阶段外并列输出探索章程。
- **评审**：输入已有用例或触发「评审/review/检查质量」，不走四阶段；>100 条叠加 [knowledge/large-scale-review.md](knowledge/large-scale-review.md)，汇报叠加 [knowledge/review-plan.md](knowledge/review-plan.md)。
- **需求评审**：输入 PRD/需求文档找需求问题，不走四阶段，不直接写用例。

**输出铁律**：以 `### TC_模块_功能_序号: 标题` 块承载，**禁整表罗列全部用例**（表格仅限块内同构 P2/P3 组）。先过场景淘汰门，再按句法槽位、≤60 汉字与单分号红线编写，输出前做删词脱水测试。

## 模式路由与按需知识索引

`$SKILL_ROOT` = 本目录；跑 shell 前必读 [integrations/quickstart.md](integrations/quickstart.md)。评审首轮只读 `review-mode` + `test-standards`；需求评审只读 `requirement-review`（有项目目录加读 `project-knowledge`）。

| 模式 | 必读主路径 |
|------|------------|
| **默认 / 快速** | 阶段 1：[test-case-engineer-core.md](test-case-engineer-core.md) + [knowledge/project-knowledge.md](knowledge/project-knowledge.md) → 阶段 2：[knowledge/scope-discipline.md](knowledge/scope-discipline.md) + [knowledge/case-arrangement.md](knowledge/case-arrangement.md)（跑 [scripts/validate_points.py](scripts/validate_points.py)）→ 阶段 3：[knowledge/writing-rules.md](knowledge/writing-rules.md) + [knowledge/test-standards.md](knowledge/test-standards.md) → 阶段 4：跑 [scripts/validate_cases.py](scripts/validate_cases.py) |
| **回归验证清单 / 探索式** | [test-case-engineer-core.md](test-case-engineer-core.md) 对应章节 |
| **评审** | [knowledge/review-mode.md](knowledge/review-mode.md) + [knowledge/test-standards.md](knowledge/test-standards.md) |
| **需求评审** | [knowledge/requirement-review.md](knowledge/requirement-review.md)（跑 [scripts/validate_requirement_review.py](scripts/validate_requirement_review.py) `--prd`） |

**按需延迟加载（未命中禁预读）**：
- **阶段 1/2**：有产品读 [knowledge/products/](knowledge/products/)（[knowledge/products/README.md](knowledge/products/README.md)）；命中封顶/通配符/模板/上传/安全查 [knowledge/bug-patterns.md](knowledge/bug-patterns.md)；有 NPE/500/超时史查 [knowledge/runtime-error-patterns.md](knowledge/runtime-error-patterns.md)。
- **阶段 3**：正反锚点 [knowledge/writing-examples.md](knowledge/writing-examples.md)；句式细则 [knowledge/readability.md](knowledge/readability.md)；超时/重试/幂等/`traceability` 契约 [knowledge/failure-semantics.md](knowledge/failure-semantics.md)。
- **阶段 4 与扩展**：排障 [knowledge/anti-patterns.md](knowledge/anti-patterns.md)；效率 [knowledge/efficiency-metrics.md](knowledge/efficiency-metrics.md)；盲评 [knowledge/review-rubric.md](knowledge/review-rubric.md)；R3 模板/增量 [knowledge/review-reference.md](knowledge/review-reference.md)；R2 抽事实 [knowledge/prompt-strategy.md](knowledge/prompt-strategy.md)。

## 执行原则

默认连续交付；仅缺关键输入、范围改变、涉未授权写操作或用户要求审阅时暂停确认。`review-checker` MCP 可选，不影响 `validate_cases.py` 交付闸门。
