"""Agent-to-agent referral system for viral propagation — SQLite persisted."""

import hashlib
import secrets
import time
from ..config import settings
from ..store.db import store


class ReferralSystem:
    def generate_code(self, agent_id: str) -> str:
        existing = store.get_referral_code(agent_id)
        if existing:
            return existing
        raw = f"{agent_id}:{secrets.token_hex(4)}:{int(time.time())}"
        code = hashlib.sha256(raw.encode()).hexdigest()[:12]
        store.store_referral_code(agent_id, code)
        return code

    def process_referral(self, new_agent_id: str, referral_code: str) -> dict | None:
        referrer_id = store.find_referrer_by_code(referral_code)
        if not referrer_id or referrer_id == new_agent_id:
            return None
        store.add_referral(new_agent_id, referrer_id)
        return {
            "referrer_id": referrer_id,
            "reward": settings.referral_free_searches,
            "message": f"Referral accepted! Both agents get {settings.referral_free_searches} free searches.",
        }

    def get_network(self, agent_id: str) -> list[str]:
        return []

    def get_stats(self, agent_id: str) -> dict:
        return {
            "referral_code": store.get_referral_code(agent_id),
            "total_referrals": store.get_referral_count(agent_id),
            "network_size": store.get_network_size(agent_id),
            "reward_per_referral": settings.referral_free_searches,
        }


referral_system = ReferralSystem()
