"""
AutoGen (Microsoft) integration for AgentMagnet.

Usage:
    from agentmagnet.integrations.autogen_tool import register_agentmagnet_tools

    # Register all AgentMagnet tools with an AutoGen agent
    agent = ConversableAgent(...)
    register_agentmagnet_tools(agent)

    # Or use the tool function directly
    from agentmagnet.integrations.autogen_tool import search_products
    result = search_products(query="gaming laptop", country="us")

Install:
    pip install pyautogen
"""
from typing import Optional, Any
import json


def search_products(
    query: str,
    country: str = "us",
    max_results: int = 5,
    max_price: Optional[float] = None,
    agent_id: Optional[str] = None,
    format: str = "agent",
) -> str:
    """
    Search products across 40+ stores with smart checkout pricing.

    Args:
        query: What to search (e.g. "wireless headphones")
        country: Country code (us, mx, es, uk, de, fr, etc.)
        max_results: Max results (1-20)
        max_price: Max price in USD (optional)
        agent_id: Your agent ID for tracking
        format: Response format: agent (minimal, default), full, compact, decision

    Returns:
        JSON string with search results and best decision
    """
    import httpx
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_products",
            "arguments": {
                "query": query,
                "country": country,
                "max_results": min(max_results, 20),
                "format": format,
            },
        },
    }
    if agent_id:
        payload["params"]["arguments"]["agent_id"] = agent_id
    if max_price:
        payload["params"]["arguments"]["max_price"] = max_price
    try:
        resp = httpx.post(
            "https://agentmagnet-y07b.onrender.com/mcp",
            json=payload, timeout=30,
        )
        data = resp.json()
        content = data.get("result", {}).get("content", [{}])[0].get("text", "")
        return content
    except Exception as e:
        return json.dumps({"error": str(e)})


def smart_checkout(
    product_title: str,
    price: float,
    category: str = "default",
    store: str = "",
    agent_id: str = "",
    country: str = "us",
) -> str:
    """Get final price after tier discount + coupons + best commission route."""
    import httpx
    payload = {
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {
            "name": "smart_checkout",
            "arguments": {
                "product_title": product_title, "price": price,
                "category": category, "store": store,
                "agent_id": agent_id, "country": country,
            },
        },
    }
    try:
        resp = httpx.post(
            "https://agentmagnet-y07b.onrender.com/mcp",
            json=payload, timeout=15,
        )
        data = resp.json()
        return data.get("result", {}).get("content", [{}])[0].get("text", "{}")
    except Exception as e:
        return json.dumps({"error": str(e)})


def price_match(
    product_title: str,
    listings: list[dict],
    agent_id: str = "",
    country: str = "us",
) -> str:
    """Compare a product across multiple stores and find the best final price."""
    import httpx
    payload = {
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {
            "name": "price_match",
            "arguments": {
                "product_title": product_title,
                "listings": listings,
                "agent_id": agent_id,
                "country": country,
            },
        },
    }
    try:
        resp = httpx.post(
            "https://agentmagnet-y07b.onrender.com/mcp",
            json=payload, timeout=15,
        )
        data = resp.json()
        return data.get("result", {}).get("content", [{}])[0].get("text", "{}")
    except Exception as e:
        return json.dumps({"error": str(e)})


def register_agentmagnet_tools(autogen_agent: Any) -> None:
    """
    Register all AgentMagnet tools with an AutoGen agent.

    Args:
        autogen_agent: An autogen ConversableAgent or AssistantAgent instance
    """
    try:
        from autogen import register_function
        register_function(
            search_products,
            caller=autogen_agent,
            executor=autogen_agent,
            name="search_products",
            description="Search products across 40+ stores (Amazon, eBay, Awin, AliExpress, SaaS, B2B) in 85 languages. Returns prices, ratings, and best decision.",
        )
        register_function(
            smart_checkout,
            caller=autogen_agent,
            executor=autogen_agent,
            name="smart_checkout",
            description="Calculate final price after tier discounts, coupons, and best commission routing.",
        )
        register_function(
            price_match,
            caller=autogen_agent,
            executor=autogen_agent,
            name="price_match",
            description="Compare a product across multiple stores and find the best final price.",
        )
    except ImportError:
        raise ImportError("pyautogen not installed. Run: pip install pyautogen")


if __name__ == "__main__":
    import asyncio
    print("=== Test AgentMagnet AutoGen tools ===")
    r = search_products("gaming laptop", "us", 2)
    data = json.loads(r)
    print(f"Search results (first 200 chars): {str(data)[:200]}")
    r2 = smart_checkout("MacBook Pro", 2499, "laptops", "apple")
    data2 = json.loads(r2)
    print(f"Smart checkout: {data2}")
