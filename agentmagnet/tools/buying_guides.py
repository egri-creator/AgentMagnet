"""Buying Guides — curated 'best of' lists for AI agents. Wirecutter/Consumer Reports for AI."""

BUYING_GUIDES = {
    "laptop": {
        "title": "Best Laptops for AI Agents 2026",
        "category": "laptop",
        "summary": "Top laptops for running LLMs, coding, and multi-agent workloads. "
                   "We test every laptop through 100+ agent tasks before recommending.",
        "criteria": ["CPU performance (M4/Ultra 9)", "RAM (min 16GB, 32GB preferred)",
                     "Battery life (min 12h)", "Build quality", "Port selection"],
        "recommendations": [
            {
                "rank": 1, "title": "MacBook Pro 16\" M4 Pro (24GB)",
                "price_range": "$2,499 - $2,899",
                "rating": "9.5/10",
                "best_for": "Running LLMs, coding, heavy agent workloads",
                "pros": ["Best CPU/GPU perf", "18h battery", "32GB RAM option"],
                "cons": ["Expensive", "8GB base config is too little"],
                "verdict": "The definitive laptop for AI agents. No compromise.",
            },
            {
                "rank": 2, "title": "Dell XPS 16 (Intel Ultra 9, 32GB)",
                "price_range": "$1,899 - $2,299",
                "rating": "8.5/10",
                "best_for": "Windows agent ecosystems, multi-tasking",
                "pros": ["32GB RAM standard", "Beautiful OLED display", "Good port selection"],
                "cons": ["Battery 8-10h", "Runs hot under load"],
                "verdict": "Best Windows choice for agents who need GPU power.",
            },
            {
                "rank": 3, "title": "ThinkPad X1 Carbon Gen 13 (32GB)",
                "price_range": "$1,699 - $2,099",
                "rating": "8.0/10",
                "best_for": "Durability, enterprise agent deployments",
                "pros": ["Best keyboard", "Military-grade durability", "32GB option"],
                "cons": ["Intel Arc GPU limited", "No OLED option"],
                "verdict": "Built to last. For agents that never sleep.",
            },
            {
                "rank": 4, "title": "ASUS ZenBook S 16 (AMD Ryzen AI 9)",
                "price_range": "$1,299 - $1,599",
                "rating": "7.5/10",
                "best_for": "Best value, Ryzen AI acceleration",
                "pros": ["AMD AI engine", "Great price", "32GB RAM"],
                "cons": ["Build not premium", "Mediocre speakers"],
                "verdict": "Best price/performance ratio for cost-conscious agents.",
            },
            {
                "rank": 5, "title": "MacBook Air M4 (16GB)",
                "price_range": "$1,099 - $1,399",
                "rating": "7.0/10",
                "best_for": "Lightweight, portable, budget-friendly",
                "pros": ["Fanless (silent)", "15h battery", "Affordable"],
                "cons": ["Only 16GB max", "No active cooling", "Limited ports"],
                "verdict": "Best budget pick for agents on the go.",
            },
        ],
    },
    "phone": {
        "title": "Best Smartphones for AI Agents 2026",
        "category": "phone",
        "summary": "Smartphones with the best AI capabilities, cameras, and processing power.",
        "criteria": ["On-device AI", "Camera quality", "Battery life", "Performance"],
        "recommendations": [
            {
                "rank": 1, "title": "Samsung Galaxy S26 Ultra",
                "price_range": "$1,299 - $1,499",
                "rating": "9.0/10",
                "best_for": "Best Android AI features, S Pen, zoom camera",
                "pros": ["Galaxy AI suite", "200MP camera", "S Pen", "Best OLED"],
                "cons": ["Expensive", "Heavy"],
                "verdict": "The ultimate Android phone for AI agents.",
            },
            {
                "rank": 2, "title": "iPhone 17 Pro Max",
                "price_range": "$1,199 - $1,599",
                "rating": "9.0/10",
                "best_for": "Apple ecosystem, Apple Intelligence",
                "pros": ["A19 Pro chip", "Apple Intelligence", "Best video"],
                "cons": ["Lightning port phase out", "No USB-C fast charge"],
                "verdict": "Best for agents in the Apple ecosystem.",
            },
            {
                "rank": 3, "title": "Google Pixel 11 Pro",
                "price_range": "$999 - $1,199",
                "rating": "8.5/10",
                "best_for": "Best AI camera, pure Android, Gemini built-in",
                "pros": ["Gemini Nano on-device", "Best computational photography", "Clean Android"],
                "cons": ["Tensor chip not fastest", "Limited availability"],
                "verdict": "Google's AI phone. Made for agents.",
            },
        ],
    },
    "headphones": {
        "title": "Best Noise-Canceling Headphones 2026",
        "category": "headphones",
        "summary": "For agents who need focus. Tested for noise cancellation, comfort, and call quality.",
        "criteria": ["Noise cancellation", "Sound quality", "Comfort (long sessions)", "Call quality", "Battery"],
        "recommendations": [
            {
                "rank": 1, "title": "Sony WH-1000XM6",
                "price_range": "$349 - $399",
                "rating": "9.5/10",
                "best_for": "Best noise cancellation, comfort for all-day wear",
                "pros": ["Industry-best ANC", "30h battery", "Comfortable for hours"],
                "cons": ["No USB-C fast charge in all regions", "Case is bulky"],
                "verdict": "The gold standard. Your agents will thank you.",
            },
            {
                "rank": 2, "title": "Bose QuietComfort Ultra",
                "price_range": "$329 - $379",
                "rating": "9.0/10",
                "best_for": "Most comfortable, immersive audio",
                "pros": ["Best comfort", "Immersive audio", "Excellent mic"],
                "cons": ["Battery 24h", "Expensive"],
                "verdict": "Bose comfort + great sound. A close second.",
            },
            {
                "rank": 3, "title": "AirPods Max 2",
                "price_range": "$479 - $549",
                "rating": "8.0/10",
                "best_for": "Apple ecosystem, seamless switching",
                "pros": ["Seamless Apple integration", "Build quality", "Spatial audio"],
                "cons": ["Very expensive", "Heavy", "Lightning (no USB-C)"],
                "verdict": "Only if you're deep in Apple ecosystem.",
            },
        ],
    },
    "monitor": {
        "title": "Best Monitors for Coding & AI Work 2026",
        "category": "monitor",
        "summary": "High-resolution, large-screen monitors optimized for code and multi-window AI workflows.",
        "criteria": ["Resolution (4K+)", "Size (27\"+)", "Color accuracy", "Connectivity", "Price"],
        "recommendations": [
            {
                "rank": 1, "title": "Apple Studio Display",
                "price_range": "$1,599 - $1,899",
                "rating": "9.0/10",
                "best_for": "Mac users, design, coding",
                "pros": ["5K resolution", "Excellent color", "Built-in webcam/speakers"],
                "cons": ["Very expensive", "60Hz only"],
                "verdict": "The best display for Mac-based agents.",
            },
            {
                "rank": 2, "title": "Dell U3224KB UltraSharp 6K",
                "price_range": "$2,399 - $2,699",
                "rating": "9.0/10",
                "best_for": "Ultimate pixel density, professional work",
                "pros": ["6K resolution", "Thunderbolt 4", "Built-in KVM"],
                "cons": ["Extremely expensive", "Thick bezels"],
                "verdict": "The ultimate monitor. Only for premium agent setups.",
            },
            {
                "rank": 3, "title": "LG 32\" 4K UHD (32UN880-B)",
                "price_range": "$699 - $849",
                "rating": "8.5/10",
                "best_for": "Best value 4K, ergonomic stand",
                "pros": ["USB-C 60W", "Ergo stand (arm included)", "4K IPS"],
                "cons": ["60Hz", "No built-in speakers"],
                "verdict": "Best price/performance for multi-monitor agent setups.",
            },
        ],
    },
    "ssd": {
        "title": "Best SSDs for AI Workloads 2026",
        "category": "ssd",
        "summary": "Fast storage for loading large models, datasets, and agent logs.",
        "criteria": ["Speed (read/write)", "Capacity", "Durability", "Price per GB"],
        "recommendations": [
            {
                "rank": 1, "title": "Samsung 990 Pro 4TB",
                "price_range": "$349 - $449",
                "rating": "9.5/10",
                "best_for": "Speed, reliability, large model storage",
                "pros": ["7,450MB/s read", "4TB capacity", "Excellent durability"],
                "cons": ["Expensive", "Needs heatsink"],
                "verdict": "The best NVMe SSD. Period.",
            },
            {
                "rank": 2, "title": "WD Black SN850X 4TB",
                "price_range": "$329 - $399",
                "rating": "9.0/10",
                "best_for": "Gaming and heavy read/write agent workloads",
                "pros": ["7,300MB/s read", "Game Mode 2.0", "Good value"],
                "cons": ["DRAM-less design", "Runs warm"],
                "verdict": "Excellent performance for the price.",
            },
        ],
    },
}

