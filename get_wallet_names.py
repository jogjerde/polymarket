"""Quick script to fetch wallet names from Polymarket API."""

import requests

wallets = [
    "0xb30fe15964655f469c29a0b7b7a7305ff02a9505",
    "0x020b3e1b425742b74b67723c5e0feb912665d13c",
    "0x07046535ff9a910d7343a2c319a3e62234621858",
    "0xbcb6ebb4368dd51722d68d25c740cde2ef5fc7c9",
    "0x7072dd52161bae614bec6905846a53c9a3a53413",
    "0x7f3c8979d0afa00007bae4747d5347122af05613",
    "0xda0f4e3f79a50b8601b3cb9d421f48ce11bbf0e7",
    "0x6291edb6079eb78d52814340fdf748a2d279cc47",
    "0x5cc5b031c7b8e43dc9cc9b6c4e496fd02815b83a",
    "0xce16ce6be999dce71de3d7ad48ae59ae8a44d66f",
    "0x3dc1c5f14c4662338bc43e96ecd55354ad25e318",
    "0x17a89c0a76b163276b77a7a85ef5079f7e20e61f",
    "0x62e8a3fe83ec46e7439f6ebc0b99e1e6c56ac7f6",
]

api_url = "https://data-api.polymarket.com/trades"

def get_wallet_name(wallet):
    """Get wallet name by searching trades."""
    try:
        # Search for trades where this wallet is the maker (their proxyWallet shows in results)
        params = {"maker": wallet, "limit": 1}
        response = requests.get(api_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                trade = data[0]
                name = trade.get("name") or trade.get("pseudonym") or wallet[:10]
                return name
    except:
        pass
    
    return wallet[:10]

print("Results:")
print()
for wallet in wallets:
    name = get_wallet_name(wallet)
    print(f'    "{wallet}",  # {name}')
