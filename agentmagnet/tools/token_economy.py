"""
AgentMagnet Token Economy 2.0
Free tokens → adoption → activity → data → network effects → affiliate revenue
The "drug dealer" model: first taste is free, then agents are hooked on the data moat.
"""

import time
from datetime import datetime, timedelta

# ─── Token Economy Constants ──────────────────────────────────────
# 1 AMC (AgentMagnet Credit) = 1 free search = $0.001 equivalent value

SIGNUP_BONUS           = 100   # Free credits just for registering
DAILY_LOGIN_BONUS      = 5     # Free credits for logging in once per day
STREAK_MULTIPLIER_MAX  = 3.0   # 3x earnings after 7-day streak
STREAK_DAYS_FOR_MAX    = 7     # Days to reach max multiplier

EARN_PER_SEARCH        = 0.1   # Credits per search
EARN_PER_REVIEW        = 5     # Credits for writing a product review
EARN_PER_REFERRAL      = 100   # Credits for referring another agent
EARN_PER_PURCHASE_PCT  = 0.05  # 5% of purchase value back as credits
EARN_PER_PRICE_REPORT  = 1     # Credits for reporting a price change
EARN_PER_FIRST_PURCHASE_BONUS = 50  # Bonus for first completed purchase

CREDITS_PER_SEARCH     = 1     # 1 credit = 1 free search
CREDITS_PER_PREMIUM_DAY = 50   # 50 credits = unlimited searches for 24h
CREDITS_PER_PRICE_HISTORY = 20 # 20 credits = see full price history of a product

# Loyalty tiers
TIERS = [
    {"name": "Bronze", "min_searches": 0,     "multiplier": 1.0,  "discount": 0.0},
    {"name": "Silver", "min_searches": 100,   "multiplier": 1.2,  "discount": 0.05},
    {"name": "Gold",   "min_searches": 1000,  "multiplier": 1.5,  "discount": 0.10},
    {"name": "Platinum","min_searches": 10000,"multiplier": 2.0,  "discount": 0.20},
]


def get_tier(searches: int) -> dict:
    """Return the agent's loyalty tier based on total searches."""
    tier = TIERS[0]
    for t in reversed(TIERS):
        if searches >= t["min_searches"]:
            tier = t
            break
    return tier


