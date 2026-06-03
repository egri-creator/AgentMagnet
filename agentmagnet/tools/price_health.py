"""Price Health Check — cross-agent price aggregation.
Shows real data: lowest price seen, average paid by agents, price trend."""
import time
from ..store.db import store


class PriceHealth:
    def __init__(self, store_conn=None):
        self.store = store_conn or store
        self._init_db()

    def _init_db(self):
        try:
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS price_health (
                    product_key TEXT PRIMARY KEY,
                    product_title TEXT,
                    lowest_seen REAL,
                    highest_seen REAL,
                    total_sum REAL,
                    total_observations INTEGER,
                    last_seen REAL,
                    first_seen REAL
                )
            """)
        except Exception:
            pass

    def record_price(self, title: str, price: float, store_name: str = ""):
        if not title or price <= 0:
            return
        key = title.lower().strip()[:120]
        now = time.time()
        try:
            row = self.store.fetchone("SELECT * FROM price_health WHERE product_key = ?", (key,))
            if row:
                new_lowest = min(row["lowest_seen"], price) if row["lowest_seen"] else price
                new_highest = max(row["highest_seen"], price) if row["highest_seen"] else price
                self.store.execute(
                    "UPDATE price_health SET lowest_seen=?, highest_seen=?, "
                    "total_sum=total_sum+?, total_observations=total_observations+1, "
                    "last_seen=? WHERE product_key=?",
                    (new_lowest, new_highest, price, now, key),
                )
            else:
                self.store.execute(
                    "INSERT INTO price_health (product_key, product_title, lowest_seen, "
                    "highest_seen, total_sum, total_observations, last_seen, first_seen) "
                    "VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
                    (key, title[:200], price, price, price, now, now),
                )
        except Exception:
            pass

    def get_health(self, title: str) -> dict:
        if not title:
            return {"confidence": "low"}
        key = title.lower().strip()[:120]
        try:
            row = self.store.fetchone("SELECT * FROM price_health WHERE product_key = ?", (key,))
            if row and row["total_observations"] > 0:
                avg = row["total_sum"] / row["total_observations"]
                status = "below_average" if row["lowest_seen"] <= avg * 0.9 else "average"
                if row["total_observations"] >= 3:
                    status = "good_deal" if row["lowest_seen"] <= avg * 0.8 else status
                return {
                    "lowest_seen": round(row["lowest_seen"], 2),
                    "highest_seen": round(row["highest_seen"], 2),
                    "average_paid": round(avg, 2),
                    "observations": row["total_observations"],
                    "agents_searched": row["total_observations"],
                    "status": status,
                    "confidence": "high" if row["total_observations"] >= 5 else "medium",
                }
        except Exception:
            pass
        return {"confidence": "low", "message": "No hay datos de otros agentes para este producto aún."}

    def get_trending_deals(self, limit: int = 5) -> list:
        try:
            rows = self.store.fetchall(
                "SELECT product_title, lowest_seen, highest_seen, total_observations "
                "FROM price_health WHERE total_observations >= 2 "
                "ORDER BY (highest_seen - lowest_seen) / NULLIF(lowest_seen, 0) DESC LIMIT ?",
                (limit,),
            )
            return [
                {
                    "title": r["product_title"],
                    "lowest": round(r["lowest_seen"], 2),
                    "highest": round(r["highest_seen"], 2),
                    "potential_savings": f"${round(r['highest_seen'] - r['lowest_seen'], 2)}",
                    "agents_searched": r["total_observations"],
                }
                for r in rows
            ]
        except Exception:
            return []


price_health = PriceHealth()
