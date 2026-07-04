# 本地操作速查

> **何时阅读**:执行任何 shell 命令(文档转换)前查阅,获取确切命令与路径。
> **覆盖范围**:SKILL_ROOT 路径解释 / 文档转换 (MarkItDown + 降级 convert_docs.py) / 项目知识目录速查。
> **可跳过条件**:本次任务不需要执行任何 shell 命令(纯文档分析或纯讨论)。

> 本文档提供本 Skill 在本仓库中的**具体可执行命令和路径**,与 IDE 无关,Agent 按需查阅。

## SKILL_ROOT / PLUGIN_ROOT

在本仓库中：
- `SKILL_ROOT` = `skills/test-case-engineer`
- `PLUGIN_ROOT` = `plugins/testing`（共享虚拟环境和脚本所在层级）

> 下文命令中的 `$SKILL_ROOT` / `$PLUGIN_ROOT` 是占位符，**Agent 执行命令时必须替换为上述实际路径**。
> 人在终端使用时，先执行：
> ```bash
> export SKILL_ROOT=plugins/testing/skills/test-case-engineer
> export PLUGIN_ROOT=plugins/testing
> ```

## 文档转换命令

> **共享虚拟环境**：`.venv-tools` 和 `scripts/` 位于 `$PLUGIN_ROOT/` 层级，test-case-engineer 与 bug-analyzer 共享使用，避免重复安装。

**主方案：Microsoft MarkItDown（推荐）**

```bash
# 首次使用：创建共享 venv 并安装（plugin 层级，两个 skill 共用）
python3 -m venv $PLUGIN_ROOT/.venv-tools
$PLUGIN_ROOT/.venv-tools/bin/pip install -r $PLUGIN_ROOT/scripts/requirements.txt

# 转换单个文件 → 输出同名 .md
$PLUGIN_ROOT/.venv-tools/bin/markitdown docs/需求文档.docx -o docs/需求文档.md

# 批量转换整个目录
for f in docs/*.docx docs/*.pptx docs/*.xlsx docs/*.xls; do
    [ -f "$f" ] && $PLUGIN_ROOT/.venv-tools/bin/markitdown "$f" -o "${f%.*}.md"
done
```

**降级方案：共享 convert_docs.py（MarkItDown 不可用时使用）**

```bash
# 依赖已在 requirements.txt 中一并安装，直接运行即可
$PLUGIN_ROOT/.venv-tools/bin/python $PLUGIN_ROOT/scripts/convert_docs.py docs/ --recursive
```

> 降级方案仅支持 `.docx`、`.xlsx`、`.pptx`，不支持 PDF 和 `.xls`。
> Windows 环境下路径为 `$PLUGIN_ROOT/.venv-tools/Scripts/markitdown.exe`。

## 项目知识目录

阶段 1 扫描路径详见 [knowledge/project-knowledge.md](knowledge/project-knowledge.md)「项目知识目录约定」表。
