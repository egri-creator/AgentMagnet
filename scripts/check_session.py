"""Follow Awin redirect chain to understand auth."""
import httpx

cookies = {"DARWINSESSIONID": "dij2gk30a8kon85ij3a64bihvs"}
c = httpx.Client(cookies=cookies, headers={"User-Agent": "Mozilla/5.0"}, timeout=15, follow_redirects=True)

resp = c.get("https://ui.awin.com/awin/affiliate/2919575/")
print(f"Final: {resp.status_code} {len(resp.text)} bytes")
print(f"Final URL: {resp.url}")
print()

# Check for login indicators
if "login" in resp.text.lower()[:1000]:
    print("LOGIN PAGE DETECTED - session invalid")
elif resp.status_code == 200:
    print("AUTHENTICATED - session working")
    # Save HTML to analyze
    with open("awin_dashboard.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("Saved to awin_dashboard.html")
