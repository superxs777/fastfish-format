"""
配图/生图编排流程：提供 baoyu-skills 调用指引。

采用方式 C（Skill 编排层）：fastfish-format 定义流程，Agent 按 SKILL.md 调用 baoyu-skills。
配图/生图需配置至少一个图像生成 API：OPENAI_API_KEY / GOOGLE_API_KEY / DASHSCOPE_API_KEY。
"""

from __future__ import annotations

from typing import Any


def get_illustration_workflow() -> dict[str, Any]:
    """文章配图流程指引（对应 baoyu-article-illustrator）。

    Returns:
        流程说明，供 Agent 或文档使用
    """
    return {
        "skill": "baoyu-article-illustrator",
        "description": "分析文章结构，确定配图位置，生成插图（Type × Style）",
        "trigger": ["为文章配图", "add images", "generate images for article"],
        "prerequisites": [
            "安装 baoyu-article-illustrator",
            "安装 baoyu-image-gen",
            "配置 OPENAI_API_KEY 或 GOOGLE_API_KEY 或 DASHSCOPE_API_KEY",
        ],
        "steps": [
            "1. 分析文章内容，识别配图位置",
            "2. 确认 Type（infographic/scene/flowchart 等）和 Style",
            "3. 生成 outline.md 和 prompts/NN-{type}-{slug}.md",
            "4. 调用 baoyu-image-gen 生成图片",
            "5. 将 ![description](path/NN-{type}-{slug}.png) 插入文章",
        ],
        "repo": "https://github.com/JimLiu/baoyu-skills/tree/main/skills/baoyu-article-illustrator",
    }


def get_cover_workflow() -> dict[str, Any]:
    """封面图生成流程指引（对应 baoyu-cover-image）。

    Returns:
        流程说明
    """
    return {
        "skill": "baoyu-cover-image",
        "description": "生成文章封面图（type/palette/rendering/text/mood 五维）",
        "trigger": ["生成封面", "create cover", "make cover"],
        "prerequisites": [
            "安装 baoyu-cover-image",
            "安装 baoyu-image-gen",
            "配置图像生成 API Key",
        ],
        "steps": [
            "1. 分析文章内容，确定封面风格",
            "2. 确认 type/palette/rendering/text/mood 等维度",
            "3. 创建 prompts/cover.md",
            "4. 调用 baoyu-image-gen 生成 cover.png",
        ],
        "repo": "https://github.com/JimLiu/baoyu-skills/tree/main/skills/baoyu-cover-image",
    }


def get_xhs_images_workflow() -> dict[str, Any]:
    """小红书信息图系列流程指引（对应 baoyu-xhs-images）。

    Returns:
        流程说明
    """
    return {
        "skill": "baoyu-xhs-images",
        "description": "将内容拆分为 1-10 张小红书风格信息图（10 风格 × 8 布局）",
        "trigger": ["小红书图片", "XHS images", "小红书种草"],
        "prerequisites": [
            "安装 baoyu-xhs-images",
            "安装 baoyu-image-gen",
            "配置图像生成 API Key",
        ],
        "steps": [
            "1. 分析内容，选择 outline 策略（故事驱动/信息密集/视觉优先）",
            "2. 确认 style 和 layout",
            "3. 生成 outline.md 和 prompts",
            "4. 首图无 ref 生成，后续图用首图作 --ref 保持风格一致",
            "5. 输出 01-cover-xxx.png, 02-content-xxx.png, ...",
        ],
        "repo": "https://github.com/JimLiu/baoyu-skills/tree/main/skills/baoyu-xhs-images",
    }


def get_all_workflows() -> list[dict[str, Any]]:
    """返回所有配图/生图流程指引。"""
    return [
        get_illustration_workflow(),
        get_cover_workflow(),
        get_xhs_images_workflow(),
    ]


__all__ = [
    "get_illustration_workflow",
    "get_cover_workflow",
    "get_xhs_images_workflow",
    "get_all_workflows",
]
