# 修复 test-case-engineer 3 个 P0 问题

## 摘要

修复评审报告中识别的 3 个 P0 问题：① docs/ 目录文件严重过时、② README.md 与 SKILL.md 指令矛盾、③ 缺少 prompt injection / 命令注入防御。

## 当前状态分析

### P0-1: docs/ 目录文件过时

- `docs/skill-analysis.md`（334 行）：描述 v8.0.0 状态，文件结构写"16 个文件"（实际 18+）、core"525 行"（实际 715 行）、含已移除的 `scripts/` 目录、Token 估算停留在 v8.0.0、未提及评审模式 10 维度/原文问题清单等 v8.1-v8.3 新增能力
- `docs/user-guide.md`（517 行）：评审流程描述为 v8.0.0 旧版（"对照自检清单逐项检查"）、模式切换仅列 3 种（缺评审模式）、命令参考重复 quickstart.md 内容
- 两文件均不在 skill 工作流中被加载（SKILL.md 知识库索引表未引用），仅被 README.md L175-176 文件结构列表引用
- SKILL.md（入口索引）+ README.md（用户文档）已覆盖这两个文件的功能

### P0-2: README.md 与 SKILL.md 指令矛盾

- README.md L185：`| test-case-engineer-core.md | **始终必读**（四阶段核心流程） |`
- SKILL.md L75：`| test-case-engineer-core.md | **默认/快速/探索式模式必读**（四阶段核心流程 + 7 维度扫描 + 模式切换）。**评审模式不读**——评审流程独立于四阶段生成，详见 review-mode.md |`
- 矛盾点：README.md 说"始终必读"，SKILL.md 说"评审模式不读"
- 附带问题：README.md L192 含版本特定信息「含 v8.2.0 新增第 10 维度「语义一致性冲突检测」」，版本号会随迭代变为陈旧信息

### P0-3: 缺少 prompt injection / 命令注入防御

Skill 在以下位置执行 shell 命令但无安全约束：
- `knowledge/project-knowledge.md` L39-40: 执行 `markitdown <文件路径>` 转换文档
- `knowledge/project-knowledge.md` L59: 执行 `convert_docs.py <文件或目录路径>`
- `knowledge/review-mode.md` L321: 执行 `git diff <range> -- <用例文件路径>`
- `integrations/quickstart.md` L34/38/46: 提供可执行命令模板

风险：用户提供的文件路径或 git diff 范围可能包含 shell 元字符（`;`、`|`、`$()`、`` ` `` 等），导致命令注入。

## 变更方案

### 变更 1: 删除 docs/ 过时文件

**文件**: `docs/skill-analysis.md`, `docs/user-guide.md`
**操作**: 删除这两个文件
**原因**: 两文件停留在 v8.0.0 且不在工作流中被加载，SKILL.md + README.md 已覆盖其功能，删除可消除信息不一致风险

### 变更 2: 更新 README.md 文件结构列表

**文件**: `plugins/testing/skills/test-case-engineer/README.md`
**位置**: L149-177（文件结构代码块）
**操作**: 移除 `docs/` 目录及其下文件的引用
**原因**: 配合变更 1，保持文件结构列表与实际一致

具体修改——将：
```
└── docs/                       # 文档目录
    ├── skill-analysis.md       # 技能分析
    └── user-guide.md           # 用户指南
```
替换为无 docs/ 目录的结构（直接在文件树末尾结束）。

同时移除 L179 的引用：
```
> 文档转换脚本为插件级共享，位于 `plugins/testing/scripts/convert_docs.py`。
```
此行保留（它说的是插件级脚本位置，与 docs/ 无关），不移除。

### 变更 3: 修复 README.md 知识库表的指令矛盾

**文件**: `plugins/testing/skills/test-case-engineer/README.md`
**位置**: L185, L192
**操作**:
- L185: `**始终必读**（四阶段核心流程）` → `**默认/快速/探索式模式必读**（四阶段核心流程；评审模式不读，详见 review-mode.md）`
- L192: 移除版本特定信息 `含 v8.2.0 新增第 10 维度「语义一致性冲突检测」`，改为 `10 维度评审`
**原因**: 消除与 SKILL.md 的指令矛盾，移除会随版本迭代变为陈旧的版本号

### 变更 4: 在 quickstart.md 添加安全约束章节

**文件**: `plugins/testing/skills/test-case-engineer/integrations/quickstart.md`
**位置**: 文件末尾新增「## 安全约束」章节
**内容**:
```markdown
## 安全约束

