"""Try www.awin1.com join endpoint with session cookie."""
import httpx

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Origin": "https://ui.awin.com",
    "Referer": "https://ui.awin.com/",
    "Content-Type": "application/json",
}

c = httpx.Client(cookies=cookies, headers=headers, timeout=30)

# Try various endpoints
endpoints = [
    "https://www.awin1.com/awin/api/publisher/programme/join",
    "https://www.awin1.com/awin/api/publisher/programme/apply",
    "https://www.awin1.com/awin/api/publisher/2919575/programme/8/join",
    "https://www.awin1.com/awin/api/publisher/2919575/programme/8/apply",
    "https://www.awin1.com/api/v1/publisher/2919575/programme/8/join",
    "https://www.awin1.com/api/publisher/2919575/programme/8/join",
]

data = {"publisherId": 2919575, "programmeId": 8}

for ep in endpoints:
    try:
        resp = c.post(ep, json=data)
        print(f"{resp.status_code} {ep}")
        if resp.status_code not in (404, 405, 301, 302):
            print(f"  -> {resp.text[:300]}")
    except httpx.ReadTimeout:
        print(f"TIMEOUT {ep}")
    except Exception as e:
        print(f"ERROR {ep}: {e}")
