"""
公众号渠道：文本规范化与 Markdown 渲染。
"""

from __future__ import annotations

from fastfish_format.template import normalize_to_wechat_format
from fastfish_format.render import render_markdown_to_html, get_available_styles


def normalize_wechat(text: str) -> tuple[str, str | None]:
    """将自由文本整理为公众号规范 Markdown。

    Returns:
        (content, title): content 为整理后的 Markdown；title 为 [主标题] 提取的标题
    """
    return normalize_to_wechat_format(text)


def format_wechat(
    markdown_text: str,
    format_style: str = "minimal",
    use_premailer: bool = True,
) -> str:
    """将 Markdown 渲染为公众号兼容的 HTML（含内联样式）。"""
    return render_markdown_to_html(
        markdown_text,
        format_style=format_style,
        use_premailer=use_premailer,
    )


def get_wechat_styles() -> list[dict]:
    """返回公众号可用样式列表。"""
    return get_available_styles()


__all__ = ["normalize_wechat", "format_wechat", "get_wechat_styles"]
