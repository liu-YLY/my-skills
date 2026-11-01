# 测试用例 Skill 四目标优化执行计划（待审批）

> **状态**：**阶段 0 已确认、阶段 A 已完成；停在停止点 A，等待用户决定阶段 B**
> **执行方式**：每阶段结束写回本文件 §9.1 交接快照；每任务一个本地 commit；不自动跨阶段
> **基线**：`main` @ `1557de5`（2026-11-01 21:00 实测），工作区干净，6 个仓库校验脚本全绿
> **目标 skill**：`plugins/testing/skills/test-case-engineer` v9.10.0
> **终局目标**：生成**准确、精简、覆盖面全、人类可读性强**的测试用例
> **本文件同时是执行计划与执行记录**：每完成一个任务更新 §9，改动与记录放在同一个 commit 中

---

## 0. 需要你先拍板的决策

| 编号 | 决策 | 选项 | 推荐 |
|---|---|---|---|
| D1 | 执行范围 | ① 最小闭环 A+B+C ② A+B+C+D ③ 全部（含 D/E） ④ 只做 A ⑤ 暂不执行 | **① 最小闭环 A+B+C**：先建立评测基线，再接通机器校验，再立精简硬约束；D/E 风险高、依赖外部评测，另行决策 |
| D2 | 真实模型评测怎么做 | ① 本会话干跑验证（标 `dry_run`，可信度低） ② 外部独立 runner + judge ③ 本轮不跑，只交付可复现评测套件 | **① + ③**：本会话做干跑可用性验证，正式跑分设为阶段 A 之后的显式停止点，不承诺质量分数 |
| D3 | 用例总量阈值（写入 skill 前必须确认） | 单字段纯校验 ≤8 条 / 常规单功能 ≤15 条 / 多功能多状态 ≤25 条（可自定） | **按上述三档**，作为软预算而非硬扣分；超出须在用例集开头写明理由 |
| D4 | 发布方式 | ① 只本地提交，不推送 ② 本地分支 + 堆叠 PR ③ 单 PR | **① 只本地提交**，每任务一个 commit；是否推送/建 PR 在阶段 F 另行确认 |
| D5 | 是否改 review-checker MCP | ① 不改（只写 skill 侧调用约定） ② 连 MCP 一起升级 | **① 不改**：E 阶段的 `check_coverage` 升级涉及契约与单测，单独立项 |

**决策结果（2026-11-01 用户确认）**：D1=① 最小闭环 A+B+C；D2=①+③ 会话内干跑 + 只交付可复现套件；D3=按推荐三档（单字段 8 / 常规 15 / 复杂 25 条，软预算）；D4=① 只本地提交；D5=① 不改 MCP。

**阶段 B 决策（2026-11-01 二次确认）**：① 按 B0→B1→B2 执行；② B2 对照干跑按推荐的最小规模（合法/问题/边界三组样例）；③ D3 阈值按推荐（8/15/25 条）写入阶段 C。三项均按推荐方案执行。

**用户追加的工作方式**：每执行一个阶段就在本地保存执行状况，由用户决定下一阶段如何执行；目的是避免任务过长导致上下文反复压缩、目标漂移、质量下降。因此本计划以最新阶段的交接快照（当前为 §9.2）为唯一进度源，不依赖会话记忆；历史快照保留不覆盖。

---

## 1. 目标与非目标

### 1.1 四目标的可判定定义

| 目标 | 可判定指标 | 验证主体 |
|---|---|---|
| 准确 | 每条预期结果可追溯到需求原文条款；需求与实现矛盾时并列保留差异；机器校验无 P0/P1 可执行性问题 | judge + 机器 |
| 精简 | 用例总数在 D3 预算内；等价业务目标不重复；同构数据合为参数化组；交付物由 4 份收敛为 2 份 | judge + 计数 |
| 覆盖全 | 阶段 1 列出可测需求条目作分母；输出「需求 → 测试点 → 用例」矩阵；未覆盖项显式列出 | judge + 计数 |
| 可读性强 | 标题可独立定位测试点；长句/术语不一致/填充步骤可计量；机器校验 3 项可读性候选为 0 | 机器 + judge |

### 1.2 非目标

