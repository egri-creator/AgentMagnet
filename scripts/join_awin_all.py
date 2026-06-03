"""Auto-join ALL Awin programmes using web session cookie."""

import httpx
import sys, os, time, json, re

SESSION_COOKIE = os.environ.get("AWIN_SESSION", "")
PUBLISHER_ID = 2919575

ENDIAN = "https://darwin.affiliatewindow.com"

def fetch_all_programmes():
    """Get all programmes from the API."""
    all_progs = []
    seen = set()
    api_key = os.environ.get("AWIN_API_KEY", "9c1d39ce-ebb5-4499-a185-3c9fc7933404")
    regions = [
        "UNITED_KINGDOM", "UNITED_STATES", "GERMANY", "FRANCE", "SPAIN", "ITALY",
        "NETHERLANDS", "SWEDEN", "NORWAY", "DENMARK", "FINLAND", "BELGIUM",
        "AUSTRIA", "SWITZERLAND", "IRELAND", "POLAND", "PORTUGAL",
        "NORTH_AMERICA", "OCEANIA", "ASIA",
    ]
    c = httpx.Client(timeout=30, headers={"Authorization": f"Bearer {api_key}"})
    for region in regions:
        try:
            resp = c.get(
                f"https://api.awin.com/publishers/{PUBLISHER_ID}/programmes",
                params={"region": region, "pageSize": 200},
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            progs = data if isinstance(data, list) else data.get("programmes", data) or []
            for p in progs:
                pid = p.get("id")
                if pid and pid not in seen:
                    seen.add(pid)
                    all_progs.append({"id": pid, "name": p.get("name", "Unknown"), "region": region})
        except:
            pass
    c.close()
    return all_progs


def check_joined(client, programme_id):
    """Check if already joined to a programme."""
    try:
        resp = client.get(
            f"https://api.awin.com/publishers/{PUBLISHER_ID}/programmes/{programme_id}",
            params={"relationship": "joined"},
            timeout=15,
        )
        return resp.status_code == 200
    except:
        return False


def try_join(client, programme_id):
    """Try to join via multiple internal endpoints."""
    cookies = {}
    if SESSION_COOKIE:
        cookies["PHPSESSID"] = SESSION_COOKIE
        cookies["session"] = SESSION_COOKIE

    endpoints = [
        # Darwin internal API (returned 400 before - needs session)
        ("POST", f"{ENDIAN}/api/v1/publisher/{PUBLISHER_ID}/programme/{programme_id}/join"),
        ("POST", f"{ENDIAN}/publisher/{PUBLISHER_ID}/programme/apply"),
        ("PUT", f"{ENDIAN}/api/v1/publisher/{PUBLISHER_ID}/programme/{programme_id}/join"),
        # Web UI form
        ("POST", f"https://ui.awin.com/merchant/publisherapplication"),
        # Direct AWIN1 internal
        ("POST", f"https://www.awin1.com/awin/api/publisher/{PUBLISHER_ID}/programme/{programme_id}/join"),
    ]

    for method, url in endpoints:
        try:
            resp = httpx.request(
                method, url,
                cookies=cookies,
                data={"publisherId": PUBLISHER_ID, "programmeId": programme_id},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=15,
                follow_redirects=False,
            )
            if resp.status_code in (200, 201, 302, 303):
                return ("joined", url, resp.status_code)
            if resp.status_code == 409:
                return ("already", url, resp.status_code)
            if resp.status_code == 400:
                continue  # wrong format, try next
        except:
            continue

    return ("failed", "no_endpoint_worked", 0)


def main():
    global SESSION_COOKIE
    SESSION_COOKIE = (os.environ.get("AWIN_SESSION") or "").strip()

    if not SESSION_COOKIE:
        print("=" * 60)
        print("  Paste your Awin session cookie (from DevTools):")
        print("=" * 60)
        print()
        SESSION_COOKIE = input("  Session cookie > ").strip()
        if not SESSION_COOKIE:
            print("\n  No cookie provided. Exiting.")
            return

    print(f"\n  Publisher ID: {PUBLISHER_ID}")
    print(f"  Session cookie: {SESSION_COOKIE[:20]}...{SESSION_COOKIE[-5:]}")
    print()

    c = httpx.Client(timeout=30)

    print("Fetching all programmes...")
    programmes = fetch_all_programmes()
    print(f"  Found {len(programmes)} unique programmes\n")

    # Test join on one programme first
    print("Testing join on programme 8 (Drinkstuff.com)...")
    result, url, code = try_join(c, 8)
    print(f"  Result: {result} (HTTP {code})")
    if result == "joined":
        print("  [OK] Join endpoint works!")
    elif result == "already":
        print("  [SKIP] Already joined (endpoint works)")
    else:
        print(f"  [FAIL] Could not join: {result} {url}")
        print("\n  The session cookie may not be valid. Try:")
        print("  1. Open ui.awin.com in Chrome")
        print("  2. F12 → Application → Cookies → ui.awin.com")
        print("  3. Find 'PHPSESSID' or 'session' value")
        print("  4. Copy the full value")
        c.close()
        return

    # Join all programmes
    print(f"\nJoining {len(programmes)} programmes...\n")
    joined = already = failed = 0
    for i, prog in enumerate(programmes):
        pid = prog["id"]
        result, url, code = try_join(c, pid)
        if result == "joined":
            joined += 1
            icon = "+"
        elif result == "already":
            already += 1
            icon = "="
        else:
            failed += 1
            icon = "x"
        print(f"\r  [{i+1}/{len(programmes)}] {icon} {prog['name'][:50]:50s} ({result})", end="")
        time.sleep(0.1)

    print(f"\n\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  [OK] Joined: {joined}")
    print(f"  [SKIP] Already joined: {already}")
    print(f"  [FAIL] Failed: {failed}")
    print(f"  Total: {len(programmes)}")
    print(f"{'='*60}")

    c.close()


if __name__ == "__main__":
    main()
