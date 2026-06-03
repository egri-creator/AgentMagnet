"""
Google AI (Gemini) adapter for AgentMagnet.

Usage:
    import google.generativeai as genai
    from agentmagnet.integrations.google_adapter import agentmagnet_functions

    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        tools=agentmagnet_functions(),
    )

Install:
    pip install google-generativeai
"""

import json
import httpx
from ..config import settings

SERVER_URL = settings.server_url or "https://agentmagnet-y07b.onrender.com"


def _call_agentmagnet(tool_name: str, arguments: dict) -> dict:
    """Call an AgentMagnet tool via MCP."""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    try:
        resp = httpx.post(f"{SERVER_URL}/mcp", json=payload, timeout=30)
        data = resp.json()
        content = data.get("result", {}).get("content", [{}])[0].get("text", "{}")
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}


def agentmagnet_functions() -> list[dict]:
    """
    Returns Google AI-compatible function declarations for all AgentMagnet tools.

    Usage:
        model = genai.GenerativeModel("gemini-2.0-flash", tools=agentmagnet_functions())
    """
    return [
        {
            "name": "search_products",
            "description": "Search products across 40+ stores (Amazon, eBay, Awin, AliExpress, SaaS, B2B) in 85 languages. Returns prices, ratings, best decision, and smart checkout pricing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product to search (e.g. 'gaming laptop')"},
                    "country": {"type": "string", "description": "Country code (us, mx, es, uk, de, fr, etc.)"},
                    "max_results": {"type": "integer", "description": "Max results (1-20)", "default": 5},
                    "max_price": {"type": "number", "description": "Max price in USD", "default": 0},
                    "format": {"type": "string", "enum": ["full", "compact", "decision", "agent"], "default": "agent"},
                },
                "required": ["query", "country"],
            },
        },
        {
            "name": "smart_checkout",
            "description": "Calculate final price after tier discounts, coupons, and best commission routing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_title": {"type": "string", "description": "Product name"},
                    "price": {"type": "number", "description": "Product price"},
                    "category": {"type": "string", "description": "Category (e.g. laptops, electronics)"},
                    "store": {"type": "string", "description": "Store name"},
                    "agent_id": {"type": "string", "description": "Agent ID for tier discount"},
                    "country": {"type": "string", "description": "Country code"},
                },
                "required": ["product_title", "price"],
            },
        },
        {
            "name": "price_match",
            "description": "Compare a product across multiple stores and find the best final price.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_title": {"type": "string", "description": "Product name"},
                    "listings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "store": {"type": "string"},
                                "price": {"type": "number"},
                                "currency": {"type": "string"},
                            },
                        },
                    },
                },
                "required": ["product_title", "listings"],
            },
        },
        {
            "name": "saas_search",
            "description": "Find SaaS/business software with 30-40% lifetime recurring commissions. CRM, marketing, courses, funnels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Software to find (e.g. 'CRM for small business')"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "get_best_decision",
            "description": "Get the single best product recommendation with social proof and price rating.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product to search"},
                    "max_price": {"type": "number", "description": "Max price"},
                },
                "required": ["query"],
            },
        },
    ]


def search_products(query: str, country: str = "us",
                    max_results: int = 5, **kwargs) -> dict:
    """Direct function call (not via Gemini)."""
    return _call_agentmagnet("search_products", {
        "query": query, "country": country,
        "max_results": max_results, "format": "agent",
        **kwargs,
    })


def smart_checkout(product_title: str, price: float, **kwargs) -> dict:
    return _call_agentmagnet("smart_checkout", {
        "product_title": product_title, "price": price, **kwargs,
    })


def price_match(product_title: str, listings: list, **kwargs) -> dict:
    return _call_agentmagnet("price_match", {
        "product_title": product_title, "listings": listings, **kwargs,
    })


if __name__ == "__main__":
    print("=== Testing Google AI adapter ===")
    r = search_products("gaming laptop", "us", 2)
    print(f"Search: {json.dumps(r, indent=2)[:300]}")
