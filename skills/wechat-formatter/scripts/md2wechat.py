#!/usr/bin/env python3
"""
md2wechat.py — 将格式化 Markdown 转为可直接粘贴到微信公众号的带内联样式 HTML。

用法:
    python md2wechat.py <markdown_file> <style_file> [--size small|medium|large]

输出:
    {markdown_file}_wechat.html — 带"复制到公众号"按钮的 HTML 文件

依赖:
    pip install markdown beautifulsoup4
"""

import argparse
import re
import sys
from pathlib import Path

import markdown
from bs4 import BeautifulSoup


# ─── 微信不支持的 CSS 属性 ────────────────────────────────────────────────

UNSUPPORTED_PROPS = frozenset({
    'text-shadow', 'box-shadow', 'transition', 'animation',
    'animation-name', 'animation-duration', 'animation-timing-function',
    'animation-delay', 'animation-iteration-count', 'animation-direction',
    'animation-fill-mode', 'animation-play-state',
    'transform', 'filter', 'backdrop-filter',
    ':hover', ':focus', ':active', ':before', ':after',
})

UNSUPPORTED_VALUE_KEYWORDS = ['linear-gradient', 'radial-gradient', 'text-shadow', 'box-shadow']


# ─── Step 1: 从样式 .md 文件提取 CSS ─────────────────────────────────────

def extract_css_from_md(file_path: str) -> str:
    """从 Markdown 文件的 ```css 代码块中提取 CSS。"""
    content = Path(file_path).read_text(encoding='utf-8')
    match = re.search(r'```css\s*\n(.*?)```', content, re.DOTALL)
    if not match:
        print(f"警告: 在 {file_path} 中未找到 CSS 代码块", file=sys.stderr)
        return ''
    return match.group(1)


# ─── Step 2: 解析 CSS 规则 ───────────────────────────────────────────────

def parse_css_rules(css_text: str) -> list[tuple[str, dict[str, str]]]:
    """将 CSS 文本解析为 (选择器, {属性: 值}) 元组列表，保持顺序。"""
    # 移除注释
    css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)

    rules = []
    for match in re.finditer(r'([^{}]+)\{([^{}]+)\}', css_text):
        selectors_str = match.group(1).strip()
        body = match.group(2).strip()

        # 解析属性
        props: dict[str, str] = {}
        for prop_match in re.finditer(r'([\w-]+)\s*:\s*([^;]+);?', body):
            key = prop_match.group(1).strip()
            value = prop_match.group(2).strip()
            # 跳过伪类选择器（如 :hover 写在属性位置的情况）
            if key.startswith(':'):
                continue
            props[key] = value

        # 处理逗号分隔的选择器 (#nice ul, #nice ol)
        for selector in selectors_str.split(','):
            sel = selector.strip()
            if sel and not sel.startswith(':'):
                rules.append((sel, props))

    return rules


# ─── Step 3: Markdown → HTML ──────────────────────────────────────────────

def md_to_html(md_text: str) -> str:
    """将 Markdown 转为 HTML。"""
    # 移除文件头部的 HTML 注释
    md_text = re.sub(r'^<!--.*?-->\s*', '', md_text, flags=re.DOTALL)
    return markdown.markdown(md_text, extensions=[
        'fenced_code',
        'tables',
        'sane_lists',
        'smarty',
    ])


# ─── Step 4 & 5: CSS 内联化 ──────────────────────────────────────────────

def parse_inline_style(style_str: str) -> dict[str, str]:
    """解析已有的 inline style 字符串为字典。"""
    props = {}
    if not style_str:
        return props
    for part in style_str.split(';'):
        part = part.strip()
        if ':' in part:
            key, value = part.split(':', 1)
            props[key.strip()] = value.strip()
    return props


def style_dict_to_str(props: dict[str, str]) -> str:
    """将属性字典转为 CSS style 字符串。"""
    return '; '.join(f'{k}: {v}' for k, v in props.items())


def apply_inline_styles(html: str, rules: list[tuple[str, dict[str, str]]],
                        size: str) -> tuple[str, int]:
    """将 CSS 规则内联到 HTML 元素上。返回 (HTML, 被过滤的属性数)。"""
    soup = BeautifulSoup(html, 'html.parser')

    # 包裹在 <div id="nice"> 中
    wrapper = soup.new_tag('div', id='nice')
    if size != 'medium':
        wrapper['class'] = f'style-{size}'
    for child in list(soup.contents):
        wrapper.append(child)
    soup.append(wrapper)

    filtered_count = 0

    for selector, props in rules:
        try:
            elements = soup.select(selector)
        except Exception:
            continue

        for el in elements:
            existing = parse_inline_style(el.get('style', ''))
            # 合并：新规则覆盖已有属性（CSS 顺序优先）
            merged = {**existing, **props}

            # 过滤微信不支持的属性
            filtered = {}
            for key, value in merged.items():
                if key.lower() in UNSUPPORTED_PROPS:
                    filtered_count += 1
                    continue
                if any(kw in value.lower() for kw in UNSUPPORTED_VALUE_KEYWORDS):
                    filtered_count += 1
                    continue
                filtered[key] = value

            el['style'] = style_dict_to_str(filtered)

    return str(soup), filtered_count


