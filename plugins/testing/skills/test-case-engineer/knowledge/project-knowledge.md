# 项目知识自动发现与文档格式处理

> **来源优先级**：用户明确要求 > 项目已确认资料 > Skill 通用知识 > 行业模板。冲突、缺日期或疑似过期资料注明来源与待确认；模板不覆盖项目事实，不改写历史用例。
> **何时阅读**：阶段 1 必读；Office/PDF 转换时读。用户已提供需求文本/Markdown 且无项目文档需扫描时可跳过。

## 项目知识目录约定

阶段 1 必须扫描以下目录，存在则读：

| 路径 | 内容 |
|------|------|
| `docs/README.md` | 文档索引 |
| `docs/prd/` | PRD 需求文档 |
| `docs/api/` | API 文档、Swagger/OpenAPI |
| `docs/design/` | UI 设计稿说明、交互规范 |
| `docs/reference/` | 行业规范、竞品、第三方文档 |
| `testing-tm-cases/releases/` | 已有用例（继承风格/ID） |
| `CHANGELOG.md` 或 `docs/changelog/` | 版本变更与影响范围 |

## 文档格式处理

优先读文本格式；PDF/图片可直接读。

遇到 `.docx`/`.xlsx`/`.xls`/`.pptx`/`.pdf`：

1. 先找同名 `.md`/`.csv`，存在直接读。
2. 不存在则主动转换后继续后续阶段，不得回复「请先手动转换」或中途停下。执行前遵守 [integrations/quickstart.md](../integrations/quickstart.md)「安全约束」，不拼接或改写用户路径。
3. 优先 MarkItDown：`"$TOOLS_ENV/bin/markitdown" <文件路径> -o <输出路径>.md`
4. 首次自举：解析 `TOOLS_ROOT`，用临时 `TOOLS_ENV` 安装 `$TOOLS_ROOT/scripts/requirements.txt`。

**降级**：MarkItDown 不可用（Python <3.10、安装失败、找不到命令）时用 `"$TOOLS_ENV/bin/python" "$TOOLS_ROOT/scripts/convert_docs.py" <路径> --recursive`；仅支持 `.docx`/`.xlsx`/`.pptx`，不支持 PDF 和 `.xls`，须说明局限。

**无法创建 venv 或执行终端**：只处理可直接读取的格式，说明 Office/PDF 局限并建议导出 Markdown/文本，不得无限重试。

**用户只给文档路径或「根据某 docx 写用例」**：先解析路径，按上述步骤转换读取，再完成阶段 1–4。
