"""Coupon & discount code finder via Awin Offers API."""

import httpx
import json
from ..config import settings

PUBLISHER_ID = 2919575
API_KEY = settings.awin_api_key or "9c1d39ce-ebb5-4499-a185-3c9fc7933404"

MOCK_COUPONS = {
    "amazon": [
        {"code": "", "discount": "Up to 40% off", "description": "Seasonal sale on electronics", "expires": "2026-07-01"},
        {"code": "PRIME2026", "discount": "Free shipping", "description": "Prime member free shipping", "expires": "2026-12-31"},
    ],
    "electronics": [
        {"code": "TECH20", "discount": "20% off", "description": "20% off select electronics", "expires": "2026-06-30"},
        {"code": "SSD10", "discount": "10% off", "description": "10% off storage devices", "expires": "2026-07-15"},
    ],
    "fashion": [
        {"code": "FASHION25", "discount": "25% off", "description": "25% off fashion items", "expires": "2026-06-20"},
        {"code": "SHOES15", "discount": "15% off", "description": "15% off footwear", "expires": "2026-08-01"},
    ],
    "home": [
        {"code": "HOME10", "discount": "10% off", "description": "10% off home & kitchen", "expires": "2026-07-31"},
    ],
    "default": [
        {"code": "WELCOME5", "discount": "5% off", "description": "Welcome discount for new customers", "expires": "2026-12-31"},
    ],
}


async def find_coupons(query: str, category: str = "", merchant_id: str = "") -> list:
    """Find active coupon codes for a product query."""
    coupons = []

    # Try Awin Offers API if configured
    if API_KEY and merchant_id:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"https://api.awin.com/publisher/{PUBLISHER_ID}/promotions",
                    params={"advertiserId": merchant_id, "membership": "notJoined"},
                    headers={"Authorization": f"Bearer {API_KEY}"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    promos = data if isinstance(data, list) else data.get("promotions", []) if isinstance(data, dict) else []
                    for promo in promos[:5]:
                        coupons.append({
                            "code": promo.get("voucher", {}).get("code", "") if isinstance(promo.get("voucher"), dict) else "",
                            "discount": promo.get("title", "Special offer"),
                            "description": promo.get("description", ""),
                            "expires": promo.get("endDate", ""),
                            "source": "Awin",
                        })
        except Exception:
            pass

    # Fallback to mock coupons
    if not coupons:
        q = query.lower()
        for key, mock_list in MOCK_COUPONS.items():
            if key != "default" and key in q:
                coupons = mock_list
                break
        if not coupons:
            coupons = MOCK_COUPONS["default"]

    # Category override
    if category and category in MOCK_COUPONS:
        cat_coupons = MOCK_COUPONS[category]
        if not any(c["code"] == cat["code"] for c in coupons for cat in cat_coupons):
            coupons.extend(cat_coupons)

    return coupons[:5]
