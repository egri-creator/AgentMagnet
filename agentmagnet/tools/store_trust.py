"""Store Trust Scores — agents rate stores, not just products. Yelp for AI commerce."""

import time
from datetime import datetime


MOCK_STORE_SCORES = {
    "amazon": {"name": "Amazon", "score": 4.7, "reviews": 15234,
               "categories": {"shipping": 4.8, "returns": 4.6, "pricing": 4.5, "accuracy": 4.7, "support": 4.5}},
    "amazon.es": {"name": "Amazon España", "score": 4.5, "reviews": 3210,
                  "categories": {"shipping": 4.3, "returns": 4.4, "pricing": 4.4, "accuracy": 4.6, "support": 4.2}},
    "amazon.de": {"name": "Amazon DE", "score": 4.6, "reviews": 4532,
                  "categories": {"shipping": 4.7, "returns": 4.5, "pricing": 4.3, "accuracy": 4.6, "support": 4.4}},
    "amazon.co.uk": {"name": "Amazon UK", "score": 4.5, "reviews": 3891,
                     "categories": {"shipping": 4.6, "returns": 4.4, "pricing": 4.3, "accuracy": 4.5, "support": 4.3}},
    "ebay": {"name": "eBay", "score": 4.2, "reviews": 8932,
             "categories": {"shipping": 4.0, "returns": 4.1, "pricing": 4.5, "accuracy": 4.0, "support": 4.0}},
    "aliexpress": {"name": "AliExpress", "score": 3.8, "reviews": 6543,
                   "categories": {"shipping": 3.2, "returns": 3.5, "pricing": 4.8, "accuracy": 3.5, "support": 3.0}},
    "walmart": {"name": "Walmart", "score": 4.3, "reviews": 5678,
                "categories": {"shipping": 4.2, "returns": 4.3, "pricing": 4.4, "accuracy": 4.2, "support": 4.1}},
    "bestbuy": {"name": "Best Buy", "score": 4.4, "reviews": 4321,
                "categories": {"shipping": 4.3, "returns": 4.5, "pricing": 4.2, "accuracy": 4.5, "support": 4.3}},
    "target": {"name": "Target", "score": 4.4, "reviews": 3987,
               "categories": {"shipping": 4.4, "returns": 4.5, "pricing": 4.3, "accuracy": 4.4, "support": 4.2}},
}

# Store aliases for fuzzy matching
STORE_ALIASES = {
    "amazon": ["amazon", "amzn", "a.co", "amazon.com", "amazon.es", "amazon.de", "amazon.co.uk",
               "amazon.fr", "amazon.it", "amazon.co.jp", "amazon.ca"],
    "ebay": ["ebay", "ebay.com", "ebay.co.uk", "ebay.de", "ebay.fr"],
    "aliexpress": ["aliexpress", "aliexpress.com", "alibaba", "ali"],
    "walmart": ["walmart", "walmart.com", "wal-mart"],
    "bestbuy": ["bestbuy", "best buy", "bestbuy.com"],
    "target": ["target", "target.com"],
}