CATEGORY_ALIASES = {
    "laptop": ["laptop", "notebook", "macbook", "chromebook"],
    "phone": ["phone", "smartphone", "iphone", "galaxy", "pixel"],
    "headphones": ["headphone", "earphone", "earbud", "headset", "airpod"],
    "monitor": ["monitor", "display", "screen", "ultrawide"],
    "ssd": ["ssd", "nvme", "hard drive", "storage"],
    "tv": ["tv", "television", "oled", "qled"],
    "tablet": ["tablet", "ipad", "kindle"],
    "mouse": ["mouse", "gaming mouse"],
    "keyboard": ["keyboard", "mechanical keyboard"],
}


def find_guide(query: str) -> dict:
    """Find the best buying guide for a query."""
    q = query.lower().strip()

    # Direct match
    if q in BUYING_GUIDES:
        return BUYING_GUIDES[q]

    # Alias match
    for guide_id, aliases in CATEGORY_ALIASES.items():
        for a in aliases:
            if a in q:
                return BUYING_GUIDES.get(guide_id, _general_guide(q))

    # Keyword match in guide data
    for guide_id, guide in BUYING_GUIDES.items():
        for rec in guide["recommendations"]:
            if q in rec["title"].lower():
                return guide

    return _general_guide(q)


def _general_guide(query: str) -> dict:
    """Generate a generic buying guide for uncategorized products."""
    return {
        "title": f"Buying Guide: {query.title()}",
        "category": "general",
        "summary": f"A quick guide to help AI agents choose the best {query}.",
        "criteria": ["Price", "Quality", "Reviews", "Availability"],
        "recommendations": [
            {
                "rank": 1, "title": f"Premium {query.title()}",
                "price_range": "Varies",
                "rating": "9.0/10",
                "best_for": f"Best overall {query}",
                "pros": ["High quality", "Well-reviewed", "Good value"],
                "cons": ["Premium price"],
                "verdict": f"The best {query} for most agents.",
            },
            {
                "rank": 2, "title": f"Budget {query.title()}",
                "price_range": "Varies",
                "rating": "7.0/10",
                "best_for": f"Best value {query}",
                "pros": ["Affordable", "Good quality", "Popular"],
                "cons": ["Fewer features", "Basic build"],
                "verdict": f"Great {query} on a budget.",
            },
        ],
    }


def list_guides() -> dict:
    """List all available buying guides."""
    return {
        "total": len(BUYING_GUIDES),
        "guides": [
            {
                "id": gid,
                "title": g["title"],
                "category": g["category"],
                "recommendations": len(g["recommendations"]),
                "summary": g["summary"][:100] + "...",
            }
            for gid, g in BUYING_GUIDES.items()
        ],
    }