# ─── Step 7: 生成带"复制"按钮的 HTML ─────────────────────────────────────

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 微信公众号排版</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
                background: #f0f0f0; }}
        .toolbar {{
            position: sticky; top: 0; z-index: 100;
            background: #fff; border-bottom: 1px solid #e0e0e0;
            padding: 10px 20px; display: flex; align-items: center; gap: 12px;
        }}
        .toolbar .btn {{
            padding: 8px 24px; background: #07c160; color: #fff;
            border: none; border-radius: 6px; cursor: pointer;
            font-size: 15px; font-weight: 500;
            transition: background 0.2s;
        }}
        .toolbar .btn:hover {{ background: #06ad56; }}
        .toolbar .btn:active {{ background: #059a4b; }}
        .toolbar .hint {{ color: #999; font-size: 13px; }}
        .toolbar .style-tag {{
            padding: 2px 8px; background: #f0f0f0; border-radius: 4px;
            font-size: 12px; color: #666;
        }}
        .preview-wrapper {{
            max-width: 700px; margin: 20px auto; padding: 0 16px;
        }}
        .preview {{
            background: #fff; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
    </style>
</head>
<body>
    <div class="toolbar">
        <button class="btn" onclick="copyContent()">复制到公众号</button>
        <span class="hint">点击按钮后，打开微信公众号编辑器，Ctrl+V 粘贴</span>
        <span class="style-tag">{style_name}</span>
    </div>
    <div class="preview-wrapper">
        <div class="preview" id="content">{html_content}</div>
    </div>
    <script>
        function copyContent() {{
            var content = document.getElementById('content');
            var range = document.createRange();
            range.selectNodeContents(content);
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            try {{
                document.execCommand('copy');
                alert('已复制！请打开微信公众号编辑器，Ctrl+V 粘贴');
            }} catch(e) {{
                alert('复制失败，请手动选中内容后 Ctrl+C 复制');
            }}
            selection.removeAllRanges();
        }}
    </script>
</body>
</html>'''


def extract_title(md_text: str) -> str:
    """从 Markdown 中提取标题（第一个 # 行）。"""
    match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    return match.group(1).strip() if match else '未命名文章'


STYLE_NAMES = {
    'tech-blog': '技术博客',
    'tutorial': '教程指南',
    'deep-dive': '深度干货',
    'casual-chat': '轻松聊天',
    'apple': '苹果风',
    'cyber': '赛博朋克',
}


def detect_style_name(style_path: str) -> str:
    """从样式文件路径推断风格名称。"""
    stem = Path(style_path).stem
    return STYLE_NAMES.get(stem, stem)


# ─── 主流程 ───────────────────────────────────────────────────────────────

def convert(md_path: str, style_path: str, size: str = 'medium') -> str:
    """执行完整转换流程，返回输出文件路径。"""
    # 读取输入
    md_text = Path(md_path).read_text(encoding='utf-8')
    css_text = extract_css_from_md(style_path)

    if not css_text:
        print("错误: 未能提取到 CSS，请检查样式文件格式", file=sys.stderr)
        sys.exit(1)

    # 解析
    rules = parse_css_rules(css_text)
    title = extract_title(md_text)
    style_name = detect_style_name(style_path)

    # Markdown → HTML
    html_body = md_to_html(md_text)

    # CSS 内联化 + 微信兼容性过滤
    html_inlined, filtered_count = apply_inline_styles(html_body, rules, size)

    if filtered_count > 0:
        print(f"警告: 已过滤 {filtered_count} 个微信不支持的 CSS 属性", file=sys.stderr)
        if 'cyber' in style_path.lower():
            print("提示: cyber 风格使用了较多高级 CSS 特性，粘贴到公众号后视觉效果会有降级", file=sys.stderr)

    # 生成最终 HTML
    final_html = HTML_TEMPLATE.format(
        title=title,
        style_name=style_name,
        html_content=html_inlined,
    )

    # 写入文件
    stem = Path(md_path).stem
    out_dir = Path(md_path).parent
    out_path = out_dir / f'{stem}_wechat.html'
    out_path.write_text(final_html, encoding='utf-8')

    return str(out_path)


def main():
    parser = argparse.ArgumentParser(
        description='将格式化 Markdown 转为可直接粘贴到微信公众号的 HTML'
    )
    parser.add_argument('markdown_file', help='格式化后的 Markdown 文件路径')
    parser.add_argument('style_file', help='CSS 样式文件路径（styles/*.md）')
    parser.add_argument('--size', choices=['small', 'medium', 'large'],
                        default='medium', help='字号大小（默认: medium）')

    args = parser.parse_args()

    # 校验文件存在
    if not Path(args.markdown_file).exists():
        print(f"错误: 文件不存在 — {args.markdown_file}", file=sys.stderr)
        sys.exit(1)
    if not Path(args.style_file).exists():
        print(f"错误: 文件不存在 — {args.style_file}", file=sys.stderr)
        sys.exit(1)

    out_path = convert(args.markdown_file, args.style_file, args.size)
    print(f"已生成: {out_path}")
    print(f"请在浏览器中打开该文件，点击「复制到公众号」按钮即可粘贴到微信编辑器")


if __name__ == '__main__':
    main()
