"""Detailed verification of Awin joins."""
import httpx

api_key = "9c1d39ce-ebb5-4499-a185-3c9fc7933404"
pid = 2919575
c = httpx.Client(timeout=15, headers={"Authorization": f"Bearer {api_key}"})

# Get all joined programme IDs
r = c.get(f"https://api.awin.com/publishers/{pid}/programmes", params={"relationship": "joined", "pageSize": 500})
joined_ids = set()
if r.status_code == 200:
    data = r.json()
    if isinstance(data, list):
        for p in data:
            joined_ids.add(p["id"])
else:
    print(f"Error: {r.status_code} {r.text[:200]}")

print(f"\nTotal already joined: {len(joined_ids)}")
print(f"Programme 3 (Awin) joined: {3 in joined_ids}")
print(f"Programme 8 (Drinkstuff) joined: {8 in joined_ids}")
print(f"Programme 106 (Currys Business) joined: {106 in joined_ids}")

# Check some of the first 10 we joined
first_10 = [3, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
for id_ in first_10:
    r = c.get(f"https://api.awin.com/publishers/{pid}/programmedetails", params={"advertiserId": id_, "relationship": "any"})
    if r.status_code == 200:
        data = r.json()
        info = data.get("programmeInfo", {})
        status = info.get("membershipStatus", "unknown")
        name = info.get("name", "?")
        print(f"  Programme {id_:>5} ({name:40s}): status={status}")
    else:
        print(f"  Programme {id_:>5}: error {r.status_code}")
c.close()
