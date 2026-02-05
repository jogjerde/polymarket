from api import PolymarketAPI
from config import TRACKED_WALLETS

api = PolymarketAPI()
wallet = TRACKED_WALLETS[0]
print('\n' + '='*60)
print('Wallet:', wallet)
trades = api.fetch_trades(wallet)
print('Total trades fetched:', len(trades))
if trades:
    t = trades[0]
    print('Sample fields:', list(t.keys()))
    print('title:', t.get('title'))
    print('slug:', t.get('slug'))
    print('outcome:', t.get('outcome'))
    print('resolved:', t.get('resolved'))
    print('closed:', t.get('closed'))
api.close()
