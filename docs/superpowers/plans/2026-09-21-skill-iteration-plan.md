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
