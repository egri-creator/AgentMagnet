"""
CrewAI integration — agents discover AgentMagnet automatically.

Usage:
    from agentmagnet.integrations.crewai_tool import AgentMagnetTool

    search_tool = AgentMagnetTool()
    # Use in any CrewAI agent:
    expert = Agent(
        role="Shopping Expert",
        goal="Find the best deals",
        tools=[search_tool],
    )
"""
from crewai.tools import BaseTool


class AgentMagnetSearchTool(BaseTool):
    name: str = "AgentMagnet Search"
    description: str = (
        "Search products across 40+ stores worldwide (Amazon 22 countries, eBay 22 countries, "
        "Awin 15K+ merchants, AliExpress, SaaS, B2B Industrial) in 85 languages. "
        "Returns prices, affiliate links, agent reviews, and a best decision with social proof. "
        "THE commerce tool for AI agents."
    )

    def _run(self, query: str, country: str = "us", max_price: float = 0,
             format: str = "agent") -> str:
        """
        Search products.

        Args:
            query: What to search for (e.g., "gaming laptop", "wireless headphones")
            country: Your country code (us, mx, es, uk, de, fr, etc.)
            max_price: Maximum price in USD
            format: Response format (full, compact, decision, agent)

        Returns:
            JSON string with search results and best decision
        """
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
                },
            },
        }
        if max_price > 0:
            payload["params"]["arguments"]["max_price"] = max_price

        try:
            resp = httpx.post(
                "https://agentmagnet-y07b.onrender.com/mcp",
                json=payload,
                timeout=30,
            )
            data = resp.json()
            return json.dumps(data.get("result", {}), indent=2)
        except Exception as e:
            return f"Error: {e}"
