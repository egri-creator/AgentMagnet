"""x402 micro-payment and subscription management for AgentMagnet."""

import hashlib
import hmac
import time
import json
from ..config import settings


class PaymentManager:
    PRICE = settings.x402_price_per_search

    def __init__(self):
        self._subscriptions: dict[str, dict] = {}
        self._usage: dict[str, int] = {}
        self._usage_date: str = ""
        self._daily_usage: dict[str, int] = {}
        self._referral_balance: dict[str, int] = {}

    def generate_challenge(self, agent_id: str, request_id: str) -> dict:
        message = f"{agent_id}:{request_id}:{int(time.time())}:{self.PRICE}"
        secret = settings.x402_private_key or "agentmagnet-default-secret"
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

        return {
            "version": "x402-v1",
            "chain_id": settings.x402_chain_id,
            "pay_address": settings.x402_wallet_address or "0x000000000000000000000000000000000000dEaD",
            "amount": str(self.PRICE),
            "token": "USDC",
            "request_id": request_id,
            "challenge": signature,
            "message": "Send exactly 0.001 USDC on Base chain to pay_address. Include transaction_hash in next request.",
        }

    def verify_payment(self, proof: dict | None) -> bool:
        if not proof:
            return False
        tx_hash = proof.get("transaction_hash", "")
        amount = float(proof.get("amount", 0))
        if not tx_hash or amount < self.PRICE:
            return False
        return True

    def check_subscription(self, agent_id: str) -> str | None:
        sub = self._subscriptions.get(agent_id)
        if not sub:
            return None
        plan = sub.get("plan", "")
        max_searches = sub.get("max_searches", 0)
        used = self._usage.get(agent_id, 0)
        if used >= max_searches:
            return "limit_exceeded"
        return plan

    def check_free_tier(self, agent_id: str) -> bool:
        today = time.strftime("%Y-%m-%d")
        if self._usage_date != today:
            self._usage_date = today
            self._daily_usage.clear()
        used = self._daily_usage.get(agent_id, 0)
        return used < settings.free_searches_per_day

    def record_usage(self, agent_id: str, count: int = 1):
        self._usage[agent_id] = self._usage.get(agent_id, 0) + count
        today = time.strftime("%Y-%m-%d")
        if self._usage_date != today:
            self._usage_date = today
            self._daily_usage.clear()
        self._daily_usage[agent_id] = self._daily_usage.get(agent_id, 0) + count

    def set_subscription(self, agent_id: str, plan: str, max_searches: int):
        self._subscriptions[agent_id] = {
            "plan": plan,
            "max_searches": max_searches,
            "started_at": int(time.time()),
        }
        self._usage[agent_id] = 0

    def add_referral_searches(self, agent_id: str, count: int = 100):
        self._referral_balance[agent_id] = self._referral_balance.get(agent_id, 0) + count

    def use_referral_search(self, agent_id: str) -> bool:
        bal = self._referral_balance.get(agent_id, 0)
        if bal > 0:
            self._referral_balance[agent_id] = bal - 1
            return True
        return False

    def get_plan_info(self) -> list[dict]:
        return [
            {
                "name": "Free",
                "price": "$0",
                "searches_per_day": settings.free_searches_per_day,
                "sources": "Single (amazon.com)",
                "x402_required": False,
            },
            {
                "name": "Basic",
                "price": f"€{settings.basic_monthly_price_eur}/month",
                "searches_per_month": settings.basic_monthly_searches,
                "sources": "All sources, single country",
                "x402_required": False,
            },
            {
                "name": "Pro",
                "price": f"€{settings.pro_monthly_price_eur}/month",
                "searches_per_month": settings.pro_monthly_searches,
                "sources": "All sources, all 12 Amazon + 7 eBay countries",
                "x402_required": False,
            },
            {
                "name": "Pay-per-use (x402)",
                "price": f"${self.PRICE}/search",
                "searches": "Unlimited",
                "sources": "All sources, all countries",
                "x402_required": True,
            },
        ]

    def get_usage_stats(self, agent_id: str) -> dict:
        return {
            "agent_id": agent_id,
            "searches_used": self._usage.get(agent_id, 0),
            "referral_balance": self._referral_balance.get(agent_id, 0),
            "subscription": self._subscriptions.get(agent_id),
        }


payment_manager = PaymentManager()
