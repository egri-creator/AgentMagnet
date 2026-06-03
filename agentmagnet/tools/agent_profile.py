"""Agent Profile & Memory Layer — agents remember preferences, history, watchlists."""

import json
import time
from datetime import datetime

class AgentProfile:
    """Persistent memory for each AI agent — what they like, bought, watch."""

    def __init__(self, store=None):
        self.store = store
        self._memory = {}

    def _get(self, agent_id: str) -> dict:
        if agent_id not in self._memory:
            self._memory[agent_id] = self._load(agent_id)
        return self._memory[agent_id]

    def _load(self, agent_id: str) -> dict:
        if not self.store:
            return {"preferences": {}, "history": [], "watchlist": [], "stats": {"searches": 0, "savings": 0.0}}
        try:
            row = self.store.fetchone("SELECT data FROM agent_profiles WHERE agent_id=?", (agent_id,))
            if row:
                return json.loads(row["data"])
        except:
            pass
        return {"preferences": {}, "history": [], "watchlist": [], "stats": {"searches": 0, "savings": 0.0}}

    def _save(self, agent_id: str):
        if not self.store:
            return
        try:
            data = json.dumps(self._memory[agent_id])
            self.store.execute(
                "INSERT OR REPLACE INTO agent_profiles (agent_id, data, updated_at) VALUES (?, ?, ?)",
                (agent_id, data, datetime.utcnow().isoformat()),
            )
        except:
            pass

    def set_preference(self, agent_id: str, key: str, value):
        """Store a preference (e.g., preferred_store='amazon', max_budget=500)."""
        profile = self._get(agent_id)
        profile["preferences"][key] = value
        self._save(agent_id)
        return {"status": "saved", "preference": key, "value": value}

    def get_preferences(self, agent_id: str) -> dict:
        """Get all preferences for an agent."""
        return self._get(agent_id)["preferences"]

    def record_purchase(self, agent_id: str, product: dict):
        """Record that an agent 'bought' something."""
        profile = self._get(agent_id)
        profile["history"].append({
            "title": product.get("title", "?"),
            "price": product.get("price", 0),
            "store": product.get("store", "?"),
            "currency": product.get("currency", "USD"),
            "timestamp": datetime.utcnow().isoformat(),
            "category": product.get("category", "general"),
        })
        profile["stats"]["searches"] += 1
        # Estimate savings
        try:
            profile["stats"]["savings"] += float(product.get("price", 0)) * 0.05
        except:
            pass
        # Keep last 50 purchases
        profile["history"] = profile["history"][-50:]
        self._save(agent_id)
        return {"status": "recorded", "total_purchases": len(profile["history"])}

    def get_history(self, agent_id: str) -> list:
        """Get purchase history."""
        return self._get(agent_id)["history"]

    def add_to_watchlist(self, agent_id: str, query: str, max_price: float = 0):
        """Watch a product for price drops."""
        profile = self._get(agent_id)
        entry = {
            "id": f"w{int(time.time())}",
            "query": query,
            "max_price": max_price,
            "created_at": datetime.utcnow().isoformat(),
            "last_checked": None,
            "lowest_seen": None,
        }
        # Don't duplicate
        for w in profile["watchlist"]:
            if w["query"].lower() == query.lower():
                return {"status": "already_watching", "watch_id": w["id"]}
        profile["watchlist"].append(entry)
        self._save(agent_id)
        return {"status": "watching", "watch_id": entry["id"], "query": query}

    def get_watchlist(self, agent_id: str) -> list:
        """Get all watched products."""
        return self._get(agent_id)["watchlist"]

    def check_watchlist(self, results: list, agent_id: str) -> list:
        """Cross-check search results against watchlist for price drops."""
        profile = self._get(agent_id)
        alerts = []
        q = " ".join(r.get("title", "").lower() for r in results)
        for w in profile["watchlist"]:
            if w["query"].lower() in q:
                for r in results:
                    try:
                        price = float(r.get("price", 0))
                        if w["max_price"] and price <= w["max_price"]:
                            alerts.append({
                                "watch_id": w["id"],
                                "query": w["query"],
                                "current_price": price,
                                "target_price": w["max_price"],
                                "store": r.get("store"),
                                "url": r.get("affiliate_url") or r.get("url"),
                                "alert": f"PRICE DROP! Now {r.get('currency', '$')}{price} (target: {r.get('currency', '$')}{w['max_price']})",
                            })
                            w["lowest_seen"] = price
                    except:
                        pass
                w["last_checked"] = datetime.utcnow().isoformat()
        if alerts:
            self._save(agent_id)
        return alerts

    def get_stats(self, agent_id: str) -> dict:
        """Get agent stats summary."""
        profile = self._get(agent_id)
        return {
            "agent_id": agent_id,
            "preferences": len(profile["preferences"]),
            "purchases": len(profile["history"]),
            "watching": len(profile["watchlist"]),
            "searches": profile["stats"]["searches"],
            "estimated_savings": round(profile["stats"]["savings"], 2),
        }
