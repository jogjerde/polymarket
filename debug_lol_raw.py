from api import PolymarketAPI
from config import TRACKED_WALLETS

api = PolymarketAPI()

target_cid = "0xa08001184d9fc98ac4891b9cfa6a03f482931bcdef0e6488efe77129ce0849a4"

for wallet in TRACKED_WALLETS:
    trades = api.fetch_trades(wallet)
    
    for trade in trades:
        if trade.get("conditionId") == target_cid:
            print("Raw trade fields:")
            print(f"  outcome: {trade.get('outcome')}")
            print(f"  outcomeIndex: {trade.get('outcomeIndex')}")
            print(f"  side: {trade.get('side')}")
            print(f"  title: {trade.get('title')}")
            print(f"  asset: {trade.get('asset')}")
            break
    else:
        continue
    break

api.close()
