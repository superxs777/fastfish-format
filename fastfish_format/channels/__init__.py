"""
渠道适配：公众号、小红书等不同平台的格式化规则。
"""

from fastfish_format.channels.wechat import normalize_wechat, format_wechat
from fastfish_format.channels.xhs import normalize_xhs, format_xhs

__all__ = [
    "normalize_wechat",
    "format_wechat",
    "normalize_xhs",
    "format_xhs",
]
