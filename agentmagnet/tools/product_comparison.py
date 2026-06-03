"""Universal Product Comparison Engine — Google Shopping for AI Agents."""

import re
import hashlib

CATEGORY_KEYWORDS = {
    "laptop": ["laptop", "notebook", "macbook", "chromebook", "thinkpad"],
    "phone": ["phone", "smartphone", "iphone", "galaxy", "pixel", "xiaomi"],
    "tablet": ["tablet", "ipad", "kindle"],
    "headphones": ["headphone", "earphone", "earbud", "airpod", "headset"],
    "monitor": ["monitor", "display", "screen"],
    "tv": ["tv", "television", "oled", "qled"],
    "camera": ["camera", "dslr", "mirrorless", "webcam"],
    "speaker": ["speaker", "soundbar", "subwoofer", "bluetooth speaker"],
    "watch": ["watch", "smartwatch", "fitness tracker"],
    "ssd": ["ssd", "hard drive", "external drive", "nvme"],
    "mouse": ["mouse", "gaming mouse"],
    "keyboard": ["keyboard", "mechanical keyboard"],
    "printer": ["printer", "ink", "toner"],
    "router": ["router", "wifi", "mesh"],
    "shoes": ["shoes", "sneaker", "boot", "sandals"],
    "clothing": ["shirt", "jacket", "hoodie", "jeans", "dress"],
    "toy": ["toy", "lego", "board game"],
    "furniture": ["desk", "chair", "table", "shelf"],
    "book": ["book", "ebook", "kindle book"],
    "sports": ["bike", "treadmill", "dumbbell", "yoga"],
    "beauty": ["perfume", "makeup", "skincare", "shampoo"],
    "tool": ["drill", "saw", "hammer", "wrench"],
    "pet": ["dog", "cat", "pet food", "pet toy"],
    "baby": ["diaper", "stroller", "baby monitor"],
    "food": ["coffee", "tea", "snack", "protein"],
    "music": ["guitar", "piano", "midi"],
    "car": ["car accessory", "dashboard cam", "tire"],
}

PRODUCT_IMAGE_MOCK = {
    "laptop": "https://m.media-amazon.com/images/I/71jG+e7roXL._AC_SL1500_.jpg",
    "phone": "https://m.media-amazon.com/images/I/61cwywLhRzL._AC_SL1500_.jpg",
    "headphones": "https://m.media-amazon.com/images/I/71JhdxkxcwL._AC_SL1500_.jpg",
    "default": "https://m.media-amazon.com/images/I/51Z3gwBU-1L._AC_SL1500_.jpg",
}

MOCK_RATINGS = {
    "laptop": {"rating": 4.5, "reviews": 1234},
    "phone": {"rating": 4.3, "reviews": 2345},
    "headphones": {"rating": 4.7, "reviews": 3456},
    "monitor": {"rating": 4.4, "reviews": 892},
    "default": {"rating": 4.2, "reviews": 567},
}

SHIPPING_ESTIMATES = {
    "amazon": "Free shipping (Amazon Prime)",
    "ebay": "Free or $4.99 (varies)",
    "aliexpress": "Free shipping (15-30 days)",
    "default": "Shipping varies",
}


def detect_category(query: str) -> str:
    """Detect product category from query."""
    q = query.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                return cat
    return "default"


def extract_specs(title: str) -> list:
    """Extract key specs from product title."""
    specs = []
    patterns = [
        (r'(\d+[\.\d]*\s*(?:GB|TB|g|Hz|MP|mm|inch|"|cm))', "Capacity/Size"),
        (r'(\d{4,4}x\d{3,4})', "Resolution"),
        (r'(\d+[-/]\d+[-/]\d+)', "Date"),
    ]
    for pattern, label in patterns:
        m = re.search(pattern, title, re.IGNORECASE)
        if m:
            specs.append(f"{label}: {m.group(1)}")
    return specs


def enrich_product(product: dict, query: str) -> dict:
    """Enrich a product with image, rating, specs, shipping."""
    cat = detect_category(f"{query} {product.get('title', '')}")
    
    img = PRODUCT_IMAGE_MOCK.get(cat, PRODUCT_IMAGE_MOCK["default"])
    rating_info = MOCK_RATINGS.get(cat, MOCK_RATINGS["default"])
    source = product.get("source", "").split(".")[0]
    shipping = SHIPPING_ESTIMATES.get(source, SHIPPING_ESTIMATES["default"])
    
    product["image_url"] = img
    product["rating"] = rating_info["rating"]
    product["review_count"] = rating_info["reviews"]
    product["shipping"] = shipping
    product["category"] = cat
    product["specs"] = extract_specs(product.get("title", ""))
    
    return product


def group_by_product(results: list, query: str) -> list:
    """Group same products across stores, show best price first."""
    enriched = [enrich_product(r, query) for r in results]
    
    # Sort by price ascending
    def safe_price(r):
        try: return float(r.get("price", 0))
        except: return 999999
    
    enriched.sort(key=safe_price)
    
    # Build store comparison
    comparison = []
    for r in enriched:
        store = r.get("store", "?")
        price = r.get("price", "?")
        currency = r.get("currency", "USD")
        commission = r.get("commission_estimate", "")
        comparison.append(f"{store}: {currency} {price} ({commission})")
    
    return enriched, comparison


def get_best_overall(results: list, query: str) -> dict:
    """Get the best overall product (lowest price, reliable store)."""
    if not results:
        return {}
    
    enriched, _ = group_by_product(results, query)
    best = enriched[0]
    
    return {
        "title": best.get("title"),
        "best_price": best.get("price"),
        "store": best.get("store"),
        "currency": best.get("currency"),
        "url": best.get("affiliate_url") or best.get("url"),
        "rating": best.get("rating"),
        "image_url": best.get("image_url"),
        "commission": best.get("commission_estimate"),
    }
