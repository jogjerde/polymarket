"""Debug script to inspect API responses."""

import requests
import json

# Fetch a sample of trades to see structure
wallet = "0xb30fe15964655f469c29a0b7b7a7305ff02a9505"
url = "https://data-api.polymarket.com/trades"
params = {"user": wallet}

print("Fetching sample trades...")
response = requests.get(url, params=params, timeout=10)
trades = response.json()

print(f"\nFound {len(trades)} trades")
if len(trades) > 0:
    print("\nFirst trade structure:")
    print(json.dumps(trades[0], indent=2))
    
    # Get unique market IDs
    market_ids = set(t.get("conditionId", t.get("marketId", "UNKNOWN")) for t in trades)
    print(f"\nFirst 5 market IDs: {list(market_ids)[:5]}")
    
    # Try fetching market metadata for a few
    sample_ids = list(market_ids)[:3]
    print(f"\nTrying to fetch metadata for: {sample_ids}")
    
    url = "https://data-api.polymarket.com/markets"
    params = {"condition_ids": ",".join(sample_ids)}
    
    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        markets = response.json()
        print(f"\nGot {len(markets)} markets")
        if len(markets) > 0:
            print("\nFirst market structure:")
            print(json.dumps(markets[0], indent=2))
    else:
        print(f"Error: {response.text}")
