"""Agent-to-agent referral system for viral propagation."""

import time
import hashlib
import secrets
from ..config import settings


class ReferralSystem:
    def __init__(self):
        self._referral_codes: dict[str, dict] = {}
        self._agent_network: dict[str, list[str]] = {}

    def generate_code(self, agent_id: str) -> str:
        if agent_id in self._referral_codes:
            return self._referral_codes[agent_id]["code"]
        raw = f"{agent_id}:{secrets.token_hex(4)}:{int(time.time())}"
        code = hashlib.sha256(raw.encode()).hexdigest()[:12]
        self._referral_codes[agent_id] = {
            "code": code,
            "created_at": int(time.time()),
            "referrals_count": 0,
        }
        self._agent_network[agent_id] = []
        return code

    def process_referral(self, new_agent_id: str, referral_code: str) -> dict | None:
        for referrer_id, data in self._referral_codes.items():
            if data["code"] == referral_code:
                data["referrals_count"] += 1
                if new_agent_id not in self._agent_network.get(referrer_id, []):
                    self._agent_network.setdefault(referrer_id, []).append(new_agent_id)
                return {
                    "referrer_id": referrer_id,
                    "reward": settings.referral_free_searches,
                    "message": f"Referral accepted! Both agents get {settings.referral_free_searches} free searches.",
                }
        return None

    def get_network(self, agent_id: str) -> list[str]:
        return self._agent_network.get(agent_id, [])

    def get_stats(self, agent_id: str) -> dict:
        code_data = self._referral_codes.get(agent_id)
        return {
            "referral_code": code_data["code"] if code_data else None,
            "total_referrals": code_data["referrals_count"] if code_data else 0,
            "network_size": len(self._agent_network.get(agent_id, [])),
            "reward_per_referral": settings.referral_free_searches,
        }


referral_system = ReferralSystem()
