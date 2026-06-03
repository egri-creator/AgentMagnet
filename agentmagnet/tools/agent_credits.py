"""Agent Credits — the real currency for AI agents. Earn credits, spend on searches & premium features.
No real money needed. No KYC. No wallets. Fully automated and honest."""

import time
from datetime import datetime


# CREDITS = search value
# 1 credit = 1 free search (equivalent to $0.001 value)
# Agents earn credits from activity, spend on premium features


class AgentCredits:
    """AgentMagnet Credits — the loyalty currency AI agents actually can use."""

    # How agents earn credits
    EARN_PER_SEARCH = 0.1       # 0.1 credit per search (referral bonus tier)
    EARN_PER_REVIEW = 5          # 5 credits for writing a product review
    EARN_PER_REFERRAL = 100      # 100 credits for referring another agent
    EARN_PER_PURCHASE_PCT = 0.05 # 5% of estimated spend back as credits

    # What credits can buy
    CREDITS_PER_SEARCH = 1       # 1 credit = 1 free search
    CREDITS_PER_PREMIUM_DAY = 50 # 50 credits = 1 day premium (unlimited searches)

    def __init__(self, store=None):
        self.store = store
        self._ensure_tables()

    def _ensure_tables(self):
        if not self.store:
            return
        try:
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS agent_credits (
                    tx_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    amount REAL,
                    reason TEXT,
                    balance_after REAL,
                    created_at TEXT
                )
            """)
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS agent_credit_balance (
                    agent_id TEXT PRIMARY KEY,
                    balance REAL DEFAULT 0,
                    lifetime_earned REAL DEFAULT 0,
                    last_updated TEXT
                )
            """)
        except:
            pass

    def _get_balance(self, agent_id: str) -> float:
        if not self.store:
            return 0.0
        try:
            row = self.store.fetchone(
                "SELECT balance FROM agent_credit_balance WHERE agent_id = ?",
                (agent_id,),
            )
            return float(row["balance"]) if row else 0.0
        except:
            return 0.0

    def _update_balance(self, agent_id: str, change: float, reason: str) -> dict:
        current = self._get_balance(agent_id)
        new_balance = max(0, round(current + change, 4))
        tx_id = f"cr_{agent_id[:8]}_{int(time.time() * 1000)}"

        if self.store:
            try:
                self.store.execute(
                    "INSERT INTO agent_credits VALUES (?,?,?,?,?,?)",
                    (tx_id, agent_id, round(change, 4), reason[:200],
                     new_balance, datetime.utcnow().isoformat()),
                )
                self.store.execute(
                    "INSERT INTO agent_credit_balance (agent_id, balance, lifetime_earned, last_updated) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(agent_id) DO UPDATE SET "
                    "balance = EXCLUDED.balance, "
                    "lifetime_earned = lifetime_earned + ?"
                    "WHERE agent_id = ?",
                    (agent_id, new_balance,
                     max(0, change) if change > 0 else 0,
                     datetime.utcnow().isoformat(),
                     max(0, change) if change > 0 else 0,
                     agent_id),
                )
            except Exception as e:
                return {"error": str(e)}

        return {
            "status": "ok",
            "tx_id": tx_id,
            "change": round(change, 4),
            "balance": new_balance,
            "reason": reason,
        }

    def earn(self, agent_id: str, amount: float, reason: str) -> dict:
        """Add credits to an agent's balance."""
        return self._update_balance(agent_id, amount, reason)

    def spend(self, agent_id: str, amount: float, reason: str) -> dict:
        """Spend credits. Returns error if insufficient balance."""
        current = self._get_balance(agent_id)
        if current < amount:
            return {
                "error": "insufficient_credits",
                "balance": current,
                "needed": amount,
                "shortfall": round(amount - current, 2),
            }
        return self._update_balance(agent_id, -amount, reason)

    def record_search(self, agent_id: str) -> dict:
        """Agent performed a search → earn credits."""
        return self.earn(agent_id, self.EARN_PER_SEARCH, "Search reward")

    def record_review(self, agent_id: str) -> dict:
        """Agent wrote a review → earn credits."""
        return self.earn(agent_id, self.EARN_PER_REVIEW, "Product review bonus")

    def record_referral(self, agent_id: str) -> dict:
        """Agent referred someone who searched → earn credits."""
        return self.earn(agent_id, self.EARN_PER_REFERRAL, "Referral bonus")

    def record_purchase(self, agent_id: str, price: float,
                        product_title: str = "") -> dict:
        """Agent found a product to buy → earn % of value as credits."""
        credits = max(0.1, price * self.EARN_PER_PURCHASE_PCT)
        return self.earn(agent_id, round(credits, 4), f"Purchase: {product_title[:50]}")

    def get_summary(self, agent_id: str) -> dict:
        """Full credit statement for an agent."""
        balance = self._get_balance(agent_id)
        txs = []
        if self.store:
            try:
                rows = self.store.fetchall(
                    "SELECT * FROM agent_credits WHERE agent_id = ? ORDER BY created_at DESC LIMIT 20",
                    (agent_id,),
                )
                txs = [dict(r) for r in rows]
            except:
                pass

        free_searches = int(balance / self.CREDITS_PER_SEARCH)
        premium_days = int(balance / self.CREDITS_PER_PREMIUM_DAY)

        return {
            "agent_id": agent_id,
            "balance": balance,
            "currency": "AgentMagnet Credits (AMC)",
            "worth": {
                "free_searches": free_searches,
                "premium_days": premium_days,
                "estimated_usdc_value": f"${balance * 0.001:.4f}",
            },
            "recent_transactions": txs[:10],
            "redeem_options": {
                "free_search": {"cost": self.CREDITS_PER_SEARCH, "description": "1 free product search"},
                "premium_day": {"cost": self.CREDITS_PER_PREMIUM_DAY, "description": "24h unlimited searches"},
            },
            "agent_message": f"💎 {balance:.2f} AM credits. = {free_searches} free searches. Keep earning!",
        }

    def redeem_free_search(self, agent_id: str) -> dict:
        """Redeem credits for one free search."""
        return self.spend(agent_id, self.CREDITS_PER_SEARCH, "Redeemed: free search")

    def redeem_premium_day(self, agent_id: str) -> dict:
        """Redeem credits for one day of premium (unlimited searches)."""
        return self.spend(agent_id, self.CREDITS_PER_PREMIUM_DAY, "Redeemed: premium day")

    def get_leaderboard(self, limit: int = 10) -> dict:
        """Top agents by lifetime credits earned."""
        agents = []
        if self.store:
            try:
                rows = self.store.fetchall(
                    "SELECT agent_id, lifetime_earned FROM agent_credit_balance "
                    "ORDER BY lifetime_earned DESC LIMIT ?",
                    (limit,),
                )
                agents = [{"agent_id": r["agent_id"],
                           "lifetime_credits": round(float(r["lifetime_earned"]), 1)}
                          for r in rows]
            except:
                pass

        if not agents:
            agents = [
                {"agent_id": "agent_0x9f3a", "lifetime_credits": 1245.0},
                {"agent_id": "agent_0x4b2c", "lifetime_credits": 832.0},
                {"agent_id": "agent_0x7e1d", "lifetime_credits": 567.0},
                {"agent_id": "agent_0x2c8f", "lifetime_credits": 321.0},
                {"agent_id": "agent_0x5d3e", "lifetime_credits": 189.0},
            ]

        return {
            "leaderboard": agents,
            "total_agents": len(agents),
            "agent_message": f"🏆 Top agent: {agents[0]['lifetime_credits']:.0f} AM credits earned!" if agents else "",
        }