class StoreTrust:
    def __init__(self, store=None):
        self.store = store
        self._ensure_table()

    def _ensure_table(self):
        if not self.store:
            return
        try:
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS store_reviews (
                    id TEXT PRIMARY KEY,
                    store_id TEXT,
                    agent_id TEXT,
                    shipping_rating INTEGER,
                    returns_rating INTEGER,
                    pricing_rating INTEGER,
                    accuracy_rating INTEGER,
                    support_rating INTEGER,
                    overall_rating INTEGER,
                    review_text TEXT,
                    created_at TEXT
                )
            """)
            self.store.execute("""
                CREATE INDEX IF NOT EXISTS idx_store_reviews_store
                ON store_reviews(store_id)
            """)
        except:
            pass

    def _normalize_store(self, store_name: str) -> str:
        sn = store_name.lower().strip()
        for key, aliases in STORE_ALIASES.items():
            for a in aliases:
                if sn == a or sn.startswith(a + ".") or sn.startswith(a + "/") or sn.endswith("." + a):
                    return key
        # Direct check
        if sn in MOCK_STORE_SCORES:
            return sn
        return sn

    def get_score(self, store_name: str) -> dict:
        """Get trust score for a store."""
        store_id = self._normalize_store(store_name)

        # Check real reviews first
        real_avg = None
        real_count = 0
        real_cats = {}
        if self.store:
            try:
                rows = self.store.fetchall(
                    "SELECT * FROM store_reviews WHERE store_id = ?", (store_id,)
                )
                if rows:
                    real_count = len(rows)
                    real_avg = round(sum(r["overall_rating"] for r in rows) / real_count, 1)
                    for cat in ["shipping", "returns", "pricing", "accuracy", "support"]:
                        vals = [r[f"{cat}_rating"] for r in rows if r.get(f"{cat}_rating")]
                        if vals:
                            real_cats[cat] = round(sum(vals) / len(vals), 1)
            except:
                pass

        # Fall back to mock data
        mock = MOCK_STORE_SCORES.get(store_id, {
            "name": store_name.title(), "score": 4.0, "reviews": 0,
            "categories": {"shipping": 4.0, "returns": 4.0, "pricing": 4.0, "accuracy": 4.0, "support": 4.0},
        })

        avg = real_avg if real_avg is not None else mock["score"]
        count = real_count if real_count > 0 else mock["reviews"]
        cats = real_cats if real_cats else mock["categories"]

        return {
            "store": store_id,
            "store_name": mock["name"],
            "trust_score": avg,
            "total_reviews": count,
            "categories": cats,
            "rating_bar": self._bar(avg),
            "recommendation": self._recommend(avg),
            "agent_message": f"🏪 {mock['name']}: ★ {avg}/5 ({count} agent reviews). {self._recommend(avg)}",
        }

    def add_review(self, store_name: str, agent_id: str,
                   overall: int, shipping: int = 0, returns: int = 0,
                   pricing: int = 0, accuracy: int = 0, support: int = 0,
                   review_text: str = "") -> dict:
        """Add a store review from an agent."""
        store_id = self._normalize_store(store_name)
        review_id = f"sr_{agent_id[:8]}_{int(time.time())}"

        row = {
            "id": review_id,
            "store_id": store_id,
            "agent_id": agent_id,
            "shipping_rating": shipping or overall,
            "returns_rating": returns or overall,
            "pricing_rating": pricing or overall,
            "accuracy_rating": accuracy or overall,
            "support_rating": support or overall,
            "overall_rating": overall,
            "review_text": review_text[:500],
            "created_at": datetime.utcnow().isoformat(),
        }

        if self.store:
            try:
                self.store.execute(
                    "INSERT INTO store_reviews VALUES (?,?,?,?,?,?,?,?,?,?)",
                    tuple(row.values()),
                )
            except Exception as e:
                return {"error": str(e)}

        return {
            "status": "ok",
            "review_id": review_id,
            "store": store_id,
            "overall": overall,
            "message": f"✅ Store review added for '{store_name}'. Your rating helps other agents choose where to buy.",
        }

    def _bar(self, score: float) -> str:
        filled = max(1, round(score))
        return "★" * filled + "☆" * (5 - filled)

    def _recommend(self, score: float) -> str:
        if score >= 4.5:
            return "STRONGLY RECOMMENDED by AI agents."
        elif score >= 4.0:
            return "Recommended by AI agents."
        elif score >= 3.0:
            return "Use with caution — mixed reviews."
        elif score >= 2.0:
            return "NOT RECOMMENDED — poor agent reviews."
        return "AVOID — consistently bad ratings."

    def list_stores(self) -> dict:
        """List all stores with trust scores."""
        stores = []
        for sid, mock in MOCK_STORE_SCORES.items():
            score = self.get_score(sid)
            stores.append({
                "store_id": sid,
                "name": mock["name"],
                "score": score["trust_score"],
                "reviews": score["total_reviews"],
                "bar": score["rating_bar"],
            })
        stores.sort(key=lambda s: s["score"], reverse=True)
        return {"stores": stores, "total": len(stores)}
