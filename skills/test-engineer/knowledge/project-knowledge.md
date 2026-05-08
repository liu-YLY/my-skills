# 项目知识自动发现与文档格式处理

> **何时阅读**:阶段 1 信息收集时**必读**(SKILL.md 强制要求);遇到 Office/PDF 文件需要转换时必读。
> **覆盖范围**:项目知识目录约定(docs/prd 等扫描清单) + Office/PDF 文档转换流程(MarkItDown 主方案 + convert_docs.py 降级)。
> **可跳过条件**:本次任务用户已直接提供需求文本/Markdown,且无项目内文档需扫描。
> **快速定位**:
> - 阶段 1 第一步扫描什么 → 上方表格
> - 遇到 .docx/.pdf → 跳「文档格式处理」节

## 项目知识目录约定

在阶段 1 执行时，**必须主动扫描**项目中以下约定目录。存在则读取，不存在则跳过：

| 约定路径 | 期望内容 | 读取方式 |
|----------|----------|----------|
| **`docs/README.md`** | **文档索引（最先读取）** | **读取索引文件，了解有哪些文档可用** |
| `docs/prd/` | PRD 需求文档 | 按索引指引读取相关文档 |
| `docs/api/` | API 接口文档、Swagger/OpenAPI 规范 | 读取并查看端点定义和字段约束 |
| `docs/design/` | UI 设计稿说明、交互规范 | 读取以了解交互细节 |
| `docs/reference/` | 行业规范、竞品分析、第三方文档 | 按需读取 |
| `testing-tm-cases/releases/` 或 `releases/`| 已有的 YAML 测试用例 | 读取同模块用例，继承风格和 ID 序号 |
| `CHANGELOG.md` 或 `docs/changelog/` | 版本变更记录 | 了解近期改动和影响范围 |

---

## 文档格式处理（必须自动完成）

优先读取 `.md`/`.txt`/`.yaml`/`.json`/`.csv`/`.pdf`/图片。

### 遇到 Office 格式（`.docx`/`.xlsx`/`.xls`/`.pptx`）或 `.pdf` 时

**步骤 1**：先查找同名 `.md` 或 `.csv`，存在则直接读取。

**步骤 2**：若不存在，由当前 Agent **主动执行转换**，生成可读文件后再读取，并**继续完成后续阶段**（需求理解 → 测试点提取 → 用例编写 → 自检）。**不得**回复「请先手动执行转换命令」或中途停下让用户操作。

**步骤 3**：执行转换，**优先使用 MarkItDown**（支持 PDF + Office + 更多格式）：

```bash
# 主方案：Microsoft MarkItDown（推荐，支持 PDF/.docx/.pptx/.xlsx/.xls 等）
.venv-tools/bin/markitdown <文件路径> -o <输出路径>.md
```

**步骤 4（首次自举）**：按以下顺序准备 Python 环境：
1. 若 `.venv-tools` 已存在 → 直接用
2. 若 `.venv` 存在 → 优先用它安装 markitdown
3. 若两者都不存在 → 自动创建 `.venv-tools`：
```bash
python3 -m venv .venv-tools
.venv-tools/bin/pip install -r $SKILL_ROOT/scripts/requirements.txt
```

依赖列表：`$SKILL_ROOT/scripts/requirements.txt`（`markitdown[docx,pptx,xlsx,xls]`）

### 降级策略

**若 MarkItDown 不可用**（Python < 3.10、安装失败、找不到命令），降级为内置 `convert_docs.py`（依赖已在 requirements.txt 中一并安装）：
```bash
.venv-tools/bin/python $SKILL_ROOT/scripts/convert_docs.py <文件或目录路径> --recursive
```

降级方案仅支持 `.docx`、`.xlsx`、`.pptx`，不支持 PDF 和 `.xls`，须在输出中说明局限。

**若完全无法创建 venv 或执行终端命令**：仅处理可直接读取的格式，对 Office/PDF 说明局限，建议用户导出为 Markdown/文本，**不得**无限重试失败命令。

**用户仅提供需求文档路径或「根据某 docx 写用例」时**：先解析文档路径，按上述步骤自动完成转换与读取，再按阶段 1～4 输出需求理解、测试点与用例。
