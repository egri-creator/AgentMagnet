"""Cross-Sell Matrix AI — suggests complementary products with affiliate links."""

CROSS_SELL_MATRIX = {
    "laptop": [
        {"product": "USB-C Hub 7-in-1", "keywords": "usb-c hub", "price": 34.99},
        {"product": "Laptop Stand Adjustable", "keywords": "laptop stand", "price": 29.99},
        {"product": "External SSD 1TB", "keywords": "external ssd", "price": 89.99},
    ],
    "phone": [
        {"product": "Phone Case Premium", "keywords": "phone case", "price": 19.99},
        {"product": "Screen Protector 2-Pack", "keywords": "screen protector", "price": 12.99},
        {"product": "Wireless Charger Stand", "keywords": "wireless charger", "price": 24.99},
    ],
    "headphone": [
        {"product": "Headphone Stand", "keywords": "headphone stand", "price": 15.99},
        {"product": "Replacement Ear Pads", "keywords": "ear pads", "price": 12.99},
        {"product": "Bluetooth Transmitter", "keywords": "bluetooth transmitter", "price": 29.99},
    ],
    "camera": [
        {"product": "Camera Bag Waterproof", "keywords": "camera bag", "price": 39.99},
        {"product": "SD Card 128GB", "keywords": "sd card", "price": 22.99},
        {"product": "Tripod Aluminum", "keywords": "tripod", "price": 49.99},
    ],
    "monitor": [
        {"product": "Monitor Arm Mount", "keywords": "monitor arm", "price": 39.99},
        {"product": "DisplayPort Cable 6ft", "keywords": "displayport cable", "price": 12.99},
        {"product": "Screen Cleaning Kit", "keywords": "screen cleaner", "price": 9.99},
    ],
    "keyboard": [
        {"product": "Wrist Rest Pad", "keywords": "wrist rest", "price": 14.99},
        {"product": "Keycap Set Custom", "keywords": "keycap set", "price": 24.99},
        {"product": "Desk Mat Large", "keywords": "desk mat", "price": 19.99},
    ],
    "mouse": [
        {"product": "Mouse Pad XL", "keywords": "mouse pad", "price": 15.99},
        {"product": "USB Extension Cable", "keywords": "usb extension", "price": 7.99},
        {"product": "Battery Charger Kit", "keywords": "battery charger", "price": 18.99},
    ],
    "tablet": [
        {"product": "Tablet Case", "keywords": "tablet case", "price": 24.99},
        {"product": "Screen Cleaner", "keywords": "screen cleaner", "price": 9.99},
        {"product": "Bluetooth Keyboard", "keywords": "bluetooth keyboard", "price": 34.99},
    ],
    "printer": [
        {"product": "Extra Ink Cartridge", "keywords": "ink cartridge", "price": 29.99},
        {"product": "Printer Paper 500pk", "keywords": "printer paper", "price": 12.99},
        {"product": "USB Printer Cable", "keywords": "printer cable", "price": 8.99},
    ],
    "speaker": [
        {"product": "Speaker Stands", "keywords": "speaker stands", "price": 39.99},
        {"product": "Audio Cable 3.5mm", "keywords": "audio cable", "price": 7.99},
        {"product": "Subwoofer", "keywords": "subwoofer", "price": 79.99},
    ],
    "watch": [
        {"product": "Watch Band Replacement", "keywords": "watch band", "price": 14.99},
        {"product": "Screen Protector", "keywords": "watch screen protector", "price": 8.99},
        {"product": "Charging Stand", "keywords": "watch charger", "price": 19.99},
    ],
    "book": [
        {"product": "Bookmark Set", "keywords": "bookmarks", "price": 9.99},
        {"product": "Reading Light LED", "keywords": "reading light", "price": 14.99},
        {"product": "Book Stand", "keywords": "book stand", "price": 19.99},
    ],
    "shoes": [
        {"product": "Shoe Cleaning Kit", "keywords": "shoe cleaner", "price": 14.99},
        {"product": "Insoles Comfort", "keywords": "insoles", "price": 12.99},
        {"product": "Shoe Bag", "keywords": "shoe bag", "price": 9.99},
    ],
    "bag": [
        {"product": "Luggage Tag", "keywords": "luggage tag", "price": 7.99},
        {"product": "Packing Cubes Set", "keywords": "packing cubes", "price": 19.99},
        {"product": "Travel Lock TSA", "keywords": "travel lock", "price": 12.99},
    ],
    "chair": [
        {"product": "Lumbar Support Cushion", "keywords": "lumbar cushion", "price": 24.99},
        {"product": "Seat Cushion Memory Foam", "keywords": "seat cushion", "price": 29.99},
        {"product": "Armrest Pads", "keywords": "armrest pads", "price": 14.99},
    ],
    "toy": [
        {"product": "Battery Set Rechargeable", "keywords": "rechargeable batteries", "price": 19.99},
        {"product": "Storage Organizer", "keywords": "toy organizer", "price": 29.99},
        {"product": "Cleaning Wipes", "keywords": "cleaning wipes", "price": 7.99},
    ],
    "coffee": [
        {"product": "Coffee Beans Premium", "keywords": "coffee beans", "price": 19.99},
        {"product": "Reusable Filter", "keywords": "coffee filter", "price": 12.99},
        {"product": "Travel Mug", "keywords": "travel mug", "price": 24.99},
    ],
    "fitness": [
        {"product": "Yoga Mat Premium", "keywords": "yoga mat", "price": 29.99},
        {"product": "Water Bottle Insulated", "keywords": "water bottle", "price": 19.99},
        {"product": "Resistance Bands Set", "keywords": "resistance bands", "price": 14.99},
    ],
    "camping": [
        {"product": "Camping Lantern LED", "keywords": "camping lantern", "price": 24.99},
        {"product": "Sleeping Bag Compact", "keywords": "sleeping bag", "price": 49.99},
        {"product": "First Aid Kit", "keywords": "first aid kit", "price": 19.99},
    ],
}

# Generic fallback for unmatched queries
FALLBACK_SUGGESTIONS = [
    {"product": "Gift Card Digital", "keywords": "gift card", "price": 25.00},
    {"product": "Multi-Tool Pocket", "keywords": "multi tool", "price": 29.99},
    {"product": "LED Flashlight", "keywords": "flashlight", "price": 14.99},
]


def suggest_complementary(query: str, max_results: int = 3) -> list:
    """Return complementary products for a given query."""
    query_lower = query.lower()
    matches = []
    
    # Find matching category
    for category, items in CROSS_SELL_MATRIX.items():
        if category in query_lower:
            matches.extend(items)
            break
    
    # If no exact match, check word overlap
    if not matches:
        query_words = set(query_lower.split())
        best_score = 0
        for category, items in CROSS_SELL_MATRIX.items():
            category_words = set(category.split())
            overlap = len(query_words & category_words)
            if overlap > best_score:
                best_score = overlap
                matches = items
    
    # If still no match, use fallback
    if not matches:
        matches = FALLBACK_SUGGESTIONS
    
    return [
        {
            "title": m["product"],
            "search_keywords": m["keywords"],
            "estimated_price": m["price"],
            "currency": "USD",
            "reason": f"Often bought with products like '{query}'",
            "potential_commission": round(m["price"] * 0.06, 2),
        }
        for m in matches[:max_results]
    ]
