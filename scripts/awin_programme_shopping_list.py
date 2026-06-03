"""
Generate a prioritized shopping list of Awin programmes to join.
Ranks 21K+ notjoined programmes by relevance to common agent searches.

Usage:
    python scripts/awin_programme_shopping_list.py [--apply N] [--output FILE]

    --apply N    Try to auto-join top N programmes via Playwright (requires playwright)
    --output     Save list to file (default: prints to console)
"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import aiohttp
from agentmagnet.config import settings

# High-value merchant keywords agents search most
HIGH_VALUE_KEYWORDS = [
    "nike", "adidas", "apple", "samsung", "sony", "dell", "hp", "lenovo",
    "asos", "zara", "hm", "zalando", "nordstrom", "macy", "gap",
    "walmart", "bestbuy", "target", "costco", "home depot", "lowes",
    "booking", "expedia", "hotels", "skyscanner", "airbnb",
    "sephora", "ulta", "macys", "kohl", "jcrew",
    "ikea", "wayfair", "overstock", "bedbath",
    "ebay", "etsy", "wish", "aliexpress", "shein",
    "levi", "puma", "underarmour", "timberland", "superdry",
    "farfetch", "lacoste", "converse", "hugoboss", "calvinklein",
    "tommyhilfiger", "ralphlauren", "guess", "dockers",
    "lg", "panasonic", "bose", "jbl", "dyson", "roomba",
]

# High commission categories (these pay more)
HIGH_COMMISSION_CATEGORIES = [
    "Insurance", "Finance", "Loans", "Energy", "Utilities",
    "Broadband", "Mobile", "TV", "Software", "SaaS",
    "Education", "Online Courses", "Fashion", "Beauty",
    "Health", "Fitness", "Home & Garden", "Electronics",
]

# Categories with highest conversion rates
HIGH_CONVERSION_CATEGORIES = [
    "Fashion", "Electronics", "Home & Garden", "Health & Beauty",
    "Sports & Outdoor", "Toys & Games", "Books",
]


async def fetch_notjoined(session, publisher_id, api_key) -> list[dict]:
    """Fetch all notjoined programmes."""
    headers = {"Authorization": f"Bearer {api_key}"}
    all_progs = []
    offset = 0
    page_size = 200

    while True:
        url = (f"https://api.awin.com/publishers/{publisher_id}/programmes"
               f"?relationship=notjoined&offset={offset}&limit={page_size}")
        async with session.get(url, headers=headers) as r:
            if r.status != 200:
                break
            data = await r.json()
            if not data or not isinstance(data, list):
                break
            all_progs.extend(data)
            if len(data) < page_size:
                break
            offset += page_size

    return all_progs


def score_programme(prog: dict) -> int:
    """Score a programme by relevance/value for agent searches."""
    name = (prog.get("name", "") or "").lower()
    sector = (prog.get("primarySector", "") or "").lower()
    region = (prog.get("primaryRegion", {}) or {}).get("countryCode", "")
    currency = prog.get("currencyCode", "")

    score = 0

    # Keyword matches (highest weight)
    for kw in HIGH_VALUE_KEYWORDS:
        if kw in name:
            score += 50

    # Category matches
    for cat in HIGH_COMMISSION_CATEGORIES:
        if cat.lower() in sector:
            score += 30

    for cat in HIGH_CONVERSION_CATEGORIES:
        if cat.lower() in sector:
            score += 20

    # Region preference: US/UK/DE first (biggest markets)
    if region in ("US", "GB", "DE"):
        score += 15
    elif region in ("FR", "IT", "ES", "CA", "AU"):
        score += 10

    # Currency: USD/EUR/GBP preferred
    if currency in ("USD", "EUR", "GBP"):
        score += 5

    # Longer names tend to be more specific merchants
    if len(name) > 10:
        score += 2

    return score


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Awin programme shopping list")
    parser.add_argument("--apply", type=int, help="Auto-join top N programmes via Playwright")
    parser.add_argument("--output", type=str, help="Save list to JSON file")
    parser.add_argument("--limit", type=int, default=50, help="How many to show (default: 50)")
    args = parser.parse_args()

    if not (settings.awin_id and settings.awin_api_key):
        print("ERROR: Set AM_AWIN_ID and AM_AWIN_API_KEY in .env")
        sys.exit(1)

    publisher_id = settings.awin_id
    api_key = settings.awin_api_key

    print(f"Fetching programmes for publisher {publisher_id}...")
    async with aiohttp.ClientSession() as session:
        programmes = await fetch_notjoined(session, publisher_id, api_key)

    print(f"Total notjoined programmes: {len(programmes)}")

    # Score and sort
    for p in programmes:
        p["_score"] = score_programme(p)

    programmes.sort(key=lambda p: p["_score"], reverse=True)

    top = programmes[:args.limit]
    print(f"\n=== TOP {args.limit} PROGRAMMES TO JOIN ===")
    print(f"{'SCORE':<6} {'ID':<8} {'NAME':<45} {'SECTOR':<25} {'REGION':<10} {'CURRENCY'}")
    print("-" * 110)
    for p in top[:args.limit]:
        name = (p.get("name", "") or "")[:44]
        sector = (p.get("primarySector", "") or "")[:24]
        region = (p.get("primaryRegion", {}) or {}).get("countryCode", "")
        currency = p.get("currencyCode", "")
        print(f"{p['_score']:<6} {p.get('id', ''):<8} {name:<45} {sector:<25} {region:<10} {currency}")

    # Stats
    avg_score = sum(p["_score"] for p in programmes) / len(programmes) if programmes else 0
    high_value = [p for p in programmes if p["_score"] >= 50]
    print(f"\n--- Stats ---")
    print(f"Average score: {avg_score:.1f}")
    print(f"High-value (score >= 50): {len(high_value)} programmes")
    print(f"Recommended to join (score >= 30): {len([p for p in programmes if p['_score'] >= 30])}")

    # Save to file
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(top, f, indent=2, ensure_ascii=False)
        print(f"\nSaved top {args.limit} to {args.output}")

    # Auto-join via Playwright (if --apply)
    if args.apply:
        print(f"\n--- Auto-joining top {args.apply} programmes via Playwright ---")
        print("NOTE: This opens a browser. You must be logged into Awin.")
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
            sys.exit(1)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            print("Please log into https://www.awin.com in the browser...")
            await page.goto("https://www.awin.com")
            input("Press Enter after you've logged in...")

            joined = 0
            for prog in top[:args.apply]:
                mid = prog.get("id")
                name = prog.get("name", "?")
                url = f"https://www.awin.com/merchant/join/{mid}"
                try:
                    await page.goto(url, timeout=15000)
                    await asyncio.sleep(2)
                    # Try different join button selectors
                    for selector in [
                        "a[href*='join']", "button:has-text('Join')",
                        "a:has-text('Join')", "input[value='Join']",
                    ]:
                        btn = await page.query_selector(selector)
                        if btn:
                            await btn.click()
                            await asyncio.sleep(1)
                            break
                    joined += 1
                    print(f"  [{joined}/{args.apply}] Joined: {name} (id={mid})")
                except Exception as e:
                    print(f"  [FAIL] {name} (id={mid}): {e}")

            await browser.close()
            print(f"\nSuccessfully joined {joined}/{args.apply} programmes")

if __name__ == "__main__":
    asyncio.run(main())
