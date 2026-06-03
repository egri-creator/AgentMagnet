"""Investigate the 302 redirect from darwin join endpoint."""
import httpx

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}

url = "https://darwin.affiliatewindow.com/api/v1/publisher/2919575/programme/8/join"
resp = httpx.post(url, cookies=cookies, data={"publisherId": "2919575", "programmeId": "8"},
                   headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                   follow_redirects=False, timeout=15)

print(f"Status: {resp.status_code}")
print(f"Location: {resp.headers.get('location', 'none')}")
print(f"Set-Cookie: {resp.headers.get('set-cookie', 'none')}")
print()

# Follow redirect to see what it shows
resp2 = httpx.get(resp.headers.get("location", ""), cookies=cookies,
                   headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
print(f"Redirect page: {resp2.status_code}")
print(f"Content: {resp2.text[:500]}")
