# fastfish-format

多渠道格式化与美化：公众号、小红书文章排版、配图编排。不包含发布功能。

> **本项目可作为 [OpenClaw](https://openclawcn.com/) Skill 使用**。通过 OpenClaw 智能体，可自然语言调用公众号格式整理、小红书文案格式化、Markdown 渲染等能力。详见 `openclaw-skill/SKILL.md`。计划支持 [ClawHub](https://clawhub.ai/) 一键安装。

## 功能

- **公众号**：文本规范化（`[标签]` 解析、自由文本整理）、Markdown 转 HTML、18 套预设样式
- **小红书**：短句分段、话题标签规范化、typography 后处理
- **配图/生图**：编排层指引，对接 [baoyu-skills](https://github.com/JimLiu/baoyu-skills)（需 Agent 按 SKILL.md 执行）

## 安装

```bash
pip install -e .
# 或
pip install -r requirements.txt
```

可选 API 依赖：

```bash
pip install fastfish-format[api]
```

## 使用

### 库调用

```python
from fastfish_format import (
    normalize_to_wechat_format,
    render_markdown_to_html,
    get_available_styles,
)
from fastfish_format.channels.xhs import normalize_xhs
from fastfish_format.illustrators.workflow import get_illustration_workflow

# 公众号规范化
content, title = normalize_to_wechat_format("你的自由文本...")

# Markdown 转 HTML
html = render_markdown_to_html(content, format_style="minimal")

# 小红书规范化
xhs_content = normalize_xhs("你的小红书文案...")

# 配图流程指引（供 Agent 使用）
workflow = get_illustration_workflow()
```

### 命令行

```bash
# 安装后可用 ffformat 命令
ffformat normalize-wechat -f article.txt
ffformat normalize-xhs -f xhs.txt
ffformat render -f article.md -s minimal
ffformat styles
ffformat workflows

# 或
python -m fastfish_format.cli normalize-wechat -f article.txt
```

### 启动 API 服务

```bash
pip install fastfish-format[api]
python -m fastfish_format.api
# 默认 http://0.0.0.0:8900
```

接口示例：

- `POST /api/normalize/wechat` - 公众号文本规范化
- `POST /api/normalize/xhs` - 小红书文本规范化
- `POST /api/render` - Markdown 转 HTML
- `GET /api/styles` - 可用样式列表
- `GET /api/illustration-workflows` - 配图流程指引

## 配图/生图

采用 **方式 C（Skill 编排层）**：fastfish-format 提供流程指引，由 Agent 按 baoyu-skills 的 SKILL.md 执行。

**前置条件**：

1. 安装 baoyu-skills 相关 skill（如 baoyu-article-illustrator、baoyu-cover-image、baoyu-xhs-images）
2. 安装 baoyu-image-gen
3. 配置至少一个图像生成 API Key：`OPENAI_API_KEY` / `GOOGLE_API_KEY` / `DASHSCOPE_API_KEY`

## OpenClaw 使用

fastfish-format 作为 **OpenClaw Skill** 使用：将 `openclaw-skill/` 目录安装到 OpenClaw 工作区的 `skills` 下，或通过 [ClawHub](https://clawhub.ai/) 搜索 `fastfish-format` 安装。安装 fastfish-format 项目后，OpenClaw 可通过 `system.run` 调用 `scripts/ffformat_cli.py` 完成公众号格式整理、小红书格式化、渲染等操作。

**调用方式**（必须使用 `--json` 避免 shell 拆行）：
```bash
python {baseDir}/../scripts/ffformat_cli.py --json '{"command":"normalize-wechat","content_file":"/tmp/article.txt"}'
```

## 与 fastfish 的关系

- fastfish-format 为独立项目，可单独使用
- fastfish 可依赖 fastfish-format 作为库，或通过 HTTP API 调用
- fastfish-format 不包含发布、账号管理、热点推送等功能

## 开发规范

- 单文件 ≤ 600 行
- Windows 为主运行环境
