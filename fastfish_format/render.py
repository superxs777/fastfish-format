"""
改写与排版：Markdown 转 HTML + 注入预设 CSS（Inline）。

提供多套预设样式（商务、极简、文艺、phycat 等），通过 format_style 参数切换。
支持 premailer 或简化版 CSS Inline。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import markdown

try:
    from premailer import Premailer
    PREMAILER_AVAILABLE = True
except ImportError:
    PREMAILER_AVAILABLE = False

logger = logging.getLogger(__name__)

_STYLE_BUSINESS = "business"
_STYLE_MINIMAL = "minimal"
_STYLE_LITERARY = "literary"
_DEFAULT_STYLE = _STYLE_MINIMAL

_PHYCAT_LIGHT_STYLES = [
    "phycat-cherry", "phycat-caramel", "phycat-forest", "phycat-mint",
    "phycat-sky", "phycat-prussian", "phycat-sakura", "phycat-mauve",
]
_PHYCAT_DARK_STYLES = ["phycat-vampire", "phycat-radiation", "phycat-abyss"]
_EXTRA_STYLES = ["orange-heart", "lapis", "rainbow"]

_SUPPORTED_STYLES = (
    [_STYLE_BUSINESS, _STYLE_MINIMAL, _STYLE_LITERARY] +
    _PHYCAT_LIGHT_STYLES + _PHYCAT_DARK_STYLES + _EXTRA_STYLES
)

_STYLE_LABELS: dict[str, str] = {
    "business": "商务", "minimal": "极简", "literary": "文艺",
    "phycat-cherry": "樱桃红", "phycat-caramel": "焦糖橙", "phycat-forest": "森绿",
    "phycat-mint": "薄荷青", "phycat-sky": "天蓝", "phycat-prussian": "普鲁士蓝",
    "phycat-sakura": "樱花粉", "phycat-mauve": "淡紫",
    "phycat-vampire": "吸血鬼", "phycat-radiation": "辐射", "phycat-abyss": "深渊",
    "orange-heart": "橙心", "lapis": "青玉", "rainbow": "彩虹",
}


def get_available_styles() -> list[dict[str, Any]]:
    """返回可用样式列表，供前端展示选择。"""
    return [
        {"index": i, "id": s, "label": _STYLE_LABELS.get(s, s)}
        for i, s in enumerate(_SUPPORTED_STYLES, start=1)
    ]


def _get_styles_dir() -> Path:
    """返回预设 CSS 文件所在目录（包内 assets）。"""
    return Path(__file__).resolve().parent / "assets" / "styles"


def _load_css(style_name: str) -> str:
    """加载指定样式的 CSS 文件内容。"""
    styles_dir = _get_styles_dir()
    if style_name.startswith("phycat-"):
        css_file = styles_dir / "phycat" / f"{style_name}.css"
    else:
        css_file = styles_dir / f"{style_name}.css"

    if not css_file.is_file():
        logger.warning(f"样式文件不存在: {css_file}")
        return ""

    try:
        css_content = css_file.read_text(encoding="utf-8")
        css_content = _resolve_css_variables(css_content)
        return css_content
    except Exception as e:
        logger.exception(f"读取样式文件失败: {css_file}, 错误: {e}")
        return ""


def _resolve_css_variables(css: str) -> str:
    """解析 :root 中的 CSS 变量，将 var(--name) 替换为实际值。"""
    if not css or ":root" not in css:
        return css
    root_match = re.search(r":root\s*\{([^}]+)\}", css, re.DOTALL)
    if not root_match:
        return css
    vars_map: dict[str, str] = {}
    for decl in root_match.group(1).split(";"):
        decl = decl.strip()
        if ":" in decl:
            key, _, val = decl.partition(":")
            key = key.strip()
            val = val.strip().rstrip(";").strip()
            if key.startswith("--"):
                vars_map[key] = val
    if not vars_map:
        return css
    result = css
    for var_name, var_val in vars_map.items():
        result = re.sub(rf"var\(\s*{re.escape(var_name)}\s*\)", var_val, result)
    result = re.sub(r":root\s*\{[^}]*\}\s*", "", result)
    return result


def _inline_css_premailer(html: str, css: str) -> str:
    """使用 premailer 库将 CSS 内联到 HTML。"""
    if not PREMAILER_AVAILABLE:
        return _inline_css_simple(html, css)
    if not css or not html:
        return html
    try:
        html_with_style = f"<style>{css}</style>{html}"
        p = Premailer(
            html_with_style,
            strip_important=False,
            keep_style_tags=False,
            disable_validation=True,
        )
        return p.transform()
    except Exception as e:
        logger.warning(f"premailer 处理失败，回退到简化版: {e}")
        return _inline_css_simple(html, css)


def _inline_css_simple(html: str, css: str) -> str:
    """简化版 CSS 内联，仅处理常见选择器。"""
    if not css or not html:
        return html
    css_rules: list[tuple[str, str]] = []
    for match in re.finditer(r"([^{]+)\{([^}]+)\}", css):
        selector = match.group(1).strip()
        declarations = match.group(2).strip()
        if selector and declarations:
            css_rules.append((selector, declarations))

    result = html
    for selector, declarations in css_rules:
        selector_clean = selector.strip()
        if selector_clean in ["h1", "h2", "h3", "blockquote", "img", "p", "ul", "ol", "li"]:
            tag_pattern = f"<{selector_clean}([^>]*?)>"

            def replace_tag(m: re.Match) -> str:
                attrs = m.group(1)
                existing = re.search(r'style=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
                if existing:
                    new_attrs = re.sub(
                        r'style=["\'][^"\']*["\']',
                        f'style="{existing.group(1)}; {declarations}"',
                        attrs, flags=re.IGNORECASE
                    )
                else:
                    new_attrs = f'{attrs} style="{declarations}"'
                return f"<{selector_clean}{new_attrs}>"

            result = re.sub(tag_pattern, replace_tag, result, flags=re.IGNORECASE)
    return result


def _normalize_markdown_newlines(text: str) -> str:
    """规范 Markdown 换行。"""
    if not text or not text.strip():
        return text
    t = text
    t = re.sub(r"([。！？])\s*>", r"\1\n\n>", t)
    t = re.sub(r"([：:])\s*-\s*", r"\1\n\n- ", t)
    t = re.sub(r"([。！？\s])\s*---\s+", r"\1\n\n---\n\n", t)
    return t


def render_markdown_to_html(
    markdown_text: str,
    format_style: str = _DEFAULT_STYLE,
    use_premailer: bool = True,
) -> str:
    """将 Markdown 渲染为 HTML，并注入预设 CSS（Inline）。"""
    if not markdown_text or not str(markdown_text).strip():
        return ""

    markdown_text = _normalize_markdown_newlines(markdown_text)

    if format_style not in _SUPPORTED_STYLES:
        logger.warning(f"不支持的样式 '{format_style}'，使用默认 '{_DEFAULT_STYLE}'")
        format_style = _DEFAULT_STYLE

    md = markdown.Markdown(extensions=["extra", "codehilite", "tables"])
    html = md.convert(markdown_text)

    css = _load_css(format_style)
    if css:
        html = _inline_css_premailer(html, css) if use_premailer and PREMAILER_AVAILABLE else _inline_css_simple(html, css)

    return html


def render_markdown_to_html_simple(
    markdown_text: str,
    format_style: str = _DEFAULT_STYLE,
) -> str:
    """简化版：仅 Markdown 转 HTML，不注入 CSS。"""
    if not markdown_text or not str(markdown_text).strip():
        return ""
    md = markdown.Markdown(extensions=["extra", "codehilite", "tables"])
    return md.convert(markdown_text)


__all__ = [
    "render_markdown_to_html",
    "render_markdown_to_html_simple",
    "get_available_styles",
    "_SUPPORTED_STYLES",
]
