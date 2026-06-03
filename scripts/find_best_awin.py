"""Find best Awin programmes (highest EPC, conversion rate) not covered by Skimlinks."""

import httpx
import json

API_KEY = "9c1d39ce-ebb5-4499-a185-3c9fc7933404"
PUBLISHER_ID = 2919575

# Skimlinks covers Amazon, eBay, Apple, Nike, Walmart, Best Buy, etc.
# These are already covered, so we skip them
SKIMLINKS_MERCHANTS = {
    "amazon", "ebay", "walmart", "best buy", "target", "home depot",
    "apple", "nike", "adidas", "macy's", "kohl's", "lowes",
    "costco", "walgreens", "cvs", "ikea", "zara", "hm", "h&m",
    "gap", "old navy", "banana republic", "forever 21",
    "samsung", "sony", "lg", "lenovo", "dell", "hp", "acer",
    "asus", "microsoft", "xbox", "playstation", "nintendo",
}

client = httpx.Client(timeout=30, headers={"Authorization": f"Bearer {API_KEY}"})

all_programmes = []
seen = set()

for region in ["UNITED_KINGDOM", "UNITED_STATES", "GERMANY", "FRANCE", "SPAIN", "ITALY",
                "NETHERLANDS", "SWEDEN", "NORWAY", "DENMARK", "FINLAND", "BELGIUM",
                "AUSTRIA", "SWITZERLAND", "IRELAND", "POLAND", "PORTUGAL",
                "NORTH_AMERICA", "OCEANIA", "ASIA"]:
    try:
        resp = client.get(
            f"https://api.awin.com/publishers/{PUBLISHER_ID}/programmes",
            params={"region": region, "pageSize": 200},
        )
        if resp.status_code != 200:
            continue
        data = resp.json()
        progs = data if isinstance(data, list) else data.get("programmes", data) if isinstance(data, dict) else []
        for p in progs:
            pid = p.get("id")
            if pid and pid not in seen:
                seen.add(pid)
                name = (p.get("name") or "").lower()
                is_skimlinks = any(m in name for m in SKIMLINKS_MERCHANTS)
                all_programmes.append({
                    "id": pid,
                    "name": p.get("name", "Unknown"),
                    "epc": p.get("epc", 0),
                    "conversion_rate": p.get("conversionRate", 0),
                    "approval_ratio": p.get("approvalRatio", 0),
                    "payment_status": p.get("paymentStatus", "red"),
                    "region": region,
                    "skimlinks": is_skimlinks,
                })
    except Exception:
        pass

# Sort by EPC descending, filter for good payment status
sorted_progs = sorted(
    [p for p in all_programmes if p["payment_status"] == "green" and not p["skimlinks"]],
    key=lambda p: float(p["epc"] or 0),
    reverse=True,
)

print(f"\n{'='*80}")
print(f"  TOP 200 AWIN PROGRAMMES BY EPC (not covered by Skimlinks)")
print(f"{'='*80}")
print(f"  Total unique programmes: {len(all_programmes)}")
print(f"  Green payment + not Skimlinks: {len(sorted_progs)}")
print(f"\n  {'ID':>8}  {'EPC':>6}  {'Conv%':>6}  {'Appr%':>6}  {'Region':15s}  Name")
print(f"  {'-'*8}  {'-'*6}  {'-'*6}  {'-'*6}  {'-'*15}  {'-'*40}")

for i, p in enumerate(sorted_progs[:200]):
    print(f"  {p['id']:>8}  {float(p['epc'] or 0):>5.2f}€  {float(p['conversion_rate'] or 0)*100:>5.1f}%  {float(p['approval_ratio'] or 0)*100:>5.1f}%  {p['region']:15s}  {p['name'][:50]}")

print(f"\n  Output saved to awin_top200.json")
with open("awin_top200.json", "w") as f:
    json.dump(sorted_progs[:200], f, indent=2)

client.close()
