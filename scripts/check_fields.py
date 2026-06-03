import httpx, json
resp = httpx.get(
    'https://api.awin.com/publishers/2919575/programmes',
    params={'region': 'SPAIN', 'pageSize': 2},
    headers={'Authorization': 'Bearer 9c1d39ce-ebb5-4499-a185-3c9fc7933404'},
    timeout=30,
)
data = resp.json()
progs = data if isinstance(data, list) else data.get('programmes', data) if isinstance(data, dict) else []
for p in progs[:2]:
    print(json.dumps(p, indent=2)[:1000])
    print('---')
    print('Keys:', list(p.keys()))
    print()
