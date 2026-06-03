"""Central commission rate registry — auto-prioritizes highest-paying affiliate per product."""

COMMISSION_RATES = {
    # Amazon: 1-10% depending on category
    "amazon": {
        "rate": 0.06,
        "note": "1-10% per sale",
        "categories": {
            "electronics": 0.04,
            "books": 0.045,
            "clothing": 0.08,
            "home": 0.06,
            "sports": 0.06,
            "beauty": 0.08,
            "tools": 0.06,
            "default": 0.05,
        },
    },
    # eBay: 1-4% depending on category
    "ebay": {
        "rate": 0.025,
        "note": "1-4% per sale",
        "categories": {
            "electronics": 0.02,
            "fashion": 0.03,
            "home": 0.03,
            "sports": 0.025,
            "collectibles": 0.035,
            "default": 0.02,
        },
    },
    # Awin: 2-20% depending on merchant
    "awin": {
        "rate": 0.08,
        "note": "2-20% per sale (varies by merchant)",
        "merchant_overrides": {
            "nike": 0.12,
            "adidas": 0.10,
            "zara": 0.08,
            "hm": 0.10,
            "apple": 0.03,
            "samsung": 0.05,
            "sony": 0.04,
            "dell": 0.04,
        },
    },
    # AliExpress: 3-20%
    "aliexpress": {
        "rate": 0.08,
        "note": "3-20% per sale",
        "categories": {
            "electronics": 0.05,
            "clothing": 0.10,
            "home": 0.08,
            "beauty": 0.12,
            "toys": 0.10,
            "default": 0.07,
        },
    },
    # SaaS: 30-40% lifetime recurring
    "saas": {
        "rate": 0.35,
        "note": "30-40% lifetime recurring",
        "programs": {
            "gohighlevel": 0.40,
            "hubspot": 0.30,
            "kajabi": 0.30,
        },
    },
    # B2B Industrial: 2-15%
    "b2b_industrial": {
        "rate": 0.08,
        "note": "2-15% per sale (~$125-$600+)",
        "programs": {
            "tmg_industrial": 0.10,
            "promax": 0.10,
            "global_industrial": 0.03,
            "beespareparts": 0.10,
        },
    },
}


def best_commission(query: str, price: float = 100.0) -> dict:
    """Return the highest commission for a given query across all affiliates."""
    query_lower = query.lower()
    
    # Score each program
    candidates = []
    
    for source, rates in COMMISSION_RATES.items():
        rate = rates["rate"]
        
        # Check category-specific rates
        if "categories" in rates:
            for kw, cat_rate in rates["categories"].items():
                if kw in query_lower:
                    rate = cat_rate
                    break
            # Check if category hit; if not, use default
            if not any(kw in query_lower for kw in rates["categories"]):
                rate = rates["categories"].get("default", rate)
        
        # Check merchant overrides (Awin)
        if "merchant_overrides" in rates:
            for merchant, mrate in rates["merchant_overrides"].items():
                if merchant in query_lower:
                    rate = mrate
                    break
        
        # Check specific programs (SaaS, B2B)
        if "programs" in rates:
            for prog, prate in rates["programs"].items():
                prog_key = prog.replace("_", " ")
                if prog in query_lower or prog_key in query_lower:
                    rate = prate
                    break
        
        est = round(price * rate, 2)
        candidates.append({
            "source": source,
            "rate_pct": round(rate * 100, 1),
            "estimate": est,
            "note": rates["note"],
        })
    
    # Sort by commission amount descending
    candidates.sort(key=lambda x: x["estimate"], reverse=True)
    
    return {
        "best_source": candidates[0]["source"],
        "best_rate": candidates[0]["rate_pct"],
        "best_estimate": candidates[0]["estimate"],
        "ranking": candidates,
    }


def get_commission_estimate(source: str, query: str, price: float) -> str:
    """Get human-readable commission estimate string."""
    result = best_commission(query, price)
    for c in result["ranking"]:
        if c["source"] == source:
            rate = c["rate_pct"]
            est = c["estimate"]
            note = c["note"]
            return f"~{est:.2f} ({rate}% est.) — {note}"
    return f"~{price * 0.05:.2f} (est.)"