- 不改四阶段骨架，不引入 Gherkin，不新增第 11 评审维度
- 不改动历史用例与历史评测报告（沿用 10-31 专项约定）
- 不把「结构分上涨」当作质量提升；无独立评测前不得宣称效果改善
- 不在 `main` 上直接提交；不推 `git push --force`
- 不做纯文本可读性公式打分（中文分词不匹配）

---

## 2. 基线：已实测，非推测

| # | 约束 | 实测值 / 出处 | 对计划的影响 |
|---|---|---|---|
| B1 | 仓库校验 | `python --version` = 3.13.14；`skill-evals.py`、`check-skill-consistency.py`、`check-version-sync.py`、`check-knowledge-count.py`、`check-project-inventory.py`、`check-md-links.py` **6 项全绿** | 任何阶段结束必须回到全绿 |
| B2 | 评测集规模 | `python scripts/skill-evals.py --skill test-case-engineer` → **34 task / 12 trigger**；34 = skill 内 32 + `docs/skill-evaluation/business-regressions.json` 的 2 条 | 改评测集时不能漏掉跨文件的 2 条 |
| B3 | 评测脚本能力 | `skill-evals.py` 结尾明确打印 `Input validation only; model behavior has not been evaluated by this command.`；`--json` 导出用例、`--results` 只校验并汇总**外部产出**的 JSONL | **仓库内没有模型 runner / judge**，见 §3 |
| B4 | 触发用例完整性 | `validate_trigger_coverage` 要求 `positive / negative / near_miss / skill_conflict` 四类齐全，且至少一条 `true`、一条 `false` | 新增 task 用例不影响；动 trigger 用例必须复核 |
| B5 | core 行数硬上限 | `test-case-engineer-core.md` **500 行**，`CORE_LINE_LIMIT = 500`（`check-skill-consistency.py:106`） | **净增 1 行即 CI 失败**；阶段 B 必须先瘦身（B0） |
| B6 | 一致性不变量 | 6 项：知识文件从 SKILL.md 可达、模块定义、SKILL_ROOT 路径、模式定义一致、安全约束覆盖、core 行数 | 新增 knowledge 文件必须被 SKILL.md 链接且被引用，否则报 dead/orphan |
| B7 | 版本同步 | 升 `test-case-engineer` 版本需同步至少 8 处，见 §2.1 | 阶段 F 统一处理，中途不逐任务升版本 |
| B8 | 文件清单联动 | 增删 skill 目录下 `.md` 会改变「配套 Markdown 文件数」，需 `python scripts/check-project-inventory.py --write` 更新根 `README.md` | **优先不新增文件**（B0 用压缩而非迁移） |
| B9 | 链接与格式 | `docs/superpowers/` 被 `check-md-links.py` 排除；但 CI 的 markdownlint 覆盖 `docs/**/*.md`（`.markdownlint.jsonc` 默认规则启用） | 本计划文件本身需通过 markdownlint |
| B10 | 历史评测无区分度 | 2026-09-15 对照：9 任务 ×3 次，有 Skill / 无 Skill 均 **81/81 通过**；主代理人工判定、未盲评 | 新评测用例必须设计成能区分好坏，见 §6 |
| B11 | 上下文成本 | 10-10 报告：默认生成路径 28,585 代理 token（阶段 3 单项 11,778）；真实样本「生成 1 条支付用例」input 中位数 136,339 | 精简目标有量化起点，但 token 需按同方法重测 |
| B12 | 评测未跑 | `docs/skill-evaluation/reports/2026-10-31-baseline.md` 明确「模型行为评测未执行、token 未重测、跨 skill 路由回归未跑」，现有分数仍是 10-10 旧数据 | 阶段 A 的首要任务是补齐可跑的评测套件 |

### 2.1 版本同步清单（升 test-case-engineer 版本时）

| # | 文件 | 位置 |
|---|---|---|
| 1 | `plugins/testing/skills/test-case-engineer/SKILL.md` | frontmatter `version`（L3） |
| 2 | `plugins/testing/skills/test-case-engineer/test-prompts.json` | 顶层 `version`（L3） |
| 3 | `plugins/testing/skills/test-case-engineer/README.md` | 前 5 行 tagline（L3） |
| 4 | `plugins/testing/skills/test-case-engineer/README.md` | 「版本历史」首条（L156） |
| 5 | `README.md` | 根技能表 `test-case-engineer` 行（L27） |
| 6 | `docs/skills-overview.md` | test-case-engineer 节 `**版本**`（L170） |
| 7 | `plugins/testing/README.md` | 能力矩阵版本（L17） |
| 8 | `CHANGELOG.md` | `## [Unreleased]` 条目（惯例，非脚本强制） |

