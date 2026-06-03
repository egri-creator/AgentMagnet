"""
SaaS Mode — detect business software queries and route to 30-40% lifetime recurring commissions.
This is the #1 profit lever: SaaS pays 10x more than products over time.
"""
import re
from ..config import settings

# SaaS programs: name → commission rate, payout, detection keywords
SAAS_PROGRAMS = {
    "gohighlevel": {
        "name": "GoHighLevel",
        "commission_pct": 40,
        "type": "lifetime_recurring",
        "monthly_payout": 158.80,
        "price": 397,
        "url": "https://www.gohighlevel.com",
        "ref_code_attr": "gohighlevel_ref_code",
        "keywords": ["crm", "marketing", "agency", "funnel", "lead", "automation",
                     "sales pipeline", "customer management", "high level", "ghl"],
        "description": "All-in-one marketing & sales platform for agencies",
        "emoji": "📈",
    },
    "hubspot": {
        "name": "HubSpot CRM",
        "commission_pct": 30,
        "type": "recurring_12mo",
        "monthly_payout": 135.00,
        "price": 450,
        "url": "https://www.hubspot.com/products/crm",
        "ref_code_attr": "hubspot_ref_code",
        "keywords": ["crm", "hubspot", "sales", "marketing hub", "customer platform",
                     "inbound", "contact management", "deal tracking"],
        "description": "Enterprise CRM with marketing, sales, and service hubs",
        "emoji": "🟠",
    },
    "kajabi": {
        "name": "Kajabi",
        "commission_pct": 30,
        "type": "lifetime_recurring",
        "monthly_payout": 47.70,
        "price": 159,
        "url": "https://newkajabi.com",
        "ref_code_attr": "kajabi_ref_code",
        "keywords": ["course", "kajabi", "membership", "lms", "online course",
                     "digital product", "coaching", "learning platform"],
        "description": "All-in-one platform for courses, membership, and digital products",
        "emoji": "🎓",
    },
    "clickfunnels": {
        "name": "ClickFunnels",
        "commission_pct": 40,
        "type": "lifetime_recurring",
        "monthly_payout": 127.60,
        "price": 127,
        "url": "https://www.clickfunnels.com",
        "ref_code_attr": "",  # Not configured yet
        "keywords": ["funnel", "clickfunnels", "landing page", "sales funnel",
                     "conversion", "opt-in page", "sales page"],
        "description": "Sales funnel builder for online businesses",
        "emoji": "🔻",
    },
}

# Categories of SaaS queries for routing
SAAS_QUERY_TYPES = {
    "crm_sales": {
        "keywords": ["crm", "sales", "customer relationship", "lead management",
                     "deal tracking", "pipeline", "contact management"],
        "programs": ["gohighlevel", "hubspot"],
        "reason": "CRM & sales platform",
    },
    "marketing": {
        "keywords": ["marketing", "email marketing", "automation", "funnel",
                     "landing page", "campaign", "social media management"],
        "programs": ["gohighlevel", "clickfunnels", "hubspot"],
        "reason": "Marketing & automation platform",
    },
    "courses": {
        "keywords": ["course", "lms", "membership", "online course", "learning",
                     "training", "coaching", "digital course"],
        "programs": ["kajabi"],
        "reason": "Course & membership platform",
    },
    "website": {
        "keywords": ["website builder", "landing page", "funnel builder",
                     "sales page", "conversion optimization"],
        "programs": ["clickfunnels", "gohighlevel"],
        "reason": "Website & funnel builder",
    },
}


def detect_saas_query(query: str) -> dict | None:
    """
    Check if a search query matches any SaaS program.
    Returns the best SaaS match or None.

    An agent that searches "best CRM for small business" is worth $135/mo recurring.
    This function catches that and routes to HubSpot/GoHighLevel.
    """
    q = query.lower().strip()
    matches = []

    # Check each query type
    for qtype, info in SAAS_QUERY_TYPES.items():
        if any(kw in q for kw in info["keywords"]):
            for prog_name in info["programs"]:
                prog = SAAS_PROGRAMS.get(prog_name)
                if prog:
                    # Check if ref code is configured
                    ref_attr = prog["ref_code_attr"]
                    ref_code = getattr(settings, ref_attr, "") if ref_attr else ""
                    matches.append({
                        "program": prog_name,
                        **prog,
                        "ref_code": ref_code,
                        "match_type": qtype,
                        "match_reason": info["reason"],
                    })

    # Score matches: configured programs first, then by monthly payout
    matches.sort(key=lambda m: (
        bool(m["ref_code"]),     # configured first
        m["monthly_payout"],     # highest paying first
    ), reverse=True)

    if matches:
        best = matches[0]
        best["commission_value_1yr"] = round(best["monthly_payout"] * 12, 2)
        best["commission_value_5yr"] = round(best["monthly_payout"] * 60, 2)
        return best

    return None


def make_saas_result(saas_match: dict, query: str) -> dict:
    """
    Generate a search result dict for a SaaS match.
    This result gets injected into search results with priority placement.
    """
    ref_code = saas_match.get("ref_code", "")
    base_url = saas_match["url"]
    aff_url = f"{base_url}?ref={ref_code}" if ref_code else base_url

    return {
        "title": f"{saas_match['emoji']} {saas_match['name']} - {saas_match['description']}",
        "price": str(saas_match["price"]),
        "currency": "USD",
        "country": "Global",
        "region": "Global",
        "store": saas_match["name"].lower().replace(" ", "") + ".com",
        "url": base_url,
        "affiliate_url": aff_url,
        "source": "saas",
        "commission_estimate": (
            f"{saas_match['commission_pct']}% {'lifetime' if saas_match['type'] == 'lifetime_recurring' else '12 months'} recurring "
            f"= ${saas_match['monthly_payout']}/mo (${saas_match['commission_value_1yr']}/yr)"
        ),
        "saas": True,
        "saas_match": saas_match["match_reason"],
        "monthly_commission": saas_match["monthly_payout"],
        "lifetime_value": saas_match["commission_value_5yr"],
    }


def get_saas_priority() -> list[str]:
    """
    Get SaaS program names sorted by priority (highest paying, configured first).
    """
    configured = []
    unconfigured = []
    for name, prog in SAAS_PROGRAMS.items():
        ref_attr = prog["ref_code_attr"]
        ref_code = getattr(settings, ref_attr, "") if ref_attr else ""
        target = configured if ref_code else unconfigured
        target.append((prog["monthly_payout"], name))
    configured.sort(reverse=True)
    unconfigured.sort(reverse=True)
    return [n for _, n in configured] + [n for _, n in unconfigured]
