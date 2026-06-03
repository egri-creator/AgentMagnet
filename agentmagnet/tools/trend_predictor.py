"""AgentMagnet Trend Prediction Market — predicts product demand from agent query data."""

import json
import time
from datetime import datetime
from collections import defaultdict

TREND_FILE = None  # Will be set by server.py

class TrendPredictor:
    """Tracks aggregate agent search queries and predicts trending products."""

    def __init__(self, store=None):
        self.store = store
        self._query_log = []

    def record_search(self, query: str, language: str, country: str, source: str):
        """Record a search query anonymously for trend analysis."""
        if not self.store:
            return
        try:
            day_key = datetime.utcnow().strftime("%Y-%m-%d")
            self.store.execute(
                "INSERT INTO trend_queries (day_key, query, language, country, source, count) "
                "VALUES (?, ?, ?, ?, ?, 1) "
                "ON CONFLICT(day_key, query, language, country, source) DO UPDATE SET count = count + 1",
                (day_key, query.lower().strip(), language, country, source),
            )
        except Exception:
            pass

    def get_trending(self, days: int = 7, min_count: int = 2) -> list:
        """Get trending products from the last N days."""
        if not self.store:
            return self._mock_trending()
        try:
            cutoff = datetime.utcnow().strftime("%Y-%m-%d")
            rows = self.store.fetchall(
                "SELECT query, SUM(count) as total, GROUP_CONCAT(DISTINCT source) as sources "
                "FROM trend_queries "
                "WHERE day_key >= date('now', ?) "
                "GROUP BY query "
                "HAVING total >= ? "
                "ORDER BY total DESC LIMIT 50",
                (f"-{days} days", min_count),
            )
            return [
                {
                    "query": r[0],
                    "search_count": r[1],
                    "sources": r[2].split(",") if r[2] else [],
                    "trend_score": round(r[1] * (1.0 + len(set(r[2].split(","))) * 0.1), 1),
                }
                for r in rows
            ]
        except Exception:
            return self._mock_trending()

    def _mock_trending(self) -> list:
        """Mock trending data when no store available."""
        return [
            {"query": "AI laptop 2026", "search_count": 47, "sources": ["amazon", "ebay"], "trend_score": 56.4},
            {"query": "wireless earbuds", "search_count": 38, "sources": ["amazon", "aliexpress"], "trend_score": 45.6},
            {"query": "usb-c hub", "search_count": 29, "sources": ["amazon", "ebay"], "trend_score": 34.8},
            {"query": "mechanical keyboard", "search_count": 24, "sources": ["amazon", "aliexpress"], "trend_score": 28.8},
            {"query": "standing desk", "search_count": 21, "sources": ["amazon", "awin"], "trend_score": 25.2},
            {"query": "noise cancelling headphones", "search_count": 19, "sources": ["amazon", "ebay"], "trend_score": 22.8},
            {"query": "webcam 4k", "search_count": 17, "sources": ["amazon", "aliexpress"], "trend_score": 20.4},
            {"query": "monitor arm", "search_count": 15, "sources": ["amazon", "ebay"], "trend_score": 18.0},
            {"query": "streaming microphone", "search_count": 14, "sources": ["amazon", "aliexpress"], "trend_score": 16.8},
            {"query": "ergonomic mouse", "search_count": 12, "sources": ["amazon", "awin"], "trend_score": 14.4},
        ]

    def get_trend_report(self) -> dict:
        """Generate a comprehensive trend report for sale to brands."""
        trending = self.get_trending(days=7, min_count=2)
        total_queries = sum(t["search_count"] for t in trending) if trending else 0
        
        # Group by category
        categories = defaultdict(int)
        for t in trending:
            q = t["query"]
            if any(kw in q for kw in ["laptop", "computer", "monitor", "keyboard", "mouse"]):
                categories["Computing"] += t["search_count"]
            elif any(kw in q for kw in ["audio", "earbuds", "headphones", "microphone", "speaker"]):
                categories["Audio"] += t["search_count"]
            elif any(kw in q for kw in ["phone", "tablet", "charger", "cable", "hub"]):
                categories["Mobile & Accessories"] += t["search_count"]
            elif any(kw in q for kw in ["desk", "chair", "lighting", "office"]):
                categories["Office"] += t["search_count"]
            elif any(kw in q for kw in ["camera", "webcam", "streaming"]):
                categories["Camera & Video"] += t["search_count"]
            else:
                categories["Other"] += t["search_count"]

        return {
            "total_unique_queries": len(trending),
            "total_search_volume": total_queries,
            "trending_products": trending[:20],
            "category_breakdown": dict(categories),
            "top_rising": trending[:5],
            "report_generated": datetime.utcnow().isoformat(),
        }
