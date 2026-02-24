"""
小红书渠道：文本规范化与 Markdown 渲染。

小红书内容特点：短句、emoji、话题标签、分段清晰、口语化。
"""

from __future__ import annotations

import re

from fastfish_format.typography import apply_typography
from fastfish_format.render import render_markdown_to_html, get_available_styles


def normalize_xhs(text: str) -> str:
    """将自由文本整理为小红书风格 Markdown。

    规则：
    - 短句分段（按句号、换行）
    - 话题标签规范化 #xxx#
    - 应用 typography（全角引号、CJK 间距）
    """
    if not text or not text.strip():
        return text

    t = text.strip()

    # 按句号、问号、感叹号分段
    t = re.sub(r"([。！？])\s*", r"\1\n\n", t)
    t = re.sub(r"\n\n+", "\n\n", t).strip()

    # 话题标签规范化：#话题# 或 # 话题 #
    t = re.sub(r"#\s*([^\s#]+)\s*#", r"#\1#", t)

    return apply_typography(t)


def format_xhs(
    markdown_text: str,
    format_style: str = "minimal",
    use_premailer: bool = True,
) -> str:
    """将 Markdown 渲染为 HTML（小红书可复用公众号样式，或后续扩展 XHS 专用样式）。"""
    return render_markdown_to_html(
        markdown_text,
        format_style=format_style,
        use_premailer=use_premailer,
    )


def get_xhs_styles() -> list[dict]:
    """返回小红书可用样式列表（与公众号共用样式库）。"""
    return get_available_styles()


__all__ = ["normalize_xhs", "format_xhs", "get_xhs_styles"]
