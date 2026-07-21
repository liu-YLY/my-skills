# Diff 模式与只读采集

> **何时阅读**：阶段 1「收集输入」时加载本文件，确认 diff 范围并执行采集。
> **覆盖范围**：七种 diff 模式 / 自动推断规则 / 只读采集脚本字段语义 / 模式选择决策树 / 输入输出示例。

## 1. 七种 Diff 模式

| 模式 | 触发条件 | Git 命令 |
|------|---------|---------|
| 工作区改动 | 用户说"当前改动"/"本地改动"/未指定范围 | `git diff`（未暂存） |
| 暂存区改动 | 用户说"已暂存"/"staged" | `git diff --cached` |
| 分支对比 | 用户指定了两个分支名 | `git diff <base>...<head>` |
| 单个 Commit | 用户指定了单个 commit hash | `git diff <commit>~1..<commit>` |
| Commit 范围 | 用户指定了 commit 区间 | `git diff <commit1>..<commit2>` |
| Revision Range | 用户给出 `A..B` / `A...B` 形式 | 原样传入 `git diff <range>` |
| PR Diff / 外部 Patch | 用户粘贴 patch 或提供 PR diff 文件路径 | 不执行 git，直接解析 patch 内容 |

## 2. 自动推断规则

- 若用户未指定范围，默认使用「工作区改动」模式
- 若用户指定了单个分支名如 `feat/xxx`，自动对比 `main...feat/xxx`
- 若用户提供了 commit hash，使用该 commit 与前一个 commit 的 diff
- 若用户粘贴了 `diff --git ...` 开头的内容，识别为外部 Patch，跳过 git 命令

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
  │    ├─ 单个分支名 → 模式 3：分支对比（main...feat/xxx）
  │    └─ 两个分支名 → 模式 3：分支对比（base...head）
  │
  ├─ 说"已暂存"/"staged"
  │    → 模式 2：暂存区改动（git diff --cached）
  │
  ├─ 未指定范围 / 说"当前改动"/"本地改动"
  │    → 模式 1：工作区改动（git diff）
  │
  └─ 上述均不匹配
       → 主动追问用户，不擅自选择
```

## 4. 只读采集脚本

为避免一次性把整个仓库塞给模型，推荐使用只读脚本采集变更上下文，再由 Skill 定向读取相关调用方、接口、数据模型和测试文件。

### 4.1 产出结构（字段语义同 git 原生输出）

```json
{
  "source": "working-tree | staged | commit | range | patch",
  "status_short": [],
  "name_status": [],
  "numstat": [],
  "untracked_files": [],
  "diff_truncated": false,
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

### 4.2 脚本安全策略（必须遵守）

- 整个采集过程保持**只读**，不修改代码、不运行测试、不执行 git textconv
- **不读取**未跟踪文件的具体内容（仅记录文件名）
- **不对**二进制文件进行文本转换
- Diff 超过指定大小时进行**截断**，并在报告中标注「部分文件未分析」
- 跳过 `lock`/`dist`/`build`/`node_modules` 等产物与依赖文件

## 5. 各模式输入输出示例

### 5.1 模式 1：工作区改动

```
用户：帮我分析一下当前改动对测试用例的影响，用例在 docs/test-cases.md
```

执行：`git diff` + `git diff --cached`（获取本地改动）

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

执行：`git diff --cached`

### 5.3 模式 3：分支对比

```
用户：对比 main 和 feat/order-cancel 分支的改动，检查对 order 相关用例的影响
```

执行：`git diff main...feat/order-cancel`

### 5.4 模式 4：单个 Commit

```
用户：检查 commit abc1234 的改动是否影响了 regression 用例
```

执行：`git diff abc1234~1..abc1234`

### 5.5 模式 5：Commit 范围

```
用户：分析 abc1234 到 def5678 之间的所有改动
```

执行：`git diff abc1234..def5678`

### 5.6 模式 6：Revision Range

```
用户：分析 main..HEAD 的改动
```

执行：原样传入 `git diff main..HEAD`

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
- 失败兜底（不在 git 仓库 / diff 为空 / diff 过大 / 用例文件不存在等）见 [../SKILL.md](../SKILL.md) 阶段 1 内联表
- 报告输出格式见 [report-template.md](report-template.md)