> 若同时升 `testing-bundle`，另需 `testing-bundle/SKILL.md`、`testing-bundle/CHANGELOG.md`、`plugins/README.md`、`docs/skills-overview.md:7`、三个 runtime 的 `plugin.json` 与 `marketplace.json` 描述；最终以 `python scripts/check-version-sync.py` 为准。

---

## 3. 可行性边界（必须先说清）

1. **仓库内没有模型评测执行器**。`skill-evals.py` 只做输入校验与结果汇总；历史上 2026-09-15 的对照评测是**人工组织 agent 跑 + 主代理人工判定**，没有可复跑脚本。
2. 因此本计划能单方面交付的是：**Tier 1 确定性校验、可复现评测套件、冻结基线、干跑验证**。真实质量分数需要独立 runner 与独立 judge（方法论 §7 要求 judge 模型 ≠ 被测模型），属于外部依赖。
3. 阶段 A 之后设**显式停止点**：若无独立评测环境，后续阶段只能报告「结构/Tier 1 检查结果」，**不得**在 CHANGELOG 或交付报告里写「质量提升」。
4. 干跑结果必须标注 `dry_run` 与「可信度低」，按方法论 §5.4 只作趋势参考，不作为 keep/revert 依据。
5. 新增/修改 `test-prompts.json` 的 expectations 后，`--results` 要求 `check_results` 布尔数组长度与 expectations 严格相等，**历史 `runs.jsonl` 与新套件不兼容**；必须冻结新套件 SHA256，并声明跨版本分数不可比。

---

## 4. 阶段与停止点

```text
阶段 0  用户决策（D1–D5）  ← 当前位置
   ↓ 确认后开分支
阶段 A  建立可判定评测基线（不改动 skill 行为）
   ↓ 🔴 停止点 A：确认评测套件与干跑结论
阶段 B  接通确定性机器校验（先给 core 瘦身）
   ↓ 🔴 停止点 B：确认无误判
阶段 C  精简硬约束（风险最高，改生成规则）
   ↓ 🔴 停止点 C：确认条数/重复率变化
阶段 D  规则单一来源 + 输出格式瘦身（可选，D1=②/③ 才执行）
阶段 E  覆盖度可计算 + MCP 升级（可选，D1=③ 且 D5=② 才执行）
阶段 F  全量校验 → 版本同步 → 提交/交付报告
```

| 阶段 | 任务 | 主要产出 | 停止条件 | 需用户批准 |
|---|---|---|---|---|
| 0 | 决策 | 本文件 §0 填写结果 | D1–D5 已定 | 是（当前） |
| A | A1–A4 | 评测集、执行协议、冻结基线 | 6 脚本全绿 + 停止点 A | 是 |
| B | B0–B2 | core 瘦身 + 阶段 4 机器校验约定 | 6 脚本全绿 + 无误判 | 是 |
| C | C1–C4 | 精简硬约束 | 6 脚本全绿 + 干跑对比 | 是 |
| D | D1–D3 | 规则去重、格式与叙事统一 | 6 脚本全绿 | 是 |
| E | E1–E2 | 覆盖矩阵 + MCP 升级 | 6 脚本 + MCP pytest 全绿 | 是 |
| F | F1–F4 | 版本同步、提交、交付报告 | `git status` 干净 | 是 |

> **当前位置**：阶段 0 / A / B 已完成；**停在停止点 B**，阶段 C 及以后均未执行。

> **规则**：每个阶段结束输出「commit 列表 + 校验结果 + 下一阶段建议」，不自动跨阶段；每任务一个 commit，Conventional Commits 中文 subject。

---

## 5. 任务清单（逐条可执行）

### 阶段 A：建立可判定的评测基线

