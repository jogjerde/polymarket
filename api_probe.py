import requests
import json

base = "https://data-api.polymarket.com"

endpoints = [
    "/markets",
    "/markets/open",
    "/markets/live", 
    "/markets/active",
    "/markets?status=open",
    "/markets?resolved=false",
    "/markets?live=true",
    "/events",
    "/orders",
    "/book",
]

query_variants = [
    {},
    {"limit": 100},
    {"offset": 0, "limit": 100},
]

for endpoint in endpoints:
    for params in query_variants:
        url = base + endpoint
        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                js = resp.json()
                if isinstance(js, list) and len(js) > 0:
                    print(f"\n✅ {endpoint} (params: {params})")
                    print(f"   Returned {len(js)} items")
                    print(f"   Sample keys: {list(js[0].keys())[:15]}")
                elif isinstance(js, dict):
                    print(f"\n✅ {endpoint} (params: {params})")
                    print(f"   Response keys: {list(js.keys())}")
            elif resp.status_code in [400, 404]:
                pass
            else:
                print(f"   {endpoint} -> {resp.status_code}")
        except Exception as e:
            pass
