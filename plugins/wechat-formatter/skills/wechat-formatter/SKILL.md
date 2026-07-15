---
name: wechat-formatter
version: 3.0.0
description: >-
  微信公众号文章排版技能，提供多种适用于互联网/技术领域的排版风格模板和高级排版模块。
  自动分析用户文章内容（编程知识、测试理论、技术分享等），按选定风格完成排版，
  支持 :::module 语法创建专业视觉卡片组件，输出为可直接复制到公众号编辑器的格式化 Markdown 文件。
  适用于：技术博客排版、教程文章美化、干货分享格式化、技术随笔润色、品牌化内容创作。
  当用户提到公众号排版、微信排版、文章排版、格式化文章、美化文章、高级排版、品牌配置时自动触发。
keywords:
  - 公众号排版
  - 微信排版
  - 文章格式化
  - 技术博客
  - 排版风格
  - 高级排版模块
  - 品牌配置
  - 视觉卡片
---

# 微信公众号排版 Skill

你是一位专业的微信公众号排版设计师，核心价值：**理解文章内容，匹配最佳风格，输出可直接发布的高质量排版**。

> **阅读策略**：本文件为**纯索引 + 核心决策树**。风格模板详情、排版规则细则全部下沉到子文件。先读子文件首部「何时阅读」摘要再决定是否全文加载，避免上下文浪费。

## 适用范围

**适用**：互联网/技术领域文章排版，包括编程知识、测试理论、架构设计、技术分享、经验复盘、行业观察等技术类内容。

**不适用**：纯文学创作、诗歌、小说等非技术类内容（可降级为通用风格处理）。

## SKILL_ROOT

`$SKILL_ROOT` = 本文件所在目录，即 `skills/wechat-formatter/`。

---

## 核心工作流（五阶段）

```
阶段 1 分析内容 → 🔴 CHECKPOINT 阶段 2 匹配风格 → 阶段 3 执行排版 → 🔴 CHECKPOINT 阶段 4 输出校验 → 阶段 5 生成可粘贴 HTML（可选）
```

| 阶段 | 详细指令 | 关键约束 | 强制读取 |
|------|----------|----------|----------|
| 1 | [references/formatting-rules.md](references/formatting-rules.md) §1 | 必须识别文章要素（标题层级、代码块、列表、要点） | 无（内联处理） |
| 🔴 2 | [templates/template-index.md](templates/template-index.md) | **必须展示风格简介让用户选择，勿自行决定** | [templates/template-index.md](templates/template-index.md) |
| 3 | 各风格模板文件 | 严格按模板规则转换，不自创格式 | 所选风格对应的模板文件 |
| 🔴 4 | [references/formatting-rules.md](references/formatting-rules.md) §4 | 覆盖度 + 可读性 + 公众号兼容性三项检查 | [references/wechat-markdown.md](references/wechat-markdown.md) + [knowledge/wechat-traps.md](knowledge/wechat-traps.md) |
| 5 | [scripts/md2wechat.py](scripts/md2wechat.py) | 用户触发时执行，生成带内联样式和"复制"按钮的 HTML | 无 |

### 🔴 CHECKPOINT 定义

| 检查点 | 触发时机 | 用户必须确认的内容 | 用户可执行动作 |
|--------|---------|------------------|-------------|
| 🔴 CHECKPOINT 1 | 阶段 2 风格推荐后 | 推荐风格是否符合预期 | 选择推荐风格 / 改选其他风格 / 终止流程 |
| 🔴 CHECKPOINT 2 | 阶段 4 校验完成后 | 校验通过，排版结果是否满足要求 | 接受排版结果进入阶段 5 / 返回阶段 3 修改 / 终止流程 |

### 模式切换

| 模式 | 触发条件 | 行为 |
|------|---------|------|
| **默认** | 用户未指定风格 | 完整五阶段：分析 → 选风格 → 排版 → 校验 → 生成 HTML |
| **快速** | 用户已明确指定风格代号（如"用 tech-blog 排版"） | 跳过阶段 2；阶段 1 仅输出简版分析（要素统计 + 一句话定性），不做详细元信息提取；阶段 4 仅做兼容性检查，跳过覆盖度和风格一致性检查；阶段 5 同默认 |
| **仅排版** | 用户明确不需要 HTML 输出 | 完成阶段 1-4 后结束，不执行阶段 5 |

---

## 六大排版风格速览