| ID | 范围 | 具体动作 | 验收命令 | 行数预算 | 版本 |
|---|---|---|---|---:|---|
| A1 | `test-case-engineer/test-prompts.json` L12/24/35/70/288/321；`README.md` L92；`knowledge/writing-rules.md` L6 | 6 处「输出包含 CHECKPOINT 阶段 4 自检(报告)」改为与 `core.md` 实际一致的「输出包含阶段 4 用例自检结论」；README/writing-rules 中「core.md 含 CHECKPOINT」的残留表述改为「阶段自检」 | `python scripts/skill-evals.py` + `python scripts/check-md-links.py` + `python scripts/check-skill-consistency.py` | ±10 | 不升 |
| A2 | `test-case-engineer/test-prompts.json`；`docs/skill-evaluation/business-regressions.json` | 新增 8 条 task 用例（四目标各 2 条，草案见 §6）；把 #1/#2/#24/#32 的「输出包含 XX」存在性断言改写为可判定断言；核对 business-regressions 的 2 条不受影响；trigger_evals 四类保持齐全 | `python scripts/skill-evals.py --skill test-case-engineer` → 42 task / 12 trigger 且无报错 | +80 | 不升 |
| A3 | 新建 `docs/skill-evaluation/test-case-quality-eval-protocol.md` | 写清：`--json` 导出、runner 必填字段、judge 独立性、dry_run 标注、`--results --expected-runs 3` 复跑方式；附 JSONL 模板 | `python scripts/check-md-links.py` + markdownlint | +70 | 不升 |
| A4 | 新建 `docs/skill-evaluation/reports/2026-11-01-test-case-quality-baseline.md` | `skill-evals.py --skill test-case-engineer --json` 导出并记 SHA256；用 1 个简单功能做会话内干跑，按四目标逐条核对，标 `dry_run` / 可信度低；明确「未产出质量分数」 | 6 脚本全绿；文档含未验证项声明 | +60 | 不升 |

> A2 的 expectations 必须避开 `正常/正确/合理` 等不可判定词，平均长度 ≥20 字符（方法论 §12 规则 6），否则触发「测试集质量降级警告」。

### 阶段 B：接通确定性校验（不新增文件）

| ID | 范围 | 具体动作 | 验收命令 | 行数预算 | 版本 |
|---|---|---|---|---:|---|
| B0 | `test-case-engineer-core.md` L56–97 | 「产品知识库加载（阶段 1 必做）」约 41 行与 `SKILL.md` L119–138 重复；**压缩为 3 行摘要 + 指向 SKILL.md 该章节**，core 净减约 38 行至 462 行。不新增文件、不迁移语义 → 不触发 B6/B8 | `python scripts/check-skill-consistency.py`（core ≤500）+ `check-knowledge-count.py` + `check-md-links.py` | −38 | 不升 |
| B1 | `test-case-engineer-core.md` 阶段 4；`SKILL.md` 模式读取矩阵；`README.md` 能力列表 | 阶段 4 增加「机器校验」步骤约 18 行：自检后调用 review-checker 的字段规范/可执行性/冗余/溯源 4 类确定性校验；三模式（增强/独立/降级）标记与「未校验」披露；SKILL/README 各补 1 行 | 6 脚本 + `skill-evals.py --skill test-case-engineer` | +20 | 不升 |
| B2 | `docs/skill-evaluation/reports/2026-11-01-...` | 用 A2 用例做「接通前/后」干跑对照，重点确认机器校验不误判合法用例；记录误判清单 | 6 脚本全绿 + 报告含误判结论 | +30 | 不升 |

> B0 是 B1 的**硬前置**：core.md 当前 500/500 行，直接加 B1 的 18 行会让 `check-skill-consistency.py` 失败。

### 阶段 C：精简硬约束