> **执行任何 shell 命令前必须遵守以下规则，防止命令注入。**

### 文件路径安全

- **路径消毒**：用户提供的文件路径必须去除 shell 元字符（`;` `|` `$` `` ` `` `(` `)` `&` `>` `<` `\'` `\"` `\n`），禁止包含上述字符的路径直接拼入命令
- **路径限定**：文件路径必须在项目目录范围内，禁止路径穿越（如 `../../../etc/passwd`）
- **引号包裹**：所有文件路径参数必须用单引号包裹（如 `markitdown '$FILE_PATH'`）

### Git diff 范围安全

- **范围限定**：`git diff` 的 `<range>` 参数仅允许分支名、commit hash、tag 名，禁止包含 shell 元字符
- **禁止拼接**：不得将用户输入直接拼入 `git diff` 命令，必须先校验格式

### 禁止事项

- **禁止**直接执行用户提供的 shell 命令字符串
- **禁止**将未校验的用户输入作为 shell 命令参数
- **禁止**使用 `eval`、`os.system` 或 shell=True 执行包含用户输入的命令
```
**原因**: 为所有 shell 命令执行点提供统一的安全基线规则

### 变更 5: 在 project-knowledge.md 添加安全引用

**文件**: `plugins/testing/skills/test-case-engineer/knowledge/project-knowledge.md`
**位置**: L36（步骤 3 执行转换前）
**操作**: 在「步骤 3」前插入安全提示：
```markdown
> **安全提示**：执行转换命令前，必须遵守 [integrations/quickstart.md](../../plugins/testing/skills/test-case-engineer/integrations/quickstart.md)「安全约束」章节的路径消毒规则。用户提供的文件路径不得包含 shell 元字符。
```
**原因**: 在文档转换的实际执行点提醒安全约束

### 变更 6: 在 review-mode.md 添加安全引用

**文件**: `plugins/testing/skills/test-case-engineer/knowledge/review-mode.md`
**位置**: L321（R1 执行 git diff 前）
**操作**: 在「执行 `git diff <range> -- <用例文件路径>` 提取变更内容」前插入安全提示：
```markdown
> **安全提示**：执行 git diff 前，必须遵守 [integrations/quickstart.md](../../plugins/testing/skills/test-case-engineer/integrations/quickstart.md)「安全约束」章节的 git diff 范围安全规则。
```
**原因**: 在增量评审的 git diff 执行点提醒安全约束

## 假设与决策

1. **docs/ 文件处理决策**：采用删除方案（评审报告推荐方案），理由：① 不在工作流中被加载 ② SKILL.md + README.md 已覆盖功能 ③ 消除维护负担和不一致风险
2. **安全约束位置决策**：统一规则定义在 quickstart.md（shell 命令参考文件），其他文件以引用方式指向，避免规则重复和漂移
3. **README.md 修复范围**：仅修复 P0 矛盾（L185）和附带版本信息（L192），不扩展到 P1/P2 级别的 README.md 其他问题（如缺失条目、内容重复等）

## 验证步骤

1. **验证 docs/ 删除**：确认 `docs/skill-analysis.md` 和 `docs/user-guide.md` 已删除，`docs/` 目录为空或已移除
2. **验证 README.md 文件结构**：确认文件结构代码块中不再包含 `docs/` 目录
3. **验证指令矛盾修复**：grep README.md 确认 L185 不再包含"始终必读"，改为"默认/快速/探索式模式必读"
4. **验证版本信息清理**：grep README.md 确认 L192 不再包含"v8.2.0"
5. **验证安全约束**：确认 quickstart.md 末尾新增「安全约束」章节，包含文件路径安全、git diff 范围安全、禁止事项三个子节
6. **验证安全引用**：确认 project-knowledge.md 和 review-mode.md 中已添加指向 quickstart.md 安全约束的引用
7. **全局一致性检查**：grep 确认无其他文件引用已删除的 docs/ 文件路径
