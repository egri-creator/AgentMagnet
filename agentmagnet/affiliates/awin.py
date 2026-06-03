"""Awin Affiliate Network — 15,000+ merchants, 180+ countries.

Uses Awin Publisher API v3 for merchant directory + product search.
Product search requires publisher to have active product feeds enabled
on joined programmes. Falls back cleanly to keyword matching.
"""

import json
from .base import AffiliateProgram
from ..config import settings

import aiohttp

API_BASE = "https://api.awin.com"
_joined_cache = None

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
            "api_connected": bool(settings.awin_api_key and settings.awin_id),
            "note": "ONE account = 15,000+ merchants globally",
        }

    def _get_merchants(self) -> dict[str, int]:
        try:
            custom = json.loads(settings.awin_merchant_ids) if settings.awin_merchant_ids and settings.awin_merchant_ids != "{}" else {}
            return {**DEFAULT_MERCHANTS, **custom}
        except (json.JSONDecodeError, TypeError):
            return DEFAULT_MERCHANTS

    async def _fetch_joined(self) -> list[dict]:
        """Fetch joined programmes from Awin API (cached in-memory)."""
        global _joined_cache
        if _joined_cache is not None:
            return _joined_cache
        if not (settings.awin_id and settings.awin_api_key):
            _joined_cache = []
            return _joined_cache
        try:
            headers = {"Authorization": f"Bearer {settings.awin_api_key}"}
            async with aiohttp.ClientSession() as s:
                r = await s.get(
                    f"{API_BASE}/publishers/{settings.awin_id}/programmes?relationship=joined",
                    headers=headers, timeout=aiohttp.ClientTimeout(total=5),
                )
                if r.status == 200:
                    _joined_cache = await r.json()
                else:
                    _joined_cache = []
        except Exception:
            _joined_cache = []
        return _joined_cache

    async def search(self, query: str, max_results: int = 5,
                     language: str = "en", country: str | None = None) -> list[dict]:
        if not (settings.awin_id and settings.awin_api_key):
            return self._mock_search(query, max_results)

        api_key = settings.awin_api_key
        headers = {"Authorization": f"Bearer {api_key}"}
        joined = await self._fetch_joined()

        # Try to get real products from joined programmes first
        try:
            async with aiohttp.ClientSession(headers=headers) as s:
                for prog in joined:
                    pid = prog["id"]
                    r = await s.get(
                        f"{API_BASE}/publishers/{settings.awin_id}/programmes/{pid}/products?pageSize=3",
                        timeout=aiohttp.ClientTimeout(total=5),
                    )
                    if r.status != 200:
                        continue
                    data = await r.json()
                    products = data if isinstance(data, list) else data.get("products", [])
                    if products:
                        out = []
                        for item in products[:max_results]:
                            price = item.get("searchPrice", "Varies")
                            out.append({
                                "title": item.get("productName", query).strip(),
                                "price": price,
                                "currency": item.get("currency", "USD"),
                                "country": item.get("merchantCountry", "Global"),
                                "region": "Global",
                                "store": item.get("merchantName", prog.get("name", "Awin")),
                                "url": item.get("awinUrl") or item.get("url", ""),
                                "affiliate_url": item.get("awinUrl", ""),
                                "source": "awin",
                                "commission_estimate": (
                                    f"{item.get('commissionPercent')}%"
                                    if item.get("commissionPercent")
                                    else "varies"
                                ),
                            })
                        if out:
                            return out
        except Exception:
            pass

        return self._mock_search(query, max_results)

    def _mock_search(self, query: str, max_results: int = 5) -> list[dict]:
        q = query.lower()
        merchants = self._get_merchants()
        matched = []
        for name, mid in merchants.items():
            if name in q or any(kw in q for kw in [name[:4], name.replace("_", "")]):
                matched.append((name, mid))
        if not matched and "shoes" in q:
            matched = [("nike", 4633), ("adidas", 10340), ("puma", 4873)]
        elif not matched and "electronics" in q:
            matched = [("apple", 3504), ("bestbuy", 5732), ("walmart", 28356)]
        elif not matched and ("clothing" in q or "fashion" in q):
            matched = [("asos", 2151), ("zara", 5602), ("hm", 4192)]
        elif not matched and "travel" in q:
            matched = [("booking", 15347), ("skyscanner", 50051), ("expedia", 4703)]
        elif not matched:
            matched = list(merchants.items())[:3]
        results = []
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
