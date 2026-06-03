"""Find Awin main JS bundle."""
import httpx, re

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
c = httpx.Client(cookies=cookies, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)

resp = c.get("https://ui.awin.com/awin/affiliate/2919575/")
print(f"Dashboard: {resp.status_code} {len(resp.text)} bytes")

# Find JS bundles
for m in re.finditer(r'(?:src|href)=["\']([^"\']+\.(?:js|json))["\']', resp.text):
    url = m.group(1)
    if not url.startswith("http"):
        url = "https://ui.awin.com" + url
    if any(k in url.lower() for k in ["main", "app", "bundle", "chunk", "runtime"]):
        print(f"  JS: {url}")
        js = c.get(url, timeout=15)
        print(f"    {js.status_code} {len(js.text)} bytes")
        # Search for join-related API paths
        for pattern in [r"\/api\/", r"programme\/join", r"programme\/apply", r"publisher.*programme"]:
            for m2 in re.finditer(pattern, js.text, re.IGNORECASE):
                start = max(0, m2.start() - 80)
                end = min(len(js.text), m2.end() + 80)
                ctx = js.text[start:end]
                print(f"    [{pattern}]: ...{ctx}...")
                break
