# 规范语句清单：state-machine-test-engineer

> 由 `scripts/extract-rule-inventory.py` 生成。分类为启发式初筛，删除/移位前必须人工复核。
> 共 155 条：D1 重复 52 / D2 移位 0 / D3 冲突 0 / D4 参考 25 / D5 行为 78

| ID | 位置 | 规范语句 | 类别 | 判定依据 | 处置 | 复核 |
|---|---|---|---|---|---|---|
| state-machine-test-engineer-001 | `SKILL.md:32` | > ✅ **MCP Server 状态说明**：本仓库 MCP 协议层（stdio + streamable-http）已有真实调用回归；当前宿主须暴露兼容工具才可使用增强模式。`build_state_machine` 为确定性实现（行业模板加载，不内置 LLM）。未安装或调用失败时 skill 仍自动降级为独立模式（输出首行标 `⚠ 独立模式（未校验）`）。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-002 | `SKILL.md:39` | - PRD 描述了"对象处于什么状态、允许什么变化、哪些操作必须被拒绝" | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-003 | `SKILL.md:51` | PRD 通常只描述"用户做什么"，没有显性表达"对象处于什么状态、允许什么变化、哪些操作必须被拒绝"。本 skill 用状态机作为业务建模语言，让测试设计从"功能点罗列"升级为"状态网络穷举"。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-004 | `SKILL.md:61` | \| 阶段 \| 输入 \| 必须输出 \| 门禁 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-005 | `SKILL.md:64` | \| 2. 状态机建模 \| 阶段 1 结果 \| 状态、转换、守卫、副作用、不变量、禁止转换 \| 状态用名词、事件用动词；每条规则标依据类型 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-006 | `SKILL.md:68` | \| 5. MCP 增强 \| 模型与场景 \| 校验状态、差异和最终产物 \| MCP 仅复核；不可用或失败必须显式降级 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-007 | `SKILL.md:89` | 模型 Schema 见 &#91;state-modeling.md&#93;(knowledge/state-modeling.md)，场景完整 Schema 见 &#91;scenario-types.md&#93;(knowledge/scenario-types.md)。入口只保留跨阶段和下游必须稳定的字段： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-008 | `SKILL.md:92` | - 每条转换与禁止规则必须包含 `evidence_type` 和 `source`；未知业务规则标 `待确认`，不得伪造目标状态。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-009 | `SKILL.md:126` | > **阶段隔离原则**：建模阶段（阶段 2）不预读完整性检查规则和场景穷举细则。CHECKPOINT 前的知识资料不得在 CHECKPOINT 前加载。MCP 配置资料仅在用户明确要求时读取。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-010 | `SKILL.md:130` | > 以下反模式会导致状态机测试质量下降，必须避免。详见 &#91;knowledge/anti-patterns.md&#93;(knowledge/anti-patterns.md)。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-011 | `SKILL.md:134` | \| 1 \| 把"页面提示"等同于"业务状态" \| 页面提示 ≠ 后台真实状态，混淆会导致漏测真实状态变化 \| 状态/事件/结果必须分层描述，区分"接口调用成功""申请已受理""业务最终成功" \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-012 | `SKILL.md:135` | \| 2 \| 把"请求受理"等同于"处理完成" \| 受理只是提交结果，不代表业务完成（如退款申请成功 ≠ 退款成功） \| 转换必须明确 FROM → TO，不能跳过中间态 \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-013 | `SKILL.md:136` | \| 3 \| PRD 缺权限/异常路径时自行脑补 \| LLM 脑补管理员逻辑会引入幻觉，与真实需求不符 \| 必须输出"待确认"节点，暴露给用户裁定 \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-014 | `SKILL.md:137` | \| 4 \| 不标注依据类型 \| 无法区分哪些是 PRD 明确、哪些是推理，评审无法聚焦 \| 每条 transition 和场景必须标 `需求明确/合理推理/待确认` \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-015 | `SKILL.md:139` | \| 6 \| 不定义禁止转换 \| 只测合法路径会漏掉非法跳转的高风险场景 \| 每个状态必须明确"禁止进入哪些状态"及理由 \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-016 | `SKILL.md:140` | \| 7 \| 把"申请成功"作为终态 \| 申请成功只是提交结果，业务可能仍在中态（如退款中） \| 终态必须是业务最终态（退款成功/退款失败），不是受理态 \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-017 | `SKILL.md:158` | 2. **依据类型强制标注** — 每条 transition 和场景必须标 `需求明确/合理推理/待确认`；标签不代表依据已核实 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-018 | `SKILL.md:159` | 3. **歧义暴露而非补齐** — PRD 缺权限/异常路径时必须输出"待确认"节点，禁止 LLM 自行脑补 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-019 | `SKILL.md:160` | 4. **完整性检查独立成阶段** — 不混在建模里，强制人工审视缺口（终态吸收/退出路径/副作用） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-020 | `integrations/quickstart.md:25` | \| 覆盖度报告 \| 简单统计 \| MCP 详细报告（转换/禁止/类型/依据分布） \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-021 | `integrations/quickstart.md:205` | - 工具不存在、连接失败、超时和参数错误分别报告；缺少 Trae 文件不证明服务不可用 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-022 | `knowledge/anti-patterns.md:11` | \| 1 \| 把"页面提示"等同于"业务状态" \| 页面提示 ≠ 后台真实状态，混淆会导致漏测真实状态变化 \| 状态/事件/结果必须分层描述，区分"接口调用成功""申请已受理""业务最终成功" \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-023 | `knowledge/anti-patterns.md:12` | \| 2 \| 把"请求受理"等同于"处理完成" \| 受理只是提交结果，不代表业务完成（如退款申请成功 ≠ 退款成功） \| 转换必须明确 FROM → TO，不能跳过中间态 \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-024 | `knowledge/anti-patterns.md:13` | \| 3 \| PRD 缺权限/异常路径时自行脑补 \| LLM 脑补管理员逻辑会引入幻觉，与真实需求不符 \| 必须输出"待确认"节点，暴露给用户裁定 \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-025 | `knowledge/anti-patterns.md:14` | \| 4 \| 不标注依据类型 \| 无法区分哪些是 PRD 明确、哪些是推理，评审无法聚焦 \| 每条 transition 和场景必须标 `需求明确/合理推理/待确认` \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-026 | `knowledge/anti-patterns.md:16` | \| 6 \| 不定义禁止转换 \| 只测合法路径会漏掉非法跳转的高风险场景 \| 每个状态必须明确"禁止进入哪些状态"及理由 \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-027 | `knowledge/anti-patterns.md:17` | \| 7 \| 把"申请成功"作为终态 \| 申请成功只是提交结果，业务可能仍在中态（如退款中） \| 终态必须是业务最终态（退款成功/退款失败），不是受理态 \| | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-028 | `knowledge/anti-patterns.md:180` | reason: 已取消订单不可支付 | D1 | 在 6 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-029 | `knowledge/anti-patterns.md:253` | \| W1 \| 跳过阶段 1 直接建模 \| 需求理解不完整导致状态机偏离业务意图 \| 必须完成阶段 1 输出业务对象清单 + 歧义清单 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-030 | `knowledge/completeness-check.md:13` | \| C0 \| 模型结构一致 \| 状态、端点、初始态、规则标识和合法/禁止关系 \| pass \| 名称或标识重复、端点不存在、缺少初始态、明确矛盾 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-031 | `knowledge/completeness-check.md:17` | \| C4 \| 终态真的不可变化 \| `transitions&#91;&#93;.from` \| pass \| 终态出现在任何 transition 的 from \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-032 | `knowledge/completeness-check.md:18` | \| C5 \| 禁止转换无遗漏 \| `forbidden&#91;&#93;` + 业务规则 \| not_checked \| 无法自动判定，需人工审视 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-033 | `knowledge/completeness-check.md:120` | name: 终态真的不可变化 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-034 | `knowledge/completeness-check.md:136` | - 已知不可逆操作是否都加了 forbidden（如"已取消 → 已支付"） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-035 | `knowledge/completeness-check.md:137` | - 是否有"看似合法但业务禁止"的转换未在 forbidden 中声明 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-036 | `knowledge/completeness-check.md:147` | name: 禁止转换无遗漏 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-037 | `knowledge/completeness-check.md:149` | detail: 需人工审视终态吸收规则与已知不可逆操作是否完整 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-038 | `knowledge/completeness-check.md:152` | - 检查"已取消 → 已支付"等已知不可逆操作是否在 forbidden 中 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-039 | `knowledge/completeness-check.md:196` | - 不可达状态标 `unreachable` warning | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-040 | `knowledge/completeness-check.md:205` | detail: 状态"退款失败"从初始态"待支付"不可达，可能是建模遗漏了某条 transition | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-041 | `knowledge/completeness-check.md:279` | \| 跳过 C5（禁止转换无遗漏） \| C5 无法自动判定，但跳过会导致大量非法转换漏测 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-042 | `knowledge/completeness-check.md:282` | \| 不输出 contradictions \| contradictions 是 fail 项，必须列出供用户裁定 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-043 | `knowledge/completeness-check.md:295` | 模型可选 `safety_properties`（id/statement/applies_to/source/verification_method/evidence_type）；自然语言安全规则不是机器证明，输出属性 `not_checked` 与实际验证方法。示例“不重复扣款”必须核对资金流水，不能由状态名推断。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-044 | `knowledge/industry-templates/approval-flow.md:26` | - 审批内容不可修改 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-045 | `knowledge/industry-templates/approval-flow.md:40` | - 审批结果不可修改 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-046 | `knowledge/industry-templates/approval-flow.md:48` | - 不可在同一审批单上继续操作 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-047 | `knowledge/industry-templates/approval-flow.md:105` | reason: 必须经过审批中状态 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-048 | `knowledge/industry-templates/approval-flow.md:109` | reason: 必须经过审批中状态 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-049 | `knowledge/industry-templates/approval-flow.md:129` | name: 终态真的不可变化 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-050 | `knowledge/industry-templates/approval-flow.md:132` | name: 禁止转换无遗漏 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-051 | `knowledge/industry-templates/membership.md:166` | event: 管理员强制注销 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-052 | `knowledge/industry-templates/membership.md:167` | side_effects: &#91;脱敏个人数据, 释放资源, 记录强制注销&#93; | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-053 | `knowledge/industry-templates/membership.md:177` | reason: 冻结期间不可直接升级 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-054 | `knowledge/industry-templates/membership.md:181` | reason: 冻结期间不可直接升级 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-055 | `knowledge/industry-templates/membership.md:185` | reason: 冻结期间不可直接升级 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-056 | `knowledge/industry-templates/membership.md:384` | 已冻结 --> 已注销: 管理员强制注销 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-057 | `knowledge/industry-templates/order-refund.md:27` | - 订单金额不可修改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-058 | `knowledge/industry-templates/order-refund.md:34` | - 支付金额不可修改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-059 | `knowledge/industry-templates/order-refund.md:35` | - 支付时间不可篡改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-060 | `knowledge/industry-templates/order-refund.md:37` | meaning: 订单已取消，不可再支付 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-061 | `knowledge/industry-templates/order-refund.md:48` | - 退款金额不可修改 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-062 | `knowledge/industry-templates/order-refund.md:55` | - 退款金额不可再修改 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-063 | `knowledge/industry-templates/order-refund.md:56` | - 不可再次发起退款 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-064 | `knowledge/industry-templates/order-refund.md:109` | reason: 已取消订单不可支付 | D1 | 在 6 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-065 | `knowledge/industry-templates/order-refund.md:114` | reason: 已取消订单不可退款 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-066 | `knowledge/industry-templates/order-refund.md:145` | name: 终态真的不可变化 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-067 | `knowledge/industry-templates/order-refund.md:148` | name: 禁止转换无遗漏 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-068 | `knowledge/industry-templates/ticket.md:26` | - 工单内容不可修改 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-069 | `knowledge/industry-templates/ticket.md:50` | meaning: 工单最终关闭，不可再操作 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-070 | `knowledge/industry-templates/ticket.md:62` | - 必须重新进入处理中 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-071 | `knowledge/industry-templates/ticket.md:122` | reason: 必须经过处理中状态 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-072 | `knowledge/industry-templates/ticket.md:126` | reason: 必须经过处理中状态 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-073 | `knowledge/industry-templates/ticket.md:130` | reason: 待回复状态下不可直接解决 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-074 | `knowledge/products/order-refund.md:4` | > **来源**：本文为**示例沉淀**——基于行业模板与 skill 测试集文章案例编写，用于验证 products/ 机制端到端可用；团队落地时须按真实 PRD 核对每项，来源字段已标注。 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-075 | `knowledge/products/order-refund.md:16` | source: 行业模板 order-refund.md + skill 测试集文章案例（示例沉淀，团队落地须核对真实 PRD） | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-076 | `knowledge/products/order-refund.md:35` | - 订单金额不可修改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-077 | `knowledge/products/order-refund.md:43` | - 支付金额不可修改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-078 | `knowledge/products/order-refund.md:44` | - 支付时间不可篡改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-079 | `knowledge/products/order-refund.md:48` | meaning: 订单已取消，不可再支付 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-080 | `knowledge/products/order-refund.md:59` | - 退款金额不可修改 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-081 | `knowledge/products/order-refund.md:67` | - 退款金额不可再修改 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-082 | `knowledge/products/order-refund.md:68` | - 不可再次发起退款 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-083 | `knowledge/products/order-refund.md:140` | reason: 已取消订单不可支付 | D1 | 在 6 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-084 | `knowledge/products/order-refund.md:145` | reason: 已取消订单不可退款 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-085 | `knowledge/products/order-refund.md:208` | lesson: forbidden 规则必须覆盖所有终态吸收 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-086 | `knowledge/products/order-refund.md:227` | industry: 退款失败为终态，不可恢复 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-087 | `knowledge/products/order-refund.md:250` | - &#91;x&#93; 禁止转换包含终态吸收 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-088 | `knowledge/products/products-template.md:37` | - 订单金额不可修改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-089 | `knowledge/products/products-template.md:45` | - 支付金额不可修改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-090 | `knowledge/products/products-template.md:46` | - 支付时间不可篡改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-091 | `knowledge/products/products-template.md:78` | reason: 已取消订单不可支付 | D1 | 在 6 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-092 | `knowledge/products/products-template.md:96` | answer: 不允许，退款失败为终态，需用户联系客服处理 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-093 | `knowledge/products/products-template.md:136` | lesson: forbidden 规则必须覆盖所有终态吸收 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-094 | `knowledge/products/products-template.md:157` | industry: 退款失败为终态，不可恢复 | D1 | 在 2 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-095 | `knowledge/products/products-template.md:178` | - &#91; &#93; 禁止转换包含终态吸收 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-096 | `knowledge/scenario-types.md:36` | reason: 已取消订单不可支付 | D1 | 在 6 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-097 | `knowledge/scenario-types.md:161` | **生成条件**：同一对象同一前置状态有可竞争事件；触发源和并发成立条件需核实，不要求必须是用户加系统回调。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-098 | `knowledge/scenario-types.md:302` | 十类均输出 `status: applicable / not_applicable / unknown`，以及 `reason/source/evidence_type/missing_information`。模型结构可判断当前是否有转换、禁止规则、守卫或副作用，来源注明模型层，不能证明业务完整性。幂等、并发、消息、等待、权限和失败能力需要需求明确提供范围；事件关键词仅产生候选，不证明业务能力。未知不等于不适用，未说明权限时目标保持 `待确认`，不能默认拒绝；显式不… | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-099 | `knowledge/scenario-types.md:304` | `scenario_applicability` 是模型与清单的可选兼容字段；缺省时业务能力为 unknown。同步且明确无消息通道才可将乱序标不适用。并发候选必须来自同一对象同一前置状态的事件，联合触发条件未知时保留待确认。场景类型条数保留描述统计，不作为完整性门槛。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-100 | `knowledge/scenario-types.md:325` | 1. **同 risk_type 同 (state, event)**：只有转换/禁止引用、完整守卫、违反守卫、前置输入、尝试目标和所有断言都等价时才可合并；不能把不同 guard 或目标压成一条。来源不同的依据分别保留。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-101 | `knowledge/scenario-types.md:340` | \| 把 access_control 全部脑补为"管理员才能" \| PRD 未说明权限矩阵时必须标"待确认"，不能脑补 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-102 | `knowledge/scenario-types.md:341` | \| 把 message_reorder 跳过 \| 即使无显式异步消息，支付/退款回调本质是异步，必须生成 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-103 | `knowledge/scenario-types.md:366` | 执行记录新增可选 `evidence_status`，缺省 unknown；verified 还需明确 `evidence_check_source` 记录核验依据。未提供 execution_records 表示未评估，显式 &#91;&#93; 表示该基线尚无执行记录；空用例基线表示不适用。只有调用方明确核验为 verified 且有非占位证据引用才计已执行，MCP 不自行验证文件/远端引用内容。未知或不可达证据、旧基线版本不计入分子。需求/设计层同时列未确定关联项… | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-104 | `knowledge/scenario-types.md:372` | 失败恢复只在明确单一 allowed_states 与目标一致时计已确定设计；未给集合、集合条件未确定或目标冲突均列缺口。场景先按 from/event/完整守卫/可选 transition_id 唯一关联；匹配转换未声明 failure_outcomes 时可使用场景本身的明确单一失败事实，添加无关转换的结果不改变结论。匹配转换已声明 failure_outcomes 时，并匹配阶段、允许态、禁止副作用、观测与恢复条件；错误引用不能绕过模型依据，待确认模型结果不得由场… | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-105 | `knowledge/state-modeling.md:8` | 每个状态机模型必须包含 6 个要素，缺一不可： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-106 | `knowledge/state-modeling.md:16` | \| 副作用（Side Effect） \| `transitions&#91;&#93;.side_effects` \| 转换后必须执行的动作 \| 生成支付记录/触发履约 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-107 | `knowledge/state-modeling.md:17` | \| 不变量（Invariant） \| `states&#91;&#93;.invariants` \| 状态内不可破坏的约束 \| 待支付状态订单金额不可修改 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-108 | `knowledge/state-modeling.md:19` | **禁止转换**（Forbidden）是第 7 个可选要素，用于显式声明业务上不允许的跳转（如"已取消 → 已支付"）。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-109 | `knowledge/state-modeling.md:48` | PRD 未完整描述但业务必须处理的流程，如超时/失败/重试。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-110 | `knowledge/state-modeling.md:56` | 异常流程的 transition 大量标 `evidence_type: 待确认`，这正是 LLM 必须暴露而非脑补的部分。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-111 | `knowledge/state-modeling.md:62` | 3. **最后补异常流程**：识别 PRD 未覆盖的异常情况，**全部标"待确认"**，禁止脑补 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-112 | `knowledge/state-modeling.md:67` | 不变量是状态内不可破坏的约束，违反不变量意味着状态机模型有缺陷。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-113 | `knowledge/state-modeling.md:71` | 每个状态可列 0-N 条不变量，写法为"主语 + 不可/必须 + 谓语"： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-114 | `knowledge/state-modeling.md:77` | - 订单金额不可修改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-115 | `knowledge/state-modeling.md:79` | - 必须保留创建时间 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-116 | `knowledge/state-modeling.md:82` | - 支付金额不可修改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-117 | `knowledge/state-modeling.md:83` | - 支付时间不可篡改 | D1 | 在 4 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-118 | `knowledge/state-modeling.md:84` | - 必须保留支付渠道 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-119 | `knowledge/state-modeling.md:87` | - 退款金额不可再修改 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-120 | `knowledge/state-modeling.md:88` | - 不可再次发起退款 | D1 | 在 3 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-121 | `knowledge/state-modeling.md:101` | 终态是业务最终态，**不可再变化**。终态必须满足： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-122 | `knowledge/state-modeling.md:104` | - 不变量包含"不可再修改"类约束 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-123 | `knowledge/state-modeling.md:108` | 终态吸收 = 终态到任意状态都禁止，写法： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-124 | `knowledge/state-modeling.md:156` | - 状态名与事件名不可重复（避免"退款成功"既是状态又是事件） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-125 | `knowledge/state-modeling.md:157` | - 若不可避免（PRD 原文如此），状态加"态"后缀（如"退款成功态"），事件加"回调"后缀（如"退款成功回调"） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-126 | `knowledge/state-modeling.md:184` | \| `from` \| ✅ \| 必须是 `states&#91;&#93;` 中已定义的状态名 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-127 | `knowledge/state-modeling.md:185` | \| `to` \| ✅ \| 必须是 `states&#91;&#93;` 中已定义的状态名 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-128 | `knowledge/state-modeling.md:188` | \| `side_effects` \| 可选 \| 后置动作，转换成功后必须执行 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-129 | `knowledge/state-modeling.md:217` | 只要业务上"不允许 A → B"，就必须在 `forbidden&#91;&#93;` 中显式声明： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-130 | `knowledge/state-modeling.md:223` | reason: 已取消订单不可支付 | D1 | 在 6 个文件中重复 | 纯重复：保留单一权威源，其余删为指针 | 待复核 |
| state-machine-test-engineer-131 | `knowledge/state-modeling.md:235` | `to: "*"` 表示"任意状态"，仅用于终态吸收场景。其他场景必须明确写出目标状态。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-132 | `knowledge/state-modeling.md:240` | - 一对状态只出现在 `forbidden&#91;&#93;` 不出现在 `transitions&#91;&#93;`——正常，表示业务明确禁止 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-133 | `knowledge/state-modeling.md:254` | 模型顶层必填 `meta/states/transitions`，`forbidden` 默认空列表。`meta.object` 必填，版本默认 `"1.0"`；每个状态必填 `name/meaning`，初始/终态标志默认 false。转换必填 `from/to/event/evidence_type`；`guards/side_effects` 默认空列表，`source` 默认空字符串。禁止规则必填 `from/to/reason/evidence_type`，`… | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-134 | `knowledge/state-modeling.md:261` | `traceability` 默认缺省；可提供 sources（id/location/version/availability）、artifacts（id/kind/version）和 links（upstream/downstream/confirmation/source）。来源版本未知保留 null，不编造；来源不可达与业务结果未知分别记录。需求→风险→模型/场景→用例→执行证据用对象命名空间下的稳定引用关联，候选关联与已确认关联分开。来源或需求变化后确定性传播… | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-135 | `knowledge/state-modeling.md:267` | 追溯边可选 `source_refs` 关联来源 ID。confirmed 标签还需关联依据 source、来源 available 和明确版本；缺失或不可达只输出 candidate_impacts，并在 uncorroborated_links 列依据缺口，不把输入标签当作已确认事实。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-136 | `knowledge/usage-examples.md:17` | - 禁止：已取消→已支付（已取消订单不可支付）、退款成功→任何状态（终态吸收） | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| state-machine-test-engineer-137 | `state-machine-core.md:27` | - 终态描述（完成后不可修改/已退款订单不可再退） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-138 | `state-machine-core.md:28` | - 禁止描述（已取消订单不能支付） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-139 | `state-machine-core.md:29` | 4. **歧义标记**：需求未说明的权限/异常/恢复路径，**必须标"待确认"**，禁止 LLM 自行脑补 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-140 | `state-machine-core.md:48` | - 终态描述: 退款成功后不可再修改 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-141 | `state-machine-core.md:49` | - 禁止描述: 已取消订单不能支付 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-142 | `state-machine-core.md:69` | 基于阶段 1 的摘要，构建符合 Schema 的状态机模型（YAML/JSON），含状态/转换/守卫/副作用/不变量/禁止转换/依据类型。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-143 | `state-machine-core.md:75` | - 每个状态必须填写 `meaning`（含义） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-144 | `state-machine-core.md:79` | - 每条转换必须标 `evidence_type`：`需求明确` / `合理推理` / `待确认` | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-145 | `state-machine-core.md:80` | - 每条转换必须标 `source`（PRD 章节或推理依据） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-146 | `state-machine-core.md:82` | - 每个状态列出不可破坏的约束（如"待支付状态订单金额不可修改"） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-147 | `state-machine-core.md:85` | - 终态吸收：终态到任意状态都禁止（`forbidden: { from: 终态, to: "*" }`） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-148 | `state-machine-core.md:87` | - 列出业务上不允许的跳转（如"已取消 → 已支付"） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-149 | `state-machine-core.md:88` | - 每条禁止转换必须标 `reason` 和 `evidence_type` | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-150 | `state-machine-core.md:92` | 状态机模型必须符合 `knowledge/state-modeling.md` 中定义的 6 要素 + MAE + 不变量结构。以下示例同时作为 skill 与 MCP 的结构协作契约： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-151 | `state-machine-core.md:106` | invariants: &#91;订单金额不可修改&#93; | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-152 | `state-machine-core.md:132` | - 显示完整状态机模型（状态/转换/禁止/不变量） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-153 | `state-machine-core.md:159` | \| 4 \| 终态真的不可变化 \| 终态不出现在任何 transition 的 `from` \| 标 contradiction \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-154 | `state-machine-core.md:160` | \| 5 \| 禁止转换无遗漏 \| 每个状态都明确"禁止进入哪些" \| 标 gap，要求补充 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| state-machine-test-engineer-155 | `state-machine-core.md:225` | 完整场景 Schema 和可校验示例见 &#91;knowledge/scenario-types.md&#93;(knowledge/scenario-types.md)。每条场景必须包含： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
