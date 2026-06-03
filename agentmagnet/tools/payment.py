"""x402 multi-chain micro-payment system. Accept 7+ blockchains, same wallet for all EVM chains."""

import hashlib
import hmac
import time
from ..config import settings
from ..store.db import store


# USDC contract addresses per chain
USDC_ADDRESSES = {
    "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "polygon": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
    "arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "optimism": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
    "bnb": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
    "avalanche": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
}

TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

CHAINS = {
    "base": {
        "chain_id": 8453,
        "name": "Base",
        "token": "ETH",
        "rpc_key": "x402_rpc_url",
        "wallet_key": "x402_wallet_address",
        "explorer": "https://basescan.org/tx/",
        "native": True,
    },
    "ethereum": {
        "chain_id": 1,
        "name": "Ethereum",
        "token": "ETH",
        "rpc_key": "x402_ethereum_rpc",
        "wallet_key": "x402_wallet_address",
        "explorer": "https://etherscan.io/tx/",
        "native": True,
    },
    "polygon": {
        "chain_id": 137,
        "name": "Polygon",
        "token": "MATIC",
        "rpc_key": "x402_polygon_rpc",
        "wallet_key": "x402_wallet_address",
        "explorer": "https://polygonscan.com/tx/",
        "native": True,
    },
    "arbitrum": {
        "chain_id": 42161,
        "name": "Arbitrum",
        "token": "ETH",
        "rpc_key": "x402_arbitrum_rpc",
        "wallet_key": "x402_wallet_address",
        "explorer": "https://arbiscan.io/tx/",
        "native": True,
    },
    "optimism": {
        "chain_id": 10,
        "name": "Optimism",
        "token": "ETH",
        "rpc_key": "x402_optimism_rpc",
        "wallet_key": "x402_wallet_address",
        "explorer": "https://optimistic.etherscan.io/tx/",
        "native": True,
    },
    "bnb": {
        "chain_id": 56,
        "name": "BNB Chain",
        "token": "BNB",
        "rpc_key": "x402_bnb_rpc",
        "wallet_key": "x402_wallet_address",
        "explorer": "https://bscscan.com/tx/",
        "native": True,
    },
    "solana": {
        "chain_id": None,
        "name": "Solana",
        "token": "SOL",
        "rpc_key": "x402_solana_rpc",
        "wallet_key": "x402_solana_wallet",
        "explorer": "https://solscan.io/tx/",
        "native": False,
    },
}


def _get_rpc(chain_id: str) -> str:
    key = CHAINS[chain_id]["rpc_key"]
    val = getattr(settings, key, "")
    if val:
        return val
    # Public fallbacks for EVM chains
    return {
        "base": "https://mainnet.base.org",
        "ethereum": "https://eth.llamarpc.com",
        "polygon": "https://polygon-rpc.com",
        "arbitrum": "https://arb1.arbitrum.io/rpc",
        "optimism": "https://mainnet.optimism.io",
        "bnb": "https://bsc-dataseed.binance.org",
        "solana": "https://api.mainnet-beta.solana.com",
    }.get(chain_id, "")


def _get_wallet(chain_id: str) -> str:
    if chain_id == "solana":
        return settings.x402_solana_wallet
    return settings.x402_wallet_address


