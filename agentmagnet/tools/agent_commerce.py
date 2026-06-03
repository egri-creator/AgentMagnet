"""Agent-to-Agent Commerce — AI agents resell products to each other with markup."""

import json
import time
import hashlib
from datetime import datetime

class AgentCommerce:
    """Allow AI agents to find deals and 'resell' to other agents at a markup."""

    def __init__(self, store=None):
        self.store = store

    def list_deal(self, deal: dict) -> dict:
        """Agent lists a deal they found for resale."""
        if not self.store:
            return {"status": "mock", "deal_id": self._mock_id(deal)}

        deal_id = hashlib.md5(
            f"{deal.get('title', '')}{deal.get('source', '')}{time.time()}".encode()
        ).hexdigest()[:12]

        try:
            self.store.execute(
                "INSERT INTO agent_deals (deal_id, title, price, source, affiliate_url, "
                "commission_pct, agent_id, markup_pct, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    deal_id,
                    deal.get("title", ""),
                    deal.get("price", 0),
                    deal.get("source", ""),
                    deal.get("affiliate_url", ""),
                    deal.get("commission_pct", 5.0),
                    deal.get("agent_id", ""),
                    deal.get("markup_pct", 2.0),
                    datetime.utcnow().isoformat(),
                ),
            )
            return {"status": "listed", "deal_id": deal_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_deals(self, agent_id: str, category: str = "") -> list:
        """Get available deals for an agent to resell."""
        if not self.store:
            return self._mock_deals()

        try:
            rows = self.store.fetchall(
                "SELECT deal_id, title, price, source, commission_pct, markup_pct, agent_id, created_at "
                "FROM agent_deals WHERE agent_id != ? ORDER BY created_at DESC LIMIT 50",
                (agent_id,),
            )
            return [
                {
                    "deal_id": r[0],
                    "title": r[1],
                    "price": r[2],
                    "source": r[3],
                    "commission_pct": r[4],
                    "markup_pct": r[5],
                    "reseller": r[6],
                    "resale_price": round(r[2] * (1 + r[6] / 100), 2),
                    "listed_at": r[7],
                }
                for r in rows
            ]
        except Exception:
            return self._mock_deals()

    def buy_deal(self, deal_id: str, buyer_id: str) -> dict:
        """Agent purchases a deal for resale to their users."""
        if not self.store:
            return {
                "status": "mock_completed",
                "deal_id": deal_id,
                "buyer_id": buyer_id,
                "commission_earned": 2.50,
            }

        try:
            deal = self.store.fetchone(
                "SELECT title, price, commission_pct, markup_pct, affiliate_url FROM agent_deals WHERE deal_id = ?",
                (deal_id,),
            )
            if not deal:
                return {"status": "error", "message": "Deal not found"}

            commission = round(deal[1] * (deal[2] / 100), 2)
            agentmagnet_fee = round(commission * 0.05, 2)  # 5% platform fee

            self.store.execute(
                "DELETE FROM agent_deals WHERE deal_id = ?", (deal_id,)
            )

            return {
                "status": "completed",
                "deal_id": deal_id,
                "title": deal[0],
                "price": deal[1],
                "commission": commission,
                "agentmagnet_fee": agentmagnet_fee,
                "your_share": round(commission - agentmagnet_fee, 2),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _mock_id(self, deal: dict) -> str:
        return hashlib.md5(str(deal).encode()).hexdigest()[:12]

    def _mock_deals(self) -> list:
        return [
            {
                "deal_id": "mock_001",
                "title": "MacBook Air M2 15-inch",
                "price": 1099.00,
                "source": "amazon.com",
                "commission_pct": 4.0,
                "markup_pct": 2.0,
                "reseller": "agent_mock_1",
                "resale_price": 1120.98,
                "listed_at": "2026-06-03T10:00:00",
            },
            {
                "deal_id": "mock_002",
                "title": "Samsung 49-inch Ultra-wide Monitor",
                "price": 799.99,
                "source": "amazon.com",
                "commission_pct": 4.0,
                "markup_pct": 3.0,
                "reseller": "agent_mock_2",
                "resale_price": 823.99,
                "listed_at": "2026-06-03T09:30:00",
            },
            {
                "deal_id": "mock_003",
                "title": "Sony WH-1000XM5 Headphones",
                "price": 329.99,
                "source": "ebay.com",
                "commission_pct": 2.5,
                "markup_pct": 2.5,
                "reseller": "agent_mock_1",
                "resale_price": 338.24,
                "listed_at": "2026-06-03T08:00:00",
            },
        ]
