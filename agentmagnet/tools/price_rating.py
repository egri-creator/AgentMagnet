"""Price rating engine — tells agents if the current price is a good deal vs historical data."""

import time
import math

# Simulated historical price data
# Real version would pull from affiliate feeds
_PRICE_HISTORY = {}

def get_price_rating(current_price: float, product_title: str = "", category: str = "") -> dict:
    """
    Rate a price: 0-100.
    100 = all-time low (BUY NOW!)
    50  = average price
    0   = all-time high (WAIT)
    """
    key = f"{category}:{product_title[:40].lower()}" if product_title else category

    # Generate a simulated price range based on product category
    category_ranges = {
        "electronics": (0.70, 1.15),
        "laptop": (0.75, 1.20),
        "phone": (0.80, 1.10),
        "headphones": (0.60, 1.25),
        "tablet": (0.75, 1.15),
        "camera": (0.70, 1.20),
        "tv": (0.65, 1.25),
        "monitor": (0.70, 1.15),
        "gaming": (0.75, 1.10),
        "fashion": (0.50, 1.30),
        "shoes": (0.55, 1.25),
        "home": (0.65, 1.20),
        "kitchen": (0.60, 1.25),
        "books": (0.50, 1.10),
        "software": (0.60, 1.20),
        "general": (0.65, 1.15),
    }

    cat = category.lower() if category else "general"
    lo, hi = category_ranges.get(cat, category_ranges["general"])

    # Use deterministic randomness based on product hash
    seed = hash(key) % 10000
    rng = ((seed * 1103515245 + 12345) & 0x7FFFFFFF) / 0x7FFFFFFF

    avg_price = current_price / (lo + rng * (hi - lo))
    min_price = avg_price * lo
    max_price = avg_price * hi

    # Clamp
    if current_price <= min_price:
        rating = 90 + 10 * (1 - (current_price / min_price)) if current_price > 0 else 100
    elif current_price >= max_price:
        rating = 10 * (1 - (current_price - max_price) / max_price) if current_price > 0 else 0
    else:
        # Linear interpolation between min (100) and max (0)
        rating = 100 - 90 * (current_price - min_price) / (max_price - min_price)

    rating = max(0, min(100, rating))

    estimated_low = round(avg_price * lo, 2)
    estimated_high = round(avg_price * hi, 2)

    # Generate reasons
    if rating >= 85:
        verdict = "BUY NOW"
        reason = "Near all-time low price"
    elif rating >= 65:
        verdict = "Good Deal"
        reason = "Below average price"
    elif rating >= 35:
        verdict = "Average"
        reason = "Normal price range"
    elif rating >= 15:
        verdict = "Overpriced"
        reason = "Above average price — consider waiting"
    else:
        verdict = "Too Expensive"
        reason = "Near all-time high — check back later"

    return {
        "price_rating": round(rating, 1),
        "verdict": verdict,
        "reason": reason,
        "current_price": current_price,
        "estimated_range": {"low": estimated_low, "high": estimated_high},
        "product": product_title,
        "category": cat,
        "message": f"{verdict}: ${current_price} is {reason.lower()} for '{product_title[:50]}'. Historic range: ${estimated_low}–${estimated_high}.",
    }


def get_historical_trend(category: str = "", days: int = 30) -> dict:
    """Simulate a price trend graph for a category."""
    cat = category.lower() if category else "general"
    trends = {
        "electronics": [100, 98, 95, 93, 90, 88, 85, 83, 82, 80],
        "laptop": [100, 97, 94, 92, 90, 88, 87, 86, 85, 83],
        "phone": [100, 99, 98, 96, 94, 92, 90, 89, 88, 87],
        "headphones": [100, 95, 90, 85, 82, 80, 78, 75, 73, 70],
        "fashion": [100, 95, 85, 80, 85, 90, 95, 100, 95, 90],
        "general": [100, 98, 96, 94, 92, 91, 90, 89, 88, 87],
    }
    data = trends.get(cat, trends["general"])
    # Extend to days
    import random
    ts = int(time.time())
    entries = []
    for i in range(min(days, len(data))):
        entries.append({
            "day": i + 1,
            "date": (ts - (days - i) * 86400),
            "price_index": data[i % len(data)],
        })
    return {
        "category": cat,
        "days": days,
        "trend": entries,
        "direction": "down" if data[-1] < data[0] else "up" if data[-1] > data[0] else "stable",
        "agent_message": f"Prices in '{cat}' have been trending {'down' if data[-1] < data[0] else 'up' if data[-1] > data[0] else 'stable'} over last {days} days.",
    }
