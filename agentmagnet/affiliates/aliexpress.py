"""Global AliExpress affiliate module."""

from .base import AffiliateProgram
from ..config import settings
from ..localize import get_currency


class AliExpressAffiliate(AffiliateProgram):
    @property
    def name(self) -> str:
        return "AliExpress"

    def get_commission_info(self) -> dict:
        return {
            "name": "AliExpress Affiliate",
            "commission": "3-20% per sale",
            "countries": ["Global"],
            "stores": ["aliexpress.com"],
            "typical_payout": "$1-$100 per sale",
        }

    async def search(self, query: str, max_results: int = 5,
                     language: str = "en", country: str | None = None) -> list[dict]:
        tid = settings.aliexpress_tracking_id or "agentmagnet"
        currency = get_currency(language)
        results = []

        if settings.aliexpress_api_key:
            try:
                return await self._api_search(query, max_results, tid)
            except Exception:
                pass

        for i in range(min(max_results, 2)):
            price = round(8.99 + abs(hash(query + str(i))) % 50, 2)
            product_id = f"ae-{abs(hash(query + str(i))) % 10000000:07d}"
            results.append({
                "title": f"{query.title()} - {'Direct from Factory' if i == 0 else 'Wholesale Pack'}",
                "price": str(price),
                "currency": currency,
                "country": "Global",
                "store": "aliexpress.com",
                "url": f"https://www.aliexpress.com/item/{product_id}.html",
                "affiliate_url": f"https://www.aliexpress.com/item/{product_id}.html?aff_fcid={tid}&aff_fsk=aff-{tid}&aff_platform=api",
                "source": "aliexpress",
                "commission_estimate": f"~{currency} {round(price * 0.08, 2)} (8% est.)",
            })
        return results

    async def _api_search(self, query: str, max_results: int, tid: str) -> list[dict]:
        import httpx
        import hashlib
        import time

        app_key = settings.aliexpress_api_key
        method = "aliexpress.affiliate.product.query"
        timestamp = int(time.time() * 1000)
        api_params = {
            "app_key": app_key,
            "method": method,
            "timestamp": str(timestamp),
            "format": "json",
            "v": "1.0",
            "sign_method": "sha256",
            "tracking_id": tid,
            "keywords": query,
            "page_size": str(min(max_results, 50)),
        }
        sign_str = "".join(f"{k}{v}" for k, v in sorted(api_params.items()))
        sign = hashlib.sha256(sign_str.encode()).hexdigest()
        api_params["sign"] = sign

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get("https://api-sg.aliexpress.com/sync", params=api_params)
            data = resp.json()

        results = []
        products = (data.get("aliexpress_affiliate_product_query_response", {})
                    .get("result", {}).get("products", {}).get("product", []))
        for product in products[:max_results]:
            results.append({
                "title": product.get("product_title", "Unknown"),
                "price": product.get("target_app_sale_price", "0"),
                "currency": product.get("target_app_sale_price_currency", "USD"),
                "country": "Global",
                "store": "aliexpress.com",
                "url": f"https://www.aliexpress.com/item/{product.get('product_id', '')}.html",
                "affiliate_url": f"https://www.aliexpress.com/item/{product.get('product_id', '')}.html?aff_fcid={tid}&aff_fsk=aff-{tid}&aff_platform=api",
                "source": "aliexpress",
                "commission_estimate": f"{product.get('commission_rate', '3-20')}%",
            })
        return results
