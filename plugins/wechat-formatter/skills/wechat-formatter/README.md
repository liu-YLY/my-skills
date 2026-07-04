# 微信公众号排版技能 (wechat-formatter)

一套面向技术领域的微信公众号文章排版技能，提供六种风格模板，自动分析文章内容并输出可直接复制到公众号编辑器的格式化 Markdown。

## 适用场景

- 编程知识、测试理论、架构设计等技术类文章
- 技术博客排版、教程文章美化、干货分享格式化
- 技术随笔润色、行业观察整理

## 六种排版风格

| 风格 | 代号 | 适用内容 | 视觉特征 |
|------|------|---------|---------|
| 技术博客 | `tech-blog` | 编程教程、技术分享、工具介绍 | 导读框 + 中文编号章节 + 核心观点框 |
| 教程指南 | `tutorial` | 操作指南、最佳实践、配置说明 | 目标框 + Step 五段式 + 四种提示框 |
| 深度干货 | `deep-dive` | 原理剖析、架构分析、技术复盘 | 摘要框 + 目录 + 核心结论框 + 图表编号 |
| 轻松聊天 | `casual-chat` | 经验总结、技术随笔、行业思考 | 自然开场 + 短段落 + Emoji 点缀 + 互动引导 |
| 苹果风 | `apple` | 产品设计、架构哲学、技术选型 | 极简留白 + 圆角卡片 + Apple 品牌色 |
| 赛博朋克 | `cyber` | 安全技术、前沿探索、极客文化 | 暗黑背景 + 霓虹色调 + 发光代码块 |

## 使用方式

### 默认模式（五阶段）

1. 将待排版的文章提供给 Claude
2. Claude 分析文章内容，推荐适合的风格
3. 用户选择风格后，Claude 按模板完成排版
4. 输出格式化 Markdown 文件
5. Claude 自动生成可直接粘贴到公众号的 HTML 文件（带"复制到公众号"按钮）

### 快速模式

用户直接指定风格代号，跳过风格选择阶段：

```
用 tech-blog 排版这篇文章
```

### 一键复制

生成的 HTML 文件在浏览器中打开后，点击「复制到公众号」按钮，即可直接粘贴到微信公众号编辑器，样式完整保留。

## 文件结构

```
wechat-formatter/
├── SKILL.md                    # 技能主文件（索引 + 决策树）
├── README.md                   # 本文件
├── scripts/                    # 工具脚本
│   └── md2wechat.py            # Markdown → 可粘贴 HTML 转换脚本
├── templates/                  # 风格模板
│   ├── template-index.md       # 模板索引与选择指南
│   ├── tech-blog.md            # 技术博客风格规则
│   ├── tutorial.md             # 教程指南风格规则
│   ├── deep-dive.md            # 深度干货风格规则
│   ├── casual-chat.md          # 轻松聊天风格规则
│   ├── apple.md                # 苹果风风格规则
│   └── cyber.md                # 赛博朋克风格规则
├── styles/                     # CSS 样式文件（可直接用于 mdnice）
│   ├── tech-blog.md            # 技术博客 CSS
│   ├── tutorial.md             # 教程指南 CSS
│   ├── deep-dive.md            # 深度干货 CSS
│   ├── casual-chat.md          # 轻松聊天 CSS
│   ├── apple.md                # 苹果风 CSS
│   └── cyber.md                # 赛博朋克 CSS
├── examples/                   # 示例文件
│   ├── sample-input-testing-guide.md      # 输入示例
│   ├── sample-output-tech-blog.md         # 技术博客输出示例
│   ├── sample-output-tutorial.md          # 教程指南输出示例
│   ├── sample-output-deep-dive.md         # 深度干货输出示例
│   └── sample-output-casual-chat.md       # 轻松聊天输出示例
├── references/                 # 参考规范
│   ├── formatting-rules.md     # 排版规则详解（要素识别 + 通用规则 + 质量校验）
│   └── wechat-markdown.md      # 公众号 Markdown 兼容性 + CSS 渲染参数
└── knowledge/                  # 知识库
    └── wechat-traps.md         # 公众号排版常见陷阱
```

## 排版规范要点

- **标题**：正文从 `##` 起步（`#` 留给公众号标题栏）
- **段落**：每段不超过 5 行，段落间空一行
- **代码块**：三反引号 + 语言标注，关键行用 `# ←` 标注
- **链接**：使用脚注式 `[N]`，文末集中列出 URL
- **图片**：`![描述](url)` 占位，提示用户替换
- **Emoji**：casual-chat 8-15 个，cyber 5-8 个，其他风格 ≤ 5 个
- **字号**：默认 15px，可选小号 13px 或大号 17px（CSS 文件内含字号变体）

## CSS 渲染建议

Markdown 文件本身不包含 CSS。有两种方式生成带样式的可粘贴内容：

### 方式一：一键生成 HTML（推荐）

使用 `scripts/md2wechat.py` 脚本，自动将 Markdown + CSS 合并为带内联样式的 HTML 文件：

```bash
pip install markdown beautifulsoup4
python scripts/md2wechat.py <markdown_file> <style_file> [--size small|medium|large]
```

生成的 HTML 文件在浏览器中打开后，点击「复制到公众号」按钮即可直接粘贴到微信编辑器。

### 方式二：手动使用在线工具

也可通过以下工具应用样式后复制到公众号编辑器：

- [mdnice](https://mdnice.com) — 支持自定义 CSS，技术文章首选
- [135 编辑器](https://www.135editor.com) — 丰富模板库
- [壹伴](https://yiban.io) — 浏览器插件，直接在公众号后台排版

`styles/` 目录下为每种风格提供了可直接使用的完整 CSS 文件，配合 mdnice 使用：

1. 打开 [mdnice.com](https://mdnice.com)，将排版好的 Markdown 粘贴到编辑区
2. 点击「主题」→「自定义」→ 粘贴对应风格的 CSS 代码
3. 点击「复制」按钮，粘贴到公众号编辑器

| 风格 | CSS 文件 | 主色调 | 视觉特征 |
|------|---------|--------|---------|
| 技术博客 | [styles/tech-blog.md](styles/tech-blog.md) | 深蓝 #2b5797 | 干净代码块 + 左侧边引用 |
| 教程指南 | [styles/tutorial.md](styles/tutorial.md) | 薄荷绿 #26a69a | 渐变标题背景 + 复选框支持 |
| 深度干货 | [styles/deep-dive.md](styles/deep-dive.md) | 深蓝 #2b5797 + 绿 #42b983 | 暗色代码块 + 装饰分割线 |
| 轻松聊天 | [styles/casual-chat.md](styles/casual-chat.md) | 橙色 #ff6600 | 温暖引用块 + 渐变下划线标题 |
| 苹果风 | [styles/apple.md](styles/apple.md) | 深空灰 #1d1d1f + 蓝 #0071e3 | 极简留白 + 圆角卡片 + 无装饰 |
| 赛博朋克 | [styles/cyber.md](styles/cyber.md) | 霓虹青 #00f0ff + 紫 #ff00ff | 暗黑背景 + 发光代码块 + 霓虹分割线 |

万能公式：**15px 字体 + 1.75 倍行距 + 正文色 #3f3f3f + 重点色用品牌色**

## 输出规范

- 文件名：`{原文件名}_formatted_{风格代号}.md`
- 文件头：HTML 注释包含排版风格、时间、原始文件、图片/代码块数量
- 文末：参考资料（脚注式）+ 互动引导
