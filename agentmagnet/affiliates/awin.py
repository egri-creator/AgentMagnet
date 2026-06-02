"""Awin Affiliate Network — 15,000+ merchants, 180+ countries.

With ONE Awin account, you can promote:
Nike, Apple, Adidas, ASOS, Booking.com, Skyscanner, Walmart, Best Buy,
Sephora, Zara, H&M, Zalando, IKEA, Farfetch, and 15,000+ more.

Register: https://www.awin.com (5 min)
Get your Publisher ID from your Awin dashboard.
"""

import json
from .base import AffiliateProgram
from ..config import settings

DEFAULT_MERCHANTS = {
    "nike": 4633, "adidas": 10340, "apple": 3504, "booking": 15347,
    "asos": 2151, "zara": 5602, "hm": 4192, "zalando": 7393,
    "skyscanner": 50051, "expedia": 4703, "hotels": 35000,
    "nordstrom": 6835, "sephora": 9875, "ikea": 6050,
    "levi": 3042, "puma": 4873, "underarmour": 15567,
    "timberland": 4859, "superdry": 12381, "farfetch": 21047,
    "aliexpress": 36244, "shein": 59925, "walmart": 28356,
    "bestbuy": 5732, "gap": 3892, "macy": 2676,
    "lacoste": 15517, "converse": 7830, "raynban": 7638,
    "calvinklein": 10365, "tommyhilfiger": 7439, "hugoboss": 15323,
}


class AwinAffiliate(AffiliateProgram):
    @property
    def name(self) -> str:
        return "Awin"

    def get_commission_info(self) -> dict:
        merchant_count = len(self._get_merchants())
        return {
            "name": "Awin Affiliate Network",
            "commission": "2-20% per sale (varies by merchant)",
            "total_merchants": merchant_count,
            "countries": "180+",
            "typical_payout": "$1-$500 per sale",
            "register": "https://www.awin.com",
            "note": "ONE account = 15,000+ merchants globally",
        }

    def _get_merchants(self) -> dict[str, int]:
        try:
            custom = json.loads(settings.awin_merchant_ids) if settings.awin_merchant_ids and settings.awin_merchant_ids != "{}" else {}
            return {**DEFAULT_MERCHANTS, **custom}
        except (json.JSONDecodeError, TypeError):
            return DEFAULT_MERCHANTS

    async def search(self, query: str, max_results: int = 5,
                     language: str = "en", country: str | None = None) -> list[dict]:
        if not settings.awin_id:
            return []

        q = query.lower()
        results = []
        merchants = self._get_merchants()

        matched = []
        for name, mid in merchants.items():
            if name in q or any(kw in q for kw in [name[:4], name.replace("_", "")]):
                matched.append((name, mid))

        if not matched and "shoes" in q:
            matched = [("nike", 4633), ("adidas", 10340), ("puma", 4873)]
        elif not matched and "electronics" in q:
            matched = [("apple", 3504), ("bestbuy", 5732), ("walmart", 28356)]
        elif not matched and "clothing" in q or "fashion" in q:
            matched = [("asos", 2151), ("zara", 5602), ("hm", 4192)]
        elif not matched and "travel" in q:
            matched = [("booking", 15347), ("skyscanner", 50051), ("expedia", 4703)]
        elif not matched:
            matched = list(merchants.items())[:3]

        for name, mid in matched[:max_results]:
            comm_range = "5-15%" if any(x in name for x in ["nike", "adidas", "zara"]) else "2-10%"
            results.append({
                "title": f"{name.title()} - via Awin Network",
                "price": "Varies",
                "currency": "USD",
                "country": "Global (180+ countries)",
                "region": "Global",
                "store": f"{name}.com",
                "url": f"https://www.{name}.com",
                "affiliate_url": f"https://www.awin1.com/awclick.php?awinmid={mid}&awinaffid={settings.awin_id}&clickref=agentmagnet&p=https://www.{name}.com/search?q={query.replace(' ', '%20')}",
                "source": "awin",
                "commission_estimate": comm_range,
            })

        return results
