# 本地操作速查

> **何时阅读**：执行任何 shell 命令（文档转换、日志读取）前查阅，获取确切命令与路径。
> **覆盖范围**：SKILL_ROOT 路径解释 / 文档转换 / 缺陷模式库引用路径。
> **可跳过条件**：本次任务不需要执行任何 shell 命令（纯分析或纯讨论）。

## SKILL_ROOT

在本仓库中：`SKILL_ROOT` = `skills/bug-analyzer`

> 下文命令中的 `$SKILL_ROOT` 是占位符，**Agent 执行命令时必须替换为上述实际路径**。
> 人在终端使用时，先执行 `export SKILL_ROOT=skills/bug-analyzer`，或手动将 `$SKILL_ROOT` 替换为实际路径。

## 文档转换命令

**主方案：Microsoft MarkItDown（推荐）**

```bash
# 首次使用：创建 venv 并安装
python3 -m venv .venv-tools
.venv-tools/bin/pip install -r $SKILL_ROOT/scripts/requirements.txt

# 转换单个文件 → 输出同名 .md
.venv-tools/bin/markitdown logs/bug-report.docx -o logs/bug-report.md

# 批量转换整个目录
for f in logs/*.docx logs/*.pptx logs/*.xlsx logs/*.xls; do
    [ -f "$f" ] && .venv-tools/bin/markitdown "$f" -o "${f%.*}.md"
done
```

**降级方案：内置 convert_docs.py（MarkItDown 不可用时使用）**

```bash
.venv-tools/bin/python $SKILL_ROOT/scripts/convert_docs.py logs/ --recursive
```

> 降级方案仅支持 `.docx`、`.xlsx`、`.pptx`，不支持 PDF 和 `.xls`。

## 共享缺陷模式库路径

缺陷模式库主文件位于 test-case-engineer skill：

```
../test-case-engineer/knowledge/bug-patterns.md
```

详见 [knowledge/bug-patterns-index.md](knowledge/bug-patterns-index.md)。
