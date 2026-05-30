# 轻松聊天 (casual-chat) CSS 样式

**适用风格**：casual-chat（轻松聊天）
**推荐工具**：mdnice.com → 自定义主题 → 粘贴下方 CSS
**设计思路**：温暖、亲切、不拘束。橙色调为主，段落间距更大，阅读压力更低，像在和朋友聊天。

## 使用方法

1. 打开 [mdnice.com](https://mdnice.com)
2. 将你的 Markdown 文章粘贴到左侧编辑区
3. 点击「主题」→「自定义」→ 粘贴下方 CSS
4. 点击「复制」按钮，粘贴到公众号编辑器

## CSS 代码

```css
/* ============================================================
   轻松聊天风格 — casual-chat
   适配 mdnice 自定义主题
   ============================================================ */

/* --- 全局基础 --- */
#nice {
    font-family: -apple-system, "Noto Sans SC", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 15px;
    color: #3f3f3f;
    line-height: 1.85;
    letter-spacing: 0.8px;
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
    color: #d35400;
    margin-top: 32px;
    margin-bottom: 16px;
    padding: 8px 0;
    position: relative;
}

#nice h2::after {
    content: "";
    display: block;
    width: 40px;
    height: 3px;
    background: linear-gradient(90deg, #ff6600, #ff9966);
    border-radius: 2px;
    margin-top: 8px;
}

#nice h3 {
    font-size: 16px;
    font-weight: 600;
    color: #e67e22;
    margin-top: 24px;
    margin-bottom: 12px;
}

/* --- 段落 --- */
#nice p {
    margin-bottom: 18px;
    line-height: 1.9;
    text-align: justify;
}

/* --- 引用块 --- */
#nice blockquote {
    border-left: 3px solid #ff6600;
    background: #fff8f0;
    padding: 14px 18px;
    margin: 18px 0;
    border-radius: 0 8px 8px 0;
    font-size: 14px;
    color: #665544;
    line-height: 1.8;
}

#nice blockquote strong {
    color: #d35400;
}

/* --- 代码块 --- */
#nice pre {
    background: #2b2b3d;
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
    color: #f8f8f2;
    font-size: 13px;
}

/* --- 行内代码 --- */
#nice code {
    background: #fff3e6;
    color: #d35400;
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
    margin-bottom: 18px;
}

#nice li {
    margin-bottom: 8px;
    line-height: 1.85;
}

/* --- 粗体强调 --- */
#nice strong {
    color: #1a1a1a;
    font-weight: 600;
}

/* --- 链接 --- */
#nice a {
    color: #ff6600;
    text-decoration: none;
    border-bottom: 1px solid rgba(255, 102, 0, 0.3);
}

#nice a:hover {
    border-bottom-color: #ff6600;
}

/* --- 分割线（em dash 风格）--- */
#nice hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #ffd5b8, transparent);
    margin: 32px 0;
}

/* --- 图片 --- */
#nice img {
    max-width: 100%;
    border-radius: 8px;
    margin: 16px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
```