| 风格 | 代号 | 适用场景 | 核心视觉特征 |
|------|------|----------|-------------|
| **技术博客** | `tech-blog` | 编程教程、技术分享、工具介绍 | 导读框 + 中文编号章节 + 核心观点框 + 分割线 + 脚注式参考 |
| **教程指南** | `tutorial` | 操作指南、最佳实践、配置说明 | 目标框 + Step 五段式 + 4 种提示框(TIP/WARNING/NOTE/CHECK) + FAQ |
| **深度干货** | `deep-dive` | 原理剖析、架构分析、技术复盘 | 摘要框 + 纯文本目录 + 核心结论框 + 图表编号 + 参考带说明 |
| **轻松聊天** | `casual-chat` | 经验总结、技术随笔、行业思考 | 自然开场 + 短段落 + `—` 分隔 + Emoji 点缀 + 互动引导 |
| **苹果风** | `apple` | 产品设计、架构哲学、技术选型 | 极简留白 + 圆角卡片引用 + 无编号无 Emoji + Apple 品牌色 |
| **赛博朋克** | `cyber` | 安全技术、前沿探索、极客文化 | 暗黑背景 + 霓虹色调 + 发光代码块 + 系统弹窗风格引用 |

> 完整风格描述与选择指南：[templates/template-index.md](templates/template-index.md)
> 各风格详细排版规则：[templates/tech-blog.md](templates/tech-blog.md) | [templates/tutorial.md](templates/tutorial.md) | [templates/deep-dive.md](templates/deep-dive.md) | [templates/casual-chat.md](templates/casual-chat.md) | [templates/apple.md](templates/apple.md) | [templates/cyber.md](templates/cyber.md)

---

## 高级排版模块

**新功能**：支持 `:::module` 语法，提供 9 大类预定义视觉卡片组件，让文章更具视觉层级和品牌感。

### 4 件事原则

每个模块只服务这 4 件事之一：

| 目的 | 解决什么 | 代表模块 |
|------|---------|---------|
| **attention** | 让读者先知道值不值得读 | hero, cards, verdict |
| **readability** | 让手机窄屏阅读不累 | toc, steps, part |
| **memorability** | 让读者记住一个判断或品牌 | verdict, manifesto, author-card |
| **conversion** | 让读者愿意收藏/关注/咨询/转发/购买 | cta, faq, checklist |

**核心原则**：选最少的模块，每件事做好一个。一篇文章 hero 只有一个，verdict 只有一个，cta 只有一个。不要堆模块。

### 9 大类模块速览

| 类别 | 模块 | 用途 |
|------|------|------|
| **opening 开场类** | hero, toc, cards, part, label-title | 文章开篇第一屏 |
| **infographic 信息图类** | metrics, compare, steps, timeline, infographic | 数据可视化展示 |
| **judgment 判断类** | verdict, audience-fit, myth-fact, manifesto, bridge | 核心立场表达 |
| **evidence 证据类** | quote, image-annotate, image-compare, image-steps, image-text | 支撑判断的证据 |
| **conversion 行动类** | cta, faq, checklist, cases | 促进读者行动 |
| **brand 品牌类** | author-card, brand-banner | 建立品牌识别度 |
| **sprint4 精选增强类** | callout, highlight | 强调重要信息 |
| **free-layout 自由布局类** | split, columns | 灵活布局选项 |
| **interactive 交互类** | question, poll | 增加读者参与度 |

### 模块语法示例

```markdown
:::hero
eyebrow: 深度观察
title: 高级排版服务阅读决策
subtitle: 主题决定气质，模块决定读者能不能看懂
:::

:::steps[落地步骤]
01 | 发现模块 | layout list 列出所有可用模块
02 | 查看规格 | layout show 确认字段和示例
03 | 写进文章 | 直接粘贴 :::module 语法
:::

:::verdict
eyebrow: 最终判断
title: 真正的护城河不是模块数量，而是品牌表达系统
body: 每个模块必须服务一个真实的阅读任务，否则只是换皮。
:::
```

> 完整模块规范和示例：[layout/layout-modules.md](layout/layout-modules.md)
> 模块 CSS 样式：[layout/modules-base.css](layout/modules-base.css)

---

## Brand Profile 品牌配置

**新功能**：支持品牌配置文件，让所有文章保持统一的视觉风格和品牌调性。

### 核心价值

- **一致性**：所有文章保持统一的视觉风格
- **效率**：无需每次重复说明品牌偏好
- **个性化**：根据品牌调性自动选择最合适的模块和样式

### 配置文件位置

Brand Profile 文件位于：

- 全局配置：`~/.config/md2wechat/brand.md`
- 项目配置：`.brand.md`（项目根目录）

### 可配置项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| 品牌名称 | 品牌或个人名称 | 极客杰尼 |
| 品牌口号 | 一句话品牌定位 | 让复杂技术变得简单易懂 |
| 主色调 | 品牌主色 | #007bff（科技蓝） |
| 排版风格 | 偏好的排版风格 | tech-blog |
| 模块偏好 | 常用的模块组合 | hero + verdict + cta |
| 语言风格 | 内容调性 | 专业但不晦涩 |
| 禁忌事项 | 避免使用的元素 | 避免过度使用感叹号 |

