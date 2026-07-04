# 本地操作速查

> **何时阅读**：执行任何 shell 命令（文档转换、日志读取）前查阅，获取确切命令与路径。
> **覆盖范围**：SKILL_ROOT 路径解释 / 文档转换 / 缺陷模式库引用路径。
> **可跳过条件**：本次任务不需要执行任何 shell 命令（纯分析或纯讨论）。

## SKILL_ROOT / PLUGIN_ROOT

在本仓库中：
- `SKILL_ROOT` = `skills/bug-analyzer`
- `PLUGIN_ROOT` = `plugins/testing`（共享虚拟环境和脚本所在层级）

> 下文命令中的 `$SKILL_ROOT` / `$PLUGIN_ROOT` 是占位符，**Agent 执行命令时必须替换为上述实际路径**。
> 人在终端使用时，先执行：
> ```bash
> export SKILL_ROOT=plugins/testing/skills/bug-analyzer
> export PLUGIN_ROOT=plugins/testing
> ```

## 文档转换命令

> **共享虚拟环境**：`.venv-tools` 和 `scripts/` 位于 `$PLUGIN_ROOT/` 层级，bug-analyzer 与 test-case-engineer 共享使用，避免重复安装。

**主方案：Microsoft MarkItDown（推荐）**

```bash
# 首次使用：创建共享 venv 并安装（plugin 层级，两个 skill 共用）
python3 -m venv $PLUGIN_ROOT/.venv-tools
$PLUGIN_ROOT/.venv-tools/bin/pip install -r $PLUGIN_ROOT/scripts/requirements.txt

# 转换单个文件 → 输出同名 .md
$PLUGIN_ROOT/.venv-tools/bin/markitdown logs/bug-report.docx -o logs/bug-report.md

# 批量转换整个目录
for f in logs/*.docx logs/*.pptx logs/*.xlsx logs/*.xls; do
    [ -f "$f" ] && $PLUGIN_ROOT/.venv-tools/bin/markitdown "$f" -o "${f%.*}.md"
done
```

**降级方案：共享 convert_docs.py（MarkItDown 不可用时使用）**

```bash
$PLUGIN_ROOT/.venv-tools/bin/python $PLUGIN_ROOT/scripts/convert_docs.py logs/ --recursive
```

> 降级方案仅支持 `.docx`、`.xlsx`、`.pptx`，不支持 PDF 和 `.xls`。
> Windows 环境下路径为 `$PLUGIN_ROOT/.venv-tools/Scripts/markitdown.exe`。

## 共享缺陷模式库路径

缺陷模式库主文件位于 test-case-engineer skill：

```
../test-case-engineer/knowledge/bug-patterns.md
```

详见 [knowledge/bug-patterns-index.md](knowledge/bug-patterns-index.md)。
