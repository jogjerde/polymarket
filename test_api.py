import requests
import json

# Fetch a sample trade to see what fields are available
wallet = '0xf5b723a4a8efb369f4db1228eb7ba9279c353e1c'
url = 'https://data-api.polymarket.com/trades'
params = {'user': wallet}

response = requests.get(url, params=params, timeout=10)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    trades = response.json()
    if trades:
        t = trades[0]
        print(f"Trade keys: {t.keys()}")
        print(f"\nFull first trade:")
        print(json.dumps(t, indent=2))



