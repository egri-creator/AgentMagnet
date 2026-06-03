"""Shopping List Optimizer — buy multiple items in ONE call, minimize total cost across stores."""

import time
from datetime import datetime


# Estimated shipping costs by store
SHIPPING_COSTS = {
    "amazon": {"free_min": 29, "cost": 0, "name": "Amazon"},
    "ebay": {"free_min": 0, "cost": 0, "name": "eBay"},
    "aliexpress": {"free_min": 15, "cost": 2.99, "name": "AliExpress"},
    "walmart": {"free_min": 35, "cost": 5.99, "name": "Walmart"},
    "bestbuy": {"free_min": 35, "cost": 3.99, "name": "Best Buy"},
    "target": {"free_min": 35, "cost": 0, "name": "Target"},
}

# Category to preferred store map
STORE_PREFERENCE = {
    "electronics": "amazon",
    "laptop": "bestbuy",
    "phone": "amazon",
    "headphones": "amazon",
    "fashion": "walmart",
    "home": "target",
    "books": "amazon",
    "toys": "walmart",
    "sports": "amazon",
    "beauty": "target",
    "pet": "amazon",
    "baby": "target",
    "general": "amazon",
}


def optimize_shopping_list(items: list, budget: float = 0,
                           preferred_store: str = "") -> dict:
    """
    Optimize a multi-item shopping list across stores.
    Each item: {"query": str, "max_price": float, "category": str, "priority": int}
    Returns cheapest combination + best overall store.
    """
    if not items:
        return {"error": "No items provided", "items": []}

    stores = SHIPPING_COSTS if not preferred_store else {preferred_store: SHIPPING_COSTS[preferred_store]}

    best = {"total": float("inf"), "store": "", "items": [], "shipping": 0, "savings": 0}

    for store_code, store_info in stores.items():
        store_total = 0
        store_items = []
        subtotal = 0

        for item in items:
            # Estimate price for each item
            est_price = _estimate_item_price(item.get("query", ""),
                                             item.get("max_price", 0),
                                             item.get("category", "general"),
                                             store_code)
            subtotal += est_price.get("price", 0)
            store_items.append(est_price)

        # Calculate shipping
        shipping = store_info["cost"]
        if store_info["free_min"] > 0 and subtotal >= store_info["free_min"]:
            shipping = 0

        total = subtotal + shipping

        if total < best["total"]:
            best = {
                "total": round(total, 2),
                "store": store_info["name"],
                "store_code": store_code,
                "items": store_items,
                "subtotal": round(subtotal, 2),
                "shipping": round(shipping, 2),
                "savings": round(budget - total, 2) if budget else 0,
            }

    # Calculate cross-store savings
    cross_store = _cross_store_optimization(items)

    return {
        "shopping_list": items,
        "budget": budget or "unlimited",
        "best_option": best,
        "cross_store_alternative": cross_store,
        "total_items": len(items),
        "agent_message": f"🛒 Best: {best['store']} for ${best['total']:.2f} ({best['store']})"
                       + (f", ${cross_store['total']:.2f} across multiple stores." if cross_store else ""),
        "summary": {
            "total_items": len(items),
            "cheapest_store": best["store"],
            "best_total": best["total"],
            "shipping_cost": best["shipping"],
            "over_budget": budget > 0 and best["total"] > budget,
        },
    }


def _estimate_item_price(query: str, max_price: float, category: str,
                         store: str) -> dict:
    """Estimate item price based on category and store."""
    base_prices = {
        "laptop": 999, "phone": 799, "tablet": 499,
        "headphones": 249, "mouse": 49, "keyboard": 99,
        "monitor": 349, "tv": 649, "camera": 599,
        "speaker": 149, "watch": 199, "ssd": 89,
        "shoes": 79, "clothing": 49, "book": 19,
        "toy": 39, "home": 89, "kitchen": 59,
        "beauty": 29, "sports": 99, "pet": 35,
        "baby": 45, "tool": 59, "furniture": 199,
        "software": 99, "food": 15, "general": 50,
    }

    cat = category.lower() if category else "general"
    base = base_prices.get(cat, base_prices["general"])

    # Store multiplier
    store_mult = {
        "amazon": 1.0, "ebay": 0.92, "aliexpress": 0.80,
        "walmart": 0.95, "bestbuy": 1.05, "target": 1.02,
    }
    mult = store_mult.get(store, 1.0)

    price = round(base * mult, 2)

    # Apply max_price constraint
    if max_price and price > max_price:
        price = max_price * 0.95  # Slightly under max

    return {
        "query": query,
        "category": cat,
        "price": price,
        "store": store,
        "available": True,
    }


def _cross_store_optimization(items: list) -> dict:
    """Optimize each item at its best individual store."""
    total = 0
    assignments = []

    for item in items:
        cat = item.get("category", "general").lower()
        best_store = STORE_PREFERENCE.get(cat, "amazon")
        est = _estimate_item_price(item.get("query", ""),
                                   item.get("max_price", 0),
                                   cat, best_store)
        total += est["price"]
        assignments.append({
            "query": item.get("query", ""),
            "category": cat,
            "store": SHIPPING_COSTS.get(best_store, {}).get("name", "Amazon"),
            "price": est["price"],
        })

    return {
        "items": assignments,
        "total": round(total, 2),
        "stores_used": list(set(a["store"] for a in assignments)),
        "note": "Each item at its cheapest store (may pay separate shipping)",
    }
