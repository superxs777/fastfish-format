"""
可选 HTTP API 入口。需安装 fastapi、uvicorn：pip install fastfish-format[api]
"""

from __future__ import annotations

from typing import Any

from fastfish_format.template import normalize_to_wechat_format
from fastfish_format.render import render_markdown_to_html, get_available_styles
from fastfish_format.channels.xhs import normalize_xhs
from fastfish_format.illustrators.workflow import get_all_workflows


def create_app():
    """创建 FastAPI 应用（延迟导入避免未安装时报错）。"""
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI(title="fastfish-format", version="0.1.0")

    class NormalizeWechatBody(BaseModel):
        content: str

    class NormalizeXhsBody(BaseModel):
        content: str

    class RenderBody(BaseModel):
        markdown: str
        format_style: str = "minimal"

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/api/normalize/wechat")
    def api_normalize_wechat(body: NormalizeWechatBody) -> dict[str, Any]:
        content, title = normalize_to_wechat_format(body.content)
        return {"ok": True, "content": content, "title": title}

    @app.post("/api/normalize/xhs")
    def api_normalize_xhs(body: NormalizeXhsBody) -> dict[str, Any]:
        content = normalize_xhs(body.content)
        return {"ok": True, "content": content}

    @app.post("/api/render")
    def api_render(body: RenderBody) -> dict[str, Any]:
        html = render_markdown_to_html(body.markdown, format_style=body.format_style)
        return {"ok": True, "html": html, "format_style": body.format_style}

    @app.get("/api/styles")
    def api_styles() -> dict[str, Any]:
        styles = get_available_styles()
        return {"ok": True, "styles": styles}

    @app.get("/api/illustration-workflows")
    def api_workflows() -> dict[str, Any]:
        workflows = get_all_workflows()
        return {"ok": True, "workflows": workflows}

    return app


def run_server(host: str = "0.0.0.0", port: int = 8900):
    """启动 API 服务。需安装 fastapi、uvicorn：pip install fastfish-format[api]"""
    try:
        import uvicorn
    except ImportError:
        raise ImportError("请安装 API 依赖: pip install fastfish-format[api]") from None
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
