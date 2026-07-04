# 技术博客 (tech-blog) CSS 样式

**适用风格**：tech-blog（技术博客）
**推荐工具**：mdnice.com → 自定义主题 → 粘贴下方 CSS
**设计思路**：专业、干净、克制。深蓝主色调，强调代码可读性和信息层级。

## 使用方法

1. 打开 [mdnice.com](https://mdnice.com)
2. 将你的 Markdown 文章粘贴到左侧编辑区
3. 点击「主题」→「自定义」→ 粘贴下方 CSS
4. 点击「复制」按钮，粘贴到公众号编辑器

## CSS 代码

```css
/* ============================================================
   技术博客风格 — tech-blog
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
    color: #2b5797;
    margin-top: 32px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e8edf3;
    text-align: left;
}

#nice h3 {
    font-size: 16px;
    font-weight: 600;
    color: #333333;
    margin-top: 24px;
    margin-bottom: 12px;
    padding-left: 12px;
    border-left: 3px solid #2b5797;
}

/* --- 段落 --- */
#nice p {
    margin-bottom: 16px;
    line-height: 1.8;
    text-align: justify;
}

/* --- 引用块（核心观点 / 注意）--- */
#nice blockquote {
    border-left: 3px solid #2b5797;
    background: #f0f4fa;
    padding: 14px 18px;
    margin: 16px 0;
    border-radius: 4px;
    font-size: 14px;
    color: #4a5568;
    line-height: 1.75;
}

#nice blockquote strong {
    color: #2b5797;
}

/* --- 代码块 --- */
#nice pre {
    background: #f6f8fa;
    border: 1px solid #e2e8f0;
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
    background: #eff1f3;
    color: #2b5797;
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
    color: #2b5797;
    text-decoration: none;
    border-bottom: 1px solid rgba(43, 87, 151, 0.3);
}

#nice a:hover {
    border-bottom-color: #2b5797;
}

/* --- 分割线 --- */
#nice hr {
    border: none;
    border-top: 1px solid #e8edf3;
    margin: 28px 0;
}

/* --- 图片 --- */
#nice img {
    max-width: 100%;
    border-radius: 4px;
    margin: 12px 0;
}
```
