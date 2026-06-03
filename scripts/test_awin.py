import httpx
resp = httpx.get(
    'https://api.awin.com/publishers/2919575/programmes',
    params={'region': 'SPAIN', 'pageSize': 3},
    headers={'Authorization': 'Bearer 9c1d39ce-ebb5-4499-a185-3c9fc7933404'},
    timeout=30,
)
print('Status:', resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    progs = data if isinstance(data, list) else data.get('programmes', data)
    print(f'Found {len(progs)} programmes')
    for p in progs[:3]:
        print(f'  - {p.get("name","?")} (id={p.get("id","?")})')
else:
    print('Error:', resp.text[:300])