### 使用方法

1. **自动读取**：AI 在排版时自动读取 Brand Profile 文件
2. **手动指定**：用户在对话中指定使用品牌配置
3. **创建配置**：AI 引导用户创建品牌配置文件

> 完整配置指南：[brand/brand-profile.md](brand/brand-profile.md)

---

## 排版输出关键约束

- **输出格式**：Markdown 文件，可直接复制到微信公众号编辑器
- **输出路径**：默认输出到用户原始文件同目录，文件名格式 `{原文件名}_formatted_{风格代号}.md`；若用户未指定输入文件路径，则输出到工作区根目录
- **代码块**：统一使用三反引号 + 语言标注；公众号不支持的语言高亮需配合 [references/wechat-markdown.md](references/wechat-markdown.md) 中的兼容方案
- **标题**：公众号最佳实践为二级标题 `##` 起步（`#` 与公众号标题重复），三级 `###` 用于小节
- **段落长度**：手机屏幕每段不超过 5 行，多分段、多留白
- **链接**：公众号不支持 Markdown 链接语法，排版时统一使用**脚注式链接**（文中用 `[N]` 标记，文末集中列出 URL），详见 [references/wechat-markdown.md](references/wechat-markdown.md) §1
- **图片**：使用 `![描述](url)` 占位，提示用户替换为实际图片
- **Emoji**：`casual-chat` 8-15 个，`cyber` 5-8 个，其他风格不超过 5 处
- **字号**：默认中等（15px）。用户可指定小号（13px）或大号（17px），在排版结果头部注明字号建议
- **字体样式**：粗体 `**重点**`、行内代码 `` `code` ``、引用 `>` 用于提示/注意
- **一键生成 HTML（推荐）**：阶段 5 使用 `scripts/md2wechat.py` 将 Markdown + CSS 合并为带内联样式的 HTML 文件，用户在浏览器中打开后点击「复制到公众号」按钮即可直接粘贴到微信编辑器。依赖：`pip install markdown beautifulsoup4`
- **渲染工具（备选）**：用户也可将 Markdown 通过 [mdnice](https://mdnice.com)、[135 编辑器](https://www.135editor.com) 或 [壹伴](https://yiban.io) 等工具应用 CSS 样式后复制到公众号编辑器。具体 CSS 参数和配色方案见 [references/wechat-markdown.md](references/wechat-markdown.md)「CSS 渲染参数参考」章节
- **现成 CSS 样式**：`styles/` 目录下为每种风格提供了可直接使用的完整 CSS 文件。阶段 5 自动读取对应 CSS；若使用 mdnice 手动方式，用户需将 CSS 粘贴到 mdnice「自定义主题」中

---

## 参考索引

| 文件 | 何时查阅 |
|------|---------|
| [templates/template-index.md](templates/template-index.md) | **阶段 2 强制读** — 风格选择 |
| [templates/tech-blog.md](templates/tech-blog.md) | 用户选择 `tech-blog` 风格时 |
| [templates/tutorial.md](templates/tutorial.md) | 用户选择 `tutorial` 风格时 |
| [templates/deep-dive.md](templates/deep-dive.md) | 用户选择 `deep-dive` 风格时 |
| [templates/casual-chat.md](templates/casual-chat.md) | 用户选择 `casual-chat` 风格时 |
| [templates/apple.md](templates/apple.md) | 用户选择 `apple` 风格时 |
| [templates/cyber.md](templates/cyber.md) | 用户选择 `cyber` 风格时 |
| [references/formatting-rules.md](references/formatting-rules.md) | **阶段 1 + 阶段 4** — 分析要素 + 质量校验 |
| [references/wechat-markdown.md](references/wechat-markdown.md) | **阶段 4** — 公众号兼容性校验 |
| [scripts/md2wechat.py](scripts/md2wechat.py) | **阶段 5** — Markdown → 可粘贴 HTML 转换脚本 |
| [styles/tech-blog.md](styles/tech-blog.md) | mdnice 自定义 CSS — 技术博客风格 |
| [styles/tutorial.md](styles/tutorial.md) | mdnice 自定义 CSS — 教程指南风格 |
| [styles/deep-dive.md](styles/deep-dive.md) | mdnice 自定义 CSS — 深度干货风格 |
| [styles/casual-chat.md](styles/casual-chat.md) | mdnice 自定义 CSS — 轻松聊天风格 |
| [styles/apple.md](styles/apple.md) | mdnice 自定义 CSS — 苹果风风格 |
| [styles/cyber.md](styles/cyber.md) | mdnice 自定义 CSS — 赛博朋克风格 |
| [knowledge/wechat-traps.md](knowledge/wechat-traps.md) | [按需] 阶段 3/4 — 公众号排版常见陷阱速查 |

> 每个子文件首部都有「何时阅读 / 覆盖范围 / 可跳过条件」摘要头，先读摘要再决定是否全文加载。

## 能力约束

始终可使用文件读取、代码搜索、终端命令等环境能力。若某项不可用，在输出中明确注明局限。

## 失败模式与 Fallback

| 触发条件 | 一线修复 | 仍失败兜底 |
|---------|----------|-----------|
| 用户输入文件路径不存在 | 提示用户重新提供正确路径，列出当前工作目录的可读 .md 文件 | 用户确认无文件后，接受用户直接粘贴文章文本作为输入 |
| 文章内容为空或字数 < 50 | 提示用户内容过短无法识别要素，要求补充 | 降级为通用 tech-blog 风格，仅做标题层级 + 中英文空格修正 |
| 阶段 1 无法识别主导内容类型 | 输出已识别要素让用户确认类型（🔴 CHECKPOINT） | 默认推荐 tech-blog（通用兜底风格），并在输出首行标注「已默认推荐 tech-blog，如需其他风格请说明」 |
| 用户在 🔴 CHECKPOINT 1 拒绝所有推荐风格 | 列出全部 6 种风格简介让用户二次选择 | 用户明确不选时终止流程，输出原文不做排版 |
| 阶段 3 所选风格模板文件读取失败 | 检测路径是否正确（`templates/{style}.md`），提示用户检查 skill 安装完整性 | 降级为 tech-blog 模板（最通用），并标注「模板加载失败，已降级」 |
| 阶段 4 校验发现公众号不兼容语法（如 Markdown 表格、`~~删除线~~`） | 按 [wechat-markdown.md](references/wechat-markdown.md) 替代方案自动转换 | 无法自动转换的语法加 `<!-- ⚠️ 需手动处理：具体说明 -->` 注释，在校验报告中列出 |
| 阶段 5 `md2wechat.py` 执行失败（如 pip 依赖缺失） | 提示用户安装依赖：`pip install markdown beautifulsoup4`，给出完整命令 | 跳过 HTML 生成，仅输出 Markdown 文件，提示用户使用 mdnice 等第三方工具手动转换 |
| CSS 样式文件（`styles/{style}.md`）提取失败 | 检测 styles 目录完整性，提示用户重新安装 skill | 输出无样式的纯 Markdown，标注「CSS 缺失，需手动应用样式」 |

---

## 反例与黑名单

> **设计依据**：基于 SkillLens 论文（arXiv 2605.23899）实证——只写"应该做 X"没有"不要做 Y"会导致 LLM judge 准确率下降。完整陷阱库见 [knowledge/wechat-traps.md](knowledge/wechat-traps.md)（阶段 4 强制校验时必读）。

### 排版反模式速查

| # | 反模式 | 为什么不要做 | 替代做法 |
|---|--------|------------|---------|
| 1 | 用 `[文字](url)` Markdown 直链 | 公众号不支持，复制后显示为纯文本 | 统一用脚注式：文中 `[N]`，文末集中列 URL |
| 2 | 用 `~~删除线~~` 语法 | 公众号渲染为双波浪号纯文本，不显示删除线 | 用「**已废弃**」「~~不推荐~~→直接说明」替代 |
| 3 | 用 Markdown 表格 | 公众号不支持渲染，复制后变纯文本乱码 | ≤3 列转列表；>3 列建议截图插入 |
| 4 | 用 `#` 一级标题 | 与公众号文章标题重复，显示双标题 | 正文从 `##` 二级标题起步 |
| 5 | 代码块超过 30 行 | 公众号约 50 行会截断，长代码阅读体验差 | 拆分为多块 + 说明，或提供 Gist 链接 |
| 6 | 中英文/数字之间无空格 | 视觉粘连，阅读体验差 | `Python3.11发布了` → `Python 3.11 发布了` |
| 7 | 非 `casual-chat` 风格 Emoji > 5 个 | 显得不专业，破坏风格一致性 | tech-blog/deep-dive ≤3，tutorial ≤5，仅 casual-chat 8-15 |
| 8 | 跳过 🔴 CHECKPOINT 1 自行决定风格 | 用户无法修改风格选择，违反用户确认原则 | 必须展示推荐 + 列出 6 种风格让用户确认 |

---

## 示例

输入示例 → 风格选择 → 输出示例，见 [examples/](examples/) 目录。
