# 苹果风 (apple) CSS 样式

**适用风格**：apple（苹果风）
**推荐工具**：mdnice.com → 自定义主题 → 粘贴下方 CSS
**设计思路**：极简、优雅、留白克制。参考 Apple 官网设计语言，大量留白，字体层级清晰，无多余装饰，让内容本身成为焦点。

## 使用方法

1. 打开 [mdnice.com](https://mdnice.com)
2. 将你的 Markdown 文章粘贴到左侧编辑区
3. 点击「主题」→「自定义」→ 粘贴下方 CSS
4. 点击「复制」按钮，粘贴到公众号编辑器

## CSS 代码

```css
/* ============================================================
   苹果风风格 — apple
   适配 mdnice 自定义主题
   ============================================================ */

/* --- 全局基础 --- */
#nice {
    font-family: -apple-system, "Noto Sans SC", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 15px;
    color: #1d1d1f;
    line-height: 1.8;
    letter-spacing: 0.3px;
    padding: 0 16px;
    word-break: break-all;
}

/* --- 字号变体（用户可在 mdnice 中切换）--- */
/* 小号 */
#nice.style-small {
    font-size: 13px;
}

/* 中等（默认）*/
#nice.style-medium {
    font-size: 15px;
}

/* 大号 */
#nice.style-large {
    font-size: 17px;
}

/* --- 标题 --- */
#nice h2 {
    font-size: 20px;
    font-weight: 600;
    color: #1d1d1f;
    margin-top: 40px;
    margin-bottom: 20px;
    letter-spacing: -0.3px;
}

#nice h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1d1d1f;
    margin-top: 28px;
    margin-bottom: 14px;
}

/* --- 段落 --- */
#nice p {
    margin-bottom: 20px;
    line-height: 1.85;
    text-align: justify;
}

/* --- 引用块 --- */
#nice blockquote {
    border-left: none;
    background: #f5f5f7;
    padding: 20px 24px;
    margin: 24px 0;
    border-radius: 12px;
    font-size: 14px;
    color: #6e6e73;
    line-height: 1.8;
}

#nice blockquote strong {
    color: #1d1d1f;
}

/* --- 代码块 --- */
#nice pre {
    background: #fafafa;
    border: 1px solid #e8e8ed;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 20px 0;
    font-size: 13px;
    line-height: 1.7;
    overflow-x: auto;
}

#nice pre code {
    font-family: "SF Mono", "Fira Code", "JetBrains Mono",
                 "Source Code Pro", Consolas, monospace;
    color: #1d1d1f;
    font-size: 13px;
}

/* --- 行内代码 --- */
#nice code {
    background: #f0f0f5;
    color: #1d1d1f;
    padding: 2px 6px;
    border-radius: 4px;
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
    margin-bottom: 20px;
}

#nice li {
    margin-bottom: 8px;
    line-height: 1.8;
}

/* --- 粗体强调 --- */
#nice strong {
    color: #1d1d1f;
    font-weight: 600;
}

/* --- 链接 --- */
#nice a {
    color: #0071e3;
    text-decoration: none;
}

#nice a:hover {
    text-decoration: underline;
}

/* --- 分割线 --- */
#nice hr {
    border: none;
    height: 1px;
    background: #e8e8ed;
    margin: 40px 0;
}

/* --- 图片 --- */
#nice img {
    max-width: 100%;
    border-radius: 12px;
    margin: 20px 0;
}

/* --- 表格 --- */
#nice table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
}

#nice th {
    background: #f5f5f7;
    color: #1d1d1f;
    font-weight: 600;
    padding: 12px 16px;
    border: 1px solid #e8e8ed;
    text-align: left;
}

#nice td {
    padding: 10px 16px;
    border: 1px solid #e8e8ed;
    color: #6e6e73;
}
```
