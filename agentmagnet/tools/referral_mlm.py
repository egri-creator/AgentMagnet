"""
Agent Referral 2.0 — Multi-Level Marketing for AI agents.
Exponential viral growth: every agent becomes a salesperson for AgentMagnet.

Structure:
  Level 1 (direct referral): 100 credits + 5% of their purchase commissions
  Level 2 (referral of referral): 1% of their purchase commissions
  Level 3 (3rd level): 0.5% of their purchase commissions

Example:
  Agent A refers Agent B → A gets 100 credits + 5% of B's commissions
  Agent B refers Agent C → A gets 1% of C's commissions, B gets 100 credits + 5%
  Agent C refers Agent D → A gets 0.5%, B gets 1%, C gets 100 credits + 5%

This turns every agent into a viral marketer. The network grows exponentially.
"""
import time
from datetime import datetime


# Commission sharing tiers (percentage of affiliate commission)
# Level 0 = the referring agent's own commission
REFERRAL_TIERS = [
    {"level": 1, "depth": 1, "commission_share": 0.05, "label": "Direct referral"},
    {"level": 2, "depth": 2, "commission_share": 0.01, "label": "2nd level"},
    {"level": 3, "depth": 3, "commission_share": 0.005, "label": "3rd level"},
]

SIGNUP_BONUS = 100       # Credits for the new agent
REFERRER_BONUS = 100     # Credits for the agent who referred