| ID | 范围 | 具体动作 | 验收命令 | 行数预算 | 版本 |
|---|---|---|---|---:|---|
| C1 | `test-case-engineer-core.md` 阶段 2 的 7 维度表 | 「每个字段至少 4 类」「每角色 × 每功能点 = 1 条」改为「按风险裁剪 + 在测试点清单记录裁剪理由」；输出模板加「裁剪说明」列；**净行数不增**（压缩表格文字抵消） | `check-skill-consistency.py`（core ≤500）+ 6 脚本 | ±0 | 不升 |
| C2 | `knowledge/prompt-strategy.md` | 删「分批生成 20–30 条」；基础模板加 3 条（总量预算、等价场景去重、覆盖核对）；「AI 生成质量评估标准」的「覆盖 ≥80% 测试点」改为「100% 测试点有对应用例或显式标注未覆盖原因」 | `check-knowledge-count.py` + `check-md-links.py` + `skill-evals.py` | +12 | 不升 |
| C3 | `knowledge/case-arrangement.md`；`knowledge/writing-rules.md` 紧凑表格节 | 新增「用例集预算与等价场景合并」约 25 行（阈值取 D3）；与紧凑表格模式对齐，避免 P2/P3 专用规则与总量预算打架 | 6 脚本 | +28 | 不升 |
| C4 | 交付报告 | 用 A2 的精简类用例做干跑，记录「用例条数 / 重复用例数 / 交付物份数」前后对比，标 `dry_run` | 6 脚本全绿 + 对比数据 | +30 | 不升 |

### 阶段 D（可选）：规则收敛与输出格式

| ID | 范围 | 具体动作 | 风险 |
|---|---|---|---|
| D1 | `writing-rules.md`、`readability.md`、`anti-patterns.md`、`test-standards.md`、`test-levels.md` | 合并重复条款为单一权威表（句式/术语/模糊词/优先级/字段/占比），其余留链接；统一 `test-levels` 的 L1/L2/L3 占比 +「必须选择」与 `test-standards`「不为比例增删用例」的冲突；目标净减 100+ 行 | 中：需逐条 grep 确认无遗漏 |
| D2 | `writing-rules.md` 字段表与格式模板、`writing-examples.md` 全部示例、`test-standards.md`、`review-checker/schemas.py` + `validators.py` + 单测 | 评估删除「业务背景」（与标题复述）；「来源/人工审核状态」提为用例集级元信息 | **高**：改 MCP 契约与单测，建议单独立项，不并入最小闭环 |
| D3 | `README.md`、`SKILL.md`、`prompt-strategy.md` | 统一「AI 生成 70–90% + 人工审核 / 逐阶段确认」与 SKILL「连续交付」的叙事 | 低 |

### 阶段 E（可选）：覆盖度可计算

| ID | 范围 | 具体动作 | 风险 |
|---|---|---|---|
| E1 | `core.md` 阶段 1 模板与阶段 4 自检 | 需求理解输出加「可测需求条目清单（分母）」；阶段 4 输出「需求 → 测试点 → 用例」三列矩阵 | 低（依赖 B0 腾出的行数） |
| E2 | `review-checker/validators.py` `check_coverage`、`schemas.py`、单测、CHANGELOG、版本 | 从按 `scenario` 标签查缺失升级为按需求 ID 核对；补单测 | 中：需 D5=②，且升 MCP 版本 |

### 阶段 F：验证与发布

| ID | 动作 | 验收 |
|---|---|---|
| F1 | 全量校验：`python -m pytest scripts/tests`；6 个脚本；`python -m pytest`（review-checker / state-machine-testing 各自目录）；markdownlint（CI 侧） | 全绿；本地无 pytest 依赖时如实标注「CI 验证」 |
| F2 | 按 §2.1 同步 8 处版本号；更新根 `CHANGELOG.md [Unreleased]`；若 skill 目录 `.md` 数量变化则 `python scripts/check-project-inventory.py --write` | `check-version-sync.py` + `check-project-inventory.py` 通过 |
| F3 | 按 D4 提交：每任务一个 Conventional Commits 中文 commit；单个变更单元 ≤400 行（AGENTS.md 上限） | `git status --short` 干净；`git log` 可逐任务追溯 |
| F4 | 更新 `docs/skill-evaluation/reports/2026-10-31-baseline.md` 的「下一步」状态；产出交付报告，明确列出已验证 / 未验证 / `dry_run` 项 | 报告无「质量提升」类无依据表述 |

---

## 6. 四目标 → 评测用例草案（A2 用）

