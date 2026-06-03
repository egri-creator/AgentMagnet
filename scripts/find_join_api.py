"""Find join endpoint in Angular main bundle."""
import httpx, re, gzip, io

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
c = httpx.Client(cookies=cookies, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)

# Fetch the main bundle
url = "https://ui.awin.com/main.5f07e21492bc4234.js"
resp = c.get(url)
print(f"Main bundle: {resp.status_code} {len(resp.content)} bytes")

# The file might be gzipped
data = resp.content
if data[:2] == b'\x1f\x8b':
    data = gzip.decompress(data)

text = data.decode("utf-8", errors="replace")

# Search for API endpoint patterns
patterns = [
    r'["\'](https?://[^"\']*programme[^"\']*)["\']',
    r'["\'](/api/[^"\']*programme[^"\']*)["\']',
    r'["\'](/[^"\']*join[^"\']*)["\']',
    r'["\'](/[^"\']*apply[^"\']*)["\']',
    r'["\'](/[^"\']*application[^"\']*)["\']',
    r'programme\.(?:join|apply)',
    r'programmeId',
    r'publisherId',
    r'/publisher/\d+/programme/\d+',
]

for pattern in patterns:
    matches = list(re.finditer(pattern, text, re.IGNORECASE))
    if matches:
        for m in matches[:3]:
            start = max(0, m.start() - 60)
            end = min(len(text), m.end() + 60)
            print(f"[{pattern}]: ...{text[start:end]}...")
        print()