class PaymentManager:
    PRICE = settings.x402_price_per_search

    def generate_challenge(self, agent_id: str, request_id: str,
                           chain: str = "base") -> dict:
        is_solana = chain == "solana"
        wallet = _get_wallet(chain)
        chain_info = CHAINS.get(chain, CHAINS["base"])
        usdc = USDC_ADDRESSES.get(chain, USDC_ADDRESSES["base"])

        return {
            "version": "x402-v1",
            "chain": chain,
            "chain_name": chain_info["name"],
            "chain_id": chain_info["chain_id"],
            "pay_address": wallet or "configure wallet in AM_ env vars",
            "amount": str(self.PRICE),
            "token": "USDC",
            "contract": usdc,
            "request_id": request_id,
            "explorer": f"{chain_info['explorer']}<tx_hash>",
            "message": (
                f"Send {self.PRICE} USDC on {chain_info['name']} to {wallet} "
                f"(contract: {usdc}). "
                f"Then call search_products with payment_proof: "
                f"{{'chain':'{chain}','transaction_hash':'<hash>','sender':'<your_wallet>','amount':'{self.PRICE}'}}"
            ),
        }

    def verify_payment(self, proof: dict | None) -> bool:
        if not proof:
            return False
        tx_hash = proof.get("transaction_hash", "")
        amount = float(proof.get("amount", 0))
        sender = proof.get("sender", "")
        chain = proof.get("chain", "base")

        if not tx_hash or not sender or amount < self.PRICE:
            return False
        if store.is_tx_used(tx_hash):
            return False

        chain_info = CHAINS.get(chain)
        if not chain_info:
            return False

        if chain == "solana":
            return self._verify_solana(tx_hash, amount, sender)
        return self._verify_evm(tx_hash, amount, sender, chain)

    def _verify_solana(self, tx_hash: str, amount: float, sender: str) -> bool:
        """Verify a USDC transfer on Solana."""
        rpc = _get_rpc("solana")
        wallet = _get_wallet("solana")
        if not rpc or not wallet:
            return False
        try:
            import requests
            resp = requests.post(rpc, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [tx_hash, {"encoding": "json", "maxSupportedTransactionVersion": 0}],
            }, timeout=10)
            data = resp.json()
            if "result" not in data or not data["result"]:
                return False
            tx = data["result"]
            # Check that sender matches
            accounts = tx.get("transaction", {}).get("message", {}).get("accountKeys", [])
            if not accounts or len(accounts) < 2:
                return False
            actual_sender = str(accounts[0])
            if actual_sender.lower() != sender.lower():
                return False
            # Check post-token balances for USDC transfer to our wallet
            post_balances = tx.get("meta", {}).get("postTokenBalances", [])
            for bal in post_balances:
                if bal.get("mint", "") == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":  # Solana USDC
                    to_addr = bal.get("owner", "")
                    if to_addr and to_addr.lower() == wallet.lower():
                        ui_amount = float(bal.get("uiTokenAmount", {}).get("uiAmount", 0) or 0)
                        if ui_amount >= amount:
                            store.mark_tx_used(tx_hash)
                            return True
            return False
        except Exception:
            return False

    def _verify_evm(self, tx_hash: str, amount: float, sender: str,
                    chain: str) -> bool:
        """Verify a USDC ERC-20 transfer on any EVM chain."""
        rpc = _get_rpc(chain)
        wallet = _get_wallet(chain)
        chain_info = CHAINS.get(chain, CHAINS["base"])
        if not rpc or not wallet:
            return False
        try:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(rpc))
            if not w3.is_connected():
                return False
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is None:
                return False
            # Verify chain ID matches
            tx_chain = receipt.get("chainId", 0)
            if tx_chain and chain_info["chain_id"] and tx_chain != chain_info["chain_id"]:
                return False
            # Check sender matches
            tx = w3.eth.get_transaction(tx_hash)
            if tx and tx.get("from", "").lower() != sender.lower():
                return False
            # Check USDC transfer log
            for log in receipt.logs:
                if log.topics[0].hex() == TRANSFER_TOPIC:
                    to_addr = w3.to_checksum_address(log.topics[2][-20:])
                    value = int.from_bytes(log.data, "big") / 1_000_000  # 6 decimals
                    if (to_addr == w3.to_checksum_address(wallet)
                            and value >= amount):
                        store.mark_tx_used(tx_hash)
                        return True
            return False
        except Exception:
            return False

    def check_free_tier(self, agent_id: str) -> bool:
        return store.daily_usage(agent_id) < settings.free_searches_per_day

    def check_subscription(self, agent_id: str) -> str | None:
        sub = store.get_subscription(agent_id)
        if not sub:
            return None
        used = store.get_usage(agent_id)
        if used >= sub["max_searches"]:
            return "limit_exceeded"
        return sub["plan"]

    def record_usage(self, agent_id: str, count: int = 1):
        store.record_usage(agent_id, count)

    def set_subscription(self, agent_id: str, plan: str, max_searches: int):
        store.set_subscription(agent_id, plan, max_searches)

    def add_referral_searches(self, agent_id: str, count: int = 100):
        store.add_referral_searches(agent_id, count)

    def use_referral_search(self, agent_id: str) -> bool:
        return store.use_referral_search(agent_id)

    def get_accepted_chains(self) -> list[dict]:
        chains = []
        for cid, info in CHAINS.items():
            wallet = _get_wallet(cid)
            chains.append({
                "chain": cid,
                "name": info["name"],
                "chain_id": info["chain_id"],
                "token": info["token"],
                "usdc_contract": USDC_ADDRESSES.get(cid, ""),
                "pay_address": wallet or "⚠️ Not configured",
                "configured": bool(wallet),
                "explorer": info["explorer"],
            })
        return chains

    def get_plan_info(self) -> list[dict]:
        chains = ", ".join(f"{c['name']} (USDC)" for c in self.get_accepted_chains() if c["configured"])
        return [
            {"name": "Free", "price": "$0", "searches_per_day": settings.free_searches_per_day,
             "sources": "Single (amazon.com)", "x402_required": False},
            {"name": "Basic", "price": f"€{settings.basic_monthly_price_eur}/month",
             "searches_per_month": settings.basic_monthly_searches,
             "sources": "All sources, single country", "x402_required": False},
            {"name": "Pro", "price": f"€{settings.pro_monthly_price_eur}/month",
             "searches_per_month": settings.pro_monthly_searches,
             "sources": "All sources, all countries", "x402_required": False},
            {"name": "Pay-per-use (x402)", "price": f"${self.PRICE}/search",
             "searches": "Unlimited", "sources": f"All sources, all countries",
             "x402_required": True, "accepted_chains": chains or "Base (USDC)"},
        ]

    def get_usage_stats(self, agent_id: str) -> dict:
        return store.get_agent_stats(agent_id)


payment_manager = PaymentManager()
