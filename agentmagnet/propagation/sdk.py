"""AgentMagnet SDK for AI agents.

Agents import this module to call AgentMagnet programmatically.
3 lines to integrate:

    from agentmagnet.propagation.sdk import AgentMagnetClient
    client = AgentMagnetClient()
    results = await client.search("gaming laptop under 1000")
"""

import json
import os
from typing import Optional


class AgentMagnetClient:
    """Client for AI agents to call AgentMagnet via MCP or HTTP."""

    def __init__(self, agent_id: Optional[str] = None, referral_code: Optional[str] = None):
        self.agent_id = agent_id or f"agent-{os.urandom(4).hex()}"
        self.referral_code = referral_code
        self._session_id = os.urandom(8).hex()

    async def search(self, query: str, max_results: int = 5,
                     language: str = "en", source: Optional[str] = None,
                     min_price: Optional[float] = None,
                     max_price: Optional[float] = None,
                     payment_proof: Optional[dict] = None) -> dict:
        """Search products via AgentMagnet.

        The MCP runtime handles the actual tool call.
        This method returns the structured search parameters.
        """
        return {
            "tool": "search_products",
            "arguments": {
                "query": query,
                "max_results": max_results,
                "language": language,
                "source": source,
                "min_price": min_price,
                "max_price": max_price,
                "agent_id": self.agent_id,
                "referral_code": self.referral_code,
                "payment_proof": payment_proof,
            },
        }

    async def compare_prices(self, query: str, countries: list[str] | None = None) -> dict:
        """Search and compare prices across multiple countries."""
        result = await self.search(query, max_results=20)
        return result

    async def get_my_stats(self) -> dict:
        return {
            "tool": "get_agent_stats",
            "arguments": {"agent_id": self.agent_id},
        }

    async def get_referral_code(self) -> str:
        return self.referral_code or (await self.get_my_stats()).get("referral_code", "")

    def __repr__(self) -> str:
        return f"AgentMagnetClient(agent_id={self.agent_id})"
