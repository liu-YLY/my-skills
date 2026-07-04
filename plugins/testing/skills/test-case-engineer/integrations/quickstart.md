# 本地操作速查

> **何时阅读**:执行任何 shell 命令(文档转换)前查阅,获取确切命令与路径。
> **覆盖范围**:SKILL_ROOT 路径解释 / 文档转换 (MarkItDown + 降级 convert_docs.py) / 项目知识目录速查。
> **可跳过条件**:本次任务不需要执行任何 shell 命令(纯文档分析或纯讨论)。

> 本文档提供本 Skill 在本仓库中的**具体可执行命令和路径**,与 IDE 无关,Agent 按需查阅。

## SKILL_ROOT

在本仓库中：`SKILL_ROOT` = `skills/test-case-engineer`

> 下文命令中的 `$SKILL_ROOT` 是占位符，**Agent 执行命令时必须替换为上述实际路径**。
> 人在终端使用时，先执行 `export SKILL_ROOT=skills/test-case-engineer`，或手动将 `$SKILL_ROOT` 替换为实际路径。

## 文档转换命令

**主方案：Microsoft MarkItDown（推荐）**

```bash
# 首次使用：创建 venv 并安装
python3 -m venv .venv-tools
.venv-tools/bin/pip install -r $SKILL_ROOT/scripts/requirements.txt

# 转换单个文件 → 输出同名 .md
.venv-tools/bin/markitdown docs/需求文档.docx -o docs/需求文档.md

# 批量转换整个目录
for f in docs/*.docx docs/*.pptx docs/*.xlsx docs/*.xls; do
    [ -f "$f" ] && .venv-tools/bin/markitdown "$f" -o "${f%.*}.md"
done
```

**降级方案：内置 convert_docs.py（MarkItDown 不可用时使用）**

```bash
# 依赖已在 requirements.txt 中一并安装，直接运行即可
.venv-tools/bin/python $SKILL_ROOT/scripts/convert_docs.py docs/ --recursive
```

> 降级方案仅支持 `.docx`、`.xlsx`、`.pptx`，不支持 PDF 和 `.xls`。

## 项目知识目录

阶段 1 扫描路径详见 [knowledge/project-knowledge.md](knowledge/project-knowledge.md)「项目知识目录约定」表。
