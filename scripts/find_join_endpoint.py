"""Find the join endpoint by analyzing Awin web UI JS bundle."""
import httpx, re

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

c = httpx.Client(cookies=cookies, headers=headers, timeout=15)

# Get the main page
resp = c.get("https://ui.awin.com/awin/affiliate/2919575/programmes/directory")
print(f"Main page: {resp.status_code}")

# Look for JS bundle URLs
js_pattern = re.compile(r'src=["\']([^"\']+\.js[^"\']*)["\']')
for match in js_pattern.finditer(resp.text):
    js_url = match.group(1)
    if not js_url.startswith("http"):
        js_url = "https://ui.awin.com" + js_url
    print(f"  Found JS: {js_url}")
    try:
        js_resp = c.get(js_url, timeout=10)
        if js_resp.status_code == 200:
            # Search for join-related patterns
            for pattern in [r'join', r'programme', r'application', r'unirse', r'apply']:
                if pattern in js_resp.text.lower():
                    # Find context around matches
                    for match2 in re.finditer(pattern, js_resp.text, re.IGNORECASE):
                        start = max(0, match2.start() - 100)
                        end = min(len(js_resp.text), match2.end() + 100)
                        context = js_resp.text[start:end]
                        print(f"    [{pattern}] ...{context}...")
                        break
    except:
        pass
