# 规范语句清单：change-impact-analyzer

> 由 `scripts/extract-rule-inventory.py` 生成。分类为启发式初筛，删除/移位前必须人工复核。
> 共 58 条：D1 重复 0 / D2 移位 7 / D3 冲突 0 / D4 参考 2 / D5 行为 49

| ID | 位置 | 规范语句 | 类别 | 判定依据 | 处置 | 复核 |
|---|---|---|---|---|---|---|
| change-impact-analyzer-001 | `SKILL.md:84` | - 可选输入：需求/验收标准、现有用例或执行记录；披露来源、版本、读取范围和可达状态，不强制要求旧用例。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-002 | `SKILL.md:85` | - 范围硬约束：用户说“当前改动”时先看工作区；工作区干净且 feature 分支领先默认分支时使用 `<default>...HEAD`，不得误报无变更。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-003 | `SKILL.md:86` | - 用例格式：Markdown、CSV、JSON、YAML；Excel 必须先转换或由用户粘贴内容。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-004 | `SKILL.md:87` | - 输出：实际命令或变更来源、基线/head SHA（片段则记录可用版本）、工作区状态、变更文件数、已读/未读/过滤项；用例基线记录为可用/无/不可达，并说明是否完整。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-005 | `SKILL.md:89` | - 分支/ref 不存在时不擅自替代；用户指定用例不可达时暂停该项对照，仍交付可确定的代码影响与测试建议。没有用例基线时注明「既有覆盖未评估」，不报覆盖率或确定缺口。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-006 | `SKILL.md:100` | - Git 文件状态须有 Git/完整 patch 元数据；新增入口或语句不能证明文件是 A 或 M，缺元数据则 unknown。用户提供目录可记录数量与来源，不伪装 Git 统计，也不补猜路径、行号、SHA 或完整文件数。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-007 | `SKILL.md:101` | - 沿页面、API、服务、数据、缓存/MQ/外部系统追踪 `impact_chains`，契约变化必须检查两侧。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-008 | `SKILL.md:103` | - 构建产物可过滤；依赖升级需检查清单/锁文件对应的版本变化，承载行为或验收约定的配置、SKILL、测试文档不得按“纯文档”跳过。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-009 | `SKILL.md:105` | - 无法解析函数级信息时降级到文件级并标低置信度；二进制、截断和异常格式均须披露。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-010 | `SKILL.md:117` | 5. 候选关联、无法分析的用例和未读范围单列；降低风险或排除回归必须有证据。自动化用例存在不证明当前版本验证通过。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-011 | `SKILL.md:131` | - diff 涉及凭据、用户数据或内部地址时只报告风险类别，不复制敏感值；对外报告必须脱敏。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-012 | `SKILL.md:132` | - 未执行的测试、不可访问的环境和被截断的范围必须在报告中列出。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-013 | `SKILL.md:138` | > 输入不足、材料不可达和大 diff 的降级规则详见 &#91;knowledge/anti-patterns.md&#93;(knowledge/anti-patterns.md) 第 7 节。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-014 | `SKILL.md:154` | \| 5 \| 报告中只列问题不给建议 \| 每个问题必须附带建议操作（修改用例/补充用例/验证确认） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-015 | `knowledge/anti-patterns.md:15` | \| 5 \| 报告中只列问题不给建议 \| 用户需要可落地的行动项，而非仅发现问题 \| 每个问题必须附带建议操作（修改用例/补充用例/验证确认） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-016 | `knowledge/anti-patterns.md:16` | \| 6 \| 对 Excel 格式强行解析 \| Excel 解析不可靠，容易丢失格式或乱码 \| 提示用户转换为 CSV/Markdown，或在对话中粘贴内容 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-017 | `knowledge/anti-patterns.md:23` | **典型表现**：用户说"分析当前改动"后，未披露比较基线、输入来源或未评估范围就给结论；没有旧用例则强制终止代码影响分析。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-018 | `knowledge/anti-patterns.md:63` | - 变更清单包含需要随证据修正的分析判断，不能当成不可变的确定性结果 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-019 | `knowledge/anti-patterns.md:78` | **替代做法**：每个问题必须附带建议操作，至少包括： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-020 | `knowledge/anti-patterns.md:88` | - Excel 解析不可靠，合并单元格、公式、数据验证等都会丢失信息 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-021 | `knowledge/anti-patterns.md:114` | \| E1 \| 降低风险没有证据就下调等级 \| "开发说改动很小"不构成低风险证据，凭印象下调会漏掉高风险 \| 必须给出「调用方数量/契约一致性/自动化覆盖」等具体证据才能下调 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-022 | `knowledge/anti-patterns.md:115` | \| E2 \| Mode A 把推断当事实陈述 \| 推断与事实混淆会让用户误以为代码已经验证，导致决策失误 \| 必须区分代码事实/影响推断/待确认问题，推断需标注置信度 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-023 | `knowledge/anti-patterns.md:117` | \| E4 \| 测试场景写"验证 XX 是否正常" \| 不可执行，依赖主观判断，无法判定 pass/fail \| 必须用 `&#91;P级&#93;&#91;类型&#93; 前置→操作→预期—证据` 结构（详见 &#91;report-template.md&#93;(report-template.md) 第 3 节） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-024 | `knowledge/anti-patterns.md:118` | \| E5 \| 只看变更一侧不查契约对端 \| 接口契约变更只看一端会漏掉对端未同步修改的问题 \| 接口契约变更必须同时检查前后端两侧（详见 &#91;cross-impact-analysis.md&#93;(cross-impact-analysis.md) 第 2 节） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-025 | `knowledge/anti-patterns.md:173` | \| 阶段 1 \| 无旧用例或指定用例不可达 \| 保留既有覆盖未评估，有已读基线才对照 \| 仍交付代码影响范围和测试内容，不虚构用例或覆盖率 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-026 | `knowledge/cross-analysis-guide.md:36` | 为每个变更点分别记录 `coverage_status` 与 `execution_status`，标用例/断言位置、基线完整度和执行证据版本。没有用例基线、无法解析断言、用例不可达时保持「未评估」。已有测试代码或过去通过的记录不证明当前代码已通过。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-027 | `knowledge/cross-impact-analysis.md:37` | - 记录已查入口与停止位置。动态调用、消息消费、配置开关或跨仓库对端不可达时列为待核实；「未找到调用方」不等于「没有调用方」。静态调用成立不证明运行时条件已满足。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-028 | `knowledge/cross-impact-analysis.md:87` | - **逐调用方核对语义**：共享读方法可能在不同入口中只用于判空、用于解密展示、用于外部比对。某入口只依赖支付后的状态，不可写成它新增了支付字段解密。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-029 | `knowledge/cross-impact-analysis.md:88` | - **检查失败前后状态**：沿错误返回和事务范围确认哪些写入/外部调用已发生、哪些后续动作未发生；失败响应不能证明全部回滚。遇到不可达服务则在该处停止确认，保留候选副作用。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-030 | `knowledge/cross-impact-analysis.md:96` | **目标**：接口契约变化必须同时检查两侧，不能只看变更的一端。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-031 | `knowledge/cross-impact-analysis.md:179` | - 用例基线单列来源、版本、可达性、已读范围与完整程度；没有用例或指定文件不可达时，跳过该项用例对照，不能把未评估写成未覆盖。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-032 | `knowledge/cross-impact-analysis.md:185` | **输出三分原则**：根据代码变化推断业务意图时，必须明确区分以下三类信息，**避免 AI 把推断当成事实**。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-033 | `knowledge/cross-impact-analysis.md:190` | \| 影响推断 \| 根据调用关系推断出来的潜在影响 \| 该接口被订单详情页和退款页同时调用；状态判断变化可能影响退款入口；新字段可能导致历史数据为空 \| 必须标注置信度（高/中/低），并说明推断依据 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-034 | `knowledge/cross-impact-analysis.md:191` | \| 待确认问题 \| 代码本身无法回答的问题 \| 状态 2 是否允许退款？老版本客户端是否必须兼容？新字段为空时产品希望展示什么？这次修改是否需要处理历史数据？ \| 必须以问号结尾，不能给出臆测答案 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-035 | `knowledge/cross-impact-analysis.md:196` | - 必须写成「从状态判断变化推断，状态 2 可能被纳入退款范围，置信度中等，需要确认实际业务规则」 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-036 | `knowledge/cross-impact-analysis.md:219` | \| 跨服务、支付、消息或异步状态 \| 集成/测试环境验证，用业务关联标识核对事件、账单、外部记录和最终状态 \| 单次日志或成功提示不能证明无重复处理；外部环境不可达则列未验证层 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-037 | `knowledge/cross-impact-analysis.md:272` | 例如：需求只要求修改订单列表展示，但代码同时放开了订单导出权限。这不一定就是 Bug，也可能是必要的技术调整，但因为缺少明确需求依据、又可能影响用户行为，所以必须**单独标记**让产品、开发、测试一起确认。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-038 | `knowledge/cross-impact-analysis.md:298` | - candidate链只形成候选影响清单，记录需要核对的规则/调用依赖；不得将关键词同名升级为confirmed。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-039 | `knowledge/cross-impact-analysis.md:299` | - 来源不可达只报告取证缺口；业务结果未知另报状态，两者不能互相替代。无追溯图时按现有Mode A/B继续，关系未评估而不是假装无影响。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-040 | `knowledge/diff-modes.md:20` | 用户要求定位实际改动，或材料涉及共享库与多个服务时，在已授权仓库范围内先查版本，再定向核对 diff；技术说明本身也可作为改动点输入，不强制等待源码。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-041 | `knowledge/diff-modes.md:23` | 2. 核对候选提交的实际 diff、父节点及先后关系，按仓库记录 `base/head` 和相关提交；未知仓库、不可达 ref 保持待核实，不自动扩展目录或替换基线。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-042 | `knowledge/diff-modes.md:34` | - 若工作区干净且当前位于默认分支，才输出「无变更」；不得忽略 feature 分支上已提交但未合并的改动 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-043 | `knowledge/diff-modes.md:38` | - 有前后片段或具体改动点时直接解析材料，标明源码是否已核对；不要求用户必须导出 patch。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-044 | `knowledge/diff-modes.md:108` | \| `base_ref/base_sha/head_sha/material_version` \| 比较口径及来源版本；不能虚构不可得的 SHA \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-045 | `knowledge/diff-modes.md:122` | > **执行任何 `git diff` 命令前必须遵守以下规则，防止命令注入。** | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-046 | `knowledge/diff-modes.md:124` | - **参数校验**：分支名、commit hash、tag 名仅允许字母、数字、`/`、`-`、`_`、`.`、`^`、`~` 字符，禁止包含 shell 元字符（`;` `\|` `$` `` ` `` `(` `)` `&` `>` `<` `'` `"` `\n`） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-047 | `knowledge/diff-modes.md:125` | - **禁止拼接**：不得将用户输入直接拼入 `git diff` 命令，必须先校验格式 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-048 | `knowledge/diff-modes.md:126` | - **禁止事项**：禁止直接执行用户提供的 shell 命令字符串；禁止使用 `eval`、`os.system` 或 shell=True 执行包含用户输入的命令 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-049 | `knowledge/diff-modes.md:210` | - 失败兜底（不在 git 仓库 / diff 为空 / diff 过大 / 可选用例不可达等）见 &#91;anti-patterns.md&#93;(anti-patterns.md) 第 7 节 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| change-impact-analyzer-050 | `knowledge/report-template.md:28` | > 用例基线：&#91;来源/版本/完整程度；无或不可达则未评估&#93; | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| change-impact-analyzer-051 | `knowledge/report-template.md:63` | 列出风险等级、判断原因，以及对应的验证方式。高风险必须给出具体证据，不能仅靠"开发说改动很小"下调。 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| change-impact-analyzer-052 | `knowledge/report-template.md:121` | 保留旧执行证据，区分来源不可达、业务结果未知和当前未执行。只定向复核受影响产物，不宣称整套用例失效。 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| change-impact-analyzer-053 | `knowledge/report-template.md:126` | - 老版本客户端是否必须兼容旧字段？（需客户端团队确认） | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| change-impact-analyzer-054 | `knowledge/report-template.md:138` | 为每条必测内容标注优先级，**优先级的意义不是减少测试**，而是在时间有限时明确哪些问题必须在发布前发现。 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| change-impact-analyzer-055 | `knowledge/report-template.md:142` | \| **P0** \| 不通过就不建议发布 \| 核心业务不可用；金额计算错误；数据可能丢失；权限可以被绕过；数据库迁移失败；公共接口发生破坏性变化 \| | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| change-impact-analyzer-056 | `knowledge/report-template.md:148` | 每条必测内容必须采用以下统一结构，**不能只写"验证 XX 是否正常"这种不可执行的描述**。 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| change-impact-analyzer-057 | `templates/business-impact-test-scope.md:16` | > 分析依据：&#91;需求/改动说明及版本、已核对代码范围、未读或不可达材料&#93;。 | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| change-impact-analyzer-058 | `templates/business-impact-test-scope.md:30` | **回归建议：** &#91;哪些业务必须验证，哪些需沿共享调用或数据继续回归；有隔离证据才说明哪些可不回归。&#93; | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
