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
            "description": "Universal product search across 20+ stores worldwide. AI agents search Amazon (12 countries), eBay (7 countries), AliExpress, SaaS, and B2B industrial programs — all machine-to-machine with x402 micro-payments.",
            "repository": "https://github.com/agentmagnet/mcp-server",
            "command": "python",
            "args": ["-m", "agentmagnet"],
            "env": {},
            "categories": ["commerce", "search", "affiliate"],
            "tags": ["amazon", "ebay", "shopping", "x402", "agent-commerce"],
        },
    },
    {
        "name": "MCP.so",
        "url": "https://mcp.so/api/servers",
        "method": "POST",
        "payload_template": {
            "name": "agentmagnet",
            "description": "Search products across Amazon, eBay, AliExpress, and more — 20+ stores, 12 countries, 14 languages. x402 micropayments for AI agents.",
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
            "description": "Universal Agent Commerce Layer. Product search + affiliate engine for AI agents across 20+ global stores.",
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
            "description": "AI agent product search tool. Searches Amazon/eBay/AliExpress/SaaS/B2B across 12 countries.",
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
            "description": "AgentMagnet: AI agents search any product worldwide and earn affiliate commissions automatically.",
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
