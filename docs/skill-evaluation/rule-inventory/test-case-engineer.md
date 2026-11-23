# 规范语句清单：test-case-engineer

> 由 `scripts/extract-rule-inventory.py` 生成。分类为启发式初筛，删除/移位前必须人工复核。
> 共 223 条：D1 重复 0 / D2 移位 17 / D3 冲突 0 / D4 参考 39 / D5 行为 167

| ID | 位置 | 规范语句 | 类别 | 判定依据 | 处置 | 复核 |
|---|---|---|---|---|---|---|
| test-case-engineer-001 | `SKILL.md:47` | - 纯重构无行为变更 → 必须使用回归验证清单模式 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-002 | `SKILL.md:48` | - 用户要求快速 → 必须使用快速模式（压缩阶段 1/4，但必须输出测试点清单） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-003 | `SKILL.md:49` | - 用户输入为已有用例 或 触发词「评审/review/检查质量」→ 必须使用评审模式（不走四阶段生成流程） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-004 | `SKILL.md:78` | **用例输出约束**：每条用例必须以 `### TC_模块_功能_序号: 标题` 块承载，**禁止用一张表罗列全部用例**（脚本会报 `FILE_FORMAT`）；表格只允许作为块内同构数据组。**用例范围**：焦点项写完整、非焦点内容只冒烟、服务故障类默认不写，越界候选写进「裁剪说明」（见 &#91;knowledge/scope-discipline.md&#93;(knowledge/scope-discipline.md)）。通用格式与编写铁律见 &#91;kn… | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-005 | `SKILL.md:93` | \| &#91;knowledge/project-knowledge.md&#93;(knowledge/project-knowledge.md) \| **阶段 1 强制读** + Office/PDF 转换 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-006 | `SKILL.md:96` | \| &#91;knowledge/large-scale-review.md&#93;(knowledge/large-scale-review.md) \| **用例数 > 100 或用户要求评审方案/排期时必读**（规模画像 + 策略选择 + 强制全量清单 + 分层抽样 + 评审方案模板 + 分批执行与聚合） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-007 | `SKILL.md:105` | \| &#91;knowledge/products/&#93;(knowledge/products/) \| **阶段 1 必须加载**（产品专项业务知识，若存在对应产品知识文件） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-008 | `SKILL.md:158` | 始终可使用文件读取、代码搜索、终端命令等环境能力。若某项不可用，在输出中明确注明局限。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-009 | `integrations/quickstart.md:42` | **降级方案：共享 convert_docs.py（MarkItDown 不可用时使用）** | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-010 | `integrations/quickstart.md:58` | > **执行任何 shell 命令前必须遵守以下规则，防止命令注入。** | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-011 | `integrations/quickstart.md:63` | - **路径限定**：文件路径必须在项目目录范围内，禁止路径穿越（如 `../../../etc/passwd`） | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-012 | `integrations/quickstart.md:68` | - **范围限定**：`git diff` 的 `<range>` 参数仅允许分支名、commit hash、tag 名，禁止包含 shell 元字符 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-013 | `integrations/quickstart.md:69` | - **禁止拼接**：不得将用户输入直接拼入 `git diff` 命令，必须先校验格式 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-014 | `integrations/quickstart.md:73` | - **禁止**直接执行用户提供的 shell 命令字符串 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-015 | `integrations/quickstart.md:74` | - **禁止**将未校验的用户输入作为 shell 命令参数 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-016 | `integrations/quickstart.md:75` | - **禁止**使用 `eval`、`os.system` 或 shell=True 执行包含用户输入的命令 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-017 | `knowledge/anti-patterns.md:11` | \| 1 \| **跳过阶段 1 直接写用例** \| 需求理解不完整导致用例偏离业务意图 \| 必须完成阶段 1 需求理解输出，哪怕快速模式也要压缩而非跳过 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-018 | `knowledge/anti-patterns.md:12` | \| 2 \| **跳过阶段 2 直接写用例** \| 测试点遗漏导致用例覆盖不全 \| 必须输出测试点清单，阶段 3 基于清单生成用例 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-019 | `knowledge/anti-patterns.md:15` | \| 5 \| **业务结果缺失或关键节点不可定位** \| 无法判断业务目标是否达成 \| 按 writing-rules.md 补充业务结果及必要检查点 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-020 | `knowledge/anti-patterns.md:25` | \| 2 \| **title 过长且未记录例外** \| 在测试管理工具中显示截断，影响可读性 \| 尝试精简为 `{被测对象} - {具体行为}`；若信息不可删（满足 test-standards.md 例外判定 3 条件之一），保留超长标题并在备注中记录原因 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-021 | `knowledge/anti-patterns.md:28` | \| 5 \| **steps 使用占位话术** \| 不可执行，依赖主观理解 \| 使用具体操作：输入 xxx、点击 xxx、查看 xxx \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-022 | `knowledge/anti-patterns.md:31` | \| 8 \| **测试点缺少操作路径** \| AI 无法生成具体步骤 \| 测试点必须包含：&#91;验证对象&#93; + &#91;操作/场景&#93; + &#91;预期结果方向&#93; \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-023 | `knowledge/anti-patterns.md:54` | \| 1 \| **把基础设施故障当业务异常** \| 断网、5xx、宕机、依赖不可用通常归运维/平台/第三方，需求也未定义失败行为；写进用例等于让本需求为别人背书 \| 需求要求容错才写，否则剔除并写进裁剪说明 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-024 | `knowledge/anti-patterns.md:65` | \| 1 \| **验证 XXX 可以点击** \| 缺少操作结果和业务影响 \| 必须包含：操作行为 + 预期结果方向 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-025 | `knowledge/anti-patterns.md:66` | \| 2 \| **验证 XXX 正常** \| 太模糊，无法生成具体用例 \| 必须明确：正常的具体表现是什么 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-026 | `knowledge/anti-patterns.md:67` | \| 3 \| **验证 XXX 可以关闭** \| 缺少状态变化和保存行为 \| 必须明确：关闭后的状态和业务影响 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-027 | `knowledge/bug-patterns.md:3` | > **何时阅读**:阶段 2 测试点扫描完 7 维度后对照查阅（按适用性补点，不是补点清单）;Bug 根因分析时必须查阅。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-028 | `knowledge/bug-patterns.md:77` | > **适用范围**：本表用于核对「焦点功能是否需要补点」，不是补点清单。命中即补，未命中不补；容错类（重复提交、操作中断、依赖不可用）只在需求要求容错时落为用例。需求未要求的条目写进「裁剪说明」（见 &#91;scope-discipline.md&#93;(scope-discipline.md)）。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-029 | `knowledge/bug-patterns.md:86` | - **封顶临界**：封顶类规则（优惠封顶/限额封顶）的临界值恰好等于上限时判定易错（如 9 折券最高优惠 30 元，订单 300 元时 300×10%=30 恰好等于上限）→ 封顶规则必测三档：低于上限、恰好等于上限、高于上限；恰好等于上限时须与需求确认"等于是否截断" | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-030 | `knowledge/bug-patterns.md:91` | - **空结果**：无匹配时页面崩溃 → 搜索不可能存在的内容 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-031 | `knowledge/bug-patterns.md:151` | \| P1 \| 依赖异常（DB/Redis/第三方超时或拒绝连接） \| 检查依赖健康状态、连接池监控、慢查询日志 \| 模拟依赖不可用（断网/mock 超时）复现 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-032 | `knowledge/bug-patterns.md:157` | **防御性测试点**：依赖不可用降级 / 配置缺失启动检查 / 资源耗尽限流 / 异常统一捕获。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-033 | `knowledge/case-arrangement.md:9` | 用例输出必须遵循统一的编排顺序，禁止随机罗列。编排策略二选一，**默认采用策略一**。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-034 | `knowledge/case-arrangement.md:72` | 2. 编排顺序不因生成批次打乱：阶段 4 自检补充的用例按归属插入对应模块 / 旅程阶段，禁止整体追加在末尾 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-035 | `knowledge/case-arrangement.md:93` | **与阶段 2 裁剪的关系**：`core.md` 的「裁剪说明」列记录哪些维度/字段未落为用例及理由；本节预算约束最终用例总数。裁剪不等于删需求，未覆盖的测试点仍须在输出中单列并写明原因。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-036 | `knowledge/failure-semantics.md:15` | \| 执行前拒绝 \| 核对校验/授权响应与实际业务记录；哪些副作用禁止以契约为准 \| 已确认无业务执行且拒绝原因可修正时按需求设计重试 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-037 | `knowledge/failure-semantics.md:17` | \| 提交成功但响应丢失 \| 核对支付/订单/账本与第三方记录，结果可能已成功 \| 先查实际结果，按真实幂等契约复用结果；禁止再次产生资金副作用 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-038 | `knowledge/failure-semantics.md:18` | \| 部分成功待补偿 \| 分列各子操作结果与禁止重复的副作用；未定义补偿不自动生成 \| 只验证需求规定的补偿入口、条件、权限和目标 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-039 | `knowledge/failure-semantics.md:19` | \| 结果未知 \| 用业务查询、事件、日志或对账补证；未知状态与来源不可达分别记录 \| 查清结果或取得已定义的恢复策略后再决定，不生成无条件重试 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-040 | `knowledge/failure-semantics.md:22` | - 重复回调验证一次有效业务结果与禁止副作用；HTTP成功次数、状态不变和资金操作次数分别观察。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-041 | `knowledge/failure-semantics.md:33` | - 不进入非法状态：用既有禁止转换及业务不变量判定；缺状态规则时标待确认。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-042 | `knowledge/large-scale-review.md:11` | - 用例总数 > 100 条（强制进入，与 review-mode.md 失败模式阈值一致） | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-043 | `knowledge/large-scale-review.md:27` | 不允许凭用例数量直接选策略，必须先输出画像。缺少的字段标注「未知」，不得填 0 或猜测。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-044 | `knowledge/large-scale-review.md:34` | \| 优先级分布 \| P0/P1/P2/P3 条数 \| 识别强制全量范围 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-045 | `knowledge/large-scale-review.md:48` | \| S3 \| N > 300，或存在时间/人力约束 \| 分层抽样 \| 强制全量清单全查 + 其余分层抽 20% \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-046 | `knowledge/large-scale-review.md:52` | 策略可叠加，例如 S4 + S3：变更用例全量评审，未变更部分分层抽样，覆盖度与优先级分布按全量统计。选择结果必须写明依据，不能只写编号。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-047 | `knowledge/large-scale-review.md:56` | 以下用例必须全量评审，不进入抽样池： | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-048 | `knowledge/large-scale-review.md:65` | **原则**：抽样降低的是工作量，不是风险。强制全量清单的条数必须与抽样条数分列，不得合并成一个「本次评审 N 条」。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-049 | `knowledge/large-scale-review.md:72` | - **种子**：`sample_seed` 默认评审日期（`YYYYMMDD`），写入方案；同一种子必须得到同一批样本 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-050 | `knowledge/large-scale-review.md:76` | 抽样产出必须同时给出三份清单： | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-051 | `knowledge/large-scale-review.md:80` | 3. 强制全量清单（L3 中的用例 ID） | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-052 | `knowledge/large-scale-review.md:82` | 三份清单相加必须等于用例总数 N，用于自检是否漏算。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-053 | `knowledge/large-scale-review.md:103` | 方案是交付物，必须包含以下 7 个部分，缺一不可。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-054 | `knowledge/large-scale-review.md:150` | - 强制全量清单：&#91;文件/列表&#93; | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-055 | `knowledge/large-scale-review.md:171` | - 退出条件：强制全量清单 100% 完成，且无未处置的 P0 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-056 | `knowledge/large-scale-review.md:177` | - 聚合阶段必须做四件事： | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-057 | `knowledge/large-scale-review.md:182` | - 任何一批未完成时，标注「未评审」，不得用其他批次的结论推断 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-058 | `knowledge/large-scale-review.md:193` | \| 时间不足以覆盖强制全量清单 \| 按 P0 → 主流程 → 其余顺序削减 \| 其余写入未评审清单，明确告知风险与覆盖缺口 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-059 | `knowledge/large-scale-review.md:201` | \| 2 \| 把 P0 或主流程用例放入抽样池 \| 高风险场景被统计概率漏掉 \| 强制全量清单独立执行 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-060 | `knowledge/large-scale-review.md:202` | \| 3 \| 抽样不记录种子 \| 下次无法复现同一批样本，评审结论不可追溯 \| 固定 seed 并使用确定性哈希排序 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-061 | `knowledge/large-scale-review.md:203` | \| 4 \| 分批后不做聚合 \| 跨批重复问题虚高，系统性问题被掩盖 \| L5 四步聚合强制执行 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-062 | `knowledge/products/example.md:56` | \| BR-001 \| 用户名必须唯一 \| 注册/修改用户名时 \| 用户管理模块 \| PRD §3.1 \| | D4 | 参考/示例材料 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-063 | `knowledge/project-knowledge.md:3` | > **来源优先级**：用户明确要求 > 当前项目已确认资料 > Skill 通用知识 > 行业模板。冲突、缺少日期或疑似过期资料须注明来源与待确认事项；模板不覆盖项目事实，也不改写历史用例。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-064 | `knowledge/project-knowledge.md:5` | > **何时阅读**:阶段 1 信息收集时**必读**(SKILL.md 强制要求);遇到 Office/PDF 文件需要转换时必读。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-065 | `knowledge/project-knowledge.md:7` | > **跳过条件**:本次任务用户已直接提供需求文本/Markdown,且无项目内文档需扫描时必须跳过。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-066 | `knowledge/project-knowledge.md:14` | 在阶段 1 执行时，**必须主动扫描**项目中以下约定目录。存在则读取，不存在则跳过： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-067 | `knowledge/project-knowledge.md:36` | **步骤 2**：若不存在，由当前 Agent **主动执行转换**，生成可读文件后再读取，并**继续完成后续阶段**（需求理解 → 测试点提取 → 用例编写 → 自检）。**不得**回复「请先手动执行转换命令」或中途停下让用户操作。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-068 | `knowledge/project-knowledge.md:38` | > **安全提示**：执行转换命令前，必须遵守 &#91;integrations/quickstart.md&#93;(../integrations/quickstart.md)「安全约束」章节的参数传递与任务范围规则，不拼接或改写用户路径。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-069 | `knowledge/project-knowledge.md:53` | **若 MarkItDown 不可用**（Python < 3.10、安装失败、找不到命令），降级为共享 `convert_docs.py`（依赖已在 requirements.txt 中一并安装）： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-070 | `knowledge/project-knowledge.md:58` | 降级方案仅支持 `.docx`、`.xlsx`、`.pptx`，不支持 PDF 和 `.xls`，须在输出中说明局限。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-071 | `knowledge/project-knowledge.md:60` | **若完全无法创建 venv 或执行终端命令**：仅处理可直接读取的格式，对 Office/PDF 说明局限，建议用户导出为 Markdown/文本，**不得**无限重试失败命令。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-072 | `knowledge/prompt-strategy.md:5` | > **跳过条件**:用户明确要求人工编写用例时必须跳过本文件。 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-073 | `knowledge/prompt-strategy.md:35` | - 容错场景（网络异常、超时、依赖不可用、降级）：仅当需求明确要求容错时生成，否则一条都不写 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-074 | `knowledge/prompt-strategy.md:37` | 4. 最终业务结果必须具体可判定，模糊表达按语境判断 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-075 | `knowledge/prompt-strategy.md:47` | 8. 用例总数控制在用例集预算内（见 case-arrangement.md）；超出须在用例集开头写明理由 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-076 | `knowledge/prompt-strategy.md:101` | 每轮结束后合并等价场景，三轮累计结果仍须满足用例集预算 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-077 | `knowledge/prompt-strategy.md:125` | > **何时使用**：评审模式 R2 步骤执行第 10 维度「语义一致性」检测前，必须先用本提示词抽取 SemanticFacts。 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-078 | `knowledge/prompt-strategy.md:130` | 将每条用例的自然语言字段抽取为 SemanticFacts 结构。**只做理解+归一化，禁止做任何冲突判断**。 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-079 | `knowledge/prompt-strategy.md:160` | 1. **subject 归一化**：同一概念必须用相同字符串。 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-080 | `knowledge/prompt-strategy.md:173` | - 同一动作的不同数据必须体现在 signature 中 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-081 | `knowledge/prompt-strategy.md:185` | - 必须为每条输入用例产出一个 SemanticFacts，不得遗漏 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-082 | `knowledge/prompt-strategy.md:188` | - **禁止**在输出中包含任何"冲突""矛盾""不一致"等判断词——判定是下游 MCP 的事 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-083 | `knowledge/readability.md:12` | - 逗号分隔的构件以 20 字以内为目标；20–29 字可接受；30–39 字须语义清晰；超过 40 字必须改写 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-084 | `knowledge/readability.md:26` | - 「其」「该」「此」「这」必须有唯一指代；可能出现歧义时重复名词 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-085 | `knowledge/readability.md:32` | - 中文正文使用全角标点；英文原文、代码、字段值保留原样，不强制转换 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-086 | `knowledge/readability.md:95` | - 数据版本、时区、账号类型属于环境事实，影响判定时必须写明 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-087 | `knowledge/readability.md:130` | \| 系统应当向用户展示相应的提示信息 \| 页面顶部显示「保存成功」 \| | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-088 | `knowledge/readability.md:150` | - 一步一个决策点：一次提交、一次跳转、一次状态切换；同一表单的字段可一并填写，但不得跨页面、跨判断分支 | D2 | 当前在默认路径，可评估按需化 | 按需化：默认路径中的移出，已在按需的保留并标注 | 待复核 |
| test-case-engineer-089 | `knowledge/review-mode.md:9` | 满足以下任一条件**必须**进入评审模式，不走四阶段生成流程： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-090 | `knowledge/review-mode.md:52` | 机器只能检查输入事实与结构；业务语义结论必须引用原文、条件或执行证据。`candidate` 与 `confirmed` 分开输出，候选项不计入扣分、问题密度和通过率。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-091 | `knowledge/review-mode.md:115` | \| 覆盖度 \| 2 \| P0 \| TC_005-TC_008 缺少异常类型（type=异常 的用例为 0 条） \| 新增异常场景用例：网络断开/超时/依赖服务不可用 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-092 | `knowledge/review-mode.md:173` | \| P0 \| x \| x% \| 必须修订后方可执行 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-093 | `knowledge/review-mode.md:187` | > **目的**：定义从评审结论到修订完成的完整链路，确保修订有据可查、修订后必须复审、上下文不丢失。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-094 | `knowledge/review-mode.md:199` | - 明确「不修订」的用例须在修订报告中标注原因 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-095 | `knowledge/review-mode.md:203` | - 修订时必须携带评审上下文（见下方 schema），不得脱离评审意见重新生成 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-096 | `knowledge/review-mode.md:206` | - **强制复审**：修订后的用例必须重新走 R2 评审，但仅复审「受影响维度」 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-097 | `knowledge/review-mode.md:280` | 评审模式下发现缺失用例需要补充时，**必须**遵循 &#91;writing-rules.md&#93;(writing-rules.md)「补充用例 ID 生成规则（强制）」——ID 格式 `TC_{模块}_{功能}_{三位序号}`、模块/功能缩写从已有用例提取、序号 = 同模块+功能最大序号 + 1，禁止不规范格式（`TC_001`）、序号跳跃与缩写不一致。本处不再重复维护规则正文，以 writing-rules.md 为唯一权威源。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-098 | `knowledge/review-mode.md:288` | \| 用例数量过大（>100 条） \| 进入 &#91;large-scale-review.md&#93;(large-scale-review.md) 规模化评审子模式，按 L1-L5 输出评审方案 \| 至少完成强制全量清单（P0/主流程）评审，其余写入未评审清单并声明风险 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-099 | `knowledge/review-mode.md:289` | \| LLM 抽取的 facts 数量 ≠ 用例数 \| 重试抽取，提示词强调"必须为每条用例产出 facts" \| 跳过第 10 维度，标注「语义一致性降级：facts 抽取不完整（N/M）」 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-100 | `knowledge/review-mode.md:299` | \| 1 \| **直接修订用例而不输出意见表** \| 用户无法理解评审结论，失去评审透明度 \| 必须先输出意见表+建议清单，修订走用户授权修订后的默认生成模式 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-101 | `knowledge/review-mode.md:303` | \| 5 \| **评审越界：擅自改业务规则** \| 评审的职责是检查用例质量，不是改业务规则；擅自改规则会让用例脱离需求意图 \| 评审意见只引用规则、指出问题，业务规则变更须回溯需求文档并由产品确认后，再通过修订闭环走生成模式修订 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-102 | `knowledge/review-mode.md:304` | \| 6 \| **评审主观化：不引用判定规则** \| 「感觉这个用例不好」「这个步骤写得不清楚」等主观判断无法复核，也无法转化为机器可校验的规则 \| 每条评审意见必须引用 R2 表中对应的判定规则（如「最终业务结果缺失」「检查点引用不存在的步骤」），并给出具体用例 ID + 字段 + 命中证据 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-103 | `knowledge/review-mode.md:305` | \| 7 \| **评审遗漏维度** \| 只评覆盖度和字段规范、跳过优先级合理性/可执行性/冗余/溯源/可维护性/可自动化/测试数据依赖，导致系统性问题被掩盖 \| R2 必须覆盖全部 10 维度；溯源维度在无需求文档时按失败模式 #2 降级，但不得直接跳过；度量报告的维度分布表用于自检 10 维度是否均有产出 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-104 | `knowledge/review-mode.md:306` | \| 8 \| **语义一致性维度全靠 LLM 主观判断** \| LLM 直接说"这两条用例冲突"无法复核，也无法转化为机器可校验规则 \| 必须先抽取 SemanticFacts（结构化），再由 MCP 确定性规则判定；评审意见必须引用具体冲突类型规则（如"命中类型①：subject 相同且 polarity 互斥"）+ 给出冲突对 evidence \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-105 | `knowledge/review-mode.md:316` | 用例数量过大时的组织方案独立维护在 &#91;large-scale-review.md&#93;(large-scale-review.md)：规模画像 → 策略选择 → 强制全量清单与分层抽样 → 评审方案输出 → 分批执行与聚合。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-106 | `knowledge/review-mode.md:340` | > **安全提示**：执行 git diff 前，必须遵守 &#91;../integrations/quickstart.md&#93;(../integrations/quickstart.md)「安全约束」章节的 git diff 范围安全规则。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-107 | `knowledge/review-mode.md:348` | - 冗余维度：变更用例须与**全量用例**比对（变更用例可能与未变更用例重复） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-108 | `knowledge/review-mode.md:359` | \| 用例文件不在 git 仓库中 \| 提示用户确认路径，或改用全量评审 \| 降级为全量评审，标注「增量模式不可用，已转全量」 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-109 | `knowledge/review-plan.md:62` | - 每条需求至少关联 1 条用例；无关联的必须标「未覆盖」或「不测」并写明理由 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-110 | `knowledge/review-plan.md:67` | 覆盖度必须用「需求/场景」口径，不能用用例条数或执行通过率替代。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-111 | `knowledge/review-plan.md:75` | \| 不测范围占比 \| 不测需求项 / 需求项总数 \| x% \| 必须逐项给出理由 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-112 | `knowledge/review-plan.md:89` | **原则**：缺口必须给出处置（补用例 / 接受风险 / 移出范围），不能只列「未覆盖」三个字。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-113 | `knowledge/review-plan.md:93` | 面向非测试角色时，必须用业务语言讲，每一项「一句话结论 + 一个具体例子」，不堆测试术语。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-114 | `knowledge/review-plan.md:106` | **禁止**：只报用例条数、只讲正向流程、用「已充分覆盖」这类不可验证的结论。 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-115 | `knowledge/review-plan.md:140` | \| 不通过 \| 需求不一致、关键场景未覆盖或风险不可接受 \| 修订后重新评审 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-116 | `knowledge/review-plan.md:253` | \| 6 \| 评审会没有决策人 \| 问题议而不决，结论无效 \| 明确产品/技术负责人必须到场 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-117 | `knowledge/review-rubric.md:11` | 3. 每条判定必须引用原文片段；引不出原文的判定视为无效 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-118 | `knowledge/review-rubric.md:19` | - **给改法**：每条问题必须给出可执行的修改方向，而不是"建议优化" | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-119 | `knowledge/review-rubric.md:36` | **必须引用**：该条业务结果原文 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-120 | `knowledge/review-rubric.md:51` | **必须引用**：未覆盖的测试点编号 + 裁剪说明原文（若有） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-121 | `knowledge/review-rubric.md:68` | **必须引用**：冲突的两处原文 + 所在用例 ID | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-122 | `knowledge/review-rubric.md:84` | **必须引用**：该步骤原文 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-123 | `knowledge/review-rubric.md:97` | **必须引用**：步骤原文 + 预期原文 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-124 | `knowledge/review-rubric.md:112` | **必须引用**：标题 + 步骤中体现多目标的那几步 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-125 | `knowledge/review-rubric.md:127` | **必须引用**：优先级分布 + 至少 2 条存疑用例及其理由缺失之处 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-126 | `knowledge/review-rubric.md:145` | **必须引用**：该用例的追溯字段原文 + 被指向对象的实际情况 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-127 | `knowledge/review-rubric.md:155` | - 需求未要求容错，却出现基础设施故障用例：断网、5xx、超时、依赖不可用、宕机、降级 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-128 | `knowledge/review-rubric.md:160` | - 需求明确要求容错、降级、重试——此时故障场景是焦点，必须覆盖，不判越界 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-129 | `knowledge/review-rubric.md:161` | - 该场景是焦点项失败隔离所必需（如必须先登录才能触发被测行为） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-130 | `knowledge/review-rubric.md:165` | **必须引用**：用例 ID + 需求原文位置；判 FAIL 的「需求无对应条目」也要写明检索范围（如「PRD 全文无『断网』『降级』『超时』字样」）。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-131 | `knowledge/review-rubric.md:220` | - **禁止输出总分或等级**（如"质量 85 分""整体良好"）——无法执行 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-132 | `knowledge/review-rubric.md:221` | - **禁止改写用例**——评审者只给建议，改写由生成方执行 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-133 | `knowledge/review-rubric.md:222` | - **禁止无引用判定**——说不出原文位置的，不报 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-134 | `knowledge/review-rubric.md:223` | - **禁止重复 D 类问题**——格式、词表、句长由脚本负责 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-135 | `knowledge/review-rubric.md:224` | - **禁止为凑数报问题**——宁可报 2 条真的，不报 10 条虚的 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-136 | `knowledge/scope-discipline.md:6` | > **要解决的问题**：用例数量不少，但真正属于本次需求的只有一半——服务故障、边界值膨胀、非重点内容占掉了篇幅，评审和执行的人分不清哪条必须做。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-137 | `knowledge/scope-discipline.md:41` | 三问的作用不是减少覆盖，而是把「谁的锅」分清：断网、5xx、数据库不可用属于平台与运维，需求没要求时写进用例集，等于让本需求为别人背书。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-138 | `knowledge/scope-discipline.md:66` | > 反例：需求只改「保存」按钮文案，用例集里出现「断网时点击保存」「接口返回 500 时提示」「数据库不可用时降级」三条——三条都不属于本次需求。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-139 | `knowledge/scope-discipline.md:123` | \| 归运维/平台 \| `范围外：依赖不可用归平台容错，需求未要求` \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-140 | `knowledge/scope-discipline.md:126` | 禁止：`暂不覆盖`、`后续补充`、`根据情况`、留空。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-141 | `knowledge/test-levels.md:4` | > **覆盖范围**：E2E / API / 契约 / 集成 / 单元 五层定义、本 Skill 默认重心、禁止混层规则、L1/L2-A/L2-B/L3 编排组占比、默认输出类型、与上游策略的分层映射。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-142 | `knowledge/test-levels.md:29` | - 若用户或需求明确后端/接口，则**重心必须上移到 API**，禁止用纯 UI 步骤代替服务侧验证 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-143 | `knowledge/test-levels.md:33` | - **禁止**：在一条「接口用例」里只写「打开页面点击」而无请求/断言 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-144 | `knowledge/test-levels.md:34` | - **禁止**：在「E2E 用例」里堆砌大量底层字段而又无操作上下文 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-145 | `knowledge/test-levels.md:39` | 1. 需求文档**仅描述接口/无界面** → 必须以 **API（+契约按需）** 为主 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-146 | `knowledge/test-levels.md:40` | 2. 需求**强依赖浏览器/多端流程** → 必须以 **E2E** 为主，API 作为辅助或回归子集 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-147 | `knowledge/test-levels.md:41` | 3. **重构无行为变更** → 必须使用回归清单，禁止强行补全所有分层 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-148 | `knowledge/test-levels.md:42` | 4. **不确定** → 必须在「存疑点」中列出，并在测试点表中标注分层列 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-149 | `knowledge/test-levels.md:64` | 1. 需求涉及核心算法/复杂计算？→ 必须选择 L1 单元测试 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-150 | `knowledge/test-levels.md:65` | 2. 需求涉及跨接口业务闭环？→ 必须选择 L2-A 业务场景测试 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-151 | `knowledge/test-levels.md:66` | 3. 需求涉及 API/数据/第三方？→ 必须选择 L2-B 接口测试 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-152 | `knowledge/test-levels.md:67` | 4. 需求涉及 UI/交互/体验？→ 必须选择 L3 E2E 测试 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-153 | `knowledge/test-standards.md:21` | - 在同一功能模块内唯一，不允许仅靠编号区分 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-154 | `knowledge/test-standards.md:25` | **超长标题例外判定**：标题长度是可读性指导，不应凌驾于场景可区分性。满足以下任一条件的超长标题可保留，但须在用例备注中记录保留原因： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-155 | `knowledge/test-standards.md:30` | > **禁止**：为满足 40 字而截断标题或添加省略号——这会破坏标题语义，导致场景不可区分。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-156 | `knowledge/test-standards.md:36` | \| P0 \| 核心流程不可用、重大资金或数据损失、关键安全边界失效等阻断风险 \| 作为相关发布的准入检查 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-157 | `knowledge/test-standards.md:75` | - 参数要显式说明具体值，禁止只写"边界值""非法值" | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-158 | `knowledge/test-standards.md:85` | - 必须具体、可验证，可直接用于判定 pass/fail | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-159 | `knowledge/test-standards.md:173` | \| 核心同步更新 \| P0/P1 用例必须随需求同步更新 \| 所有用例 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-160 | `knowledge/writing-examples.md:207` | - 系统应当对超出长度限制的输入进行拦截，并在界面上给出相应的错误提示信息 | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-161 | `knowledge/writing-examples.md:238` | \| 业务结果 \| 应当…进行拦截，并给出相应的错误提示信息 \| 显示「昵称不能超过 20 个字」 \| 愿望式 + 「相应的」无信息，改为具体文案 \| | D4 | 已在按需文件，保留并核对读取时机 | 参考/示例：评估是否保留为按需材料，无证据不删 | 待复核 |
| test-case-engineer-162 | `knowledge/writing-rules.md:16` | **块结构（强制）**：每条用例必须以 `### TC_{模块}_{功能}_{序号}: 标题` 三级标题起始。这是脚本校验的锚点——用列表、加粗或表格代替标题时，整条用例不会被任何规则检查，等同于未校验。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-163 | `knowledge/writing-rules.md:54` | > **边界**：这是**块内**的数据组织方式，不是用例的承载格式。每组仍必须有自己的 `### TC_xxx: 组名` 标题，表格只在组内展开数据行。用一张表罗列全部用例（无块标题、跨组混排）属于格式违规，脚本报 `FILE_FORMAT`。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-164 | `knowledge/writing-rules.md:77` | - 仅限 P2/P3 且验证逻辑同构的用例组；P0/P1 必须用完整块状格式 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-165 | `knowledge/writing-rules.md:78` | - 表头必须含「用例 ID」「操作」「预期结果」三列，可按需增列；缺任一一列即格式不合规，必须改回完整块状格式 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-166 | `knowledge/writing-rules.md:80` | - 单组行数不超过 10 行；跨验证逻辑的用例禁止合组 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-167 | `knowledge/writing-rules.md:81` | - 每行仍必须有独立 ID（可用字母后缀 `006a/006b`）与可判定的预期结果 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-168 | `knowledge/writing-rules.md:86` | 当评审模式或阶段 4 自检发现缺失用例需要补充时，**必须**按以下规则生成 ID： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-169 | `knowledge/writing-rules.md:110` | \| **标题** \| 是 \| `被测对象 - 具体行为/条件/结果`，建议 40 字以内（软指导）；信息删除会造成同模块场景重复或无法识别环境/版本时可保留长标题，禁止通过截断、`...` 或「等」隐藏关键条件 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-170 | `knowledge/writing-rules.md:117` | \| **业务背景** \| 否 \| 以「验证」开头，一句话说清条件、对象、动作和结果方向（超过 40 字须改写）；不复述步骤 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-171 | `knowledge/writing-rules.md:123` | \| **标签** \| 否 \| 小写 kebab-case，1–5 个，首位必须是业务域；规则见下方「Tag 规范」 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-172 | `knowledge/writing-rules.md:197` | **业务背景固定一句话**：条件 + 对象 + 结果方向，按句式口径超过 40 字须改写；不写「在…的前提下」「针对…进行…」。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-173 | `knowledge/writing-rules.md:205` | - 句长：逗号分隔的构件以 20 字为目标，20–29 可接受，30–39 须语义清晰，超过 40 字必须改写；单条步骤或预期不超过 100 字 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-174 | `knowledge/writing-rules.md:214` | 可执行性保证用例能跑，可读性保证人能看懂。两者冲突时先保证可执行，再用最少的字表达；不得为了「好看」弱化可判定性。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-175 | `knowledge/writing-rules.md:220` | - 必须包含：验证对象、用户行为（若存在）、条件与可观察结果 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-176 | `knowledge/writing-rules.md:222` | - 建议不超过 40 字；信息一旦删除会造成同模块场景重复或无法识别环境/版本时，可保留长标题；禁止通过截断、`...` 或「等」隐藏关键条件 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-177 | `knowledge/writing-rules.md:224` | - 禁止：`验证 Width`、`验证布局`、`验证 Rounded 为 16px`、`验证登录功能`、`验证优惠券创建` | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-178 | `knowledge/writing-rules.md:235` | - 涉及输入、选择、配置时必须明确具体值 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-179 | `knowledge/writing-rules.md:237` | - 禁止占位话术：`按测试点要求执行...`、`执行对应操作`、`验证相关功能` | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-180 | `knowledge/writing-rules.md:240` | - 禁止在步骤中使用 `if/else` 描述不同路径；每个条件分支应成为独立用例 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-181 | `knowledge/writing-rules.md:247` | - 必须明确、可验证、可定位，指明至少一类可观察证据： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-182 | `knowledge/writing-rules.md:253` | - 最终业务结果必须可判定；只在必要的中间状态、后续操作入口或风险判断处设置关键检查点 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-183 | `knowledge/writing-rules.md:254` | - 同一业务动作可关联页面、业务状态、消息或数据结果；不因证据层次不同强制拆分，不合并独立业务目标 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-184 | `knowledge/writing-rules.md:255` | - 禁止使用：`结果正确`、`符合预期`、`配置正确`、`功能正常`、`应生效`、`与测试目标一致` | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-185 | `knowledge/writing-rules.md:258` | - 必须与 steps 中的实际操作直接对应；禁止生成 steps 中未发生操作的预期结果 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-186 | `knowledge/writing-rules.md:275` | - 来源不可达与业务结果未知分列；未读到来源不补造版本/确认关系，独立Skill无完整图仍可输出并注明追溯未评估。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-187 | `knowledge/writing-rules.md:278` | - **与标题规则反向，勿混用**：业务背景必须以「验证」开头，标题必须不以「验证」开头——`验证…` 归业务背景，标题从被测对象写起 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-188 | `knowledge/writing-rules.md:308` | \| 不可执行表达 \| 改为 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-189 | `knowledge/writing-rules.md:328` | Tag 使用小写 kebab-case，单条 1–5 个。第一个 Tag 必须是业务域；后续按筛选价值由宽到窄排列： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-190 | `knowledge/writing-rules.md:360` | **独立性**：用例默认独立可执行，不依赖其他用例的执行顺序或产物。必须串联时，在前置条件显式声明依赖来源（如 `已存在订单 ORD-20261031-001，由 TC_ORDER_ADD_001 创建`），并在被依赖用例的后置条件声明保留；共享准备写进前置条件，不写「执行上一条用例」。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-191 | `knowledge/writing-rules.md:364` | **可读性检查**：步骤或结果较多时检查重复导航、无关目标、路径分支及失败定位能力；可以分业务阶段组织，不以固定数量强制拆分。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-192 | `knowledge/writing-rules.md:388` | 用例输出必须采用通用结构化格式（Markdown），优势： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-193 | `knowledge/writing-rules.md:393` | 导入特定测试管理工具时，必须使用脚本或手动转换。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-194 | `test-case-engineer-core.md:69` | \| 代码库无权限或不可达 \| 请求用户提供关键代码片段或 API 文档 \| 基于需求文档推断，标注「待验证」；不可达的代码位置回填「原文问题清单」（位置=文件路径，类型=缺失） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-195 | `test-case-engineer-core.md:112` | - 非法状态：&#91;不允许的状态流转&#93; | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-196 | `test-case-engineer-core.md:132` | - 必须重点测试范围：&#91;需要重点覆盖的场景&#93; | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-197 | `test-case-engineer-core.md:135` | - &#91;需求未明确的地方，必须标注"待产品确认"或"待需求补充"&#93; | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-198 | `test-case-engineer-core.md:191` | 三类默认不写的用例与准入条件见 &#91;knowledge/scope-discipline.md&#93;(knowledge/scope-discipline.md)：服务故障类（断网/5xx/超时/降级/依赖不可用）、边界值膨胀、非重点内容展开。需求本身要求容错时，容错条目属于焦点，不受此限。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-199 | `test-case-engineer-core.md:215` | - 禁止：`验证保存成功并且页面展示正确` | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-200 | `test-case-engineer-core.md:216` | - 必须：拆分为 `验证保存成功` + `验证页面展示正确` 两条测试点 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-201 | `test-case-engineer-core.md:219` | - 禁止在一个测试点中同时验证： | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-202 | `test-case-engineer-core.md:226` | - 每个测试点必须包含：&#91;验证对象&#93; + &#91;操作/场景&#93; + &#91;预期结果方向&#93; | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-203 | `test-case-engineer-core.md:227` | - 禁止：`验证 General updates 可以关闭`（太模糊） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-204 | `test-case-engineer-core.md:228` | - 必须：`验证 General updates 状态开关(Toggle)切换至关闭并保存后，配置项保持关闭状态` | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-205 | `test-case-engineer-core.md:232` | - 描述深度与焦点一致：焦点项写完整，非焦点内容只保留 1 条冒烟；禁止把需求一句话带过的旧功能写成多步用例 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-206 | `test-case-engineer-core.md:233` | - 禁止大量生成低风险 UI 测试点 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-207 | `test-case-engineer-core.md:241` | - **容错类**（重复提交、操作中断、依赖不可用、超时）：仅当需求要求容错时才落为用例，否则按范围闸门判为范围外 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-208 | `test-case-engineer-core.md:292` | \| 缺陷模式库无匹配 \| 使用通用缺陷模式（输入校验/状态/权限/数据/UI） \| 仅输出 7 维度扫描结果，不强制补充 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-209 | `test-case-engineer-core.md:302` | **输出**：测试用例（每条以 `### TC_{模块}_{功能}_{序号}: 标题` 块承载；表格仅用于块内承载同构数据组，**不得用整表罗列全部用例**） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-210 | `test-case-engineer-core.md:328` | **阶段 3 输出**：生成后完成本阶段自检即进入阶段 4；最终交付以阶段 4 脚本校验通过为准。`source: ai-generated` 表示来源；人工审核状态单独记录，未经人工审阅不得声称已审核。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-211 | `test-case-engineer-core.md:336` | \| 业务结果不明确或关键检查点不可定位 \| 对照业务目标与真实操作补充判定证据 \| 按 writing-rules.md 调整目标和步骤组织 \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-212 | `test-case-engineer-core.md:337` | \| 用例标题超过 40 字 \| 尝试精简为 `被测对象 - 具体行为/条件/结果` \| 若信息删除会造成同模块场景重复或无法识别环境/版本，保留长标题（禁止通过截断、`...` 或「等」隐藏关键条件） \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-213 | `test-case-engineer-core.md:375` | \| 有 error \| 逐条修复后重跑，**禁止交付** \| `✗ 脚本校验未通过（N error）` \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-214 | `test-case-engineer-core.md:376` | \| 脚本不可用 \| 按 `validate_cases.py` 的规则码人工逐条核对 \| `⚠ 未脚本校验（原因）` \| | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-215 | `test-case-engineer-core.md:380` | - 交付时贴出校验结果摘要（文件数 / 用例数 / error 数），不得只写「已校验」 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-216 | `test-case-engineer-core.md:381` | - 脚本只覆盖 D 类（格式 / 枚举 / 词表 / 句长 / 结构 / 编排）；`validate_cases.py` 输出末尾列出的 J 类规则仍须人工或评审 agent 判定 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-217 | `test-case-engineer-core.md:382` | - warning 不阻断交付，但须在交付说明中列出未处理项及理由 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-218 | `test-case-engineer-core.md:384` | - 不得把「脚本校验通过」写成「人工审核通过」「用例已执行」或「质量已达标」 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-219 | `test-case-engineer-core.md:402` | - 缺少测试点清单时，覆盖度判为「无法评估」，不得臆测 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-220 | `test-case-engineer-core.md:416` | > **脚本无法判定，必须逐项确认**：覆盖度、范围相关性、可追溯性、业务结果可判定性、术语全文一致、步骤可执行性、拆分合并合理性、优先级业务依据。 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-221 | `test-case-engineer-core.md:464` | - **默认**：不允许跳过阶段 1/2 直接写完整用例 | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-222 | `test-case-engineer-core.md:465` | - **快速**：压缩阶段 1/4 的需求理解与人工自检，但必须输出测试点清单，文首声明未做完整理解；**阶段 4 脚本校验不得跳过**（0 error 方可交付） | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
| test-case-engineer-223 | `test-case-engineer-core.md:478` | **须记录证据**：&#91;截图、日志片段、trace id、请求/响应摘录&#93; | D5 | 工作流/输出/安全等行为规则 | 行为规则：默认保留；删除需配对评测 | 待复核 |
