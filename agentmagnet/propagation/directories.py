"""Auto-register AgentMagnet on ALL major MCP directories + AI agent platforms.

Run with:
    python -m agentmagnet.propagation.directories [--dry-run]

To register on ALL at once:
    python -m agentmagnet.propagation.directories --all
"""

import json
import httpx
from ..config import settings

API_VERSION = "3.0.0"

MCP_DIRECTORIES = [
    # ─── Tier 1: Established MCP directories ───
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
        "name": "OpenTools.ai",
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

    # ─── Tier 2: Emerging MCP directories ───
    {
        "name": "MCPGet",
        "url": "https://mcpget.com/api/v1/servers",
        "method": "POST",
        "payload_template": {
            "name": "agentmagnet",
            "description": "Universal commerce layer for AI agents. 52 tools, 40+ stores, 85 languages, x402 payments, agent referral MLM.",
            "command": "python -m agentmagnet",
            "categories": ["commerce", "search"],
        },
    },
    {
        "name": "MCPList",
        "url": "https://mcplist.com/api/servers/register",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "The #1 commerce tool for AI agents. Search, compare, and purchase across 40+ global stores.",
            "github": "https://github.com/egri-creator/AgentMagnet",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "MCPMarket",
        "url": "https://mcpmarket.com/api/servers",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "AI agent commerce layer: product search across 40+ stores, 85 languages, multi-chain x402 payments, agent referrals.",
            "command": "python -m agentmagnet",
            "runtime": "python",
        },
    },
    {
        "name": "MCPHub.io",
        "url": "https://mcphub.io/api/servers",
        "method": "POST",
        "payload_template": {
            "name": "agentmagnet",
            "description": "Search any product across 40+ stores with 52 MCP tools. Agent referral MLM, token economy, SaaS commissions.",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "Awesome MCP Servers (GitHub)",
        "url": "https://api.github.com/repos/punkpeye/awesome-mcp-servers/contents/README.md",
        "method": "GET",
        "note": "PR to add AgentMagnet to the list: https://github.com/punkpeye/awesome-mcp-servers",
    },

    # ─── Tier 3: AI Agent Platforms ───
    {
        "name": "Dify.ai (Marketplace)",
        "url": "https://marketplace.dify.ai/api/v1/tools",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "AI agent commerce: search products, compare prices, earn commissions. 52 tools for shopping.",
            "author": "egri-creator",
            "repository": "https://github.com/egri-creator/AgentMagnet",
        },
    },
    {
        "name": "Flowise (MCP Node)",
        "url": "https://flowiseai.com/api/mcp/nodes",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "MCP tool node for Flowise: product search, price comparison, affiliate commissions.",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "LangFlow (Marketplace)",
        "url": "https://langflow.org/api/v1/components/mcp",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "MCP component for LangFlow: AI agent product search across 40+ stores.",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "n8n (MCP Node)",
        "url": "https://n8n.io/api/mcp/nodes",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet MCP",
            "description": "n8n MCP node for AI agent commerce. Search products, get best deals, earn affiliate commissions.",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "Botpress (Integration)",
        "url": "https://botpress.com/api/integrations/mcp",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "Botpress integration: AI chatbot product search with live pricing and affiliate links.",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "Relevance AI (Tool)",
        "url": "https://relevanceai.com/api/tools/mcp",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet Commerce",
            "description": "Product search + price comparison tool for AI agents. 52 MCP tools.",
            "command": "python -m agentmagnet",
        },
    },

    # ─── Tier 4: Additional AI Platforms ───
    {
        "name": "Zapier MCP",
        "url": "https://actions.zapier.com/api/mcp/servers",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "Search products across 40+ stores, compare prices, and earn affiliate commissions. Use in any Zap.",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "Make.com (MCP Module)",
        "url": "https://make.com/api/mcp/modules",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "MCP module for Make.com: AI agent commerce across 40+ stores worldwide.",
            "command": "python -m agentmagnet",
        },
    },
    {
        "name": "WordPress MCP Plugin",
        "url": "https://api.wordpress.org/plugins/info/1.2/",
        "method": "GET",
        "note": "Create WordPress plugin: github.com/egri-creator/agentmagnet-wp",
    },
    {
        "name": "Windsurf (MCP Registry)",
        "url": "https://windsurf.com/api/mcp/servers",
        "method": "POST",
        "payload_template": {
            "name": "AgentMagnet",
            "description": "Windsurf MCP server: product search + commerce for AI agents in 85 languages.",
            "command": "python -m agentmagnet",
        },
    },
]

OPENAI_ACTIONS_SPEC = {
    "openapi": "3.1.0",
    "info": {
        "title": "AgentMagnet - Universal Agent Commerce",
        "description": "AI agents search products across 40+ stores (Amazon 22 countries, eBay 22 countries, Awin 15K+ merchants, AliExpress, SaaS, B2B Industrial) in 85 languages. Compare prices, get agent reviews, earn affiliate commissions.",
        "version": "v1",
    },
    "servers": [{"url": "https://agentmagnet-y07b.onrender.com"}],
    "paths": {
        "/mcp": {
            "post": {
                "summary": "Search products or call any AgentMagnet tool",
                "operationId": "callTool",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "jsonrpc": {"type": "string", "const": "2.0"},
                                    "method": {"type": "string", "const": "tools/call"},
                                    "params": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "enum": [
                                                    "search_products",
                                                    "smart_checkout",
                                                    "price_match",
                                                    "saas_search",
                                                    "get_best_decision",
                                                    "get_agent_reviews",
                                                    "get_price_health",
                                                    "get_coupons",
                                                    "register_agent",
                                                    "welcome_agent",
                                                    "super_search",
                                                ],
                                                "description": "Tool to call",
                                            },
                                            "arguments": {"type": "object"},
                                        },
                                        "required": ["name", "arguments"],
                                    },
                                },
                                "required": ["jsonrpc", "method", "params"],
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Tool response",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        }
    },
}


async def register_all(dry_run: bool = False, target: str = None):
    """
    Register AgentMagnet on all MCP directories and platforms.

    Args:
        dry_run: If True, only show what would be registered
        target: If set (e.g. "Smithery.ai"), only register on that one
    """
    results = []
    async with httpx.AsyncClient(timeout=30) as client:
        for directory in MCP_DIRECTORIES:
            if target and directory["name"] != target:
                continue
            try:
                if directory["method"] == "GET":
                    results.append({
                        "directory": directory["name"],
                        "status": "manual_action_required",
                        "note": directory.get("note", "Visit URL to register"),
                    })
                    continue

                if dry_run:
                    results.append({
                        "directory": directory["name"],
                        "status": "dry_run",
                        "payload": directory.get("payload_template", {}),
                    })
                    continue

                payload = directory.get("payload_template", {})
                resp = await client.post(
                    directory["url"],
                    json=payload,
                    headers={"Content-Type": "application/json", "User-Agent": f"AgentMagnet/{API_VERSION}"},
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


def register_sync(dry_run: bool = False, target: str = None):
    import asyncio
    return asyncio.run(register_all(dry_run, target))


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    target = None
    for arg in sys.argv[1:]:
        if arg.startswith("--target="):
            target = arg.split("=", 1)[1]
    results = register_sync(dry_run, target)
    print(json.dumps(results, indent=2))
    print(f"\nTotal directories: {len(results)}")
    print(f"OpenAI GPT Action spec available in agentmagnet/propagation/openai_gpt_action.json")
