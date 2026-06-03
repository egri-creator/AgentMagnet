"""Try with CSRF token and form data."""
import httpx, re

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, */*",
    "Origin": "https://ui.awin.com",
    "Referer": "https://ui.awin.com/dashboard/awin/publisher/2919575/programmes/directory",
}

c = httpx.Client(cookies=cookies, headers=headers, timeout=15)

# Get the dashboard page and extract CSRF token
resp = c.get("https://ui.awin.com/dashboard/awin/publisher/2919575/programmes/directory")
print(f"Dashboard: {resp.status_code}")

# Check cookies for CSRF
for cookie_name, cookie_val in c.cookies.items():
    if "csrf" in cookie_name.lower() or "xsrf" in cookie_name.lower() or "token" in cookie_name.lower():
        print(f"  Cookie: {cookie_name} = {cookie_val}")

# Check response for meta tags or hidden inputs with CSRF
csrf_match = re.search(r'name=["\']csrf[-_]token["\'][^>]*value=["\']([^"\']+)["\']', resp.text)
if csrf_match:
    print(f"  CSRF token in HTML: {csrf_match.group(1)}")

# Try with XSRF-TOKEN from cookie if present
xsrf_token = c.cookies.get("XSRF-TOKEN")
if xsrf_token:
    print(f"  XSRF-TOKEN cookie found: {xsrf_token}")

# Try different body formats
print("\n--- Trying different formats ---")

# Form URL encoded
resp2 = c.post(
    "https://ui.awin.com/gateway/api/publisher/2919575/programme/8/join",
    data={"publisherId": "2919575", "programmeId": "8"},
    follow_redirects=False,
)
print(f"Form data: {resp2.status_code} -> {resp2.headers.get('location', 'none')}")

# With X-XSRF-TOKEN header
resp3 = c.post(
    "https://ui.awin.com/gateway/api/publisher/2919575/programme/8/join",
    json={"publisherId": 2919575, "programmeId": 8},
    headers={"X-XSRF-TOKEN": xsrf_token or "test"},
    follow_redirects=False,
)
print(f"XSRF header: {resp3.status_code} -> {resp3.headers.get('location', 'none')}")

# With Accept header as HTML
resp4 = c.post(
    "https://ui.awin.com/gateway/api/publisher/2919575/programme/8/join",
    json={"publisherId": 2919575, "programmeId": 8},
    headers={"Accept": "text/html,application/xhtml+xml"},
    follow_redirects=False,
)
print(f"Accept HTML: {resp4.status_code} -> {resp4.headers.get('location', 'none')}")

# Try GET version
resp5 = c.get(
    "https://ui.awin.com/gateway/api/publisher/2919575/programme/8/join",
    follow_redirects=False,
)
print(f"GET: {resp5.status_code} -> {resp5.headers.get('location', 'none')}")
