"""
图片压缩工具。

在格式化/上传流程中可选压缩大图，减小存储与传输体积。
"""

from __future__ import annotations

import io


def compress_image_if_needed(
    content: bytes,
    ext: str,
    threshold_bytes: int = 512_000,
    quality: int = 85,
) -> bytes:
    """对大图进行可选压缩。

    仅当 content 长度 > threshold_bytes 时压缩。
    支持 jpg/jpeg/png/webp；gif 不压缩（保留动图）。

    Args:
        content: 原始图片字节
        ext: 扩展名，如 .jpg .png
        threshold_bytes: 超过此大小才压缩，默认 500KB
        quality: JPEG/WebP 质量 1-100，默认 85

    Returns:
        压缩后的字节，或原 content（未压缩时）
    """
    if len(content) <= threshold_bytes:
        return content
    ext_lower = ext.lower().lstrip(".")
    if ext_lower in ("gif",):
        return content
    try:
        from PIL import Image
    except ImportError:
        return content

    try:
        img = Image.open(io.BytesIO(content))
        if ext_lower in ("jpg", "jpeg"):
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            out = io.BytesIO()
            img.save(out, "JPEG", quality=quality, optimize=True)
            return out.getvalue()
        if ext_lower == "webp":
            out = io.BytesIO()
            save_kw = {"quality": quality, "method": 6}
            if img.mode == "RGBA":
                save_kw["lossless"] = False
            img.save(out, "WEBP", **save_kw)
            return out.getvalue()
        if ext_lower == "png":
            out = io.BytesIO()
            img.save(out, "PNG", optimize=True)
            return out.getvalue()
    except Exception:
        pass
    return content


__all__ = ["compress_image_if_needed"]
