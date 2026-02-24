"""
Typography 后处理：全角引号、CJK 间距。

在 normalize 返回前调用，提升公众号观感。跳过代码块、链接、图片。
"""

from __future__ import annotations

import re


def apply_typography(text: str) -> str:
    """对 Markdown 文本应用 typography 规则。

    规则：
    - 半角引号 "xxx" -> 全角「xxx」（跳过代码块、链接、图片）
    - CJK 与英文/数字之间加空格

    Args:
        text: 原始 Markdown 文本

    Returns:
        处理后的文本
    """
    if not text or not text.strip():
        return text

    # 1. 跳过代码块，只处理非代码部分
    parts = re.split(r"```[\s\S]*?```", text)
    result_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            result_parts.append(part)
        else:
            result_parts.append(_apply_to_plain_part(part))
    return "".join(result_parts)


def _apply_to_plain_part(text: str) -> str:
    """对非代码块部分应用 typography。"""
    lines = text.split("\n")
    out = []
    for line in lines:
        if "`" in line:
            out.append(line)
            continue
        if "![" in line or "](" in line:
            out.append(line)
            continue
        t = _apply_fullwidth_quotes(line)
        t = _apply_cjk_spacing(t)
        out.append(t)
    return "\n".join(out)


def _apply_fullwidth_quotes(line: str) -> str:
    """半角引号 "xxx" -> 全角「xxx」。"""
    def repl(m: re.Match) -> str:
        inner = m.group(1)
        if "「" in inner or "」" in inner:
            return m.group(0)
        return f"「{inner}」"

    return re.sub(r'"([^"]+)"', repl, line)


def _apply_cjk_spacing(line: str) -> str:
    """CJK 与英文/数字之间加空格。"""
    cjk = r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]"
    ascii_char = r"[A-Za-z0-9]"
    line = re.sub(rf"({cjk})({ascii_char})", r"\1 \2", line)
    line = re.sub(rf"({ascii_char})({cjk})", r"\1 \2", line)
    return line


__all__ = ["apply_typography"]
