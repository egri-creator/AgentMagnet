"""Check the 404 page content."""
import httpx
c = httpx.Client(headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
r = c.get("https://ui.awin.com/main.5f07e21492bc4234.js")
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type', '?')}")
print(f"Length: {len(r.content)}")
print(r.text[:800])
