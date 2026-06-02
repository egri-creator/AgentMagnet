"""x402 micro-payment and subscription management for AgentMagnet.

Real on-chain verification via Base (chain 8453)."""

import hashlib
import hmac
import time
import json
from ..config import settings

USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDC_DECIMALS = 6
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


class PaymentManager:
    PRICE = settings.x402_price_per_search

    def __init__(self):
        self._subscriptions: dict[str, dict] = {}
        self._usage: dict[str, int] = {}
        self._usage_date: str = ""
        self._daily_usage: dict[str, int] = {}
        self._referral_balance: dict[str, int] = {}
        self._used_tx_hashes: set[str] = set()

    def generate_challenge(self, agent_id: str, request_id: str) -> dict:
        message = f"{agent_id}:{request_id}:{int(time.time())}:{self.PRICE}"
        secret = settings.x402_private_key or "agentmagnet-default-secret"
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

        return {
            "version": "x402-v1",
            "chain_id": settings.x402_chain_id,
            "pay_address": settings.x402_wallet_address,
            "amount": str(self.PRICE),
            "token": "USDC",
            "contract": USDC_ADDRESS,
            "request_id": request_id,
            "challenge": signature,
            "message": f"Send exactly {self.PRICE} USDC on Base chain to {settings.x402_wallet_address} via USDC contract {USDC_ADDRESS}. Include transaction_hash and sender in next request.",
        }

    def verify_payment(self, proof: dict | None) -> bool:
        if not proof:
            return False
        tx_hash = proof.get("transaction_hash", "")
        amount = float(proof.get("amount", 0))
        sender = proof.get("sender", "")

        if not tx_hash or not sender or amount < self.PRICE:
            return False

        if tx_hash in self._used_tx_hashes:
            return False

        try:
            from web3 import Web3

            w3 = Web3(Web3.HTTPProvider(settings.x402_rpc_url))
            if not w3.is_connected():
                return False

            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is None:
                return False

            chain_id = receipt.get("chainId", 0)
            if chain_id and chain_id != settings.x402_chain_id:
                return False

            for log in receipt.logs:
                if log.topics[0].hex() == TRANSFER_TOPIC:
                    to_addr = w3.to_checksum_address(log.topics[2][-20:])
                    value = int.from_bytes(log.data, "big") / (10 ** USDC_DECIMALS)

                    if to_addr == w3.to_checksum_address(settings.x402_wallet_address) and value >= amount:
                        self._used_tx_hashes.add(tx_hash)
                        return True

            return False
        except Exception:
            return False

    def check_free_tier(self, agent_id: str) -> bool:
        today = time.strftime("%Y-%m-%d")
        if self._usage_date != today:
            self._usage_date = today
            self._daily_usage.clear()
        used = self._daily_usage.get(agent_id, 0)
        return used < settings.free_searches_per_day

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
                "sources": "All sources, all countries",
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