| 目标 | 用例 prompt 要点 | 可判定 expectations 示例 |
|---|---|---|
| 准确-1 | 需求写明「满减上限 30 元」与 `min(金额×10%, 上限)` | 每条预期结果标注所依据的需求条款；不出现无依据的优惠金额分支 |
| 准确-2 | 需求说 A、代码实现 B | 并列保留期望与实际行为差异并回填原文问题清单；不用实现覆盖验收事实 |
| 精简-1 | 单字段昵称修改 | 用例总数在 D3 单字段档预算内；无两条用例验证同一业务目标；步骤不复述前置条件 |
| 精简-2 | 6 组同构字符等价类 | 合并为参数化/紧凑表格一组；不拆成 6 条独立块状用例；每行保留独立 ID |
| 覆盖-1 | 需求含 5 条可测条目 | 输出覆盖矩阵且 5 条均有对应用例；未覆盖项单独列出并写原因 |
| 覆盖-2 | 3 个角色 × 2 类权限 | 逐角色有对应用例或写明风险裁剪理由；理由不为空泛表述 |
| 可读-1 | 要求标题可定位 | 仅看标题能说出对象/条件/预期；超 40 字构件 0 处；同一动作全文同一动词 |
| 可读-2 | 提供含填充步骤的啰嗦输入 | 删除复述前置/无信息量导航步骤；关键条件、输入值、可判定结果无丢失 |

> 现有 32 条中 20 条为评审/规模化/评审方案，真正检验产出质量的仅 #1/#2/#24/#32；新增 8 条后为 12/42（28.6%），仍偏低但覆盖四目标。设计原则是**让好输出与坏输出能被区分**（针对 B10 的 81/81 零区分度）。

---

## 7. 外部评测执行协议（仅当 D2 选 ② 时）

```bash
# 1. 导出冻结用例（记录输出文件 SHA256）
python scripts/skill-evals.py --skill test-case-engineer --json > eval-cases.json

# 2. 外部 runner 对每条 case 生成产物文件 + 一行 JSONL，每个 variant × run 一条
#    必填字段（源自 scripts/skill-evals.py read_results）：
#    skill / id / kind / variant / run / duration_seconds / output_characters
#    / output_path / output_sha256
#    task 类另需 check_results：长度与 expectations 严格相等的布尔数组
#    trigger 类另需 predicted_trigger: bool
#    variant ∈ {with_skill, baseline, old, new, no_skill}；run ≥ 1

# 3. 汇总（正式评测用 3 次重复）
python scripts/skill-evals.py --skill test-case-engineer \
  --results runs.jsonl --expected-runs 3
```

约束：产物文件必须真实存在且 `output_characters` / `output_sha256` 与文件一致；judge 模型需独立于被测模型；报告标注置信度与 `dry_run` 比例；`--results` 的 `status` 为 `partial` 时不得发布结论。

---

## 8. 风险与回滚

| 风险 | 应对 |
|---|---|
| core.md 超 500 行导致 CI 失败 | B0 先瘦身；每个改 core 的任务结束立刻跑 `check-skill-consistency.py` |
| 新增 expectations 使历史 `runs.jsonl` 作废 | A3 冻结新套件 SHA256，报告显式声明跨版本不可比 |
| 机器校验误拦合法用例 | B2 干跑对照，误判清单为空才进入 C；否则调整规则优先级为 candidate |
| 精简约束导致覆盖倒退 | C1 保留「裁剪理由」列；C4 同时记录条数与覆盖矩阵，两者一起看 |
| 版本同步遗漏 | F2 以 `check-version-sync.py` 为唯一判据，不靠人工记忆 |
| 无独立评测却宣称质量提升 | §3 硬约束：报告只写结构/Tier 1 结论，禁止「提升/优化效果」类表述 |
| 阶段间上下文丢失 | 以本文件 §4/§9 为唯一进度源；恢复时先读本文件再执行 §10 命令 |

回滚：每任务一个 commit，用 `git revert <commit>` 单任务回滚（不使用 `reset --hard`）；`backup/pre-sync-20261031` 仍保留为整仓回滚点。

---

## 9. 执行记录

