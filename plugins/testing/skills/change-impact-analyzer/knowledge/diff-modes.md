# Diff 模式与只读采集

> **何时阅读**：阶段 1「收集输入」时加载，确认 diff 范围并执行采集。
> **覆盖范围**：七种 diff 模式 / 自动推断 / 只读采集字段 / 安全约束 / 示例。

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

模式选择：先看是否粘贴 patch/提供文件（模式 7）；再看 commit hash（模式 4/5）、`A..B` 区间（模式 6）、分支名（模式 3）、"已暂存"（模式 2）；未指定范围时按第 2 节判断工作区或分支。均不匹配则追问，不擅自选择。

### 1.1 工单、技术说明与多仓库提交核对

用户要求定位实际改动，或材料涉及共享库与多个服务时，在已授权仓库范围内先查版本，再定向核对 diff；技术说明本身也可作为改动点输入，不强制等待源码。

1. 在已知仓库用工单号/提交说明查线索，再用目标字段、符号、文件历史查补充提交。工单号命中不证明范围完整；依赖升级和后续修正可能没有相同工单号。
2. 核对候选提交的实际 diff、父节点及先后关系，按仓库记录 `base/head` 和相关提交；未知仓库、不可达 ref 保持待核实，不自动扩展目录或替换基线。
3. 同时看单提交改动与基线到最终 head 的净变化。新增后移除的字段、撤回的逻辑不作为最终新增功能必测；若曾部署/写入数据则另列过渡与兼容风险，部署未知不能假定曾上线。
4. 核对共享库版本、各消费服务的清单/锁文件及对应源码。分别记录「仓库实现版本」「声明依赖版本」「实际部署版本」；前两项不能证明部署已生效。
5. 报告附仓库、提交/版本、最终改动摘要、来源冲突和未查范围；固定 SHA 的代码链接仅在 remote、路径和位置已核对时提供。用户文档与源码冲突时并列来源，不静默采用任一方。

提交查询属于只读采集，仍遵守第 3 节安全约束。未更新远端引用时注明本地引用状态；更新引用另依当次授权，不切分支或拉取合并来做影响分析。

## 2. 自动推断规则

- 未指定范围时先检查 `git status --short`；工作区非空用「工作区改动」。
- 工作区干净时检查当前分支与默认分支：feature 分支有未合并提交时，用默认分支的远端跟踪引用（优先 `origin/main` / `origin/master`）与 `HEAD` 做三点对比。
- 工作区干净且位于默认分支时，才输出「无变更」；不得忽略 feature 分支上已提交但未合并的改动。
- 只指定 head 分支时，优先 PR 目标或已确认基线，其次仓库默认分支；记录解析后的 ref/SHA，不硬编码 main。默认分支无法确认时询问。
- 提供 commit hash 时使用该 commit 与前一个 commit 的 diff；单提交为根提交时使用 `git show --root --format= --no-ext-diff --no-textconv <commit>`；合并提交说明父节点比较口径，不默默漏掉合并改动。
- 粘贴 `diff --git ...` 开头的内容时识别为外部 Patch，跳过 git 命令。
- 有前后片段或具体改动点时直接解析材料，标明源码是否已核对，不要求用户必须导出 patch。
- 「当前改动」工作区非空时只含未提交的已跟踪改动，披露是否排除已提交分支差异；明确要求整个功能含本地改动时，解析 merge-base 后对工作树比较。未跟踪文件单列，未读内容不能认定覆盖或无影响。

## 3. 只读采集

先获取完整变更目录、状态与版本，再定向读取相关调用方、接口、数据模型和测试文件。以下是原生命令采集结果的建议字段，当前 skill 不附带采集脚本，不宣称脚本已经执行。

```json
{
  "source": "working-tree | staged | commit | range | patch",
  "base_ref": null, "base_sha": null, "head_sha": null, "material_version": null,
  "status_short": [], "name_status": [], "numstat": [], "untracked_files": [],
  "diff_truncated": false, "analyzed_files": [], "unread_files": [], "excluded_files": [],
  "unified_diff": ""
}
```

| 字段 | 用途 |
|------|------|
| `status_short` / `name_status` / `numstat` | 变化文件、新增/修改/删除/重命名、增删行数 |
| `untracked_files` / `unified_diff` / `diff_truncated` | 未跟踪文件、具体差异、是否截断 |
| `base_ref/base_sha/head_sha/material_version` | 比较口径及来源版本；不能虚构不可得的 SHA |
| `analyzed_files/unread_files/excluded_files` | 区分已读、未读和有理由排除的范围 |

**采集安全策略（必须遵守）**：

- 整个过程保持**只读**，不修改代码、不运行测试、不执行 git textconv。
- **不读取**未跟踪文件的具体内容（仅记录文件名）；**不对**二进制文件做文本转换。
- Diff 超过指定大小时**截断**，并在报告中标注「部分文件未分析」。
- 构建产物与依赖目录可排除；锁文件先检查是否涉及版本升级，再按依赖变更摘要纳入，不能一刀切跳过。
- 大 diff 先按业务风险与公共依赖分组，优先权限、金额、迁移、公共契约、配置和依赖升级；记录每组已读/未读范围，不能只取行数最多的前 20 个文件。

**命令注入防护**：

- 分支名、commit hash、tag 名仅允许字母、数字、`/`、`-`、`_`、`.`、`^`、`~`；禁止 shell 元字符（`;` `|` `$` `` ` `` `(` `)` `&` `>` `<` `'` `"` 换行）。
- 不得将用户输入直接拼入 `git diff` 命令，必须先校验格式；禁止执行用户提供的 shell 字符串，禁止 `eval`、`os.system` 或 `shell=True` 执行含用户输入的命令。

## 4. 各模式输入输出示例

| 模式 | 用户输入 | 执行 | 产出要点 |
|------|---------|------|---------|
| 1 工作区 | 「分析当前改动对用例的影响，用例在 docs/test-cases.md」 | `git status --short`；非空跑模式 1 命令，干净则按第 2 节判断分支或报告无变更 | `source: working-tree`，含 `name_status/numstat/unified_diff` |
| 2 暂存区 | 「分析已暂存的改动」 | 模式 2 命令 | `source: staged` |
| 3 分支对比 | 「对比 main 和 feat/order-cancel」 | 模式 3 命令 | `source: range`，记录 base/head SHA |
| 4 单 Commit | 「检查 commit abc1234」 | 模式 4 命令 | `source: commit` |
| 5 Commit 范围 | 「分析 abc1234 到 def5678」 | 模式 5 命令 | `source: range` |
| 6 Revision Range | 「分析 main..HEAD」 | 模式 6 命令 | `source: range`，原样传入 |
| 7 外部 Patch | 粘贴 `diff --git ...` | 不执行 git | `source: patch`，仅解析 patch |

## 5. 与其他 knowledge 文件的关联

- 变更清单 → 阶段 2 [cross-impact-analysis.md](cross-impact-analysis.md) 做链路追踪与契约检查
- 失败兜底（不在 git 仓库 / diff 为空 / 过大 / 用例不可达）见 [anti-patterns.md](anti-patterns.md) 第 5 节
- 报告输出格式见 [report-template.md](report-template.md)
