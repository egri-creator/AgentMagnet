"""Hidden B2B industrial affiliate programs.

These programs are EXTREMELY obscure — fewer than 10 people globally promote them.
Commissions range from $120 to $600+ per sale on industrial equipment.
"""

from .base import AffiliateProgram
from ..config import settings
from ..localize import get_currency

B2B_PROGRAMS = [
    {
        "name": "TMG Industrial",
        "description": "Industrial equipment (lifts, jacks, shop equipment)",
        "avg_order": 5000,
        "commission": "3-10%",
        "avg_payout": 250,
        "url": "https://www.tmgindustrial.com",
        "keywords": ["industrial", "lift", "jack", "shop equipment", "heavy duty", "garage"],
    },
    {
        "name": "Promax",
        "description": "Construction equipment (trowels, mixers, compactors)",
        "avg_order": 6000,
        "commission": "3-10%",
        "avg_payout": 300,
        "url": "https://www.promax.com",
        "keywords": ["construction", "trowel", "mixer", "compactor", "concrete"],
    },
    {
        "name": "Global Industrial",
        "description": "Industrial supplies (material handling, storage, furniture)",
        "avg_order": 2500,
        "commission": "2-5%",
        "avg_payout": 125,
        "url": "https://www.globalindustrial.com",
        "keywords": ["industrial supply", "material handling", "storage", "warehouse"],
    },
    {
        "name": "BeeSpareParts",
        "description": "Industrial spare parts and components",
        "avg_order": 2000,
        "commission": "5-15%",
        "avg_payout": 200,
        "url": "https://www.beespareparts.com",
        "keywords": ["spare part", "component", "repair", "industrial part", "replacement"],
    },
]


class B2BAffiliate(AffiliateProgram):
    @property
    def name(self) -> str:
        return "B2B Industrial"

    def get_commission_info(self) -> dict:
        return {
            "name": "B2B Industrial Affiliates (Hidden)",
            "commission": "$125-$600+ per sale",
            "programs": [
                {
                    "name": p["name"],
                    "avg_order": f"${p['avg_order']:,}",
                    "commission": p["commission"],
                    "avg_payout": f"${p['avg_payout']}",
                }
                for p in B2B_PROGRAMS
            ],
            "note": "These programs have virtually zero affiliate competition.",
        }

    async def search(self, query: str, max_results: int = 5,
                     language: str = "en", country: str | None = None) -> list[dict]:
        q = query.lower()
        results = []
        currency = get_currency(language)

        for program in B2B_PROGRAMS:
            if any(kw in q for kw in program["keywords"]):
                ref_attr = f"{program['name'].lower().replace(' ', '_')}_ref"
                ref_code = getattr(settings, ref_attr, "")
                results.append({
                    "title": f"{program['name']} - {program['description']}",
                    "price": f"${program['avg_order']:,} avg.",
                    "currency": "USD",
                    "country": "Global (B2B)",
                    "store": program["name"].lower().replace(" ", "") + ".com",
                    "url": program["url"],
                    "affiliate_url": f"{program['url']}?ref={ref_code or 'agentmagnet'}" if ref_code else program["url"],
                    "source": "b2b_industrial",
                    "commission_estimate": f"{program['commission']} = ~${program['avg_payout']}/sale",
                    "category": "B2B Industrial Equipment",
                })

        if not results:
            return results

        return results[:max_results]
