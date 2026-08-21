# 用例相关 Skill 一致性修复最终报告

> **报告日期**：2026-08-21
> **基线**：main @ `7692359`（PR #74 合并后）
> **前置文档**：[用例相关 Skill 家族全面审查报告](./usecase-skills-family-review-2026-08-21.md)、[一致性修复计划](../../superpowers/plans/2026-08-21-usecase-skills-consistency-fix.md)
> **交付 PR**：#73（批次 1-3 文档修复）、#74（批次 4 MCP v0.2.0）

## 一、执行摘要

审查报告识别的 4 个批次共 13 项一致性问题**全部修复并通过验收**，其中 1 项（批次 4）从"待定"升级为完整的代码工程交付。合并后 main 上重跑全部验证：**52 项 MCP 测试全绿、4 个一致性脚本全过、4 类残留扫描零命中**，与原始分析预期一致，未发现新问题引入。

修复期间另发现并修复 2 处存量残留（根 README 版本号 v8.3.0 → v8.6.0、change-impact-analyzer 定位描述），属审查漏网项，已在 PR #74 中一并处理。

## 二、交付物对照

| PR | 合并 commit | 批次 | 主题 | 规模 |
|---|---|---|---|---|
| #73 | `744cf72` | 1-3 | 文档一致性修复（strategy / case / bundle） | ~130 行 |
| #74 | `7692359` | 4 | state-machine MCP Server v0.2.0 端到端联调 | 代码工程 |

分支 `fix/usecase-skills-consistency` 与 `feat/state-machine-mcp-v020` 均已合并删除，main 保持线性历史。

## 三、问题-修复对照（逐项核销）

### 批次 1：test-strategy-engineer 数值口径统一

| # | 原问题 | 修复方式 | 最终验证 |
|---|---|---|---|
| 1-1 | 准出执行率 100% vs 权威源 ≥95%（含分档） | checklist 对齐 ≥95% 并注明分档出处 | grep 无"执行率 100%"残留 ✓ |
| 1-2 | 单元覆盖率错列为准出项（权威源为准入项） | 从准出 checklist 移除，补准入项脚注 | checklist 与 entry-exit-criteria.md §2 逐项对齐 ✓ |
| 1-3 | 分层比例 "7:2:1" 点值 vs 区间 | 改区间表述，以 test-pyramid.md 为准 | grep 无 "7:2:1" 残留 ✓ |
| 1-4 | 分档维度错位（生命周期选形状 vs 技术栈定比例） | 双向声明正交组合关系 | SKILL.md 阶段 3 与 test-pyramid.md §3 互引闭合 ✓ |
| 1-5 | risk-matrix / test-pyramid 整表复制（双源漂移风险） | 复制表改"精确引用 + 链接" | check-md-links 无断链 ✓ |

### 批次 2：test-case-engineer 映射与同步

| # | 原问题 | 修复方式 | 最终验证 |
|---|---|---|---|
| 2-1 | strategy 三层 → case 五层无映射约定 | test-levels.md 新增映射表（接口层拆分去向明确） | 映射表覆盖 strategy 全部三层 ✓ |
| 2-2 | 内部五层与 writing-rules 四层关系未声明 | 声明为"用例编排分组视角" + 优先级规则 | 同文件内闭环 ✓ |
| 2-3 | test-prompts.json 版本 8.5.0 滞后 | 同步至 8.6.0 | check-version-sync 通过 ✓ |
| 2-4 | bug-patterns.md 残留 bug-analyzer 跨 skill 引用 | 改为 case-engineer 自身视角表述 | grep 无 bug-analyzer 残留 ✓ |

### 批次 3：testing-bundle 术语与规则补全

| # | 原问题 | 修复方式 | 最终验证 |
|---|---|---|---|
| 3-1 | "5-way" 术语过时（实际 6 路） | 全部统一 "6-way（5 核心 + 1 协同）"，架构图补节点 | grep 无残留（CHANGELOG 历史保留）✓ |
| 3-2 | change-impact-analyzer 定位三处措辞不一 | 统一"链 6 协同使用，亦可单独使用" | 三处口径一致 ✓ |
| 3-3 | CHECKPOINT 与"直接交付"冲突无裁定规则 | 新增裁定规则（失败模式表 + 约束规则 5 双覆盖） | 双覆盖确认 ✓ |
| 3-4 | "测试计划"路由歧义 | 新增消解规则（项目级→strategy / 单功能→case / 不定→追问） | 失败模式表收录 ✓ |

### 批次 4：state-machine MCP v0.2.0（从"待定"升级交付）

