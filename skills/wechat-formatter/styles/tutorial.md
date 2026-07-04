# 教程指南 (tutorial) CSS 样式

**适用风格**：tutorial（教程指南）
**推荐工具**：mdnice.com → 自定义主题 → 粘贴下方 CSS
**设计思路**：清新、引导感强。绿色主色调，四种提示框各有独立配色，步骤感清晰。

## 使用方法

1. 打开 [mdnice.com](https://mdnice.com)
2. 将你的 Markdown 文章粘贴到左侧编辑区
3. 点击「主题」→「自定义」→ 粘贴下方 CSS
4. 点击「复制」按钮，粘贴到公众号编辑器

## CSS 代码

```css
/* ============================================================
   教程指南风格 — tutorial
   适配 mdnice 自定义主题
   ============================================================ */

/* --- 全局基础 --- */
#nice {
    font-family: -apple-system, "Noto Sans SC", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 15px;
    color: #3f3f3f;
    line-height: 1.75;
    letter-spacing: 0.5px;
    padding: 0 16px;
    word-break: break-all;
}

/* --- 字号变体 --- */
#nice.style-small {
    font-size: 13px;
}

#nice.style-medium {
    font-size: 15px;
}

#nice.style-large {
    font-size: 17px;
}

/* --- 标题 --- */
#nice h2 {
    font-size: 18px;
    font-weight: 700;
    color: #1a6e4e;
    margin-top: 32px;
    margin-bottom: 16px;
    padding: 10px 16px;
    background: linear-gradient(90deg, #e8f5e9 0%, transparent 100%);
    border-left: 4px solid #26a69a;
    border-radius: 0 4px 4px 0;
}

#nice h3 {
    font-size: 16px;
    font-weight: 600;
    color: #2e7d32;
    margin-top: 24px;
    margin-bottom: 12px;
    padding-left: 12px;
    border-left: 3px solid #81c784;
}

/* --- 段落 --- */
#nice p {
    margin-bottom: 16px;
    line-height: 1.8;
    text-align: justify;
}

/* --- 引用块：通用样式（TIP / 默认）--- */
#nice blockquote {
    border-left: 3px solid #26a69a;
    background: #f0faf5;
    padding: 14px 18px;
    margin: 16px 0;
    border-radius: 4px;
    font-size: 14px;
    color: #4a5568;
    line-height: 1.75;
}

#nice blockquote strong {
    color: #1a6e4e;
}

/* --- 代码块 --- */
#nice pre {
    background: #f4faf6;
    border: 1px solid #d4edda;
    border-radius: 6px;
    padding: 16px;
    margin: 16px 0;
    font-size: 13px;
    line-height: 1.6;
    overflow-x: auto;
}

#nice pre code {
    font-family: "SF Mono", "Fira Code", "JetBrains Mono",
                 "Source Code Pro", Consolas, monospace;
    color: #24292e;
    font-size: 13px;
}

/* --- 行内代码 --- */
#nice code {
    background: #e8f5e9;
    color: #1a6e4e;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.9em;
    font-family: "SF Mono", "Fira Code", Consolas, monospace;
}

#nice pre code {
    background: transparent;
    padding: 0;
    border-radius: 0;
    color: inherit;
}

/* --- 列表 --- */
#nice ul,
#nice ol {
    padding-left: 24px;
    margin-bottom: 16px;
}

#nice li {
    margin-bottom: 6px;
    line-height: 1.75;
}

/* --- 粗体强调 --- */
#nice strong {
    color: #1a1a1a;
    font-weight: 600;
}

/* --- 链接 --- */
#nice a {
    color: #26a69a;
    text-decoration: none;
    border-bottom: 1px solid rgba(38, 166, 154, 0.3);
}

#nice a:hover {
    border-bottom-color: #26a69a;
}

/* --- 分割线 --- */
#nice hr {
    border: none;
    border-top: 1px solid #d4edda;
    margin: 28px 0;
}

/* --- 图片 --- */
#nice img {
    max-width: 100%;
    border-radius: 4px;
    margin: 12px 0;
}

/* --- 复选框列表（教程专用）--- */
#nice li input[type="checkbox"] {
    margin-right: 6px;
    accent-color: #26a69a;
}
```
