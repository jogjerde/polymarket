from api import PolymarketAPI
from config import TRACKED_WALLETS

api = PolymarketAPI()

lol_by_condition = {}

for wallet in TRACKED_WALLETS:
    trades = api.fetch_trades(wallet)
    
    for t in trades:
        if 'lol' in t.get('title', '').lower() and 'ratones' in t.get('title', '').lower():
            cid = t.get('conditionId')
            if cid not in lol_by_condition:
                lol_by_condition[cid] = {
                    'title': t.get('title'),
                    'slug': t.get('slug'),
                    'wallets': []
                }
            lol_by_condition[cid]['wallets'].append(wallet[:8] + '...')

print(f"\nLoL 'Los Ratones' markets found:")
print(f"Total unique condition IDs: {len(lol_by_condition)}\n")

for cid, data in lol_by_condition.items():
    print(f"Condition ID: {cid}")
    print(f"Title: {data['title']}")
    print(f"Slug: {data['slug']}")
    print(f"Wallets: {len(set(data['wallets']))} unique")
    print(f"  {set(data['wallets'])}\n")

api.close()
