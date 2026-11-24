#!/usr/bin/env python3
"""Generate an offline review page using the maintained interactive template."""
import argparse
import copy
import html
import json
import os
import re
import sys
import tempfile
from pathlib import Path

from check_review_map import load_data, validate, with_layout

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "swimlane-review.html"
DATA_BLOCK = re.compile(r'(<script\b[^>]*\bid=["\']review-data["\'][^>]*>)(.*?)(</script>)', re.S)


def prepare(data):
    if not isinstance(data, dict):
        raise ValueError("生成器需要评审 JSON 对象")
    result = with_layout(copy.deepcopy(data))
    for key in ("title", "intro", "scope"):
        if not isinstance(result.get(key), str) or not result[key].strip():
            raise ValueError(f"缺少页面 {key}")
    defaults = {
        "context": "测试评审", "status": "评审稿 · 未执行", "provenance": "",
        "aliases": {}, "sources": [], "orphan_cases": [],
        "source": "", "sourceLabel": "原始材料", "peer": "", "peerLabel": "相关页面",
        "md": "", "mdLabel": "Markdown",
    }
    for key, value in defaults.items():
        result.setdefault(key, value)
    if "ticket" in result:
        ticket = result["ticket"]
        if not isinstance(ticket, list) or len(ticket) != 4 or not all(isinstance(s, str) for s in ticket):
            raise ValueError("ticket 应为四段文字")
    if not isinstance(result["aliases"], dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in result["aliases"].items()):
        raise ValueError("aliases 应为旧目标到新目标的字符串映射")
    for key in ("context", "status", "provenance", "source", "sourceLabel", "peer", "peerLabel", "md", "mdLabel"):
        if not isinstance(result[key], str):
            raise ValueError(f"{key} 应为字符串")
    # Reject active URI schemes; relative paths and ordinary source links remain usable.
    for key in ("source", "peer", "md"):
        scheme = re.match(r'^\s*([^/:?#]+):', result[key])
        if scheme and scheme[1].lower() not in ("http", "https", "file"):
            raise ValueError(f"{key} 的链接协议不支持")
    return result


def render(data):
    prepared = prepare(data)
    gaps = validate(prepared, quiet=True)
    prepared["coverage_gaps"] = gaps
    template = TEMPLATE.read_text(encoding="utf-8")
    if len(DATA_BLOCK.findall(template)) != 1:
        raise ValueError("内置样板的数据区不唯一")
    payload = json.dumps(prepared, ensure_ascii=False, indent=2, allow_nan=False).replace("<", "\\u003c")
    content = DATA_BLOCK.sub(lambda m: m[1] + payload + m[3], template)
    content = re.sub(r"<title>.*?</title>", lambda m: "<title>" + html.escape(prepared["title"]) + "</title>", content, count=1, flags=re.S)
    return content, gaps


def write_atomic(output, content):
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent, prefix="."+output.name+".", delete=False) as stream:
            temp_path = Path(stream.name)
            stream.write(content)
        if output.exists():
            os.chmod(temp_path, output.stat().st_mode & 0o777)
        os.replace(temp_path, output)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="review.json；也支持迁移旧样板 HTML")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve() or args.output.resolve() == TEMPLATE.resolve():
            raise ValueError("请使用独立输出路径，保留输入和内置样板")
        data = load_data(args.input)
        content, gaps = render(data)
        write_atomic(args.output, content)
        count = sum(len(p["cases"]) for p in data["points"]) + len(data.get("orphan_cases", []))
        print(f"已生成 {args.output}；{count} 条用例记录，{len(gaps)} 项设计缺口。")
    except (ValueError, OSError, TypeError, KeyError) as error:
        print("生成失败：" + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
