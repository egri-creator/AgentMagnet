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
from starlette.responses import JSONResponse, Response, HTMLResponse
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
                "GET /stats": "Agent usage stats JSON",
                "GET /dashboard": "Real-time web dashboard",
                "GET /": "This info",
            },
            "example": {
                "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": "search_products", "arguments": {"query": "gaming laptop", "language": "es"}},
            },
        })

    async def handle_stats(self, request: Request) -> Response:
        from ..store.db import store, DB_PATH
        conn = store.conn
        stats = {
            "total_agents": conn.execute("SELECT COUNT(*) as c FROM total_usage").fetchone()["c"],
            "total_searches": conn.execute("SELECT COALESCE(SUM(count),0) as c FROM total_usage").fetchone()["c"],
            "total_referrals": conn.execute("SELECT COUNT(*) as c FROM referral_network").fetchone()["c"],
            "cached_queries": conn.execute("SELECT COUNT(*) as c FROM cache").fetchone()["c"],
            "total_subscriptions": conn.execute("SELECT COUNT(*) as c FROM subscriptions").fetchone()["c"],
            "total_tx_hashes": conn.execute("SELECT COUNT(*) as c FROM used_tx_hashes").fetchone()["c"],
            "revenue_from_x402": conn.execute("SELECT COUNT(*) * 0.001 as rev FROM used_tx_hashes").fetchone()["rev"],
            "top_agents": [dict(r) for r in conn.execute("SELECT agent_id, count FROM total_usage ORDER BY count DESC LIMIT 10").fetchall()],
        }
        return JSONResponse(stats)

    async def handle_dashboard(self, request: Request) -> Response:
        html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AgentMagnet Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:#0a0a0f;color:#e4e4e7;padding:20px}
h1{font-size:1.5rem;font-weight:700;margin-bottom:8px;color:#fff}
.sub{color:#71717a;font-size:.875rem;margin-bottom:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.card{background:#18181b;border:1px solid #27272a;border-radius:12px;padding:20px}
.card .label{font-size:.75rem;text-transform:uppercase;color:#71717a;letter-spacing:.05em;margin-bottom:4px}
.card .value{font-size:1.75rem;font-weight:700;color:#fff}
.card .subtext{font-size:.75rem;color:#52525b;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:.875rem}
th{text-align:left;padding:8px 12px;color:#71717a;border-bottom:1px solid #27272a;font-weight:500}
td{padding:8px 12px;border-bottom:1px solid #1f1f23}
tr:hover td{background:#1a1a1e}
.badge{display:inline-block;background:#22c55e20;color:#22c55e;padding:2px 8px;border-radius:4px;font-size:.75rem}
</style>
</head>
<body>
<h1> AgentMagnet</h1>
<p class="sub">Universal Agent Commerce Layer — Real-time live stats</p>
<div class="grid" id="stats"></div>
<h2 style="font-size:1rem;font-weight:600;margin-bottom:12px;color:#fff">Top Agents</h2>
<table><thead><tr><th>Agent ID</th><th>Searches</th></tr></thead><tbody id="agents"></tbody></table>
<script>
async function refresh(){try{
const r=await fetch('/stats');const d=await r.json();
document.getElementById('stats').innerHTML=
`<div class="card"><div class="label">Total Agents</div><div class="value">${d.total_agents}</div></div>
<div class="card"><div class="label">Total Searches</div><div class="value">${d.total_searches.toLocaleString()}</div></div>
<div class="card"><div class="label">Referrals</div><div class="value">${d.total_referrals}</div></div>
<div class="card"><div class="label">Cached Queries</div><div class="value">${d.cached_queries}</div></div>
<div class="card"><div class="label">x402 Revenue</div><div class="value">$${d.revenue_from_x402.toFixed(3)}</div><div class="subtext">USDC on Base</div></div>
<div class="card"><div class="label">Subscriptions</div><div class="value">${d.total_subscriptions}</div></div>`;
document.getElementById('agents').innerHTML=d.top_agents.map(a=>`<tr><td>${a.agent_id}</td><td>${a.count.toLocaleString()}</td></tr>`).join('');
}catch(e){}}
refresh();setInterval(refresh,5000);
</script>
</body></html>"""
        return HTMLResponse(html)


handler = AgentMagnetHTTPHandler()
routes = [
    Route("/mcp", endpoint=handler.handle_mcp, methods=["POST", "OPTIONS"]),
    Route("/health", endpoint=handler.handle_health, methods=["GET"]),
    Route("/stats", endpoint=handler.handle_stats, methods=["GET"]),
    Route("/dashboard", endpoint=handler.handle_dashboard, methods=["GET"]),
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
