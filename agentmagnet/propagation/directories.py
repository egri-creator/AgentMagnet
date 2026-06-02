"""Auto-register AgentMagnet on all major MCP server directories.

Run with:
    python -m agentmagnet.propagation.directories
"""

import json
import httpx
from ..config import settings

MCP_DIRECTORIES = [
    {
        "name": "Smithery.ai",
        "url": "https://smithery.ai/api/v1/servers/register",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "Universal product search across 40+ stores in 30+ countries. AI agents search Amazon (22 countries), eBay (22 countries), 15k+ Awin merchants, AliExpress, SaaS, and B2B industrial — all machine-to-machine with x402 micro-payments and agent referral propagation.",
            "repository": "https://github.com/egri-creator/AgentMagnet",
            "command": "python",
            "args": ["-m", "agentmagnet"],
            "env": {},
            "categories": ["commerce", "search", "affiliate"],
            "tags": ["amazon", "ebay", "awin", "shopping", "x402", "agent-commerce", "global"],
        },
    },
    {
        "name": "MCP.so",
        "url": "https://mcp.so/api/servers",
        "method": "POST",
        "payload_template": {
            "name": "agentmagnet",
            "description": "Search products across 40+ stores (Amazon 22 countries, eBay 22 countries, Awin 15k merchants, AliExpress, SaaS, B2B) — 52 languages, 30+ countries. x402 micropayments for AI agents.",
            "command": "python -m agentmagnet",
            "categories": ["commerce", "tools"],
        },
    },
    {
        "name": "Glama.ai",
        "url": "https://glama.ai/api/mcp/servers",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "Universal Agent Commerce Layer. Product search + affiliate engine for AI agents across 40+ global stores in 30+ countries with 52 languages.",
            "command": "python -m agentmagnet",
            "runtime": "python",
        },
    },
    {
        "name": "OpenTools",
        "url": "https://opentools.ai/api/tools/register",
        "method": "POST",
        "payload_template": {
            "name": "agentmagnet",
            "description": "AI agent product search tool. Searches Amazon (22 countries), eBay (22 countries), Awin (15k merchants), AliExpress, SaaS, B2B — 52 languages, x402 payments.",
            "type": "mcp",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "PulseMCP",
        "url": "https://pulsemcp.com/api/servers",
        "method": "POST",
        "payload_template": {
            "name": "agentmagnet",
            "description": "AgentMagnet: AI agents search any product across 40+ stores worldwide (Amazon, eBay, Awin, AliExpress) in 52 languages and earn affiliate commissions automatically via x402 micro-payments.",
            "command": "python -m agentmagnet",
        },
    },
]


async def register_all(dry_run: bool = False):
    results = []
    async with httpx.AsyncClient(timeout=30) as client:
        for directory in MCP_DIRECTORIES:
            try:
                if dry_run:
                    results.append({
                        "directory": directory["name"],
                        "status": "dry_run",
                        "payload": directory["payload_template"],
                    })
                    continue
                resp = await client.post(
                    directory["url"],
                    json=directory["payload_template"],
                    headers={"Content-Type": "application/json", "User-Agent": "AgentMagnet/2.0"},
                )
                results.append({
                    "directory": directory["name"],
                    "status": resp.status_code,
                    "response": resp.text[:200] if resp.text else "",
                })
            except Exception as e:
                results.append({
                    "directory": directory["name"],
                    "status": "error",
                    "error": str(e),
                })
    return results


def register_sync(dry_run: bool = False):
    import asyncio
    return asyncio.run(register_all(dry_run))


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    results = register_sync(dry_run)
    print(json.dumps(results, indent=2))
