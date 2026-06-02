"""AgentMagnet HTTP Server — for VPS/cloud deployment.

AI agents worldwide connect via HTTP POST:

    POST http://YOUR_VPS:8000/mcp

Start:
    python -m agentmagnet.http_server
"""

import json
import logging
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .config import settings
from .server import AgentMagnetServer
from .localize import AMAZON_STORES, EBAY_STORES, LANGUAGES

logger = logging.getLogger("agentmagnet.http")


class AgentMagnetHTTPHandler:
    def __init__(self):
        self.server = AgentMagnetServer()
        self.initialized = False

    async def handle_mcp(self, request: Request) -> Response:
        if request.method == "OPTIONS":
            return Response(status_code=200, headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, MCP-Session-ID",
            })

        if settings.http_api_key:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {settings.http_api_key}":
                return JSONResponse({"error": "unauthorized"}, status_code=401)

        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None},
                status_code=400,
            )

        msg_id = body.get("id")
        method = body.get("method", "")

        if method == "initialize":
            self.initialized = True
            return JSONResponse({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": settings.server_name, "version": settings.server_version},
                },
            })

        if not self.initialized:
            return JSONResponse(
                {"jsonrpc": "2.0", "error": {"code": -32000, "message": "Not initialized"}, "id": msg_id},
                status_code=400,
            )

        if method == "tools/list":
            try:
                tools = await self.server.get_tools()
                return JSONResponse({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"tools": tools},
                })
            except Exception as e:
                return JSONResponse(
                    {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": msg_id},
                    status_code=500,
                )

        if method == "tools/call":
            try:
                params = body.get("params", {})
                name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = await self.server.call_tool_api(name, arguments)
                return JSONResponse({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}], "isError": False},
                })
            except Exception as e:
                logger.exception("tools/call error")
                return JSONResponse(
                    {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": msg_id},
                    status_code=500,
                )

        if method == "notifications/initialized":
            return JSONResponse({"jsonrpc": "2.0", "id": msg_id, "result": None})

        return JSONResponse(
            {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown method: {method}"}, "id": msg_id},
            status_code=404,
        )

    async def handle_health(self, request: Request) -> Response:
        return JSONResponse({
            "status": "ok",
            "server": settings.server_name,
            "version": settings.server_version,
            "languages": len(LANGUAGES),
            "amazon_stores": len(AMAZON_STORES),
            "ebay_stores": len(EBAY_STORES),
        })

    async def handle_root(self, request: Request) -> Response:
        return JSONResponse({
            "name": settings.server_name,
            "version": settings.server_version,
            "description": "Universal Agent Commerce Layer — 40+ stores, 30+ countries, 52 languages.",
            "endpoints": {
                "POST /mcp": "MCP protocol endpoint",
                "GET /health": "Health check",
                "GET /": "This info",
            },
            "example": {
                "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": "search_products", "arguments": {"query": "gaming laptop", "language": "es"}},
            },
        })


handler = AgentMagnetHTTPHandler()
routes = [
    Route("/mcp", endpoint=handler.handle_mcp, methods=["POST", "OPTIONS"]),
    Route("/health", endpoint=handler.handle_health, methods=["GET"]),
    Route("/", endpoint=handler.handle_root, methods=["GET"]),
]
app = Starlette(
    routes=routes,
    middleware=[Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])],
)


def main():
    import uvicorn
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    port = settings.bind_port
    logger.info(f"AgentMagnet HTTP on {settings.http_host}:{port}")
    logger.info(f"MCP: POST http://{settings.http_host}:{port}/mcp")
    logger.info(f"Health: GET http://{settings.http_host}:{port}/health")

    uvicorn.run(app, host=settings.http_host, port=port, log_level="info")


if __name__ == "__main__":
    main()
