# 规范语句清单：testing-bundle

> 由 `scripts/extract-rule-inventory.py` 生成。分类为启发式初筛，删除/移位前必须人工复核。
> 共 16 条：D1 重复 0 / D2 移位 0 / D3 冲突 0 / D4 参考 1 / D5 行为 15

| ID | 位置 | 规范语句 | 类别 | 判定依据 | 处置 | 复核 |
|---|---|---|---|---|---|---|
| testing-bundle-001 | `SKILL.md:49` | 禁止只凭单个关键词直接调用子 skill。先提取以下三要素，再对照路由表： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-002 | `SKILL.md:113` | 路由确定后才读取目标文件；混合链按顺序加载，禁止预先加载全部子 skill： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-003 | `SKILL.md:130` | **入口必须守住的三条**： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-004 | `SKILL.md:133` | 2. 子 skill 不可用 → 标注「子 skill 不可用」，交付上游产物与方向性指导，不假装完成 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-005 | `SKILL.md:139` | 2. **路由必须基于显式意图判断** — 不得"默认路由"或"随机路由" | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-006 | `SKILL.md:143` | 6. **上下文必须完整传递** — 路由时需携带用户原始请求和已收集的上下文 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-007 | `knowledge/mixed-intent-chains.md:185` | - 压测方案、状态机模型或变更影响产物需要离线数据时，按实际产物依赖转交 test-data-generator，不强制新增完整用例 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-008 | `knowledge/mixed-intent-chains.md:214` | - 前端准备产物中的正确预期必须引用需求、设计或用户确认；代码现状只能作为实现证据，不能自动成为验收标准 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-009 | `knowledge/mixed-intent-chains.md:215` | - 缺少运行条件时只交付代码分析与待确认项，不把未执行标为通过；运行核实不得扩大当次授权范围 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-010 | `knowledge/routing-fallbacks.md:3` | > **何时阅读**：意图判定出现歧义、需要降级处理、子 skill 不可用、上下文丢失，或需要核对路由/安装反例时。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-011 | `knowledge/routing-fallbacks.md:15` | \| 子 skill 未安装（路由目标 skill 不存在） \| 检测到子 skill 不可用，提示用户安装对应 skill，并给出安装命令 \| 标注「子 skill 不可用」，输出 bundle 层方向性指导模板（按目标 skill 选一）：bug-analyzer→「按五步定位法：复现→隔离→定位→验证→报告」；case-engineer→「按四阶段：理解需求→提取测试点→编写用例→自检补全」；strategy→「按五阶段：项目特征→风险矩阵→分层→范围准入准出… | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-012 | `knowledge/routing-fallbacks.md:17` | \| 混合意图协同失败（上游 skill 完成但下游 skill 不可用） \| 输出上游 skill 的中间产物（防御性测试点清单 / 分层策略 / 瓶颈定位报告），提示用户手动转交下游 skill 或自行处理 \| 标注「协同中断」，仅输出上游 skill 报告，中间产物按上下文 schema 格式作为附录 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-013 | `knowledge/routing-fallbacks.md:24` | \| strategy 与 case-engineer 协同失败（strategy 完成但 case-engineer 不可用） \| 输出 strategy 的分层策略与优先级，提示用户手动转交 case-engineer 生成对应层用例 \| 标注「协同中断」，仅输出测试策略报告，分层策略作为用例生成依据附录 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-014 | `knowledge/routing-fallbacks.md:27` | **上下文传递 schema**（路由/转交时必须按此 JSON 结构传递）： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-015 | `knowledge/routing-fallbacks.md:52` | \| 1 \| 不判断意图直接调用某个子 skill \| 跳过路由会导致用户请求被错误 skill 处理，违反 bundle 职责 \| 必须按路由决策表判断意图，意图不明确时追问用户（🔴 CHECKPOINT） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| testing-bundle-016 | `knowledge/usage-examples.md:37` | 🔴 **CHECKPOINT · 意图不明确时强制追问**：不得"默认路由"，必须列出 7 个子 skill 的能力让用户选择。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
