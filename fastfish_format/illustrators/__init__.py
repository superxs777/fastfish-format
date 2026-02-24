"""
配图/生图编排层：对接 baoyu-skills 的流程说明与指引。

本模块不直接调用 AI，由 Agent 按 SKILL.md 执行 baoyu-skills。
"""

from fastfish_format.illustrators.workflow import (
    get_illustration_workflow,
    get_cover_workflow,
    get_xhs_images_workflow,
)

__all__ = [
    "get_illustration_workflow",
    "get_cover_workflow",
    "get_xhs_images_workflow",
]
