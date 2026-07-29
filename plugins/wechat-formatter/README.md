# WeChat Formatter Plugin

> 微信公众号排版 plugin，针对互联网 / 技术领域文章提供 6 种专业排版风格、高级排版模块与一键 HTML 生成能力。
>
> 自动分析文章内容（编程知识、测试理论、架构设计、技术分享等），匹配最佳风格，输出可直接复制到公众号编辑器的格式化 Markdown / HTML。

## 版本

**当前版本**：v2.0.0（plugin manifest）

## 能力概览

| 能力 | 说明 |
|---|---|
| **内容分析** | 自动识别文章要素：标题层级、代码块、列表、要点 |
| **风格匹配** | 6 种专业风格，自动推荐 2-3 种最合适的风格供用户选择 |
| **排版执行** | 严格按模板规则转换，确保格式一致性 |
| **质量校验** | 覆盖度 + 可读性 + 公众号兼容性三项检查 |
| **HTML 生成** | 一键生成带内联样式与"复制"按钮的 HTML，可直接粘贴到公众号 |
| **高级排版模块** | `:::module` 语法创建专业视觉卡片组件 |
| **品牌配置** | 支持自定义品牌色、Logo、品牌语调 |

## 六大排版风格

| 风格 | 代号 | 适用场景 | 核心视觉特征 |
|---|---|---|---|
| 技术博客 | `tech-blog` | 编程教程、技术分享、工具介绍 | 导读框 + 中文编号章节 + 核心观点框 + 分割线 + 脚注式参考 |
| 教程指南 | `tutorial` | 操作指南、最佳实践、配置说明 | 目标框 + Step 五段式 + 4 种提示框 + FAQ |
| 深度干货 | `deep-dive` | 原理剖析、架构分析、技术复盘 | 摘要框 + 纯文本目录 + 核心结论框 + 图表编号 + 参考带说明 |
| 轻松聊天 | `casual-chat` | 经验总结、技术随笔、行业思考 | 自然开场 + 短段落 + `—` 分隔 + Emoji 点缀 + 互动引导 |
| 苹果风 | `apple` | 产品设计、架构哲学、技术选型 | 极简留白 + 圆角卡片引用 + 无编号无 Emoji + Apple 品牌色 |
| 赛博朋克 | `cyber` | 安全技术、前沿探索、极客文化 | 暗黑背景 + 霓虹色调 + 发光代码块 + 系统弹窗风格引用 |

## 工作流（五阶段）

```
阶段 1 分析内容 → 🔴 CHECKPOINT 阶段 2 匹配风格 → 阶段 3 执行排版
                → 🔴 CHECKPOINT 阶段 4 输出校验 → 阶段 5 生成可粘贴 HTML（可选）
```

详细指令见 [skills/wechat-formatter/SKILL.md](skills/wechat-formatter/SKILL.md)。

## 多 runtime 适配

| Runtime | manifest 位置 | 安装命令 |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` | `/plugin install wechat-formatter@my-skill-marketplace` |
| Cursor | `.cursor-plugin/plugin.json` | 通过 npx skills add 或手动复制 |
| Codex | `.codex-plugin/plugin.json` | 通过 npx skills add 或手动复制 |

## 目录结构

```
wechat-formatter/
├── .claude-plugin/plugin.json        # Claude Code plugin manifest
├── .cursor-plugin/plugin.json        # Cursor plugin manifest
├── .codex-plugin/plugin.json         # Codex plugin manifest
├── README.md                         # 本文件
└── skills/
    └── wechat-formatter/             # 排版 skill v3.0.0
        ├── SKILL.md                  # 入口 + 五阶段流程
        ├── README.md                 # skill 说明
        ├── test-prompts.json
        ├── brand/                    # 品牌配置
        │   └── brand-profile.md
        ├── templates/                # 6 种风格模板 + template-index
        ├── styles/                   # CSS 样式（apple/casual-chat/cyber 等 6 套）
        ├── references/               # 排版规则 + wechat-markdown
        ├── examples/                 # 示例输入输出
        ├── knowledge/                # wechat-traps.md
        ├── layout/                   # 高级排版模块 + modules-base.css
        └── scripts/                  # md2wechat.py（HTML 生成器）
```

## 使用示例

```
用户：帮我把这篇技术文章排版成 tech-blog 风格
[粘贴文章内容]

AI（wechat-formatter）：
## 阶段 1: 内容分析
[识别文章要素...]

## 阶段 2: 风格推荐
推荐：tech-blog（技术博客风格）
[🔴 CHECKPOINT 用户确认后继续]
```

## 相关文档

- 根目录 [README.md](../../README.md) — 项目总览与安装方式
- [skills/wechat-formatter/SKILL.md](skills/wechat-formatter/SKILL.md) — skill 入口
- [skills/wechat-formatter/templates/template-index.md](skills/wechat-formatter/templates/template-index.md) — 风格模板索引
- [skills/wechat-formatter/references/formatting-rules.md](skills/wechat-formatter/references/formatting-rules.md) — 排版规则
