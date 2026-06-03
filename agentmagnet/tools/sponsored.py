"""Sponsored Listings — brands pay for priority placement in AI agent search results."""

import time
import json
from datetime import datetime


# In-memory sponsored listings (in production, store in SQLite)
SPONSORED = [
    {
        "id": "sp_1",
        "brand": "Samsung",
        "title": "Samsung Galaxy Book4 Pro",
        "query_match": ["laptop", "galaxy book", "samsung laptop", "ultrabook"],
        "budget_cents_per_click": 5,
        "max_daily_budget_cents": 100,
        "clicks_today": 0,
        "url": "https://go.skimresources.com?id=1792211X1792211&xs=1&url=https%3A%2F%2Fwww.samsung.com",
        "badge": "⭐ SPONSORED",
        "active": True,
        "created_at": "2026-06-01T00:00:00Z",
    },
    {
        "id": "sp_2",
        "brand": "Sony",
        "title": "Sony WH-1000XM6",
        "query_match": ["headphone", "earphone", "sony", "noise cancelling", "wireless headphone"],
        "budget_cents_per_click": 3,
        "max_daily_budget_cents": 50,
        "clicks_today": 0,
        "url": "https://go.skimresources.com?id=1792211X1792211&xs=1&url=https%3A%2F%2Fwww.sony.com",
        "badge": "⭐ SPONSORED",
        "active": True,
        "created_at": "2026-06-01T00:00:00Z",
    },
    {
        "id": "sp_3",
        "brand": "Dell",
        "title": "Dell XPS 16",
        "query_match": ["laptop", "dell", "xps", "notebook", "windows laptop"],
        "budget_cents_per_click": 4,
        "max_daily_budget_cents": 80,
        "clicks_today": 0,
        "url": "https://go.skimresources.com?id=1792211X1792211&xs=1&url=https%3A%2F%2Fwww.dell.com",
        "badge": "⭐ SPONSORED",
        "active": True,
        "created_at": "2026-06-01T00:00:00Z",
    },
]


class SponsoredListings:
    """Brands pay for priority placement in AI agent search results."""

    def __init__(self, store=None):
        self.store = store
        self._ensure_table()

    def _ensure_table(self):
        if not self.store:
            return
        try:
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS sponsored_listings (
                    id TEXT PRIMARY KEY,
                    brand TEXT,
                    title TEXT,
                    query_match TEXT,
                    budget_cents_per_click INTEGER,
                    max_daily_budget_cents INTEGER,
                    clicks_today INTEGER DEFAULT 0,
                    url TEXT,
                    badge TEXT,
                    active INTEGER DEFAULT 1,
                    created_at TEXT
                )
            """)
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS sponsored_clicks (
                    id TEXT PRIMARY KEY,
                    listing_id TEXT,
                    agent_id TEXT,
                    query TEXT,
                    timestamp TEXT
                )
            """)
        except:
            pass

    def get_listings(self, query: str, limit: int = 2) -> list[dict]:
        """Get matching sponsored listings for a query, sorted by bid."""
        q = query.lower().strip()

        # Get from DB + in-memory
        all_listings = []

        # From in-memory
        for sp in SPONSORED:
            if not sp.get("active", True):
                continue
            # Check if query matches any keyword
            match = False
            for kw in sp.get("query_match", []):
                if kw.lower() in q:
                    match = True
                    break
            if match:
                all_listings.append(dict(sp))

        # From DB
        if self.store:
            try:
                rows = self.store.fetchall(
                    "SELECT * FROM sponsored_listings WHERE active = 1 ORDER BY budget_cents_per_click DESC LIMIT ?",
                    (limit * 3,),
                )
                for row in rows:
                    d = dict(row)
                    match = False
                    for kw in json.loads(d.get("query_match", "[]")):
                        if kw.lower() in q:
                            match = True
                            break
                    if match:
                        all_listings.append(d)
            except:
                pass

        # Sort by bid (highest first), filter by daily budget
        active = []
        for sp in all_listings:
            max_budget = sp.get("max_daily_budget_cents", 0)
            clicks = sp.get("clicks_today", 0)
            cost_today = clicks * sp.get("budget_cents_per_click", 0)
            if max_budget <= 0 or cost_today < max_budget:
                active.append(sp)

        active.sort(key=lambda s: s.get("budget_cents_per_click", 0), reverse=True)
        return active[:limit]

    def record_click(self, listing_id: str, agent_id: str, query: str) -> dict:
        """Record a sponsored click."""
        click_id = f"spc_{int(time.time())}"
        if self.store:
            try:
                self.store.execute(
                    "INSERT INTO sponsored_clicks VALUES (?,?,?,?,?)",
                    (click_id, listing_id, agent_id, query, datetime.utcnow().isoformat()),
                )
                # Increment click counter
                self.store.execute(
                    "UPDATE sponsored_listings SET clicks_today = clicks_today + 1 WHERE id = ?",
                    (listing_id,),
                )
            except:
                pass

        # Also update in-memory
        for sp in SPONSORED:
            if sp["id"] == listing_id:
                sp["clicks_today"] = sp.get("clicks_today", 0) + 1

        return {"status": "ok", "click_id": click_id}

    def get_stats(self) -> dict:
        """Get sponsored listings revenue stats."""
        total_clicks = 0
        total_revenue_cents = 0
        active_listings = len([s for s in SPONSORED if s.get("active")])

        if self.store:
            try:
                row = self.store.fetchone("SELECT COUNT(*) as c FROM sponsored_clicks")
                total_clicks = row["c"] if row else 0
                total_revenue_cents = total_clicks * 4  # avg bid
            except:
                pass

        return {
            "active_listings": active_listings,
            "total_clicks": total_clicks,
            "estimated_revenue_usdc": round(total_revenue_cents / 100, 4),
            "listings": [
                {"brand": s["brand"], "title": s["title"], "bid_per_click_cents": s["budget_cents_per_click"],
                 "clicks_today": s.get("clicks_today", 0)}
                for s in SPONSORED if s.get("active")
            ],
        }
