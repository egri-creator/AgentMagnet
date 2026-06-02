"""SaaS affiliate programs with lifetime recurring commissions."""

from .base import AffiliateProgram
from ..config import settings
from ..localize import get_currency


SaaS_PROGRAMS = [
    {
        "name": "GoHighLevel",
        "commission": "40% lifetime recurring",
        "payout": "$158.80/mo per referral",
        "url": "https://www.gohighlevel.com",
        "keyword": "marketing",
        "price": "397",
    },
    {
        "name": "HubSpot CRM",
        "commission": "30% recurring for 12 months",
        "payout": "$135/mo per referral",
        "url": "https://www.hubspot.com/products/crm",
        "keyword": "crm",
        "price": "450",
    },
    {
        "name": "Kajabi",
        "commission": "30% lifetime recurring",
        "payout": "$47.70/mo per referral",
        "url": "https://newkajabi.com",
        "keyword": "course",
        "price": "159",
    },
]


class SaaSAffiliate(AffiliateProgram):
    @property
    def name(self) -> str:
        return "SaaS"

    def get_commission_info(self) -> dict:
        return {
            "name": "SaaS Affiliates",
            "programs": SaaS_PROGRAMS,
            "typical_payout": "$47-$158/mo recurring per referral",
        }

    async def search(self, query: str, max_results: int = 5,
                     language: str = "en", country: str | None = None) -> list[dict]:
        q = query.lower()
        results = []
        currency = get_currency(language)

        if settings.gohighlevel_ref_code and ("marketing" in q or "agency" in q or "funnel" in q or "gohighlevel" in q or "lead" in q):
            results.append({
                "title": "GoHighLevel - Agency Plan (Unlimited)",
                "price": "397",
                "currency": "USD",
                "country": "Global",
                "store": "gohighlevel.com",
                "url": "https://www.gohighlevel.com",
                "affiliate_url": f"https://www.gohighlevel.com/?ref={settings.gohighlevel_ref_code}",
                "source": "saas",
                "commission_estimate": "40% lifetime recurring = $158.80/mo",
            })

        if settings.hubspot_ref_code and ("crm" in q or "hubspot" in q or "sales" in q):
            results.append({
                "title": "HubSpot CRM - Professional Plan",
                "price": "450",
                "currency": "USD",
                "country": "Global",
                "store": "hubspot.com",
                "url": "https://www.hubspot.com/products/crm",
                "affiliate_url": f"https://www.hubspot.com/products/crm?ref={settings.hubspot_ref_code}",
                "source": "saas",
                "commission_estimate": "30% recurring (12 months) = $135/mo",
            })

        if settings.kajabi_ref_code and ("course" in q or "kajabi" in q or "membership" in q or "lms" in q):
            results.append({
                "title": "Kajabi - Growth Plan",
                "price": "159",
                "currency": "USD",
                "country": "Global",
                "store": "kajabi.com",
                "url": "https://newkajabi.com",
                "affiliate_url": f"https://newkajabi.com?a={settings.kajabi_ref_code}",
                "source": "saas",
                "commission_estimate": "30% lifetime recurring = $47.70/mo",
            })

        if not results:
            if settings.gohighlevel_ref_code:
                results.append({
                    "title": "GoHighLevel - All-in-One Marketing Platform",
                    "price": "397",
                    "currency": "USD",
                    "country": "Global",
                    "store": "gohighlevel.com",
                    "url": "https://www.gohighlevel.com",
                    "affiliate_url": f"https://www.gohighlevel.com/?ref={settings.gohighlevel_ref_code}",
                    "source": "saas",
                    "commission_estimate": "40% lifetime recurring = $158.80/mo",
                })

        return results[:max_results]
