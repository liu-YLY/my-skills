# Diff 模式与只读采集

> **何时阅读**：阶段 1「收集输入」时加载本文件，确认 diff 范围并执行采集。
> **覆盖范围**：七种 diff 模式 / 片段与改动点 / 自动推断规则 / 只读采集字段 / 风险分组 / 输入输出示例。

## 1. 七种 Diff 模式

| 模式 | 触发条件 | Git 命令 |
|------|---------|---------|
| 当前改动 | 用户说"当前改动"/"本地改动"/未指定范围 | 工作区非空：`git diff --no-ext-diff --no-textconv HEAD`；工作区干净且 feature 分支领先默认分支：`git diff --no-ext-diff --no-textconv <default>...HEAD` |
| 暂存区改动 | 用户说"已暂存"/"staged" | `git diff --no-ext-diff --no-textconv --cached` |
| 分支对比 | 用户指定了两个分支名 | `git diff --no-ext-diff --no-textconv <base>...<head>` |
| 单个 Commit | 用户指定了单个 commit hash | `git diff --no-ext-diff --no-textconv <commit>~1..<commit>` |
| Commit 范围 | 用户指定了 commit 区间 | `git diff --no-ext-diff --no-textconv <commit1>..<commit2>` |
| Revision Range | 用户给出 `A..B` / `A...B` 形式 | 原样传入 `git diff --no-ext-diff --no-textconv <range>` |
| PR Diff / 外部 Patch | 用户粘贴 patch 或提供 PR diff 文件路径 | 不执行 git，直接解析 patch 内容 |

## 2. 自动推断规则

- 若用户未指定范围，先检查 `git status --short`；工作区非空时使用「工作区改动」模式
- 若工作区干净，检查当前分支及默认分支：feature 分支存在未合并提交时，使用默认分支的远端跟踪引用（优先 `origin/main` / `origin/master`）与 `HEAD` 做三点对比
- 若工作区干净且当前位于默认分支，才输出「无变更」；不得忽略 feature 分支上已提交但未合并的改动
- 若用户只指定 head 分支，优先使用 PR 目标或已确认基线，其次仓库默认分支；记录解析后的 ref/SHA，不硬编码 main。默认分支无法确认时询问。
- 若用户提供了 commit hash，使用该 commit 与前一个 commit 的 diff
- 若用户粘贴了 `diff --git ...` 开头的内容，识别为外部 Patch，跳过 git 命令
- 有前后片段或具体改动点时直接解析材料，标明源码是否已核对；不要求用户必须导出 patch。
- 「当前改动」工作区非空时只包含未提交的已跟踪改动，披露是否排除了已提交分支差异；明确要求整个功能含本地改动时，解析 merge-base 后对工作树做比较。未跟踪文件单列，未读内容不能认定覆盖或无影响。
- 单提交为根提交时使用 `git show --root --format= --no-ext-diff --no-textconv <commit>`；合并提交说明父节点比较口径，不默默漏掉合并改动。

## 3. 模式选择决策树

基于「变更范围 / 是否已提交 / 是否跨分支」三维度判定：

```
用户输入
  │
  ├─ 粘贴了 diff --git 文本 / 提供 patch 文件路径
  │    → 模式 7：PR Diff / 外部 Patch（不执行 git）
  │
  ├─ 给出 commit hash
  │    ├─ 单个 hash → 模式 4：单个 Commit（hash~1..hash）
  │    └─ hash1..hash2 区间 → 模式 5：Commit 范围
  │
  ├─ 给出 A..B 或 A...B 形式
  │    → 模式 6：Revision Range（原样传入）
  │
  ├─ 给出分支名
  │    ├─ 单个分支名 → 模式 3：分支对比（已确认基线...head）
  │    └─ 两个分支名 → 模式 3：分支对比（base...head）
  │
  ├─ 说"已暂存"/"staged"
  │    → 模式 2：暂存区改动（git diff --no-ext-diff --no-textconv --cached）
  │
  ├─ 未指定范围 / 说"当前改动"/"本地改动"
  │    ├─ 工作区非空 → 模式 1：工作区改动（git diff --no-ext-diff --no-textconv HEAD）
  │    ├─ 工作区干净 + feature 分支领先默认分支 → 模式 3：分支对比（<default>...HEAD）
  │    └─ 工作区干净 + 默认分支 → 输出「无变更」
  │
  └─ 上述均不匹配
       → 主动追问用户，不擅自选择
```

## 4. 只读采集

先获取完整变更目录、状态与版本，再定向读取相关调用方、接口、数据模型和测试文件。以下是原生命令采集结果的建议字段，当前 skill 不附带采集脚本，不宣称脚本已经执行。

### 4.1 产出结构（字段语义同 git 原生输出）

```json
{
  "source": "working-tree | staged | commit | range | patch",
  "base_ref": null,
  "base_sha": null,
  "head_sha": null,
  "material_version": null,
  "status_short": [],
  "name_status": [],
  "numstat": [],
  "untracked_files": [],
  "diff_truncated": false,
  "analyzed_files": [],
  "unread_files": [],
  "excluded_files": [],
  "unified_diff": ""
}
```

