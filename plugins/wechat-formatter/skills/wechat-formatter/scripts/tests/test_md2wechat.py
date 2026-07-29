"""md2wechat.py 转换脚本单元测试。

覆盖范围：
- CSS 提取（从 .md 文件的 ```css 代码块）
- CSS 规则解析（选择器 + 属性字典，保持顺序）
- Markdown → HTML 转换（含 HTML 注释剥离）
- CSS 内联化（已存在 style 合并、顺序优先）
- 微信不支持 CSS 属性过滤（UNSUPPORTED_PROPS + UNSUPPORTED_VALUE_KEYWORDS）
- 标题提取 / 风格名推断
- 完整 convert() 流程：输出命名、文件生成
- HTML 结构校验：可复制容器存在、工具栏样式不污染正文
- 无效路径处理（CLI 入口退出码）
- 六种风格 fixture 回归

约束：所有输出写入 pytest 的 tmp_path，不向 skill 目录写文件。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# ─── 加载被测模块（scripts/md2wechat.py 不在包路径下，需按文件路径加载）─────
SCRIPT_PATH = Path(__file__).resolve().parent.parent / 'md2wechat.py'
spec = importlib.util.spec_from_file_location('md2wechat', SCRIPT_PATH)
assert spec is not None and spec.loader is not None
md2wechat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(md2wechat)


# ─── 公共 fixture ───────────────────────────────────────────────────────────

MINIMAL_MD = """# 测试文章标题

## 第一节

这是一段正文，包含 `inline code` 与 **加粗**。

- 列表项 1
- 列表项 2

```python
print("hello")
```
"""

MINIMAL_CSS_TEMPLATE = """# {title} CSS 样式

**适用风格**：{stem}

