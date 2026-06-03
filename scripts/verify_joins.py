"""Verify Awin joins."""
import httpx

api_key = "9c1d39ce-ebb5-4499-a185-3c9fc7933404"
pid = 2919575
c = httpx.Client(timeout=15, headers={"Authorization": f"Bearer {api_key}"})

# Check joined programmes list
r = c.get(f"https://api.awin.com/publishers/{pid}/programmes", params={"relationship": "joined", "pageSize": 10})
print(f"Joined programmes: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    if isinstance(data, list):
        for p in data:
            print(f"  [{p['id']:>6}] {p['name']}")
    else:
        print(f"  {str(data)[:300]}")
else:
    print(f"  {r.text[:200]}")
print()

# Check programme 3 details
r = c.get(f"https://api.awin.com/publishers/{pid}/programmedetails", params={"advertiserId": 3, "relationship": "any"})
print(f"Programme 3 details: {r.status_code}")
print(f"  {r.text[:300]}")
c.close()
