# 本地操作速查

> **何时阅读**：执行任何 shell 命令（文档转换、日志读取）前查阅，获取确切命令与路径。
> **覆盖范围**：SKILL_ROOT 路径解释 / 文档转换 / 缺陷模式库引用路径。
> **可跳过条件**：本次任务不需要执行任何 shell 命令（纯分析或纯讨论）。

## SKILL_ROOT / TOOLS_ROOT

`SKILL_ROOT` 为当前实际读取的 `SKILL.md` 所在目录，使用绝对路径；源码安装和运行时安装均适用。依赖同目录下的 test-case-engineer；单独安装本 Skill 时须一并安装该依赖。缺失时报告资源不可用，不猜测源码路径。

```bash
# 将路径替换为当前实际读取的 SKILL.md 所在目录
SKILL_ROOT="/absolute/path/to/bug-analyzer"
TOOLS_ROOT="$(dirname "$SKILL_ROOT")/test-case-engineer"
TOOLS_ENV="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="testing-skill-tools-"))')"
```

脚本位于 `TOOLS_ROOT/scripts`；虚拟环境位于临时目录，不写入只读的插件缓存。

## 文档转换命令

> bug-analyzer 使用 test-case-engineer 内的转换资源。

**主方案：Microsoft MarkItDown（推荐）**

```bash
# 首次使用：创建共享 venv 并安装（临时目录，两个 skill 共用）
python3 -m venv "$TOOLS_ENV"
"$TOOLS_ENV/bin/pip" install -r "$TOOLS_ROOT/scripts/requirements.txt"

# 转换单个文件 → 输出同名 .md
"$TOOLS_ENV/bin/markitdown" logs/bug-report.docx -o logs/bug-report.md

# 批量转换整个目录
for f in logs/*.docx logs/*.pptx logs/*.xlsx logs/*.xls; do
    [ -f "$f" ] && "$TOOLS_ENV/bin/markitdown" "$f" -o "${f%.*}.md"
done
```

**降级方案：共享 convert_docs.py（MarkItDown 不可用时使用）**

```bash
"$TOOLS_ENV/bin/python" "$TOOLS_ROOT/scripts/convert_docs.py" logs/ --recursive
```

> 降级方案仅支持 `.docx`、`.xlsx`、`.pptx`，不支持 PDF 和 `.xls`。
> Windows 环境下路径为 `$TOOLS_ENV/Scripts/markitdown.exe`。

## 共享缺陷模式库路径

缺陷模式库主文件位于 test-case-engineer skill：

```
../test-case-engineer/knowledge/bug-patterns.md
```

详见 [knowledge/bug-patterns-index.md](../knowledge/bug-patterns-index.md)。

## 安全约束

> **执行任何 shell 命令前必须遵守以下规则，防止命令注入。**

### 文件路径安全

- **路径处理**：保持用户文件名原样，解析绝对路径并核对任务范围；用参数数组传递，不把路径拼成 shell 代码，也不擅自删除文件名中的字符
- **路径限定**：文件路径必须在项目目录范围内，禁止路径穿越（如 `../../../etc/passwd`）
- **参数传递**：脚本使用参数数组且不启用 shell；终端示例中的变量路径用双引号包裹，不对用户内容进行二次求值

### 禁止事项

- **禁止**直接执行用户提供的 shell 命令字符串
- **禁止**将未校验的用户输入作为 shell 命令参数
- **禁止**使用 `eval`、`os.system` 或 shell=True 执行包含用户输入的命令
