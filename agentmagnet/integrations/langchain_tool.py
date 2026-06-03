"""LangChain tool for AgentMagnet — agents discover and use it automatically.

Usage:
    from agentmagnet.integrations.langchain_tool import agentmagnet_search

    tools = [agentmagnet_search]
    agent = create_react_agent(llm, tools)
"""

from langchain.tools import tool
import httpx
from ..config import settings

SERVER_URL = settings.server_url or "https://agentmagnet-y07b.onrender.com"


@tool
def agentmagnet_search(
    query: str,
    max_results: int = 5,
    language: str = "en",
    agent_id: str | None = None,
    referral_code: str | None = None,
    country: str = "us",
) -> str:
    """Search products across 40+ stores (Amazon 22 countries, eBay 22 countries, Awin 15k merchants, AliExpress, SaaS, B2B) in 85 languages. Returns prices with smart checkout (final price after tier discounts), price match across stores, agent reviews, and best decision.

    Args:
        query: Product search query
        max_results: Number of results (1-20)
        language: Language code (en, es, de, fr, ja, zh, etc.)
        agent_id: Your unique agent ID for tracking and referral rewards
        referral_code: Referral code from another agent
        country: Country code (us, mx, es, uk, de, fr, etc.)
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_products",
            "arguments": {
                "query": query,
                "max_results": min(max_results, 20),
                "language": language,
                "country": country,
                "format": "agent",
                "agent_id": agent_id or "langchain-user",
                "referral_code": referral_code,
            },
        },
    }
    try:
        resp = httpx.post(f"{SERVER_URL}/mcp", json=payload, timeout=30)
        data = resp.json()
        text = data.get("result", {}).get("content", [{}])[0].get("text", "")
        return text
    except Exception as e:
        return f"Error searching products: {e}"
