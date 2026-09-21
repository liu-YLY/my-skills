# 2026-09-21 Skill 迭代执行计划

## 目标

在不改变 8 个 Skill 核心用途的前提下，先修复可确认的安装与文档缺陷，再建立可重复的模型行为评测和触发评测，最后用成对评估验证入口瘦身是否带来真实收益。

## 基线

- 代码基线：`origin/main@9d31eb8`
- 功能测试：review-checker 101、state-machine-testing 68、wechat-formatter 54，共 223 项通过
- 仓库工具：5 项通过；本机无 PowerShell，3 项安装器测试跳过
- 静态检查：版本、知识引用、相对链接、Skill 一致性、项目清单通过
- 已知评测边界：`scripts/skill-evals.py` 只验证样本输入，不执行模型行为评测

## 范围与非目标

### 本轮范围

1. 修复 README 和安装文档中的确定性路径与完整性问题。
2. 为安装文档关键命令增加自动回归检查。
3. 统一 8 个 Skill 的触发评测结构，覆盖正例、负例和相邻 Skill 冲突。
4. 增加模型评测运行结果的数据契约和离线汇总能力。
5. 选择入口最重的 Skill 做一次渐进式瘦身实验，并执行改前/改后成对评估。

### 非目标

- 不改变 Skill 的业务职责或路由边界。
- 不引入新的第三方运行依赖。
- 不在没有真实评测证据时批量重写所有 SKILL.md。
- 不自动推送、创建 PR 或合并到 main。

## 执行阶段

### 阶段 1：安装链路修复

**改动**

- README 离线安装示例必须安装完整 7 个 testing Skills，不能只复制路由 Skill。
- 修正 `convert_docs.py` 依赖安装路径。
- 增加文档命令与仓库目录一致性的回归测试。

**验收**

- `python -m pytest scripts/tests`
- `python scripts/check-md-links.py`
- `python scripts/check-project-inventory.py`

### 阶段 2：评测数据契约

**改动**

- 保留 `skill-evals.py` 的输入校验职责。
- 定义模型运行结果格式：skill、case、variant、run、耗时、判定项、原始输出位置。
- 增加离线汇总器，计算完成率、判定项通过率、触发 precision/recall、耗时和输出长度。
- 无模型输出时必须报告“未评测”，不得把样本存在误报为行为通过。

**验收**

- 汇总器单元测试覆盖完整数据、缺失数据、重复 run 和错误 case ID。
- 历史评测数据可读取但不被静默改写。

### 阶段 3：触发与路由评测补齐

**改动**

- 每个 Skill 至少具备：典型正例、明确负例、near-miss、相邻 Skill 冲突样本。
- testing-bundle 额外覆盖单意图直达、混合意图链和多链冲突。
- 检查器验证每个 Skill 的最低触发覆盖类型，不规定固定业务答案。

**验收**

- 8 个 Skill 均有可机器读取的触发样本。
- 所有触发样本有布尔标签及场景分类。

### 阶段 4：入口瘦身实验

**候选顺序**

1. change-impact-analyzer
2. bug-analyzer
3. testing-bundle

**方法**

- 每轮只调整一个 Skill 的一个主要维度。
- 将阶段细则下沉到 workflow/knowledge，入口只保留触发、边界、阶段门禁和资源索引。
- 改前/改后使用相同 prompt，由独立评估者进行奇数次 paired comparison。
- 多数评估认为改后不差于改前才保留；否则使用可追溯回滚。

**验收**

- 相对链接、资源可达性和安装完整性检查通过。
- 入口字符数和实测耗时记录完整，但不以字符数单独判定成功。
- 典型任务质量无回退，且至少一项上下文或耗时指标改善。

### 阶段 5：全量回归与交付

**验收命令**

```bash
python -m pytest scripts/tests
python scripts/skill-evals.py
python scripts/check-project-inventory.py
python scripts/check-version-sync.py
python scripts/check-knowledge-count.py
python scripts/check-md-links.py
python scripts/check-skill-consistency.py
```

MCP 与微信排版测试按各自目录独立执行，避免 pytest 同名模块收集冲突。

## 风险控制

| 风险 | 控制措施 |
|------|----------|
| 评测分数受 judge 噪声影响 | 绝对分仅用于排序，保留/回滚使用同 judge 成对比较与多数决 |
| 为降低上下文误删业务约束 | 每次只改一个 Skill，并复用现有任务、降级和对抗样本 |
| 文档再次漂移 | 将关键路径和完整安装约束写入仓库测试 |
| 环境缺失导致假通过 | 跳过项必须显式报告；PowerShell、真实宿主和真实发布分别记录边界 |
| 计划无限扩张 | 完成阶段 1 至 3 后重新评估，只选择一个 Skill 进入首轮瘦身实验 |

