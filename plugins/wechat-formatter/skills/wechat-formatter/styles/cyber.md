# 赛博朋克 (cyber) CSS 样式

**适用风格**：cyber（赛博朋克）
**推荐工具**：mdnice.com → 自定义主题 → 粘贴下方 CSS
**设计思路**：暗黑、霓虹、未来感。深色背景搭配荧光色点缀，代码块发光效果，整体呈现赛博朋克美学。适合前沿技术、黑客文化、极客风格的文章。

## 使用方法

1. 打开 [mdnice.com](https://mdnice.com)
2. 将你的 Markdown 文章粘贴到左侧编辑区
3. 点击「主题」→「自定义」→ 粘贴下方 CSS
4. 点击「复制」按钮，粘贴到公众号编辑器

## CSS 代码

```css
/* ============================================================
   赛博朋克风格 — cyber
   适配 mdnice 自定义主题
   ============================================================ */

/* --- 全局基础 --- */
#nice {
    font-family: -apple-system, "Noto Sans SC", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 15px;
    color: #c0c0c0;
    line-height: 1.8;
    letter-spacing: 0.5px;
    padding: 0 16px;
    word-break: break-all;
    background: #0a0a0f;
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
    color: #00f0ff;
    margin-top: 36px;
    margin-bottom: 16px;
    padding: 10px 16px;
    background: linear-gradient(90deg, rgba(0, 240, 255, 0.08) 0%, transparent 100%);
    border-left: 3px solid #00f0ff;
    border-radius: 0 4px 4px 0;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
}

#nice h3 {
    font-size: 16px;
    font-weight: 600;
    color: #ff00ff;
    margin-top: 28px;
    margin-bottom: 12px;
    padding-left: 14px;
    border-left: 2px solid #ff00ff;
}

/* --- 段落 --- */
#nice p {
    margin-bottom: 16px;
    line-height: 1.85;
    text-align: justify;
}

/* --- 引用块 --- */
#nice blockquote {
    border-left: 3px solid #ff00ff;
    background: rgba(255, 0, 255, 0.05);
    padding: 16px 20px;
    margin: 18px 0;
    border-radius: 0 8px 8px 0;
    font-size: 14px;
    color: #a0a0b0;
    line-height: 1.8;
    box-shadow: inset 0 0 20px rgba(255, 0, 255, 0.03);
}

#nice blockquote strong {
    color: #00f0ff;
    text-shadow: 0 0 6px rgba(0, 240, 255, 0.2);
}

/* --- 代码块 --- */
#nice pre {
    background: #0d0d14;
    border: 1px solid rgba(0, 240, 255, 0.15);
    border-radius: 8px;
    padding: 18px 20px;
    margin: 18px 0;
    font-size: 13px;
    line-height: 1.65;
    overflow-x: auto;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.05),
                inset 0 0 30px rgba(0, 0, 0, 0.3);
}

#nice pre code {
    font-family: "SF Mono", "Fira Code", "JetBrains Mono",
                 "Source Code Pro", Consolas, monospace;
    color: #00ff88;
    font-size: 13px;
}

/* --- 行内代码 --- */
#nice code {
    background: rgba(0, 240, 255, 0.08);
    color: #00f0ff;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.9em;
    font-family: "SF Mono", "Fira Code", Consolas, monospace;
    border: 1px solid rgba(0, 240, 255, 0.12);
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
    margin-bottom: 8px;
    line-height: 1.8;
}

/* --- 粗体强调 --- */
#nice strong {
    color: #ffffff;
    font-weight: 600;
}

/* --- 链接 --- */
#nice a {
    color: #00f0ff;
    text-decoration: none;
    border-bottom: 1px solid rgba(0, 240, 255, 0.3);
    transition: all 0.2s ease;
}

#nice a:hover {
    border-bottom-color: #00f0ff;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
}

/* --- 分割线 --- */
#nice hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00f0ff, #ff00ff, transparent);
    margin: 36px 0;
    opacity: 0.5;
}

/* --- 图片 --- */
#nice img {
    max-width: 100%;
    border-radius: 6px;
    margin: 16px 0;
    border: 1px solid rgba(0, 240, 255, 0.1);
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.05);
}

/* --- 表格 --- */
#nice table {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 14px;
}

#nice th {
    background: rgba(0, 240, 255, 0.08);
    color: #00f0ff;
    font-weight: 600;
    padding: 12px 16px;
    border: 1px solid rgba(0, 240, 255, 0.15);
    text-align: left;
}

#nice td {
    padding: 10px 16px;
    border: 1px solid rgba(0, 240, 255, 0.08);
    color: #a0a0b0;
}
```
