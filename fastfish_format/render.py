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
_LEGACY_GROUPING_STYLES = {
    _STYLE_BUSINESS,
    _STYLE_MINIMAL,
    _STYLE_LITERARY,
    "orange-heart",
    "lapis",
    "rainbow",
    "phycat-cherry",
    "phycat-caramel",
    "phycat-forest",
    "phycat-mint",
    "phycat-sky",
    "phycat-prussian",
    "phycat-sakura",
    "phycat-mauve",
    "phycat-vampire",
    "phycat-radiation",
    "phycat-abyss",
}

# OpenClaw 选择样式时按“颜值优先”排序展示（总计 30 套）
_SUPPORTED_STYLES = [
    "mweb-bear-default",
    "phycat-sakura",
    "phycat-cherry",
    "phycat-mauve",
    "phycat-caramel",
    "mweb-duotone-light",
    "rainbow",
    "lapis",
    "mweb-smartblue",
    "mweb-solarized-light",
    "phycat-sky",
    "phycat-mint",
    "phycat-forest",
    "orange-heart",
    "mweb-duotone-heat",
    "mweb-ayu",
    "mweb-indigo",
    "mweb-lark",
    "mweb-typo",
    "mweb-v-green",
    "mweb-red-graphite",
    "mweb-gandalf",
    "phycat-prussian",
    _STYLE_LITERARY,
    _STYLE_BUSINESS,
    "mweb-contrast",
    _STYLE_MINIMAL,
    "phycat-vampire",
    "phycat-radiation",
    "phycat-abyss",
]

