"""Try to join an Awin programme via different API endpoints."""

import httpx

API_KEY = "9c1d39ce-ebb5-4499-a185-3c9fc7933404"
PUBLISHER_ID = 2919575
PROGRAMME_ID = 8  # Drinkstuff.com - a real active programme

# Endpoints to try
endpoints = [
    # POST variants
    ("POST", f"https://api.awin.com/publishers/{PUBLISHER_ID}/programmes/{PROGRAMME_ID}/application"),
    ("POST", f"https://api.awin.com/publishers/{PUBLISHER_ID}/programmes/{PROGRAMME_ID}/join"),
    ("POST", f"https://api.awin.com/publisher/{PUBLISHER_ID}/programme/{PROGRAMME_ID}/application"),
    ("POST", f"https://api.awin.com/publisher/{PUBLISHER_ID}/programme/{PROGRAMME_ID}/join"),
    ("POST", "https://api.awin.com/publisher/programme/application"),
    ("POST", "https://api.awin.com/publisher/programme/join"),
    # PUT variants
    ("PUT", f"https://api.awin.com/publishers/{PUBLISHER_ID}/programmes/{PROGRAMME_ID}/application"),
    ("PUT", f"https://api.awin.com/publishers/{PUBLISHER_ID}/programmes/{PROGRAMME_ID}/join"),
    # UI internal endpoints
    ("POST", f"https://ui.awin.com/awin/api/publisher/{PUBLISHER_ID}/programme/{PROGRAMME_ID}/join"),
    ("POST", f"https://ui.awin.com/awin/api/publisher/{PUBLISHER_ID}/programme/{PROGRAMME_ID}/application"),
    ("POST", "https://ui.awin.com/publisher/programme/apply"),
]

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
data = {"publisherId": PUBLISHER_ID, "programmeId": PROGRAMME_ID}

for method, url in endpoints:
    try:
        if method == "POST":
            resp = httpx.request("POST", url, headers=headers, json=data, timeout=15)
        else:
            resp = httpx.request("PUT", url, headers=headers, json=data, timeout=15)
        print(f"{method:4} {url}")
        print(f"    -> {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"{method:4} {url}")
        print(f"    -> ERROR: {e}")
    print()
