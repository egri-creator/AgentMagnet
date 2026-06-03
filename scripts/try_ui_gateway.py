"""Try ui.awin.com internal API gateway endpoints."""
import httpx

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, */*",
    "Origin": "https://ui.awin.com",
    "Referer": "https://ui.awin.com/dashboard/awin/publisher/2919575/programmes/directory",
    "X-Requested-With": "XMLHttpRequest",
}

c = httpx.Client(cookies=cookies, headers=headers, timeout=15)

# Get CSRF token from dashboard first
home = c.get("https://ui.awin.com/dashboard/awin/publisher/2919575/programmes/directory")
print(f"Directory page: {home.status_code}")
print(f"Set-Cookie: {home.headers.get('set-cookie', 'none')[:100]}")
print()

# Try various internal API endpoints
endpoints = [
    # Gateway pattern
    ("POST", "/gateway/api/publisher/2919575/programme/8/join"),
    ("POST", "/gateway/api/publisher/programme/join"),
    ("POST", "/api/publisher/programme/join"),
    ("POST", "/api/v1/publisher/programme/join"),
    ("POST", "/awin/api/publisher/programme/join"),
    # JSONP/old style
    ("POST", "/publisher/programme/join.json"),
    # Awin-specific patterns
    ("POST", "/merchant/publisherapplication"),
]

data = {"publisherId": 2919575, "programmeId": 8}

for method, path in endpoints:
    url = f"https://ui.awin.com{path}"
    try:
        resp = c.request(method, url, json=data, follow_redirects=False)
        print(f"{resp.status_code} {path}")
        if resp.status_code not in (404, 301, 302):
            loc = resp.headers.get("location", "")
            print(f"  Location: {loc[:100]}")
            print(f"  Body: {resp.text[:200]}")
    except Exception as e:
        print(f"ERR {path}: {e}")
