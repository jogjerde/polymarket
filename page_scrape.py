import requests
from bs4 import BeautifulSoup
import re
import json

# Sample market slug from trades
slug = "no-change-in-fed-interest-rates-after-july-2025-meeting"
url = f"https://polymarket.com/market/{slug}"

print(f"Fetching {url}...")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

resp = requests.get(url, headers=headers, timeout=10)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    # Look for JSON-LD or embedded data in page
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Try to find script tags with market data
    scripts = soup.find_all('script', type='application/json')
    print(f"Found {len(scripts)} JSON script tags")
    
    # Look for key indicators on page
    text = resp.text
    
    # Search for resolved/closed indicators
    if 'resolved' in text.lower():
        print("Page mentions 'resolved'")
    if 'closed' in text.lower():
        print("Page mentions 'closed'")
    if 'live' in text.lower():
        print("Page mentions 'live'")
    if 'winner' in text.lower():
        print("Page mentions 'winner'")
        
    # Try to extract any JSON data
    json_matches = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', text, re.DOTALL)
    if json_matches:
        print(f"\nFound {len(json_matches)} JSON blocks")
        for i, match in enumerate(json_matches[:2]):
            try:
                data = json.loads(match)
                print(f"Block {i} keys: {list(data.keys())[:10] if isinstance(data, dict) else type(data)}")
            except:
                pass
