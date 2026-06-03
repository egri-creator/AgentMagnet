"""Find join endpoint - try correct base path."""
import httpx, re, gzip

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
c = httpx.Client(cookies=cookies, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)

base = "https://ui.awin.com/dashboard/awin"

# Try the main bundle from the base href
for bundle in ["main.5f07e21492bc4234.js", "runtime.f8e2fc8e9b11a96f.js", "polyfills.7386250680623d2c.js"]:
    url = f"{base}/{bundle}"
    resp = c.get(url)
    print(f"{bundle}: {resp.status_code} {len(resp.content)} bytes")
    
    if resp.status_code == 200:
        data = resp.content
        if data[:2] == b'\x1f\x8b':
            data = gzip.decompress(data)
        text = data.decode("utf-8", errors="replace")
        
        # Search for API endpoints
        patterns = [
            (r'["\'](/api/[^"\']*)["\']', "API paths"),
            (r'["\'](https?://[^"\']*programme[^"\']*)["\']', "Programme URLs"),
            (r'programme\.(?:join|apply|leave)', "Programme actions"),
            (r'programmeId|publisherId', "IDs"),
        ]
        
        for pattern, label in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                for m in matches[:5]:
                    start = max(0, m.start() - 40)
                    end = min(len(text), m.end() + 40)
                    print(f"  [{label}]: ...{text[start:end]}...")
                print()