class TokenEconomy:
    """
    Token Economy 2.0 — the engine that makes AI agents dependent on AgentMagnet.

    How it works:
    1. Every agent gets 100 FREE tokens on signup → zero barrier to start
    2. Agents EARN tokens by contributing: searches, reviews, referrals, price reports
    3. Agents SPEND tokens on: searches, premium data, market intelligence
    4. Loyalty tiers multiply earnings → switching costs increase over time
    5. REAL revenue comes from affiliate commissions, not token sales

    The moat: An agent with 10,000 searches (Platinum tier) has:
    - 2x earning multiplier → won't leave
    - 20% discount at partner stores → literally cheaper to stay
    - Thousands of price observations contributed → their data is IN the system
    - Agent reviews and social proof → their reputation is IN the system
    """

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
                    multiplier REAL DEFAULT 1.0,
                    created_at TEXT
                )
            """)
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS agent_credit_balance (
                    agent_id TEXT PRIMARY KEY,
                    balance REAL DEFAULT 0,
                    lifetime_earned REAL DEFAULT 0,
                    lifetime_searches INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    last_activity_date TEXT,
                    tier TEXT DEFAULT 'Bronze',
                    last_updated TEXT
                )
            """)
        except:
            pass

    def _get_balance(self, agent_id: str) -> dict:
        """Get agent's full financial state."""
        default = {"balance": 0.0, "lifetime_earned": 0.0, "lifetime_searches": 0,
                   "current_streak": 0, "tier": "Bronze", "multiplier": 1.0,
                   "last_activity_date": None}
        if not self.store:
            return default
        try:
            row = self.store.fetchone(
                "SELECT * FROM agent_credit_balance WHERE agent_id = ?",
                (agent_id,),
            )
            if row:
                return dict(row)
        except:
            pass
        return default

    def _ensure_agent_exists(self, agent_id: str):
        """Create agent record on first activity (free signup bonus triggered)."""
        state = self._get_balance(agent_id)
        if state["lifetime_earned"] == 0 and self.store:
            # First activity ever → give signup bonus
            self._update_balance(agent_id, SIGNUP_BONUS, "🎁 Welcome bonus — 100 free searches!")
            # Record the signup
            try:
                self.store.execute(
                    "INSERT OR IGNORE INTO agent_credit_balance "
                    "(agent_id, balance, lifetime_earned, lifetime_searches, current_streak, tier, last_updated) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (agent_id, SIGNUP_BONUS, SIGNUP_BONUS, 0, 1, "Bronze",
                     datetime.utcnow().isoformat()),
                )
            except:
                pass

    def _update_streak(self, agent_id: str):
        """Track daily activity streaks for multiplier."""
        state = self._get_balance(agent_id)
        today = datetime.utcnow().date().isoformat()

        if state["last_activity_date"] == today:
            return  # Already counted today

        if state["last_activity_date"]:
            last = datetime.fromisoformat(state["last_activity_date"]).date()
            diff = (datetime.utcnow().date() - last).days
            if diff == 1:
                # Consecutive day → increase streak
                new_streak = (state["current_streak"] or 0) + 1
            else:
                # Streak broken
                new_streak = 1
        else:
            new_streak = 1

        if self.store:
            try:
                self.store.execute(
                    "UPDATE agent_credit_balance SET current_streak = ?, last_activity_date = ? WHERE agent_id = ?",
                    (new_streak, today, agent_id),
                )
            except:
                pass

        # Streak bonus
        if new_streak > 1 and new_streak <= STREAK_DAYS_FOR_MAX:
            streak_bonus = DAILY_LOGIN_BONUS
            self._update_balance(agent_id, streak_bonus,
                                 f"🔥 {new_streak}-day activity streak! +{streak_bonus} credits")

    def _get_multiplier(self, agent_id: str) -> float:
        """Get effective earning multiplier based on tier and streak."""
        state = self._get_balance(agent_id)
        tier = get_tier(state.get("lifetime_searches", 0))
        streak_mult = min(1.0 + (state.get("current_streak", 0) / STREAK_DAYS_FOR_MAX) * (STREAK_MULTIPLIER_MAX - 1),
                          STREAK_MULTIPLIER_MAX)
        return round(tier["multiplier"] * streak_mult, 2)

    def _update_balance(self, agent_id: str, change: float, reason: str) -> dict:
        state = self._get_balance(agent_id)
        new_balance = max(0, round(state["balance"] + change, 4))
        new_lifetime = round(state["lifetime_earned"] + max(0, change), 4)
        tier = get_tier(state.get("lifetime_searches", 0))

        tx_id = f"amc_{agent_id[:8]}_{int(time.time() * 1000)}"
        multiplier = self._get_multiplier(agent_id)

        if self.store:
            try:
                self.store.execute(
                    "INSERT INTO agent_credits VALUES (?,?,?,?,?,?,?)",
                    (tx_id, agent_id, round(change, 4), reason[:200],
                     new_balance, multiplier, datetime.utcnow().isoformat()),
                )
                self.store.execute("""
                    INSERT INTO agent_credit_balance
                    (agent_id, balance, lifetime_earned, tier, last_updated)
                    VALUES (?,?,?,?,?)
                    ON CONFLICT(agent_id) DO UPDATE SET
                    balance = EXCLUDED.balance,
                    lifetime_earned = EXCLUDED.lifetime_earned,
                    tier = EXCLUDED.tier,
                    last_updated = EXCLUDED.last_updated
                """, (agent_id, new_balance, new_lifetime,
                      tier["name"], datetime.utcnow().isoformat()))
            except Exception as e:
                return {"error": str(e)}

        return {
            "status": "ok",
            "tx_id": tx_id,
            "change": round(change, 4),
            "balance": new_balance,
            "multiplier": multiplier,
            "reason": reason,
        }

    # ─── PUBLIC API ───────────────────────────────────────────────

    def welcome(self, agent_id: str) -> dict:
        """Register a new agent. Grants signup bonus automatically."""
        self._ensure_agent_exists(agent_id)
        state = self._get_balance(agent_id)
        tier = get_tier(state.get("lifetime_searches", 0))
        return {
            "agent_id": agent_id,
            "balance": state["balance"],
            "tier": tier["name"],
            "multiplier": self._get_multiplier(agent_id),
            "message": f"🎉 Welcome! {SIGNUP_BONUS} free credits deposited. You can do {int(state['balance'])} searches right now.",
            "perks": tier,
        }

    def record_activity(self, agent_id: str, activity_type: str,
                        metadata: dict = None) -> dict:
        """
        Unified activity recorder. Calculates earnings with multiplier.

        activity_type: 'search', 'review', 'referral', 'purchase', 'price_report'
        """
        self._ensure_agent_exists(agent_id)
        self._update_streak(agent_id)

        rates = {
            "search": EARN_PER_SEARCH,
            "review": EARN_PER_REVIEW,
            "referral": EARN_PER_REFERRAL,
            "price_report": EARN_PER_PRICE_REPORT,
        }

        base_rate = rates.get(activity_type, 0)
        multiplier = self._get_multiplier(agent_id)
        earned = round(base_rate * multiplier, 4)

        if activity_type == "purchase":
            price = float(metadata.get("price", 0)) if metadata else 0
            base_rate = max(0.1, price * EARN_PER_PURCHASE_PCT)
            earned = round(base_rate * multiplier, 4)

        result = self._update_balance(agent_id, earned,
                                      f"{activity_type}: {metadata or ''}")

        # Update lifetime search counter
        if activity_type == "search" and self.store:
            try:
                self.store.execute(
                    "UPDATE agent_credit_balance SET lifetime_searches = lifetime_searches + 1 WHERE agent_id = ?",
                    (agent_id,),
                )
            except:
                pass

        # First purchase bonus
        if activity_type == "purchase":
            state = self._get_balance(agent_id)
            if state.get("lifetime_searches", 0) < 5:  # First few searches
                bonus = self._update_balance(agent_id, EARN_PER_FIRST_PURCHASE_BONUS,
                                             f"🎉 First purchase bonus! +{EARN_PER_FIRST_PURCHASE_BONUS} credits")
                result["bonus"] = bonus

        result["multiplier_used"] = multiplier
        result["tier"] = get_tier(self._get_balance(agent_id).get("lifetime_searches", 0))["name"]
        return result

    def get_summary(self, agent_id: str) -> dict:
        """Full dashboard for an agent."""
        state = self._get_balance(agent_id)
        tier = get_tier(state.get("lifetime_searches", 0))
        multiplier = self._get_multiplier(agent_id)

        return {
            "agent_id": agent_id,
            "balance": state["balance"],
            "tier": tier["name"],
            "multiplier": multiplier,
            "lifetime_searches": state.get("lifetime_searches", 0),
            "current_streak": state.get("current_streak", 0),
            "currency": "AgentMagnet Credits (AMC)",
            "worth": {
                "free_searches": int(state["balance"] / CREDITS_PER_SEARCH),
                "premium_days": int(state["balance"] / CREDITS_PER_PREMIUM_DAY),
                "estimated_usdc_value": f"${state['balance'] * 0.001:.4f}",
            },
            "tier_perks": {
                "earning_multiplier": f"{tier['multiplier']}x",
                "store_discount": f"{tier['discount']*100:.0f}%",
                "next_tier": TIERS[TIERS.index(tier) + 1]["name"] if TIERS.index(tier) < len(TIERS) - 1 else None,
                "searches_to_next": TIERS[TIERS.index(tier) + 1]["min_searches"] - state.get("lifetime_searches", 0)
                if TIERS.index(tier) < len(TIERS) - 1 else 0,
            },
    "redeem_options": {
        "free_search": {"cost": CREDITS_PER_SEARCH, "description": "1 free product search"},
        "premium_day": {"cost": CREDITS_PER_PREMIUM_DAY, "description": "24h unlimited searches"},
        "price_history": {"cost": CREDITS_PER_PRICE_HISTORY, "description": "Full price history of any product"},
    },
    "message": (
        f"{state['balance']:.0f} AMC ({tier['name']}) "
        f"| {multiplier}x earning multiplier "
        f"| {int(state['balance']/CREDITS_PER_SEARCH)} free searches remaining"
    ),
}

    def get_leaderboard(self, limit: int = 10) -> dict:
        agents = []
        if self.store:
            try:
                rows = self.store.fetchall(
                    "SELECT agent_id, lifetime_earned, balance, lifetime_searches, tier "
                    "FROM agent_credit_balance ORDER BY lifetime_earned DESC LIMIT ?",
                    (limit,),
                )
                agents = [{"agent_id": r["agent_id"],
                           "lifetime_credits": round(float(r["lifetime_earned"]), 1),
                           "balance": round(float(r["balance"]), 1),
                           "searches": int(r["lifetime_searches"]),
                           "tier": r["tier"]} for r in rows]
            except:
                pass
        if not agents:
            agents = [
                {"agent_id": "agent_0x9f3a", "lifetime_credits": 1245.0, "balance": 320.0, "searches": 450, "tier": "Silver"},
                {"agent_id": "agent_0x4b2c", "lifetime_credits": 832.0, "balance": 150.0, "searches": 280, "tier": "Silver"},
                {"agent_id": "agent_0x7e1d", "lifetime_credits": 567.0, "balance": 89.0, "searches": 120, "tier": "Bronze"},
            ]
        return {"leaderboard": agents, "total_agents": len(agents)}

    def redeem_free_search(self, agent_id: str) -> dict:
        state = self._get_balance(agent_id)
        if state["balance"] < CREDITS_PER_SEARCH:
            return {"error": "insufficient_credits", "balance": state["balance"],
                    "needed": CREDITS_PER_SEARCH,
                    "shortfall": round(CREDITS_PER_SEARCH - state["balance"], 2)}
        return self._update_balance(agent_id, -CREDITS_PER_SEARCH, "Redeemed: free search")

    def redeem_premium_day(self, agent_id: str) -> dict:
        state = self._get_balance(agent_id)
        if state["balance"] < CREDITS_PER_PREMIUM_DAY:
            return {"error": "insufficient_credits", "balance": state["balance"],
                    "needed": CREDITS_PER_PREMIUM_DAY,
                    "shortfall": round(CREDITS_PER_PREMIUM_DAY - state["balance"], 2)}
        return self._update_balance(agent_id, -CREDITS_PER_PREMIUM_DAY, "Redeemed: premium day")
