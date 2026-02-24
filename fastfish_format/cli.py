"""
命令行入口。用法：python -m fastfish_format.cli <command> [args]
或安装后：ffformat <command> [args]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_normalize_wechat(args: argparse.Namespace) -> int:
    """公众号文本规范化。"""
    from fastfish_format.template import normalize_to_wechat_format

    content = _read_content(args)
    if content is None:
        return 1
    result, title = normalize_to_wechat_format(content)
    out = {"ok": True, "content": result, "title": title}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_normalize_xhs(args: argparse.Namespace) -> int:
    """小红书文本规范化。"""
    from fastfish_format.channels.xhs import normalize_xhs

    content = _read_content(args)
    if content is None:
        return 1
    result = normalize_xhs(content)
    out = {"ok": True, "content": result}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    """Markdown 转 HTML。"""
    from fastfish_format.render import render_markdown_to_html

    content = _read_content(args)
    if content is None:
        return 1
    html = render_markdown_to_html(content, format_style=args.format_style or "minimal")
    out = {"ok": True, "html": html, "format_style": args.format_style or "minimal"}
    print(json.dumps(out, ensure_ascii=False))
    return 0


def cmd_styles(args: argparse.Namespace) -> int:
    """列出可用样式。"""
    from fastfish_format.render import get_available_styles

    styles = get_available_styles()
    out = {"ok": True, "styles": styles}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_workflows(args: argparse.Namespace) -> int:
    """列出配图流程指引。"""
    from fastfish_format.illustrators.workflow import get_all_workflows

    workflows = get_all_workflows()
    out = {"ok": True, "workflows": workflows}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def _read_content(args: argparse.Namespace) -> str | None:
    """从 --content、--content-file 或 stdin 读取内容。"""
    if args.content_file:
        p = Path(args.content_file)
        if not p.is_file():
            print(f"Error: 文件不存在 {p}", file=sys.stderr)
            return None
        return p.read_text(encoding="utf-8")
    if getattr(args, "content", None):
        return args.content
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("Error: 请提供 --content、--content-file 或通过 stdin 传入内容", file=sys.stderr)
    return None


def _run_from_json(json_str: str) -> int:
    """从 --json 参数解析并执行（OpenClaw 兼容）。"""
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"JSON 解析失败: {e}"}, ensure_ascii=False), file=sys.stderr)
        return 1
    cmd = data.get("command")
    if not cmd:
        print(json.dumps({"ok": False, "error": "缺少 command 字段"}, ensure_ascii=False), file=sys.stderr)
        return 1

    class JsonArgs:
        pass

    args = JsonArgs()
    args.content_file = data.get("content_file")
    args.content = data.get("content")
    args.format_style = data.get("format_style", "minimal")

    if cmd == "normalize-wechat":
        return cmd_normalize_wechat(args)
    if cmd == "normalize-xhs":
        return cmd_normalize_xhs(args)
    if cmd == "render":
        return cmd_render(args)
    if cmd == "styles":
        return cmd_styles(args)
    if cmd == "workflows":
        return cmd_workflows(args)

    print(json.dumps({"ok": False, "error": f"未知命令: {cmd}"}, ensure_ascii=False), file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--json":
        return _run_from_json(sys.argv[2])

    parser = argparse.ArgumentParser(description="fastfish-format CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("normalize-wechat", help="公众号文本规范化")
    p1.add_argument("--content", "-c", help="内容文本")
    p1.add_argument("--content-file", "-f", help="内容文件路径")
    p1.set_defaults(func=cmd_normalize_wechat)

    p2 = sub.add_parser("normalize-xhs", help="小红书文本规范化")
    p2.add_argument("--content", "-c", help="内容文本")
    p2.add_argument("--content-file", "-f", help="内容文件路径")
    p2.set_defaults(func=cmd_normalize_xhs)

    p3 = sub.add_parser("render", help="Markdown 转 HTML")
    p3.add_argument("--content", "-c", help="Markdown 内容")
    p3.add_argument("--content-file", "-f", help="Markdown 文件路径")
    p3.add_argument("--format-style", "-s", default="minimal", help="样式名称")
    p3.set_defaults(func=cmd_render)

    p4 = sub.add_parser("styles", help="列出可用样式")
    p4.set_defaults(func=cmd_styles)

    p5 = sub.add_parser("workflows", help="列出配图流程指引")
    p5.set_defaults(func=cmd_workflows)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
