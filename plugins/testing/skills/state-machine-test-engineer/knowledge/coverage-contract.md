# 覆盖率与失败语义契约（按需）

> **何时阅读**：调用 MCP `check_coverage`、需要输出覆盖报告、或处理失败阶段/结果未知时读取。
> **不在默认路径**：阶段 4 只生成场景清单时不读；默认只使用 [scenario-types.md](scenario-types.md) 的生成规则。

## 覆盖报告三态

覆盖报告保留 `scenario_type_coverage`（类型条数）和 `missing_scenario_types`（零计数类型）的旧描述性含义；新增 `applicable_missing_scenario_types / not_applicable_scenario_types / unknown_scenario_types` 分别表示适用但缺场景、不适用、尚未确定适用性。完成判断使用新三态信息，不能把待确认候选算成已验证业务行为。

`applicable_missing_scenario_types` 只认可结构匹配、目标已明确且依据非待确认的场景；错误 legal/illegal 目标与 pending 候选不代表已处理。旧类型计数保留所有输入场景的描述性含义。

## 失败阶段与不确定结果

转换可选 `failure_outcomes`、场景可选 `failure_semantics`，默认不要求旧输入提供。每项包含 `phase/allowed_states/forbidden_side_effects/observations/recovery_conditions/source/evidence_type`；阶段是 `pre_execution_rejected/pre_commit_failed/committed_response_lost/partial_success/unknown`。只有已核实提交才选响应丢失阶段；普通超时保留 unknown。phase 为 unknown 时即使只有一个允许态且来源标签明确，目标仍为待确认，不以该集合推断提交边界已知。允许态为多元素集合时目标 `待确认` 并说明条件，不能伪造复合状态名。副作用、幂等键、时限和补偿动作均需需求依据。先核实业务记录与外部结果，再依据重试政策决定动作；结果未知不能生成无条件重试。缺少失败资料仅给 unknown 候选，不能自动认定原态未变。

## 分层覆盖契约

`check_coverage` 增加末尾可选 `context`，旧调用不变。context 可提供 requirement_baseline/design_baseline/case_baseline（source/version/items）、requirement_links（item_id/scenario_ref/confirmation）及 execution_records（case_id/baseline_version/run_id/status/evidence_ref）。需求关联只有 confirmed 且场景目标/依据已确定才计入；场景设计基线由已确认适用场景集合提供，不从条数猜分母。无基线为 `not_assessed`、数值 null；显式空基线为 `not_applicable`、分母 0 且比例 null。

layers 分别报告 requirements/model/scenario_design/execution/execution_pass，每层带 status、分子分母、比例、基线来源版本及未评估项。旧 transition/forbidden 比例与分母保持。执行覆盖和通过率分开，仅使用对应版本、实际执行且有证据引用的记录；重复证据不重复计数，同一用例同一运行结果冲突单列未评估。设计完成但未执行不能声称通过；业务待确认场景不计已确定覆盖。`export_artifacts` 可选 coverage_report 将层级结果带入 Markdown/JSON。

执行记录新增可选 `evidence_status`，缺省 unknown；verified 还需明确 `evidence_check_source` 记录核验依据。未提供 execution_records 表示未评估，显式 [] 表示该基线尚无执行记录；空用例基线表示不适用。只有调用方明确核验为 verified 且有非占位证据引用才计已执行，MCP 不自行验证文件/远端引用内容。未知或不可达证据、旧基线版本不计入分子。需求/设计层同时列未确定关联项；失败阶段 unknown 或依据待确认不计已确定场景覆盖。

新 model 层独立统计依据已确定且完整匹配的合法转换；场景或转换仍待确认不计分子，legacy transition_coverage 仍保留原结构覆盖口径。

执行通过层比例是「已确认通过用例数 / 已核实执行用例数」。同一用例同一基线存在声称 passed/failed 但证据未核实的运行时，不计已确认通过；已有核实运行仍计执行覆盖，未评估项保留。未知不等于失败，不能由此反算失败率。其他基线的记录不影响当前基线用例结论，撤去失败证据不能提升确认等级。

失败恢复只在明确单一 allowed_states 与目标一致时计已确定设计；未给集合、集合条件未确定或目标冲突均列缺口。场景先按 from/event/完整守卫/可选 transition_id 唯一关联；匹配转换未声明 failure_outcomes 时可使用场景本身的明确单一失败事实，添加无关转换的结果不改变结论。匹配转换已声明 failure_outcomes 时，并匹配阶段、允许态、禁止副作用、观测与恢复条件；错误引用不能绕过模型依据，待确认模型结果不得由场景标签升级。该检查不改变旧转换/禁止覆盖分母。