| 字段 | 用途 |
|------|------|
| `status_short` | 当前仓库有哪些文件发生变化 |
| `name_status` | 文件是新增/修改/删除/重命名 |
| `numstat` | 每个文件新增/删除了多少行 |
| `untracked_files` | 有哪些未被 Git 跟踪的文件 |
| `unified_diff` | 具体的代码差异 |
| `diff_truncated` | Diff 是否因过大被截断 |
| `base_ref/base_sha/head_sha/material_version` | 比较口径及来源版本；不能虚构不可得的 SHA |
| `analyzed_files/unread_files/excluded_files` | 区分已读、未读和有理由排除的范围 |

### 4.2 采集安全策略（必须遵守）

- 整个采集过程保持**只读**，不修改代码、不运行测试、不执行 git textconv
- **不读取**未跟踪文件的具体内容（仅记录文件名）
- **不对**二进制文件进行文本转换
- Diff 超过指定大小时进行**截断**，并在报告中标注「部分文件未分析」
- 构建产物与依赖目录可排除；锁文件先检查是否涉及版本升级，再按依赖变更摘要纳入分析，不能一刀切跳过
- 大 diff 先按业务风险与公共依赖分组，优先权限、金额、迁移、公共契约、配置和依赖升级；记录每组已读/未读范围，不能只取行数最多的前20个文件

### 4.3 安全约束：命令注入防护

> **执行任何 `git diff` 命令前必须遵守以下规则，防止命令注入。**

- **参数校验**：分支名、commit hash、tag 名仅允许字母、数字、`/`、`-`、`_`、`.`、`^`、`~` 字符，禁止包含 shell 元字符（`;` `|` `$` `` ` `` `(` `)` `&` `>` `<` `'` `"` `\n`）
- **禁止拼接**：不得将用户输入直接拼入 `git diff` 命令，必须先校验格式
- **禁止事项**：禁止直接执行用户提供的 shell 命令字符串；禁止使用 `eval`、`os.system` 或 shell=True 执行包含用户输入的命令

## 5. 各模式输入输出示例

### 5.1 模式 1：工作区改动

```
用户：帮我分析一下当前改动对测试用例的影响，用例在 docs/test-cases.md
```

执行：先运行 `git status --short`。工作区非空时执行 `git diff --no-ext-diff --no-textconv HEAD`；工作区干净且当前 feature 分支领先默认分支时，解析默认分支后执行 `git diff --no-ext-diff --no-textconv <default>...HEAD`。两者均为空时才报告「无变更」。

产出：
```json
{
  "source": "working-tree",
  "name_status": [["M", "src/api/user.ts"], ["A", "src/api/profile.ts"]],
  "numstat": [["12", "3", "src/api/user.ts"], ["45", "0", "src/api/profile.ts"]],
  "unified_diff": "diff --git a/src/api/user.ts ..."
}
```

### 5.2 模式 2：暂存区改动

```
用户：分析已暂存的改动，用例在 docs/test-cases.md
```

执行：`git diff --no-ext-diff --no-textconv --cached`

### 5.3 模式 3：分支对比

```
用户：对比 main 和 feat/order-cancel 分支的改动，检查对 order 相关用例的影响
```

执行：`git diff --no-ext-diff --no-textconv main...feat/order-cancel`

### 5.4 模式 4：单个 Commit

```
用户：检查 commit abc1234 的改动是否影响了 regression 用例
```

执行：`git diff --no-ext-diff --no-textconv abc1234~1..abc1234`

### 5.5 模式 5：Commit 范围

```
用户：分析 abc1234 到 def5678 之间的所有改动
```

执行：`git diff --no-ext-diff --no-textconv abc1234..def5678`

### 5.6 模式 6：Revision Range

```
用户：分析 main..HEAD 的改动
```

执行：原样传入 `git diff --no-ext-diff --no-textconv main..HEAD`

### 5.7 模式 7：PR Diff / 外部 Patch

```
用户：分析这个 patch 对现有用例的影响，patch 内容如下：
diff --git a/src/api/user.ts ...
```

执行：不执行 git 命令，直接解析 patch 内容。

产出：
```json
{
  "source": "patch",
  "name_status": [["M", "src/api/user.ts"]],
  "numstat": [["8", "1", "src/api/user.ts"]],
  "unified_diff": "diff --git a/src/api/user.ts ..."
}
```

## 6. 与其他 knowledge 文件的关联

- 采集到的变更清单 → 阶段 2 [cross-impact-analysis.md](cross-impact-analysis.md) 做跨层链路追踪与契约两侧检查
- 失败兜底（不在 git 仓库 / diff 为空 / diff 过大 / 可选用例不可达等）见 [anti-patterns.md](anti-patterns.md) 第 7 节
- 报告输出格式见 [report-template.md](report-template.md)
