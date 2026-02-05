from api import PolymarketAPI
from config import TRACKED_WALLETS

api = PolymarketAPI()

# Check the 2 new wallets
new_wallets = [
    "0x528635df9791d3dcebf9b82ad4b83e8570440d47",
    "0xa1b3fa26d16c11b222f6785851981c2f560b0329",
    "0x5bc1f038c4cd8344bc97f542bf90b9babb5d9932",
]

for wallet in new_wallets:
    print(f"\n{'='*70}")
    print(f"Wallet: {wallet}")
    trades = api.fetch_trades(wallet)
    print(f"Total trades: {len(trades)}")
    
    # Search for LoL markets
    lol_trades = [t for t in trades if 'lol' in t.get('title', '').lower()]
    print(f"LoL trades found: {len(lol_trades)}")
    
    # Show all market titles
    print("\nAll market titles in this wallet:")
    for t in trades[:20]:  # Show first 20
        print(f"  - {t.get('title')} ({t.get('outcome')})")

api.close()