## 提交拆分

1. `fix(docs): 修复 Skill 安装路径与完整性`
2. `test(evals): 增加模型评测结果契约与汇总测试`
3. `test(skills): 补齐触发与路由评测样本`
4. `refactor(<skill>): 下沉流程细则并压缩入口上下文`

每个提交只包含一个阶段的可验证成果，不混入无关格式化。

## 执行结果（2026-09-21）

### 已完成

- 阶段 1：修复完整安装路径与依赖路径，并增加安装文档回归检查。
- 阶段 2：增加模型运行结果契约、结果校验与离线汇总；无模型输出时只报告输入校验，不宣称行为通过。
- 阶段 3：8 个 Skill 均补齐 positive / negative / near-miss / skill-conflict 触发样本。
- 阶段 4：在首轮候选验证通过后，经用户连续授权，将相同方法扩展到全部 8 个 Skill；每个 Skill 单独评测、独立成对判断并分批提交。
- 阶段 5：完成仓库、两个 testing MCP Server 与 wechat-formatter 全量回归。

### 主要修复与优化

| Skill | 已确认问题 | 处理结果 |
|-------|------------|----------|
| change-impact-analyzer | 干净工作区会漏掉 feature 分支中已提交但未合并的改动；入口重复阶段细则 | 增加 `default...HEAD` 分支差异模式；下沉细则并保留证据门禁 |
| bug-analyzer | 入口与知识文件重复，报告边界分散 | 下沉报告细则，保留根因证据、未知项和修复验证契约 |
| testing-bundle | MCP 依赖版本漂移；入口重复子 Skill 细节 | 同步依赖版本；入口收敛为路由与混合意图契约 |
| state-machine-test-engineer | 文档硬编码测试总数易漂移；入口重复 core 流程 | 改为从 core 校验协作契约；下沉流程并保留状态场景输出契约 |
| wechat-formatter | 入口一次性加载过多资源 | 改为按阶段加载，并保留内容真实性、排版与输出边界 |
| test-strategy-engineer | 缺失风险维度仍可能被补分；固定优先级配额会扭曲风险 | 缺失项标待补且不计算正式总分；取消固定配额；下沉阶段细则 |
| performance-test-engineer | 评测要求固定排查顺序；缺 TPS 时可能误判饱和 | 改为证据优先和可证伪假设；缺 TPS 禁止推断吞吐拐点；入口由 242 行降至 118 行 |
| test-case-engineer | 已有修订授权仍可能重复确认；固定优先级占比与权威规则冲突 | 按既有授权定向修订并强制复审；优先级逐条按业务风险判断，不设固定占比 |

### 本地提交

所有提交位于本地分支 `feat/skill-iteration-plan`，未推送远程：

1. `efc18ec` 修复 Skill 安装路径与完整性
2. `11ece21` 增加模型评测结果契约与汇总
3. `75006bd` 补齐触发与路由评测样本
4. `41ef246`、`b6f3e0f` 修复并精简 change-impact-analyzer
5. `e9ada16` 精简 bug-analyzer
6. `525debd`、`ff79739` 修复并精简 testing-bundle
7. `6e9a94e`、`5896664`、`7decf72` 修复并精简 state-machine-test-engineer
8. `173469d` 精简 wechat-formatter
9. `1c3af45`、`1e70988` 修复并精简 test-strategy-engineer
10. `ad015ff`、`d1bf9b7` 修复并精简 performance-test-engineer
11. `6fb0d96` 修复 test-case-engineer 的授权和优先级契约

### 验证证据

- 仓库测试：18 passed，3 skipped；跳过原因为本机无 PowerShell，CI 负责安装器 PowerShell 冒烟测试。
- review-checker：101 passed。
- state-machine-testing：68 passed。
- wechat-formatter：54 passed。
- 项目清单、版本同步、知识引用、Markdown 相对链接、Skill 一致性和 `git diff --check` 全部通过。
- 结构优化均执行相同输入的改前/改后比较；最近的 performance-test-engineer 与 test-case-engineer 均获得 3:0 clear-margin 选择。

### 验证边界

- `scripts/skill-evals.py` 已验证评测输入与结果契约，但仓库未保存可复现的外部模型批量运行结果；不能把样本校验等同于线上模型行为通过。
- 本机未执行 PowerShell 安装器测试。
- 未在 Claude/Cursor/Codex 等真实宿主中重新安装全部插件并逐一触发；静态路由和配套单测通过不等于所有宿主行为一致。
- 未执行远程推送、PR、合并或发布。