_STYLE_LABELS: dict[str, str] = {
    "business": "商务", "minimal": "极简", "literary": "文艺",
    "phycat-cherry": "樱桃红", "phycat-caramel": "焦糖橙", "phycat-forest": "森绿",
    "phycat-mint": "薄荷青", "phycat-sky": "天蓝", "phycat-prussian": "普鲁士蓝",
    "phycat-sakura": "樱花粉", "phycat-mauve": "淡紫",
    "phycat-vampire": "吸血鬼", "phycat-radiation": "辐射", "phycat-abyss": "深渊",
    "orange-heart": "橙心", "lapis": "青玉", "rainbow": "彩虹",
    "mweb-typo": "Typo 阅读",
    "mweb-lark": "Lark 文档",
    "mweb-indigo": "Indigo 资讯",
    "mweb-smartblue": "SmartBlue 清爽",
    "mweb-contrast": "Contrast 高对比",
    "mweb-duotone-light": "Duotone Light",
    "mweb-duotone-heat": "Duotone Heat",
    "mweb-bear-default": "Bear 柔和",
    "mweb-gandalf": "Gandalf 专栏",
    "mweb-solarized-light": "Solarized Light",
    "mweb-red-graphite": "Red Graphite",
    "mweb-v-green": "V Green",
    "mweb-ayu": "Ayu 现代",
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


def _strip_style_props(style_value: str, remove_props: set[str]) -> str:
    """从 style 字符串中移除指定样式属性。"""
    kept: list[str] = []
    for decl in style_value.split(";"):
        decl = decl.strip()
        if not decl or ":" not in decl:
            continue
        key, _, value = decl.partition(":")
        key = key.strip().lower()
        if key in remove_props:
            continue
        kept.append(f"{key}: {value.strip()}")
    return "; ".join(kept)


def _extract_style_property(opening_tag: str, prop_name: str) -> str:
    """从 opening tag 的 style 属性中提取某个样式值。"""
    style_match = re.search(r'style=["\']([^"\']*)["\']', opening_tag, re.IGNORECASE)
    if not style_match:
        return ""
    style_value = style_match.group(1)
    prop_pattern = rf"{re.escape(prop_name)}\s*:\s*([^;]+)"
    match = re.search(prop_pattern, style_value, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _sanitize_group_children(group_html: str) -> str:
    """去掉组内段落自身底色/边框，避免出现“每段单独一个框”效果。"""
    remove_props = {
        "background",
        "background-color",
        "border",
        "border-top",
        "border-right",
        "border-bottom",
        "border-left",
        "border-radius",
        "padding",
        "box-shadow",
    }

    def _rewrite_opening_tag(match: re.Match) -> str:
        tag = match.group(1)
        attrs = match.group(2) or ""
        attrs = re.sub(r'\s*bgcolor=["\'][^"\']*["\']', "", attrs, flags=re.IGNORECASE)
        style_match = re.search(r'style=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        if style_match:
            cleaned_style = _strip_style_props(style_match.group(1), remove_props)
            if cleaned_style:
                attrs = re.sub(
                    r'style=["\'][^"\']*["\']',
                    f'style="{cleaned_style}"',
                    attrs,
                    flags=re.IGNORECASE,
                )
            else:
                attrs = re.sub(r'\s*style=["\'][^"\']*["\']', "", attrs, flags=re.IGNORECASE)
        return f"<{tag}{attrs}>"

    return re.sub(r"<(p|ul|ol|table)\b([^>]*)>", _rewrite_opening_tag, group_html, flags=re.IGNORECASE)


def _upsert_style_property(opening_tag: str, prop_name: str, prop_value: str) -> str:
    """在 opening tag 上新增或更新 style 属性。"""
    prop_name = prop_name.strip().lower()
    style_match = re.search(r'\sstyle=["\']([^"\']*)["\']', opening_tag, re.IGNORECASE)
    if style_match:
        style_value = style_match.group(1)
        cleaned_style = _strip_style_props(style_value, {prop_name})
        merged = f"{cleaned_style}; {prop_name}: {prop_value}" if cleaned_style else f"{prop_name}: {prop_value}"
        return re.sub(
            r'\sstyle=["\'][^"\']*["\']',
            f' style="{merged}"',
            opening_tag,
            flags=re.IGNORECASE,
        )
    return opening_tag[:-1] + f' style="{prop_name}: {prop_value}">'


def _set_group_edge_margins(group_html: str) -> str:
    """将分组内首尾内容块贴合容器边缘，避免视觉断层。"""
    block_pattern = re.compile(r"<(?:p|ul|ol|table)\b[^>]*>", re.IGNORECASE)
    matches = list(block_pattern.finditer(group_html))
    if not matches:
        return group_html

    first = matches[0]
    last = matches[-1]
    replace_map: dict[int, tuple[int, str]] = {}

    first_tag = group_html[first.start():first.end()]
    first_tag = _upsert_style_property(first_tag, "margin-top", "0")

    if first.start() == last.start():
        first_tag = _upsert_style_property(first_tag, "margin-bottom", "0")
        replace_map[first.start()] = (first.end(), first_tag)
    else:
        last_tag = group_html[last.start():last.end()]
        last_tag = _upsert_style_property(last_tag, "margin-bottom", "0")
        replace_map[first.start()] = (first.end(), first_tag)
        replace_map[last.start()] = (last.end(), last_tag)

    result = group_html
    for start in sorted(replace_map.keys(), reverse=True):
        end, new_tag = replace_map[start]
        result = result[:start] + new_tag + result[end:]
    return result


def _wrap_group_blocks(group_html: str) -> str:
    """将连续段落块包裹成一个分组容器。"""
    first_block_match = re.search(r"<(p|ul|ol|table)\b[^>]*>", group_html, re.IGNORECASE)
    opening_tag = first_block_match.group(0) if first_block_match else ""

    group_bg = _extract_style_property(opening_tag, "background-color") or "#fcfcfc"
    group_border = _extract_style_property(opening_tag, "border") or "1px solid #e5e7eb"
    group_radius = _extract_style_property(opening_tag, "border-radius") or "4px"
    group_padding = _extract_style_property(opening_tag, "padding") or "12px 16px"

    cleaned_group = _sanitize_group_children(group_html)
    cleaned_group = _set_group_edge_margins(cleaned_group)
    return (
        f'<div class="ff-section-group" '
        f'style="margin: 12px 0; padding: {group_padding}; '
        f'background-color: {group_bg}; border: {group_border}; border-radius: {group_radius};">'
        f"{cleaned_group}</div>"
    )


def _group_section_content(section_html: str) -> str:
    """按连续正文块分组，生成 section 容器。"""
    block_pattern = re.compile(
        r"(?is)<(?:p|ul|ol|table)\b[^>]*>.*?</(?:p|ul|ol|table)>"
    )
    matches = list(block_pattern.finditer(section_html))
    if not matches:
        return section_html

    result_parts: list[str] = []
    cursor = 0
    current_group: list[str] = []

    def _flush_group() -> None:
        nonlocal current_group
        if current_group:
            result_parts.append(_wrap_group_blocks("".join(current_group)))
            current_group = []

    for match in matches:
        between = section_html[cursor:match.start()]
        block = match.group(0)
        if current_group:
            if between.strip():
                _flush_group()
                result_parts.append(between)
                current_group.append(block)
            else:
                current_group.append(between)
                current_group.append(block)
        else:
            if between.strip():
                result_parts.append(between)
                current_group.append(block)
            else:
                current_group.append(between)
                current_group.append(block)
        cursor = match.end()

    tail = section_html[cursor:]
    if current_group and not tail.strip():
        current_group.append(tail)
        tail = ""
    _flush_group()
    if tail:
        result_parts.append(tail)
    return "".join(result_parts)


def _apply_legacy_section_grouping(html: str, format_style: str) -> str:
    """旧样式（尤其 phycat）按 h3 对正文分组，解决每段单独框问题。"""
    if format_style not in _LEGACY_GROUPING_STYLES or "<h3" not in html:
        return html

    h3_pattern = re.compile(r"(?is)<h3\b[^>]*>.*?</h3>")
    heading_pattern = re.compile(r"(?is)<h[1-3]\b[^>]*>.*?</h[1-3]>")
    h3_matches = list(h3_pattern.finditer(html))
    if not h3_matches:
        return html

    result_parts: list[str] = []
    cursor = 0

    for h3_match in h3_matches:
        if h3_match.start() < cursor:
            continue
        result_parts.append(html[cursor:h3_match.end()])
        section_start = h3_match.end()
        next_heading = heading_pattern.search(html, section_start)
        section_end = next_heading.start() if next_heading else len(html)
        section_html = html[section_start:section_end]
        result_parts.append(_group_section_content(section_html))
        cursor = section_end

    result_parts.append(html[cursor:])
    return "".join(result_parts)


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
    html = _apply_legacy_section_grouping(html, format_style)

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
