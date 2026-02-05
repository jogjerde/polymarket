from api import PolymarketAPI
from config import TRACKED_WALLETS

api = PolymarketAPI()

target_cid = "0xa08001184d9fc98ac4891b9cfa6a03f482931bcdef0e6488efe77129ce0849a4"

yes_wallets = []
no_wallets = []

for wallet in TRACKED_WALLETS:
    trades = api.fetch_trades(wallet)
    
    for trade in trades:
        if trade.get("conditionId") == target_cid:
            outcome = trade.get("outcome", "").upper()
            print(f"Found LoL trade in {wallet[:10]}... outcome={outcome}")
            
            if outcome == "YES" and wallet not in yes_wallets:
                yes_wallets.append(wallet)
            elif outcome == "NO" and wallet not in no_wallets:
                no_wallets.append(wallet)

print(f"\nSummary:")
print(f"YES: {len(yes_wallets)} wallets")
print(f"NO: {len(no_wallets)} wallets")
print(f"Total: {len(yes_wallets) + len(no_wallets)} wallets")

api.close()