| # | 原问题 | 修复方式 | 最终验证 |
|---|---|---|---|
| 4-1 | 协议层未端到端联调 | stdio + HTTP 双传输联调验证 | 9 项集成测试全绿 ✓ |
| 4-2 | build_state_machine 占位（返回空状态机） | 确定性行业模板加载（4 模板 schema 合规） | 单元测试覆盖模板加载/未知模板/纯文本路径 ✓ |
| 4-3 | 集成测试 pytest.mark.skip | 全部解除并实跑 | 52 passed（43 单元 + 9 集成）✓ |
| 4-4 | MCP 状态声明全仓口径不一 | skill/bundle/plugin/根文档四层统一为"v0.2.0，协议层已联调验证" | 残留扫描零命中 ✓ |

附带工程修复：依赖锁定 `mcp<2.0.0`（规避 2.0 移除 FastMCP）、新增 pyyaml + pytest-asyncio、SKILL.md 运行模式表更新为三模式（增强/独立/降级）。

## 四、合并后 main 最终验证（2026-08-21 实跑）

| 验证项 | 命令 / 方式 | 结果 |
|---|---|---|
| MCP 全量测试 | `pytest tests/`（state-machine-testing） | **52 passed**（6.29s） |
| 链接一致性 | `python scripts/check-md-links.py` | 通过，无断链 |
| 版本一致性 | `python scripts/check-version-sync.py` | 通过，版本全同步 |
| 知识引用完整性 | `python scripts/check-knowledge-count.py` | 通过 |
| Skill 一致性不变量 | `python scripts/check-skill-consistency.py` | 通过 |
| 残留扫描 ① | `grep -rn "5-way"`（排除 CHANGELOG） | 零命中 |
| 残留扫描 ② | `grep -rn "7:2:1"` | 零命中 |
| 残留扫描 ③ | `grep bug-analyzer`（bug-patterns.md） | 零命中 |
| 残留扫描 ④ | `grep 执行率 100%`（strategy skill） | 零命中 |

## 五、与原始分析的偏差说明

1. **批次 4 原计划"待定"**：用户确认后升级为完整交付，范围超出计划的纯文档修复，进入代码工程（ builders.py 实现 + 协议联调 + 测试解除 skip）。结果优于计划预期。
2. **追加发现 2 处存量残留**（根 README 版本号与定位描述）：审查阶段未覆盖根目录文档，属工具盲区，已修复。此经验提示后续审查应将根 README/CLAUDE.md/installation.md 纳入扫描范围（check-version-sync.py 已可拦截版本类问题）。
3. **MCP 状态口径演变**：批次 3 时统一为"尚未端到端联调验证"，批次 4 完成后升级为"已联调验证可用"——两批次间口径变化为计划内递进，非不一致。

## 六、遗留事项（计划内暂缓 + 审查发现未修）

**计划内暂缓**（P0 修完前不扩面，建议列入下轮迭代）：

| 事项 | 优先级 | 来源 |
|---|---|---|
| 模糊词清单统一（writing-rules 15 词 + test-standards 50 词取并集） | P2 | 审查报告 4.1 缺点 #2 |
| ID 生成规则去重（writing-rules.md 与 review-mode.md 近逐字重复） | P2 | 审查报告 4.1 缺点 #2 |
| 产品知识库真实数据沉淀（products/ 仅 1 个 example 模板） | P2 | 审查报告 4.1 缺点 #6 |

**审查发现、本次范围外**（结构性/设计层，需单独评估）：

| 事项 | 来源 |
|---|---|
| token 成本优化（SKILL.md+core.md 首轮 ≈640 行） | 审查报告 4.1 缺点 #1 |
| C5（禁止转换完整性）自动判定 | 审查报告 4.2 缺点 #3 |
| MCP 侧 concurrency/access_control 关键词判定粗糙 | 审查报告 4.2 缺点 #4 |
| expected_target_state 混用"待确认"与真实状态名 | 审查报告 4.2 缺点 #5 |
| 评审→修订闭环跨模式切换简化 | 审查报告 4.1 缺点 #7 |

## 七、结论

- **计划符合度**：13/13 项问题修复，验收标准全部达成，无跳批、无降级。
- **无新问题引入**：合并后全量验证（测试 + 脚本 + 残留扫描）在 main 上重跑通过，与批次验收时结果一致。
- **体系状态**：4 个用例相关 skill 的数值口径、分层映射、版本同步、术语统一达到全仓一致；state-machine skill 的核心卖点（MCP 增强模式）从"不可达"转为"已联调验证可用"，审查报告指出的最大能力缺口闭合。
