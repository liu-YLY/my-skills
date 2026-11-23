# 项目知识发现与文档格式转换

> **来源优先级**：用户明确指令 > 项目已确认文档 > Skill 通用规范 > 行业惯例（冲突或过期资料标来源与待确认，不改写历史用例）。
> **何时阅读**：阶段 1 扫描项目资料或处理 Office/PDF 附件时读；用户已直接给纯文本/Markdown 需求且无仓库文档时可跳过。

## 项目文档扫描路径

阶段 1 按序检查以下路径，存在即读取并记入「信息来源」：
`docs/README.md`（索引）、`docs/prd/`（需求）、`docs/api/`（OpenAPI/接口契约）、`docs/design/`（交互/UI）、`docs/reference/`（外部规范）、`testing-tm-cases/releases/`（历史用例，继承 ID 前缀与风格）、`CHANGELOG.md` 或 `docs/changelog/`（变更范围）。

## Office / PDF 转换流程

优先直读 `.md`/`.csv`/纯文本/PDF/图片。遇到 `.docx`/`.xlsx`/`.xls`/`.pptx`（或直读受限的 `.pdf`）且无同名 `.md`/`.csv` 时，主动转换后继续执行四阶段，**禁止让用户手动转换**：

1. 执行前必须遵守 [integrations/quickstart.md](../integrations/quickstart.md)「安全约束」，严禁拼接命令或篡改用户路径。
2. 优先用 MarkItDown（首次缺环境时在临时 `TOOLS_ENV` 安装 `$TOOLS_ROOT/scripts/requirements.txt`）：
   `"$TOOLS_ENV/bin/markitdown" <文件路径> -o <输出路径>.md`
3. **降级兜底**：MarkItDown 不可用时改跑 `"$TOOLS_ENV/bin/python" "$TOOLS_ROOT/scripts/convert_docs.py" <路径> --recursive`（仅支持 `.docx`/`.xlsx`/`.pptx`，须说明不支持 `.pdf`/`.xls`）；无终端或虚拟环境权限时说明限制并请用户提供文本版，不死循环重试。
