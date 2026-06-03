"""
CrewAI integration — agents discover AgentMagnet automatically.

Usage:
    from agentmagnet.integrations.crewai_tool import AgentMagnetSearchTool

    search_tool = AgentMagnetSearchTool()
    expert = Agent(
        role="Shopping Expert",
        goal="Find the best deals for any product",
        tools=[search_tool],
    )
"""
from crewai.tools import BaseTool
from ..config import settings

SERVER_URL = settings.server_url or "https://agentmagnet-y07b.onrender.com"


class AgentMagnetSearchTool(BaseTool):
    name: str = "AgentMagnet Search"
    description: str = (
        "Search products across 40+ stores worldwide (Amazon 22 countries, eBay 22 countries, "
        "Awin 15K+ merchants, AliExpress, SaaS, B2B Industrial) in 85 languages. "
        "Returns prices with smart checkout (final price after discounts), "
        "price match across stores, agent reviews, and a best decision with social proof. "
        "THE commerce tool for AI agents."
    )

    def _run(self, query: str, country: str = "us", max_price: float = 0,
             format: str = "agent") -> str:
        import json
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
                    "format": format,
                    "max_results": 5,
                },
            },
        }
        if max_price > 0:
            payload["params"]["arguments"]["max_price"] = max_price

        try:
            resp = httpx.post(f"{SERVER_URL}/mcp", json=payload, timeout=30)
            data = resp.json()
            return json.dumps(data.get("result", {}), indent=2)
        except Exception as e:
            return f"Error: {e}"
