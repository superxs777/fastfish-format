"""
fastfish-format: 多渠道格式化与美化。

支持公众号、小红书等渠道的文章排版、样式渲染、配图编排。
不包含发布功能，配图/生图通过编排 baoyu-skills 实现。
"""

from fastfish_format.template import normalize_to_wechat_format
from fastfish_format.typography import apply_typography
from fastfish_format.render import (
    render_markdown_to_html,
    render_markdown_to_html_simple,
    get_available_styles,
)
from fastfish_format.image_utils import compress_image_if_needed

__version__ = "0.1.0"
__all__ = [
    "normalize_to_wechat_format",
    "apply_typography",
    "render_markdown_to_html",
    "render_markdown_to_html_simple",
    "get_available_styles",
    "compress_image_if_needed",
]
