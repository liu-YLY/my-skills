# 深度干货 (deep-dive) CSS 样式

**适用风格**：deep-dive（深度干货）
**推荐工具**：mdnice.com → 自定义主题 → 粘贴下方 CSS
**设计思路**：沉稳、学术、信息密度高。深蓝主色调，引用块强化「核心结论」的视觉冲击力，代码块更精致。

## 使用方法

1. 打开 [mdnice.com](https://mdnice.com)
2. 将你的 Markdown 文章粘贴到左侧编辑区
3. 点击「主题」→「自定义」→ 粘贴下方 CSS
4. 点击「复制」按钮，粘贴到公众号编辑器

## CSS 代码

```css
/* ============================================================
   深度干货风格 — deep-dive
   适配 mdnice 自定义主题
   ============================================================ */

/* --- 全局基础 --- */
#nice {
    font-family: -apple-system, "Noto Sans SC", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 15px;
    color: #3f3f3f;
    line-height: 1.8;
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
    color: #1a1a1a;
    margin-top: 36px;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #2b5797;
    position: relative;
}

#nice h2::before {
    content: "";
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 40px;
    height: 2px;
    background: #42b983;
}

#nice h3 {
    font-size: 16px;
    font-weight: 600;
    color: #2b5797;
    margin-top: 28px;
    margin-bottom: 12px;
    padding-left: 14px;
    border-left: 3px solid #42b983;
}

/* --- 段落 --- */
#nice p {
    margin-bottom: 16px;
    line-height: 1.85;
    text-align: justify;
}

/* --- 引用块：核心结论（加粗标签）--- */
#nice blockquote {
    border-left: 3px solid #42b983;
    background: linear-gradient(135deg, #f0faf5 0%, #f8f9ff 100%);
    padding: 16px 20px;
    margin: 18px 0;
    border-radius: 0 6px 6px 0;
    font-size: 14px;
    color: #4a5568;
    line-height: 1.8;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

#nice blockquote strong {
    color: #2b5797;
}

/* --- 代码块 --- */
#nice pre {
    background: #1e1e2e;
    border-radius: 8px;
    padding: 18px 20px;
    margin: 18px 0;
    font-size: 13px;
    line-height: 1.65;
    overflow-x: auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

#nice pre code {
    font-family: "SF Mono", "Fira Code", "JetBrains Mono",
                 "Source Code Pro", Consolas, monospace;
    color: #cdd6f4;
    font-size: 13px;
}

/* --- 行内代码 --- */
#nice code {
    background: #eef1f5;
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
    margin-bottom: 8px;
    line-height: 1.8;
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
    margin: 32px 0;
    position: relative;
}

#nice hr::after {
    content: "· · ·";
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: #ffffff;
    padding: 0 12px;
    color: #b2b2b2;
    font-size: 14px;
    letter-spacing: 4px;
}

/* --- 图片 --- */
#nice img {
    max-width: 100%;
    border-radius: 6px;
    margin: 16px 0;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

/* --- 表格（如有）--- */
#nice table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 14px;
}

#nice th {
    background: #f0f4fa;
    color: #2b5797;
    font-weight: 600;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    text-align: left;
}

#nice td {
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    color: #4a5568;
}
```
