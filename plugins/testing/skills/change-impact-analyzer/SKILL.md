---
name: change-impact-analyzer
version: 1.5.4
description: >-
  Derives business impact scope and actionable test content from git diffs, patches,
  or code change points, even without existing test cases. Explains each affected
  business operation through its call chain, trigger conditions and consequences,
  and selects test methods and evidence. With optional cases or requirements,
  checks coverage gaps and implementation conflicts. Use for 变更影响分析、代码改动影响范围、
  根据改动生成测试内容和方式、为什么影响这个业务、diff 分析、回归风险.
keywords:
  - 变更影响分析
  - 代码改动检查
  - 测试用例影响
  - 覆盖缺口
  - diff 分析
  - 回归风险
  - change impact
  - 变更测试范围
  - 影响链路分析
  - 影响范围和测试内容
---

# 变更影响分析师

从实际业务动作交付「改动与触发条件 → 影响与依据 → 具体怎么测」。仅按给定片段作简要分析时直接回答，标来源和待核实项。随附 PR 链接只作来源，无需再读采集指南。根据需要再读取：

| 需要解决的问题 | 读取 |
|------|------|
| 比较版本、PR/MR、多个仓库、Git 采集 | [diff-modes.md](knowledge/diff-modes.md) 对应小节。PR 按 §1.2 固定仓库身份与比较点。 |
| 链路、契约、风险或覆盖关联需深入核对 | [cross-impact-analysis.md](knowledge/cross-impact-analysis.md) 对应小节。用例基线可读时按 §5 核对。 |
| 用户要求完整业务方案或详细追溯 | [业务方案模板](templates/business-impact-test-scope.md)；需要风险/场景或追溯表细则时查 [report-template.md](knowledge/report-template.md)，需要示例时查 [report-example.md](knowledge/report-example.md)。 |
| 采样、格式不明或资料中断 | [anti-patterns.md](knowledge/anti-patterns.md) 对应项。 |

1. **定范围。** 用已给 diff、patch、前后片段或改动点，注明来源、比较版本、已读和不可达范围。仅改动描述时标未核对源码，缺全部依据才追问。分析保持只读，工作区干净且 feature 分支领先默认分支时核对 `<default>...HEAD`。固定 ref 不可用时按已得材料交付，披露缺口。敏感值与对外材料须脱敏。
2. **查关系。** 从改动点反向找业务入口，再正向确认实际调用或消费。契约两侧均需核对，缺证据列候选，不凭同名、导入或共享字段确认。分别说明直接改动与间接影响。复杂分析用 `change_id` 关联变更、证据和场景，Git 状态缺元数据时为 `unknown`。配置、锁文件、测试依赖与覆盖变更按实际作用纳入，风险与排除均给依据。
3. **给测试内容。** 写可执行的操作、触发条件和观察结果。按需选择业务入口、单元分支、真实数据库或跨服务验证，核对失败前已发生的写入和副作用。区分代码观察、已确认业务预期和待确认。有需求则追加实现对照，有用例则核对步骤与断言。仅有旧版本通过记录时保留为历史证据。无可读用例标「既有覆盖未评估」，实现、覆盖和执行分别报告。

默认在对话交付，写文件或外部文档按用户要求与授权。需要完整新用例时转 `test-case-engineer`，先定位缺陷根因时转 `bug-analyzer`。

[使用说明](README.md)