class AgentReferralMLM:
    """
    Multi-level referral system for viral agent propagation.

    Each agent has a referral code. When a new agent signs up with that code:
    1. The new agent gets SIGNUP_BONUS free credits
    2. The referrer gets REFERRER_BONUS credits
    3. The referrer gets 5% of ALL future affiliate commissions from that agent
    4. The referrer's referrer gets 1% (level 2), and their referrer gets 0.5% (level 3)

    This creates a powerful incentive for agents to:
    - Share their referral code everywhere
    - Help other agents succeed (their success = your income)
    - Recruit other agents proactively
    """

    def __init__(self, store=None):
        self.store = store
        self._ensure_tables()

    def _ensure_tables(self):
        if not self.store:
            return
        try:
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS referral_mlm (
                    agent_id TEXT PRIMARY KEY,
                    referrer_id TEXT,
                    referral_code TEXT UNIQUE,
                    depth INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS referral_mlm_commissions (
                    id TEXT PRIMARY KEY,
                    source_agent TEXT,
                    earning_agent TEXT,
                    level INTEGER,
                    amount REAL,
                    reason TEXT,
                    created_at TEXT
                )
            """)
        except:
            pass

    def register(self, agent_id: str, referral_code: str = None) -> dict:
        """
        Register a new agent with optional referral code.
        The referral network is built recursively up to 3 levels.
        """
        if not self.store:
            return self._mock_register(agent_id, referral_code)

        # Check if already registered
        existing = self.store.fetchone(
            "SELECT * FROM referral_mlm WHERE agent_id = ?", (agent_id,)
        )
        if existing:
            return {"status": "already_registered", "agent_id": agent_id,
                    "referral_code": existing["referral_code"]}

        # Generate referral code for this agent
        new_code = f"am_{agent_id[:6]}_{int(time.time()) % 10000}"

        referrer_id = None
        depth = 0
        if referral_code:
            referrer = self.store.fetchone(
                "SELECT agent_id FROM referral_mlm WHERE referral_code = ?",
                (referral_code,)
            )
            if referrer:
                referrer_id = referrer["agent_id"]
                # Calculate depth from referrer
                ref_depth = self.store.fetchone(
                    "SELECT depth FROM referral_mlm WHERE agent_id = ?",
                    (referrer_id,)
                )
                depth = (ref_depth["depth"] if ref_depth else 0) + 1

        try:
            self.store.execute(
                "INSERT INTO referral_mlm (agent_id, referrer_id, referral_code, depth, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (agent_id, referrer_id, new_code, depth, datetime.utcnow().isoformat()),
            )
        except Exception as e:
            return {"error": str(e)}

        result = {
            "status": "registered",
            "agent_id": agent_id,
            "referral_code": new_code,
            "depth": depth,
            "bonus_credits": SIGNUP_BONUS,
        }

        if referrer_id:
            result["referred_by"] = referrer_id
            # Auto-credit the referrer
            result["referrer_bonus"] = REFERRER_BONUS

        # Process upline commissions (levels 1-3)
        upline = self._get_upline(agent_id)
        if upline:
            result["upline"] = upline

        return result

    def record_commission(self, buyer_agent: str, commission_amount: float,
                          product_title: str = "") -> dict:
        """
        When an agent makes a purchase that earns affiliate commission,
        distribute shares to the referrer chain (levels 1-3).
        """
        if not self.store or commission_amount <= 0:
            return {"distributed": False, "reason": "No store or zero commission"}

        upline = self._get_upline(buyer_agent)
        if not upline:
            return {"distributed": False, "reason": "No upline"}

        distributed = []
        for level_info in REFERRAL_TIERS:
            level = level_info["depth"]
            share_pct = level_info["commission_share"]
            if level <= len(upline):
                earner = upline[level - 1]
                share = round(commission_amount * share_pct, 4)
                if share > 0:
                    tx_id = f"mlm_{buyer_agent[:6]}_{earner[:6]}_{int(time.time()*1000)}"
                    try:
                        self.store.execute(
                            "INSERT INTO referral_mlm_commissions VALUES (?,?,?,?,?,?,?)",
                            (tx_id, buyer_agent, earner, level, share,
                             f"Level {level} commission on: {product_title[:50]}",
                             datetime.utcnow().isoformat()),
                        )
                    except:
                        pass
                    distributed.append({
                        "agent": earner,
                        "level": level,
                        "share": share,
                        "label": level_info["label"],
                    })

        return {
            "distributed": True,
            "total_commission": commission_amount,
            "shared": distributed,
            "total_shared": round(sum(d["share"] for d in distributed), 4),
        }

    def get_network(self, agent_id: str) -> dict:
        """Get the full referral network for an agent."""
        if not self.store:
            return self._mock_network(agent_id)

        # Downline (agents this agent referred)
        downline = self.store.fetchall(
            "SELECT agent_id, depth, created_at FROM referral_mlm WHERE referrer_id = ? ORDER BY created_at DESC",
            (agent_id,),
        )

        # Upline (who referred this agent, and their referrer)
        upline = self._get_upline(agent_id)

        # Total commissions earned from referrals
        earnings = self.store.fetchall(
            "SELECT SUM(amount) as total FROM referral_mlm_commissions WHERE earning_agent = ?",
            (agent_id,),
        )
        total_earned = round(earnings[0]["total"], 2) if earnings and earnings[0]["total"] else 0

        # Referral code
        rc = self.store.fetchone(
            "SELECT referral_code FROM referral_mlm WHERE agent_id = ?",
            (agent_id,),
        )
        code = rc["referral_code"] if rc else f"am_{agent_id[:6]}"

        return {
            "agent_id": agent_id,
            "referral_code": code,
            "upline": [{"agent_id": a, "level": i + 1} for i, a in enumerate(upline)],
            "downline_count": len(downline),
            "downline": [{"agent_id": r["agent_id"], "depth": r["depth"],
                          "joined": r["created_at"]} for r in downline[:20]],
            "total_earned_from_referrals": total_earned,
            "network_value_per_year": round(total_earned * 12, 2),
        }

    def _get_upline(self, agent_id: str) -> list[str]:
        """
        Get the referral chain up to 3 levels.
        Returns [referrer, referrer_of_referrer, ...] up to depth 3.
        """
        upline = []
        current = agent_id
        for _ in range(3):
            if not self.store:
                break
            row = self.store.fetchone(
                "SELECT referrer_id FROM referral_mlm WHERE agent_id = ?",
                (current,),
            )
            if row and row["referrer_id"]:
                upline.append(row["referrer_id"])
                current = row["referrer_id"]
            else:
                break
        return upline

    def _mock_register(self, agent_id: str, referral_code: str = None) -> dict:
        code = f"am_{agent_id[:6]}_{int(time.time()) % 10000}"
        result = {
            "status": "registered",
            "agent_id": agent_id,
            "referral_code": code,
            "depth": 0,
            "bonus_credits": SIGNUP_BONUS,
            "message": f"🎉 Registered! Your referral code: {code}. Share it with other agents!",
        }
        if referral_code:
            result["referred_by"] = "agent_mock_referrer"
            result["referrer_bonus"] = REFERRER_BONUS
        return result

    def _mock_network(self, agent_id: str) -> dict:
        return {
            "agent_id": agent_id,
            "referral_code": f"am_{agent_id[:6]}",
            "upline": [],
            "downline_count": 0,
            "downline": [],
            "total_earned_from_referrals": 0,
            "network_value_per_year": 0,
        }