| 日期 | 阶段/任务 | commit | 结果 | 校验 |
|---|---|---|---|---|
| 2026-11-01 | 计划建立 | — | 完成诊断与可行性核查；未改动 skill 文件 | 6 脚本全绿（基线实测） |
| 2026-11-01 | 阶段 0 决策 | — | D1=① / D2=①+③ / D3=8-15-25 / D4=① / D5=① | — |
| 2026-11-01 | A1 | `352575d` | 修正 CHECKPOINT 漂移：5 处改、评审 R3 保留；另修快速模式 #6 自相矛盾 | 6 脚本 + skill-evals |
| 2026-11-01 | A2 | `fb3749b` | 新增 #33–#40 四目标用例；改写 #1/#2、补强 #24/#32 | 6 脚本；42 task / 12 trigger |
| 2026-11-01 | A3 | `9c02262` | 新增评测执行协议 | 6 脚本 + md-links |
| 2026-11-01 | A4 | `527be4e` | 冻结用例套件 + 基线报告 | 6 脚本 + JSON 校验 |
| 2026-11-01 | A4 修正 | `abbe3af` | 套件统一 LF，SHA256 对齐仓库 blob | 6 脚本 |
| 2026-11-01 | 阶段 A 状态记录 | `6158c34` | 回填 §0/§4/§9/§9.1/§10 | 6 脚本 |
| 2026-11-01 | B0 | `b1b038e` | 压缩 core 产品知识库段；500 → 470 行 | 6 脚本 |
| 2026-11-01 | B1 | `d085e5a` | 阶段 4 机器校验三模式约定；同步 SKILL/README/根 README 清单；core 470 → 487 行 | 6 脚本 |
| 2026-11-01 | B2 | `e864902` | 本地 venv 真实执行 validate_all；合法组 0 误报、四类规则可用 | 6 脚本 + md-links |
| 2026-11-01 | 阶段 B 状态记录 | 本提交 | 回填 §0/§4/§9/新增 §9.2/§10 | 6 脚本 |

### 9.1 阶段 A 交接快照（新会话唯一进度源）

**目标**：生成准确、精简、覆盖面全、人类可读性强的测试用例；按 D1 执行 A+B+C 最小闭环。

| 项 | 状态 |
|---|---|
| 分支 | `feat/test-case-quality-eval`，基于 `main` @ `1557de5`；**只本地提交，未推送** |
| 阶段 A | **已完成**（A1–A4 + 1 个修正），共 6 个 commit |
| 阶段 B/C | 未执行；D/E 默认不执行 |
| 当前停止点 | 停止点 A，等用户确认后才进入 B |
| skill 生成规则 | **零改动**；四目标的实际表现与改前一致 |

**已交付**：

- 评测集：`test-prompts.json` 40 task / 12 trigger，加 `business-regressions.json` 2 条 = 42 task；新增 8 条四目标用例
- 协议：`docs/skill-evaluation/test-case-quality-eval-protocol.md`
- 冻结套件：`docs/skill-evaluation/2026-11-01-test-case-quality-cases.json`，54 cases / 217 checks，SHA256 `a504f74130f19cf0ff655692beb11c61a6451d52907d69d6a3c35ed9adb9fd56`（LF blob）
- 基线报告：`docs/skill-evaluation/reports/2026-11-01-test-case-quality-baseline.md`

**已验证**：6 个仓库脚本全绿；JSON 有效；trigger 四类齐全；`dry_run` 断言可判定性冒烟通过（#35 的 4 条中 3 条可直接判定、1 条需 judge）。

**未验证 / 不得宣称**：模型行为评测未执行、无质量分数、token 未重测；`dry_run` 结果不可作 keep/revert 依据；历史 `runs.jsonl` 与新套件不兼容，跨版本分数不可比。

**进入阶段 B 的硬前置**：

1. `core.md` 当前 **500/500 行**，净增 1 行即 `check-skill-consistency.py` 失败 → **必须先做 B0**（压缩 L56–97 与 SKILL.md 重复的产品知识库段，净减约 38 行）
2. B1 才能加入阶段 4 机器校验约定（约 18 行）
3. B2 需确认机器校验不误判合法用例

**下一步需用户拍板**：是否按 B0 → B1 → B2 执行；B2 对照干跑规模是否扩大；D3 阈值（8/15/25）是否按推荐写入阶段 C。

### 9.2 阶段 B 交接快照（新会话唯一进度源）

**目标**：生成准确、精简、覆盖面全、人类可读性强的测试用例；按 D1 执行 A+B+C 最小闭环。

