from api import PolymarketAPI
from config import TRACKED_WALLETS
import json

api = PolymarketAPI()

# Check one wallet's trades to see all available fields
wallet = TRACKED_WALLETS[0]
trades = api.fetch_trades(wallet)

if trades:
    print("All fields in a trade:")
    print(json.dumps(trades[0], indent=2))
    
    print("\n\nUnique fields across sample trades:")
    all_fields = set()
    for t in trades[:5]:
        all_fields.update(t.keys())
    
    for field in sorted(all_fields):
        print(f"  - {field}")

api.close()
