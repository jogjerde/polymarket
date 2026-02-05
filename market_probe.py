import requests
import json

base = "https://data-api.polymarket.com"
trades_url = f"{base}/trades"
markets_url = f"{base}/markets"

wallet = "0xb30fe15964655f469c29a0b7b7a7305ff02a9505"
print(f"Fetching trades for sample wallet {wallet}")
r = requests.get(trades_url, params={"user": wallet}, timeout=10)
trades = r.json()
print(f"Fetched {len(trades)} trades")
if not trades:
    print("No trades returned; aborting")
    raise SystemExit(1)

sample_ids = list({t.get('conditionId') for t in trades if t.get('conditionId')})[:5]
print("Sample condition IDs:")
for sid in sample_ids:
    print(" -", sid)

param_names = ["condition_ids", "conditionId", "conditionId[]", "ids", "id", "market_ids", "marketId"]

for name in param_names:
    params = {name: ",".join(sample_ids)}
    try:
        resp = requests.get(markets_url, params=params, timeout=10)
        print(f"Param: {name:15} Status: {resp.status_code}")
        if resp.status_code == 200:
            try:
                js = resp.json()
                print(f"  -> returned {len(js)} items")
                if len(js) > 0:
                    print("  -> sample item keys:", list(js[0].keys())[:10])
            except Exception as e:
                print("  -> json parse error", e)
        else:
            # print short body
            text = resp.text
            print("  -> body:", text[:200].replace('\n',' '))
    except Exception as e:
        print(f"  -> request error: {e}")