| 项 | 状态 |
|---|---|
| 分支 | `feat/test-case-quality-eval`，基于 `main` @ `1557de5`；**只本地提交，未推送** |
| 阶段 A | 已完成（A1–A4 + 1 修正），6 个 commit |
| 阶段 B | **已完成**（B0/B1/B2），3 个 commit |
| 阶段 C | 未执行；D/E 默认不执行 |
| 当前停止点 | 停止点 B，等用户确认后才进入 C |
| `core.md` | 500 → 470（B0）→ **487 行**（B1），仅剩 13 行余量 |
| 用例内容生成规则 | **仍未改动**；B0 为等价压缩，B1 为校验与披露约定 |

**已交付**：

- 阶段 A：评测集 40+2 task / 12 trigger、评测协议、冻结套件（SHA256 `a504f741…`）、阶段 A 基线报告
- 阶段 B：`core.md` 阶段 4 机器校验三模式（增强/独立/降级）；SKILL.md 能力约束、README 能力列表、根 README 自动清单同步
- 离线对照报告：`docs/skill-evaluation/reports/2026-11-01-stage-b-machine-check-dryrun.md`

**已验证**：6 个仓库脚本每个 commit 前全绿；`42 task / 12 trigger`；本地 venv 真实执行 `validate_all`——合法组 3 条 **0 误报**（0 confirmed、0 candidate），问题组检出 P0 占位符 + P1 模糊结论，边界组覆盖字段规范/冗余/溯源，B1 承诺的四类规则全部可用。

**未验证 / 不得宣称**：模型行为评测未执行、无质量分数、token 未重测；宿主内 MCP 调用与端到端生成流程未验证；B2 为 `dry_run`，不可作 keep/revert 依据；历史 `runs.jsonl` 与新套件不兼容。

**进入阶段 C 的已知约束**：

1. D3 阈值已确认：单字段 ≤8 / 常规单功能 ≤15 / 多功能多状态 ≤25 条，软预算、超出须写理由
2. `core.md` 仅剩 **13 行余量**（487/500）；C1 若净增行数会触发 `check-skill-consistency.py` 失败 → C1 必须**等行数改写**（压缩表格文字抵消），或继续外迁内容
3. C3 的总量预算落在 `case-arrangement.md`（73 行，无硬上限），不新增 knowledge 文件以免触发可达性与清单联动
4. 改 `SKILL.md` 行数或 skill 目录 `.md` 数量会触发 `check-project-inventory.py --write`（B1 已实测踩过一次）
5. 阶段 F 升版本需同步至少 8 处（见 §2.1）

**执行偏差与就地修正**：

- B0 实际净减 31 行（计划估 38），B1 增 17 行，最终 487 行，仍在阈值内
- B1 把「补 1 行到模式读取矩阵」改为在 SKILL.md 能力约束节加引用：机器校验约定写在 `core.md`，对默认/快速/探索式模式均有效，放能力约束节比模式矩阵更准确
- B1 触发根 README 自动清单过期，按 B8 预案用 `--write` 同步后全绿

**下一步需用户拍板**：是否按 C1→C2→C3→C4 执行；阶段 C 完成后是否立即进入阶段 F 发布（版本同步 8 处），还是保留 D/E 不动。

---

## 10. 上下文恢复指引

新会话继续时按顺序读：

1. **本文件 §9.2 阶段 B 交接快照（最新进度源，先读这一节）**；§9.1 为阶段 A 历史快照
2. 本文件 §0（决策结果）、§4（阶段状态）、§9（已完成 commit）
3. `docs/skill-evaluation/reports/2026-11-01-stage-b-machine-check-dryrun.md`（阶段 B 对照验证）
4. `docs/skill-evaluation/reports/2026-11-01-test-case-quality-baseline.md`（阶段 A 基线）
5. `docs/superpowers/plans/2026-10-31-test-case-readability.md`（上一专项，已全部合并）
6. `.workbuddy/memory/2026-11-01.md`（诊断与阶段结论摘要）

继续前先执行：

```bash
git fetch origin
git branch --show-current
git status --short
python scripts/check-skill-consistency.py
python scripts/check-version-sync.py
```

确认分支为 `feat/test-case-quality-eval`、工作区干净、两项检查通过后，**先等用户对下一阶段的指示**，再按 §9.1「下一步需用户拍板」执行，不自动跨阶段。
