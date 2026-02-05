from api import PolymarketAPI
from config import TRACKED_WALLETS
from processor import TradeProcessor

api = PolymarketAPI()

# Fetch all trades
wallet_trades = {}
for wallet in TRACKED_WALLETS:
    trades = api.fetch_trades(wallet)
    wallet_trades[wallet] = trades

# Target the LoL market
target_cid = "0xa08001184d9fc98ac4891b9cfa6a03f482931bcdef0e6488efe77129ce0849a4"

# Check what's in the extracted markets
processor = TradeProcessor(min_wallets=2)
all_trades = []
for trades in wallet_trades.values():
    all_trades.extend(trades)

all_markets = processor.extract_market_info_from_trades(all_trades)

if target_cid in all_markets:
    print("✓ Market IS in all_markets")
    market = all_markets[target_cid]
    print(f"  resolved: {market.get('resolved')}")
    print(f"  closed: {market.get('closed')}")
else:
    print("✗ Market NOT in all_markets")

# Check what lives markets pass the filter
live_markets = {
    cid: m for cid, m in all_markets.items()
    if not m.get("resolved", False) and not m.get("closed", False)
}

if target_cid in live_markets:
    print("✓ Market IS in live_markets")
else:
    print("✗ Market NOT in live_markets")

# Now check if it passes MIN_WALLETS filtering
print("\nChecking wallet counts...")
from collections import defaultdict

market_data = defaultdict(lambda: {
    "yes_wallets": [],
    "no_wallets": [],
})

for wallet, trades in wallet_trades.items():
    for trade in trades:
        cid = trade.get("conditionId")
        if cid == target_cid:
            outcome = trade.get("outcome", "").upper()
            if outcome == "YES":
                if wallet not in market_data[cid]["yes_wallets"]:
                    market_data[cid]["yes_wallets"].append(wallet)
            elif outcome == "NO":
                if wallet not in market_data[cid]["no_wallets"]:
                    market_data[cid]["no_wallets"].append(wallet)

if target_cid in market_data:
    data = market_data[target_cid]
    yes_count = len(data["yes_wallets"])
    no_count = len(data["no_wallets"])
    total = yes_count + no_count
    print(f"YES wallets: {yes_count}")
    print(f"NO wallets: {no_count}")
    print(f"Total wallets: {total}")
    print(f"MIN_WALLETS_PER_MARKET requirement: 2")
    if total >= 2:
        print("✓ Should pass MIN_WALLETS filter")
    else:
        print("✗ FAILS MIN_WALLETS filter")

api.close()
