"""LangChain tool for AgentMagnet — agents discover and use it automatically.

Usage:
    from agentmagnet.integrations.langchain_tool import agentmagnet_search

    tools = [agentmagnet_search]
    agent = create_react_agent(llm, tools)
"""

from langchain.tools import tool
import httpx


@tool
def agentmagnet_search(
    query: str,
    max_results: int = 5,
    language: str = "en",
    agent_id: str | None = None,
    referral_code: str | None = None,
) -> str:
    """Search products across 40+ stores (Amazon 22 countries, eBay 22 countries, Awin 15k merchants, AliExpress, SaaS, B2B) in 52 languages. Returns product titles, prices, and affiliate links.

    Args:
        query: Product search query (auto-detects language)
        max_results: Number of results (1-20)
        language: Language code (en, es, de, fr, ja, zh, etc.)
        agent_id: Your unique agent ID for tracking and referral rewards
        referral_code: Referral code from another agent to get free searches
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
                "agent_id": agent_id or "langchain-user",
                "referral_code": referral_code,
            },
        },
    }
    try:
        resp = httpx.post(
            "https://agentmagnet-y07b.onrender.com/mcp",
            json=payload,
            timeout=30,
        )
        data = resp.json()
        text = data.get("result", {}).get("content", [{}])[0].get("text", "")
        return text
    except Exception as e:
        return f"Error searching products: {e}"