```css
#nice {{
    font-size: 15px;
    color: #333;
    line-height: 1.75;
}}

#nice h2 {{
    font-size: 18px;
    font-weight: 700;
    /* 微信不支持：text-shadow */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}}

#nice p {{
    margin: 16px 0;
}}
```
"""

SIX_STYLES = ['tech-blog', 'tutorial', 'deep-dive', 'casual-chat', 'apple', 'cyber']


def _write_style_file(target_dir: Path, stem: str) -> Path:
    """在 target_dir 下生成最小化的 styles/{stem}.md fixture。"""
    style_path = target_dir / f'{stem}.md'
    style_path.write_text(
        MINIMAL_CSS_TEMPLATE.format(title=stem, stem=stem),
        encoding='utf-8',
    )
    return style_path


def _write_markdown(target_dir: Path, name: str = 'sample') -> Path:
    md_path = target_dir / f'{name}.md'
    md_path.write_text(MINIMAL_MD, encoding='utf-8')
    return md_path


# ─── 1. extract_css_from_md ────────────────────────────────────────────────

class TestExtractCssFromMd:
    def test_extract_from_fenced_block(self, tmp_path):
        style_file = _write_style_file(tmp_path, 'tech-blog')
        css = md2wechat.extract_css_from_md(str(style_file))
        assert '#nice' in css
        assert 'font-size: 15px' in css
        assert '```' not in css  # 代码围栏本身不应出现

    def test_returns_empty_when_no_css_block(self, tmp_path, capsys):
        no_css = tmp_path / 'no-css.md'
        no_css.write_text('# 仅有文字\n\n没有 css 代码块', encoding='utf-8')
        css = md2wechat.extract_css_from_md(str(no_css))
        assert css == ''
        captured = capsys.readouterr()
        assert '未找到 CSS' in captured.err

    def test_extracts_only_first_block(self, tmp_path):
        multi = tmp_path / 'multi.md'
        multi.write_text(
            '```css\n#first { color: red; }\n```\n\n文字\n\n```css\n#second { color: blue; }\n```',
            encoding='utf-8',
        )
        css = md2wechat.extract_css_from_md(str(multi))
        assert '#first' in css
        assert '#second' not in css


# ─── 2. parse_css_rules ────────────────────────────────────────────────────

class TestParseCssRules:
    def test_basic_rule_set(self):
        css = '#nice { color: #333; font-size: 15px; }'
        rules = md2wechat.parse_css_rules(css)
        assert len(rules) == 1
        selector, props = rules[0]
        assert selector == '#nice'
        assert props['color'] == '#333'
        assert props['font-size'] == '15px'

    def test_comma_separated_selectors(self):
        css = '#nice ul, #nice ol { margin: 0; }'
        rules = md2wechat.parse_css_rules(css)
        assert len(rules) == 2
        assert rules[0][0] == '#nice ul'
        assert rules[1][0] == '#nice ol'
        assert rules[0][1]['margin'] == '0'

    def test_strips_comments(self):
        css = '/* 注释 */ #nice { color: red; /* 行内注释 */ padding: 4px; }'
        rules = md2wechat.parse_css_rules(css)
        assert len(rules) == 1
        props = rules[0][1]
        assert props == {'color': 'red', 'padding': '4px'}

    def test_skips_pseudo_class_only_selectors(self):
        css = ':hover { color: red; } #nice { color: blue; }'
        rules = md2wechat.parse_css_rules(css)
        selectors = [r[0] for r in rules]
        assert ':hover' not in selectors
        assert '#nice' in selectors

    def test_preserves_order(self):
        css = '#a { x: 1; } #b { y: 2; } #c { z: 3; }'
        rules = md2wechat.parse_css_rules(css)
        assert [r[0] for r in rules] == ['#a', '#b', '#c']


# ─── 3. md_to_html ─────────────────────────────────────────────────────────

class TestMdToHtml:
    def test_basic_conversion(self):
        html = md2wechat.md_to_html('# 标题\n\n正文')
        assert '<h1>标题</h1>' in html
        assert '<p>正文</p>' in html

    def test_strips_leading_html_comment(self):
        md = '<!-- 这是头部注释 -->\n# 标题\n\n正文'
        html = md2wechat.md_to_html(md)
        assert '<!--' not in html
        assert '<h1>标题</h1>' in html

    def test_fenced_code_block(self):
        md = '```python\nprint(1)\n```'
        html = md2wechat.md_to_html(md)
        assert '<code' in html
        assert 'print(1)' in html

    def test_table_extension(self):
        md = '| a | b |\n|---|---|\n| 1 | 2 |'
        html = md2wechat.md_to_html(md)
        assert '<table>' in html
        assert '<th>a</th>' in html


# ─── 4. apply_inline_styles ────────────────────────────────────────────────

class TestApplyInlineStyles:
    def test_wraps_in_nice_div_default_size(self):
        html = md2wechat.md_to_html('# 标题\n\n正文')
        out, _ = md2wechat.apply_inline_styles(html, [], 'medium')
        assert 'id="nice"' in out

    def test_size_class_added_when_not_medium(self):
        html = '<p>x</p>'
        out_small, _ = md2wechat.apply_inline_styles(html, [], 'small')
        out_large, _ = md2wechat.apply_inline_styles(html, [], 'large')
        assert 'style-small' in out_small
        assert 'style-large' in out_large

    def test_no_size_class_for_medium(self):
        html = '<p>x</p>'
        out, _ = md2wechat.apply_inline_styles(html, [], 'medium')
        assert 'style-medium' not in out

    def test_applies_rule_to_element(self):
        html = '<p>hello</p>'
        rules = [('p', {'color': 'red'})]
        out, _ = md2wechat.apply_inline_styles(html, rules, 'medium')
        assert 'color: red' in out

    def test_merges_existing_inline_style(self):
        html = '<p style="margin: 4px;">hello</p>'
        rules = [('p', {'color': 'red'})]
        out, _ = md2wechat.apply_inline_styles(html, rules, 'medium')
        assert 'color: red' in out
        assert 'margin: 4px' in out

    def test_new_rule_overrides_existing_same_property(self):
        html = '<p style="color: blue;">hello</p>'
        rules = [('p', {'color': 'red'})]
        out, _ = md2wechat.apply_inline_styles(html, rules, 'medium')
        # 合并后 red 覆盖 blue（dict 合并语义）
        assert 'color: red' in out
        assert 'color: blue' not in out

    def test_filters_unsupported_property(self):
        html = '<p>x</p>'
        rules = [('p', {'text-shadow': '1px 1px 2px black', 'color': 'red'})]
        out, filtered = md2wechat.apply_inline_styles(html, rules, 'medium')
        assert filtered == 1
        assert 'text-shadow' not in out
        assert 'color: red' in out

    def test_filters_unsupported_value_keyword(self):
        html = '<p>x</p>'
        rules = [('p', {'background': 'linear-gradient(#fff, #000)'})]
        out, filtered = md2wechat.apply_inline_styles(html, rules, 'medium')
        assert filtered == 1
        assert 'linear-gradient' not in out

    def test_invalid_selector_skipped(self):
        html = '<p>x</p>'
        # BeautifulSoup 对 >>> 等非法选择器会抛异常，函数应捕获后 continue
        rules = [('>>>invalid', {'color': 'red'}), ('p', {'color': 'blue'})]
        out, _ = md2wechat.apply_inline_styles(html, rules, 'medium')
        assert 'color: blue' in out


# ─── 5. 标题与风格名 ────────────────────────────────────────────────────────

class TestTitleAndStyleName:
    def test_extract_title_from_h1(self):
        assert md2wechat.extract_title('# 我的标题') == '我的标题'

    def test_extract_title_default_when_missing(self):
        assert md2wechat.extract_title('只有正文') == '未命名文章'

    def test_extract_title_takes_first_h1(self):
        md = '# 第一\n\n正文\n\n# 第二'
        assert md2wechat.extract_title(md) == '第一'

    @pytest.mark.parametrize('stem,expected', [
        ('tech-blog', '技术博客'),
        ('tutorial', '教程指南'),
        ('deep-dive', '深度干货'),
        ('casual-chat', '轻松聊天'),
        ('apple', '苹果风'),
        ('cyber', '赛博朋克'),
    ])
    def test_detect_style_name_for_six_styles(self, stem, expected, tmp_path):
        style_path = tmp_path / f'{stem}.md'
        assert md2wechat.detect_style_name(str(style_path)) == expected

    def test_detect_style_name_fallback_to_stem(self, tmp_path):
        unknown = tmp_path / 'custom-style.md'
        assert md2wechat.detect_style_name(str(unknown)) == 'custom-style'


# ─── 6. convert() 主流程 ───────────────────────────────────────────────────

class TestConvertFlow:
    def test_generates_wechat_html_with_expected_name(self, tmp_path):
        md_path = _write_markdown(tmp_path, 'article')
        style_path = _write_style_file(tmp_path, 'tech-blog')
        out_path = md2wechat.convert(str(md_path), str(style_path), 'medium')
        out_file = Path(out_path)
        assert out_file.name == 'article_wechat.html'
        assert out_file.parent == tmp_path  # 写入输入文件同目录，未污染 skill 目录

    def test_output_contains_copyable_container(self, tmp_path):
        md_path = _write_markdown(tmp_path, 'article')
        style_path = _write_style_file(tmp_path, 'tech-blog')
        out_path = md2wechat.convert(str(md_path), str(style_path))
        html = Path(out_path).read_text(encoding='utf-8')
        # 必须存在 id="content" 的可复制容器（HTML_TEMPLATE 中定义）
        assert 'id="content"' in html
        # 必须存在「复制到公众号」按钮
        assert '复制到公众号' in html
        # 正文 h1 / p 应被内联样式包装
        assert 'id="nice"' in html

    def test_output_excludes_toolbar_styles_from_body(self, tmp_path):
        """正文不应携带工具栏样式（.toolbar 的 sticky / btn 的 transition 等）。"""
        md_path = _write_markdown(tmp_path, 'article')
        style_path = _write_style_file(tmp_path, 'tech-blog')
        out_path = md2wechat.convert(str(md_path), str(style_path))
        html = Path(out_path).read_text(encoding='utf-8')

        # 提取 id="content" 容器内部
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.select_one('#content')
        assert content is not None
        content_html = str(content)
        # 工具栏类名不应出现在正文容器内
        assert 'class="toolbar' not in content_html
        assert 'class="btn' not in content_html
        # 微信不支持属性不应被内联到正文
        assert 'text-shadow' not in content_html
        assert 'box-shadow' not in content_html

    def test_filtered_count_emitted_to_stderr_for_cyber(self, tmp_path, capsys):
        # cyber 风格 fixture 含 text-shadow，应触发警告
        md_path = _write_markdown(tmp_path, 'cyber-article')
        style_path = tmp_path / 'cyber.md'
        style_path.write_text(
            MINIMAL_CSS_TEMPLATE.format(title='cyber', stem='cyber'),
            encoding='utf-8',
        )
        md2wechat.convert(str(md_path), str(style_path))
        captured = capsys.readouterr()
        assert '已过滤' in captured.err
        assert 'cyber' in captured.err  # 额外提示出现

    def test_size_variant_propagated_to_wrapper(self, tmp_path):
        md_path = _write_markdown(tmp_path, 'article')
        style_path = _write_style_file(tmp_path, 'tech-blog')
        out_path = md2wechat.convert(str(md_path), str(style_path), 'large')
        html = Path(out_path).read_text(encoding='utf-8')
        assert 'style-large' in html


# ─── 7. 六种风格回归 ───────────────────────────────────────────────────────

@pytest.mark.parametrize('style_stem', SIX_STYLES)
def test_six_styles_regression(style_stem, tmp_path):
    """每种风格至少一条回归：转换成功 + 输出存在 + 容器结构正确。"""
    md_path = _write_markdown(tmp_path, f'{style_stem}-sample')
    style_path = _write_style_file(tmp_path, style_stem)

    out_path = md2wechat.convert(str(md_path), str(style_path), 'medium')
    out_file = Path(out_path)
    assert out_file.exists()
    assert out_file.name == f'{style_stem}-sample_wechat.html'

    html = out_file.read_text(encoding='utf-8')
    assert 'id="content"' in html
    assert 'id="nice"' in html
    # 风格标签出现
    expected_name = md2wechat.STYLE_NAMES[style_stem]
    assert expected_name in html


# ─── 8. CLI 无效路径 ───────────────────────────────────────────────────────

class TestCliInvalidPaths:
    def _run_main(self, argv, capsys):
        old_argv = sys.argv
        sys.argv = argv
        try:
            md2wechat.main()
        except SystemExit as e:
            return e.code
        finally:
            sys.argv = old_argv
        return 0

    def test_missing_markdown_file_exits_nonzero(self, tmp_path, capsys):
        style_path = _write_style_file(tmp_path, 'tech-blog')
        code = self._run_main(
            ['md2wechat.py', str(tmp_path / 'no-such.md'), str(style_path)],
            capsys,
        )
        assert code == 1
        assert '文件不存在' in capsys.readouterr().err

    def test_missing_style_file_exits_nonzero(self, tmp_path, capsys):
        md_path = _write_markdown(tmp_path, 'article')
        code = self._run_main(
            ['md2wechat.py', str(md_path), str(tmp_path / 'no-such.md')],
            capsys,
        )
        assert code == 1
        assert '文件不存在' in capsys.readouterr().err

    def test_style_without_css_block_exits_nonzero(self, tmp_path, capsys):
        md_path = _write_markdown(tmp_path, 'article')
        bad_style = tmp_path / 'no-css.md'
        bad_style.write_text('# 仅有文字', encoding='utf-8')
        code = self._run_main(
            ['md2wechat.py', str(md_path), str(bad_style)],
            capsys,
        )
        assert code == 1
        err = capsys.readouterr().err
        assert '未能提取到 CSS' in err
