# 微信公众号排版技能 (wechat-formatter)

一套面向技术领域的微信公众号文章排版技能，提供四种风格模板，自动分析文章内容并输出可直接复制到公众号编辑器的格式化 Markdown。

## 适用场景

- 编程知识、测试理论、架构设计等技术类文章
- 技术博客排版、教程文章美化、干货分享格式化
- 技术随笔润色、行业观察整理

## 四种排版风格

| 风格 | 代号 | 适用内容 | 视觉特征 |
|------|------|---------|---------|
| 技术博客 | `tech-blog` | 编程教程、技术分享、工具介绍 | 导读框 + 中文编号章节 + 核心观点框 |
| 教程指南 | `tutorial` | 操作指南、最佳实践、配置说明 | 目标框 + Step 五段式 + 四种提示框 |
| 深度干货 | `deep-dive` | 原理剖析、架构分析、技术复盘 | 摘要框 + 目录 + 核心结论框 + 图表编号 |
| 轻松聊天 | `casual-chat` | 经验总结、技术随笔、行业思考 | 自然开场 + 短段落 + Emoji 点缀 + 互动引导 |

## 使用方式

### 默认模式（四阶段）

1. 将待排版的文章提供给 Claude
2. Claude 分析文章内容，推荐适合的风格
3. 用户选择风格后，Claude 按模板完成排版
4. 输出格式化 Markdown 文件

### 快速模式

用户直接指定风格代号，跳过风格选择阶段：

```
用 tech-blog 排版这篇文章
```

## 文件结构

```
wechat-formatter/
├── SKILL.md                    # 技能主文件（索引 + 决策树）
├── README.md                   # 本文件
├── templates/                  # 风格模板
│   ├── template-index.md       # 模板索引与选择指南
│   ├── tech-blog.md            # 技术博客风格规则
│   ├── tutorial.md             # 教程指南风格规则
│   ├── deep-dive.md            # 深度干货风格规则
│   └── casual-chat.md          # 轻松聊天风格规则
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
- **Emoji**：tech-blog/tutorial/deep-dive ≤ 5 个，casual-chat 8-15 个

## CSS 渲染建议

Markdown 文件本身不包含 CSS。建议通过以下工具应用样式后复制到公众号编辑器：

- [mdnice](https://mdnice.com) — 支持自定义 CSS，技术文章首选
- [135 编辑器](https://www.135editor.com) — 丰富模板库
- [壹伴](https://yiban.io) — 浏览器插件，直接在公众号后台排版

万能公式：**15px 字体 + 1.75 倍行距 + 正文色 #3f3f3f + 重点色用品牌色**

## 输出规范

- 文件名：`{原文件名}_formatted_{风格代号}.md`
- 文件头：HTML 注释包含排版风格、时间、原始文件、图片/代码块数量
- 文末：参考资料（脚注式）+ 互动引导
