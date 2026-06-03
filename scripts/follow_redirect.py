"""Follow 302 redirects to see where they go."""
import httpx

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, */*",
    "Origin": "https://ui.awin.com",
    "Referer": "https://ui.awin.com/dashboard/awin/publisher/2919575/programmes/directory",
}

c = httpx.Client(cookies=cookies, headers=headers, timeout=15)

# First get CSRF/cookies from directory
c.get("https://ui.awin.com/dashboard/awin/publisher/2919575/programmes/directory")

# Now try join with follow_redirects=False to see the Location
paths = [
    "/gateway/api/publisher/2919575/programme/8/join",
    "/merchant/publisherapplication",
]

for path in paths:
    url = f"https://ui.awin.com{path}"
    resp = c.post(url, json={"publisherId": 2919575, "programmeId": 8}, follow_redirects=False)
    print(f"{resp.status_code} {path}")
    print(f"  Location: {resp.headers.get('location', 'none')}")
    print(f"  Set-Cookie: {resp.headers.get('set-cookie', 'none')[:200]}")
    print()
